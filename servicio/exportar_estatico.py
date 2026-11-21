"""Escribe en web/public/estatico/ cada respuesta que el recorrido del demo puede pedir.

Correr, con una variable `red` por cada motor que pasó su sello (`motor/artefactos/<motor>/sello.json`):

    KRYLOV_MOTOR_ESPACIAL=red KRYLOV_MOTOR_CINETICA=red uv run python -m servicio.exportar_estatico

Los demás motores: KRYLOV_MOTOR_DEFORMACION, KRYLOV_MOTOR_DESGASTE, KRYLOV_MOTOR_SISMICO. Sin variable, el
motor responde con su método lento precalculado si existe; si no, sale el ejemplo fijo. Al final imprime quién
responde cada tarjeta, para comprobar el rótulo antes de subir.
"""

import json
import shutil
from pathlib import Path

from nucleo import api as nucleo
from servicio import fijos, respuestas
from servicio.calce import calce_del_demo
from servicio.interpretar import interpretar

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "web" / "public" / "estatico"
CASOS = RAIZ / "casos"
# Tecla M: banda roja con el motivo. El segundo (una serie demasiado corta) se exporta solo si su caso existe.
ARCHIVOS_QUE_NO_ALCANZAN = ("leyes_pocos", "taludes_corto")


def _escribir(ruta: str, datos: dict) -> None:
    archivo = DESTINO / f"{ruta}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def _analisis(clave: str, datos: dict) -> int:
    """La respuesta y su interpretación, precalculada y rotulada. Solo la de Claude se sube; si no, la plantilla."""
    _escribir(f"analizar/{clave}", datos)
    _escribir(f"interpretar/{clave}", {**interpretar(datos, solo_claude=True), "precalculado": True})
    return 2


def _quien(datos: dict) -> str:
    """Quién responde, con las mismas reglas que el rótulo de la web (`web/src/textos.ts`, `rotuloQuien`)."""
    if "_aviso" in datos:
        return "ejemplo"
    if datos["semaforo"]["estado"].startswith("rojo"):
        return f"no responde ({datos['semaforo']['estado']})"
    return "precalculado" if datos.get("precalculado") else "red"


def _si_existe(ruta: str, pedir) -> int:
    try:
        datos = pedir()
    except Exception:  # noqa: BLE001 — lo que falta se reporta al final como no exportado
        return 0
    if "error" in datos:
        return 0
    _escribir(ruta, datos)
    return 1


def exportar() -> tuple[int, dict[str, str]]:
    shutil.rmtree(DESTINO, ignore_errors=True)
    lista = respuestas.casos()
    _escribir("casos", lista)
    _escribir("textos", respuestas.textos())
    n = 2
    quien: dict[str, str] = {}
    for c in lista["casos"]:
        nombre = c["nombre"]
        datos = respuestas.analizar(nombre)
        quien[nombre] = _quien(datos)
        n += _analisis(nombre, datos)
        if c["tiene_cartera"]:
            _escribir(f"cartera/{nombre}", respuestas.cartera(nombre))
            n += 1
        if c["motor"] == "espacial":
            donde = respuestas.donde_medir(nombre)
            # En vivo tarda más de 2 s (regla 7): se sirve precalculado, con el tiempo medido al generarlo.
            _escribir(f"donde-medir/{nombre}", {**donde, "precalculado": True})
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
    for nombre in ARCHIVOS_QUE_NO_ALCANZAN:
        datos = respuestas.analizar(nombre) if (CASOS / f"{nombre}.yaml").exists() else None
        if datos is None or "error" in datos:
            quien[nombre] = "sin exportar (falta el caso o su motor)"
            continue
        quien[nombre] = _quien(datos)
        n += _analisis(nombre, datos)
    return n, quien


if __name__ == "__main__":
    total, quien = exportar()
    print(f"{total} archivos en {DESTINO}")
    for nombre, texto in quien.items():
        print(f"  {nombre:<14} {texto}")
