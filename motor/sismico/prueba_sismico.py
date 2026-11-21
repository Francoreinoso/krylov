"""`sismico`: el simulador respeta su diseño, usa el preprocesamiento del servicio, la forma cerrada coincide con simular
hacia adelante y el archivo del demo cae dentro de lo simulado."""

import numpy as np

from motor.sismico import simular as s
from nucleo import series, sismico
from nucleo.casos import cargar_caso


def test_el_diseno_sortea_tamanos_dentro_del_rango():
    gen = np.random.default_rng(0)
    sectores, ventanas, sismos = set(), [], []
    for _ in range(150):
        sim = s.simular(gen, 4)
        e = sim["extra"]
        sectores.add(e["mascara"].shape[1]); ventanas.extend(e["T"]); sismos.extend(e["mascara"].sum(-1).ravel())
        assert all(np.isfinite(sim[k]).all() for k in ("x", "cov", "tam", "eta", "lam", "cantidad"))
        assert (sim["mascara"][..., 0] == 1).all() and sim["mascara"].shape[2] == e["mascara"].shape[2] + 1     # la tronadura, siempre
        assert (np.diff(e["t"], axis=-1)[e["mascara"][..., 1:] > 0] >= 0).all() and (e["t"] <= e["T"][:, None, None]).all()
    d = sismico.DISENO
    assert min(sectores) == d["unidades"][0] and max(sectores) == d["unidades"][1]
    assert d["ventana_horas"][0] <= min(ventanas) and max(ventanas) <= d["ventana_horas"][1]
    assert min(sismos) == 0 and max(sismos) <= sismico.MAX_SISMOS                    # un sector sin sismos es un dato válido


def test_un_solo_preprocesamiento():
    """Lo que entra a la red al simular es lo que `preparar` da para ese mismo dataset leído como archivo."""
    sim = s.simular(np.random.default_rng(1), 3)
    e = sim["extra"]
    for b in range(3):
        n = e["mascara"][b].sum(-1).astype(int)
        t, mascara = series.con_relleno([e["t"][b, j, : n[j]] for j in range(len(n))])
        m, _ = series.con_relleno([e["m"][b, j, : n[j]] for j in range(len(n))])
        x, mascara_x, cov, tam = sismico.preparar(t, m, mascara, e["T"][b])
        k = mascara_x.shape[1]
        assert np.allclose(x, sim["x"][b, :, :k], atol=1e-5) and np.allclose(mascara_x, sim["mascara"][b, :, :k])
        assert np.allclose(cov, sim["cov"][b], atol=1e-5) and np.allclose(tam, sim["tam"][b], atol=1e-5)


def test_la_forma_cerrada_coincide_con_simular_hacia_adelante():
    """El número esperado de sismos en las H horas siguientes, y la probabilidad de uno fuerte, contra 20.000 simulaciones.

    Se parte de la tronadura (T = 0, sin sismos previos): ahí la historia es la misma en todas las simulaciones."""
    gen = np.random.default_rng(2)
    mu, A, n, alfa, omega, b, H, sobre = 0.6, 8.0, 0.45, 1.0, 1.2, 1.0, 6.0, 1.3
    G = 20000
    uno = np.ones(G)
    g, t, m = s.ramificar(gen, mu * uno, A * uno, n * uno, alfa * uno, omega * uno, b * sismico.LN10 * uno, H * uno, tope=None)
    eta = np.array([0.0, 0.0, np.log(n / (1 - n)), np.log(alfa), np.log(omega), np.log(b)])
    lam = np.array([[np.log(mu), np.log(A)]])
    esperado = sismico.esperados(eta, lam, np.zeros(1), np.float64(0.0), H)[0]
    assert abs(len(g) / G - esperado) < 0.02 * esperado, (len(g) / G, esperado)
    hubo_fuerte = np.bincount(g[m >= sobre], minlength=G) > 0
    p = sismico.sismo_fuerte(eta, lam, np.zeros(1), np.float64(0.0), H, sobre)[0]
    assert abs(hubo_fuerte.mean() - p) < 0.05, (hubo_fuerte.mean(), p)             # aproximación de Poisson: va en `limitaciones`


def test_predictivo_a_priori_cubre_el_archivo_del_demo():
    """El tamaño del archivo del demo está bien adentro del diseño y sus resúmenes entre los percentiles 2 y 98 de lo simulado."""
    caso = cargar_caso("sismicidad")
    datos = series.leer(caso)
    m0 = float(caso["columnas"]["magnitud_minima"])
    d = sismico.DISENO
    T = max(t.max() for t in datos["t"])
    assert d["unidades"][0] < len(datos["ids"]) < d["unidades"][1] and d["ventana_horas"][0] < T < d["ventana_horas"][1]
    assert max(len(t) for t in datos["t"]) < sismico.MAX_SISMOS / 2

    def resumenes(t, m, mascara, T):          # por sector: sismos por hora, la mayor magnitud y qué parte cae en el primer cuarto de la ventana
        n = mascara.sum(-1)
        T = np.asarray(T, dtype=float)[..., None]                                  # (...) → (..., 1): un valor por dataset
        temprano = ((t < T[..., None] / 4) * mascara).sum(-1) / np.maximum(n, 1)
        return n / T, (m * mascara).max(-1), temprano

    gen = np.random.default_rng(3)
    sims = [[], [], []]
    for _ in range(200):
        sim = s.simular(gen, 8)
        e = sim["extra"]
        for lista, r in zip(sims, resumenes(e["t"], e["m"], e["mascara"], e["T"])):
            lista.append(r.ravel())
    t, mascara = series.con_relleno(datos["t"]); m, _ = series.con_relleno([y - m0 for y in datos["y"]])
    for lista, del_demo in zip(sims, resumenes(t, m, mascara, T)):
        bajo, alto = np.quantile(np.concatenate(lista), [0.02, 0.98])
        assert bajo <= del_demo.min() and del_demo.max() <= alto, (bajo, alto, del_demo.min(), del_demo.max())


def test_fuera_del_rango_es_rojo_datos():
    from nucleo import api
    columnas = {"unidad": "unidad", "tiempo": "tiempo", "valor": "valor"}
    un_sector = {"unidad": ["A"] * 5, "tiempo": ["0.5", "1", "2", "3", "5"], "valor": ["-0.5"] * 5}
    r = api.analizar_archivo("sismico", un_sector, columnas)
    assert r["semaforo"]["estado"] == "rojo_datos" and "1 sector" in r["semaforo"]["motivo"]
    corto = {"unidad": ["A", "A", "B", "B"], "tiempo": ["0.1", "0.2", "0.1", "0.3"], "valor": ["-0.5"] * 4}
    r = api.analizar_archivo("sismico", corto, columnas)
    assert r["semaforo"]["estado"] == "rojo_datos" and "ventanas de 2 a 24 horas" in r["semaforo"]["motivo"]
