"""MCMC de referencia del motor `deformacion`: NUTS (NumPyro) sobre η, los λ_j continuos y el modo común, con z_j marginalizado.

El mismo modelo que `motor/deformacion/simular.py` (`WORKPLAN.md`, 11.2), condicionado a lo mismo que ve la red:

- **Estado discreto.** z_j (estable o acelerando) se marginaliza: cada sector aporta una mezcla de dos componentes sobre su
  serie entera, con peso π. Después z_j se sortea de su condicional exacta dado lo continuo y va como última columna de λ.
- **Modo común.** Es un latente más, con su prior exacto: AR(1) estacionario, ρ ~ Uniforme(0,80; 0,98) y amplitud
  a·exp(μ_v), a ~ Uniforme(0; 0,4). Dado el modo común, los sectores son independientes y la mezcla es por sector.
- **Primera lectura.** La red ve cada sector contado desde su primera lectura. Aquí eso es un desplazamiento inicial o_j
  por sector con prior plano, marginalizado en forma cerrada (residuos centrados por sector, n_j − 1 grados de libertad).
- **Escala.** La red ve las lecturas divididas por la escala e del archivo y no conoce e. Aquí los datos son D = s·D',
  con D' = lecturas / e y s incógnita con medida plana; el jacobiano de pasar de D a (D', s) es s^(n − U − 1)
  (n lecturas, U desplazamientos iniciales ya marginalizados). Se muestrea directo en las unidades de la red (μ_v, μ_A,
  log σ_e, log v_j, log A_j y el modo común, todos divididos por s): ese jacobiano se cancela con el de σ_e en la
  verosimilitud, y log s queda solo en los priors de μ_v, μ_A y log σ_e.

Aproximaciones, dichas: los pisos y recortes numéricos del prior (σ ≥ 0,001; π en [0,0001; 0,9999]) no se replican, y la
red ve además la mediana entre sectores ya calculada, que aquí entra por las lecturas mismas.
"""
from __future__ import annotations

import math
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
from nucleo.deformacion import (DISENO, FALTANTES_TOLERADAS, MIN_LECTURAS_SECTOR, PRACTICA, PRIOR as P, a_grilla, en_la_grilla,  # noqa: E402
                                normalizar_tiempo, preparar)

MOTOR_ID = "deformacion"
LAM_CONTINUAS = 3
MODO_COMUN_MAX, MODO_COMUN_RHO = 0.4, (0.80, 0.98)        # como en `motor/deformacion/simular.py`


def modelo(u, yp, mascara, log_ruido_rel=0.0):
    U, K = yp.shape
    n_j = mascara.sum(-1)
    pi = numpyro.sample("pi", dist.Beta(P["pi_a"], P["pi_b"]))
    # Se muestrea en las unidades de la red (divididas por s): ahí los datos identifican los parámetros, y log s
    # queda solo en los tres priors con unidades de desplazamiento. Es un cambio de variables, no otro modelo.
    plano = dist.ImproperUniform(dist.constraints.real, (), ())
    mu_v = numpyro.sample("mu_v", plano)
    sigma_v = numpyro.sample("sigma_v", dist.HalfNormal(P["sigma_v_escala"]))
    mu_f = numpyro.sample("mu_f", dist.Normal(P["mu_f_media"], P["mu_f_desv"]))
    sigma_f = numpyro.sample("sigma_f", dist.HalfNormal(P["sigma_f_escala"]))
    mu_A = numpyro.sample("mu_A", plano)
    log_sigma_e = numpyro.sample("log_sigma_e", plano)
    a = numpyro.sample("a", dist.Uniform(0.0, MODO_COMUN_MAX))
    rho = numpyro.sample("rho", dist.Uniform(*MODO_COMUN_RHO))
    log_s = numpyro.sample("log_s", plano)
    numpyro.factor("prior_con_unidades", dist.Normal(P["mu_v_media"], P["mu_v_desv"]).log_prob(mu_v + log_s)
                   + dist.Normal(P["mu_A_media"], P["mu_A_desv"]).log_prob(mu_A + log_s)
                   + dist.Normal(P["sigma_e_media"], P["sigma_e_desv"]).log_prob(log_sigma_e + log_s))
    with numpyro.plate("sectores", U):
        log_v = numpyro.sample("log_v", dist.Normal(mu_v, sigma_v))
        z_f = numpyro.sample("z_f", dist.Normal(0.0, 1.0))
        z_A = numpyro.sample("z_A", dist.Normal(0.0, 1.0))
    log_falta, log_A = mu_f + sigma_f * z_f, mu_A + P["sigma_A"] * z_A
    y = yp
    d0 = jnp.exp(log_v)[:, None] * u[None, :]
    u_f = 1.0 + jnp.exp(log_falta)[:, None]
    d1 = d0 + jnp.exp(log_A)[:, None] * jnp.log(u_f / (u_f - u[None, :]))
    # Modo común: AR(1) estacionario de amplitud a·exp(μ_v), también dividido por s (el jacobiano s^K se cancela con la
    # amplitud). Se muestrea como desvío δ respecto del promedio entre sectores de lo que queda al restar la componente
    # estable (c = δ + ese promedio): es un corrimiento que depende solo de los otros parámetros (jacobiano 1) y quita
    # la correlación entre el modo común y las velocidades de todos los sectores.
    r0 = (y - d0) * mascara
    r0 = (r0 - (r0.sum(-1) / n_j)[:, None]) * mascara
    delta = numpyro.sample("delta", dist.ImproperUniform(dist.constraints.real, (), (K,)))
    c = delta + r0.sum(0) / jnp.maximum(mascara.sum(0), 1.0)
    amp = a * jnp.exp(mu_v)
    innov = (c[1:] - rho * c[:-1]) / (amp * jnp.sqrt(1.0 - rho**2))
    numpyro.factor("modo_comun", -K * jnp.log(amp) - 0.5 * (K - 1) * jnp.log1p(-rho**2) - 0.5 * (c[0] / amp) ** 2 - 0.5 * (innov**2).sum())

    def log_l(d):                      # por sector, con el desplazamiento inicial (prior plano) marginalizado
        r = (y - c[None, :] - d) * mascara
        centrado = (r - (r.sum(-1) / n_j)[:, None]) * mascara
        return -(n_j - 1.0) * log_sigma_e - 0.5 * (centrado**2).sum(-1) * jnp.exp(-2.0 * log_sigma_e)

    l0, l1 = log_l(d0), log_l(d1)
    mezcla = jnp.logaddexp(jnp.log1p(-pi) + l0, jnp.log(pi) + l1)
    numpyro.factor("verosimilitud", mezcla.sum())
    numpyro.deterministic("logit_z", jnp.log(pi) - jnp.log1p(-pi) + l1 - l0)
    numpyro.deterministic("eta", jnp.stack([jnp.log(pi) - jnp.log1p(-pi), mu_v, jnp.log(sigma_v), mu_f, jnp.log(sigma_f), mu_A, log_sigma_e]))
    numpyro.deterministic("lam3", jnp.stack([log_v, log_falta, log_A], axis=-1))


def inicial(datos):
    """Punto de partida: cada sector parte del ajuste por mínimos cuadrados de su componente acelerada (grilla en log_falta).

    No cambia el posterior: evita que las cadenas partan con todos los sectores como estables y el ruido de lectura
    inflado, un modo local del que la mezcla no sale. Un sector estable ajusta A cerca de cero y la mezcla lo devuelve a z = 0."""
    u, yp, m = (np.asarray(datos[k]) for k in ("u", "yp", "mascara"))
    U, K = yp.shape
    hay = m > 0
    rel = np.where(hay, yp - yp[np.arange(U), np.argmax(hay, -1)][:, None], np.nan)
    comun_ = np.nan_to_num(np.nanmedian(rel, axis=0))                     # el muro típico más el modo común
    v_med = max(float(np.polyfit(u, comun_, 1)[0]), 0.05)
    log_v, log_f, log_A = np.zeros(U), np.zeros(U), np.zeros(U)
    for j in range(U):
        k = hay[j]
        r, uj = rel[j, k] - comun_[k], u[k]
        mejor = None
        for lf in np.linspace(-4.0, 1.5, 23):
            u_f = 1.0 + np.exp(lf)
            X = np.stack([np.ones_like(uj), uj, np.log(u_f / (u_f - uj))], axis=-1)
            coef, *_ = np.linalg.lstsq(X, r, rcond=None)
            ss = float(((X @ coef - r) ** 2).sum()) if coef[2] > 0 else np.inf
            if mejor is None or ss < mejor[0]:
                mejor = (ss, lf, coef)
        if not np.isfinite(mejor[0]):                                     # ninguna aceleración positiva: sector estable
            pendiente = np.polyfit(uj, r, 1)[0]
            log_v[j], log_f[j], log_A[j] = np.log(max(v_med + pendiente, 0.02)), P["mu_f_media"], P["mu_A_media"] - 1.0
        else:
            _, lf, coef = mejor
            log_v[j], log_f[j], log_A[j] = np.log(max(v_med + coef[1], 0.02)), lf, np.log(max(coef[2], 0.02))
    mu_A0 = float(np.clip(np.median(log_A), -1.5, 1.5))
    return {"pi": 0.2, "mu_v": float(np.median(log_v)), "sigma_v": 0.5, "mu_f": P["mu_f_media"], "sigma_f": 0.6, "mu_A": mu_A0,
            "log_sigma_e": -float(np.asarray(datos["log_ruido_rel"])), "a": 0.2, "rho": 0.9, "log_s": 0.0,
            "log_v": jnp.asarray(log_v), "z_f": jnp.asarray(np.clip((log_f - P["mu_f_media"]) / 0.6, -3, 3)),
            "z_A": jnp.asarray(np.clip((log_A - mu_A0) / P["sigma_A"], -3, 3)), "delta": jnp.zeros(K)}


def a_eta_lam(muestras, datos):
    logit = np.asarray(muestras["logit_z"])
    z = (np.random.default_rng(0).random(logit.shape) < 1.0 / (1.0 + np.exp(-np.clip(logit, -700, 700)))).astype(np.float64)
    return np.asarray(muestras["eta"]), np.concatenate([np.asarray(muestras["lam3"]), z[..., None]], axis=-1)


def _datos(u, y, mascara, log_e, tam):
    return {"u": jnp.asarray(u, dtype=jnp.float64), "yp": jnp.asarray(y * mascara / np.exp(log_e), dtype=jnp.float64),
            "mascara": jnp.asarray(mascara, dtype=jnp.float64), "log_ruido_rel": float(tam[2])}


def datos_del_caso(nombre):
    """Las mismas lecturas, en la misma grilla, que usa `nucleo.deformacion.analizar` con el archivo del caso."""
    caso = cargar_caso(nombre)
    leido, grilla, _ = a_grilla(series.leer(caso))
    k_min = max(MIN_LECTURAS_SECTOR, math.ceil(len(grilla) * (1 - FALTANTES_TOLERADAS)))
    leido, _ = series.revisar_tamano(caso, leido, {"unidades": DISENO["unidades"], "lecturas": (k_min, len(grilla))}, PRACTICA)
    y, mascara = en_la_grilla(leido, grilla)
    u, _, _ = normalizar_tiempo(grilla)
    x, cov, tam, log_e = preparar(u, y, mascara)
    return _datos(u, y, mascara, log_e, tam), {"x": x, "mascara": mascara, "cov": cov, "tam": tam}, {"ids": np.array(leido["ids"]), "log_e": log_e}


def datos_simulados(i):
    from motor.deformacion.simular import simular
    sim = simular(np.random.default_rng([2026, i]), 1)
    return (_datos(sim["u"], sim["y"][0], sim["mascara"][0], sim["log_e"][0], sim["tam"][0]),
            {"x": sim["x"][0], "mascara": sim["mascara"][0], "cov": sim["cov"][0], "tam": sim["tam"][0]},
            {"eta_verdadero": sim["eta"][0], "lam_verdadero": sim["lam"][0], "log_e": sim["log_e"][0]})


if __name__ == "__main__":
    comun.principal(sys.modules[__name__])
