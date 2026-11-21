"""Escribe en web/public/estatico/ cada respuesta que el recorrido del demo puede pedir.

Correr: KRYLOV_MOTOR_ESPACIAL=red uv run python -m servicio.exportar_estatico
"""

import json
import shutil
from pathlib import Path

from nucleo import api as nucleo
from servicio import fijos, respuestas
from servicio.calce import calce_del_demo
from servicio.interpretar import interpretar

DESTINO = Path(__file__).resolve().parent.parent / "web" / "public" / "estatico"
ARCHIVO_QUE_NO_ALCANZA = "leyes_pocos"  # tecla M: banda roja con el motivo


def _escribir(ruta: str, datos: dict) -> None:
    archivo = DESTINO / f"{ruta}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def _analisis(clave: str, datos: dict) -> int:
    """La respuesta y su interpretación, precalculada y rotulada. Solo la de Claude se sube; si no, la plantilla."""
    _escribir(f"analizar/{clave}", datos)
    _escribir(f"interpretar/{clave}", {**interpretar(datos, solo_claude=True), "precalculado": True})
    return 2


def _si_existe(ruta: str, pedir) -> int:
    try:
        datos = pedir()
    except Exception:  # noqa: BLE001 — lo que falta se reporta al final como no exportado
        return 0
    if "error" in datos:
        return 0
    _escribir(ruta, datos)
    return 1


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
            donde = respuestas.donde_medir(nombre)
            _escribir(f"donde-medir/{nombre}", donde)
            n += 1
            # «¿Dónde perforo?»: el mapa rehecho con la muestra simulada en cada pin (su resultado medio).
            for p in donde.get("candidatas", []):
                medicion = {"x": p["x"], "y": p["y"], "valor": p["resultados_posibles"]["medio"], "etiqueta": p["etiqueta"]}
                n += _analisis(fijos.clave(nombre, mediciones=[medicion]), respuestas.analizar(nombre, mediciones=[medicion]))
        # Un motor que todavía no tiene sello ni papeles (los de series antes de su ronda) no los exporta:
        # sin papeles, el chat analiza directo con las columnas del caso.
        n += _si_existe(f"sello/{c['motor']}", lambda: respuestas.sello(c["motor"]))
        n += _si_existe(f"papeles/{c['motor']}", lambda: nucleo.papeles(c["motor"]))
        n += _si_existe(f"calce/{nombre}", lambda: calce_del_demo(nombre))
    n += _analisis(ARCHIVO_QUE_NO_ALCANZA, respuestas.analizar(ARCHIVO_QUE_NO_ALCANZA))
    return n


if __name__ == "__main__":
    print(f"{exportar()} archivos en {DESTINO}")
