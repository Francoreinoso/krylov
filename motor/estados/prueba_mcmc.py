"""El modelo en NumPyro de `estados`: su densidad es la de NumPy, y NUTS da unos pasos.

No es una corrida de MCMC (eso se hace sin nada entrenando): una evaluación de la densidad
y un puñado de pasos sobre una cartera chica.
"""

import jax.numpy as jnp
import numpy as np
from numpyro.infer.util import log_density

from motor.estados import mcmc, simular
from nucleo import estados


def _cartera(n: int = 120):
    lote = simular.simular(np.random.default_rng(5), 1, n)
    return {k: lote[k][0] for k in mcmc.VARIABLES}, lote["impago"][0], lote["theta"][0]


def test_densidad_igual_a_numpy():
    """La verosimilitud en JAX es la misma función que en NumPy (el filtro forward de nucleo/estados.py)."""
    datos, impago, _ = _cartera()
    z = np.random.default_rng(0).normal(0, 0.7, estados.DIM_THETA)
    log_p, _ = log_density(mcmc.modelo, (mcmc.a_jax(datos), jnp.asarray(impago)), {}, {"z": jnp.asarray(z)})
    directo = (-0.5 * z ** 2 - 0.9189385332046727).sum() + estados.log_verosimilitud(simular.MEDIAS + simular.DESVS * z, datos, impago)
    assert abs(float(log_p) - directo) < 1e-6 * abs(directo)


def test_nuts_da_unos_pasos():
    datos, impago, _ = _cartera()
    r = mcmc.correr(datos, impago, calentamiento=30, muestras=20, cadenas=1)
    assert r["theta"].shape == (20, estados.DIM_THETA) and np.isfinite(r["theta"]).all()
    d = estados.a_restringido(r["theta"])["d"]
    assert (np.diff(d, axis=-1) > 0).all()
