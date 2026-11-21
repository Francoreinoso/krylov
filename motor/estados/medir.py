"""Mide el rendimiento real de `estados` en este computador (skill `medir-rendimiento`). Sin nada entrenando.

    uv run python -m motor.estados.medir                          # simulador, y entrenamiento en procesador y en la GPU del Mac
    uv run python -m motor.estados.medir --dispositivos cpu --hilos 4

Datasets de tamaño fijo (1.000 clientes) para que los dispositivos se comparen sobre lo mismo.
"""

from __future__ import annotations

import argparse

import numpy as np
import torch

from motor.comun.medir import medir
from motor.estados import simular
from motor.estados.red import RedEstados, lote_a_tensores


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--dispositivos", nargs="+", default=["cpu", "mps"])
    analizador.add_argument("--lote", type=int, default=16)
    analizador.add_argument("--pasos", type=int, default=100)
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)
    rng, reales = np.random.default_rng(0), simular.cargar_covariables_reales()
    n = 1000

    def preparar(dispositivo: str):
        torch.manual_seed(0)
        red = RedEstados().to(dispositivo)
        def perdida_de(lote: dict) -> torch.Tensor:
            return red.perdida(*lote_a_tensores(lote, dispositivo))
        perdida_de.parametros = list(red.parameters())
        return perdida_de

    medir("estados", lambda: simular.simular(rng, a.lote, n, reales), preparar, a.lote, a.dispositivos, a.pasos)


if __name__ == "__main__":
    principal()
