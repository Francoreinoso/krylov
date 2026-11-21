"""Simulador del motor `desgaste`: flotas inventadas con el modelo de `WORKPLAN.md`, 11.4.

Tres niveles, en este orden: el **diseño** del dataset (cuántos camiones, cuántas muestras tiene cada uno y a qué horas
de operación, a intervalos irregulares), los parámetros globales η de la flota y los locales λ_i de cada camión: su
ritmo de desgaste ν_i y el desgaste que lleva hoy, X_i(hoy), que no se ve. El diseño se sortea en cada lote, dentro de
`nucleo.desgaste.DISENO`: la red no practica con un tamaño fijo.

**Los camiones del archivo siguen en servicio.** Un camión simulado cuyo desgaste ya cruzó 0,92 no estaría en el
archivo: se descarta entero (su ruta, sus horas, su ritmo y su trayectoria) y se sortea otro, con el mismo η. El
modelo es entonces el prior condicionado a «todavía no falla», y el MCMC de referencia tiene que condicionar en lo mismo.

Es la especificación que pide `motor/comun/series.py`.
"""

from __future__ import annotations

import numpy as np

from nucleo.desgaste import CANALES, DIM_COV, DIM_TAM, DISENO, EN_SERVICIO_BAJO, MOTOR_ID, NOMBRES_ETA, NOMBRES_LAM, PISO, PRIOR, margen, preparar

__all__ = ["MOTOR_ID", "NOMBRES_ETA", "NOMBRES_LAM", "CANALES", "DIM_COV", "DIM_TAM", "DISENO", "PRIOR", "simular", "cantidad_de"]

MAX_INTENTOS = 2000
MAX_FLOTAS = 20                        # veces que se vuelve a sortear el η de una flota que no puede estar en servicio


def prior_eta(gen: np.random.Generator, lote: int) -> np.ndarray:
    """η en espacio sin restricciones: (μ_ν, log σ_ν, β, log c, log σ_ε)."""
    p = PRIOR
    return np.stack([
        p["mu_nu_media"] + p["mu_nu_desv"] * gen.standard_normal(lote),
        np.log(np.maximum(p["sigma_nu_escala"] * np.abs(gen.standard_normal(lote)), 1e-3)),
        p["beta_media"] + p["beta_desv"] * gen.standard_normal(lote),
        p["c_media"] + p["c_desv"] * gen.standard_normal(lote),
        p["sigma_eps_media"] + p["sigma_eps_desv"] * gen.standard_normal(lote),
    ], axis=-1)


def _camiones(gen: np.random.Generator, eta: np.ndarray, muestras: np.ndarray, K: int) -> dict:
    """Un camión por fila de `eta` (n, d), con `muestras` (n,) lecturas cada uno: diseño, ritmo y trayectoria del proceso gamma."""
    n = len(eta)
    exigencia = gen.standard_normal(n)
    hoy = gen.uniform(*DISENO["miles_de_horas_hoy"], n)
    a_mantencion = gen.uniform(*DISENO["miles_de_horas_a_mantencion"], n)
    # Tiempos irregulares: muestras − 1 instantes al azar en (0, hoy), ordenados, y la última muestra es hoy.
    u = gen.random((n, K))
    u[np.arange(K) >= (muestras - 1)[:, None]] = np.inf
    t = np.sort(u, axis=-1) * hoy[:, None]
    t[np.arange(n), muestras - 1] = hoy
    mascara = np.arange(K) < muestras[:, None]
    t = np.where(mascara, t, 0.0)
    log_nu = eta[:, 0] + eta[:, 2] * exigencia + np.exp(eta[:, 1]) * gen.standard_normal(n)
    c2 = np.exp(2 * eta[:, 3])[:, None]
    dt = np.diff(t, axis=-1, prepend=0.0) * mascara
    saltos = gen.gamma(np.maximum(np.exp(log_nu)[:, None] * dt / c2, 1e-12)) * c2 * mascara
    X = np.cumsum(saltos, axis=-1)
    return {"exigencia": exigencia, "a_mantencion": a_mantencion, "t": t, "mascara": mascara.astype(np.float32),
            "log_nu": log_nu, "X": X, "X_hoy": X[:, -1]}


def simular(gen: np.random.Generator, lote: int) -> dict:
    u_min, u_max = DISENO["unidades"]
    camiones = int(min(u_max, np.floor(np.exp(gen.uniform(np.log(u_min), np.log(u_max + 1))))))      # común al lote
    muestras = gen.integers(DISENO["lecturas"][0], DISENO["lecturas"][1] + 1, (lote, camiones)).ravel()
    K = int(muestras.max())
    eta = prior_eta(gen, lote)
    eta_c = np.repeat(eta, camiones, axis=0)                                           # (B·M, d): el η de cada camión
    c = _camiones(gen, eta_c, muestras, K)
    for _ in range(MAX_FLOTAS):
        for _ in range(MAX_INTENTOS):                                                   # los que ya fallaron se sortean de nuevo
            fuera = np.flatnonzero(c["X_hoy"] >= EN_SERVICIO_BAJO)
            if len(fuera) == 0:
                break
            nuevo = _camiones(gen, eta_c[fuera], muestras[fuera], K)
            for k in c:
                c[k][fuera] = nuevo[k]
        else:
            # Un η de la cola del prior (desgaste tan rápido que casi ningún camión seguiría en servicio: menos de
            # 1 en MAX_INTENTOS) no produce un archivo posible. Esa flota se sortea entera, con otro η.
            flotas = np.unique(fuera // camiones)
            eta[flotas] = prior_eta(gen, len(flotas))
            de_la_flota = (flotas[:, None] * camiones + np.arange(camiones)).ravel()
            eta_c[de_la_flota] = np.repeat(eta[flotas], camiones, axis=0)
            nuevo = _camiones(gen, eta_c[de_la_flota], muestras[de_la_flota], K)
            for k in c:
                c[k][de_la_flota] = nuevo[k]
            continue
        break
    else:
        raise RuntimeError("desgaste: quedaron camiones sin trayectoria en servicio")
    forma = (lote, camiones)
    t, mascara, X = (c[k].reshape(forma + (K,)) for k in ("t", "mascara", "X"))
    exigencia, a_mantencion = c["exigencia"].reshape(forma), c["a_mantencion"].reshape(forma)
    y = (X + np.exp(eta[:, 4])[:, None, None] * gen.standard_normal(X.shape)) * mascara
    x, cov, tam = preparar(t, y, mascara, exigencia, a_mantencion)
    lam = np.stack([c["log_nu"], np.log(c["X_hoy"] + PISO)], axis=-1).reshape(forma + (2,))
    return {"x": x, "mascara": mascara, "cov": cov, "tam": tam, "eta": eta.astype(np.float32), "lam": lam.astype(np.float32),
            "cantidad": margen(eta, lam, a_mantencion), "extra": {"a_mantencion": a_mantencion},
            "t": t, "y": y, "exigencia": exigencia}


def cantidad_de(eta: np.ndarray, lam: np.ndarray, extra: dict) -> np.ndarray:
    """Lo que se decide, en su versión continua, para muestras del posterior: eta (L, B, d), lam (L, B, M, 2) → (L, B, M)."""
    return margen(eta, lam, extra["a_mantencion"][None])
