"""Escribe en web/public/estatico/ cada respuesta que el recorrido del demo puede pedir.

Correr: uv run python -m servicio.exportar_estatico
"""

import json
import shutil
from pathlib import Path

from servicio import fijos

DESTINO = Path(__file__).resolve().parent.parent / "web" / "public" / "estatico"
CORRECCION = ["quitar_factor:fecha_salida"]


def _escribir(ruta: str, datos: dict) -> None:
    archivo = DESTINO / f"{ruta}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def exportar() -> int:
    shutil.rmtree(DESTINO, ignore_errors=True)
    lista = fijos.casos()
    _escribir("casos", lista)
    n = 1
    for c in lista["casos"]:
        nombre = c["nombre"]
        _escribir(f"analizar/{nombre}", fijos.analizar(nombre))
        n += 1
        if c["tiene_cartera"]:
            _escribir(f"cartera/{nombre}", fijos.cartera(nombre))
            n += 1
        if c["motor"] == "espacial":
            _escribir(f"donde-medir/{nombre}", fijos.donde_medir(nombre))
            n += 1
        _escribir(f"sello/{c['motor']}", fijos.sello(c["motor"]))
        n += 1
    # El arco rojo → corrección → verde del archivo malo.
    for t in ([], CORRECCION):
        clave = fijos.clave("rotacion_malo", t)
        _escribir(f"analizar/{clave}", fijos.analizar("rotacion_malo", t))
        _escribir(f"nube/{clave}", fijos.nube("rotacion_malo", t))
        n += 2
    return n


if __name__ == "__main__":
    print(f"{exportar()} archivos en {DESTINO}")
