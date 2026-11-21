"""Simulador del motor `cinetica`: plantas de flotación inventadas con el modelo de `WORKPLAN.md`, 11.3.

Tres niveles, en este orden: el **diseño** del dataset (cuántas líneas, cuántas celdas, cuántas medidas en cada
línea y a qué tiempos), los parámetros globales η de la planta y los locales λ_b de cada línea. El diseño se sortea
en cada lote, dentro de `nucleo.cinetica.DISENO`: la red no practica con un tamaño fijo.

Es la especificación que pide `motor/comun/series.py`.
"""

from __future__ import annotations

import numpy as np

from nucleo.cinetica import CANALES, DIM_COV, DIM_TAM, DISENO, MOTOR_ID, NOMBRES_ETA, NOMBRES_LAM, PRIOR, final_de_linea, preparar, recuperacion

__all__ = ["MOTOR_ID", "NOMBRES_ETA", "NOMBRES_LAM", "CANALES", "DIM_COV", "DIM_TAM", "DISENO", "PRIOR", "simular", "cantidad_de"]


def prior_eta(gen: np.random.Generator, lote: int) -> np.ndarray:
    """η en espacio sin restricciones: (μ_k, log σ_k, μ_R, log σ_R, logit φ, log σ_y)."""
    p = PRIOR
    phi = np.clip(gen.beta(p["phi_a"], p["phi_b"], lote), 1e-4, 1 - 1e-4)
    return np.stack([
        p["mu_k_media"] + p["mu_k_desv"] * gen.standard_normal(lote),
        np.log(np.maximum(p["sigma_k_escala"] * np.abs(gen.standard_normal(lote)), 1e-3)),
        p["mu_R_media"] + p["mu_R_desv"] * gen.standard_normal(lote),
        np.log(np.maximum(p["sigma_R_escala"] * np.abs(gen.standard_normal(lote)), 1e-3)),
        np.log(phi / (1 - phi)),
        p["sigma_y_media"] + p["sigma_y_desv"] * gen.standard_normal(lote),
    ], axis=-1)


def disenar(gen: np.random.Generator, lote: int) -> dict:
    """El nivel de diseño. Líneas y celdas son comunes al lote (no se gasta relleno); lo demás cambia en cada dataset y línea."""
    lineas = int(gen.integers(DISENO["unidades"][0], DISENO["unidades"][1] + 1))
    celdas = int(gen.integers(DISENO["celdas"][0], DISENO["celdas"][1] + 1))
    c_min, c_max = DISENO["minutos_por_celda"]
    por_celda = np.exp(gen.uniform(np.log(c_min), np.log(c_max), lote))                  # (B,): minutos por celda de la planta
    t_final = celdas * por_celda
    propio = por_celda[:, None] * gen.uniform(0.85, 1.15, (lote, lineas))                # cada línea, su tiempo por celda
    t = np.minimum(propio[..., None] * np.arange(1, celdas + 1), t_final[:, None, None])  # (B, U, K)
    medidas = gen.integers(DISENO["lecturas"][0], celdas + 1, (lote, lineas))            # de 3 al total
    mascara = (np.arange(celdas) < medidas[..., None]).astype(np.float32)
    return {"t": t, "t_final": t_final, "mascara": mascara}


def simular(gen: np.random.Generator, lote: int) -> dict:
    d = disenar(gen, lote)
    t, mascara, t_final = d["t"], d["mascara"], d["t_final"]
    lineas = t.shape[1]
    eta = prior_eta(gen, lote)
    lam = np.stack([eta[:, None, 0] + np.exp(eta[:, None, 1]) * gen.standard_normal((lote, lineas)),
                    eta[:, None, 2] + np.exp(eta[:, None, 3]) * gen.standard_normal((lote, lineas))], axis=-1)
    limpio = recuperacion(t, lam[..., 0, None], lam[..., 1, None], eta[:, 4, None, None])
    y = limpio + np.exp(eta[:, 5])[:, None, None] * gen.standard_normal(t.shape)
    y = np.clip(y, 0.001, 0.999) * mascara                                               # como el analizador: entre 0 y 1
    x, cov, tam = preparar(t * mascara, y, mascara, t_final)
    return {"x": x, "mascara": mascara, "cov": cov, "tam": tam, "eta": eta.astype(np.float32), "lam": lam.astype(np.float32),
            "cantidad": final_de_linea(eta, lam, t_final[:, None]), "extra": {"t_final": t_final}, "t": t, "y": y}


def cantidad_de(eta: np.ndarray, lam: np.ndarray, extra: dict) -> np.ndarray:
    """La recuperación al final de la línea para muestras del posterior: eta (L, B, d), lam (L, B, U, 2) → (L, B, U)."""
    return final_de_linea(eta, lam, extra["t_final"][None, :, None])
