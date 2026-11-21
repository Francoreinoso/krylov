"""El modelo en NumPyro de `espacial`: su densidad coincide con la cuenta directa, y NUTS da unos pasos.

No es una corrida de MCMC (eso se hace sin nada entrenando): es una evaluación de la
densidad y un puñado de pasos sobre un terreno chico.
"""

import math

import jax.numpy as jnp
import numpy as np
import torch
from numpyro.infer.util import log_density

from motor.espacial import mcmc
from motor.espacial.simular import Prior, simular
from nucleo import espacial


def _terreno_chico(n_maximo: int = 40):
    lote = simular(1, Prior(n_min=30, n_max=n_maximo), torch.Generator().manual_seed(3))
    return lote["canales"][0].numpy(), lote


def test_densidad_igual_a_la_cuenta_directa():
    canales, _ = _terreno_chico()
    datos = mcmc.datos_de_canales(canales)
    prior = Prior()
    z, m, log_s = np.array([0.3, -0.5, 0.8, 0.2, -0.4, 0.1, -1.0]), 0.2, -0.1
    log_p, _ = log_density(mcmc.modelo, (), {**datos, "prior": prior}, {"z": jnp.asarray(z), "media": m, "log_escala": log_s})

    # Directo, en NumPy: prior truncado de z + jacobiano + log-verosimilitud gaussiana con la covarianza de nucleo/espacial.py.
    medias, desvs = (np.asarray(v) for v in mcmc._medias_y_desvs(prior))
    theta = medias + desvs * z
    fila, columna, valor, raiz = (np.asarray(datos[k]) for k in ("fila", "columna", "valor", "raiz_dist"))
    n = len(valor)
    k = math.exp(2 * theta[3]) * espacial.correlacion(theta[None], fila[:, None] - fila[None, :], columna[:, None] - columna[None, :])[0]
    k = k + (math.exp(2 * theta[4]) + 1e-9) * np.eye(n)
    residuo = m + math.exp(log_s) * valor - (theta[5] + theta[6] * raiz)
    log_ver = -0.5 * (residuo @ np.linalg.solve(k, residuo) + np.linalg.slogdet(k)[1] + n * math.log(2 * math.pi))
    masa = math.erf(prior.corte / math.sqrt(2))
    log_prior = sum(-0.5 * zi ** 2 - 0.5 * math.log(2 * math.pi) - math.log(masa) for zi in z)
    assert abs(float(log_p) - (log_prior + (n - 1) * log_s + log_ver)) < 1e-6


def test_nuts_da_unos_pasos_y_devuelve_theta_estandarizado():
    canales, lote = _terreno_chico()
    r = mcmc.correr(canales, calentamiento=30, muestras=20, cadenas=1)
    assert r["theta_est"].shape == (20, 7) and np.isfinite(r["theta_est"]).all()
    # Unidades correctas: con d' estandarizado, σ' y τ' son del orden de 1 y β0' cerca de 0.
    assert abs(r["theta_est"][:, 5].mean()) < 5 and np.exp(r["theta_est"][:, 3]).mean() < 10
