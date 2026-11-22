"""Respuestas de ejemplo fijo (contratos/ejemplos/) para cada ruta de la API.

Es el respaldo de `servicio.respuestas` cuando un motor de `nucleo/api.py` todavía
no responde (sin red, sin MCMC precalculado o sin sello).
"""

import json
from functools import cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EJEMPLOS = RAIZ / "contratos" / "ejemplos"
INICIO = RAIZ / "casos" / "INICIO"


class PeticionInvalida(ValueError):
    """Error con frase en español para la interfaz."""

    def __init__(self, error: str, codigo: str):
        super().__init__(error)
        self.error = error
        self.codigo = codigo


@cache
def _leer(nombre: str) -> dict:
    return json.loads((EJEMPLOS / nombre).read_text(encoding="utf-8"))


def _copia(nombre: str) -> dict:
    return json.loads(json.dumps(_leer(nombre)))


def _motor_de(caso: str) -> str:
    for c in casos()["casos"]:
        if c["nombre"] == caso:
            return c["motor"]
    raise PeticionInvalida(f"No conozco el caso «{caso}».", "caso_desconocido")


def casos_del_demo_o_error(caso: str) -> None:
    if caso not in {c["nombre"] for c in casos()["casos"]}:
        raise PeticionInvalida(f"No conozco el caso «{caso}».", "caso_desconocido")


def clave(caso: str, transformaciones=(), mediciones=()) -> str:
    """Nombre del archivo estático de una petición (CONTRATO.md, sección 6)."""
    partes = [caso]
    partes += [t.replace(":", "-") for t in transformaciones]
    partes += [m["etiqueta"] if "etiqueta" in m else f"{m['x']}-{m['y']}-{m['valor']}" for m in mediciones]
    return "__".join(partes)


def casos() -> dict:
    """Las tarjetas del inicio, en el orden de casos/INICIO."""
    lineas = INICIO.read_text(encoding="utf-8").splitlines()
    orden = [l.strip() for l in lineas if l.strip() and not l.startswith("#")]
    respuesta = _copia("casos.json")
    por_nombre = {c["nombre"]: c for c in respuesta["casos"]}
    respuesta["casos"] = [por_nombre[n] for n in orden if n in por_nombre]
    return respuesta


def analizar(caso: str, transformaciones=(), mediciones=()) -> dict:
    """El mapa de ejemplo en `leyes`; en los casos de lista, el ejemplo fijo de cada uno, con curva (D-37)."""
    if _motor_de(caso) == "espacial":
        return _copia("analizar_espacial.json")
    return _copia(f"analizar_{caso}.json")


def donde_medir(caso: str, mediciones=()) -> dict:
    if _motor_de(caso) != "espacial":
        raise PeticionInvalida("«¿Dónde perforo?» solo existe en la decisión con mapa.", "sin_mapa")
    return _copia("donde_medir.json")


def nube(caso: str, transformaciones=()) -> dict:
    respuesta = _copia("nube.json")
    respuesta["caso"] = caso
    if transformaciones:
        respuesta["archivo"]["dentro"] = True
    return respuesta


def sello(motor_id: str) -> dict:
    nombre = "sello.json" if motor_id == "espacial" else f"sello_{motor_id}.json"
    if not (EJEMPLOS / nombre).exists():
        raise PeticionInvalida(f"No conozco el motor «{motor_id}».", "motor_desconocido")
    return _copia(nombre)
