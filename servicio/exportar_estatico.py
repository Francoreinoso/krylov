"""Escribe en web/public/estatico/ cada respuesta que el recorrido del demo puede pedir.

Correr (configuración del H2): KRYLOV_MOTOR_ESPACIAL=red KRYLOV_MOTOR_SUPERVIVENCIA=mcmc uv run python -m servicio.exportar_estatico
"""

import json
import shutil
from pathlib import Path

from nucleo import api as nucleo
from servicio import fijos, respuestas
from servicio.calce import calce_del_demo
from servicio.interpretar import interpretar

DESTINO = Path(__file__).resolve().parent.parent / "web" / "public" / "estatico"
CORRECCION = ["quitar_factor:fecha_salida"]


def _escribir(ruta: str, datos: dict) -> None:
    archivo = DESTINO / f"{ruta}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def _analisis(clave: str, datos: dict) -> int:
    """La respuesta y su interpretación, precalculada y rotulada. Solo la de Claude se sube; si no, la plantilla."""
    _escribir(f"analizar/{clave}", datos)
    _escribir(f"interpretar/{clave}", {**interpretar(datos, solo_claude=True), "precalculado": True})
    return 2


def exportar() -> int:
    shutil.rmtree(DESTINO, ignore_errors=True)
    lista = respuestas.casos()
    _escribir("casos", lista)
    n = 1
    for c in lista["casos"]:
        nombre = c["nombre"]
        n += _analisis(nombre, respuestas.analizar(nombre))
        if c["tiene_cartera"]:
            _escribir(f"cartera/{nombre}", respuestas.cartera(nombre))
            n += 1
        if c["motor"] == "espacial":
            _escribir(f"donde-medir/{nombre}", respuestas.donde_medir(nombre))
            n += 1
        _escribir(f"sello/{c['motor']}", respuestas.sello(c["motor"]))
        _escribir(f"papeles/{c['motor']}", nucleo.papeles(c["motor"]))
        _escribir(f"calce/{nombre}", calce_del_demo(nombre))
        n += 3
    # El arco rojo → corrección → verde del archivo malo.
    for t in ([], CORRECCION):
        clave = fijos.clave("rotacion_malo", t)
        n += _analisis(clave, respuestas.analizar("rotacion_malo", t))
        _escribir(f"nube/{clave}", respuestas.nube("rotacion_malo", t))
        n += 1
    return n


if __name__ == "__main__":
    print(f"{exportar()} archivos en {DESTINO}")
