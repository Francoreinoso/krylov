"""La cobertura por rangos es exacta con un posterior perfecto, y el umbral del SBC se corrige por el número de parámetros."""

import numpy as np

from motor.comun import validacion


def test_cobertura_por_rangos_es_exacta_y_los_cuantiles_no():
    # Con 99 muestras hay 100 rangos igual de probables: de 5 a 94 son exactamente 90.
    assert validacion.dentro_del_rango(np.arange(100), 99).sum() == 90
    assert validacion.dentro_del_rango(np.arange(40), 39).sum() == 36
    # Posterior perfecto: verdad y muestras salen de la misma normal.
    rng = np.random.default_rng(0)
    verdad, muestras = rng.standard_normal(20_000), rng.standard_normal((99, 20_000))
    por_rangos = validacion.dentro_del_rango((muestras < verdad).sum(axis=0), 99).mean()
    bajo, alto = np.quantile(muestras, [0.05, 0.95], axis=0)
    por_cuantiles = ((verdad >= bajo) & (verdad <= alto)).mean()
    assert abs(por_rangos - 0.90) < 0.008 and abs(por_cuantiles - 0.882) < 0.008


def test_umbral_del_sbc_y_comparacion_de_posteriores():
    assert abs(validacion.umbral_chi2(1) - 21.67) < 0.01 and validacion.umbral_chi2(33) > validacion.umbral_chi2(7) > 21.67
    bien = {"a": {"chi2_uniformidad": 12.0, "rango_medio": 0.51}, "b": {"chi2_uniformidad": 22.0, "rango_medio": 0.49}}
    assert validacion.sbc_sin_sesgo(bien) == (True, [])
    assert validacion.sbc_sin_sesgo({**bien, "c": {"chi2_uniformidad": 9.0, "rango_medio": 0.56}}) == (False, ["c"])
    rng = np.random.default_rng(1)
    referencia = rng.standard_normal((4000, 3))
    diferencia, razon = validacion.comparar_posteriores(referencia[:2000] * [1, 2, 1] + [0, 0, 0.5], referencia[2000:])
    assert diferencia[0] < 0.1 and abs(diferencia[2] - 0.5) < 0.1 and abs(razon[1] - 2) < 0.15
