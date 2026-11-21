"""MCMC de referencia del motor `yacimiento`: NUTS (NumPyro) sobre los 15 parámetros con la verosimilitud marginal
exacta del proceso gaussiano, y después el kriging exacto de los 16.384 bloques para cada muestra de θ.

Es «el método lento de siempre»: cada evaluación factoriza una matriz de n × n (n = compósitos) y su gradiente, y el
mapa exige resolver contra todos los bloques por cada θ. El mismo modelo que `yacimiento/modelo.py`: mismo prior (normal
en espacio sin restricciones), misma covarianza exponencial anisotrópica, mismas covariables. La única diferencia con el
simulador es el recorte del circulant embedding (bajo 1,3% de la varianza; ver `modelo.py`).

    uv run python -m yacimiento.mcmc --demo                 # el yacimiento del demo
    uv run python -m yacimiento.mcmc --simulados 2          # yacimientos simulados (semilla fija), para comparar con la red

Nunca corre encima de un entrenamiento.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, init_to_value
from scipy.linalg import cho_factor, cho_solve, solve_triangular
from scipy.stats import norm

from yacimiento import modelo as M

numpyro.enable_x64()
CARPETA = Path("yacimiento/artefactos/mcmc")
MEDIA, DESV = np.asarray(M.PRIOR_MEDIA, dtype=np.float64), np.asarray(M.PRIOR_DESV, dtype=np.float64)


def _h(theta, d, xp):
    """Distancia anisotrópica para desfases d (..., 3) en bloques; la misma fórmula que `modelo.metrica`."""
    a2 = xp.exp(2 * theta[0])
    rho = xp.sqrt(theta[1] ** 2 + theta[2] ** 2 + 1e-12)
    cosh, sinhc = xp.cosh(rho), xp.sinh(rho) / rho
    m11, m12, m22, mz = (cosh - sinhc * theta[1]) / a2, (-sinhc * theta[2]) / a2, (cosh + sinhc * theta[1]) / a2, xp.exp(-2 * theta[3])
    h2 = m11 * d[..., 0] ** 2 + 2 * m12 * d[..., 0] * d[..., 1] + m22 * d[..., 1] ** 2 + mz * d[..., 2] ** 2
    positivo = h2 > 0
    return xp.where(positivo, xp.sqrt(xp.where(positivo, h2, 1.0)), 0.0)


def modelo(pos, cov, y):
    z = numpyro.sample("z", dist.Normal(0.0, 1.0).expand([M.DIM_THETA]).to_event(1))
    theta = jnp.asarray(MEDIA) + jnp.asarray(DESV) * z
    k = jnp.exp(2 * theta[4]) * jnp.exp(-_h(theta, pos[:, None, :] - pos[None, :, :], jnp)) + jnp.exp(2 * theta[5]) * jnp.eye(pos.shape[0])
    numpyro.sample("obs", dist.MultivariateNormal(theta[6] + cov @ theta[7:], covariance_matrix=k), obs=y)
    numpyro.deterministic("theta", theta)


def datos_de(mascara: np.ndarray, y: np.ndarray, cov: np.ndarray) -> dict:
    i, j, k = np.nonzero(mascara)
    return {"pos": jnp.asarray(np.stack([i, j, k], -1), dtype=jnp.float64), "cov": jnp.asarray(cov[:, i, j, k].T, dtype=jnp.float64),
            "y": jnp.asarray(y[i, j, k], dtype=jnp.float64)}


def correr(datos: dict, calentamiento: int = 400, muestras: int = 400, cadenas: int = 4, semilla: int = 0) -> dict:
    nucleo = NUTS(modelo, init_strategy=init_to_value(values={"z": jnp.zeros(M.DIM_THETA)}), target_accept_prob=0.85)
    mcmc = MCMC(nucleo, num_warmup=calentamiento, num_samples=muestras, num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), **datos, extra_fields=("diverging",))
    por_cadena = np.asarray(mcmc.get_samples(group_by_chain=True)["theta"])
    segundos = time.time() - inicio
    d = numpyro.diagnostics.summary({"theta": por_cadena}, group_by_chain=True)["theta"]
    return {"theta": por_cadena.reshape(-1, M.DIM_THETA), "segundos": segundos, "r_hat": np.asarray(d["r_hat"]), "n_eff": np.asarray(d["n_eff"]),
            "divergencias": int(np.asarray(mcmc.get_extra_fields()["diverging"]).sum())}


def mapa(theta: np.ndarray, datos: dict, cov: np.ndarray, cuantas: int = 100) -> dict:
    """Predictivo posterior de la ley en los 16.384 bloques: kriging exacto para `cuantas` muestras de θ (adelgazadas) y su mezcla.
    Devuelve media y desviación de la mezcla, las medias y desviaciones por muestra (para probabilidades), y los segundos."""
    inicio = time.time()
    pos, c_obs, y = (np.asarray(datos[k]) for k in ("pos", "cov", "y"))
    bloques = np.stack(np.meshgrid(np.arange(M.NX), np.arange(M.NY), np.arange(M.NZ), indexing="ij"), -1).reshape(-1, 3).astype(np.float64)
    c_bloques = cov.reshape(M.N_COV, -1).T.astype(np.float64)
    medias, desvs = [], []
    for th in theta[np.round(np.linspace(0, len(theta) - 1, cuantas)).astype(int)]:
        s2, t2 = np.exp(2 * th[4]), np.exp(2 * th[5])
        factor = cho_factor(s2 * np.exp(-_h(th, pos[:, None, :] - pos[None, :, :], np)) + t2 * np.eye(len(pos)), lower=True)
        k_b = s2 * np.exp(-_h(th, bloques[:, None, :] - pos[None, :, :], np))                         # (16384, n)
        medias.append(th[6] + c_bloques @ th[7:] + k_b @ cho_solve(factor, y - th[6] - c_obs @ th[7:]))
        v = solve_triangular(factor[0], k_b.T, lower=True)
        desvs.append(np.sqrt(np.maximum(s2 - (v**2).sum(0), 1e-12)))
    medias, desvs = np.array(medias), np.array(desvs)
    media = medias.mean(0)
    forma = (M.NX, M.NY, M.NZ)
    return {"media": media.reshape(forma), "desv": np.sqrt((desvs**2 + medias**2).mean(0) - media**2).reshape(forma),
            "medias": medias.astype(np.float32), "desvs": desvs.astype(np.float32), "segundos_mapa": time.time() - inicio}


def sobre_el_corte(m: dict, log_corte: float) -> np.ndarray:
    """P(ley del bloque > corte | datos), mezclando sobre las muestras de θ."""
    return norm.sf((log_corte - m["medias"]) / m["desvs"]).mean(0).reshape(M.NX, M.NY, M.NZ)


def _uno(clave: str, mascara, y, cov, a, **extra) -> None:
    datos = datos_de(mascara, y, cov)
    r = correr(datos, a.calentamiento, a.muestras, a.cadenas)
    m = mapa(r["theta"], datos, cov, a.mapas)
    CARPETA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CARPETA / f"{clave}.npz", theta=r["theta"].astype(np.float32), r_hat=r["r_hat"], n_eff=r["n_eff"], segundos=r["segundos"],
                        segundos_mapa=m["segundos_mapa"], divergencias=r["divergencias"], media=m["media"].astype(np.float32),
                        desv=m["desv"].astype(np.float32), medias=m["medias"], desvs=m["desvs"], **extra)
    print(json.dumps({"clave": clave, "compositos": int(len(datos["y"])), "segundos_nuts": round(r["segundos"], 1), "segundos_mapa": round(m["segundos_mapa"], 1),
                      "r_hat_max": round(float(r["r_hat"].max()), 3), "n_eff_min": round(float(r["n_eff"].min())), "divergencias": r["divergencias"]}), flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--simulados", type=int, default=0)
    p.add_argument("--muestras", type=int, default=400)
    p.add_argument("--calentamiento", type=int, default=400)
    p.add_argument("--cadenas", type=int, default=4)
    p.add_argument("--mapas", type=int, default=100, help="muestras de θ con que se rehace el kriging de todos los bloques")
    a = p.parse_args()
    if a.demo:
        z = np.load("yacimiento/datos/demo.npz")
        _uno("demo", z["mascara"], z["y"], z["cov"], a)
    if a.simulados:
        import torch
        sim = M.simular(a.simulados, torch.Generator().manual_seed(4242))
        for i in range(a.simulados):
            s = {k: v[i].numpy() for k, v in sim.items()}
            _uno(f"simulado_{i:02d}", s["mascara"], s["y"], s["cov"], a, mascara=s["mascara"], y=s["y"], cov=s["cov"], verdad=s["verdad"], theta_verdadero=s["theta"])


if __name__ == "__main__":
    main()
