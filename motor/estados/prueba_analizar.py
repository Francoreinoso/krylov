"""`analizar` de crédito de punta a punta, con la red sin entrenar y con muestras «de MCMC» inventadas.

Prueba la forma de la respuesta y la mecánica (lectura, filas, onnxruntime, flujo en NumPy,
filtro forward, decisión, examen). Los valores no significan nada: la red no está entrenada.
"""

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from motor.estados import simular
from motor.estados.exportar import configuracion, exportar
from motor.estados.red import RedEstados
from nucleo import api, casos

EJEMPLO = Path(__file__).resolve().parents[2] / "contratos" / "ejemplos" / "analizar_tabla.json"


@pytest.fixture(scope="module")
def artefactos(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp("artefactos")
    torch.manual_seed(0)
    exportar(RedEstados(), carpeta / "estados", configuracion())
    (carpeta / "estados" / "mcmc").mkdir()
    np.savez(carpeta / "estados" / "mcmc" / "credito.npz", theta=simular.muestrear_prior(np.random.default_rng(0), 200))
    return carpeta


@pytest.mark.parametrize("impl", ["red", "mcmc"])
def test_analizar_credito(artefactos, monkeypatch, impl):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESTADOS", impl)
    r = api.analizar("credito")
    assert "error" not in r, r
    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(r), set(ejemplo) - set(r)
    assert r["motor_id"] == "estados" and r["implementacion"] == impl and r["precalculado"] is (impl == "mcmc")
    assert len(r["unidades"]) == 400 and set(r["unidades"][0]) == set(ejemplo["unidades"][0])
    assert all(len(u["muestras_p"]) == 32 and 0 <= u["rango_bajo"] <= u["p"] + 0.05 for u in r["unidades"])
    assert r["unidades"][0]["duda"] >= r["unidades"][-1]["duda"] >= 0
    assert sum(r["resumen_colores"].values()) == 400 and r["costo_de_no_saber"]["valor"] >= 0
    assert [set(f) for f in r["factores"]] == [set(ejemplo["factores"][0])] * 3
    assert r["examen"]["tipo"] == "datos_reales_reservados" and r["examen"]["n"] == 400
    assert sum(t["n"] for t in r["examen"]["tramos"]) <= 400 and r["registro"][0] == "400 clientes por decidir"
    assert r["titular"].endswith("dólares.") and set(r["columnas"]) == set(ejemplo["columnas"])
    json.dumps(r)
    assert api.analizar("credito")["unidades"] == r["unidades"]                     # semilla fija
    caros = api.analizar("credito", costos={"falso_si": 3000})                     # los costos cambian la decisión, no las p
    assert sorted(u["p"] for u in caros["unidades"]) == sorted(u["p"] for u in r["unidades"])
    assert api.analizar("credito", transformaciones=["quitar_factor:AGE"])["codigo"] == "no_disponible"
