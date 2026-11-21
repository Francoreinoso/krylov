"""Red del motor `estados`: codificador de conjuntos sobre los clientes y flujo condicional sobre θ (NPE).

Cada fila es el historial aplanado de un cliente (53 números, `nucleo.estados.armar_filas`).
Dado θ los clientes son independientes, así que la cartera es un conjunto: el codificador
(DeepSets con pooling de atención) es invariante al orden de las filas y admite n variable.
El flujo de acoplamiento afín entrega q(θ | s(D)) sobre los 33 parámetros en espacio sin
restricciones, estandarizados con la media y la desviación del prior.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun.codificador import CodificadorConjunto
from motor.comun.flujo import FlujoCondicional
from motor.estados import simular
from nucleo.estados import DIM_FILA, DIM_THETA

ARQUITECTURA = {"dim_fila": DIM_FILA, "dim_oculta": 128, "dim_resumen": 128, "pooling": "atencion", "capas_flujo": 8}


class RedEstados(nn.Module):
    def __init__(self):
        super().__init__()
        self.codificador = CodificadorConjunto(DIM_FILA, ARQUITECTURA["dim_oculta"], ARQUITECTURA["dim_resumen"])
        self.flujo = FlujoCondicional(DIM_THETA, ARQUITECTURA["dim_resumen"], ARQUITECTURA["capas_flujo"])
        # El prior es normal e independiente: su media y su desviación son la estandarización exacta de θ.
        self.flujo.media_theta.copy_(torch.tensor(simular.MEDIAS, dtype=torch.float32))
        self.flujo.escala_theta.copy_(torch.tensor(simular.DESVS, dtype=torch.float32))

    def resumen(self, filas: Tensor) -> Tensor:
        """filas: (B, n, 53), sin relleno (todas las carteras del lote tienen el mismo n)."""
        return self.codificador(filas, torch.ones(filas.shape[:2], device=filas.device))

    def perdida(self, filas: Tensor, theta: Tensor) -> Tensor:
        """Pérdida NPE: −log q(θ | s(D)), promediada sobre las carteras simuladas del lote."""
        return -self.flujo.log_prob(theta, self.resumen(filas)).mean()

    def muestrear(self, filas: Tensor, m: int) -> Tensor:
        return self.flujo.muestrear(self.resumen(filas), m)


def lote_a_tensores(lote: dict, dispositivo: str | torch.device = "cpu") -> tuple[Tensor, Tensor]:
    return torch.from_numpy(lote["filas"]).to(dispositivo), torch.from_numpy(np.asarray(lote["theta"], dtype=np.float32)).to(dispositivo)
