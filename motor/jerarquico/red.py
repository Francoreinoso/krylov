"""Red del motor `jerarquico`: codificador de conjuntos en tres niveles y flujo condicional sobre θ (NPE).

El dataset entra anidado como lo es el modelo: barrios × pacientes × citas, con una máscara.

    cita      phi sobre la fila de la cita (26 números de `nucleo.jerarquico.armar_filas`: la matriz de diseño, las marcas de presencia de los papeles opcionales, la respuesta y la marca «por decidir»)
    paciente  pooling de atención sobre sus citas + cuántas tiene → psi.   De aquí sale σ_v: cuánto se
              parecen entre sí las citas de un mismo paciente.
    barrio    pooling de atención sobre sus pacientes + cuántos son → xi.  De aquí sale σ_b.
    dataset   pooling de atención sobre los barrios + atajo de segundo orden (promedio y covarianza de las
              26 columnas sobre todas las citas, de donde salen los efectos fijos) + log del número de
              citas y número de barrios → rho → resumen s(D) de 128.

Cada nivel es invariante al orden de sus elementos. Los poolings de atención normalizan sus pesos y
por eso no ven el tamaño del conjunto: los conteos entran aparte, porque el ancho del posterior depende de ellos.
El flujo de acoplamiento afín entrega q(θ | s(D)) sobre los 20 parámetros sin restricciones.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun.codificador import PoolingAtencion
from motor.comun.flujo import FlujoCondicional
from motor.jerarquico import simular
from nucleo.jerarquico import DIM_FILA, DIM_THETA

ARQUITECTURA = {"dim_fila": DIM_FILA, "niveles": ["cita", "paciente", "barrio"], "anchos": [64, 96, 128], "dim_resumen": 128, "capas_flujo": 8}


def _mlp(entrada: int, oculta: int, salida: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(entrada, oculta), nn.ReLU(), nn.Linear(oculta, salida), nn.ReLU())


class CodificadorJerarquico(nn.Module):
    """Codificador de conjuntos anidado: citas → paciente → barrio → dataset."""

    def __init__(self, dim_resumen: int = 128):
        super().__init__()
        self.phi = _mlp(DIM_FILA, 64, 64)
        self.pooling_citas = PoolingAtencion(64, cabezas=2)
        self.psi = _mlp(self.pooling_citas.dim_salida + 1, 96, 96)
        self.pooling_pacientes = PoolingAtencion(96, cabezas=2)
        self.xi = _mlp(self.pooling_pacientes.dim_salida + 1, 128, 128)
        self.pooling_barrios = PoolingAtencion(128, cabezas=2)
        momentos = DIM_FILA + DIM_FILA ** 2
        self.rho = nn.Sequential(nn.Linear(self.pooling_barrios.dim_salida + momentos + 2, 256), nn.ReLU(), nn.Linear(256, dim_resumen))

    def forward(self, filas: Tensor, mascara: Tensor) -> Tensor:
        """filas: (B, G, P, C, 26); mascara: (B, G, P, C) con 1 donde hay cita → resumen s(D): (B, 128)."""
        citas_del_paciente = mascara.sum(dim=-1)                                   # (B, G, P)
        hay_paciente = citas_del_paciente.clamp(max=1.0)
        pacientes_del_barrio = hay_paciente.sum(dim=-1)                            # (B, G)
        hay_barrio = pacientes_del_barrio.clamp(max=1.0)

        h = self.pooling_citas(self.phi(filas), mascara)                           # (B, G, P, ·)
        h = self.psi(torch.cat([h, citas_del_paciente.unsqueeze(-1) / 8.0], dim=-1))
        h = self.pooling_pacientes(h, hay_paciente)                                # (B, G, ·)
        h = self.xi(torch.cat([h, torch.log1p(pacientes_del_barrio).unsqueeze(-1) / 5.0], dim=-1))
        h = self.pooling_barrios(h, hay_barrio)                                    # (B, ·)

        # Atajo de segundo orden sobre todas las citas del dataset.
        sueltas, m = filas.flatten(1, 3), mascara.flatten(1, 3).unsqueeze(-1)      # (B, n, 19), (B, n, 1)
        n = m.sum(dim=1).clamp(min=1.0)                                            # (B, 1)
        promedio = (sueltas * m).sum(dim=1) / n
        centradas = (sueltas - promedio.unsqueeze(1)) * m
        covarianza = (centradas.transpose(1, 2) @ centradas) / n.unsqueeze(-1)
        junto = torch.cat([h, promedio, 4.0 * covarianza.flatten(1), torch.log(n) - 7.5, hay_barrio.sum(dim=1, keepdim=True) / 40.0], dim=-1)
        return self.rho(junto)


class RedJerarquico(nn.Module):
    def __init__(self):
        super().__init__()
        self.codificador = CodificadorJerarquico(ARQUITECTURA["dim_resumen"])
        self.flujo = FlujoCondicional(DIM_THETA, ARQUITECTURA["dim_resumen"], ARQUITECTURA["capas_flujo"])
        # El prior es normal e independiente: su media y su desviación son la estandarización exacta de θ.
        self.flujo.media_theta.copy_(torch.tensor(simular.MEDIAS, dtype=torch.float32))
        self.flujo.escala_theta.copy_(torch.tensor(simular.DESVS, dtype=torch.float32))

    def perdida(self, filas: Tensor, mascara: Tensor, theta: Tensor) -> Tensor:
        """Pérdida NPE: −log q(θ | s(D)), promediada sobre los datasets simulados del lote."""
        return -self.flujo.log_prob(theta, self.codificador(filas, mascara)).mean()

    def muestrear(self, filas: Tensor, mascara: Tensor, m: int) -> Tensor:
        return self.flujo.muestrear(self.codificador(filas, mascara), m)


def lote_a_tensores(lote: dict, dispositivo: str | torch.device = "cpu") -> tuple[Tensor, Tensor, Tensor]:
    return tuple(torch.from_numpy(np.asarray(lote[k], dtype=np.float32)).to(dispositivo) for k in ("filas", "mascara", "theta"))
