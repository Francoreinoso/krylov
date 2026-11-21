"""Red del motor `estados`: codificador de conjuntos sobre los clientes y flujo condicional sobre θ (NPE).

Cada fila es el historial aplanado de un cliente (53 números, `nucleo.estados.armar_filas`).
Dado θ los clientes son independientes, así que la cartera es un conjunto: el codificador es
invariante al orden de las filas y admite n variable. Tiene tres caminos hacia el resumen s(D):

- phi por cliente y pooling de atención: lo no lineal de cada historial (rachas, saltos de estado).
- Atajo de segundo orden: el promedio y la matriz de covarianza de las 53 columnas de la cartera.
  Las transiciones entre estados se leen en covarianzas entre meses vecinos (atraso de un mes ×
  atraso del siguiente), y las emisiones, en covarianzas dentro del mes; sin el atajo, phi tiene
  que descubrir cada producto.
- log(n): el pooling normaliza sus pesos y no ve el tamaño de la cartera, del que depende el
  ancho del posterior.

El flujo de acoplamiento afín entrega q(θ | s(D)) sobre los 33 parámetros en espacio sin
restricciones, estandarizados con la media y la desviación del prior.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun.codificador import PoolingAtencion
from motor.comun.flujo import FlujoCondicional
from motor.estados import simular
from nucleo.estados import DIM_FILA, DIM_THETA

ARQUITECTURA = {"dim_fila": DIM_FILA, "dim_oculta": 128, "dim_resumen": 128, "pooling": "atencion", "atajo": "promedio y covarianza",
                "capas_flujo": 8}


class CodificadorEstados(nn.Module):
    """Codificador de conjuntos de la cartera: phi por cliente, pooling de atención y atajo de segundo orden."""

    def __init__(self, dim_oculta: int = 128, dim_resumen: int = 128):
        super().__init__()
        self.phi = nn.Sequential(nn.Linear(DIM_FILA, dim_oculta), nn.ReLU(), nn.Linear(dim_oculta, dim_oculta), nn.ReLU())
        self.pooling = PoolingAtencion(dim_oculta)
        self.momentos = nn.Sequential(nn.Linear(DIM_FILA + DIM_FILA ** 2, 256), nn.ReLU())
        self.rho = nn.Sequential(nn.Linear(self.pooling.dim_salida + 256 + 1, 256), nn.ReLU(), nn.Linear(256, dim_resumen))

    def forward(self, x: Tensor, mascara: Tensor) -> Tensor:
        """x: (B, n, 53); mascara: (B, n) con 1 = cliente real → resumen s(D): (B, dim_resumen)."""
        m = mascara.unsqueeze(-1)
        n = m.sum(dim=1).clamp(min=1.0)                                            # (B, 1)
        promedio = (x * m).sum(dim=1) / n
        centradas = (x - promedio.unsqueeze(1)) * m
        covarianza = (centradas.transpose(1, 2) @ centradas) / n.unsqueeze(-1)
        atajo = self.momentos(torch.cat([promedio, 4.0 * covarianza.flatten(1)], dim=-1))
        return self.rho(torch.cat([self.pooling(self.phi(x), mascara), atajo, torch.log(n) - 7.0], dim=-1))


class RedEstados(nn.Module):
    def __init__(self):
        super().__init__()
        self.codificador = CodificadorEstados(ARQUITECTURA["dim_oculta"], ARQUITECTURA["dim_resumen"])
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
