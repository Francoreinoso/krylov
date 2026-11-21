"""La nube de inasistencias de punta a punta, con la red sin entrenar: mecánica y forma (los valores no significan nada)."""

import json
from pathlib import Path

import pytest
import torch

from motor.jerarquico import nube
from motor.jerarquico.exportar import configuracion, exportar
from motor.jerarquico.red import RedJerarquico
from motor.jerarquico import simular
from nucleo import api, casos

EJEMPLO = Path(__file__).resolve().parents[2] / "contratos" / "ejemplos" / "nube.json"


@pytest.mark.skipif(simular.leer_real() is None, reason="datos/demo/inasistencias.csv no se versiona")
def test_nube_de_inasistencias(tmp_path, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", tmp_path)
    assert api.nube("inasistencias")["codigo"] == "no_disponible"                  # sin nube.npz no se inventa nada
    torch.manual_seed(0)
    exportar(RedJerarquico(), tmp_path / "jerarquico", configuracion())
    resumen = nube.generar(tmp_path / "jerarquico", simulaciones=40, por_lote=20)
    assert resumen["n_simulaciones"] == 40 and resumen["citas"] == 1980 and resumen["barrios"] == 30 and 0.5 <= resumen["x_maximo"] <= 1
    r = api.nube("inasistencias")
    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(r) == {k for k in ejemplo if not k.startswith("_")} and r["caso"] == "inasistencias" and r["n_simulaciones"] == 40
    assert len(r["puntos"]) == 40 and all(0.5 <= x <= 1 and 0 <= y <= 1 for x, y in r["puntos"])
    assert set(r["detectores"]) == set(ejemplo["detectores"]) and r["detectores"]["resumenes_aprendidos"]["distancia"] > 0
    assert 0.5 <= r["archivo"]["x"] <= 1 and abs(r["archivo"]["y"] - 0.21) < 0.01       # la proporción de inasistencia del archivo
    json.dumps(r)
