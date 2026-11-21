"""El método rápido de siempre: la regresión logística en NumPy recupera coeficientes conocidos y su intervalo cubre."""

import numpy as np

from motor.comun import rapido


def _datos(rng, n, beta, intercepto=-1.0):
    x = rng.standard_normal((n, len(beta))) * np.array([1.0, 3.0, 0.2])[: len(beta)] + 5.0
    p = 1 / (1 + np.exp(-(intercepto + ((x - 5.0) @ beta))))
    return x, (rng.random(n) < p).astype(float), p


def test_recupera_los_coeficientes_y_la_probabilidad():
    rng = np.random.default_rng(0)
    beta = np.array([0.8, -0.3, 2.0])
    x, y, p_real = _datos(rng, 20_000, beta)
    modelo = rapido.ajustar(x, y)
    en_escala_original = modelo["beta"][1:] / modelo["escala"]
    assert np.abs(en_escala_original - beta).max() < 0.15, en_escala_original
    p, bajo, alto = rapido.predecir(modelo, x)
    assert np.abs(p - p_real).max() < 0.04 and (bajo <= p).all() and (p <= alto).all()


def test_el_intervalo_de_wald_cubre_cerca_de_90_cuando_el_modelo_es_el_correcto():
    rng = np.random.default_rng(1)
    dentro = []
    for _ in range(40):
        x, y, p_real = _datos(rng, 600, np.array([0.8, -0.3, 2.0]))
        _, bajo, alto = rapido.predecir(rapido.ajustar(x, y), x)
        dentro.append(((p_real >= bajo) & (p_real <= alto)).mean())
    assert 0.84 < np.mean(dentro) < 0.96, np.mean(dentro)


def test_filas_del_codificador_columna_constante_y_separacion_perfecta():
    rng = np.random.default_rng(2)
    x, y, _ = _datos(rng, 400, np.array([1.0, 0.0, 0.0]))
    y[:80] = np.nan                                                               # 80 filas por decidir
    filas = np.c_[x, np.ones(400), np.nan_to_num(y), np.isnan(y).astype(float)]   # una columna constante de más
    p, bajo, alto = rapido.ajustar_y_predecir(filas)
    assert p.shape == (80,) and np.isfinite(p).all() and (bajo <= alto).all()
    # Una columna que separa perfecto no revienta el ajuste: el ridge lo mantiene finito.
    y2 = (x[:, 0] > 5.0).astype(float)
    modelo = rapido.ajustar(x[:, :1], y2)
    assert np.isfinite(modelo["beta"]).all() and rapido.metricas(rapido.predecir(modelo, x[:, :1])[0], y2)["auc"] > 0.99


def test_metricas():
    y = np.array([1.0, 0.0, 1.0, 0.0])
    m = rapido.metricas(np.array([0.9, 0.1, 0.8, 0.3]), y)
    assert m["auc"] == 1.0 and m["brier"] < m["brier_tasa_base"] == 0.25
    assert rapido.metricas(1 - np.array([0.9, 0.1, 0.8, 0.3]), y)["auc"] == 0.0
