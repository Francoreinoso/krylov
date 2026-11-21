"""El paso local de `supervivencia`: contra la integración directa, sin depender del número de nodos, y calibrado con el θ verdadero."""
import math

import numpy as np

from motor.supervivencia import simular
from nucleo import casos, supervivencia as sv

CONFIG = simular.cargar_config()


def _theta(semilla, B):
    return sv.a_libre(simular.muestrear_prior(np.random.default_rng(semilla), B, CONFIG["prior"]))


def test_paso_local_igual_a_la_integracion_directa():
    """Un cargo con cinco personas: la cuadratura anidada contra una integral doble en grilla fina, escrita aparte."""
    rng = np.random.default_rng(1)
    libre = _theta(3, 1)
    libre[0, [sv.I_LOG_K, sv.I_LAMBDA, sv.I_LOG_SIGMA_U]] = [np.log(1.3), 0.8, np.log(0.6)]
    datos = {"x": rng.normal(size=(5, 3)), "w": rng.normal(size=5), "encuestas": rng.integers(1, 5, (5, 4)),
             "tiempo": np.array([3.0, 7.0, 0.0, 12.0, 1.0]), "evento": np.array([1.0, 0.0, np.nan, np.nan, 0.0]), "grupo": np.zeros(5, dtype=int)}
    p = sv.paso_local(libre, datos, nodos=40, nodos_persona=60)[:, 0]

    th = {k: v[0] for k, v in sv.a_restringido(libre).items()}
    u = np.linspace(-8, 8, 801)[:, None] * th["sigma_u"]
    z = np.linspace(-9, 9, 1201)[None, :]
    def s_c(c):
        return 1.0 if c == 0 else 0.5 * math.erfc((math.log(c) - th["mu_c"]) / th["s_c"] / math.sqrt(2))
    logistica = lambda v: 1 / (1 + np.exp(-v))                                         # noqa: E731
    m1, m0 = [], []                                                                    # M1_i(u), M0_i(u) de cada persona
    for i in range(5):
        t = datos["tiempo"][i]
        h = np.exp(th["beta0"] + datos["x"][i] @ th["beta"] + sv.base_spline(datos["w"][i]) @ th["gamma"] + u - th["lambda"] * z)
        peso = np.exp(-0.5 * z ** 2)
        for j in range(4):
            cortes = np.concatenate([[-np.inf], th["cortes"][j], [np.inf]])
            nivel = datos["encuestas"][i, j]
            peso = peso * (logistica(cortes[nivel] - th["a"][j] * z) - logistica(cortes[nivel - 1] - th["a"][j] * z))
        f1 = (np.exp(-h * t ** th["k"]) - np.exp(-h * (t + 1) ** th["k"])) * s_c(t + 0.5)
        f0 = np.exp(-h * (t + 0.5) ** th["k"]) * (s_c(t) - s_c(t + 1))
        m1.append((f1 * peso).sum(axis=1))
        m0.append((f0 * peso).sum(axis=1))
    m1, m0 = np.array(m1), np.array(m0)
    ver = np.where(datos["evento"][:, None] == 1, m1, np.where(datos["evento"][:, None] == 0, m0, m1 + m0))
    posterior_u = ver.prod(axis=0) * np.exp(-0.5 * (u[:, 0] / th["sigma_u"]) ** 2)
    directo = (m1 / (m1 + m0) * posterior_u).sum(axis=1) / posterior_u.sum()
    np.testing.assert_allclose(p[[2, 3]], directo[[2, 3]], rtol=1e-6)
    # Con los nodos del servicio la diferencia es chica.
    assert np.abs(sv.paso_local(libre, datos)[:, 0] - p)[[2, 3]].max() < 1e-3
    # La persona 3 lleva 12 años: saber que el cargo retiene (la persona 1 sigue tras 7 años, la 4 tras 1) no la deja igual que sin vecinos.
    sola = {k: v[[3]] for k, v in datos.items()}
    assert abs(sv.paso_local(libre, sola, nodos=40, nodos_persona=60)[0, 0] - p[3]) > 1e-4


def test_no_depende_del_numero_de_nodos_con_el_archivo_real():
    """Cargos de hasta 326 personas: el posterior de u es mucho más angosto que el prior, y la cuadratura adaptativa lo encuentra.

    Incluye muestras del prior que no se parecen en nada al archivo (el posterior del cargo queda a más de 10 σ_u de cero).
    """
    caso = casos.cargar_caso("rotacion")
    datos = sv.variables_del_modelo(sv.leer_tabla(casos.RAIZ / caso["dataset"], caso["columnas"]))
    libre = _theta(0, 32)[[0, 3, 8, 9, 20, 23, 29, 31]]
    por_decidir = np.isnan(datos["evento"])
    fino = sv.paso_local(libre, datos, nodos=20, nodos_persona=40)[por_decidir]
    servicio = sv.paso_local(libre, datos)[por_decidir]                                 # 8 nodos de cargo, 12 de persona
    assert np.isfinite(fino).all() and 0 <= servicio.min() and servicio.max() <= 1
    assert np.abs(servicio - fino).max() < 2e-3, np.abs(servicio - fino).max(axis=0)
    assert np.quantile(np.abs(servicio - fino), 0.999) < 1e-4


def test_con_el_theta_verdadero_las_probabilidades_calibran():
    """En empresas simuladas, de las personas por decidir a las que el paso local da p, renunció cerca de p."""
    lote = simular.simular(np.random.default_rng(5), 40, 800, CONFIG, simular.cargar_filas_reales(CONFIG))
    p = sv.paso_local_por_empresa(lote["theta"].astype(np.float64), sv.variables_del_modelo(lote))
    por_decidir = np.isnan(lote["evento"])
    p, renuncio = p[por_decidir], lote["delta"][por_decidir]
    assert abs(p.mean() - renuncio.mean()) < 0.01
    for bajo, alto in [(0, 0.05), (0.05, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 0.95), (0.95, 1.01)]:
        en = (p >= bajo) & (p < alto)
        error_tipico = np.sqrt((p[en] * (1 - p[en])).sum()) / en.sum()
        assert en.sum() > 200 and abs(renuncio[en].mean() - p[en].mean()) < 4 * error_tipico + 0.005, (bajo, alto)
    # Una empresa sola da lo mismo por los dos caminos.
    una = {k: np.asarray(v)[7] for k, v in sv.variables_del_modelo(lote).items()}
    np.testing.assert_allclose(sv.paso_local(lote["theta"][7:8].astype(np.float64), una)[:, 0],
                               sv.paso_local_por_empresa(lote["theta"].astype(np.float64), sv.variables_del_modelo(lote))[7], atol=1e-5)


def test_el_modo_de_la_cartera_da_lo_mismo_que_el_exacto():
    """rapido=True (Laplace en el cargo y cuadratura solo para las personas por decidir) contra el paso local completo.

    Con θ compatibles con los datos (aquí, el verdadero de cada empresa simulada) la diferencia típica es de milésimas.
    """
    lote = simular.simular(np.random.default_rng(11), 30, 600, CONFIG)
    variables, theta = sv.variables_del_modelo(lote), lote["theta"].astype(np.float64)
    por_decidir = np.isnan(lote["evento"])
    exacto = sv.paso_local_por_empresa(theta, variables, nodos=16, nodos_persona=30)
    rapido = sv.paso_local_por_empresa(theta, {**variables, "base_w": sv.base_spline(variables["w"])}, *sv.NODOS_CARTERA, rapido=True)
    assert np.isnan(rapido[~por_decidir]).all() and np.isfinite(rapido[por_decidir]).all()
    diferencia = np.abs(rapido - exacto)[por_decidir]
    # Medido: promedio 0,0009, percentil 99 0,011, máximo 0,041 (en una empresa con θ en la cola del prior).
    assert diferencia.max() < 0.06 and np.quantile(diferencia, 0.99) < 0.02 and diferencia.mean() < 2e-3, (diferencia.max(), diferencia.mean())
