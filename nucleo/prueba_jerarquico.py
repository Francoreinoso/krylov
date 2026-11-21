"""`jerarquico`: la matriz de diseño, la forma anidada y el paso local contra la integración directa."""

import numpy as np

from nucleo import jerarquico as jq


def _logistica(x):
    return 1 / (1 + np.exp(-x))


def test_spline_y_matriz_de_diseno():
    t = np.linspace(0, jq.T_MAXIMO, 50)
    base = jq.base_spline(t)
    np.testing.assert_allclose(base.sum(-1), 1)
    assert base[0, 0] == 1 and (base[0, 1:] == 0).all()                    # en t = 0 solo vive la primera función: f(0) = 0
    z = jq.matriz_de_diseno([0, 5, 30], [0, 2, 4], [0, 1, 1], [38, 61, 15], [[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0]])
    assert z.shape == (3, jq.DIM_COEF) and jq.DIM_THETA == 20 and jq.DIM_FILA == 19
    assert (z[0, 1:6] == 0).all() and z[0, 6] == 1 and (z[0, 7:11] == 0).all()   # mismo día, lunes
    assert z[1, 8] == 1 and z[1, 11] == 1 and abs(z[1, 12] - (np.log(6) - 2.5)) < 1e-12 and abs(z[1, 13] - 1.0) < 1e-12
    th = jq.a_restringido(np.arange(20.0) / 10)
    np.testing.assert_allclose(th["coef"][1:6], np.cumsum(np.arange(1, 6) / 10))
    filas = jq.armar_filas(z, [1.0, np.nan, 0.0])
    assert filas.shape == (3, 19) and (filas[1, -2:] == [0, 1]).all() and (filas[0, -2:] == [1, 0]).all()


def test_anidar_conserva_cada_fila():
    rng = np.random.default_rng(0)
    paciente = rng.integers(0, 40, 150)
    barrio = paciente % 6                                                  # cada paciente en un solo barrio
    filas = rng.normal(0, 1, (150, 5)).astype(np.float32)
    tensor, mascara, posicion = jq.anidar(filas, barrio, paciente)
    assert tensor.shape[0] == 6 and mascara.sum() == 150
    np.testing.assert_array_equal(tensor[tuple(posicion.T)], filas)
    for i, j in ((0, 1), (10, 77)):                                        # mismo paciente ⇔ mismo (barrio, paciente) anidado
        assert (paciente[i] == paciente[j]) == (tuple(posicion[i, :2]) == tuple(posicion[j, :2]))


def test_paso_local_igual_a_la_integracion_directa():
    """Un barrio con dos pacientes: la cuadratura anidada contra una integral doble en grilla fina."""
    rng = np.random.default_rng(1)
    libre = rng.normal(0, 0.4, (1, jq.DIM_THETA))
    libre[0, 18:] = [np.log(1.2), np.log(0.6)]
    paciente = np.array([0, 0, 0, 1, 1])
    respuesta = np.array([1.0, 0.0, np.nan, 1.0, np.nan])
    z = jq.matriz_de_diseno(rng.integers(0, 40, 5), rng.integers(0, 5, 5), [0, 1, 0, 1, 0], rng.integers(1, 80, 5), rng.integers(0, 2, (5, 4)))
    p = jq.paso_local(libre, z, respuesta, paciente, np.array([0, 0]), nodos=40)[:, 0]

    th = jq.a_restringido(libre[0])
    eta = z @ th["coef"]
    u = np.linspace(-6, 6, 1201) * th["sigma_b"]
    v = np.linspace(-7, 7, 1401) * th["sigma_v"]
    dens_u, dens_v = np.exp(-0.5 * (u / th["sigma_b"]) ** 2), np.exp(-0.5 * (v / th["sigma_v"]) ** 2)
    def ver(cita):                                                          # p(respuesta de la cita | u, v), (U, V)
        q = _logistica(eta[cita] + u[:, None] + v[None, :])
        return q if respuesta[cita] == 1 else 1 - q
    l0 = (ver(0) * ver(1) * dens_v).sum(1)                                  # paciente 0: L_0(u)
    l1 = (ver(3) * dens_v).sum(1)                                           # paciente 1: L_1(u)
    posterior_u = l0 * l1 * dens_u
    directo_2 = ((_logistica(eta[2] + u[:, None] + v[None, :]) * ver(0) * ver(1) * dens_v).sum(1) / l0 * posterior_u).sum() / posterior_u.sum()
    directo_4 = ((_logistica(eta[4] + u[:, None] + v[None, :]) * ver(3) * dens_v).sum(1) / l1 * posterior_u).sum() / posterior_u.sum()
    np.testing.assert_allclose([p[2], p[4]], [directo_2, directo_4], rtol=1e-6)
    # Con 12 nodos (los del servicio) la diferencia es chica.
    p12 = jq.paso_local(libre, z, respuesta, paciente, np.array([0, 0]), nodos=12)[:, 0]
    assert np.abs(p12 - p)[[2, 4]].max() < 2e-3
    # El paciente 0 ya faltó una vez y fue otra; el 1 solo faltó: su cita por decidir sube respecto de no saber nada.
    sin_historia = jq.paso_local(libre, z, np.full(5, np.nan), paciente, np.array([0, 0]), nodos=40)[:, 0]
    assert p[4] > sin_historia[4]
