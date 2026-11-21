"""Valida la red de `cinetica` sin el MCMC de referencia y escribe su sello (`WORKPLAN.md`, 11.8).

    uv run python -m motor.cinetica.validar --sbc 200          # prueba de humo: no escribe el sello
    uv run python -m motor.cinetica.validar                    # 2.000 datasets nuevos; escribe sello.json y validacion.json

SBC global y local, cobertura de lo que se decide (la recuperación al final de la línea) por tramos de tamaño,
latencia de un análisis y examen con la verdad escondida del archivo del demo. Los campos `mcmc_*` quedan en `null`
hasta que se corra `motor/cinetica/mcmc.py`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from motor.cinetica import simular
from motor.comun import validacion
from motor.comun.series import cargar_red, sbc, sello

CARPETA = Path("motor/artefactos") / simular.MOTOR_ID
LIMITACIONES = [
    "Entre 2 y 16 líneas, cada una medida en 3 a 12 celdas",
    "Celdas de 2 a 6 minutos; el cobre recuperado va entre 0 y 1",
    "La fracción lenta flota 8 veces más lento que la rápida (fijo)",
    "Una sola fracción rápida para toda la planta",
    "Sin comparación todavía con el método lento",
]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sbc", type=int, default=2000, help="datasets simulados nuevos")
    p.add_argument("--punto", type=Path, default=None)
    a = p.parse_args()
    red, progreso = cargar_red(simular, a.punto)
    informe = sbc(simular, red, datasets=a.sbc)
    ensayo = a.sbc < 1000 or not progreso["entrenada"]
    latencia, examen = None, None
    if (CARPETA / "codificador.onnx").exists():
        os.environ["KRYLOV_MOTOR_CINETICA"] = "red"
        from nucleo import api
        latencia, respuesta = validacion.mejor_de_3(lambda: api.analizar("flotacion"))
        examen = respuesta.get("examen")
    ficha = sello(simular, informe, progreso, latencia, examen, LIMITACIONES, ensayo=ensayo)
    if ensayo:
        print(json.dumps({k: informe[k] for k in ("datasets", "sbc_global_pasa", "sbc_global_fallan", "sbc_local_pasa", "sbc_local_fallan",
                                                  "cobertura_90_parametros", "cobertura_90_locales", "cobertura_90_decision", "por_tramo")},
                         indent=1, ensure_ascii=False))
        print("ensayo: no se escribe el sello")
        return
    validacion.escribir(CARPETA, ficha, informe)


if __name__ == "__main__":
    main()
