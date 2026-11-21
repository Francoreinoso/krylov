"""Valida la red de `desgaste` sin el MCMC de referencia y escribe su sello (`WORKPLAN.md`, 11.8).

    uv run python -m motor.desgaste.validar --sbc 200          # prueba de humo: no escribe el sello
    uv run python -m motor.desgaste.validar                    # 2.000 datasets nuevos; escribe sello.json y validacion.json

SBC global y local, cobertura de lo que se decide (fallar antes de la mantención, en su versión continua: el margen sobre el límite) por tramos de tamaño,
latencia de un análisis y examen con la verdad escondida del archivo del demo. Los campos `mcmc_*` quedan en `null`
hasta que se corra `motor/desgaste/mcmc.py (A-36)`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from motor.desgaste import simular
from motor.comun import validacion
from motor.comun.series import cargar_red, sbc, sello

CARPETA = Path("motor/artefactos") / simular.MOTOR_ID
LIMITACIONES = [
    "Entre 8 y 120 camiones, cada uno con 3 a 20 muestras",
    "Camiones con 500 a 3.000 horas de operación y de 50 a 1.000 horas hasta su mantención",
    "Un solo indicador de desgaste por camión, con la falla en un límite conocido",
    "Una sola covariable (la exigencia de la ruta), ya estandarizada",
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
        os.environ["KRYLOV_MOTOR_DESGASTE"] = "red"
        from nucleo import api
        latencia, respuesta = validacion.mejor_de_3(lambda: api.analizar("flota"))
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
