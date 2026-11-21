"""Entrena la red del motor `cinetica` con plantas simuladas al vuelo (tamaño sorteado en cada lote).

    caffeinate -dims uv run python -m motor.cinetica.entrenar --hasta 16:10 --guardar-cada-min 10

Se retoma solo desde `motor/checkpoints/cinetica/ultimo.pt`; `--nuevo` parte de cero.
"""

from motor.cinetica import simular
from motor.comun.series import entrenar_motor

if __name__ == "__main__":
    entrenar_motor(simular)
