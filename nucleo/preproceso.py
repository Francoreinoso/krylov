"""Preprocesamiento único: la misma función transforma los datos simulados y los reales.

Regla del proyecto: el simulador de entrenamiento (`motor/`, en torch) y el servicio
(`nucleo/`, en NumPy) pasan los datos por **la misma función**. Si difirieran, la red
recibiría en vivo algo que nunca vio al entrenar y fallaría sin avisar.

Por eso `canales_terreno` está escrita solo con operaciones que NumPy y torch comparten
(suma, división, `clip`, potencia): recibe arreglos de cualquiera de los dos y devuelve
lo mismo. `motor/espacial/prueba_simular.py` pasa el mismo arreglo por los dos caminos.

Lo que sigue en este archivo (geometría de la grilla, acumulación de puntos) solo se usa
con datos reales y es NumPy puro: el simulador genera las mediciones ya en celdas.
"""

from __future__ import annotations

import numpy as np

VERSION = "espacial-1"   # va en config.json: si cambia el preprocesamiento, cambia la versión
LADO = 32                # la grilla fija del motor espacial es de LADO × LADO bloques
ESCALA_MINIMA = 1e-3


def canales_terreno(suma, cuenta, raiz_dist):
    """Los tres canales de entrada de la red del terreno, desde las mediciones acumuladas por bloque.

    suma:      (..., LADO, LADO) suma de los valores medidos que cayeron en cada bloque.
    cuenta:    (..., LADO, LADO) cuántas mediciones cayeron en cada bloque (0 si ninguna).
    raiz_dist: (..., LADO, LADO) raíz de la distancia normalizada al río, o ceros si no hay tendencia.

    Si varias mediciones caen en un bloque se promedian. El valor se estandariza con el
    promedio y la desviación estándar **de lo medido**; los bloques sin medición valen 0.

    Devuelve ((valor, marca, raiz_dist), media, escala): los tres canales, y la media y la
    escala (con forma (..., 1, 1)) para llevar umbrales y parámetros al mismo espacio.
    Funciona igual con arreglos de NumPy y con tensores de torch.
    """
    marca = cuenta.clip(0, 1)                                  # 1 si el bloque tiene medición
    promedio = suma / cuenta.clip(1, None)
    n = marca.sum((-2, -1), keepdims=True).clip(1, None)
    media = (promedio * marca).sum((-2, -1), keepdims=True) / n
    varianza = (((promedio - media) ** 2) * marca).sum((-2, -1), keepdims=True) / n
    escala = (varianza ** 0.5).clip(ESCALA_MINIMA, None)
    valor = (promedio - media) / escala * marca
    return (valor, marca, raiz_dist), media, escala


# ---------------------------------------------------------------------------------------
# Solo datos reales (NumPy): de puntos con coordenadas a mediciones acumuladas por bloque.
# ---------------------------------------------------------------------------------------

def transformar_valor(valor, transformacion: str | None):
    """Transformación que pide el caso (`log` para el zinc). El umbral pasa por la misma."""
    if transformacion in (None, "", "ninguna"):
        return np.asarray(valor, dtype=np.float64)
    if transformacion == "log":
        return np.log(np.asarray(valor, dtype=np.float64))
    raise ValueError(f"Transformación desconocida: {transformacion!r}")


def geometria_grilla(x, y, lado: int = LADO) -> dict:
    """Grilla cuadrada de `lado` × `lado` bloques que cubre los puntos, con una sola escala para los dos ejes."""
    x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    ancho = max(x.max() - x.min(), y.max() - y.min())
    lado_celda = ancho / lado * (1 + 1e-9) if ancho > 0 else 1.0
    return {
        "nx": lado, "ny": lado, "lado": float(lado_celda),
        "x0": float((x.min() + x.max()) / 2 - lado * lado_celda / 2),
        "y0": float((y.min() + y.max()) / 2 - lado * lado_celda / 2),
    }


def indices_bloque(x, y, geo: dict) -> tuple[np.ndarray, np.ndarray]:
    """(fila, columna) del bloque de cada punto. La fila 0 es la de más abajo (y menor)."""
    columna = np.floor((np.asarray(x, dtype=np.float64) - geo["x0"]) / geo["lado"]).astype(int)
    fila = np.floor((np.asarray(y, dtype=np.float64) - geo["y0"]) / geo["lado"]).astype(int)
    return fila.clip(0, geo["ny"] - 1), columna.clip(0, geo["nx"] - 1)


def acumular_por_bloque(fila, columna, valor, lado: int = LADO) -> tuple[np.ndarray, np.ndarray]:
    """Suma y cuenta de las mediciones por bloque: la entrada de `canales_terreno`."""
    suma, cuenta = np.zeros((lado, lado), dtype=np.float32), np.zeros((lado, lado), dtype=np.float32)
    np.add.at(suma, (fila, columna), np.asarray(valor, dtype=np.float32))
    np.add.at(cuenta, (fila, columna), 1.0)
    return suma, cuenta


def canal_tendencia(x, y, dist, geo: dict) -> tuple[np.ndarray, np.ndarray]:
    """Raíz de la distancia al río por bloque, desde la grilla fina del caso (`x`, `y`, `dist`).

    Devuelve (raiz_dist, dentro): el promedio de √dist de las celdas finas de cada bloque, y
    qué bloques pertenecen al terreno. Los bloques de fuera se rellenan con el del bloque de
    dentro más cercano, para que la red no vea un borde artificial.
    """
    fila, columna = indices_bloque(x, y, geo)
    suma, cuenta = acumular_por_bloque(fila, columna, np.sqrt(np.asarray(dist, dtype=np.float64)), geo["nx"])
    dentro = cuenta > 0
    raiz = np.where(dentro, suma / np.maximum(cuenta, 1), 0.0).astype(np.float32)
    if dentro.any() and not dentro.all():
        f_in, c_in = np.nonzero(dentro)
        f_out, c_out = np.nonzero(~dentro)
        cercano = ((f_out[:, None] - f_in[None, :]) ** 2 + (c_out[:, None] - c_in[None, :]) ** 2).argmin(1)
        raiz[f_out, c_out] = raiz[f_in[cercano], c_in[cercano]]
    return raiz, dentro


def preparar_terreno(x, y, valor, transformacion: str | None = None, grilla: dict | None = None) -> dict:
    """De los puntos medidos de un caso espacial a los canales de la red.

    x, y, valor: las mediciones. `grilla`, opcional: {"x", "y", "dist"} con la distancia al
    río en cada celda fina del terreno; define la geometría y el canal de tendencia.
    Devuelve los canales (3, LADO, LADO) en float32, la media y la escala de la
    estandarización, la geometría y la máscara de bloques dentro del terreno.
    """
    if grilla is not None:
        geo = geometria_grilla(np.concatenate([grilla["x"], x]), np.concatenate([grilla["y"], y]))
        raiz_dist, dentro = canal_tendencia(grilla["x"], grilla["y"], grilla["dist"], geo)
    else:
        geo = geometria_grilla(x, y)
        raiz_dist, dentro = np.zeros((LADO, LADO), dtype=np.float32), np.ones((LADO, LADO), dtype=bool)
    fila, columna = indices_bloque(x, y, geo)
    suma, cuenta = acumular_por_bloque(fila, columna, transformar_valor(valor, transformacion))
    (v, m, r), media, escala = canales_terreno(suma, cuenta, raiz_dist)
    return {
        "canales": np.stack([v, m, r]).astype(np.float32),
        "media": float(media.reshape(())), "escala": float(escala.reshape(())),
        "geometria": geo, "dentro": dentro, "tiene_tendencia": grilla is not None,
    }
