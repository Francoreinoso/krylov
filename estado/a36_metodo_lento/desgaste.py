"""MCMC de referencia del motor `desgaste`: NUTS (NumPyro) sobre η, el ritmo ν_i de cada camión y su trayectoria latente.

Apunta al mismo posterior que la red: el modelo generativo de `motor/desgaste/simular.py` (proceso gamma jerárquico
con lecturas ruidosas y la covariable de exigencia), condicionado a que cada camión del archivo sigue en servicio.

**La trayectoria latente, reparametrizada sin cambiar el modelo.** El simulador sortea saltos
ΔX_k ~ Gamma(ν_i·Δt_k / c², escala c²) y los acumula. Por las propiedades del proceso gamma, eso equivale exactamente a

    X_i(hoy) ~ Gamma(ν_i·hoy_i / c², escala c²)
    X_i(t_k) / X_i(t_{k+1}) ~ Beta(ν_i·t_k / c², ν_i·(t_{k+1} − t_k) / c²),   independientes entre sí y de X_i(hoy)

y así la restricción «sigue en servicio» es una cota sobre una sola variable: X_i(hoy) ∈ (0; 0,92).

**El condicionamiento «sigue en servicio».** El simulador descarta entero (exigencia, horas, ritmo y trayectoria) al
camión con X_i(hoy) ≥ 0,92 y sortea otro con el mismo η. La densidad de cada camión lleva entonces el factor
1[X_i(hoy) < 0,92] / Z(η), con

    Z(η) = P(un camión al azar sigue en servicio | η) = E_{x, hoy, ν}[ P(a = ν·hoy / c², 0,92 / c²) ],

donde P(a, ·) es la gamma incompleta regularizada, x ~ Normal(0, 1), hoy ~ Uniforme(0,5; 3) y
log ν ~ Normal(μ_ν + β·x, σ_ν). El modelo suma −M·log Z(η) (M camiones).

**Qué es aproximado.**
  1. Z(η) se estima con `NODOS_Z` nodos fijos de cuasi Monte Carlo (Sobol, semilla fija): es una función suave y
     determinista de η, con error relativo del orden de 1e-3.
  2. Se ignora el re-sorteo de la flota entera: el simulador cambia el η de una flota cuando un camión no logra quedar
     en servicio en 2.000 intentos (Z(η) ≲ 1/2.000, la cola del prior con desgaste muy rápido). Es un recorte del prior
     en una zona de masa despreciable.
  3. Las formas de las Gamma y Beta llevan un piso de 1e-6 (el simulador usa 1e-12): solo actúa si un archivo trae dos
     muestras a la misma hora o una muestra a la hora 0.
El piso de σ_ν (`np.maximum(…, 1e-3)` en el prior) sí es exacto: se sortea la media normal y se aplica el mismo piso.

Lo que se guarda va en el espacio sin restricciones y el orden de la red: η = (μ_ν, log σ_ν, β, log c, log σ_ε) y
λ_i = (log ν_i, log(X_i(hoy) + 0,01)), como `NOMBRES_ETA` y `NOMBRES_LAM`.

    PYTHONPATH=. python <esta carpeta>/desgaste.py --caso flota          # el archivo del demo
    PYTHONPATH=. python <esta carpeta>/desgaste.py --simulados 5         # flotas simuladas, para comparar con la red

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
from jax.scipy.special import gammainc
from numpyro.infer import MCMC, NUTS
from scipy.stats import norm, qmc

from nucleo.desgaste import DISENO, EN_SERVICIO_BAJO, HORAS_POR_UNIDAD, NOMBRES_ETA, NOMBRES_LAM, PISO, PRIOR, preparar

numpyro.enable_x64()
CARPETA = Path(__file__).resolve().parent / "salida" / "desgaste"
NODOS_Z = 512                          # nodos fijos de cuasi Monte Carlo para Z(η)
FORMA_MINIMA = 1e-6


def _nodos_z() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Nodos fijos (exigencia, horas de hoy, ruido de log ν) de un camión al azar del diseño."""
    u = qmc.Sobol(3, seed=2026).random(NODOS_Z)
    u = np.clip(u, 1e-9, 1 - 1e-9)
    h_min, h_max = DISENO["miles_de_horas_hoy"]
    return norm.ppf(u[:, 0]), h_min + (h_max - h_min) * u[:, 1], norm.ppf(u[:, 2])


def log_z(mu_nu, sigma_nu, beta, c2, nodos) -> jnp.ndarray:
    """log Z(η): log de la probabilidad de que un camión al azar del diseño siga en servicio."""
    exigencia, hoy, ruido = nodos
    nu = jnp.exp(mu_nu + beta * exigencia + sigma_nu * ruido)
    return jnp.log(jnp.mean(gammainc(jnp.maximum(nu * hoy / c2, FORMA_MINIMA), EN_SERVICIO_BAJO / c2)))


def modelo(t, y, exigencia, hoy, fila, columna, t_anterior, t_siguiente, nodos):
    """t, y: (M, K) con relleno; exigencia, hoy: (M,). `fila`, `columna`: dónde están las lecturas reales.
    t_anterior, t_siguiente: los pares de lecturas consecutivas (t_k, t_{k+1}) de todos los camiones, en una sola lista;
    cada cociente X(t_k)/X(t_{k+1}) va en la posición (fila_c, columna_c) = (camión, k), que son las lecturas reales
    que no son la última de su camión."""
    p = PRIOR
    M = t.shape[0]
    mu_nu = numpyro.sample("mu_nu", dist.Normal(p["mu_nu_media"], p["mu_nu_desv"]))
    sigma_nu = jnp.maximum(numpyro.sample("sigma_nu_cruda", dist.HalfNormal(p["sigma_nu_escala"])), 1e-3)
    beta = numpyro.sample("beta", dist.Normal(p["beta_media"], p["beta_desv"]))
    log_c = numpyro.sample("log_c", dist.Normal(p["c_media"], p["c_desv"]))
    log_sigma_eps = numpyro.sample("log_sigma_eps", dist.Normal(p["sigma_eps_media"], p["sigma_eps_desv"]))
    c2 = jnp.exp(2 * log_c)

    # Ritmo de cada camión, no centrado: log ν_i = μ_ν + β·x_i + σ_ν·z_i.
    z = numpyro.sample("z_nu", dist.Normal(0.0, 1.0).expand([M]).to_event(1))
    log_nu = mu_nu + beta * exigencia + sigma_nu * z
    nu = jnp.exp(log_nu)

    # Desgaste de hoy: Gamma(ν·hoy/c², c²) recortada a (0; 0,92), sin normalizar por camión: la constante es Z(η).
    x_hoy = numpyro.sample("x_hoy", dist.Uniform(0.0, EN_SERVICIO_BAJO).expand([M]).to_event(1))
    numpyro.factor("gamma_hoy", dist.Gamma(jnp.maximum(nu * hoy / c2, FORMA_MINIMA), 1.0 / c2).log_prob(x_hoy).sum())
    numpyro.factor("en_servicio", -M * log_z(mu_nu, sigma_nu, beta, c2, nodos))

    # El resto de la trayectoria: cocientes Beta entre lecturas consecutivas.
    fila_c, columna_c = fila[1], columna[1]
    nu_c = nu[fila_c]
    cociente = numpyro.sample("cociente", dist.Beta(jnp.maximum(nu_c * t_anterior / c2, FORMA_MINIMA),
                                                    jnp.maximum(nu_c * (t_siguiente - t_anterior) / c2, FORMA_MINIMA)).to_event(1))
    log_b = jnp.zeros(t.shape).at[fila_c, columna_c].set(jnp.log(cociente))
    desde = log_b.sum(-1, keepdims=True) - jnp.cumsum(log_b, axis=-1) + log_b          # Σ_{j ≥ k} log b_j
    X = x_hoy[:, None] * jnp.exp(desde)
    numpyro.sample("obs", dist.Normal(X[fila[0], columna[0]], jnp.exp(log_sigma_eps)).to_event(1), obs=y[fila[0], columna[0]])

    numpyro.deterministic("eta", jnp.stack([mu_nu, jnp.log(sigma_nu), beta, log_c, log_sigma_eps]))
    numpyro.deterministic("lam", jnp.stack([log_nu, jnp.log(x_hoy + PISO)], axis=-1))


def argumentos(datos: dict) -> dict:
    """De `t`, `y`, `mascara` (M, K) y `exigencia` (M,) a los argumentos de `modelo`."""
    t, y = np.asarray(datos["t"], dtype=np.float64), np.asarray(datos["y"], dtype=np.float64)
    mascara = np.asarray(datos["mascara"]) > 0
    n = mascara.sum(-1)
    fila, columna = np.nonzero(mascara)
    no_ultima = columna < n[fila] - 1
    fila_c, columna_c = fila[no_ultima], columna[no_ultima]
    return {"t": jnp.asarray(t), "y": jnp.asarray(y), "exigencia": jnp.asarray(datos["exigencia"], dtype=jnp.float64),
            "hoy": jnp.asarray((t * mascara).max(-1)), "fila": (jnp.asarray(fila), jnp.asarray(fila_c)),
            "columna": (jnp.asarray(columna), jnp.asarray(columna_c)),
            "t_anterior": jnp.asarray(t[fila_c, columna_c]), "t_siguiente": jnp.asarray(t[fila_c, columna_c + 1]),
            "nodos": tuple(jnp.asarray(v) for v in _nodos_z())}


def correr(datos: dict, calentamiento: int = 500, muestras: int = 500, cadenas: int = 4, semilla: int = 0) -> dict:
    """Corre NUTS y devuelve `eta` (n, d), `lam` (n, U, d_local), los segundos de `mcmc.run` y los diagnósticos.

    datos: `t` (miles de horas), `y` (falla en 1), `mascara` (M, K) con el relleno al final, y `exigencia` (M,).
    """
    mcmc = MCMC(NUTS(modelo, target_accept_prob=0.9), num_warmup=calentamiento, num_samples=muestras,
                num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    args = argumentos(datos)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), **args, extra_fields=("diverging",))
    m = mcmc.get_samples()
    eta, lam = np.asarray(m["eta"]), np.asarray(m["lam"])
    segundos = time.time() - inicio
    por_cadena = mcmc.get_samples(group_by_chain=True)
    diag = numpyro.diagnostics.summary({k: np.asarray(por_cadena[k]) for k in ("eta", "lam")}, group_by_chain=True)
    junto = lambda campo: np.concatenate([np.asarray(diag[k][campo]).ravel() for k in ("eta", "lam")])     # noqa: E731
    return {"eta": eta, "lam": lam, "segundos": segundos, "r_hat": junto("r_hat"), "n_eff": junto("n_eff"),
            "divergencias": int(np.asarray(mcmc.get_extra_fields()["diverging"]).sum())}


def guardar(clave: str, resultado: dict, carpeta: Path = CARPETA, **extra) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{clave}.npz"
    np.savez(ruta, eta=resultado["eta"].astype(np.float32), lam=resultado["lam"].astype(np.float32),
             nombres_eta=np.array(NOMBRES_ETA), nombres_lam=np.array(NOMBRES_LAM), segundos=resultado["segundos"],
             r_hat=resultado["r_hat"], n_eff=resultado["n_eff"], divergencias=resultado["divergencias"], **extra)
    return ruta


def datos_del_caso(nombre: str) -> tuple[dict, dict]:
    """El archivo del caso, armado igual que `nucleo.desgaste.analizar`: (datos para `correr`, tensores de la red)."""
    from nucleo import series
    from nucleo.casos import cargar_caso
    caso = cargar_caso(nombre)
    leido = series.leer(caso, extras=("covariables", "horizonte_por_unidad"))
    limite = float(caso["columnas"].get("umbral", 1.0))
    leido, _ = series.revisar_tamano(caso, leido, DISENO, "")
    a_mantencion = leido["extras"]["horizonte_por_unidad"] / HORAS_POR_UNIDAD
    exigencia = leido["extras"]["covariables"]
    t, mascara = series.con_relleno([ti / HORAS_POR_UNIDAD for ti in leido["t"]])
    y, _ = series.con_relleno([yi / limite for yi in leido["y"]])
    x, cov, tam = preparar(t, y, mascara, exigencia, a_mantencion)
    return ({"t": t, "y": y, "mascara": mascara, "exigencia": exigencia},
            {"x": x, "mascara": mascara, "cov": cov, "tam": tam, "ids": np.array(leido["ids"])})


def _linea(clave: str, ruta: Path, r: dict) -> str:
    return json.dumps({"clave": clave, "ruta": str(ruta), "segundos": round(r["segundos"], 1),
                       "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3), "n_eff_min": round(float(np.nanmin(r["n_eff"]))),
                       "divergencias": r["divergencias"], "unidades": int(r["lam"].shape[1])})


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--caso", default=None, help="nombre de un caso de casos/ con motor desgaste (el archivo del demo)")
    p.add_argument("--simulados", type=int, default=0, help="cuántas flotas simuladas (semilla fija)")
    p.add_argument("--simulado", type=int, default=None, help="solo la flota simulada de ese índice")
    p.add_argument("--muestras", type=int, default=500)
    p.add_argument("--calentamiento", type=int, default=500)
    p.add_argument("--cadenas", type=int, default=4)
    a = p.parse_args()
    opciones = {"calentamiento": a.calentamiento, "muestras": a.muestras, "cadenas": a.cadenas}

    if a.caso:
        datos, tensores = datos_del_caso(a.caso)
        r = correr(datos, **opciones)
        print(_linea(a.caso, guardar(a.caso, r, **tensores), r), flush=True)
    if a.simulados or a.simulado is not None:
        from motor.desgaste.simular import simular
        for i in (range(a.simulados) if a.simulado is None else [a.simulado]):
            s = simular(np.random.default_rng([2026, i]), 1)
            datos = {"t": s["t"][0], "y": s["y"][0], "mascara": s["mascara"][0], "exigencia": s["exigencia"][0]}
            r = correr(datos, semilla=i, **opciones)
            clave = f"simulado_{i:02d}"
            ruta = guardar(clave, r, x=s["x"][0], mascara=s["mascara"][0], cov=s["cov"][0], tam=s["tam"][0],
                           eta_verdadero=s["eta"][0], lam_verdadero=s["lam"][0])
            print(_linea(clave, ruta, r), flush=True)


if __name__ == "__main__":
    main()
