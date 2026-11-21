"""Preprocesamiento único: la misma función transforma los datos simulados y los reales.

Regla del proyecto: el simulador de entrenamiento (`motor/`, en torch) y el servicio
(`nucleo/`, en NumPy) pasan los datos por **la misma función**. Si difirieran, la red
recibiría en vivo algo que nunca vio al entrenar y fallaría sin avisar.

Por eso `canales_terreno` está escrita solo con operaciones que NumPy y torch comparten
(suma, división, `clip`, potencia): recibe arreglos de cualquiera de los dos y devuelve
lo mismo. `motor/espacial/prueba_simular.py` pasa el mismo arreglo por los dos caminos.

Lo que sigue en este archivo (geometría de la grilla, acumulación de puntos) solo se usa
con datos reales y es NumPy puro: el simulador genera las mediciones ya en celdas.

Al final están las transformaciones de columna de un archivo subido (D-35): la lista cerrada
que el calce puede nombrar. Se aplican aquí y en ningún otro lugar, antes de que el motor lea.
"""

from __future__ import annotations

import datetime as dt
import math

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
        "suma": suma, "cuenta": cuenta, "raiz_dist": raiz_dist,
    }


# ---------------------------------------------------------------------------------------
# Transformaciones de columna de un archivo subido (D-35): la lista cerrada.
# ---------------------------------------------------------------------------------------
#
# El calce (qué columna va en cada papel) puede pedir una transformación por su nombre: el
# modelo de lenguaje o el usuario solo la nombran, y el único código que toca los datos es
# este. Cada función recibe la columna como textos (así llega del CSV), la tabla completa
# (por si necesita otra columna) y sus parámetros, y devuelve la columna transformada, otra
# vez como textos. Una celda vacía sigue vacía: en la columna de respuesta, vacío es «por
# decidir». Si una celda no se puede transformar se lanza `ValueError`, y `nucleo/api.py`
# lo devuelve como semáforo `rojo_datos` con su motivo. Son deterministas.

_FORMATOS_DE_FECHA = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y", "%Y%m%d")
_SI = {"si", "sí", "s", "yes", "y", "true", "verdadero", "1", "1.0"}
_NO = {"no", "n", "false", "falso", "0", "0.0"}


def _texto(numero: float) -> str:
    """Un número como texto, sin decimales de sobra («3», no «3.0»)."""
    return str(int(numero)) if float(numero).is_integer() else repr(float(numero))


def _fecha(texto: str) -> dt.date:
    texto = texto.strip()[:10] if "T" in texto or " " in texto.strip() else texto.strip()      # con hora: solo el día
    for formato in _FORMATOS_DE_FECHA:
        try:
            return dt.datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ValueError(f"no es una fecha: {texto!r}")


def _por_celda(valores: list[str], funcion) -> list[str]:
    return ["" if v is None or not str(v).strip() else funcion(str(v).strip()) for v in valores]


def dividir(valores: list[str], tabla: dict, por: float) -> list[str]:
    """Cada número dividido por `por`: meses a años con `por=12`, pesos a miles con `por=1000`."""
    por = float(por)
    if por == 0:
        raise ZeroDivisionError("no se puede dividir por cero")
    return _por_celda(valores, lambda v: _texto(float(v) / por))


def anios_desde_fecha(valores: list[str], tabla: dict, hasta: str | None = None) -> list[str]:
    """Años transcurridos desde la fecha de cada celda hasta `hasta`: de una fecha de ingreso a la antigüedad.

    `hasta` es una fecha (la del día en que se sacaron los datos) o el nombre de otra columna con una fecha por
    fila; en una fila donde esa columna va vacía se usa la fecha más reciente de esa misma columna. Sin `hasta`,
    se cuenta hasta la fecha más reciente de la propia columna.
    """
    if hasta is not None and hasta in tabla:
        finales = [_fecha(v) if str(v).strip() else None for v in tabla[hasta]]
        ultima = max((f for f in finales if f is not None), default=None)
        finales = [f or ultima for f in finales]
    else:
        fechas = [_fecha(str(v)) for v in valores if v is not None and str(v).strip()]
        final = _fecha(str(hasta)) if hasta is not None else max(fechas, default=None)
        finales = [final] * len(valores)
    return ["" if v is None or not str(v).strip() else _texto(round((fin - _fecha(str(v))).days / 365.25, 2))
            for v, fin in zip(valores, finales)]


def dias_entre(valores: list[str], tabla: dict, desde: str) -> list[str]:
    """Días desde la fecha de la columna `desde` hasta la fecha de cada celda: de «agendó el» y «cita el» a los días de espera."""
    if desde not in tabla:
        raise KeyError(desde)
    return ["" if not str(v).strip() or not str(d).strip() else str((_fecha(str(v)) - _fecha(str(d))).days)
            for v, d in zip(valores, tabla[desde])]


def si_no_a_binario(valores: list[str], tabla: dict) -> list[str]:
    """Sí y no, en las formas usuales (sí, no, yes, true, verdadero, 1, 0…), a 1 y 0."""
    def uno(v: str) -> str:
        if v.lower() not in _SI | _NO:
            raise ValueError(f"no es un sí ni un no: {v!r}")
        return "1" if v.lower() in _SI else "0"
    return _por_celda(valores, uno)


def reescalar_ordinal(valores: list[str], tabla: dict, de: list[float], a: list[float]) -> list[str]:
    """Una escala ordinal llevada a otra, al entero más cercano: una encuesta de 1 a 5 a la de 1 a 4 con `de=[1, 5]`, `a=[1, 4]`."""
    (de_bajo, de_alto), (a_bajo, a_alto) = (float(x) for x in de), (float(x) for x in a)
    if de_alto == de_bajo:
        raise ValueError("la escala de origen no tiene rango")
    def uno(v: str) -> str:
        numero = float(v)
        if not min(de_bajo, de_alto) <= numero <= max(de_bajo, de_alto):
            raise ValueError(f"{v!r} está fuera de la escala de origen")
        return str(int(math.floor(a_bajo + (numero - de_bajo) * (a_alto - a_bajo) / (de_alto - de_bajo) + 0.5)))
    return _por_celda(valores, uno)


def logaritmo(valores: list[str], tabla: dict) -> list[str]:
    """Logaritmo natural de cada número, que tiene que ser mayor que cero."""
    return _por_celda(valores, lambda v: _texto(math.log(float(v))))


def categoria_a_codigo(valores: list[str], tabla: dict) -> list[str]:
    """Cada categoría de texto a un código entero, de 0 en adelante, en orden alfabético de las categorías."""
    codigos = {categoria: str(i) for i, categoria in enumerate(sorted({str(v).strip() for v in valores if v is not None and str(v).strip()}))}
    return _por_celda(valores, lambda v: codigos[v])


TRANSFORMACIONES = {
    "dividir": dividir, "anios_desde_fecha": anios_desde_fecha, "dias_entre": dias_entre, "si_no_a_binario": si_no_a_binario,
    "reescalar_ordinal": reescalar_ordinal, "log": logaritmo, "categoria_a_codigo": categoria_a_codigo,
}
