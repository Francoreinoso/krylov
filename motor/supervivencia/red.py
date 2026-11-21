"""Red de `supervivencia`: codificador jerárquico del dataset y flujo normalizador condicional (NPE).

El modelo generativo (WORKPLAN.md, 11.2) es jerárquico: personas dentro de cargos dentro de una
empresa. El codificador sigue esa estructura, filas → cargo → dataset, y entrega el resumen s(D);
el flujo de acoplamiento afín de `motor/comun/flujo.py` entrega q(θ | s(D)) sobre los 32 parámetros
globales en espacio sin restricciones. La pérdida es NPE: −log q(θ | s(D)) sobre datasets simulados.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun.codificador import PoolingAtencion
from motor.comun.flujo import FlujoCondicional
from motor.supervivencia import simular
from nucleo import supervivencia as nucleo_sv

ARQUITECTURA = {"dim_oculta": 128, "dim_resumen": 128, "capas_flujo": 8, "cargos_max": simular.CARGOS_MAX}


ESCALA_COVARIANZA = 4.0     # las covarianzas entre columnas son del orden de 0,1: se llevan a orden 1


def _mlp(entrada: int, oculta: int, salida: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(entrada, oculta), nn.ReLU(), nn.Linear(oculta, salida), nn.ReLU())


class CodificadorSupervivencia(nn.Module):
    """Codificador de conjuntos jerárquico: filas → cargo → dataset. Invariante al orden de las filas
    y al nombre de los cargos, con n y número de cargos variables.

    - phi resume cada persona (fila de 11 números de `nucleo.supervivencia.armar_filas`).
    - Por cargo: promedio de sus filas y su tamaño, pasados por psi. De ahí sale la dispersión
      entre cargos (σ_u), que un promedio global no ve.
    - Dos poolings de atención hacia el dataset: uno sobre las filas y otro sobre los cargos.
    - Atajo de segundo orden: el promedio y la matriz de covarianza de las 11 columnas del dataset
      entran directo a rho. Los efectos β y λ y las cargas de las encuestas se identifican por
      covarianzas entre columnas (horas extra × renuncia, encuesta × encuesta); sin el atajo, phi
      tiene que descubrir cada producto y en las pruebas de 11 minutos no lo lograba.
    - rho junta todo, con log(n) y el número de cargos, en el resumen s(D).
    """

    def __init__(self, dim_oculta: int = 128, dim_resumen: int = 128, cargos_max: int = simular.CARGOS_MAX):
        super().__init__()
        self.cargos_max = cargos_max
        self.phi = _mlp(nucleo_sv.DIM_FILA, dim_oculta, dim_oculta)
        self.psi = _mlp(dim_oculta + 1, dim_oculta, dim_oculta)
        self.pooling_filas = PoolingAtencion(dim_oculta)
        self.pooling_cargos = PoolingAtencion(dim_oculta)
        momentos = nucleo_sv.DIM_FILA + nucleo_sv.DIM_FILA**2
        entrada_rho = self.pooling_filas.dim_salida + self.pooling_cargos.dim_salida + momentos + 2
        self.rho = nn.Sequential(nn.Linear(entrada_rho, 2 * dim_oculta), nn.ReLU(), nn.Linear(2 * dim_oculta, dim_resumen))

    def forward(self, filas: Tensor, grupo: Tensor) -> Tensor:
        """filas: (B, n, 11) float32; grupo: (B, n) enteros en 0..cargos_max−1 → s(D): (B, dim_resumen)."""
        h = self.phi(filas)                                                        # (B, n, d)
        cargos = torch.arange(self.cargos_max, device=grupo.device)
        pertenece = (grupo.unsqueeze(-1) == cargos).to(h.dtype)                    # (B, n, G)
        tamano = pertenece.sum(dim=1)                                              # (B, G)
        promedio = (pertenece.transpose(1, 2) @ h) / tamano.clamp(min=1.0).unsqueeze(-1)
        h_cargo = self.psi(torch.cat([promedio, torch.log1p(tamano).unsqueeze(-1) / 7.0], dim=-1))
        hay_cargo = (tamano > 0).to(h.dtype)
        todas = pertenece.sum(dim=-1)              # (B, n): 1 en cada fila con cargo válido
        n = tamano.sum(dim=1, keepdim=True)
        promedio_columnas = filas.mean(dim=1, keepdim=True)                        # (B, 1, 11)
        centradas = filas - promedio_columnas
        covarianza = (centradas.transpose(1, 2) @ centradas) / n.unsqueeze(-1)     # (B, 11, 11)
        junto = torch.cat(
            [
                promedio_columnas.squeeze(1),
                ESCALA_COVARIANZA * covarianza.flatten(start_dim=1),
                self.pooling_filas(h, todas),
                self.pooling_cargos(h_cargo, hay_cargo),
                torch.log(n) - 6.5,
                hay_cargo.sum(dim=1, keepdim=True) / self.cargos_max,
            ],
            dim=-1,
        )
        return self.rho(junto)


class RedSupervivencia(nn.Module):
    """Estimador neuronal del posterior: q(θ | D) = flujo(θ | codificador(D))."""

    def __init__(self, dim_oculta: int = 128, dim_resumen: int = 128, capas_flujo: int = 8,
                 cargos_max: int = simular.CARGOS_MAX):
        super().__init__()
        self.codificador = CodificadorSupervivencia(dim_oculta, dim_resumen, cargos_max)
        self.flujo = FlujoCondicional(nucleo_sv.DIM_THETA, dim_resumen, capas=capas_flujo)

    def perdida(self, filas: Tensor, grupo: Tensor, theta: Tensor) -> Tensor:
        """Pérdida NPE: −log q(θ | s(D)), promediada sobre los datasets del lote."""
        return -self.flujo.log_prob(theta, self.codificador(filas, grupo)).mean()

    @torch.no_grad()
    def muestrear(self, filas: Tensor, grupo: Tensor, m: int) -> Tensor:
        """m muestras de q(θ | D) por dataset, en espacio sin restricciones: (m, B, 32)."""
        return self.flujo.muestrear(self.codificador(filas, grupo), m)


def construir(config: dict | None = None, semilla: int = 0) -> RedSupervivencia:
    """Red sin entrenar, con la estandarización de θ fijada con 20.000 muestras del prior."""
    config = config or simular.cargar_config()
    torch.manual_seed(semilla)
    red = RedSupervivencia(**ARQUITECTURA)
    del_prior = nucleo_sv.a_libre(simular.muestrear_prior(np.random.default_rng(semilla), 20_000, config["prior"]))
    red.flujo.fijar_escala(torch.as_tensor(del_prior, dtype=torch.float32))
    return red


def lote_a_tensores(lote: dict, dispositivo: str = "cpu") -> tuple[Tensor, Tensor, Tensor]:
    """Lote del simulador (NumPy) → (filas, grupo, theta) en el dispositivo de entrenamiento."""
    return (
        torch.as_tensor(lote["filas"], device=dispositivo),
        torch.as_tensor(lote["grupo"], device=dispositivo),
        torch.as_tensor(lote["theta"], device=dispositivo),
    )
