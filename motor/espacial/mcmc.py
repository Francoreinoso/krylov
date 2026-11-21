"""MCMC de referencia del motor `espacial`: NUTS (NumPyro) sobre θ con la verosimilitud marginal del proceso gaussiano.

Sirve para validar la red (mismas medias y rangos) y es el plan B de la tarjeta: sus
muestras se guardan en `motor/artefactos/espacial/mcmc/<clave>.npz` y `nucleo/espacial.py`
las pasa por el mismo kriging.

**El mismo modelo que el simulador, incluida la estandarización.** La red no ve los datos
crudos D sino d' = (D − media)/escala, con la media y la escala de lo medido. Para que el
MCMC apunte al mismo posterior, la media m y la escala s del terreno «en unidades del
simulador» son incógnitas que se marginalizan:

    θ ~ prior del simulador (normales truncadas),   D = m + s·d',
    p(θ, m, s | d')  ∝  p(θ) · Normal(m + s·d' | β0 + β1·√dist, σ²·exp(−h) + τ²/c) · s^(n−2)

El factor s^(n−2) es el jacobiano de pasar de D (n números) a (d', m, s): d' vive en una
superficie de n−2 dimensiones. Lo que se guarda es θ' en unidades estandarizadas, igual
que el blanco del flujo: (log a, e1, e2, log(σ/s), log(τ/s), (β0 − m)/s, β1/s).

    uv run python -m motor.espacial.mcmc --caso terreno          # el archivo real
    uv run python -m motor.espacial.mcmc --simulados 5           # terrenos simulados, para comparar con la red

Nunca corre encima de un entrenamiento, y en `espacial` tarda segundos por terreno.
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

from motor.espacial.simular import NOMBRES_THETA, Prior

numpyro.enable_x64()
CARPETA = Path("motor/artefactos/espacial/mcmc")


def _medias_y_desvs(prior: Prior) -> tuple[jnp.ndarray, jnp.ndarray]:
    medias = jnp.array([prior.log_alcance_media, 0.0, 0.0, 0.0, prior.log_tau_media, 0.0, 0.0])
    desvs = jnp.array([prior.log_alcance_desv, prior.anis_desv, prior.anis_desv, prior.log_sigma_desv,
                       prior.log_tau_desv, prior.beta0_desv, prior.beta1_desv])
    return medias, desvs


def correlacion(theta: jnp.ndarray, d_fila: jnp.ndarray, d_columna: jnp.ndarray) -> jnp.ndarray:
    """exp(−h) con la distancia anisotrópica; la misma fórmula que el simulador y que `nucleo/espacial.py`."""
    a2 = jnp.exp(2 * theta[0])
    e1, e2 = theta[1], theta[2]
    rho = jnp.sqrt(e1 ** 2 + e2 ** 2 + 1e-12)
    cosh, sinhc = jnp.cosh(rho), jnp.sinh(rho) / rho
    m11, m12, m22 = (cosh - sinhc * e1) / a2, (-sinhc * e2) / a2, (cosh + sinhc * e1) / a2
    h2 = m11 * d_columna ** 2 + 2 * m12 * d_columna * d_fila + m22 * d_fila ** 2
    positivo = h2 > 0                 # raíz con gradiente finito en h = 0 (la diagonal), sin cambiar el valor
    return jnp.exp(-jnp.where(positivo, jnp.sqrt(jnp.where(positivo, h2, 1.0)), 0.0))


def modelo(valor, fila, columna, raiz_dist, cuenta, prior: Prior = Prior()):
    """valor: lo medido, estandarizado (d'), en los n bloques medidos; fila, columna, raiz_dist y cuenta, ahí mismo."""
    n = valor.shape[0]
    medias, desvs = _medias_y_desvs(prior)
    z = numpyro.sample("z", dist.TruncatedNormal(0.0, 1.0, low=-prior.corte, high=prior.corte).expand([7]).to_event(1))
    theta = medias + desvs * z                                          # θ en unidades del simulador
    m = numpyro.sample("media", dist.ImproperUniform(dist.constraints.real, (), ()))
    log_s = numpyro.sample("log_escala", dist.ImproperUniform(dist.constraints.real, (), ()))
    # Medida plana en s (no en log s) por el jacobiano s^(n−2):  (n − 2)·log s + log s.
    numpyro.factor("jacobiano", (n - 1) * log_s)

    sigma2, tau2 = jnp.exp(2 * theta[3]), jnp.exp(2 * theta[4])
    k = sigma2 * correlacion(theta, fila[:, None] - fila[None, :], columna[:, None] - columna[None, :])
    k = k + jnp.diag(tau2 / cuenta + 1e-9)
    numpyro.sample("obs", dist.MultivariateNormal(theta[5] + theta[6] * raiz_dist, covariance_matrix=k),
                   obs=m + jnp.exp(log_s) * valor)
    numpyro.deterministic("theta_est", jnp.stack([
        theta[0], theta[1], theta[2], theta[3] - log_s, theta[4] - log_s, (theta[5] - m) * jnp.exp(-log_s), theta[6] * jnp.exp(-log_s)]))


def datos_de_canales(canales: np.ndarray, cuenta: np.ndarray | None = None) -> dict:
    """De los canales (3, 32, 32) de `nucleo.preproceso` a los argumentos de `modelo`."""
    fila, columna = np.nonzero(canales[1] > 0)
    return {"valor": jnp.asarray(canales[0][fila, columna], dtype=jnp.float64), "fila": jnp.asarray(fila, dtype=jnp.float64),
            "columna": jnp.asarray(columna, dtype=jnp.float64), "raiz_dist": jnp.asarray(canales[2][fila, columna], dtype=jnp.float64),
            "cuenta": jnp.ones(len(fila)) if cuenta is None else jnp.asarray(cuenta[fila, columna], dtype=jnp.float64)}


def correr(canales: np.ndarray, cuenta: np.ndarray | None = None, calentamiento: int = 500, muestras: int = 500,
           cadenas: int = 4, semilla: int = 0, prior: Prior = Prior()) -> dict:
    """Corre NUTS y devuelve las muestras de θ' (muestras·cadenas, 7), los segundos y los diagnósticos."""
    datos = datos_de_canales(canales, cuenta)
    inicial = init_to_value(values={"z": jnp.zeros(7), "media": 0.0, "log_escala": 0.0})
    mcmc = MCMC(NUTS(modelo, init_strategy=inicial, target_accept_prob=0.9), num_warmup=calentamiento, num_samples=muestras,
                num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), **datos, prior=prior)
    theta_est = np.asarray(mcmc.get_samples()["theta_est"])
    segundos = time.time() - inicio
    por_cadena = np.asarray(mcmc.get_samples(group_by_chain=True)["theta_est"])
    diagnostico = numpyro.diagnostics.summary({"theta_est": por_cadena}, group_by_chain=True)["theta_est"]
    return {"theta_est": theta_est, "segundos": segundos, "r_hat": np.asarray(diagnostico["r_hat"]),
            "n_eff": np.asarray(diagnostico["n_eff"]), "divergencias": int(np.asarray(mcmc.get_extra_fields().get("diverging", 0)).sum())}


def guardar(clave: str, resultado: dict, carpeta: Path = CARPETA, **extra) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{clave}.npz"
    np.savez(ruta, theta_est=resultado["theta_est"].astype(np.float32), nombres_theta=np.array(NOMBRES_THETA),
             segundos=resultado["segundos"], r_hat=resultado["r_hat"], n_eff=resultado["n_eff"], **extra)
    return ruta


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--caso", default=None, help="nombre de un caso espacial de casos/ (el archivo real)")
    p.add_argument("--simulados", type=int, default=0, help="cuántos terrenos simulados (semilla fija)")
    p.add_argument("--muestras", type=int, default=500)
    p.add_argument("--cadenas", type=int, default=4)
    a = p.parse_args()

    if a.caso:
        from nucleo.espacial import canales_del_caso
        listo = canales_del_caso(a.caso)
        r = correr(listo["canales"], listo["cuenta"], muestras=a.muestras, cadenas=a.cadenas)
        ruta = guardar(a.caso, r, media=listo["media"], escala=listo["escala"])
        print(json.dumps({"clave": a.caso, "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                          "r_hat_max": round(float(r["r_hat"].max()), 3), "n_eff_min": round(float(r["n_eff"].min()))}))
    if a.simulados:
        import torch
        from motor.espacial.simular import simular
        lote = simular(a.simulados, Prior(), torch.Generator().manual_seed(2026))
        for i in range(a.simulados):
            r = correr(lote["canales"][i].numpy(), muestras=a.muestras, cadenas=a.cadenas, semilla=i)
            ruta = guardar(f"simulado_{i:02d}", r, canales=lote["canales"][i].numpy(), theta_verdadero=lote["theta"][i].numpy())
            print(json.dumps({"clave": f"simulado_{i:02d}", "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                              "r_hat_max": round(float(r["r_hat"].max()), 3), "n_eff_min": round(float(r["n_eff"].min()))}))


if __name__ == "__main__":
    main()
