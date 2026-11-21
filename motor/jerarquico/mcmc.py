"""MCMC de referencia del motor `jerarquico`: NUTS (NumPyro) con los dos niveles de efectos aleatorios explícitos.

A diferencia de la red, que entrega solo q(θ | D) y deja lo local a la cuadratura, aquí cada
paciente y cada barrio es un parámetro más: del orden de mil latentes de paciente poco
informados (la mayoría tiene una o dos citas) y decenas de barrios, en parametrización no
centrada (v_i = σ_v·ṽ_i, u_b = σ_b·ũ_b). Por eso es lento, y esa es la cifra de amortización.

El prior de θ es el del simulador (normal independiente en el espacio sin restricciones) y la
parte fija es η = Z·coef con la misma matriz de diseño. Se guarda θ en ese espacio, igual que
el blanco del flujo: `motor/artefactos/jerarquico/mcmc/<clave>.npz`.

    uv run python -m motor.jerarquico.mcmc --caso inasistencias
    uv run python -m motor.jerarquico.mcmc --simulados 5

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

from motor.jerarquico import simular
from nucleo import jerarquico as nucleo_jq
from nucleo.jerarquico import DIM_THETA, NOMBRES_THETA

numpyro.enable_x64()
CARPETA = simular.RAIZ / "motor" / "artefactos" / "jerarquico" / "mcmc"


def modelo(z, respuesta, conocida, paciente, barrio_del_paciente, n_barrios: int):
    """z: (n, 18). respuesta: (n,) con 0 donde falta. conocida: (n,) bool. paciente: (n,). barrio_del_paciente: (P,)."""
    n_pacientes = barrio_del_paciente.shape[0]
    crudo = numpyro.sample("z_theta", dist.Normal(0.0, 1.0).expand([DIM_THETA]).to_event(1))
    theta = numpyro.deterministic("theta", jnp.asarray(simular.MEDIAS) + jnp.asarray(simular.DESVS) * crudo)
    th = nucleo_jq.a_restringido(theta, xp=jnp)
    with numpyro.plate("barrios", n_barrios):
        u = th["sigma_b"] * numpyro.sample("u_crudo", dist.Normal(0.0, 1.0))
    with numpyro.plate("pacientes", n_pacientes):
        v = th["sigma_v"] * numpyro.sample("v_crudo", dist.Normal(0.0, 1.0))
    logit = z @ th["coef"] + v[paciente] + u[barrio_del_paciente[paciente]]
    with numpyro.plate("citas", z.shape[0]), numpyro.handlers.mask(mask=conocida):
        numpyro.sample("no_llega", dist.Bernoulli(logits=logit), obs=respuesta)


def argumentos(d: dict) -> tuple:
    """De un dataset en filas sueltas (`z`, `respuesta` con NaN, `paciente`, `barrio_del_paciente`) a los argumentos del modelo."""
    respuesta = np.asarray(d["respuesta"], dtype=np.float64)
    return (jnp.asarray(d["z"]), jnp.asarray(np.nan_to_num(respuesta)), jnp.asarray(~np.isnan(respuesta)),
            jnp.asarray(d["paciente"]), jnp.asarray(d["barrio_del_paciente"]), int(np.max(d["barrio_del_paciente"])) + 1)


def correr(d: dict, calentamiento: int = 500, muestras: int = 500, cadenas: int = 4, semilla: int = 0, profundidad: int = 10) -> dict:
    """Corre NUTS (`profundidad` = máximo de duplicaciones del árbol por paso) y devuelve las muestras de θ (muestras·cadenas, 20), los segundos y los diagnósticos."""
    args = argumentos(d)
    inicial = init_to_value(values={"z_theta": jnp.zeros(DIM_THETA), "u_crudo": jnp.zeros(args[5]),
                                    "v_crudo": jnp.zeros(args[4].shape[0])})
    mcmc = MCMC(NUTS(modelo, init_strategy=inicial, target_accept_prob=0.85, max_tree_depth=profundidad), num_warmup=calentamiento, num_samples=muestras,
                num_chains=cadenas, chain_method="vectorized", progress_bar=False)
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


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--caso", help="nombre de un caso de inasistencias de casos/ (el archivo real, que no se versiona)")
    analizador.add_argument("--simulados", type=int, default=0, help="cuántos datasets simulados (semilla fija)")
    analizador.add_argument("--muestras", type=int, default=500)
    analizador.add_argument("--cadenas", type=int, default=4)
    a = analizador.parse_args()

    def informar(clave, r, ruta):
        print(json.dumps({"clave": clave, "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                          "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3), "n_eff_min": round(float(np.nanmin(r["n_eff"])))}), flush=True)

    if a.caso:
        real = simular.leer_real(a.caso)
        real["z"] = nucleo_jq.matriz_de_diseno(real["espera"], real["dia"], real["sms"], real["edad"], real["binarias"])
        r = correr(real, muestras=a.muestras, cadenas=a.cadenas)
        informar(a.caso, r, guardar(a.caso, r))
    if a.simulados:
        lote = simular.simular(np.random.default_rng(2026), a.simulados, 2000, 30, simular.leer_real())
        for i in range(a.simulados):
            d = simular.a_filas_sueltas(lote, i)
            r = correr(d, muestras=a.muestras, cadenas=a.cadenas, semilla=i)
            informar(f"simulado_{i:02d}", r, guardar(f"simulado_{i:02d}", r, filas=lote["filas"][i], mascara=lote["mascara"][i],
                                                    theta_verdadero=lote["theta"][i]))


if __name__ == "__main__":
    principal()
