"""Flujo normalizador condicional de acoplamiento afín: el posterior amortizado q(θ | s(D)).

Se entrena con NPE (estimación neuronal del posterior): la pérdida es −log q(θ | s(D)),
promediada sobre datasets simulados del modelo generativo. θ entra estandarizado y en
espacio sin restricciones; s(D) es el resumen que entrega el codificador del dataset.

El flujo es `zuko.flows.NICE`: capas de acoplamiento con máscara alternada fija y
transformación afín monótona. Cada capa deja intacta la mitad `a` de θ y transforma la
otra mitad `b` con un desplazamiento y una escala que salen de un MLP de (θ_a, s(D)).

`exportar_npz` escribe los pesos capa por capa; `nucleo/flujo.py` los lee y muestrea en
NumPy, sin torch. `motor/comun/prueba_flujo.py` exige que las dos implementaciones den
la misma muestra con los mismos pesos y el mismo ruido.
"""

from __future__ import annotations

import numpy as np
import torch
import zuko
from torch import Tensor, nn

PENDIENTE_MINIMA = 1e-3  # la de zuko.transforms.MonotonicAffineTransform: acota la escala de cada capa


class FlujoCondicional(nn.Module):
    """q(θ | s): flujo de acoplamiento afín condicional sobre θ estandarizado."""

    def __init__(self, dim_theta: int, dim_contexto: int = 128, capas: int = 8, ocultas: tuple[int, ...] = (128, 128)):
        super().__init__()
        self.dim_theta, self.dim_contexto = dim_theta, dim_contexto
        self.nice = zuko.flows.NICE(features=dim_theta, context=dim_contexto, transforms=capas, hidden_features=ocultas)
        # Estandarización de θ (media y desviación bajo el prior). Las fija cada motor con `fijar_escala`.
        self.register_buffer("media_theta", torch.zeros(dim_theta))
        self.register_buffer("escala_theta", torch.ones(dim_theta))

    def fijar_escala(self, theta_del_prior: Tensor) -> None:
        """Calcula la estandarización de θ con una muestra grande del prior (una vez, antes de entrenar)."""
        self.media_theta.copy_(theta_del_prior.mean(0))
        self.escala_theta.copy_(theta_del_prior.std(0).clamp_min(1e-6))

    def log_prob(self, theta: Tensor, contexto: Tensor) -> Tensor:
        """log q(θ | s) por dataset, con θ en espacio sin restricciones. La pérdida NPE es su negativo."""
        z = (theta - self.media_theta) / self.escala_theta
        return self.nice(contexto).log_prob(z) - self.escala_theta.log().sum()

    def muestrear_con_ruido(self, contexto: Tensor, ruido: Tensor) -> Tensor:
        """Lleva ruido normal estándar a muestras de q(θ | s). contexto (..., c), ruido (m, ..., d) o (..., d)."""
        z = self.nice(contexto).transform.inv(ruido)
        return z * self.escala_theta + self.media_theta

    def muestrear(self, contexto: Tensor, m: int) -> Tensor:
        """m muestras por contexto: devuelve (m, ..., d)."""
        ruido = torch.randn(m, *contexto.shape[:-1], self.dim_theta, device=contexto.device)
        return self.muestrear_con_ruido(contexto, ruido)

    def exportar_npz(self, ruta: str, **extra: np.ndarray) -> None:
        """Guarda los pesos capa por capa en el formato que lee `nucleo/flujo.py`."""
        arreglos: dict[str, np.ndarray] = {
            "media_theta": self.media_theta.cpu().numpy(),
            "escala_theta": self.escala_theta.cpu().numpy(),
            "pendiente_minima": np.float32(PENDIENTE_MINIMA),
        }
        capas = list(self.nice.transform.transforms)
        arreglos["n_capas"] = np.int64(len(capas))
        for i, capa in enumerate(capas):
            arreglos[f"capa{i}_mascara"] = capa.mask.cpu().numpy()
            lineales = [m for m in capa.hyper if hasattr(m, "weight")]   # zuko.nn.Linear: y = x Wᵀ + b
            if len(lineales) + sum(isinstance(m, nn.ReLU) for m in capa.hyper) != len(capa.hyper):
                raise ValueError("El MLP del flujo trae capas que nucleo/flujo.py no sabe reproducir")
            arreglos[f"capa{i}_n_lineales"] = np.int64(len(lineales))
            for j, lineal in enumerate(lineales):
                arreglos[f"capa{i}_W{j}"] = lineal.weight.detach().cpu().numpy()
                arreglos[f"capa{i}_b{j}"] = lineal.bias.detach().cpu().numpy()
        np.savez(ruta, **arreglos, **extra)
