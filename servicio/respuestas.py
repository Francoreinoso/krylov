"""Las respuestas del demo: las de `nucleo/api.py` y, si un motor todavía no responde, el ejemplo fijo.

Es la única tabla entre una petición y su respuesta. La usan `servicio.app` y
`servicio.exportar_estatico`, así la API y el modo estático devuelven siempre lo mismo.
El ejemplo fijo trae `_aviso`, así se distingue de una respuesta de un motor.
"""

from nucleo import api as nucleo
from servicio import fijos


def _o_fijo(respuesta: dict, fijo, *args) -> dict:
    return fijo(*args) if "error" in respuesta else respuesta


def casos() -> dict:
    return _o_fijo(nucleo.casos(), fijos.casos)


def analizar(caso: str, transformaciones=(), costos: dict | None = None, mediciones=()) -> dict:
    return _o_fijo(nucleo.analizar(caso, list(transformaciones), costos, list(mediciones)),
                   fijos.analizar, caso, transformaciones, mediciones)


def cartera(caso: str) -> dict:
    return _o_fijo(nucleo.cartera(caso), fijos.cartera, caso)


def donde_medir(caso: str, mediciones=()) -> dict:
    return _o_fijo(nucleo.donde_medir(caso, list(mediciones)), fijos.donde_medir, caso, mediciones)


def nube(caso: str, transformaciones=()) -> dict:
    return _o_fijo(nucleo.nube(caso, list(transformaciones)), fijos.nube, caso, transformaciones)


def sello(motor_id: str) -> dict:
    return _o_fijo(nucleo.sello(motor_id), fijos.sello, motor_id)
