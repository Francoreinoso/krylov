"""Pruebas del simulador de `supervivencia` y de su preprocesamiento (solo NumPy)."""
import numpy as np

from motor.supervivencia import simular
from nucleo import supervivencia as nucleo_sv

CONFIG = simular.cargar_config()


def _lote(B=8, n=300, semilla=0, reales=None):
    return simular.simular(np.random.default_rng(semilla), B, n, CONFIG, reales)


def test_formas_y_valores():
    lote = _lote()
    assert lote["filas"].shape == (8, 300, nucleo_sv.DIM_FILA) and lote["filas"].dtype == np.float32
    assert lote["theta"].shape == (8, nucleo_sv.DIM_THETA) and lote["grupo"].shape == (8, 300)
    assert np.isfinite(lote["filas"]).all() and np.isfinite(lote["theta"]).all()
    assert lote["grupo"].min() >= 0 and lote["grupo"].max() < simular.CARGOS_MAX
    assert set(np.unique(lote["encuestas"])) <= {1, 2, 3, 4}
    assert (lote["tiempo"] >= 0).all() and (lote["tiempo"] == np.floor(lote["tiempo"])).all()
    # δ borrado exactamente en el 20%, y en esas filas la red ve δ = 0 con la marca en 1.
    por_decidir = np.isnan(lote["evento"])
    assert (por_decidir.sum(axis=1) == 60).all()
    assert (lote["filas"][..., 9][por_decidir] == 0).all() and (lote["filas"][..., 10] == por_decidir).all()


def test_un_solo_preprocesamiento():
    """El simulador y el servicio pasan por la misma función: mismas columnas crudas, mismas filas."""
    lote = _lote()
    por_el_servicio = np.stack([
        nucleo_sv.preprocesar(lote["efectos"][b], lote["sueldo"][b], lote["encuestas"][b],
                              lote["tiempo"][b], lote["evento"][b])
        for b in range(8)
    ])
    np.testing.assert_array_equal(por_el_servicio, lote["filas"])


def test_theta_libre_ida_y_vuelta():
    th = simular.muestrear_prior(np.random.default_rng(1), 64, CONFIG["prior"])
    vuelta = nucleo_sv.a_restringido(nucleo_sv.a_libre(th))
    for nombre, valor in th.items():
        np.testing.assert_allclose(vuelta[nombre], valor, rtol=1e-9, atol=1e-12)
    assert (np.diff(th["cortes"], axis=-1) > 0).all() and len(nucleo_sv.NOMBRES_THETA) == nucleo_sv.DIM_THETA


def test_base_spline_suma_uno():
    base = nucleo_sv.base_spline(np.linspace(-4, 4, 201))
    assert base.shape == (201, nucleo_sv.N_SPLINE) and (base >= 0).all()
    np.testing.assert_allclose(base.sum(axis=-1), 1.0, atol=1e-12)


def test_semilla_fija_y_remuestreo_del_archivo_del_caso():
    reales = simular.cargar_filas_reales(CONFIG)
    assert reales is not None, "falta el archivo del caso (datos/demo/rotacion.csv)"
    a, b = _lote(semilla=3, reales=reales), _lote(semilla=3, reales=reales)
    np.testing.assert_array_equal(a["filas"], b["filas"])
    np.testing.assert_array_equal(a["theta"], b["theta"])


def test_el_evento_sigue_al_modelo():
    """Con θ conocido: más riesgo lineal η, más renuncias (el signo del modelo está bien puesto)."""
    lote = _lote(B=200, n=400, semilla=5)
    eta_c = lote["eta"] - lote["eta"].mean(axis=1, keepdims=True)
    alto, bajo = lote["delta"][eta_c > 0.5].mean(), lote["delta"][eta_c < -0.5].mean()
    assert alto > bajo + 0.05
