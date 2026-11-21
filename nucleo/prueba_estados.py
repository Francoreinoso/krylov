"""`estados`: el filtro forward coincide con la enumeración directa de las cadenas, en un caso chico."""

import itertools

import numpy as np

from nucleo import estados


def _datos_y_theta(rng, n=4):
    libre = rng.normal(0, 0.6, estados.DIM_THETA)
    libre[13], libre[30] = -2.0, -2.0                         # primer corte y logit de d_1 en valores razonables
    datos = {"nivel": rng.integers(0, estados.NIVELES, (n, estados.MESES)), "uso": rng.normal(0.4, 0.3, (n, estados.MESES)),
             "pago_cero": rng.random((n, estados.MESES)) < 0.25, "log_pago": rng.normal(-3.8, 1.2, (n, estados.MESES)),
             "x": rng.normal(0, 1, (n, 3))}
    return libre, datos


def test_restricciones():
    rng = np.random.default_rng(0)
    th = estados.a_restringido(rng.normal(0, 1, (50, estados.DIM_THETA)))
    assert estados.DIM_THETA == 33 and estados.DIM_FILA == 56
    np.testing.assert_allclose(th["pi"].sum(-1), 1)
    assert (np.diff(th["d"], axis=-1) > 0).all() and (np.diff(th["posicion"], axis=-1) > 0).all() and (th["posicion"][:, 0] == 0).all()
    assert (np.diff(th["cortes"], axis=-1) > 0).all() and (th["A"][:, [0, 1, 2], [0, 1, 2]] == 0).all()
    paso = estados.transiciones(th, rng.normal(0, 1, (7, 3)))
    assert paso.shape == (50, 7, 3, 3)
    np.testing.assert_allclose(paso.sum(-1), 1)


def test_filtro_forward_igual_a_la_enumeracion():
    """Suma directa sobre las 3^7 cadenas posibles de cada cliente, contra el filtro."""
    rng = np.random.default_rng(1)
    libre, datos = _datos_y_theta(rng)
    log_ver, estado_7, p = estados.filtro_forward(libre, datos)

    th = estados.a_restringido(libre)
    emision = np.exp(estados.log_emision(th, datos["nivel"], datos["uso"], datos["pago_cero"], datos["log_pago"]))   # (n, 6, 3)
    paso = estados.transiciones(th, datos["x"])                                                                       # (n, 3, 3)
    for i in range(len(p)):
        conjunta = np.zeros(3)                       # P(historial, s_7 = k), sumando sobre s_1..s_6
        for cadena in itertools.product(range(3), repeat=7):
            prob = th["pi"][cadena[0]] * emision[i, 0, cadena[0]]
            for t in range(1, 7):
                prob *= paso[i, cadena[t - 1], cadena[t]] * (emision[i, t, cadena[t]] if t < 6 else 1.0)
            conjunta[cadena[6]] += prob
        np.testing.assert_allclose(log_ver[i], np.log(conjunta.sum()), rtol=1e-10)
        np.testing.assert_allclose(estado_7[i], conjunta / conjunta.sum(), rtol=1e-10)
        np.testing.assert_allclose(p[i], (conjunta / conjunta.sum()) @ th["d"], rtol=1e-10)


def test_emision_normalizada_y_muestras_p():
    rng = np.random.default_rng(2)
    libre, datos = _datos_y_theta(rng, n=30)
    th = estados.a_restringido(libre)
    # El logit ordenado reparte probabilidad 1 entre los cinco niveles, en cada estado.
    uno = {"uso": np.zeros((5, 1)), "pago_cero": np.ones((5, 1), dtype=bool), "log_pago": np.zeros((5, 1))}
    por_nivel = np.exp(estados.log_emision(th, np.arange(5)[:, None], **uno) - estados.log_emision(th, np.zeros((5, 1), int), **uno)
                       + estados.log_emision(th, np.zeros((5, 1), int), **uno))
    resto = np.exp(estados.log_emision(th, np.zeros((1, 1), int), uno["uso"][:1], uno["pago_cero"][:1], uno["log_pago"][:1]))
    primer_nivel = estados._logistica(th["cortes"][0] - th["posicion"])
    np.testing.assert_allclose((por_nivel / (resto / primer_nivel)).sum(0)[0], 1, rtol=1e-9)

    muestras = estados.probabilidad_de_impago(rng.normal(0, 0.5, (32, estados.DIM_THETA)), datos)
    assert muestras.shape == (30, 32) and (muestras > 0).all() and (muestras < 1).all()
    impago = np.where(rng.random(30) < 0.2, np.nan, (rng.random(30) < 0.2).astype(float))
    total = estados.log_verosimilitud(rng.normal(0, 0.5, (4, estados.DIM_THETA)), datos, impago)
    assert total.shape == (4,) and np.isfinite(total).all()
    filas = estados.armar_filas(datos["nivel"], datos["uso"], datos["pago_cero"], datos["log_pago"], datos["x"], impago)
    assert filas.shape == (30, estados.DIM_FILA) and filas.dtype == np.float32
    assert (filas[:, :30].reshape(30, 6, 5).sum(-1) == 1).all() and (filas[np.isnan(impago), -2:] == [0, 1]).all()
