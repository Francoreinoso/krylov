"""Motor `espacial` en el servicio: el paso local exacto (kriging dado θ) y la respuesta del terreno.

Modelo (WORKPLAN.md, 11.5), en las unidades estandarizadas de `nucleo.preproceso`:

    y(s) = β0 + β1·√dist(s) + w(s),   w ~ proceso gaussiano de media 0 y covarianza σ²·exp(−h)
    z_j  = y(s_j) + ε_j,              ε_j ~ Normal(0, τ²)

con h la distancia anisotrópica entre bloques. θ = (log a, e1, e2, log σ, log τ, β0, β1),
donde e = log r·(cos 2φ, sin 2φ) junta la razón de anisotropía r y la dirección φ, y el
alcance es a·√r a lo largo de φ y a/√r en la perpendicular (en bloques).

**Kriging dado θ.** Con θ fijo, el predictivo de y(s) dadas las mediciones es gaussiano y
tiene forma cerrada. El posterior de θ llega como muestras (del flujo o del MCMC de
referencia) y el predictivo del mapa es la mezcla de esos gaussianos, bloque por bloque.

Solo NumPy: este módulo corre en el servidor.
"""

from __future__ import annotations

import math

import numpy as np

NOMBRES_THETA = ("log_alcance", "anis_1", "anis_2", "log_sigma", "log_tau", "beta0", "beta1")


def metrica_anisotropica(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Coeficientes (m11, m12, m22) de h² = m11·dx² + 2·m12·dx·dy + m22·dy² (dx en columnas, dy en filas).

    Es R(φ)·diag(1/(a²r), r/a²)·R(φ)ᵀ escrito con e: M = [cosh ρ·I − (sinh ρ/ρ)·(e1·σz + e2·σx)] / a², ρ = |e|.
    La misma fórmula que `motor.espacial.simular.metrica_anisotropica`; una prueba las compara.
    """
    theta = np.asarray(theta, dtype=np.float64)
    a2 = np.exp(2 * theta[..., 0])
    e1, e2 = theta[..., 1], theta[..., 2]
    rho = np.maximum(np.sqrt(e1 ** 2 + e2 ** 2), 1e-6)
    cosh, sinhc = np.cosh(rho), np.sinh(rho) / rho
    return (cosh - sinhc * e1) / a2, (-sinhc * e2) / a2, (cosh + sinhc * e1) / a2


def correlacion(theta: np.ndarray, d_fila: np.ndarray, d_columna: np.ndarray) -> np.ndarray:
    """exp(−h) para desfases (d_fila, d_columna) en bloques. theta: (S, 7) → (S, *desfases)."""
    extra = (slice(None),) + (None,) * np.ndim(d_fila)
    m11, m12, m22 = (m[extra] for m in metrica_anisotropica(np.atleast_2d(theta)))
    h2 = m11 * d_columna ** 2 + 2 * m12 * d_columna * d_fila + m22 * d_fila ** 2
    return np.exp(-np.sqrt(np.maximum(h2, 0.0)))


def kriging(theta, fila_obs, columna_obs, z_obs, raiz_obs, fila_pred, columna_pred, raiz_pred, cuenta_obs=None):
    """Predictivo gaussiano de y en `pred` dadas las mediciones `obs`, para cada muestra de θ.

    theta: (S, 7). Las posiciones son (fila, columna) en bloques; `raiz_*` es √dist ahí.
    `cuenta_obs`: mediciones promediadas en cada bloque medido (su ruido es τ²/cuenta); por defecto 1.
    Devuelve (media, varianza), cada una (S, n_pred). Es el kriging con tendencia conocida:
        media    = t_pred + K_po·(K_oo + τ²/c)⁻¹·(z − t_obs)
        varianza = σ² − diag(K_po·(K_oo + τ²/c)⁻¹·K_op)
    """
    theta = np.atleast_2d(np.asarray(theta, dtype=np.float64))
    fila_obs, columna_obs = np.asarray(fila_obs, dtype=np.float64), np.asarray(columna_obs, dtype=np.float64)
    fila_pred, columna_pred = np.asarray(fila_pred, dtype=np.float64), np.asarray(columna_pred, dtype=np.float64)
    sigma2, tau2 = np.exp(2 * theta[:, 3])[:, None, None], np.exp(2 * theta[:, 4])[:, None]
    beta0, beta1 = theta[:, 5, None], theta[:, 6, None]
    cuenta = np.ones(len(fila_obs)) if cuenta_obs is None else np.asarray(cuenta_obs, dtype=np.float64)

    k_oo = sigma2 * correlacion(theta, fila_obs[:, None] - fila_obs[None, :], columna_obs[:, None] - columna_obs[None, :])
    k_oo = k_oo + (tau2 / cuenta)[:, :, None] * np.eye(len(fila_obs))
    k_po = sigma2 * correlacion(theta, fila_pred[:, None] - fila_obs[None, :], columna_pred[:, None] - columna_obs[None, :])
    residuo = np.asarray(z_obs, dtype=np.float64)[None, :] - (beta0 + beta1 * np.asarray(raiz_obs)[None, :])
    pesos = np.linalg.solve(k_oo, np.swapaxes(k_po, 1, 2))                     # (S, n_obs, n_pred)
    media = beta0 + beta1 * np.asarray(raiz_pred)[None, :] + np.einsum("so,sop->sp", residuo, pesos)
    varianza = sigma2[:, 0] - np.einsum("spo,sop->sp", k_po, pesos)
    return media, np.maximum(varianza, 1e-12)


def _normal_acumulada(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


def mezclar(media: np.ndarray, varianza: np.ndarray, umbral: float) -> dict[str, np.ndarray]:
    """Mezcla sobre las muestras de θ: media y desviación del predictivo, y P(y > umbral), por bloque."""
    media_total = media.mean(axis=0)
    desviacion = np.sqrt(varianza.mean(axis=0) + media.var(axis=0))
    p = _normal_acumulada((media - umbral) / np.sqrt(varianza)).mean(axis=0)
    return {"media": media_total, "desviacion": desviacion, "p": p}
