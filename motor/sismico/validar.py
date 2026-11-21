"""Valida la red de `sismico` sin el MCMC de referencia y escribe su sello (`WORKPLAN.md`, 11.8).

    uv run python -m motor.sismico.validar --sbc 200          # prueba de humo: no escribe el sello
    uv run python -m motor.sismico.validar                    # 2.000 datasets nuevos; escribe sello.json y validacion.json

SBC global y local, cobertura de lo que se decide (un sismo fuerte en el horizonte, en su versión continua: el log del número esperado) por tramos de tamaño,
latencia de un análisis y examen con la verdad escondida del archivo del demo. Los campos `mcmc_*` quedan en `null`
hasta que se corra `motor/sismico/mcmc.py (A-36)`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from motor.sismico import simular
from motor.comun import validacion
from motor.comun.series import cargar_red, sbc, sello

CARPETA = Path("motor/artefactos") / simular.MOTOR_ID
LIMITACIONES = [
    "Entre 2 y 16 sectores, observados de 2 a 24 horas desde la tronadura, con hasta 300 sismos por sector",
    "La probabilidad de un sismo fuerte usa una aproximación de Poisson sobre el número esperado (forma cerrada del núcleo exponencial)",
    "Solo el tiempo: no usa la ubicación de cada sismo dentro del sector",
    "Los sectores no se gatillan entre sí",
    "Apoya la decisión del especialista sobre el reingreso; no la reemplaza",
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
        os.environ["KRYLOV_MOTOR_SISMICO"] = "red"
        from nucleo import api
        latencia, respuesta = validacion.mejor_de_3(lambda: api.analizar("sismicidad"))
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
