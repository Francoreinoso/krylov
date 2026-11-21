"""Motor `cinetica` (caso `flotacion`): cinética de flotación de primer orden con fracción rápida y lenta, jerárquica entre líneas.

El modelo generativo (`WORKPLAN.md`, 11.3). Cada línea b tiene su velocidad k_b y su recuperación máxima Rmax_b:

    R_b(t) = Rmax_b · [ 1 − φ·exp(−k_b·t) − (1 − φ)·exp(−k_b·t / 8) ],      y_bk = R_b(t_k) + ε,  ε ~ Normal(0, σ_y)

y solo se ve la salida de sus primeras celdas. Se decide sobre R_b al final de la línea, que todavía no se mide.

Aquí vive lo que comparten el simulador (`motor/cinetica/simular.py`) y el servicio: el diseño de tamaños, el prior,
la curva, el preprocesamiento (uno solo) y `analizar`. Solo NumPy.
"""

from __future__ import annotations

import numpy as np

from nucleo import series
from nucleo.casos import ArchivoNoCalza

MOTOR_ID = "cinetica"

# El nivel de diseño del modelo: con qué tamaños de archivo practica la red. El simulador sortea dentro de estos
# rangos, `config.json` y `papeles()` publican los mismos, y un archivo que se sale da `rojo_datos`.
DISENO = {
    "unidades": (2, 16),            # líneas de la planta, uniforme
    "celdas": (5, 12),              # celdas por línea, uniforme (común a la planta)
    "lecturas": (3, 12),            # celdas medidas por línea: de 3 al total, distinto en cada línea
    "minutos_por_celda": (2.0, 6.0),   # tiempo de residencia por celda, log-uniforme; cada línea varía ±15%
}
RANGOS = {"unidades": {"minimo": DISENO["unidades"][0], "maximo": DISENO["unidades"][1]},
          "lecturas_por_unidad": {"minimo": DISENO["lecturas"][0], "maximo": DISENO["lecturas"][1]},
          "frase": "Practiqué con plantas de 2 a 16 líneas, cada una medida en 3 a 12 celdas."}
PRACTICA = (f"practiqué con plantas de {DISENO['unidades'][0]} a {DISENO['unidades'][1]} líneas, "
            f"cada una medida en al menos {DISENO['lecturas'][0]} celdas")

PRIOR = {
    "mu_k_media": float(np.log(0.25)), "mu_k_desv": 0.6, "sigma_k_escala": 0.5,
    "mu_R_media": float(np.log(0.90 / 0.10)), "mu_R_desv": 0.6, "sigma_R_escala": 0.6,
    "phi_a": 4.0, "phi_b": 2.0,
    "sigma_y_media": float(np.log(0.015)), "sigma_y_desv": 0.5,
}
RAZON_LENTA = 8.0                   # la fracción lenta flota 8 veces más lento (fijo)
NOMBRES_ETA = ("mu_k", "log_sigma_k", "mu_R", "log_sigma_R", "logit_phi", "log_sigma_y")
NOMBRES_LAM = ("log_k", "logit_rmax")
CANALES, DIM_COV, DIM_TAM = 4, 2, 3

PAPELES = [
    {"papel": "unidad", "cantidad": 1, "tipo": "texto", "texto": "La línea de flotación",
     "texto_largo": "A qué línea de la planta pertenece cada medición."},
    {"papel": "tiempo", "cantidad": 1, "tipo": "numero", "texto": "Minutos en la línea",
     "texto_largo": "Cuántos minutos lleva la pulpa en la línea al salir de la celda donde se midió."},
    {"papel": "valor", "cantidad": 1, "tipo": "numero", "texto": "Cobre recuperado, de 0 a 1",
     "texto_largo": "Qué parte del cobre que entró ya se recuperó a la salida de esa celda, entre 0 y 1."},
]


def _sigmoide(x):
    return 1.0 / (1.0 + np.exp(-x))


def recuperacion(t, log_k, logit_rmax, logit_phi):
    """R(t) del modelo, con difusión de NumPy. t en minutos."""
    k, phi = np.exp(log_k), _sigmoide(logit_phi)
    return _sigmoide(logit_rmax) * (1.0 - phi * np.exp(-k * t) - (1.0 - phi) * np.exp(-k * t / RAZON_LENTA))


def preparar(t: np.ndarray, y: np.ndarray, mascara: np.ndarray, t_final: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """El único preprocesamiento del motor: lo llaman el simulador (por lotes) y el servicio (un archivo).

    t, y, mascara: (..., U, K), con las lecturas de cada línea ordenadas por tiempo y el relleno al final; t_final: (...).
    Devuelve x (..., U, K, 4) = [t/t_final, y, y − y anterior, Δt/t_final], cov (..., U, 2) = [log de lecturas de la línea,
    último tiempo medido / t_final] y tam (..., 3) = [log de líneas, lecturas promedio por línea, log de t_final].
    """
    tf = np.asarray(t_final, dtype=np.float64)[..., None, None]
    u = t / tf
    y_prev = np.concatenate([np.zeros_like(y[..., :1]), y[..., :-1]], axis=-1)
    u_prev = np.concatenate([np.zeros_like(u[..., :1]), u[..., :-1]], axis=-1)
    x = np.stack([u, y, y - y_prev, u - u_prev], axis=-1) * mascara[..., None]
    n = mascara.sum(-1)                                                    # lecturas por línea
    hay = n > 0
    cov = np.stack([np.log(np.maximum(n, 1.0)), (u * mascara).max(-1)], axis=-1) * hay[..., None]
    lineas = hay.sum(-1)
    tam = np.stack([np.log(np.maximum(lineas, 1.0)), n.sum(-1) / np.maximum(lineas, 1.0) / 4.0, np.log(tf[..., 0, 0]) - 3.0], axis=-1)
    return x.astype(np.float32), cov.astype(np.float32), tam.astype(np.float32)


def final_de_linea(eta: np.ndarray, lam: np.ndarray, t_final) -> np.ndarray:
    """Lo que se decide: la recuperación al final de la línea, R_b(t_final). eta (..., d), lam (..., U, 2) → (..., U).

    t_final: un número, o un arreglo que se difunda contra (..., U)."""
    return recuperacion(np.asarray(t_final), lam[..., 0], lam[..., 1], eta[..., 4][..., None])


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """Lo propio del motor en la respuesta de `analizar`: por línea, la probabilidad de terminar bajo la meta y su curva."""
    col = caso["columnas"]
    try:
        datos = series.leer(caso)
        meta, t_final = float(col["umbral"]), float(col["tiempo_final"])
        if any(np.any((y <= 0) | (y >= 1)) for y in datos["y"]):
            raise ArchivoNoCalza("El cobre recuperado tiene que venir entre 0 y 1 (por ejemplo 0,85 y no 85).", "rojo_modelo")
        datos, aviso = series.revisar_tamano(caso, datos, DISENO, PRACTICA)
        t, mascara = series.con_relleno(datos["t"])
        y, _ = series.con_relleno(datos["y"])
        celda = float(np.median(np.concatenate([np.diff(np.concatenate([[0.0], ti])) for ti in datos["t"]])))
        c_min, c_max = DISENO["minutos_por_celda"]
        if not (0.85 * c_min <= celda <= 1.15 * c_max) or not (DISENO["celdas"][0] * c_min <= t_final <= DISENO["celdas"][1] * c_max):
            raise ArchivoNoCalza(f"Las mediciones van cada {celda:.3g} {col.get('unidad_tiempo', 'minutos')} y la línea dura {t_final:g}: "
                                 f"practiqué con celdas de {c_min:g} a {c_max:g} minutos y líneas de hasta {DISENO['celdas'][1] * c_max:g}.")
        if t.max() > t_final * 1.001:
            raise ArchivoNoCalza(f"Hay mediciones después del final de la línea ({t_final:g} {col.get('unidad_tiempo', 'minutos')}).")
    except ArchivoNoCalza as error:
        return series.lector.rojo(caso, error)
    x, cov, tam = preparar(t, y, mascara, np.float64(t_final))
    eta, lam, impl = series.posterior(MOTOR_ID, caso, x, mascara, cov, tam)          # (m, d), (m, l, U, 2)
    eta_l = eta[:, None, :]                                                            # cada λ con su η
    final = final_de_linea(eta_l, lam, t_final)                                        # (m, l, U)
    muestras_p = (final < meta).mean(axis=1).T                                         # (U, m): P(bajo la meta | η_i, datos)
    curvas = []
    for j, ti in enumerate(datos["t"]):
        t_banda = np.linspace(ti[-1], t_final, series.PUNTOS_BANDA) if ti[-1] < t_final else np.array([t_final])
        r = recuperacion(t_banda, lam[..., j, 0, None], lam[..., j, 1, None], eta_l[..., 4, None])   # (m, l, puntos)
        curvas.append(series.curva(ti, datos["y"][j], t_banda, r.reshape(-1, len(t_banda)), caso, meta))
    p = PRIOR
    desv_logit_phi = 0.87                                # desviación de logit φ con φ ~ Beta(4, 2)
    globales = {"velocidad": (eta[:, 0], p["mu_k_media"], p["mu_k_desv"]), "tope": (eta[:, 2], p["mu_R_media"], p["mu_R_desv"]),
                "fraccion_rapida": (eta[:, 4], 0.83, desv_logit_phi), "ruido": (eta[:, 5], p["sigma_y_media"], p["sigma_y_desv"])}
    ids = datos["ids"]
    return {
        "implementacion": impl,
        "unidades": series.unidades(ids, muestras_p, costos, curvas),
        "factores": series.factores(caso, globales),
        "columnas": {"usadas": [col["unidad"], col["tiempo"], col["valor"]], "disponibles": col.get("disponibles", 3),
                     "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "semaforo": {"estado": "amarillo" if aviso else "verde", "motivo": aviso or "", "propuesta": None},
        "examen": series.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{len(ids)} {caso['unidad']['plural']}", f"{series.numero(int(mascara.sum()))} mediciones",
                     f"{series.MUESTRAS_ETA} versiones creíbles"],
    }
