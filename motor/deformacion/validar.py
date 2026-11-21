"""Valida la red de `deformacion` sin el MCMC de referencia y escribe su sello (`WORKPLAN.md`, 11.8).

    uv run python -m motor.deformacion.validar --sbc 200          # prueba de humo: no escribe el sello
    uv run python -m motor.deformacion.validar                    # 2.000 datasets nuevos; escribe sello.json y validacion.json

SBC global y local, cobertura de lo que se decide (ceder dentro del horizonte, en su versión continua −log(u_f − 1) − 20·(1 − z)) por tramos de tamaño,
latencia de un análisis y examen con la verdad escondida del archivo del demo. Los campos `mcmc_*` quedan en `null`
hasta que se corra `motor/deformacion/mcmc.py (A-36)`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from motor.deformacion import simular
from motor.comun import validacion
from motor.comun.series import cargar_red, sbc, sello

CARPETA = Path("motor/artefactos") / simular.MOTOR_ID
LIMITACIONES = [
    "Entre 6 y 80 sectores, cada uno con 24 a 200 lecturas en la ventana y hasta 15% faltantes",
    "Dos regímenes por sector: estable (velocidad constante) o acelerando hacia la falla con la ley de velocidad inversa",
    "Un sector que se acelera y después frena no está en las reglas",
    "El modo común se resta con la mediana entre sectores: si la mitad del muro se acelera a la vez, se confunde con él",
    "En los sectores que se aceleran, la red tiende a dar una velocidad de fondo algo alta y un «cuánto falta» algo corto: el lado prudente (medido el sáb 16:28 con 1,7 millones de muros simulados)",
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
        os.environ["KRYLOV_MOTOR_DEFORMACION"] = "red"
        from nucleo import api
        latencia, respuesta = validacion.mejor_de_3(lambda: api.analizar("taludes"))
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
