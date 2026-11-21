"""Entrena la red del motor `sismico` con minas simuladas al vuelo (tamaño sorteado en cada lote).

    caffeinate -dims uv run python -m motor.sismico.entrenar --hasta 18:15 --lote 64 --guardar-cada-min 10

Se retoma solo desde `motor/checkpoints/sismico/ultimo.pt`; `--nuevo` parte de cero.
"""

from motor.sismico import simular
from motor.comun.series import entrenar_motor

if __name__ == "__main__":
    entrenar_motor(simular)
