"""Motor `desgaste` (caso `flota`): proceso gamma jerárquico con mediciones ruidosas y una covariable de exigencia de la ruta.

El modelo generativo (`WORKPLAN.md`, 11.4), con el tiempo en miles de horas de operación y el desgaste normalizado
para que la falla sea 1:

    log ν_i ~ Normal(μ_ν + β·x_i, σ_ν)                                    ritmo de desgaste del camión i
    X_i(0) = 0;   ΔX ~ Gamma(forma = ν_i·Δt / c², escala = c²)             proceso gamma: avanza a saltos y nunca retrocede
    y_ij = X_i(t_ij) + ε,   ε ~ Normal(0, σ_ε)

Los camiones del archivo siguen en servicio: X_i(hoy) < 0,92. «Hoy» es la última muestra del camión. Se decide sobre
p_i = P(X_i(hoy + h_i) ≥ 1 | datos), con h_i lo que falta para su próxima mantención programada.

Aquí vive lo que comparten el simulador (`motor/desgaste/simular.py`) y el servicio: el diseño de tamaños, el prior,
el preprocesamiento (uno solo) y `analizar`. Solo NumPy.
"""

from __future__ import annotations

import numpy as np

from nucleo import series
from nucleo.casos import ArchivoNoCalza

MOTOR_ID = "desgaste"

# El nivel de diseño del modelo: con qué tamaños de archivo practica la red. El simulador sortea dentro de estos
# rangos, `config.json` y `papeles()` publican los mismos, y un archivo que se sale da `rojo_datos`.
DISENO = {
    "unidades": (8, 120),               # camiones, log-uniforme
    "lecturas": (3, 20),                # muestras por camión, uniforme, a intervalos irregulares
    "miles_de_horas_hoy": (0.5, 3.0),   # horas de operación del camión en su última muestra, uniforme
    "miles_de_horas_a_mantencion": (0.05, 1.0),   # lo que falta para su próxima mantención, uniforme
}
EN_SERVICIO_BAJO = 0.92                 # un camión del archivo todavía no falla: su desgaste de hoy está bajo este valor
HORAS_POR_UNIDAD = 1000.0               # el archivo trae horas; el modelo, miles de horas
RANGOS = {"unidades": {"minimo": DISENO["unidades"][0], "maximo": DISENO["unidades"][1]},
          "lecturas_por_unidad": {"minimo": DISENO["lecturas"][0], "maximo": DISENO["lecturas"][1]},
          "frase": "Practiqué con flotas de 8 a 120 camiones, cada uno con 3 a 20 muestras."}
PRACTICA = (f"practiqué con flotas de {DISENO['unidades'][0]} a {DISENO['unidades'][1]} camiones, "
            f"cada uno con al menos {DISENO['lecturas'][0]} muestras")

PRIOR = {
    "mu_nu_media": float(np.log(0.5)), "mu_nu_desv": 0.5, "sigma_nu_escala": 0.5,
    "beta_media": 0.3, "beta_desv": 0.3,
    "c_media": float(np.log(0.3)), "c_desv": 0.4,
    "sigma_eps_media": float(np.log(0.04)), "sigma_eps_desv": 0.5,
}
NOMBRES_ETA = ("mu_nu", "log_sigma_nu", "beta", "log_c", "log_sigma_eps")
NOMBRES_LAM = ("log_nu", "log_desgaste_hoy")       # log_desgaste_hoy = log(X_i(hoy) + 0,01): finito aunque el camión no lleve desgaste
PISO = 0.01
CANALES, DIM_COV, DIM_TAM = 4, 4, 2
SORTEOS_FUTURO = 16                    # sorteos del incremento hasta la mantención, por cada muestra de (η, λ_i)

PAPELES = [
    {"papel": "unidad", "cantidad": 1, "tipo": "texto", "texto": "El camión",
     "texto_largo": "A qué camión pertenece cada muestra."},
    {"papel": "tiempo", "cantidad": 1, "tipo": "numero", "texto": "Horas de operación",
     "texto_largo": "Cuántas horas de operación llevaba el camión, desde su última mantención, al tomar la muestra."},
    {"papel": "valor", "cantidad": 1, "tipo": "numero", "texto": "Indicador de desgaste",
     "texto_largo": "Lo medido en la muestra (por ejemplo, hierro en el aceite), en una escala donde el camión falla al llegar al límite."},
    {"papel": "covariables", "cantidad": 1, "tipo": "numero", "texto": "Exigencia de la ruta",
     "texto_largo": "Qué tan exigente es la ruta del camión, estandarizada (0 = la ruta típica). Se repite en las filas del camión."},
    {"papel": "horizonte_por_unidad", "cantidad": 1, "tipo": "numero", "texto": "Horas hasta la mantención",
     "texto_largo": "Cuántas horas de operación le faltan al camión para su próxima mantención programada. Se repite en sus filas."},
]


def preparar(t: np.ndarray, y: np.ndarray, mascara: np.ndarray, exigencia: np.ndarray, a_mantencion: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """El único preprocesamiento del motor: lo llaman el simulador (por lotes) y el servicio (un archivo).

    t, y, mascara: (..., M, K), con las muestras de cada camión ordenadas por tiempo y el relleno al final; t en miles de
    horas, y con la falla en 1. exigencia, a_mantencion: (..., M). Devuelve
      x (..., M, K, 4) = [t / 3, y, y − y anterior, t − t anterior]   (antes de la primera muestra: desgaste 0 en t = 0);
      cov (..., M, 4)  = [log de muestras − 2, horas de hoy / 3, exigencia de la ruta, horas a la mantención];
      tam (..., 2)     = [log de camiones − 3,5, muestras promedio por camión / 10].
    """
    y_prev = np.concatenate([np.zeros_like(y[..., :1]), y[..., :-1]], axis=-1)
    t_prev = np.concatenate([np.zeros_like(t[..., :1]), t[..., :-1]], axis=-1)
    x = np.stack([t / 3.0, y, y - y_prev, t - t_prev], axis=-1) * mascara[..., None]
    n = mascara.sum(-1)
    hay = n > 0
    hoy = (t * mascara).max(-1)
    cov = np.stack([np.log(np.maximum(n, 1.0)) - 2.0, hoy / 3.0, exigencia, a_mantencion], axis=-1) * hay[..., None]
    camiones = hay.sum(-1)
    tam = np.stack([np.log(np.maximum(camiones, 1.0)) - 3.5, n.sum(-1) / np.maximum(camiones, 1.0) / 10.0], axis=-1)
    return x.astype(np.float32), cov.astype(np.float32), tam.astype(np.float32)


def desgaste_hoy(lam: np.ndarray) -> np.ndarray:
    """X_i(hoy) a partir del parámetro local, que va como log(X + 0,01)."""
    return np.maximum(np.exp(lam[..., 1]) - PISO, 0.0)


def margen(eta: np.ndarray, lam: np.ndarray, a_mantencion: np.ndarray) -> np.ndarray:
    """Lo que se decide, en una versión continua para la cobertura: cuánto se pasa del límite el desgaste esperado en la
    mantención, en desviaciones del proceso: (X_hoy + ν·h − 1) / (c·√(ν·h)). Más alto = más cerca de fallar antes.
    eta (..., d), lam (..., M, 2), a_mantencion difundible contra (..., M) → (..., M)."""
    avance = np.exp(lam[..., 0]) * a_mantencion
    return (desgaste_hoy(lam) + avance - 1.0) / (np.exp(eta[..., 3])[..., None] * np.sqrt(avance))


def falla_antes(gen: np.random.Generator, eta: np.ndarray, lam: np.ndarray, a_mantencion: np.ndarray, sorteos: int = SORTEOS_FUTURO) -> np.ndarray:
    """P(X(hoy + h) ≥ 1 | η, λ_i): el incremento hasta la mantención es Gamma(ν·h / c², c²). Fracción de `sorteos` que cruza."""
    c2 = np.exp(2 * eta[..., 3])[..., None]
    forma = np.maximum(np.exp(lam[..., 0]) * a_mantencion / c2, 1e-9)
    futuro = gen.gamma(np.broadcast_to(forma, (sorteos,) + forma.shape)) * c2
    return (desgaste_hoy(lam) + futuro >= 1.0).mean(axis=0)


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """Lo propio del motor en la respuesta de `analizar`: por camión, la probabilidad de fallar antes de su mantención y su curva."""
    col = caso["columnas"]
    try:
        datos = series.leer(caso, extras=("covariables", "horizonte_por_unidad"))
        limite = float(col.get("umbral", 1.0))
        if limite <= 0:
            raise ArchivoNoCalza("El límite de desgaste del caso tiene que ser mayor que cero.", "rojo_modelo")
        datos, aviso = series.revisar_tamano(caso, datos, DISENO, PRACTICA)
        hoy = np.array([t[-1] for t in datos["t"]]) / HORAS_POR_UNIDAD
        a_mantencion = datos["extras"]["horizonte_por_unidad"] / HORAS_POR_UNIDAD
        exigencia = datos["extras"]["covariables"]
        (h_min, h_max), (m_min, m_max) = DISENO["miles_de_horas_hoy"], DISENO["miles_de_horas_a_mantencion"]
        mil = lambda v: series.numero(int(round(v * HORAS_POR_UNIDAD)))     # noqa: E731
        if hoy.min() < 0.8 * h_min or hoy.max() > 1.1 * h_max:
            raise ArchivoNoCalza(f"Hay camiones con {mil(hoy.min())} a {mil(hoy.max())} horas de operación en su última muestra: "
                                 f"practiqué con camiones de {mil(h_min)} a {mil(h_max)} horas.", "rojo_modelo")
        if a_mantencion.min() < 0.8 * m_min or a_mantencion.max() > 1.1 * m_max:
            raise ArchivoNoCalza(f"A los camiones les faltan de {mil(a_mantencion.min())} a {mil(a_mantencion.max())} horas para su mantención: "
                                 f"practiqué con plazos de {mil(m_min)} a {mil(m_max)} horas.", "rojo_modelo")
        if not np.isfinite(exigencia).all() or np.abs(exigencia).max() > 5:
            raise ArchivoNoCalza("La exigencia de la ruta tiene que venir estandarizada (0 = la ruta típica, casi todo entre −3 y 3).", "rojo_modelo")
    except ArchivoNoCalza as error:
        return series.lector.rojo(caso, error)
    t, mascara = series.con_relleno([ti / HORAS_POR_UNIDAD for ti in datos["t"]])
    y, _ = series.con_relleno([yi / limite for yi in datos["y"]])
    x, cov, tam = preparar(t, y, mascara, exigencia, a_mantencion)
    eta, lam, impl = series.posterior(MOTOR_ID, caso, x, mascara, cov, tam)          # (m, d), (m, l, U, 2)
    eta_l = eta[:, None, :]
    gen = np.random.default_rng(series.SEMILLA)
    muestras_p = falla_antes(gen, eta_l, lam, a_mantencion).mean(axis=1).T             # (U, m): P(falla antes | η_i, datos)
    c2 = np.exp(2 * eta_l[..., 3])[..., None]                                          # (m, 1, 1)
    curvas = []
    for j, (tj, yj) in enumerate(zip(datos["t"], datos["y"])):
        pasos = np.full(series.PUNTOS_BANDA - 1, a_mantencion[j] / (series.PUNTOS_BANDA - 1))
        forma = np.maximum(np.exp(lam[..., j, 0, None]) * pasos / c2, 1e-9)            # (m, l, puntos − 1)
        camino = desgaste_hoy(lam[..., j, :])[..., None] + np.concatenate([np.zeros_like(forma[..., :1]), np.cumsum(gen.gamma(forma) * c2, axis=-1)], axis=-1)
        t_banda = tj[-1] + np.linspace(0.0, a_mantencion[j] * HORAS_POR_UNIDAD, series.PUNTOS_BANDA)
        curvas.append(series.curva(tj, yj, t_banda, limite * camino.reshape(-1, series.PUNTOS_BANDA), caso, limite))
    p = PRIOR
    globales = {"ritmo": (eta[:, 0], p["mu_nu_media"], p["mu_nu_desv"]),
                "exigencia": (eta[:, 2], 0.0, p["beta_desv"]),                         # contra «la ruta no importa»
                "saltos": (eta[:, 3], p["c_media"], p["c_desv"]), "ruido": (eta[:, 4], p["sigma_eps_media"], p["sigma_eps_desv"])}
    ids = datos["ids"]
    return {
        "implementacion": impl,
        "unidades": series.unidades(ids, muestras_p, costos, curvas),
        "factores": series.factores(caso, globales),
        "columnas": {"usadas": [col["unidad"], col["tiempo"], col["valor"], *series.lector.nombres_del_papel(col, "covariables", 1),
                                *series.lector.nombres_del_papel(col, "horizonte_por_unidad", 1)],
                     "disponibles": col.get("disponibles", 5), "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "semaforo": {"estado": "amarillo" if aviso else "verde", "motivo": aviso or "", "propuesta": None},
        "examen": series.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{len(ids)} {caso['unidad']['plural']}", f"{series.numero(int(mascara.sum()))} muestras",
                     f"{series.MUESTRAS_ETA} versiones creíbles"],
    }
