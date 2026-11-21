"""MCMC de referencia del motor `supervivencia`: NUTS (NumPyro) con el efecto de cada cargo y el compromiso de cada persona explícitos.

A diferencia de la red, que entrega solo q(θ | D) y deja lo local a la cuadratura, aquí cada
latente es un parámetro más: un compromiso z_i por persona (hasta 2.000) y un efecto u_g por
cargo, en parametrización no centrada (u_g = σ_u·ũ_g) por el embudo. Por eso es lento, y esa es
la cifra de amortización. Es además la vara con que se valida la red y el plan B de la tarjeta.

El prior es el del simulador (`motor/artefactos/supervivencia/config.json`), la verosimilitud es
la de intervalos de WORKPLAN.md 11.2 (la misma del paso local de `nucleo/supervivencia.py`) y las
personas con el evento vacío aportan sus años con la suma de los dos casos. Se guarda θ en el
espacio sin restricciones, igual que el blanco del flujo: `motor/artefactos/supervivencia/mcmc/<clave>.npz`.

    uv run python -m motor.supervivencia.mcmc --caso rotacion --tambien rotacion_malo__quitar_factor-fecha_salida
    uv run python -m motor.supervivencia.mcmc --simulados 5

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
from jax.scipy.stats import norm
from numpyro.distributions import constraints
from numpyro.infer import MCMC, NUTS, init_to_value

from motor.supervivencia import simular
from nucleo import supervivencia as nucleo_sv
from nucleo.supervivencia import CARGOS_MAX, N_CORTES, N_EFECTOS, N_ENCUESTAS, N_SPLINE, NOMBRES_THETA

numpyro.enable_x64()
CARPETA = simular.RAIZ / "motor" / "artefactos" / "supervivencia" / "mcmc"
SIN_EVENTO = -1          # código de «por decidir» en el arreglo de eventos (NaN rompería los gradientes)


def modelo(x, base_w, encuestas, tiempo, evento, grupo, prior: dict):
    """x: (n, 3). base_w: (n, 6), la base B-spline en w. encuestas: (n, 4) en 0..3. tiempo: (n,) años enteros.
    evento: (n,) con 1, 0 o SIN_EVENTO. grupo: (n,) en 0..CARGOS_MAX−1. prior: el bloque `prior` de config.json.
    """
    n = tiempo.shape[0]
    k = numpyro.sample("k", dist.LogNormal(0.0, prior["k_log_desv"]))
    beta0 = numpyro.sample("beta0", dist.Normal(prior["beta0_media"], prior["beta0_desv"]))
    beta = numpyro.sample("beta", dist.Normal(0.0, prior["beta_desv"]).expand([N_EFECTOS]).to_event(1))
    # Prior de suavidad del spline, no centrado: γ es la suma acumulada de pasos con escala (1, τ, …, τ).
    tau = numpyro.sample("tau", dist.HalfNormal(prior["tau_escala"]))
    pasos = numpyro.sample("pasos_gamma", dist.Normal(0.0, 1.0).expand([N_SPLINE]).to_event(1))
    gamma = jnp.cumsum(pasos * jnp.concatenate([jnp.array([prior["gamma1_desv"]]), tau * jnp.ones(N_SPLINE - 1)]))
    sigma_u = numpyro.sample("sigma_u", dist.HalfNormal(prior["sigma_u_escala"]))
    lam = numpyro.sample("lambda", dist.Normal(0.0, prior["lambda_desv"]))
    a = numpyro.sample("a", dist.LogNormal(0.0, prior["a_log_desv"]).expand([N_ENCUESTAS]).to_event(1))
    # Cortes: tres normales ordenadas por ítem. Su densidad es 3! por el producto de las normales, sobre los vectores ordenados.
    cortes = numpyro.sample("cortes", dist.ImproperUniform(constraints.ordered_vector, (N_ENCUESTAS,), (N_CORTES,)))
    numpyro.factor("prior_cortes", dist.Normal(0.0, prior["cortes_desv"]).log_prob(cortes).sum() + N_ENCUESTAS * jnp.log(6.0))
    mu_c = numpyro.sample("mu_c", dist.Normal(prior["mu_c_media"], prior["mu_c_desv"]))
    s_c = numpyro.sample("s_c", dist.HalfNormal(prior["s_c_escala"]))
    # θ en el espacio sin restricciones y en el orden de `nucleo.supervivencia.NOMBRES_THETA`: lo que se compara con el flujo.
    cortes_libres = jnp.concatenate([cortes[:, :1], jnp.log(cortes[:, 1:] - cortes[:, :-1])], axis=1)
    numpyro.deterministic("theta", jnp.concatenate([
        jnp.log(k)[None], beta0[None], beta, gamma, jnp.log(tau)[None], jnp.log(sigma_u)[None], lam[None],
        jnp.log(a), cortes_libres.reshape(-1), mu_c[None], jnp.log(s_c)[None]]))

    with numpyro.plate("cargos", CARGOS_MAX):
        u = sigma_u * numpyro.sample("u_crudo", dist.Normal(0.0, 1.0))
    with numpyro.plate("personas", n):
        z = numpyro.sample("z", dist.Normal(0.0, 1.0))
        # Logit ordenado: P(y ≤ m) = logistic(c_m − a z).
        numpyro.sample("encuestas", dist.OrderedLogistic(a * z[:, None], cortes).to_event(1), obs=encuestas)

    # Verosimilitud por intervalos de un año. S_T(t) = exp(−h t^k); S_C es la supervivencia de la censura LogNormal.
    h = jnp.exp(beta0 + x @ beta + base_w @ gamma + u[grupo] - lam * z)
    def potencia(v):                                             # v^k, con 0^k = 0 sin pasar por log 0
        return jnp.where(v > 0, jnp.exp(k * jnp.log(jnp.where(v > 0, v, 1.0))), 0.0)
    def s_censura(c):
        return jnp.where(c > 0, norm.sf((jnp.log(jnp.where(c > 0, c, 1.0)) - mu_c) / s_c), 1.0)
    t_k = potencia(tiempo)
    log_renuncio = -h * t_k + jnp.log(-jnp.expm1(-h * (potencia(tiempo + 1.0) - t_k)) + 1e-300) + jnp.log(s_censura(tiempo + 0.5) + 1e-300)
    log_sigue = -h * potencia(tiempo + 0.5) + jnp.log(s_censura(tiempo) - s_censura(tiempo + 1.0) + 1e-300)
    log_ver = jnp.where(evento == 1, log_renuncio, jnp.where(evento == 0, log_sigue, jnp.logaddexp(log_renuncio, log_sigue)))
    numpyro.factor("anos_y_evento", log_ver.sum())


def argumentos(datos: dict, prior: dict | None = None) -> tuple:
    """De `nucleo.supervivencia.variables_del_modelo` (una empresa) a los argumentos del modelo."""
    evento = np.asarray(datos["evento"], dtype=np.float64)
    return (jnp.asarray(datos["x"]), jnp.asarray(nucleo_sv.base_spline(datos["w"])), jnp.asarray(datos["encuestas"] - 1),
            jnp.asarray(datos["tiempo"]), jnp.asarray(np.where(np.isnan(evento), SIN_EVENTO, evento).astype(int)),
            jnp.asarray(datos["grupo"]), prior or simular.cargar_config()["prior"])


def punto_inicial(n: int, prior: dict) -> dict:
    """El centro del prior, con todos los latentes en cero."""
    return {"k": jnp.array(1.0), "beta0": jnp.array(prior["beta0_media"]), "beta": jnp.zeros(N_EFECTOS), "tau": jnp.array(0.6 * prior["tau_escala"]),
            "pasos_gamma": jnp.zeros(N_SPLINE), "sigma_u": jnp.array(0.6 * prior["sigma_u_escala"]), "lambda": jnp.array(0.0), "a": jnp.ones(N_ENCUESTAS),
            "cortes": jnp.tile(prior["cortes_desv"] * jnp.array([-1.0, 0.0, 1.0]), (N_ENCUESTAS, 1)), "mu_c": jnp.array(prior["mu_c_media"]),
            "s_c": jnp.array(0.6 * prior["s_c_escala"]), "u_crudo": jnp.zeros(CARGOS_MAX), "z": jnp.zeros(n)}


def correr(datos: dict, calentamiento: int = 500, muestras: int = 500, cadenas: int = 4, semilla: int = 0) -> dict:
    """Corre NUTS y devuelve las muestras de θ sin restricciones (muestras·cadenas, 32), los segundos y los diagnósticos."""
    args = argumentos(datos)
    nuts = NUTS(modelo, init_strategy=init_to_value(values=punto_inicial(len(datos["tiempo"]), args[-1])), target_accept_prob=0.85)
    mcmc = MCMC(nuts, num_warmup=calentamiento, num_samples=muestras, num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), *args)
    theta = np.asarray(mcmc.get_samples()["theta"])
    segundos = time.time() - inicio
    diagnostico = numpyro.diagnostics.summary({"theta": np.asarray(mcmc.get_samples(group_by_chain=True)["theta"])}, group_by_chain=True)["theta"]
    return {"theta": theta, "segundos": segundos, "r_hat": np.asarray(diagnostico["r_hat"]), "n_eff": np.asarray(diagnostico["n_eff"])}


def guardar(clave: str, resultado: dict, carpeta: Path = CARPETA, **extra) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{clave}.npz"
    np.savez(ruta, theta=resultado["theta"].astype(np.float32), nombres_theta=np.array(NOMBRES_THETA), segundos=resultado["segundos"],
             r_hat=resultado["r_hat"], n_eff=resultado["n_eff"], **extra)
    return ruta


def simulados(cuantos: int, n: int = 1470, semilla: int = 2026) -> list[tuple[dict, np.ndarray]]:
    """`cuantos` empresas simuladas con semilla fija: (variables del modelo, θ verdadero sin restricciones) de cada una."""
    config = simular.cargar_config()
    lote = simular.simular(np.random.default_rng(semilla), cuantos, n, config, simular.cargar_filas_reales(config))
    variables = nucleo_sv.variables_del_modelo(lote)
    return [({c: v[i] for c, v in variables.items()}, lote["theta"][i]) for i in range(cuantos)]


def datos_del_caso(nombre: str) -> dict:
    from nucleo import casos
    caso = casos.cargar_caso(nombre)
    return nucleo_sv.variables_del_modelo(nucleo_sv.leer_tabla(casos.RAIZ / caso["dataset"], caso["columnas"]))


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--caso", help="nombre de un caso de rotación de casos/")
    analizador.add_argument("--tambien", nargs="*", default=[], help="otras claves con los mismos datos del modelo (el archivo malo ya corregido)")
    analizador.add_argument("--simulados", type=int, default=0, help="cuántas empresas simuladas (semilla fija)")
    analizador.add_argument("--muestras", type=int, default=500)
    analizador.add_argument("--cadenas", type=int, default=4)
    a = analizador.parse_args()

    def informar(clave, r, ruta):
        print(json.dumps({"clave": clave, "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                          "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3), "n_eff_min": round(float(np.nanmin(r["n_eff"])))}), flush=True)

    if a.caso:
        r = correr(datos_del_caso(a.caso), muestras=a.muestras, cadenas=a.cadenas)
        for clave in [a.caso, *a.tambien]:
            informar(clave, r, guardar(clave, r))
    for i, (datos, verdadero) in enumerate(simulados(a.simulados) if a.simulados else []):
        r = correr(datos, muestras=a.muestras, cadenas=a.cadenas, semilla=i)
        informar(f"simulado_{i:02d}", r, guardar(f"simulado_{i:02d}", r, theta_verdadero=verdadero))


if __name__ == "__main__":
    principal()
