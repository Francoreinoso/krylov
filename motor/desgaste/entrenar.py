"""Entrena la red del motor `desgaste` con flotas simuladas al vuelo (tamaño sorteado en cada lote).

    caffeinate -dims uv run python -m motor.desgaste.entrenar --hasta 18:15 --guardar-cada-min 10

Se retoma solo desde `motor/checkpoints/desgaste/ultimo.pt`; `--nuevo` parte de cero.
"""

from motor.desgaste import simular
from motor.comun.series import entrenar_motor

if __name__ == "__main__":
    entrenar_motor(simular)
