"""`analizar` de inasistencias de punta a punta, con la red sin entrenar y con muestras «de MCMC» inventadas.

Prueba la forma de la respuesta y la mecánica (lectura, forma anidada, onnxruntime, flujo en NumPy,
cuadratura, decisión, examen). Los valores no significan nada: la red no está entrenada.
El archivo real no se versiona (CC BY-NC-SA): si no está en `datos/demo/`, la prueba se salta.
"""

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from motor.jerarquico import simular
from motor.jerarquico.exportar import configuracion, exportar
from motor.jerarquico.red import RedJerarquico
from nucleo import api, casos

RAIZ = Path(__file__).resolve().parents[2]
EJEMPLO = RAIZ / "contratos" / "ejemplos" / "analizar_tabla.json"
pytestmark = pytest.mark.skipif(not (RAIZ / "datos" / "demo" / "inasistencias.csv").exists(),
                                reason="datos/demo/inasistencias.csv no se versiona; se genera con datos/preparar/inasistencias.py")


@pytest.fixture(scope="module")
def artefactos(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp("artefactos")
    torch.manual_seed(0)
    exportar(RedJerarquico(), carpeta / "jerarquico", configuracion())
    (carpeta / "jerarquico" / "mcmc").mkdir()
    np.savez(carpeta / "jerarquico" / "mcmc" / "inasistencias.npz", theta=simular.muestrear_prior(np.random.default_rng(0), 200))
    return carpeta


@pytest.mark.parametrize("impl", ["red", "mcmc"])
def test_analizar_inasistencias(artefactos, monkeypatch, impl):
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_JERARQUICO", impl)
    r = api.analizar("inasistencias")
    assert "error" not in r, r
    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(r), set(ejemplo) - set(r)
    assert r["motor_id"] == "jerarquico" and r["implementacion"] == impl and r["precalculado"] is (impl == "mcmc")
    assert len(r["unidades"]) == 396 and set(r["unidades"][0]) == set(ejemplo["unidades"][0])
    assert all(len(u["muestras_p"]) == 32 and 0 <= u["p"] <= 1 for u in r["unidades"])
    assert sum(r["resumen_colores"].values()) == 396 and r["costo_de_no_saber"]["valor"] >= 0
    assert len(r["factores"]) == 7 and {"dias_de_espera", "SMS_received", "Age"} <= {f["nombre"] for f in r["factores"]}
    assert r["examen"]["tipo"] == "datos_reales_reservados" and r["examen"]["n"] == 396
    assert r["registro"][:3] == ["396 citas por decidir", "1147 pacientes", "30 barrios"]
    json.dumps(r)
    assert api.analizar("inasistencias")["unidades"] == r["unidades"]                # semilla fija
    assert api.analizar("inasistencias", transformaciones=["quitar_factor:Age"])["codigo"] == "no_disponible"
