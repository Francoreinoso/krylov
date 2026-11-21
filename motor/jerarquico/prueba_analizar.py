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


@pytest.mark.skipif(simular.leer_real() is None, reason="datos/demo/inasistencias.csv no se versiona")
def test_tabla_subida_y_archivo_que_no_calza(artefactos, monkeypatch):
    """D-34: el motor lee `caso["tabla"]`; si falta un papel o hay valores que el modelo no conoce, rojo con su motivo."""
    from nucleo import jerarquico
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_JERARQUICO", "red")
    base = casos.cargar_caso("inasistencias")
    tabla = casos.leer_columnas(base["dataset"])
    subido = {k: v for k, v in base.items() if k not in ("dataset", "verdad")} | {"tabla": tabla}
    costos = {"falso_si": 15.0, "falso_no": 40.0}
    r, del_demo = jerarquico.analizar(subido, [], costos), jerarquico.analizar(base, [], costos)
    assert [u["p"] for u in r["unidades"]] == [u["p"] for u in del_demo["unidades"]] and r["examen"] is None
    assert {p["papel"] for p in jerarquico.PAPELES} <= set(base["columnas"])

    def semaforo(**cambios):
        return jerarquico.analizar(subido | cambios, [], costos)["semaforo"]
    col = base["columnas"]
    sin_espera = semaforo(columnas={k: v for k, v in col.items() if k != "suave"})
    assert sin_espera["estado"] == "rojo_datos" and "suave" in sin_espera["motivo"]
    # Papeles opcionales (D-35): sin recordatorio y con solo tres factores responde igual, con menos factores en «qué pesa».
    menos = jerarquico.analizar(subido | {"columnas": {k: v for k, v in col.items() if k != "tratamiento"} | {"efectos": col["efectos"][:3]}}, [], costos)
    assert menos["semaforo"] if "semaforo" in menos else True
    assert len(menos["unidades"]) == len(r["unidades"]) and len(menos["factores"]) == 4 and len(r["factores"]) == 7
    assert list(jerarquico.leer_caso(subido | {"columnas": col | {"efectos": col["efectos"][:3]}})["presentes"]) == [1, 1, 1, 1, 1, 0, 0]
    sabado = semaforo(tabla=tabla | {"dia_semana": ["5"] * len(tabla["dia_semana"])})
    assert sabado["estado"] == "rojo_modelo" and "dia_semana" in sabado["motivo"]
    grande = semaforo(tabla={k: v * 2 for k, v in tabla.items()})
    assert grande["estado"] == "rojo_modelo" and "3000" in grande["motivo"]
