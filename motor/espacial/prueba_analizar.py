"""`analizar` y `donde_medir` del terreno real, de punta a punta, con la red sin entrenar y con muestras de MCMC de mentira.

Prueba la forma de las respuestas y la mecánica (preprocesamiento, onnxruntime, flujo en
NumPy, kriging, decisión). Los valores no significan nada: la red no está entrenada.
"""

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from motor.espacial.exportar import configuracion, exportar
from motor.espacial.red import RedEspacial
from motor.espacial.simular import Prior, simular
from nucleo import api, casos, espacial

EJEMPLOS = Path(__file__).resolve().parent.parent.parent / "contratos" / "ejemplos"


@pytest.fixture(scope="module")
def artefactos(tmp_path_factory):
    """Artefactos de una red sin entrenar, más un posterior «de MCMC» inventado (θ' del simulador)."""
    carpeta = tmp_path_factory.mktemp("artefactos")
    torch.manual_seed(0)
    red = RedEspacial()
    gen = torch.Generator().manual_seed(0)
    theta = simular(512, Prior(), gen)["theta"]
    red.flujo.fijar_escala(theta)
    exportar(red, carpeta / "espacial", configuracion(3, Prior()))
    (carpeta / "espacial" / "mcmc").mkdir()
    np.savez(carpeta / "espacial" / "mcmc" / "terreno.npz", theta_est=theta[:200].numpy())
    return carpeta


@pytest.fixture
def con_red(artefactos, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")


@pytest.fixture
def con_mcmc(artefactos, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "mcmc")


def _revisar_mapa(r: dict):
    ejemplo = json.loads((EJEMPLOS / "analizar_espacial.json").read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(r), set(ejemplo) - set(r)
    assert set(r["mapa"]) == set(ejemplo["mapa"]) and r["unidades"] is None
    p = r["mapa"]["p"]
    assert len(p) == len(r["mapa"]["media"]) == 1024 and sum(v is None for v in p) == 683
    assert all(0 <= v <= 1 for v in p if v is not None)
    assert sum(r["resumen_colores"].values()) == 341 and r["costo_de_no_saber"]["valor"] >= 0
    assert abs(sum(f["efecto"] for f in r["factores"]) - 1) < 0.01          # las tres partes de la variación suman 1
    assert set(r["factores"][0]) == set(ejemplo["factores"][0])
    json.dumps(r)


def test_analizar_con_la_red(con_red):
    r = api.analizar("terreno")
    assert "error" not in r, r
    _revisar_mapa(r)
    assert r["implementacion"] == "red" and r["precalculado"] is False
    assert r["registro"][0] == "155 mediciones" and len(r["mapa"]["puntos"]) == 155
    assert r["examen"]["tipo"] == "puntos_reales_escondidos" and r["examen"]["n"] == 31
    assert {f["nombre"] for f in r["factores"]} == {"tendencia", "continuidad", "ruido"}
    otra = api.analizar("terreno")                                         # semilla fija: misma entrada, misma salida
    assert otra["mapa"]["p"] == r["mapa"]["p"] and otra["factores"] == r["factores"]


def test_medicion_simulada_y_quitar_tendencia(con_red):
    base = api.analizar("terreno")
    medido = api.analizar("terreno", mediciones=[{"x": 179678, "y": 330800, "valor": 1500}])
    assert medido["registro"][0] == "156 mediciones" and medido["examen"] is None
    assert medido["mapa"]["p"] != base["mapa"]["p"]
    sin = api.analizar("terreno", transformaciones=["quitar_tendencia"])
    assert {f["nombre"] for f in sin["factores"]} == {"continuidad", "ruido"}
    caros = api.analizar("terreno", costos={"falso_si": 60000})
    assert caros["punto_de_corte"] > base["punto_de_corte"] and caros["mapa"]["p"] == base["mapa"]["p"]


def test_analizar_con_el_mcmc_precalculado(con_mcmc):
    r = api.analizar("terreno")
    assert "error" not in r, r
    _revisar_mapa(r)
    assert r["implementacion"] == "mcmc" and r["precalculado"] is True
    assert r["examen"] is None                              # el examen con `mcmc` necesita su propia corrida precalculada
    assert api.analizar("terreno", transformaciones=["quitar_tendencia"])["codigo"] == "no_disponible"


def test_donde_medir(con_red):
    ejemplo = json.loads((EJEMPLOS / "donde_medir.json").read_text(encoding="utf-8"))
    r = api.donde_medir("terreno")
    assert "error" not in r, r
    assert set(ejemplo) - {"_aviso"} == set(r)
    assert len(r["candidatas"]) == 3 and [c["etiqueta"] for c in r["candidatas"]] == ["A", "B", "C"]
    assert r["analisis_rehechos"] % espacial.RESULTADOS_POR_LUGAR == 0 and 0 < r["analisis_rehechos"] <= 480
    terreno = espacial.leer_terreno(casos.cargar_caso("terreno"))
    for c in r["candidatas"]:
        assert set(c) == set(ejemplo["candidatas"][0])
        assert c["valor_neto"] == c["valor_de_medir"] - c["costo_medicion"] and c["costo_medicion"] == 3000
        assert c["resultados_posibles"]["bajo"] < c["resultados_posibles"]["medio"] < c["resultados_posibles"]["alto"]
        fila, columna = espacial.indices_bloque(c["x"], c["y"], terreno["geometria"])
        assert terreno["dentro"][fila, columna] and terreno["cuenta"][fila, columna] == 0     # dentro del terreno y sin medición
    assert r["candidatas"][0]["valor_de_medir"] >= r["candidatas"][1]["valor_de_medir"] >= r["candidatas"][2]["valor_de_medir"]
    json.dumps(r)
    # La medición simulada entra por `mediciones` y cambia las candidatas.
    c = r["candidatas"][0]
    despues = api.donde_medir("terreno", mediciones=[{"x": c["x"], "y": c["y"], "valor": c["resultados_posibles"]["alto"]}])
    assert (despues["candidatas"][0]["x"], despues["candidatas"][0]["y"]) != (c["x"], c["y"])


def test_donde_medir_con_el_mcmc(con_mcmc, monkeypatch):
    monkeypatch.setattr(espacial, "MAXIMO_DE_LUGARES", 4)                 # 48 análisis por kriging: alcanza para la prueba
    r = api.donde_medir("terreno")
    assert "error" not in r, r
    assert r["precalculado"] is True and r["analisis_rehechos"] <= 48


def test_salvavidas_mapa_de_la_red_y_theta_del_mcmc(con_red, monkeypatch):
    """Con KRYLOV_ESPACIAL_THETA=mcmc el mapa no cambia y «qué manda» sale del MCMC precalculado, rotulado."""
    de_la_red = api.analizar("terreno")
    monkeypatch.setenv("KRYLOV_ESPACIAL_THETA", "mcmc")
    mixto = api.analizar("terreno")
    assert "error" not in mixto and mixto["implementacion"] == "red"
    assert mixto["mapa"]["p"] == de_la_red["mapa"]["p"] and mixto["factores"] != de_la_red["factores"]
    assert "precalculado" in mixto["registro"][-1] and "precalculado" not in de_la_red["registro"][-1]
    assert len(api.donde_medir("terreno")["candidatas"]) == 3
