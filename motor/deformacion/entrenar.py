"""Entrena la red del motor `deformacion` con muros simulados al vuelo (tamaño sorteado en cada lote).

    caffeinate -dims uv run python -m motor.deformacion.entrenar --hasta 16:10 --lote 32 --guardar-cada-min 10

Se retoma solo desde `motor/checkpoints/deformacion/ultimo.pt`; `--nuevo` parte de cero.
"""

from motor.deformacion import simular
from motor.comun.series import entrenar_motor

if __name__ == "__main__":
    entrenar_motor(simular)
