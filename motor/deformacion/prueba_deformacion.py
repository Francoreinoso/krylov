"""`deformacion`: el simulador respeta su diseño de tamaños, usa el preprocesamiento del servicio y cubre el archivo del demo."""

import numpy as np

from motor.deformacion import simular as s
from nucleo import deformacion, series
from nucleo.casos import cargar_caso


def test_el_diseno_sortea_tamanos_dentro_del_rango():
    gen = np.random.default_rng(0)
    sectores, lecturas, faltan = set(), set(), []
    for _ in range(300):
        sim = s.simular(gen, 2)
        U, K = sim["mascara"].shape[1:]
        sectores.add(U); lecturas.add(K)
        faltan.extend((1 - sim["mascara"].mean(-1)).ravel())
        assert np.isfinite(sim["x"]).all() and np.isfinite(sim["eta"]).all() and np.isfinite(sim["lam"]).all()
        assert sim["cantidad"].shape == (2, U) and set(np.unique(sim["lam"][..., 3])) <= {0.0, 1.0}
    d = deformacion.DISENO
    assert d["unidades"][0] <= min(sectores) < 8 and 60 < max(sectores) <= d["unidades"][1]
    assert d["lecturas"][0] <= min(lecturas) < 30 and 150 < max(lecturas) <= d["lecturas"][1]
    assert 0 <= min(faltan) and max(faltan) <= d["faltantes"][1] + 1e-9


def test_un_solo_preprocesamiento():
    """Lo que entra a la red al simular es lo que el servicio arma para ese mismo dataset leído como archivo."""
    sim = s.simular(np.random.default_rng(1), 3)
    K = sim["mascara"].shape[2]
    for b in range(3):
        horas = 0.5 * np.arange(1, K + 1)                                           # el mismo muro, con tiempos en horas
        datos = {"ids": [f"S-{j}" for j in range(sim["mascara"].shape[1])], "extras": {},
                 "t": [horas[m > 0] for m in sim["mascara"][b]], "y": [y[m > 0] for y, m in zip(sim["y"][b], sim["mascara"][b])]}
        datos, grilla, aviso = deformacion.a_grilla(datos)
        y, mascara = deformacion.en_la_grilla(datos, grilla)
        u, _, _ = deformacion.normalizar_tiempo(grilla)
        x, cov, tam, log_e = deformacion.preparar(u, y, mascara)
        assert aviso is None and len(grilla) == K
        assert np.allclose(x, sim["x"][b], atol=1e-5) and np.allclose(cov, sim["cov"][b]) and np.allclose(tam, sim["tam"][b], atol=1e-5)
        assert np.isclose(log_e, sim["log_e"][b])


def test_el_modo_comun_se_resta_exacto():
    """Sumar lo mismo a todos los sectores en cada lectura (la atmósfera) no cambia cuánto se aparta cada sector de la
    mediana, en las unidades del archivo. (La escala e sí lo incluye: es el movimiento total del sector típico.)"""
    sim = s.simular(np.random.default_rng(2), 1)
    u, y, m = sim["u"], sim["y"][0], sim["mascara"][0].copy()
    m[:, 0] = 1.0                                         # exacto cuando todos los sectores tienen su primera lectura
    comun = 3.0 * np.sin(7 * u)
    x1, _, _, e1 = deformacion.preparar(u, y * m, m)
    x2, _, _, e2 = deformacion.preparar(u, (y + comun) * m, m)
    assert np.allclose(np.sinh(x1[..., 1]) * np.exp(e1), np.sinh(x2[..., 1]) * np.exp(e2), atol=1e-4)


def test_grilla_adelgazada_con_mas_de_200_tiempos():
    t = np.arange(1, 501) * 0.1
    datos = {"ids": ["A", "B"], "t": [t, t], "y": [t, 2 * t], "extras": {}}
    nuevo, grilla, aviso = deformacion.a_grilla(datos)
    assert len(grilla) == 200 and aviso and all(len(v) == 200 for v in nuevo["t"])


def test_predictivo_a_priori_cubre_el_archivo_del_demo():
    """Los resúmenes del archivo del demo caen entre los percentiles 2 y 98 de lo simulado, y su tamaño está bien adentro."""
    caso = cargar_caso("taludes")
    datos = series.leer(caso)
    datos, grilla, _ = deformacion.a_grilla(datos)
    d = deformacion.DISENO
    assert d["unidades"][0] < len(datos["ids"]) < d["unidades"][1] and d["lecturas"][0] < len(grilla) < d["lecturas"][1]
    y, mascara = deformacion.en_la_grilla(datos, grilla)
    u, _, _ = deformacion.normalizar_tiempo(grilla)
    x, _, tam, _ = deformacion.preparar(u, y, mascara)

    def resumenes(x, m):          # por sector: desplazamiento final (sin el modo común, en e) y la mayor velocidad
        K = m.shape[-1]
        ultima = K - 1 - np.argmax(m[..., ::-1] > 0, axis=-1)
        return np.take_along_axis(x[..., 1], ultima[..., None], -1)[..., 0], np.abs(x[..., 2]).max(-1)

    gen = np.random.default_rng(3)
    sims, tams = [[], []], []
    for _ in range(300):
        sim = s.simular(gen, 8)
        for lista, r in zip(sims, resumenes(sim["x"], sim["mascara"])):
            lista.append(r.ravel())
        tams.append(sim["tam"])
    for lista, del_demo in zip(sims, resumenes(x, mascara)):
        bajo, alto = np.quantile(np.concatenate(lista), [0.02, 0.98])
        assert bajo <= del_demo.min() and del_demo.max() <= alto, (bajo, alto, del_demo.min(), del_demo.max())
    bajo, alto = np.quantile(np.concatenate(tams), [0.02, 0.98], axis=0)
    assert (bajo <= tam).all() and (tam <= alto).all(), (bajo, alto, tam)


def test_fuera_del_rango_de_tamano_es_rojo_datos():
    """Un muro de 3 sectores, o con 10 lecturas por sector, no se responde: practicó con 6 a 80 sectores y 24 a 200 lecturas."""
    from nucleo import api
    columnas = {"unidad": "unidad", "tiempo": "tiempo", "valor": "valor"}
    def tabla(sectores, lecturas):
        filas = [(f"S-{j}", str(0.5 * k), str(0.1 * k)) for j in range(sectores) for k in range(1, lecturas + 1)]
        return {"unidad": [f[0] for f in filas], "tiempo": [f[1] for f in filas], "valor": [f[2] for f in filas]}
    pocos = api.analizar_archivo("deformacion", tabla(3, 50), columnas)
    cortas = api.analizar_archivo("deformacion", tabla(12, 10), columnas)
    assert pocos["semaforo"]["estado"] == "rojo_datos" and "3 sectores" in pocos["semaforo"]["motivo"]
    assert cortas["semaforo"]["estado"] == "rojo_datos" and "10 lecturas" in cortas["semaforo"]["motivo"]
