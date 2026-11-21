"""Kriging dado θ: coincide con el cálculo directo en una grilla chica."""

import math

import numpy as np

from nucleo import espacial


def _theta(log_a, phi, r, sigma, tau, beta0, beta1):
    rho = math.log(r)
    return np.array([[log_a, rho * math.cos(2 * phi), rho * math.sin(2 * phi), math.log(sigma), math.log(tau), beta0, beta1]])


def _correlacion_directa(log_a, phi, r, d_fila, d_columna):
    """exp(−h) con la definición del modelo escrita aparte: rotar a los ejes del campo y escalar."""
    a = math.exp(log_a)
    u = d_columna * math.cos(phi) + d_fila * math.sin(phi)
    v = -d_columna * math.sin(phi) + d_fila * math.cos(phi)
    return np.exp(-np.sqrt((u / (a * math.sqrt(r))) ** 2 + (v * math.sqrt(r) / a) ** 2))


def test_correlacion_igual_a_la_definicion():
    d = np.arange(-5, 6.0)
    d_fila, d_columna = np.meshgrid(d, d, indexing="ij")
    for log_a, phi, r in [(math.log(4.0), 0.5, 2.0), (math.log(2.0), 2.4, 1.0), (math.log(9.0), 1.3, 4.0)]:
        np.testing.assert_allclose(espacial.correlacion(_theta(log_a, phi, r, 1, 1, 0, 0), d_fila, d_columna)[0],
                                   _correlacion_directa(log_a, phi, r, d_fila, d_columna), rtol=1e-9, atol=1e-12)


def test_kriging_coincide_con_el_condicional_directo():
    """Grilla de 6 × 6: la fórmula de kriging contra condicionar la gaussiana conjunta completa."""
    rng = np.random.default_rng(0)
    log_a, phi, r, sigma, tau, beta0, beta1 = math.log(3.0), 0.7, 2.0, 1.3, 0.4, 0.5, -2.0
    fila, columna = (m.reshape(-1).astype(float) for m in np.meshgrid(np.arange(6), np.arange(6), indexing="ij"))
    raiz = rng.random(36)
    medidos = rng.choice(36, 12, replace=False)
    cuenta = rng.integers(1, 3, 12).astype(float)
    z = rng.normal(0, 1, 12)

    media, varianza = espacial.kriging(_theta(log_a, phi, r, sigma, tau, beta0, beta1), fila[medidos], columna[medidos], z,
                                       raiz[medidos], fila, columna, raiz, cuenta)

    # Directo: gaussiana conjunta de (y en los 36 bloques, z en los 12 medidos) y su condicional.
    k = sigma ** 2 * _correlacion_directa(log_a, phi, r, fila[:, None] - fila[None, :], columna[:, None] - columna[None, :])
    conjunta = np.block([[k, k[:, medidos]], [k[medidos, :], k[np.ix_(medidos, medidos)] + np.diag(tau ** 2 / cuenta)]])
    tendencia = beta0 + beta1 * raiz
    inversa = np.linalg.inv(conjunta[36:, 36:])
    media_directa = tendencia + conjunta[:36, 36:] @ inversa @ (z - tendencia[medidos])
    varianza_directa = np.diag(conjunta[:36, :36] - conjunta[:36, 36:] @ inversa @ conjunta[36:, :36])
    np.testing.assert_allclose(media[0], media_directa, rtol=1e-8, atol=1e-10)
    np.testing.assert_allclose(varianza[0], varianza_directa, rtol=1e-8, atol=1e-10)
    # En un bloque medido con poco ruido la varianza cae; lejos de todo vuelve a σ².
    assert varianza[0][medidos].max() < sigma ** 2 and varianza[0].max() <= sigma ** 2 + 1e-9


def test_varias_muestras_y_mezcla():
    rng = np.random.default_rng(1)
    theta = np.concatenate([_theta(math.log(a), 0.3, 1.5, 1.0, 0.3, 0.0, -1.0) for a in (2.0, 4.0, 8.0)])
    fila, columna = (m.reshape(-1).astype(float) for m in np.meshgrid(np.arange(8), np.arange(8), indexing="ij"))
    raiz, medidos = rng.random(64), rng.choice(64, 20, replace=False)
    media, varianza = espacial.kriging(theta, fila[medidos], columna[medidos], rng.normal(0, 1, 20), raiz[medidos], fila, columna, raiz)
    assert media.shape == varianza.shape == (3, 64)
    mezcla = espacial.mezclar(media, varianza, umbral=0.5)
    assert mezcla["p"].shape == (64,) and (mezcla["p"] >= 0).all() and (mezcla["p"] <= 1).all()
    assert (mezcla["desviacion"] ** 2 >= varianza.mean(0) - 1e-12).all()      # la mezcla suma la dispersión entre muestras


def test_misma_metrica_que_el_simulador():
    import pytest
    torch = pytest.importorskip("torch")
    from motor.espacial import simular
    assert simular.NOMBRES_THETA == espacial.NOMBRES_THETA
    theta = simular.muestrear_prior(50, simular.Prior(), torch.Generator().manual_seed(0))
    for del_simulador, del_nucleo in zip(simular.metrica_anisotropica(theta), espacial.metrica_anisotropica(theta.numpy())):
        np.testing.assert_allclose(del_nucleo, del_simulador.numpy(), rtol=1e-4)


def test_examen_de_bloques_cuenta_todos_los_bloques(monkeypatch):
    """El examen con la verdad escondida de `leyes` reparte los mismos bloques, por color, que la respuesta."""
    from nucleo import api, espacial
    from nucleo.casos import cargar_caso, costos_numericos
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    caso = cargar_caso("leyes")
    examen = espacial.examen_de_bloques(caso, costos_numericos(caso, None))
    colores = api.analizar("leyes")["resumen_colores"]
    assert {e: v["bloques"] for e, v in examen["colores"].items()} == colores
    assert all(0 <= v["sobre_el_limite"] <= v["bloques"] for v in examen["colores"].values()) and sum(t["n"] for t in examen["tramos"]) == examen["n"]
