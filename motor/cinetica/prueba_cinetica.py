"""`cinetica`: el simulador respeta su diseño de tamaños, usa el preprocesamiento del servicio y cubre el archivo del demo."""

import numpy as np

from motor.cinetica import simular as s
from nucleo import cinetica, series
from nucleo.casos import cargar_caso


def test_el_diseno_sortea_tamanos_dentro_del_rango():
    gen = np.random.default_rng(0)
    lineas, lecturas = set(), set()
    for _ in range(200):
        sim = s.simular(gen, 4)
        n = sim["mascara"].sum(-1)
        lineas.add(sim["mascara"].shape[1]); lecturas.update(n.ravel().astype(int).tolist())
        assert sim["mascara"].shape[2] <= cinetica.DISENO["celdas"][1]
        assert np.isfinite(sim["x"]).all() and np.isfinite(sim["cantidad"]).all()
        assert sim["cantidad"].shape == sim["mascara"].shape[:2]
    assert min(lineas) == cinetica.DISENO["unidades"][0] and max(lineas) == cinetica.DISENO["unidades"][1]
    assert min(lecturas) == cinetica.DISENO["lecturas"][0] and max(lecturas) == cinetica.DISENO["lecturas"][1]


def test_un_solo_preprocesamiento():
    """Lo que entra a la red al simular es lo que `preparar` da para ese mismo dataset leído como archivo."""
    sim = s.simular(np.random.default_rng(1), 3)
    for b in range(3):
        n = sim["mascara"][b].sum(-1).astype(int)
        t, mascara = series.con_relleno([sim["t"][b, j, : n[j]] for j in range(len(n))])
        y, _ = series.con_relleno([sim["y"][b, j, : n[j]] for j in range(len(n))])
        x, cov, tam = cinetica.preparar(t, y, mascara, sim["extra"]["t_final"][b])
        k = mascara.shape[1]
        assert np.allclose(x, sim["x"][b, :, :k], atol=1e-6) and np.allclose(cov, sim["cov"][b], atol=1e-6) and np.allclose(tam, sim["tam"][b], atol=1e-6)


def test_cantidad_de_coincide_con_la_verdad():
    sim = s.simular(np.random.default_rng(2), 5)
    assert np.allclose(s.cantidad_de(sim["eta"][None], sim["lam"][None], sim["extra"])[0], sim["cantidad"], atol=1e-5)


def test_predictivo_a_priori_cubre_el_archivo_del_demo():
    """Cada resumen del archivo del demo cae entre los percentiles 2 y 98 de lo simulado, y su tamaño está bien adentro del diseño."""
    caso = cargar_caso("flotacion")
    datos = series.leer(caso)
    t_final = float(caso["columnas"]["tiempo_final"])
    d = cinetica.DISENO
    assert d["unidades"][0] < len(datos["ids"]) < d["unidades"][1]
    assert all(d["lecturas"][0] <= len(t) <= d["lecturas"][1] for t in datos["t"])

    def resumenes(t, y, mascara, tf):          # (..., U, K) → por línea: primera lectura, última, y la última como fracción del tiempo
        n = mascara.sum(-1).astype(int)
        ultimo = np.take_along_axis(y, np.maximum(n - 1, 0)[..., None], -1)[..., 0]
        u_ult = np.take_along_axis(t, np.maximum(n - 1, 0)[..., None], -1)[..., 0] / tf
        return y[..., 0], ultimo, u_ult

    gen = np.random.default_rng(3)
    sims = [[], [], []]
    for _ in range(300):
        sim = s.simular(gen, 16)
        hay = sim["mascara"].sum(-1) > 0
        for lista, r in zip(sims, resumenes(sim["t"], sim["y"], sim["mascara"], sim["extra"]["t_final"][:, None])):
            lista.append(r[hay])
    t, mascara = series.con_relleno(datos["t"]); y, _ = series.con_relleno(datos["y"])
    for lista, del_demo in zip(sims, resumenes(t, y, mascara, t_final)):
        bajo, alto = np.quantile(np.concatenate(lista), [0.02, 0.98])
        assert bajo <= del_demo.min() and del_demo.max() <= alto, (bajo, alto, del_demo)
