"""Motor `deformacion` (caso `taludes`): sectores de un muro con velocidad de fondo, y algunos acelerándose hacia la falla.

El modelo generativo (`WORKPLAN.md`, 11.2), en unidades normalizadas (u = tiempo / ventana, desplazamiento / e):

    estable (z_j = 0):     d_j(u) = v_j·u
    acelerando (z_j = 1):  d_j(u) = v_j·u + A_j·log( u_f,j / (u_f,j − u) )        (velocidad inversa: Fukuzono 1985, Voight 1988)
    y_jk = d_j(u_k) + modo común(u_k) + ε_jk,   ε_jk ~ Normal(0, σ_e)

Se decide sobre p_j = P(z_j = 1 y u_f,j ≤ 1 + H/T | datos), con H el horizonte del caso y T la ventana.

Aquí vive lo que comparten el simulador (`motor/deformacion/simular.py`) y el servicio: el diseño de tamaños, el prior,
la trayectoria, el preprocesamiento (uno solo) y `analizar`. Solo NumPy.

**El preprocesamiento.** El archivo se lleva a una grilla común de tiempos (unidades × lecturas, con máscara para las
faltantes); a cada sector se le resta su primera lectura; en cada lectura se resta la mediana entre sectores (el modo
común: la atmósfera mueve la lectura del radar en todos los sectores a la vez) y todo se divide por la escala del
archivo, e = la mediana entre sectores del movimiento total en la ventana (con piso en el ruido de lectura). Así el
motor no depende de las unidades: sirve igual para un radar que mide cada 4 minutos y para prismas que se leen cada
4 horas. Como la red ve datos divididos por e, sus parámetros con unidades de desplazamiento (μ_v, μ_A, σ_e, v_j, A_j)
también van divididos por e: en log, se les resta log e. El simulador pasa por esta misma función.
"""

from __future__ import annotations

import math
import warnings

import numpy as np

from nucleo import series
from nucleo.casos import ArchivoNoCalza

MOTOR_ID = "deformacion"
CON_CLASE = True            # cada sector tiene además un estado discreto: z_j = 1 si se está acelerando

# El nivel de diseño del modelo: con qué tamaños de archivo practica la red. El simulador sortea dentro de estos
# rangos, `config.json` y `papeles()` publican los mismos, y un archivo que se sale da `rojo_datos`.
DISENO = {
    "unidades": (6, 80),            # sectores, log-uniforme
    "lecturas": (24, 200),          # lecturas de la ventana (la grilla común), log-uniforme, a paso parejo en u
    "faltantes": (0.0, 0.15),       # fracción de lecturas que le faltan a cada sector, uniforme
}
FALTANTES_TOLERADAS = 0.15          # un sector con más faltantes que esto queda fuera, con aviso
MIN_LECTURAS_SECTOR = math.ceil(DISENO["lecturas"][0] * (1 - DISENO["faltantes"][1]))   # 21
RANGOS = {"unidades": {"minimo": DISENO["unidades"][0], "maximo": DISENO["unidades"][1]},
          "lecturas_por_unidad": {"minimo": DISENO["lecturas"][0], "maximo": DISENO["lecturas"][1]},
          "frase": "Practiqué con muros de 6 a 80 sectores, medidos de 24 a 200 veces en la ventana, con hasta 15% de lecturas faltantes."}
PRACTICA = (f"practiqué con muros de {DISENO['unidades'][0]} a {DISENO['unidades'][1]} sectores, "
            f"cada uno con al menos {DISENO['lecturas'][0]} lecturas en la ventana")

PRIOR = {
    "pi_a": 1.5, "pi_b": 6.0,
    "mu_v_media": 0.0, "mu_v_desv": 0.6, "sigma_v_escala": 0.7,
    "mu_f_media": float(np.log(0.3)), "mu_f_desv": 0.8, "sigma_f_escala": 0.6,
    "mu_A_media": float(np.log(1.5)), "mu_A_desv": 0.6, "sigma_A": 0.5,
    "sigma_e_media": float(np.log(0.05)), "sigma_e_desv": 0.7,
}
NOMBRES_ETA = ("logit_pi", "mu_v", "log_sigma_v", "mu_f", "log_sigma_f", "mu_A", "log_sigma_e")
NOMBRES_LAM = ("log_v", "log_falta", "log_A")          # log_falta = log(u_f − 1); z_j va como última columna de λ
CANALES, DIM_COV, DIM_TAM = 4, 2, 3
CASTIGO_ESTABLE = 20.0              # en `cantidad`: un sector estable queda 20 unidades de log bajo cualquier acelerado
TOPE_BANDA = 20.0                   # el abanico de la curva no sube más de 20 veces la escala e sobre la última lectura

PAPELES = [
    {"papel": "unidad", "cantidad": 1, "tipo": "texto", "texto": "El sector del muro",
     "texto_largo": "A qué sector del muro (prisma o grupo de píxeles del radar) pertenece cada lectura."},
    {"papel": "tiempo", "cantidad": 1, "tipo": "numero", "texto": "Cuándo se leyó",
     "texto_largo": "Cuándo se tomó la lectura, en horas (o días) desde que parte la ventana."},
    {"papel": "valor", "cantidad": 1, "tipo": "numero", "texto": "Cuánto se ha movido",
     "texto_largo": "El desplazamiento acumulado del sector en esa lectura, en milímetros o en la unidad que mida el radar."},
]


def trayectoria(u, log_v, log_falta, log_A, z):
    """d(u) del modelo, con difusión de NumPy. Para u ≥ u_f (después de la falla) devuelve +inf."""
    u_f = 1.0 + np.exp(log_falta)
    restante = u_f - u
    acel = np.where(restante > 0, np.log(u_f / np.maximum(restante, 1e-300)), np.inf)
    return np.exp(log_v) * u + np.where(z > 0.5, np.exp(log_A) * acel, 0.0)


def _primera_y_ultima(mascara: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Índice de la primera y de la última lectura real de cada sector, (..., U)."""
    k = mascara.shape[-1]
    primera = np.argmax(mascara > 0, axis=-1)
    ultima = k - 1 - np.argmax(mascara[..., ::-1] > 0, axis=-1)
    return primera, ultima


def _mediana(a: np.ndarray, axis: int) -> np.ndarray:
    """Mediana ignorando los NaN, con un solo ordenamiento (`np.nanmedian` pasa por arreglos enmascarados y es lenta).
    NaN donde no hay ningún valor."""
    a = np.sort(a, axis=axis)                                                        # los NaN quedan al final
    n = (~np.isnan(a)).sum(axis=axis, keepdims=True)
    bajo = np.take_along_axis(a, np.maximum((n - 1) // 2, 0), axis=axis)
    alto = np.take_along_axis(a, np.maximum(n // 2, 0) - (n == 0), axis=axis)
    return np.squeeze(np.where(n > 0, 0.5 * (bajo + alto), np.nan), axis=axis)


def preparar(u: np.ndarray, y: np.ndarray, mascara: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """El único preprocesamiento del motor: lo llaman el simulador (por lotes) y el servicio (un archivo).

    u (..., K): la grilla común de tiempos, normalizada a la ventana (1 = la última lectura); y, mascara (..., U, K): las
    lecturas de cada sector en esa grilla (0 en las faltantes). Devuelve
      x (..., U, K, 4) = [u, asinh(y'), asinh(K·Δy'), asinh(mediana')] con y' = lo que el sector se aparta de la mediana entre
                         sectores, contado desde su primera lectura y dividido por e, y
                         mediana' = la mediana entre sectores / e (lo que se restó: el muro típico más el modo común);
      cov (..., U, 2)  = [log de lecturas del sector − log 100, fracción de la grilla que tiene];
      tam (..., 3)     = [log de sectores − 3, log de lecturas de la grilla − 4,5, log(e / ruido)];
      log_e (...)      = log de la escala del archivo.
    """
    y = np.asarray(y, dtype=np.float64)
    m = np.asarray(mascara) > 0
    K = y.shape[-1]
    primera, ultima = _primera_y_ultima(m)
    y0 = np.take_along_axis(y, primera[..., None], -1)
    rel = np.where(m, y - y0, np.nan)                                               # cada sector desde su primera lectura
    hay = m.any(-1)                                                                  # (..., U)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)                              # columnas o sectores sin lecturas
        mediana = _mediana(rel, axis=-2)                                         # (..., K): entre sectores, lectura por lectura
        mediana = np.where(np.isfinite(mediana), mediana, 0.0)
        resto = rel - mediana[..., None, :]
        resto = resto - np.take_along_axis(resto, primera[..., None], -1)            # de nuevo desde la primera lectura del sector
        total = np.take_along_axis(np.where(m, y, 0.0), ultima[..., None], -1)[..., 0] - y0[..., 0]
        movimiento = _mediana(np.where(hay, total, np.nan), axis=-1)            # (...): mediana del movimiento total
        d = np.diff(resto, axis=-1)                                                  # NaN si falta una de las dos lecturas
        desvio = 1.4826 * _mediana(np.abs(d - _mediana(d, axis=-1)[..., None]), axis=-1) / np.sqrt(2.0)
        ruido = _mediana(np.where(hay, desvio, np.nan), axis=-1)
    ruido = np.where(np.isfinite(ruido) & (ruido > 0), ruido, 1e-6)
    movimiento = np.where(np.isfinite(movimiento), movimiento, 0.0)
    e = np.maximum(movimiento, ruido)                                                # con piso en el ruido de lectura
    yp = np.where(m, resto, 0.0) / e[..., None, None]
    dy = np.concatenate([np.zeros_like(yp[..., :1]), np.diff(yp, axis=-1)], axis=-1)
    dy = dy * m * np.concatenate([np.zeros_like(m[..., :1]), m[..., :-1]], axis=-1)  # solo entre dos lecturas reales seguidas
    uu = np.broadcast_to(np.asarray(u, dtype=np.float64)[..., None, :], y.shape)
    med = np.broadcast_to((mediana / e[..., None])[..., None, :], y.shape)
    x = np.stack([uu, np.arcsinh(yp), np.arcsinh(K * dy), np.arcsinh(med)], axis=-1) * m[..., None]
    n = m.sum(-1)
    cov = np.stack([np.log(np.maximum(n, 1)) - np.log(100.0), n / K], axis=-1) * hay[..., None]
    sectores = hay.sum(-1)
    tam = np.stack([np.log(np.maximum(sectores, 1)) - 3.0, np.full(sectores.shape, np.log(K) - 4.5),
                    np.clip(np.log(e / ruido), -3.0, 8.0)], axis=-1)
    return x.astype(np.float32), cov.astype(np.float32), tam.astype(np.float32), np.log(e)


def cantidad(lam: np.ndarray) -> np.ndarray:
    """Lo que se decide, en una versión continua y sin empates para la cobertura: −log(u_f − 1) − 20·(1 − z).

    Es monótona en lo que importa: más alta = cede antes, y cualquier sector estable queda bajo todos los acelerados.
    lam (..., U, 4) → (..., U)."""
    return -lam[..., 1] - CASTIGO_ESTABLE * (1.0 - lam[..., 3])


def a_grilla(datos: dict) -> tuple[dict, np.ndarray, str | None]:
    """Las lecturas de cada sector llevadas a una grilla común de tiempos. Devuelve (series en la grilla, grilla, aviso).

    Si hay hasta 200 tiempos distintos, la grilla son esos tiempos. Si hay más, se adelgaza la grilla (no cada serie):
    200 tiempos a paso parejo entre la primera y la última lectura, y cada lectura va al más cercano (si dos del mismo
    sector caen en el mismo, se promedian)."""
    todos = np.unique(np.concatenate(datos["t"]))
    k_max = DISENO["lecturas"][1]
    if len(todos) <= k_max:
        return datos, todos, None
    grilla = np.linspace(todos[0], todos[-1], k_max)
    paso = grilla[1] - grilla[0]
    ts, ys = [], []
    for t, y in zip(datos["t"], datos["y"]):
        idx = np.clip(np.round((t - grilla[0]) / paso).astype(int), 0, k_max - 1)
        cuales = np.unique(idx)
        ts.append(grilla[cuales]); ys.append(np.array([y[idx == c].mean() for c in cuales]))
    aviso = f"el archivo trae {len(todos)} tiempos de lectura y respondo con {k_max} a paso parejo"
    return {**datos, "t": ts, "y": ys}, grilla, aviso


def en_la_grilla(datos: dict, grilla: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(y, mascara) de forma (sectores, len(grilla)): cada lectura en su columna, 0 en las faltantes."""
    y = np.zeros((len(datos["t"]), len(grilla)), dtype=np.float64)
    mascara = np.zeros_like(y)
    for j, (t, v) in enumerate(zip(datos["t"], datos["y"])):
        idx = np.searchsorted(grilla, t)
        y[j, idx], mascara[j, idx] = v, 1.0
    return y, mascara


def normalizar_tiempo(grilla: np.ndarray) -> tuple[np.ndarray, float, float]:
    """(u, inicio, ventana): la ventana parte un paso antes de la primera lectura, como en el simulador (u_k = k/K)."""
    paso = float(np.median(np.diff(grilla))) if len(grilla) > 1 else 1.0
    inicio = float(grilla[0]) - paso
    ventana = float(grilla[-1]) - inicio
    return (grilla - inicio) / ventana, inicio, ventana


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """Lo propio del motor en la respuesta de `analizar`: por sector, la probabilidad de ceder dentro del horizonte y su curva."""
    col = caso["columnas"]
    unidad_t = col.get("unidad_tiempo", "horas")
    try:
        datos = series.leer(caso)
        horizonte = float(col["horizonte"])
        if not all(np.isfinite(v).all() for v in datos["y"]) or not all(np.isfinite(t).all() for t in datos["t"]):
            raise ArchivoNoCalza("Hay lecturas sin número (vacías o con texto) en el tiempo o en el desplazamiento.")
        datos, grilla, aviso_grilla = a_grilla(datos)
        if len(grilla) < DISENO["lecturas"][0]:
            raise ArchivoNoCalza(f"La ventana tiene {len(grilla)} lecturas por sector y {PRACTICA}.")
        k_min = max(MIN_LECTURAS_SECTOR, math.ceil(len(grilla) * (1 - FALTANTES_TOLERADAS)))
        datos, aviso = series.revisar_tamano(caso, datos, {"unidades": DISENO["unidades"], "lecturas": (k_min, len(grilla))}, PRACTICA)
        if horizonte <= 0:
            raise ArchivoNoCalza("El horizonte del caso tiene que ser mayor que cero.", "rojo_modelo")
    except ArchivoNoCalza as error:
        return series.lector.rojo(caso, error)
    avisos = [a.rstrip(".") for a in (aviso_grilla, aviso) if a]
    y, mascara = en_la_grilla(datos, grilla)
    u, inicio, ventana = normalizar_tiempo(grilla)
    x, cov, tam, log_e = preparar(u, y, mascara)
    eta, lam, impl = series.posterior(MOTOR_ID, caso, x, mascara, cov, tam)          # (m, d), (m, l, U, 4)
    h = horizonte / ventana
    acelera, log_falta = lam[..., 3] > 0.5, lam[..., 1]
    muestras_p = (acelera & (log_falta <= np.log(h))).mean(axis=1).T                   # (U, m): P(cede en el horizonte | η_i, datos)
    e = float(np.exp(log_e))
    curvas = []
    for j, (tj, yj) in enumerate(zip(datos["t"], datos["y"])):
        u_banda = np.linspace(1.0, 1.0 + h, series.PUNTOS_BANDA)
        args = [lam[:, :, j, c, None] for c in range(4)]
        d = trayectoria(u_banda, *args) - trayectoria(np.array([1.0]), *args)           # lo que se mueve desde ahora
        ancla = float(np.mean(yj[-3:]))
        banda = ancla + e * np.minimum(d, TOPE_BANDA).reshape(-1, len(u_banda))
        marca = None
        if acelera[:, :, j].mean() >= 0.5:
            falta = (np.exp(log_falta[:, :, j][acelera[:, :, j]]) * ventana)
            bajo, medio, alto = (round(float(v), 1) for v in np.quantile(falta, [0.05, 0.5, 0.95]))
            texto = lambda v: f"{v:.0f}" if v >= 10 else f"{v:.1f}".replace(".", ",")     # noqa: E731
            marca = {"texto": f"Faltan entre {texto(bajo)} y {texto(alto)} {unidad_t}", "bajo": bajo, "medio": medio, "alto": alto}
        curvas.append(series.curva(tj, yj, inicio + u_banda * ventana, banda, caso, None, marca=marca, decimales=2))
    p = PRIOR
    globales = {"fraccion_acelerando": (eta[:, 0], -1.670, 1.056),          # logit π con π ~ Beta(1,5; 6): media ψ(1,5) − ψ(6), desviación √(ψ'(1,5) + ψ'(6))
                "falta_para_ceder": (eta[:, 3], p["mu_f_media"], p["mu_f_desv"]),
                "ruido": (eta[:, 6] - eta[:, 1], p["sigma_e_media"] - p["mu_v_media"], float(np.hypot(p["sigma_e_desv"], p["mu_v_desv"])))}
    ids = datos["ids"]
    return {
        "implementacion": impl,
        "unidades": series.unidades(ids, muestras_p, costos, curvas),
        "factores": series.factores(caso, globales),
        "columnas": {"usadas": [col["unidad"], col["tiempo"], col["valor"]], "disponibles": col.get("disponibles", 3),
                     "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "semaforo": {"estado": "amarillo" if avisos else "verde", "motivo": ("; ".join(avisos).capitalize() + ".") if avisos else "", "propuesta": None},
        "examen": series.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{len(ids)} {caso['unidad']['plural']}", f"{series.numero(int(mascara.sum()))} lecturas",
                     f"{series.MUESTRAS_ETA} versiones creíbles"],
    }
