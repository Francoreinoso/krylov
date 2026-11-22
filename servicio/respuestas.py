"""Las respuestas del demo: las de `nucleo/api.py` y, si un motor todavía no responde, el ejemplo fijo.

Es la única tabla entre una petición y su respuesta. La usan `servicio.app` y
`servicio.exportar_estatico`, así la API y el modo estático devuelven siempre lo mismo.
El ejemplo fijo trae `_aviso`, así se distingue de una respuesta de un motor.
"""

from functools import cache

from nucleo import api as nucleo
from nucleo.textos import plantillas
from servicio import fijos


def _o_fijo(respuesta: dict, fijo, *args) -> dict:
    return fijo(*args) if "error" in respuesta else respuesta


def _con_sello(respuesta: dict, motor_id: str, fijo, *args) -> dict:
    """Una respuesta de la red solo sale si el sello de su motor pasa (AGENTS.md, regla 5); si no, el ejemplo fijo.

    `rojo_datos` sale siempre: es la revisión del tamaño del archivo, antes de la red, y no depende del sello.
    """
    if "error" in respuesta or respuesta.get("implementacion") != "red":
        return _o_fijo(respuesta, fijo, *args)
    if respuesta.get("semaforo", {}).get("estado") == "rojo_datos":
        return respuesta
    sello = nucleo.sello(motor_id)
    return respuesta if sello.get("pasa") is True and not sello.get("error") else fijo(*args)


def _motor_de(caso: str) -> str | None:
    return next((c["motor"] for c in casos()["casos"] if c["nombre"] == caso), None)


def casos() -> dict:
    return _o_fijo(nucleo.casos(), fijos.casos)


@cache
def inicio() -> dict:
    """Las tarjetas que se muestran: las de `casos()` cuyo motor responde (P-27). La que pinta su ejemplo fijo sale del inicio.

    Se calcula una vez por proceso: las variables `KRYLOV_MOTOR_<ID>` y los sellos no cambian mientras corre.
    """
    todas = casos()
    return {**todas, "casos": [c for c in todas["casos"] if "_aviso" not in analizar(c["nombre"])]}


def analizar(caso: str, transformaciones=(), costos: dict | None = None, mediciones=()) -> dict:
    r = nucleo.analizar(caso, list(transformaciones), costos, list(mediciones))
    return _con_sello(r, r.get("motor_id", ""), fijos.analizar, caso, transformaciones, mediciones)


def donde_medir(caso: str, mediciones=()) -> dict:
    return _con_sello(nucleo.donde_medir(caso, list(mediciones)), _motor_de(caso) or "", fijos.donde_medir, caso, mediciones)


def nube(caso: str, transformaciones=()) -> dict:
    return _o_fijo(nucleo.nube(caso, list(transformaciones)), fijos.nube, caso, transformaciones)


def sello(motor_id: str) -> dict:
    return _o_fijo(nucleo.sello(motor_id), fijos.sello, motor_id)


def textos() -> dict:
    """Los textos de pantalla que la web dibuja por su cuenta (la curva y el chat), de `casos/textos.yaml`."""
    todas = plantillas()
    return {"curva": todas["curva"], "chat": todas.get("chat") or {}}
