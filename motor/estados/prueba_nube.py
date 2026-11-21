"""La nube de crédito de punta a punta, con la red sin entrenar: mecánica y forma (los valores no significan nada)."""

import json
from pathlib import Path

import torch

from motor.estados import nube
from motor.estados.exportar import configuracion, exportar
from motor.estados.red import RedEstados
from nucleo import api, casos

EJEMPLO = Path(__file__).resolve().parents[2] / "contratos" / "ejemplos" / "nube.json"


def test_nube_de_credito(tmp_path, monkeypatch):
    monkeypatch.setattr(casos, "ARTEFACTOS", tmp_path)
    assert api.nube("credito")["codigo"] == "no_disponible"                  # sin nube.npz no se inventa nada
    torch.manual_seed(0)
    exportar(RedEstados(), tmp_path / "estados", configuracion())
    resumen = nube.generar(tmp_path / "estados", simulaciones=40, por_lote=20)
    assert resumen["n_simulaciones"] == 40 and resumen["clientes_por_cartera"] == 2000 and 0.5 <= resumen["x_maximo"] <= 1
    r = api.nube("credito")
    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(r) == {k for k in ejemplo if not k.startswith("_")} and r["caso"] == "credito" and r["n_simulaciones"] == 40
    assert len(r["puntos"]) == 40 and all(0.5 <= x <= 1 and 0 <= y <= 1 for x, y in r["puntos"])
    assert set(r["detectores"]) == set(ejemplo["detectores"]) and r["detectores"]["resumenes_aprendidos"]["distancia"] > 0
    assert 0.5 <= r["archivo"]["x"] <= 1 and abs(r["archivo"]["y"] - 0.233) < 0.01      # la proporción de impago del archivo
    json.dumps(r)
