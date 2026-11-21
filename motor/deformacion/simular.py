"""Simulador del motor `deformacion`: muros inventados con el modelo de `WORKPLAN.md`, 11.2.

Tres niveles, en este orden: el **diseño** del dataset (cuántos sectores, cuántas lecturas en la ventana y cuáles
faltan en cada sector), los parámetros globales η del muro y los locales λ_j de cada sector, con su estado discreto
z_j (estable o acelerando). El diseño se sortea en cada lote, dentro de `nucleo.deformacion.DISENO`: la red no
practica con un tamaño fijo.

Las lecturas pasan por el mismo preprocesamiento que el archivo de un usuario (`nucleo.deformacion.preparar`): resta
de la primera lectura y de la mediana entre sectores, y división por la escala e del dataset. Por eso η y λ se
entregan en esas mismas unidades: a μ_v, μ_A, log σ_e, log v_j y log A_j se les resta log e. Los demás no tienen
unidades de desplazamiento (π, σ_v, σ_f, μ_f y log(u_f − 1), que se mide en ventanas).

El modo común (la atmósfera, que mueve la lectura de todos los sectores a la vez) se simula como una perturbación
AR(1) de amplitud al azar. No es un parámetro que se infiera: el preprocesamiento lo resta exacto de cada sector,
y queda solo en el canal de la mediana, que la red ve.

Es la especificación que pide `motor/comun/series.py`.
"""

from __future__ import annotations

import numpy as np

from nucleo.deformacion import (CANALES, CON_CLASE, DIM_COV, DIM_TAM, DISENO, MOTOR_ID, NOMBRES_ETA, NOMBRES_LAM, PRIOR,
                                cantidad, preparar, trayectoria)

__all__ = ["MOTOR_ID", "NOMBRES_ETA", "NOMBRES_LAM", "CANALES", "DIM_COV", "DIM_TAM", "DISENO", "PRIOR", "CON_CLASE",
           "simular", "cantidad_de"]

MODO_COMUN_MAX = 0.4        # amplitud del modo común, hasta 40% del movimiento del sector típico
MODO_COMUN_RHO = (0.80, 0.98)


def _log_uniforme_entero(gen: np.random.Generator, bajo: int, alto: int) -> int:
    return int(min(alto, np.floor(np.exp(gen.uniform(np.log(bajo), np.log(alto + 1))))))


def prior_eta(gen: np.random.Generator, lote: int) -> dict[str, np.ndarray]:
    """η del prior, en las unidades del modelo (antes de dividir por e)."""
    p = PRIOR
    pi = np.clip(gen.beta(p["pi_a"], p["pi_b"], lote), 1e-4, 1 - 1e-4)
    return {
        "pi": pi,
        "mu_v": p["mu_v_media"] + p["mu_v_desv"] * gen.standard_normal(lote),
        "sigma_v": np.maximum(p["sigma_v_escala"] * np.abs(gen.standard_normal(lote)), 1e-3),
        "mu_f": p["mu_f_media"] + p["mu_f_desv"] * gen.standard_normal(lote),
        "sigma_f": np.maximum(p["sigma_f_escala"] * np.abs(gen.standard_normal(lote)), 1e-3),
        "mu_A": p["mu_A_media"] + p["mu_A_desv"] * gen.standard_normal(lote),
        "log_sigma_e": p["sigma_e_media"] + p["sigma_e_desv"] * gen.standard_normal(lote),
    }


def disenar(gen: np.random.Generator, lote: int) -> dict:
    """El nivel de diseño. Sectores y lecturas de la ventana son comunes al lote (no se gasta relleno); las faltantes
    cambian en cada sector: a cada uno le falta una fracción f_j ~ Uniforme(0, 0,15) de sus lecturas, al azar."""
    sectores = _log_uniforme_entero(gen, *DISENO["unidades"])
    lecturas = _log_uniforme_entero(gen, *DISENO["lecturas"])
    u = np.arange(1, lecturas + 1) / lecturas                                         # a paso parejo; 1 = la última lectura
    faltan = np.floor(gen.uniform(*DISENO["faltantes"], (lote, sectores)) * lecturas).astype(int)
    sorteo = gen.random((lote, sectores, lecturas))
    corte = np.take_along_axis(np.sort(sorteo, axis=-1), faltan[..., None], -1)        # las `faltan` de menor sorteo, fuera
    mascara = (sorteo >= corte).astype(np.float32)
    return {"u": u, "mascara": mascara}


def simular(gen: np.random.Generator, lote: int) -> dict:
    d = disenar(gen, lote)
    u, mascara = d["u"], d["mascara"]
    sectores, lecturas = mascara.shape[1:]
    g = prior_eta(gen, lote)
    forma = (lote, sectores)
    z = (gen.random(forma) < g["pi"][:, None]).astype(np.float64)
    log_v = g["mu_v"][:, None] + g["sigma_v"][:, None] * gen.standard_normal(forma)
    log_falta = g["mu_f"][:, None] + g["sigma_f"][:, None] * gen.standard_normal(forma)
    log_A = g["mu_A"][:, None] + PRIOR["sigma_A"] * gen.standard_normal(forma)
    limpio = trayectoria(u, log_v[..., None], log_falta[..., None], log_A[..., None], z[..., None])     # (B, U, K)
    # Modo común: AR(1) estacionario, igual para todos los sectores del dataset.
    rho = gen.uniform(*MODO_COMUN_RHO, lote)[:, None]
    choques = gen.standard_normal((lote, lecturas)) * np.sqrt(1 - rho**2)
    comun = np.zeros((lote, lecturas))
    comun[:, 0] = gen.standard_normal(lote)
    for k in range(1, lecturas):
        comun[:, k] = rho[:, 0] * comun[:, k - 1] + choques[:, k]
    comun *= (gen.uniform(0, MODO_COMUN_MAX, lote) * np.exp(g["mu_v"]))[:, None]
    y = limpio + comun[:, None, :] + np.exp(g["log_sigma_e"])[:, None, None] * gen.standard_normal(limpio.shape)
    y = y * mascara
    x, cov, tam, log_e = preparar(u, y, mascara)
    le = log_e[:, None]
    eta = np.stack([np.log(g["pi"] / (1 - g["pi"])), g["mu_v"] - log_e, np.log(g["sigma_v"]), g["mu_f"], np.log(g["sigma_f"]),
                    g["mu_A"] - log_e, g["log_sigma_e"] - log_e], axis=-1)
    lam = np.stack([log_v - le, log_falta, log_A - le, z], axis=-1)
    return {"x": x, "mascara": mascara, "cov": cov, "tam": tam, "eta": eta.astype(np.float32), "lam": lam.astype(np.float32),
            "cantidad": cantidad(lam), "extra": {}, "u": u, "y": y, "log_e": log_e}


def cantidad_de(eta: np.ndarray, lam: np.ndarray, extra: dict) -> np.ndarray:
    """Lo que se decide, en su versión continua, para muestras del posterior: lam (L, B, U, 4) → (L, B, U)."""
    return cantidad(lam)
