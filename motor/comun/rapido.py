"""El método rápido de siempre para los motores de tabla: una regresión logística simple, en NumPy.

Es solo la comparación (WORKPLAN.md 11.1 y tarea A-16): muestra qué se pierde sin el modelo
generativo completo. Recibe **las mismas columnas por fila que ve el codificador del motor**
(`armar_filas` de su módulo de `nucleo/`) e ignora la estructura: no hay efectos por grupo ni
latentes por unidad, cada fila es independiente. Así la diferencia con Krylov es el modelo y
no los datos que recibe.

Ajuste: máxima verosimilitud penalizada (ridge suave sobre los coeficientes estandarizados, sin
penalizar el intercepto) con Newton-Raphson (IRLS). Su «rango de 90%» es el intervalo de Wald
sobre el logit, con la covarianza asintótica (X'WX + λI)⁻¹: lo que entrega cualquier paquete.

    uv run python -m motor.comun.rapido --caso credito          # su examen con los datos reales reservados

Para un caso, el motor aporta `motor.<motor_id>.sello.filas_reales(caso)` → (filas, ids).
"""

from __future__ import annotations

import argparse
import importlib
import json

import numpy as np

Z_90 = 1.6448536269514722


def ajustar(x: np.ndarray, y: np.ndarray, ridge: float = 1.0, iteraciones: int = 50) -> dict:
    """Regresión logística de y (0/1) sobre x (n, d). Devuelve coeficientes y covarianza en la escala estandarizada.

    Las columnas se estandarizan; las constantes quedan en cero. `ridge` es λ de la penalización λ/2·‖β‖²
    (equivale a un prior Normal(0, 1/λ) sobre cada coeficiente estandarizado): con 1,0 casi no mueve nada con
    cientos de filas y evita la separación perfecta.
    """
    x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    media, escala = x.mean(axis=0), x.std(axis=0)
    escala = np.where(escala > 1e-9, escala, np.inf)
    a = np.c_[np.ones(len(x)), (x - media) / escala]
    penal = ridge * np.eye(a.shape[1])
    penal[0, 0] = 0.0
    tasa = float(np.clip(y.mean(), 1e-6, 1 - 1e-6))
    beta = np.zeros(a.shape[1])
    beta[0] = np.log(tasa / (1 - tasa))
    for _ in range(iteraciones):
        p = 1 / (1 + np.exp(-(a @ beta)))
        hessiano = a.T @ (a * (p * (1 - p))[:, None]) + penal + 1e-9 * np.eye(a.shape[1])
        paso = np.linalg.solve(hessiano, a.T @ (y - p) - penal @ beta)
        beta = beta + paso
        if np.abs(paso).max() < 1e-8:
            break
    p = 1 / (1 + np.exp(-(a @ beta)))
    covarianza = np.linalg.inv(a.T @ (a * (p * (1 - p))[:, None]) + penal + 1e-9 * np.eye(a.shape[1]))
    return {"beta": beta, "covarianza": covarianza, "media": media, "escala": escala}


def predecir(modelo: dict, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(p, extremo bajo, extremo alto) del intervalo de Wald de 90% para la probabilidad de cada fila de x."""
    a = np.c_[np.ones(len(x)), (np.asarray(x, dtype=np.float64) - modelo["media"]) / modelo["escala"]]
    logit = a @ modelo["beta"]
    desv = np.sqrt(np.einsum("ni,ij,nj->n", a, modelo["covarianza"], a))
    logistica = lambda v: 1 / (1 + np.exp(-v))                                   # noqa: E731
    return logistica(logit), logistica(logit - Z_90 * desv), logistica(logit + Z_90 * desv)


def desde_filas(filas: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """De las filas del codificador (n, F) a (x, y): las dos últimas columnas son la respuesta y la marca «por decidir»."""
    filas = np.asarray(filas, dtype=np.float64)
    return filas[:, :-2], np.where(filas[:, -1] > 0.5, np.nan, filas[:, -2])


def ajustar_y_predecir(filas: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ajusta con las filas de respuesta conocida y predice las filas por decidir: (p, bajo, alto), en su orden."""
    x, y = desde_filas(filas)
    conocida = ~np.isnan(y)
    return predecir(ajustar(x[conocida], y[conocida]), x[~conocida])


def metricas(p: np.ndarray, y: np.ndarray) -> dict:
    """Qué tan bien le fue a una probabilidad p contra lo que pasó (y en 0/1): Brier, pérdida logarítmica y AUC.

    `brier_tasa_base` es el Brier de decir a todos la proporción observada: la vara de «no saber nada».
    """
    from nucleo.nube import auc_con_signo
    p, y = np.clip(np.asarray(p, dtype=np.float64), 1e-9, 1 - 1e-9), np.asarray(y, dtype=np.float64)
    return {"n": int(len(y)), "brier": round(float(((p - y) ** 2).mean()), 4),
            "brier_tasa_base": round(float(y.mean() * (1 - y.mean())), 4),
            "log_perdida": round(float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()), 4),
            "auc": round(auc_con_signo(p, y > 0.5), 3), "tasa_observada": round(float(y.mean()), 3), "p_media": round(float(p.mean()), 3)}


def examen(caso: dict, filas: np.ndarray, ids: list[str]) -> dict | None:
    """El examen con datos reales reservados (`caso["verdad"]`) del método rápido: mismos tramos que el de Krylov.

    filas, ids: todas las filas del archivo, en su orden. Devuelve `tramos` (como `nucleo.tabla.examen`) y `metricas`,
    o None si el caso no trae verdad.
    """
    from nucleo import tabla
    from nucleo.casos import leer_columnas
    _, y = desde_filas(filas)
    por_decidir = np.isnan(y)
    p, _, _ = ajustar_y_predecir(filas)
    ids_por_decidir = [str(i) for i, falta in zip(ids, por_decidir) if falta]
    bloque = tabla.examen(caso, ids_por_decidir, p)
    if bloque is None:
        return None
    t = leer_columnas(caso["verdad"])
    verdad = {i: tabla.si_no(v) for i, v in zip(t["id"], t["objetivo"]) if v.strip()}
    con_verdad = [j for j, i in enumerate(ids_por_decidir) if i in verdad]
    return {"metodo": "regresión logística simple (Newton-Raphson, ridge 1,0)", "columnas": int(filas.shape[1] - 2),
            "filas_de_ajuste": int((~por_decidir).sum()), "tramos": bloque["tramos"],
            "metricas": metricas(p[con_verdad], np.array([verdad[ids_por_decidir[j]] for j in con_verdad]))}


def principal() -> None:
    from nucleo.casos import cargar_caso
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--caso", required=True, help="un caso de tabla de casos/, por ejemplo credito o inasistencias")
    a = analizador.parse_args()
    caso = cargar_caso(a.caso)
    filas, ids = importlib.import_module(f"motor.{caso['motor']}.sello").filas_reales(caso)
    print(json.dumps({"caso": a.caso, "motor_id": caso["motor"], **examen(caso, filas, ids)}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    principal()
