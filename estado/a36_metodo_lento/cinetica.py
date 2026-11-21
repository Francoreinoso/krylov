"""MCMC de referencia del motor `cinetica`: NUTS (NumPyro) sobre η y los λ_b de cada línea.

El mismo modelo que `motor/cinetica/simular.py` (`WORKPLAN.md`, 11.3): prior de η, jerarquía de log k_b y logit Rmax_b, y
y_bk = R_b(t_k) + ε con ε ~ Normal(0, σ_y). El simulador recorta y a [0,001; 0,999]: aquí la verosimilitud es censurada
en esos dos bordes. Los pisos y recortes numéricos del prior (σ_k, σ_R ≥ 0,001; φ en [0,0001; 0,9999]) no se replican:
tienen probabilidad despreciable. El diseño (tiempos, celdas medidas, final de la línea) es dato.
"""
from __future__ import annotations

import sys
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402
from nucleo import series  # noqa: E402
from nucleo.casos import cargar_caso  # noqa: E402
from nucleo.cinetica import DISENO, PRACTICA, PRIOR as P, RAZON_LENTA, preparar  # noqa: E402

MOTOR_ID = "cinetica"
BAJO, ALTO = 0.001, 0.999


def modelo(t, y, mascara):
    U = t.shape[0]
    mu_k = numpyro.sample("mu_k", dist.Normal(P["mu_k_media"], P["mu_k_desv"]))
    sigma_k = numpyro.sample("sigma_k", dist.HalfNormal(P["sigma_k_escala"]))
    mu_R = numpyro.sample("mu_R", dist.Normal(P["mu_R_media"], P["mu_R_desv"]))
    sigma_R = numpyro.sample("sigma_R", dist.HalfNormal(P["sigma_R_escala"]))
    phi = numpyro.sample("phi", dist.Beta(P["phi_a"], P["phi_b"]))
    log_sigma_y = numpyro.sample("log_sigma_y", dist.Normal(P["sigma_y_media"], P["sigma_y_desv"]))
    with numpyro.plate("lineas", U):
        z_k = numpyro.sample("z_k", dist.Normal(0.0, 1.0))
        z_R = numpyro.sample("z_R", dist.Normal(0.0, 1.0))
    log_k, logit_rmax = mu_k + sigma_k * z_k, mu_R + sigma_R * z_R
    k = jnp.exp(log_k)[:, None]
    R = jnp.reciprocal(1.0 + jnp.exp(-logit_rmax))[:, None] * (1.0 - phi * jnp.exp(-k * t) - (1.0 - phi) * jnp.exp(-k * t / RAZON_LENTA))
    normal = dist.Normal(R, jnp.exp(log_sigma_y))
    log_l = jnp.where(y <= BAJO, jnp.log(jnp.clip(normal.cdf(BAJO), 1e-300)),
                      jnp.where(y >= ALTO, jnp.log(jnp.clip(1.0 - normal.cdf(ALTO), 1e-300)), normal.log_prob(y)))
    numpyro.factor("verosimilitud", (log_l * mascara).sum())
    numpyro.deterministic("eta", jnp.stack([mu_k, jnp.log(sigma_k), mu_R, jnp.log(sigma_R), jnp.log(phi) - jnp.log1p(-phi), log_sigma_y]))
    numpyro.deterministic("lam", jnp.stack([log_k, logit_rmax], axis=-1))


def a_eta_lam(muestras, datos):
    return np.asarray(muestras["eta"]), np.asarray(muestras["lam"])


def _datos(t, y, mascara):
    return {"t": jnp.asarray(t, dtype=jnp.float64), "y": jnp.asarray(y, dtype=jnp.float64), "mascara": jnp.asarray(mascara, dtype=jnp.float64)}


def datos_del_caso(nombre):
    """Las mismas lecturas que usa `nucleo.cinetica.analizar` con el archivo del caso."""
    caso = cargar_caso(nombre)
    leido, _ = series.revisar_tamano(caso, series.leer(caso), DISENO, PRACTICA)
    t, mascara = series.con_relleno(leido["t"])
    y, _ = series.con_relleno(leido["y"])
    x, cov, tam = preparar(t, y, mascara, np.float64(caso["columnas"]["tiempo_final"]))
    return _datos(t, y, mascara), {"x": x, "mascara": mascara, "cov": cov, "tam": tam}, {"ids": np.array(leido["ids"])}


def datos_simulados(i):
    from motor.cinetica.simular import simular
    sim = simular(np.random.default_rng([2026, i]), 1)
    return (_datos((sim["t"] * sim["mascara"])[0], sim["y"][0], sim["mascara"][0]),
            {"x": sim["x"][0], "mascara": sim["mascara"][0], "cov": sim["cov"][0], "tam": sim["tam"][0]},
            {"eta_verdadero": sim["eta"][0], "lam_verdadero": sim["lam"][0]})


if __name__ == "__main__":
    comun.principal(sys.modules[__name__])
