"""La nube: ¿el archivo se parece a las simulaciones con que practicó el motor? (WORKPLAN.md, 11.9)

Las simulaciones son el predictivo a priori del modelo generativo del motor. Si el archivo
cae fuera, el modelo está mal especificado para esos datos y el motor no responde
(`rojo_modelo`). Hay dos detectores y basta que marque uno:

1. **Ejes con nombre** (lo que se dibuja). Dos resúmenes que se dicen en palabras: qué tan
   bien adivina la respuesta el mejor factor por sí solo (su AUC), y la proporción de «sí».
   Una columna que delata la respuesta tiene AUC cerca de 1 y cae fuera por construcción.
2. **Resúmenes aprendidos** (no se dibuja). Distancia de Mahalanobis del resumen s(D) del
   archivo a los resúmenes de las simulaciones, contra su percentil 99.

Esta parte es común a los motores de tabla y solo usa NumPy. Cada motor calcula sus
simulaciones en `motor/<id>/` (con `resumir_simulaciones`, que arma `nube.npz`) y los
resúmenes de su archivo, y llama a `ubicar`.
"""

from __future__ import annotations

import numpy as np

EJES = {"x": {"nombre": "Qué tan bien adivina la respuesta el mejor factor, solo", "min": 0.5, "max": 1.0},
        "y": {"nombre": "Proporción de «sí»", "min": 0.0, "max": 1.0}}
PUNTOS_DIBUJADOS = 3000


def auc_con_signo(factor, respuesta) -> float:
    """Área bajo la curva ROC de un factor numérico contra una respuesta sí/no, por rangos (empates a medias).

    Sobre 0,5 si el factor crece con el «sí», bajo 0,5 si ordena al revés; 0,5 si falta una de las dos clases.
    """
    factor, respuesta = np.asarray(factor, dtype=np.float64), np.asarray(respuesta).astype(bool)
    positivos, negativos = int(respuesta.sum()), int((~respuesta).sum())
    if positivos == 0 or negativos == 0:
        return 0.5
    _, grupo, cuantos = np.unique(factor, return_inverse=True, return_counts=True)       # tramos de valores iguales
    rangos = (np.cumsum(cuantos) - (cuantos - 1) / 2)[grupo]                              # rango promedio de cada tramo
    return float((rangos[respuesta].sum() - positivos * (positivos + 1) / 2) / (positivos * negativos))


def auc(factor, respuesta) -> float:
    """El AUC al derecho o al revés, lo que sea mayor: entre 0,5 (no adivina nada) y 1 (adivina siempre)."""
    area = auc_con_signo(factor, respuesta)
    return float(max(area, 1 - area))


def a_numeros(valores) -> np.ndarray:
    """Una columna del archivo, leída como texto, a números. Si no es numérica, vale 1 donde hay algo y 0 donde está vacía.

    Así una columna como `fecha_salida` (una fecha o nada) entra a los ejes con nombre: lo que delata es si está o no.
    """
    try:
        return np.array([float(v) if str(v).strip() else np.nan for v in valores])
    except ValueError:
        return np.array([1.0 if str(v).strip() else 0.0 for v in valores])


def columnas_extra(caso: dict, transformaciones: list[str]) -> dict[str, np.ndarray]:
    """Las columnas `extra` del caso (no entran al modelo, sí a los ejes con nombre), menos las que una corrección quitó."""
    from nucleo.casos import leer_columnas
    quitadas = {t.removeprefix("quitar_factor:") for t in transformaciones if t.startswith("quitar_factor:")}
    nombres = [n for n in caso["columnas"].get("extra") or [] if n not in quitadas]
    if not nombres:
        return {}
    tabla = leer_columnas(caso["dataset"])
    return {n: np.nan_to_num(a_numeros(tabla[n]), nan=-1.0) for n in nombres}


def ejes_con_nombre(factores: dict[str, np.ndarray], respuesta) -> tuple[float, float, str]:
    """(AUC del mejor factor por sí solo, proporción de «sí», nombre de ese factor) de un dataset.

    `factores` incluye las columnas `extra`; se usan solo las filas con respuesta conocida.
    """
    respuesta = np.asarray(respuesta, dtype=np.float64)
    conocida = ~np.isnan(respuesta)
    si = respuesta[conocida] > 0.5
    areas = {nombre: auc(np.asarray(valores, dtype=np.float64)[conocida], si) for nombre, valores in factores.items()}
    mejor = max(areas, key=areas.get)
    return areas[mejor], float(si.mean()), mejor


def resumir_simulaciones(ejes: np.ndarray, resumenes: np.ndarray) -> dict[str, np.ndarray]:
    """Lo que guarda `nube.npz`, desde N simulaciones del predictivo a priori.

    ejes: (N, 2) los dos resúmenes con nombre. resumenes: (N, d) los resúmenes s(D) del codificador.
    Guarda una muestra de los ejes para dibujar, sus límites, y la media, la precisión y el percentil 99 de la
    distancia de Mahalanobis en el espacio de resúmenes.
    """
    ejes, resumenes = np.asarray(ejes, dtype=np.float64), np.asarray(resumenes, dtype=np.float64)
    media = resumenes.mean(axis=0)
    covarianza = np.cov(resumenes, rowvar=False) + 1e-3 * np.trace(np.cov(resumenes, rowvar=False)) / resumenes.shape[1] * np.eye(resumenes.shape[1])
    precision = np.linalg.inv(covarianza)
    distancias = mahalanobis(resumenes, media, precision)
    elegidos = np.random.default_rng(0).choice(len(ejes), size=min(PUNTOS_DIBUJADOS, len(ejes)), replace=False)
    return {"puntos": ejes[np.sort(elegidos)].astype(np.float32), "n_simulaciones": np.int64(len(ejes)),
            "x_maximo": np.quantile(ejes[:, 0], 0.995), "y_minimo": np.quantile(ejes[:, 1], 0.005), "y_maximo": np.quantile(ejes[:, 1], 0.995),
            "media": media, "precision": precision, "limite": np.quantile(distancias, 0.99)}


def mahalanobis(resumen: np.ndarray, media: np.ndarray, precision: np.ndarray) -> np.ndarray:
    diferencia = np.atleast_2d(resumen) - media
    return np.sqrt(np.einsum("ni,ij,nj->n", diferencia, precision, diferencia))


def ubicar(nube: dict, x: float, y: float, mejor_factor: str, resumen: np.ndarray | None = None) -> dict:
    """Dónde cae un archivo respecto de la nube: la parte de la respuesta de `nube` que no depende del motor.

    Devuelve `ejes`, `puntos`, `n_simulaciones`, `archivo` y `detectores` con la forma del contrato.
    `archivo.dentro` es verdadero solo si los dos detectores dicen dentro.
    """
    motivo = ""
    if x > float(nube["x_maximo"]):
        motivo = f"La columna «{mejor_factor}» adivina sola la respuesta."
    elif not float(nube["y_minimo"]) <= y <= float(nube["y_maximo"]):
        motivo = "La proporción de «sí» no se parece a la de ninguna simulación."
    con_nombre = {"dentro": motivo == "", "motivo": motivo}

    if resumen is None:
        aprendidos = {"dentro": True, "distancia": None, "limite": round(float(nube["limite"]), 2)}
    else:
        distancia = float(mahalanobis(resumen, nube["media"], nube["precision"])[0])
        aprendidos = {"dentro": distancia <= float(nube["limite"]), "distancia": round(distancia, 2), "limite": round(float(nube["limite"]), 2)}
    return {
        "n_simulaciones": int(nube["n_simulaciones"]), "ejes": EJES,
        "puntos": [[round(float(a), 3), round(float(b), 3)] for a, b in np.asarray(nube["puntos"])],
        "archivo": {"x": round(float(x), 3), "y": round(float(y), 3), "dentro": con_nombre["dentro"] and aprendidos["dentro"]},
        "detectores": {"ejes_con_nombre": con_nombre, "resumenes_aprendidos": aprendidos},
    }


def cargar(ruta) -> dict:
    with np.load(ruta) as z:
        return {k: z[k] for k in z.files}
