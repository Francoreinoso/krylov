"""MCMC de referencia del motor `estados`: NUTS (NumPyro) sobre θ, con la cadena oculta marginalizada.

Los estados de cada cliente son discretos: NUTS no los muestrea. Se integran con el filtro
forward dentro de la verosimilitud, que es **la misma función** que usa el servicio
(`nucleo.estados.log_verosimilitud`), evaluada aquí con `jax.numpy`. El prior es el del
simulador: normal independiente en el espacio sin restricciones, con d_1 < d_2 < d_3 por
construcción. Lo que se guarda es θ en ese mismo espacio, igual que el blanco del flujo.

Sirve para validar la red y es el plan B de la tarjeta: `motor/artefactos/estados/mcmc/<clave>.npz`.

    uv run python -m motor.estados.mcmc --caso credito
    uv run python -m motor.estados.mcmc --simulados 5

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

from motor.estados import simular
from nucleo import estados as nucleo_es
from nucleo.estados import DIM_THETA, NOMBRES_THETA

numpyro.enable_x64()
CARPETA = simular.RAIZ / "motor" / "artefactos" / "estados" / "mcmc"
VARIABLES = ("nivel", "uso", "pago_cero", "log_pago", "x")


def modelo(datos: dict, impago):
    """θ = media + desv·z, z ~ Normal(0, 1); verosimilitud con el filtro forward marginalizado."""
    z = numpyro.sample("z", dist.Normal(0.0, 1.0).expand([DIM_THETA]).to_event(1))
    theta = numpyro.deterministic("theta", jnp.asarray(simular.MEDIAS) + jnp.asarray(simular.DESVS) * z)
    numpyro.factor("verosimilitud", nucleo_es.log_verosimilitud(theta, datos, impago, xp=jnp))


def a_jax(datos: dict) -> dict:
    return {k: jnp.asarray(np.asarray(datos[k])) for k in VARIABLES}


def correr(datos: dict, impago, calentamiento: int = 500, muestras: int = 500, cadenas: int = 4, semilla: int = 0, profundidad: int = 10) -> dict:
    """Corre NUTS (`profundidad` = máximo de duplicaciones del árbol por paso) y devuelve las muestras de θ (muestras·cadenas, 33), los segundos y los diagnósticos."""
    mcmc = MCMC(NUTS(modelo, init_strategy=init_to_value(values={"z": jnp.zeros(DIM_THETA)}), target_accept_prob=0.85, max_tree_depth=profundidad),
                num_warmup=calentamiento, num_samples=muestras, num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), a_jax(datos), jnp.asarray(np.asarray(impago, dtype=np.float64)))
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
    analizador.add_argument("--caso", help="nombre de un caso de crédito de casos/ (el archivo real)")
    analizador.add_argument("--simulados", type=int, default=0, help="cuántas carteras simuladas (semilla fija)")
    analizador.add_argument("--muestras", type=int, default=500)
    analizador.add_argument("--cadenas", type=int, default=4)
    a = analizador.parse_args()

    def informar(clave, r, ruta):
        print(json.dumps({"clave": clave, "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                          "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3), "n_eff_min": round(float(np.nanmin(r["n_eff"])))}), flush=True)

    if a.caso:
        real = simular.variables_del_caso(a.caso)
        r = correr(real, real["impago"], muestras=a.muestras, cadenas=a.cadenas)
        informar(a.caso, r, guardar(a.caso, r))
    if a.simulados:
        lote = simular.simular(np.random.default_rng(2026), a.simulados, 1000, simular.cargar_covariables_reales())
        for i in range(a.simulados):
            datos = {k: lote[k][i] for k in VARIABLES}
            r = correr(datos, lote["impago"][i], muestras=a.muestras, cadenas=a.cadenas, semilla=i)
            informar(f"simulado_{i:02d}", r, guardar(f"simulado_{i:02d}", r, filas=lote["filas"][i], theta_verdadero=lote["theta"][i]))


if __name__ == "__main__":
    principal()
