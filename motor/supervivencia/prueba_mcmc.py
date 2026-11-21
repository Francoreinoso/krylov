"""El modelo en NumPyro de `supervivencia`: su densidad coincide con la cuenta directa en NumPy, y NUTS da unos pasos.

No es una corrida de MCMC (eso se hace sin nada entrenando): una evaluación de la densidad y un
puñado de pasos sobre una empresa chica.
"""
import json

import jax.numpy as jnp
import numpy as np
import pytest
from numpyro.infer.util import log_density

from motor.supervivencia import mcmc, simular
from nucleo import supervivencia as sv

PRIOR = simular.cargar_config()["prior"]
# El prior candidato (cargas con un nivel común por empresa): el modelo de NumPyro tiene que seguirlo igual que el simulador.
CANDIDATO = json.loads((simular.RAIZ / "motor" / "supervivencia" / "config_candidato.json").read_text(encoding="utf-8"))["prior"]
LOG_2PI_MEDIO = 0.9189385332046727


def _empresa(n=150):
    lote = simular.simular(np.random.default_rng(4), 1, n, simular.cargar_config())
    return {c: v[0] for c, v in sv.variables_del_modelo(lote).items()}, lote["theta"][0].astype(np.float64)


@pytest.mark.parametrize("PRIOR", [PRIOR, CANDIDATO], ids=["vigente", "candidato"])
def test_densidad_igual_a_la_cuenta_directa(PRIOR):
    d, libre = _empresa()
    rng = np.random.default_rng(0)
    n = len(d["tiempo"])
    th = {c: v[0] for c, v in sv.a_restringido((libre + rng.normal(0, 0.2, sv.DIM_THETA))[None]).items()}
    pasos = np.diff(th["gamma"], prepend=0.0) / np.r_[PRIOR["gamma1_desv"], np.full(5, th["tau"])]
    u_crudo, z = rng.normal(size=sv.CARGOS_MAX), rng.normal(size=n)
    valores = {"k": th["k"], "beta0": th["beta0"], "beta": th["beta"], "tau": th["tau"], "pasos_gamma": pasos, "sigma_u": th["sigma_u"],
               "lambda": th["lambda"], "a": th["a"], "cortes": th["cortes"], "mu_c": th["mu_c"], "s_c": th["s_c"], "u_crudo": u_crudo, "z": z}
    nivel_a, comun = PRIOR.get("a_log_media", 0.0), PRIOR.get("a_log_desv_comun", 0.0)
    if comun > 0:                                             # el nivel común de las cargas es un latente más
        nivel_a = valores["nivel_a"] = nivel_a + 0.3
    log_p, traza = log_density(mcmc.modelo, mcmc.argumentos(d, PRIOR), {}, {c: jnp.asarray(v) for c, v in valores.items()})
    # El θ determinista del modelo es el mismo vector sin restricciones que usa el flujo.
    np.testing.assert_allclose(np.asarray(traza["theta"]["value"]), sv.a_libre({c: np.asarray(v)[None] for c, v in th.items()})[0], rtol=1e-10, atol=1e-10)

    normal = lambda v, media, desv: (-0.5 * ((v - media) / desv) ** 2 - np.log(desv) - LOG_2PI_MEDIO).sum()           # noqa: E731
    log_normal = lambda v, desv, media=0.0: normal(np.log(v), media, desv) - np.log(v).sum()                           # noqa: E731
    media_normal = lambda v, escala: normal(v, 0.0, escala) + np.log(2.0)                                              # noqa: E731
    log_prior = (log_normal(th["k"], PRIOR["k_log_desv"]) + normal(th["beta0"], PRIOR["beta0_media"], PRIOR["beta0_desv"])
                 + normal(th["beta"], 0.0, PRIOR["beta_desv"]) + media_normal(th["tau"], PRIOR["tau_escala"]) + normal(pasos, 0.0, 1.0)
                 + media_normal(th["sigma_u"], PRIOR["sigma_u_escala"]) + normal(th["lambda"], 0.0, PRIOR["lambda_desv"])
                 + log_normal(th["a"], PRIOR["a_log_desv"], nivel_a) + (normal(np.array(nivel_a), PRIOR["a_log_media"], comun) if comun > 0 else 0.0)
                 + normal(th["cortes"], 0.0, PRIOR["cortes_desv"]) + 4 * np.log(6.0)
                 + normal(th["mu_c"], PRIOR["mu_c_media"], PRIOR["mu_c_desv"]) + media_normal(th["s_c"], PRIOR["s_c_escala"])
                 + normal(u_crudo, 0.0, 1.0) + normal(z, 0.0, 1.0))
    # Encuestas: logit ordenado.
    logistica = lambda v: 1 / (1 + np.exp(-v))                                                                         # noqa: E731
    cortes = np.concatenate([np.full((4, 1), -np.inf), th["cortes"], np.full((4, 1), np.inf)], axis=1)
    nivel = d["encuestas"]                                                                                             # 1..4
    j = np.arange(4)
    log_encuestas = np.log(logistica(cortes[j, nivel] - th["a"] * z[:, None]) - logistica(cortes[j, nivel - 1] - th["a"] * z[:, None])).sum()
    # Años y evento: verosimilitud por intervalos, con la censura del módulo del servicio (math.erfc).
    t = d["tiempo"]
    h = np.exp(th["beta0"] + d["x"] @ th["beta"] + sv.base_spline(d["w"]) @ th["gamma"] + th["sigma_u"] * u_crudo[d["grupo"]] - th["lambda"] * z)
    s_c = lambda c: sv.supervivencia_censura(c, th["mu_c"], th["s_c"])                                                 # noqa: E731
    f1 = (np.exp(-h * t ** th["k"]) - np.exp(-h * (t + 1) ** th["k"])) * s_c(t + 0.5)
    f0 = np.exp(-h * (t + 0.5) ** th["k"]) * (s_c(t) - s_c(t + 1))
    log_evento = np.log(np.where(d["evento"] == 1, f1, np.where(d["evento"] == 0, f0, f1 + f0))).sum()
    directo = log_prior + log_encuestas + log_evento
    assert np.isnan(d["evento"]).sum() == 30 and (t == 0).any()                       # hay personas por decidir y con cero años
    assert abs(float(log_p) - directo) < 1e-8 * abs(directo), (float(log_p), directo)


def test_nuts_da_unos_pasos():
    d, _ = _empresa()
    r = mcmc.correr(d, calentamiento=30, muestras=20, cadenas=1)
    assert r["theta"].shape == (20, sv.DIM_THETA) and np.isfinite(r["theta"]).all()
