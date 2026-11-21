"""La cartera, de punta a punta con la red sin entrenar: mecánica y forma (los valores no significan nada)."""

import json
import sys
from pathlib import Path

import pytest
import torch

from motor.estados.exportar import configuracion, exportar
from motor.estados.red import RedEstados
from nucleo import cartera as comun, casos, estados

EJEMPLO = Path(__file__).resolve().parents[2] / "contratos" / "ejemplos" / "cartera.json"


@pytest.fixture(scope="module")
def artefactos(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp("artefactos")
    torch.manual_seed(0)
    exportar(RedEstados(), carpeta / "estados", configuracion())
    return carpeta


def test_cartera_en_lote(artefactos, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESTADOS", "red")
    caso = {**casos.cargar_caso("credito"), "cartera": {"modo": "simulada", "n": 120, "nombre": "Cartera", "que": "carteras"}}
    r = estados.cartera(caso)
    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(r) == {k for k in ejemplo if not k.startswith("_")} and set(r["filas"][0]) == set(ejemplo["filas"][0])
    assert r["n_analisis"] == 120 and len(r["filas"]) == 120 and r["precalculado"] is False and r["sintetico"] is True
    costos = [f["costo_de_no_saber"] for f in r["filas"]]
    assert costos == sorted(costos, reverse=True) and min(costos) >= 0
    assert all(80 <= f["n_unidades"] <= 480 for f in r["filas"])             # cerca del 20% de 500 a 2.000 clientes
    assert len({f["cliente"] for f in r["filas"]}) == 120 and r["origen_datos"] == "120 carteras simuladas, cada una distinta"
    json.dumps(r)
    assert estados.cartera(caso)["filas"] == r["filas"]                      # semilla fija


def test_cartera_precalculada_con_mcmc(artefactos, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESTADOS", "mcmc")
    caso = {**casos.cargar_caso("credito"), "cartera": {"modo": "simulada", "n": 120}}
    with pytest.raises(casos.ErrorKrylov):
        estados.cartera(caso)
    (artefactos / "estados" / "cartera.json").write_text(json.dumps({"caso": "credito", "n_analisis": 3, "filas": [], "precalculado": False}))
    assert estados.cartera(caso)["precalculado"] is True


def test_reparto_en_lotes_y_sin_torch_en_el_servicio():
    assert comun.tamanos_de_lote(1000) == [50] * 20 and comun.tamanos_de_lote(120) == [50, 50, 20]
    import subprocess
    codigo = "import sys, nucleo.api, nucleo.estados, nucleo.jerarquico, nucleo.espacial, nucleo.cartera, motor.estados.simular; print(sorted(m for m in ('torch', 'zuko', 'jax', 'numpyro') if m in sys.modules))"
    assert subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[2]).stdout.strip() == "[]"
