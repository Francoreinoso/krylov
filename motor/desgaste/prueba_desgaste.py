"""`desgaste`: el simulador respeta su diseño de tamaños, usa el preprocesamiento del servicio y cubre el archivo del demo."""

import numpy as np

from motor.desgaste import simular as s
from nucleo import desgaste, series
from nucleo.casos import cargar_caso


def test_el_diseno_sortea_tamanos_y_los_camiones_siguen_en_servicio():
    gen = np.random.default_rng(0)
    camiones, muestras = set(), set()
    d = desgaste.DISENO
    for _ in range(300):
        sim = s.simular(gen, 2)
        camiones.add(sim["mascara"].shape[1]); muestras.update(sim["mascara"].sum(-1).ravel().astype(int).tolist())
        assert all(np.isfinite(sim[k]).all() for k in ("x", "cov", "tam", "eta", "lam", "cantidad"))
        assert (desgaste.desgaste_hoy(sim["lam"]) < desgaste.EN_SERVICIO_BAJO).all()
        dt = np.diff(sim["t"], axis=-1)[sim["mascara"][..., 1:] > 0]
        assert (dt > 0).all() and sim["t"].max() <= d["miles_de_horas_hoy"][1]            # tiempos crecientes e irregulares
    assert d["unidades"][0] <= min(camiones) < 11 and 90 < max(camiones) <= d["unidades"][1]
    assert min(muestras) == d["lecturas"][0] and max(muestras) == d["lecturas"][1]


def test_un_solo_preprocesamiento():
    """Lo que entra a la red al simular es lo que `preparar` da para ese mismo dataset leído como archivo."""
    sim = s.simular(np.random.default_rng(1), 3)
    for b in range(3):
        n = sim["mascara"][b].sum(-1).astype(int)
        t, mascara = series.con_relleno([sim["t"][b, j, : n[j]] for j in range(len(n))])
        y, _ = series.con_relleno([sim["y"][b, j, : n[j]] for j in range(len(n))])
        x, cov, tam = desgaste.preparar(t, y, mascara, sim["exigencia"][b], sim["extra"]["a_mantencion"][b])
        k = mascara.shape[1]
        assert np.allclose(x, sim["x"][b, :, :k], atol=1e-6) and np.allclose(cov, sim["cov"][b], atol=1e-6) and np.allclose(tam, sim["tam"][b], atol=1e-6)


def test_cantidad_de_coincide_con_la_verdad():
    sim = s.simular(np.random.default_rng(2), 5)
    assert np.allclose(s.cantidad_de(sim["eta"][None], sim["lam"][None], sim["extra"])[0], sim["cantidad"], rtol=1e-4, atol=1e-4)


def test_falla_antes_coincide_con_simular_hacia_adelante():
    """La probabilidad de fallar antes de la mantención, contra el proceso gamma simulado en muchos pasos chicos."""
    gen = np.random.default_rng(3)
    eta = np.array([np.log(0.5), np.log(0.3), 0.3, np.log(0.3), np.log(0.04)])
    lam = np.array([[np.log(0.6), np.log(0.7 + desgaste.PISO)]])
    h = np.array([0.5])
    p = desgaste.falla_antes(gen, eta, lam, h, sorteos=40000)[0]
    pasos = gen.gamma(0.6 * (0.5 / 50) / 0.09, 0.09, size=(40000, 50)).sum(-1)
    assert abs(p - (0.7 + pasos >= 1.0).mean()) < 0.015


def test_predictivo_a_priori_cubre_el_archivo_del_demo():
    """Cada resumen del archivo del demo cae entre los percentiles 2 y 98 de lo simulado, y su tamaño está bien adentro del diseño."""
    caso = cargar_caso("flota")
    datos = series.leer(caso, extras=("covariables", "horizonte_por_unidad"))
    d = desgaste.DISENO
    assert d["unidades"][0] < len(datos["ids"]) < d["unidades"][1]
    assert all(d["lecturas"][0] <= len(t) <= d["lecturas"][1] for t in datos["t"])
    a_mantencion = datos["extras"]["horizonte_por_unidad"] / desgaste.HORAS_POR_UNIDAD
    assert d["miles_de_horas_a_mantencion"][0] < a_mantencion.min() and a_mantencion.max() < d["miles_de_horas_a_mantencion"][1]

    def resumenes(t, y, mascara):          # por camión: última medición, horas de hoy, pendiente media y el mayor salto entre muestras
        n = mascara.sum(-1).astype(int)
        ultimo = np.take_along_axis(y, (n - 1)[..., None], -1)[..., 0]
        hoy = t.max(-1)
        salto = (np.diff(y, axis=-1, prepend=0.0) * mascara).max(-1)
        return ultimo, hoy, ultimo / hoy, salto

    gen = np.random.default_rng(4)
    sims = [[], [], [], []]
    for _ in range(300):
        sim = s.simular(gen, 8)
        for lista, r in zip(sims, resumenes(sim["t"], sim["y"], sim["mascara"])):
            lista.append(r.ravel())
    t, mascara = series.con_relleno([ti / desgaste.HORAS_POR_UNIDAD for ti in datos["t"]]); y, _ = series.con_relleno(datos["y"])
    for lista, del_demo in zip(sims, resumenes(t, y, mascara)):
        # Son 40 camiones: alguno cae en las colas por azar. Se exige que ninguno salga del rango 0,1% a 99,9% de lo
        # simulado y que a lo más 3 de los 40 salgan del rango 2% a 98%.
        extremo_bajo, bajo, alto, extremo_alto = np.quantile(np.concatenate(lista), [0.001, 0.02, 0.98, 0.999])
        fuera = int(((del_demo < bajo) | (del_demo > alto)).sum())
        print(f"demo {del_demo.min():.3f} a {del_demo.max():.3f}; simulado 2-98%: {bajo:.3f} a {alto:.3f}; fuera: {fuera}")
        assert extremo_bajo <= del_demo.min() and del_demo.max() <= extremo_alto and fuera <= 3, (bajo, alto, del_demo.min(), del_demo.max(), fuera)


def test_fuera_del_rango_de_tamano_es_rojo_datos():
    from nucleo import api
    columnas = {"unidad": "unidad", "tiempo": "tiempo", "valor": "valor", "covariables": ["exigencia"], "horizonte_por_unidad": "horas_a_mantencion"}
    filas = [(f"C-{j}", str(300 * k), str(0.05 * k), "0.1", "500") for j in range(3) for k in range(1, 6)]
    tabla = dict(zip(("unidad", "tiempo", "valor", "exigencia", "horas_a_mantencion"), map(list, zip(*filas))))
    r = api.analizar_archivo("desgaste", tabla, columnas)
    assert r["semaforo"]["estado"] == "rojo_datos" and "3 camiones" in r["semaforo"]["motivo"]
