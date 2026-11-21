"""Exporta la red de `deformacion` a `motor/artefactos/deformacion/` (ONNX + dos flujos en npz + config.json).

    uv run python -m motor.deformacion.exportar            # el último punto de guardado
    uv run python -m motor.deformacion.exportar --prueba   # la red sin entrenar, a una carpeta temporal: solo comprueba que exporta
"""

import sys
import tempfile
from pathlib import Path

from motor.deformacion import simular
from motor.comun.series import cargar_red, exportar

if __name__ == "__main__":
    if "--prueba" in sys.argv:
        red, progreso = cargar_red(simular, Path("no-existe"))
        print(exportar(simular, red, Path(tempfile.mkdtemp()), progreso))
    else:
        red, progreso = cargar_red(simular)
        print(exportar(simular, red, Path("motor/artefactos") / simular.MOTOR_ID, progreso), progreso)
