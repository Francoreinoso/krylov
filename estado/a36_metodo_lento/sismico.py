"""MCMC de referencia del motor `sismico`: NUTS (NumPyro) sobre η y los λ_s con la verosimilitud exacta del proceso de Hawkes.

El mismo modelo que `motor/sismico/simular.py` (`WORKPLAN.md`, 11.5): prior de η, jerarquía de log μ_s, log A_s, y

    log L = Σ_s [ Σ_i log λ_s(t_i) − ∫_0^T λ_s(t) dt + Σ_i log(β·e^(−β·m_i)) ],
    λ_s(t) = μ_s + A_s·ω·e^(−ω·t) + Σ_{t_j < t} κ(m_j)·ω·e^(−ω·(t − t_j)),   κ(m) = n·e^(α·m)·(β − α)/β,   β = b·ln 10.

Dos diferencias con el simulador, las dos chicas y dichas: (1) el simulador descarta los datasets con algún sector sobre
300 sismos; aquí no se incluye esa constante de normalización, que depende de η (pesa solo cerca del tope); (2) los pisos
y recortes numéricos del prior (σ_μ ≥ 0,001; n en [0,001; 0,98]) no se replican: tienen probabilidad despreciable.
La restricción α < 0,95·b·ln 10 sí se impone.
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
from nucleo.sismico import LN10, PRIOR as P, preparar  # noqa: E402

MOTOR_ID = "sismico"


def modelo(t, m, mascara, T):
    S = t.shape[0]
    mu_mu = numpyro.sample("mu_mu", dist.Normal(P["mu_mu_media"], P["mu_mu_desv"]))
    sigma_mu = numpyro.sample("sigma_mu", dist.HalfNormal(P["sigma_mu_escala"]))
    n = numpyro.sample("n", dist.Beta(P["n_a"], P["n_b"]))
    log_alfa = numpyro.sample("log_alfa", dist.Normal(P["alfa_media"], P["alfa_desv"]))
    log_omega = numpyro.sample("log_omega", dist.Normal(P["omega_media"], P["omega_desv"]))
    log_b = numpyro.sample("log_b", dist.Normal(P["b_media"], P["b_desv"]))
    alfa, omega, beta = jnp.exp(log_alfa), jnp.exp(log_omega), jnp.exp(log_b) * LN10
    numpyro.factor("restriccion", jnp.where(alfa < 0.95 * beta, 0.0, -jnp.inf))
    with numpyro.plate("sectores", S):
        z_mu = numpyro.sample("z_mu", dist.Normal(0.0, 1.0))
        log_A = numpyro.sample("log_A", dist.Normal(P["A_media"], P["A_desv"]))
    log_mu = mu_mu + sigma_mu * z_mu
    mu, A = jnp.exp(log_mu), jnp.exp(log_A)
    kappa = n * jnp.exp(jnp.minimum(alfa * m, 50.0)) * jnp.maximum(beta - alfa, 1e-9) / beta * mascara            # (S, K)
    dt = t[:, :, None] - t[:, None, :]                                                                          # t_i − t_j
    antes = (dt > 0) & (mascara[:, None, :] > 0)
    de_los_sismos = (kappa[:, None, :] * omega * jnp.exp(-omega * jnp.where(antes, dt, 0.0)) * antes).sum(-1)    # (S, K)
    intensidad = mu[:, None] + A[:, None] * omega * jnp.exp(-omega * t) + de_los_sismos
    integral = mu * T + A * (1.0 - jnp.exp(-omega * T)) + (kappa * (1.0 - jnp.exp(-omega * (T - t)))).sum(-1)
    log_l = (jnp.log(intensidad) * mascara).sum() - integral.sum() + ((jnp.log(beta) - beta * m) * mascara).sum()
    numpyro.factor("verosimilitud", log_l)
    numpyro.deterministic("eta", jnp.stack([mu_mu, jnp.log(sigma_mu), jnp.log(n) - jnp.log1p(-n), log_alfa, log_omega, log_b]))
    numpyro.deterministic("lam", jnp.stack([log_mu, log_A], axis=-1))


def inicial(datos):
    S = datos["t"].shape[0]
    return {"mu_mu": P["mu_mu_media"], "sigma_mu": 0.4, "n": 0.4, "log_alfa": -0.2, "log_omega": P["omega_media"], "log_b": 0.0,
            "z_mu": jnp.zeros(S), "log_A": jnp.full(S, P["A_media"])}


def a_eta_lam(muestras, datos):
    return np.asarray(muestras["eta"]), np.asarray(muestras["lam"])


def _datos(t, m, mascara, T):
    return {"t": jnp.asarray(t, dtype=jnp.float64), "m": jnp.asarray(m, dtype=jnp.float64), "mascara": jnp.asarray(mascara, dtype=jnp.float64), "T": float(T)}


def datos_del_caso(nombre):
    """Las mismas lecturas que usa `nucleo.sismico.analizar` con el archivo del caso."""
    caso = cargar_caso(nombre)
    col = caso["columnas"]
    leido = series.leer(caso)
    m0 = float(col["magnitud_minima"])
    ts, ms = [], []
    for t, y in zip(leido["t"], leido["y"]):
        sirve = np.isfinite(t) & np.isfinite(y) & (y >= m0) & (t >= 0)
        ts.append(t[sirve]); ms.append(y[sirve] - m0)
    ventana = float(col["ventana"]) if col.get("ventana") else float(max(t.max() for t in ts if len(t)))
    t, mascara = series.con_relleno(ts)
    m, _ = series.con_relleno(ms)
    x, mascara_x, cov, tam = preparar(t, m, mascara, np.float64(ventana))
    return _datos(t, m, mascara, ventana), {"x": x, "mascara": mascara_x, "cov": cov, "tam": tam}, {"ids": np.array(leido["ids"])}


def datos_simulados(i):
    from motor.sismico.simular import simular
    sim = simular(np.random.default_rng([2026, i]), 1)
    e = sim["extra"]
    return (_datos(e["t"][0], e["m"][0], e["mascara"][0], e["T"][0]),
            {"x": sim["x"][0], "mascara": sim["mascara"][0], "cov": sim["cov"][0], "tam": sim["tam"][0]},
            {"eta_verdadero": sim["eta"][0], "lam_verdadero": sim["lam"][0]})


if __name__ == "__main__":
    comun.principal(sys.modules[__name__])
