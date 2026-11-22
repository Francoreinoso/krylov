"""Los campos de D-42: el rango de 90% de cada bloque, la posteriori y la serie de cada unidad, y todos los lugares de «¿Dónde perforo?»."""

import numpy as np
import pytest

from nucleo import api, espacial, series


def test_posteriori_resume_las_muestras():
    muestras = np.random.default_rng(0).normal(10.0, 2.0, 4096)
    q = series.posteriori(muestras)
    assert q["muestras"] == 4096 and len(q["cuantiles"]) == series.CUANTILES
    assert q["bajo"] < q["medio"] < q["alto"] and q["cuantiles"] == sorted(q["cuantiles"])
    assert abs(q["bajo"] - 10.0 + 1.645 * 2.0) < 0.2 and abs(q["alto"] - 10.0 - 1.645 * 2.0) < 0.2


def test_mapa_trae_su_rango(monkeypatch):
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    r = api.analizar("leyes")
    m = r["mapa"]
    assert len(m["bajo"]) == len(m["alto"]) == len(m["media"])
    dentro = [i for i, v in enumerate(m["media"]) if v is not None]
    assert all(m["bajo"][i] <= m["media"][i] <= m["alto"][i] for i in dentro)
    assert all(m["bajo"][i] is None and m["alto"][i] is None for i, v in enumerate(m["media"]) if v is None)
    assert r["escena"]["umbral"] == m["umbral"]


@pytest.mark.parametrize("caso, motor", [("taludes", "DEFORMACION"), ("flotacion", "CINETICA"), ("flota", "DESGASTE"), ("sismicidad", "SISMICO")])
def test_unidades_traen_posteriori_y_serie(monkeypatch, caso, motor):
    monkeypatch.setenv(f"KRYLOV_MOTOR_{motor}", "red")
    r = api.analizar(caso)
    assert r["implementacion"] == "red" and r["escena"]
    for u in r["unidades"]:
        tiempos = [t for t, _ in u["serie"]]
        assert tiempos == sorted(tiempos)
        if "posteriori" in u:
            assert u["posteriori"]["bajo"] <= u["posteriori"]["medio"] <= u["posteriori"]["alto"]
    con = [u for u in r["unidades"] if "posteriori" in u]
    if caso == "taludes":                                       # solo los sectores que se aceleran: lo mismo que su marca
        assert con and all(u["curva"]["marca"] for u in con)
    else:
        assert len(con) == len(r["unidades"])


def test_donde_medir_trae_todos_los_lugares(monkeypatch):
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    d = api.donde_medir("leyes")
    valores = [lugar["valor_de_medir"] for lugar in d["lugares"]]
    assert valores == sorted(valores, reverse=True) and len(d["lugares"]) * espacial.RESULTADOS_POR_LUGAR == d["analisis_rehechos"]
    assert [(c["x"], c["y"]) for c in d["candidatas"]] == [(lugar["x"], lugar["y"]) for lugar in d["lugares"][:3]]
