"""Simulador del modelo generativo de `estados` (WORKPLAN.md, 11.4), vectorizado en NumPy.

Genera lotes de carteras completas: prior sobre θ (33 parámetros globales, en espacio sin
restricciones) → cadena de estados ocultos de cada cliente, mes a mes → atraso, uso del
cupo y pago de los seis meses → impago del mes siguiente según el estado del mes 7, con la
respuesta borrada en el 20% por decidir.

**El prior es una normal independiente por parámetro, en el espacio sin restricciones**
(`PRIOR`). Así el simulador y el MCMC de referencia comparten exactamente el mismo prior
sin escribirlo dos veces, y el orden d_1 < d_2 < d_3 (y el de las posiciones del atraso)
queda impuesto por la parametrización con incrementos positivos: eso rompe el intercambio
de estados. Las medias se eligieron mirando el predictivo a priori contra el archivo real:

    uv run python -m motor.estados.simular --revisar

Las covariables de las transiciones (cupo, edad, educación) salen mitad de filas reales
remuestreadas con una perturbación y mitad de un generador paramétrico (normal
multivariada con correlaciones al azar y la tercera variable en niveles). Las filas que ve
la red salen de `nucleo.estados.armar_filas`, la misma función que usa el servicio.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from nucleo import estados as nucleo_es
from nucleo.estados import DIM_THETA, ESTADOS, MESES, NOMBRES_THETA

RAIZ = Path(__file__).resolve().parents[2]
N_MIN, N_MAX = 500, 2000
FRACCION_POR_DECIDIR = 0.2

# (media, desviación) de cada parámetro libre. Mismo orden que NOMBRES_THETA.
PRIOR = {
    "logit_pi_2": (-0.7, 0.7), "logit_pi_3": (-1.6, 0.7),                      # π cerca de (0,6; 0,3; 0,1)
    **{f"A_{j}{k}": (-2.0, 1.0) for j in (1, 2, 3) for k in (1, 2, 3) if j != k},   # los estados son persistentes
    "psi_cupo": (0.0, 0.5), "psi_edad": (0.0, 0.5), "psi_educacion": (0.0, 0.5),
    "log_inc_m_2": (0.4, 0.5), "log_inc_m_3": (0.4, 0.5),                      # posiciones del atraso: 0 < m_2 < m_3
    "corte_1": (-1.5, 0.8), "log_inc_corte_2": (0.1, 0.4), "log_inc_corte_3": (0.9, 0.4), "log_inc_corte_4": (0.9, 0.4),
    "mu_uso_1": (0.2, 0.25), "mu_uso_2": (0.5, 0.25), "mu_uso_3": (0.7, 0.3),  # orden esperado, no impuesto
    **{f"log_sigma_uso_{k}": (-1.4, 0.4) for k in (1, 2, 3)},
    "logit_q_1": (-1.8, 1.0), "logit_q_2": (-1.3, 1.0), "logit_q_3": (-0.6, 1.0),
    "mu_pago_1": (-3.6, 0.7), "mu_pago_2": (-3.9, 0.7), "mu_pago_3": (-4.2, 0.7),
    "log_sigma_pago": (0.2, 0.3),
    "logit_d_1": (-2.5, 1.0), "log_inc_d_2": (0.0, 0.6), "log_inc_d_3": (0.0, 0.6),   # d_1 < d_2 < d_3
}
assert tuple(PRIOR) == tuple(NOMBRES_THETA)
MEDIAS = np.array([PRIOR[n][0] for n in NOMBRES_THETA])
DESVS = np.array([PRIOR[n][1] for n in NOMBRES_THETA])


def muestrear_prior(rng: np.random.Generator, lote: int) -> np.ndarray:
    """θ ~ prior, en espacio sin restricciones: (lote, 33)."""
    return MEDIAS + DESVS * rng.standard_normal((lote, DIM_THETA))


def cargar_covariables_reales(caso: str = "credito") -> np.ndarray | None:
    """Cupo, edad y educación crudos del archivo del caso, (filas, 3). None si el archivo no está."""
    from nucleo.casos import ErrorKrylov, cargar_caso, leer_columnas
    try:
        c = cargar_caso(caso)
        tabla = leer_columnas(c["dataset"])
    except ErrorKrylov:
        return None
    return np.array([[float(v) for v in tabla[col]] for col in c["columnas"]["transiciones"]]).T


def _estandarizar(x: np.ndarray) -> np.ndarray:
    return (x - x.mean(axis=-2, keepdims=True)) / np.maximum(x.std(axis=-2, keepdims=True), 1e-9)


def covariables(rng: np.random.Generator, lote: int, n: int, reales: np.ndarray | None) -> np.ndarray:
    """x estandarizado por cartera, (lote, n, 3): mitad remuestreo de filas reales, mitad generador paramétrico."""
    # Generador: normal multivariada con correlación al azar; la tercera variable (educación) va en 2 a 6 niveles.
    mezcla = rng.normal(0, 0.6, (lote, 3, 3)) + np.eye(3)
    x = rng.standard_normal((lote, n, 3)) @ np.swapaxes(mezcla, 1, 2)
    niveles = rng.integers(2, 7, (lote, 1))
    x[..., 2] = np.floor((0.5 + 0.5 * np.tanh(x[..., 2] / 1.5)) * niveles)
    if reales is not None:
        del_archivo = rng.random(lote) < 0.5
        filas = reales[rng.integers(0, len(reales), (lote, n))].astype(np.float64)
        filas[..., 0] = np.log(filas[..., 0]) + rng.normal(0, 0.1, (lote, n))        # cupo en logaritmo, perturbado
        filas[..., 1] += rng.normal(0, 1.5, (lote, n))                                # edad
        x = np.where(del_archivo[:, None, None], filas, x)
    return _estandarizar(x)


def _categorica(rng: np.random.Generator, probabilidades: np.ndarray) -> np.ndarray:
    """Un sorteo por fila de `probabilidades` (..., K): devuelve el índice elegido, con forma (...)."""
    acumulada = np.cumsum(probabilidades, axis=-1)
    return (rng.random(probabilidades.shape[:-1] + (1,)) > acumulada[..., :-1]).sum(axis=-1)


def simular(rng: np.random.Generator, lote: int, n: int, reales: np.ndarray | None = None, opcionales: bool = True) -> dict:
    """Un lote de carteras simuladas, todas de n clientes.

    Devuelve `filas` (lote, n, 56) para el codificador, `theta` (lote, 33) sin restricciones, y las variables
    del modelo (`nivel`, `uso`, `pago_cero`, `log_pago`, `x`, `impago` con NaN en los por decidir, `impago_real`).
    """
    theta = muestrear_prior(rng, lote)
    th = nucleo_es.a_restringido(theta)
    # Papeles opcionales (D-35): la mitad de las carteras trae las tres covariables; en el resto, cada una con probabilidad 0,7.
    # La ausente va en cero: las transiciones no dependen de su ψ, y el posterior de ese ψ es el prior.
    presentes = ((rng.random((lote, 1)) < 0.5) | (rng.random((lote, nucleo_es.DIM_PRESENCIA)) < 0.7)).astype(np.float64) if opcionales else np.ones((lote, nucleo_es.DIM_PRESENCIA))
    x = covariables(rng, lote, n, reales) * presentes[:, None, :]
    paso = nucleo_es.transiciones({k: v[:, None] if k in ("A", "psi") else v for k, v in th.items()}, x[:, :, None, :])[:, :, 0]
    # ^ (lote, n, 3, 3): una matriz de transición por cliente.

    estado = np.empty((lote, n, MESES + 1), dtype=int)
    estado[..., 0] = _categorica(rng, np.broadcast_to(th["pi"][:, None, :], (lote, n, ESTADOS)))
    for t in range(1, MESES + 1):
        fila = np.take_along_axis(paso, estado[..., t - 1][..., None, None], axis=-2)[..., 0, :]
        estado[..., t] = _categorica(rng, fila)
    s = estado[..., :MESES]                                                       # (lote, n, 6): lo que emite

    def del_estado(v):                                                            # (lote, 3) → (lote, n, 6)
        return np.take_along_axis(np.broadcast_to(v[:, None, None, :], (lote, n, MESES, ESTADOS)), s[..., None], axis=-1)[..., 0]

    # Atraso: logit ordenado por variable latente. nivel = cuántos cortes quedan bajo m_k + ruido logístico.
    u = rng.random((lote, n, MESES)).clip(1e-12, 1 - 1e-12)
    latente = del_estado(th["posicion"]) + np.log(u / (1 - u))
    nivel = (latente[..., None] > th["cortes"][:, None, None, :]).sum(axis=-1)
    uso = del_estado(th["mu_uso"]) + del_estado(th["sigma_uso"]) * rng.standard_normal((lote, n, MESES))
    pago_cero = rng.random((lote, n, MESES)) < del_estado(th["q"])
    log_pago = del_estado(th["mu_pago"]) + th["sigma_pago"][:, None, None] * rng.standard_normal((lote, n, MESES))
    log_pago = np.where(pago_cero, 0.0, log_pago)
    d = np.take_along_axis(np.broadcast_to(th["d"][:, None, :], (lote, n, ESTADOS)), estado[..., MESES][..., None], axis=-1)[..., 0]
    impago_real = (rng.random((lote, n)) < d).astype(np.float64)
    impago = np.where(rng.random((lote, n)) < FRACCION_POR_DECIDIR, np.nan, impago_real)

    return {"filas": nucleo_es.armar_filas(nivel, uso, pago_cero, log_pago, x, impago, presentes[:, None, :]), "theta": theta.astype(np.float32), "presentes": presentes,
            "nivel": nivel, "uso": uso, "pago_cero": pago_cero, "log_pago": log_pago, "x": x,
            "impago": impago, "impago_real": impago_real, "estado": estado}


def muestrear_n(rng: np.random.Generator) -> int:
    """Clientes por cartera en este lote: log-uniforme entre N_MIN y N_MAX."""
    return int(np.exp(rng.uniform(np.log(N_MIN), np.log(N_MAX + 1))))


def resumenes(nivel, uso, pago_cero, log_pago, impago) -> dict[str, np.ndarray]:
    """Resúmenes por cartera para mirar el predictivo a priori contra el archivo real. Ejes delanteros libres."""
    sin_cero = ~np.asarray(pago_cero)
    atrasado = np.asarray(nivel) >= 3
    return {
        "impago": np.nanmean(impago, axis=-1),
        "atraso_sin_uso": (np.asarray(nivel) == 0).mean(axis=(-2, -1)), "atraso_al_dia": (np.asarray(nivel) == 2).mean(axis=(-2, -1)),
        "atraso_1_o_mas": atrasado.mean(axis=(-2, -1)),
        "atraso_persistencia": (atrasado[..., 1:] & atrasado[..., :-1]).sum(axis=(-2, -1)) / np.maximum(atrasado[..., :-1].sum(axis=(-2, -1)), 1),
        "uso_media": np.asarray(uso).mean(axis=(-2, -1)), "uso_desv": np.asarray(uso).std(axis=(-2, -1)),
        "pago_cero": np.asarray(pago_cero).mean(axis=(-2, -1)),
        "log_pago_media": (np.asarray(log_pago) * sin_cero).sum(axis=(-2, -1)) / np.maximum(sin_cero.sum(axis=(-2, -1)), 1),
    }


def variables_del_caso(caso: str = "credito") -> dict:
    """Las variables del modelo del archivo real de un caso: la misma lectura que hace el servicio."""
    from nucleo.casos import cargar_caso
    return nucleo_es.leer_caso(cargar_caso(caso))


def revisar(carteras: int = 2000, semilla: int = 0) -> dict:
    """Percentil de cada resumen del archivo real entre los mismos resúmenes de carteras simuladas con el prior."""
    real = variables_del_caso()
    del_real = resumenes(real["nivel"], real["uso"], real["pago_cero"], real["log_pago"], real["impago"])
    rng = np.random.default_rng(semilla)
    sim = simular(rng, carteras, 500, cargar_covariables_reales())
    simulados = resumenes(sim["nivel"], sim["uso"], sim["pago_cero"], sim["log_pago"], sim["impago"])
    return {k: {"real": round(float(v), 3), "percentil_en_lo_simulado": round(float((simulados[k] < v).mean()) * 100, 1),
                "simulado_p05_p50_p95": [round(float(q), 3) for q in np.quantile(simulados[k], [0.05, 0.5, 0.95])]}
            for k, v in del_real.items()}


def config() -> dict:
    return {"motor_id": "estados", "version_preproceso": "estados-2", "papeles_opcionales": "las tres covariables de las transiciones, con marca de presencia", "nombres_theta": list(NOMBRES_THETA),
            "prior": {n: {"media": m, "desv": s} for n, (m, s) in PRIOR.items()}, "rangos": {"n": [N_MIN, N_MAX]},
            "fraccion_por_decidir": FRACCION_POR_DECIDIR, "niveles_de_atraso": ["-2", "-1", "0", "1 o 2", "3 o más"]}


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--revisar", action="store_true", help="predictivo a priori contra datos/demo/credito.csv")
    if analizador.parse_args().revisar:
        print(json.dumps(revisar(), indent=1, ensure_ascii=False))
