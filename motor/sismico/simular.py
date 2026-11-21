"""Simulador del motor `sismico`: minas inventadas con el modelo de `WORKPLAN.md`, 11.5.

Tres niveles, en este orden: el **diseño** del dataset (cuántos sectores y cuántas horas se llevan observadas desde la
tronadura), los parámetros globales η de la mina y los locales λ_s de cada sector (su tasa de fondo μ_s y los sismos
A_s que gatilla directamente la tronadura). El número de sismos de cada sector no se sortea aparte: sale del proceso.

El proceso de Hawkes se simula **por ramificación**, vectorizado por generaciones sobre todos los sectores del lote:
los inmigrantes del fondo (Poisson de tasa μ_s en la ventana), los hijos directos de la tronadura (Poisson(A_s), con
demoras exponenciales de tasa ω) y, generación tras generación, los hijos de cada sismo (Poisson(κ(m)), misma demora).

**Tope de 300 sismos por sector.** Un dataset con algún sector sobre el tope se descarta y se sortea otro: el modelo es
el prior condicionado a «ningún sector pasa de 300», y el servicio no responde un archivo que lo pase.

Es la especificación que pide `motor/comun/series.py`.
"""

from __future__ import annotations

import numpy as np

from nucleo.sismico import (CANALES, DIM_COV, DIM_TAM, DISENO, HORIZONTE_REF, LN10, MAGNITUD_REF, MAX_SISMOS, MOTOR_ID, NOMBRES_ETA,
                            NOMBRES_LAM, PRIOR, esperados, excitacion, preparar)

__all__ = ["MOTOR_ID", "NOMBRES_ETA", "NOMBRES_LAM", "CANALES", "DIM_COV", "DIM_TAM", "DISENO", "PRIOR", "simular", "cantidad_de", "ramificar"]


def prior_eta(gen: np.random.Generator, lote: int) -> np.ndarray:
    """η en espacio sin restricciones: (μ_μ, log σ_μ, logit n, log α, log ω, log b), con α < b·ln 10."""
    p = PRIOR
    n = np.clip(gen.beta(p["n_a"], p["n_b"], lote), 1e-3, 0.98)
    log_alfa = p["alfa_media"] + p["alfa_desv"] * gen.standard_normal(lote)
    log_b = p["b_media"] + p["b_desv"] * gen.standard_normal(lote)
    while True:                                                    # la restricción α < 0,95·b·ln 10: casi siempre se cumple
        mal = np.flatnonzero(np.exp(log_alfa) >= 0.95 * np.exp(log_b) * LN10)
        if len(mal) == 0:
            break
        log_alfa[mal] = p["alfa_media"] + p["alfa_desv"] * gen.standard_normal(len(mal))
        log_b[mal] = p["b_media"] + p["b_desv"] * gen.standard_normal(len(mal))
    return np.stack([
        p["mu_mu_media"] + p["mu_mu_desv"] * gen.standard_normal(lote),
        np.log(np.maximum(p["sigma_mu_escala"] * np.abs(gen.standard_normal(lote)), 1e-3)),
        np.log(n / (1 - n)), log_alfa,
        p["omega_media"] + p["omega_desv"] * gen.standard_normal(lote), log_b,
    ], axis=-1)


def ramificar(gen: np.random.Generator, mu: np.ndarray, A: np.ndarray, n: np.ndarray, alfa: np.ndarray, omega: np.ndarray,
              beta: np.ndarray, T: np.ndarray, tope: int | None = MAX_SISMOS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """El proceso de Hawkes de G sectores en [0, T], por ramificación. Todos los argumentos son de forma (G,).

    Devuelve (sector, hora, magnitud − m_0) de cada sismo, sin ordenar. Con `tope`, un sector que lo pasa deja de
    ramificarse (su dataset se va a descartar igual) y queda con más de `tope` sismos, para que se note."""
    G = len(mu)
    g_fondo = np.repeat(np.arange(G), gen.poisson(mu * T))
    g_tron = np.repeat(np.arange(G), gen.poisson(A))
    g = np.concatenate([g_fondo, g_tron])
    t = np.concatenate([gen.uniform(0.0, T[g_fondo]), gen.exponential(1.0 / omega[g_tron])])
    dentro = t < T[g]
    g, t = g[dentro], t[dentro]
    m = gen.exponential(1.0 / beta[g])
    todos = [(g, t, m)]
    cuenta = np.bincount(g, minlength=G)
    while len(g):
        if tope is not None:                                       # los sectores que ya pasaron el tope no siguen
            sigue = cuenta[g] <= tope
            g, t, m = g[sigue], t[sigue], m[sigue]
        hijos = gen.poisson(n[g] * np.exp(np.minimum(alfa[g] * m, 50.0)) * (beta[g] - alfa[g]) / beta[g])
        g = np.repeat(g, hijos)
        t = np.repeat(t, hijos) + gen.exponential(1.0 / omega[g])
        dentro = t < T[g]
        g, t = g[dentro], t[dentro]
        m = gen.exponential(1.0 / beta[g])
        todos.append((g, t, m))
        cuenta = cuenta + np.bincount(g, minlength=G)
    return tuple(np.concatenate(v) for v in zip(*todos))


def _intento(gen: np.random.Generator, lote: int, sectores: int) -> dict:
    """`lote` datasets con `sectores` sectores cada uno, con relleno hasta el tope, y cuáles respetan el tope."""
    eta = prior_eta(gen, lote)
    v_min, v_max = DISENO["ventana_horas"]
    T = np.exp(gen.uniform(np.log(v_min), np.log(v_max), lote))
    forma = (lote, sectores)
    log_mu = eta[:, None, 0] + np.exp(eta[:, None, 1]) * gen.standard_normal(forma)
    log_A = PRIOR["A_media"] + PRIOR["A_desv"] * gen.standard_normal(forma)
    por_sector = lambda v: np.repeat(v, sectores)                                     # noqa: E731
    n = 1.0 / (1.0 + np.exp(-eta[:, 2]))
    g, t, m = ramificar(gen, np.exp(log_mu).ravel(), np.exp(log_A).ravel(), por_sector(n), por_sector(np.exp(eta[:, 3])),
                        por_sector(np.exp(eta[:, 4])), por_sector(np.exp(eta[:, 5]) * LN10), por_sector(T))
    cuenta = np.bincount(g, minlength=lote * sectores)
    orden = np.lexsort((t, g))
    g, t, m = g[orden], t[orden], m[orden]
    puesto = np.arange(len(g)) - np.concatenate([[0], np.cumsum(cuenta)])[g]           # lugar del sismo dentro de su sector
    cabe = puesto < MAX_SISMOS
    ts, ms, mascara = (np.zeros((lote * sectores, MAX_SISMOS)) for _ in range(3))
    ts[g[cabe], puesto[cabe]], ms[g[cabe], puesto[cabe]], mascara[g[cabe], puesto[cabe]] = t[cabe], m[cabe], 1.0
    a_forma = lambda v: v.reshape(forma + (MAX_SISMOS,))                               # noqa: E731
    return {"eta": eta, "T": T, "lam": np.stack([log_mu, log_A], axis=-1), "t": a_forma(ts), "m": a_forma(ms), "mascara": a_forma(mascara),
            "vale": (cuenta.reshape(forma) <= MAX_SISMOS).all(-1)}


def simular(gen: np.random.Generator, lote: int) -> dict:
    sectores = int(gen.integers(DISENO["unidades"][0], DISENO["unidades"][1] + 1))     # común al lote
    partes, faltan = [], lote
    while faltan > 0:                                                                  # los datasets sobre el tope se sortean de nuevo
        intento = _intento(gen, faltan, sectores)
        vale = intento.pop("vale")
        partes.append({k: v[vale] for k, v in intento.items()})
        faltan -= int(vale.sum())
    d = {k: np.concatenate([p[k] for p in partes]) for k in partes[0]}
    K = max(1, int(d["mascara"].sum(-1).max()))
    t, m, mascara, T = d["t"][..., :K], d["m"][..., :K], d["mascara"][..., :K], d["T"]
    x, mascara_x, cov, tam = preparar(t, m, mascara, T)
    extra = {"t": t, "m": m, "mascara": mascara, "T": T}
    return {"x": x, "mascara": mascara_x, "cov": cov, "tam": tam, "eta": d["eta"].astype(np.float32), "lam": d["lam"].astype(np.float32),
            "cantidad": cantidad_de(d["eta"][None], d["lam"][None], extra)[0], "extra": extra}


def cantidad_de(eta: np.ndarray, lam: np.ndarray, extra: dict) -> np.ndarray:
    """Lo que se decide, en una versión continua para la cobertura: el log del número esperado de sismos fuertes (2 magnitudes
    sobre la mínima) en las 6 horas siguientes. eta (L, B, d), lam (L, B, S, 2) → (L, B, S)."""
    de_los_sismos = excitacion(eta, extra["t"], extra["m"], extra["mascara"], extra["T"])
    n_esperado = esperados(eta, lam, de_los_sismos, extra["T"], HORIZONTE_REF)
    return np.log(np.maximum(n_esperado, 1e-300)) - np.exp(eta[..., 5])[..., None] * LN10 * MAGNITUD_REF
