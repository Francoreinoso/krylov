"""El modelo en NumPyro de `jerarquico`: su densidad coincide con la cuenta directa, y NUTS da unos pasos.

No es una corrida de MCMC (eso se hace sin nada entrenando): una evaluación de la densidad y un
puñado de pasos sobre un dataset chico.
"""

import jax.numpy as jnp
import numpy as np
from numpyro.infer.util import log_density

from motor.jerarquico import mcmc, simular
from nucleo import jerarquico as jq


def _dataset():
    lote = simular.simular(np.random.default_rng(4), 1, 150, 4)
    return simular.a_filas_sueltas(lote, 0)


def test_densidad_igual_a_la_cuenta_directa():
    d = _dataset()
    rng = np.random.default_rng(0)
    n_pac, n_bar = len(d["barrio_del_paciente"]), d["barrio_del_paciente"].max() + 1
    crudo, u, v = rng.normal(0, 0.7, jq.DIM_THETA), rng.normal(0, 1, n_bar), rng.normal(0, 1, n_pac)
    log_p, _ = log_density(mcmc.modelo, mcmc.argumentos(d), {}, {"z_theta": jnp.asarray(crudo), "u_crudo": jnp.asarray(u), "v_crudo": jnp.asarray(v)})

    th = jq.a_restringido(simular.MEDIAS + simular.DESVS * crudo)
    logit = d["z"] @ th["coef"] + th["sigma_v"] * v[d["paciente"]] + th["sigma_b"] * u[d["barrio_del_paciente"][d["paciente"]]]
    conocida = ~np.isnan(d["respuesta"])
    y = np.nan_to_num(d["respuesta"])
    log_ver = (y * -np.logaddexp(0, -logit) + (1 - y) * -np.logaddexp(0, logit))[conocida].sum()
    log_normal = lambda x: (-0.5 * x ** 2 - 0.9189385332046727).sum()                  # noqa: E731
    assert abs(float(log_p) - (log_normal(crudo) + log_normal(u) + log_normal(v) + log_ver)) < 1e-8 * abs(float(log_p))


def test_nuts_da_unos_pasos():
    r = mcmc.correr(_dataset(), calentamiento=30, muestras=20, cadenas=1)
    assert r["theta"].shape == (20, jq.DIM_THETA) and np.isfinite(r["theta"]).all()
