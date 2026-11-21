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


def test_tabla_subida_con_otros_nombres_y_archivo_que_no_calza(artefactos, monkeypatch):
    """D-34: el motor lee `caso["tabla"]` con las columnas que asignó el usuario; si no calza, rojo con su motivo."""
    from nucleo import estados
    monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
    monkeypatch.setenv("KRYLOV_MOTOR_ESTADOS", "red")
    base = casos.cargar_caso("credito")
    original = casos.leer_columnas(base["dataset"])
    tabla = {f"col_{nombre.lower()}": valores for nombre, valores in original.items()}          # mismo esquema, otros nombres
    renombrar = lambda v: [f"col_{n.lower()}" for n in v] if isinstance(v, list) else f"col_{v.lower()}"   # noqa: E731
    columnas = {papel: renombrar(base["columnas"][papel]) for papel in ("id", "objetivo", "atraso", "saldo", "pago", "cupo", "transiciones")}
    subido = {k: v for k, v in base.items() if k not in ("dataset", "verdad")} | {"tabla": tabla, "columnas": columnas}
    costos = {"falso_si": 800.0, "falso_no": 2500.0}
    r = estados.analizar(subido, [], costos)
    del_demo = estados.analizar(base, [], costos)
    assert [u["p"] for u in r["unidades"]] == [u["p"] for u in del_demo["unidades"]] and r["examen"] is None
    assert [p["papel"] for p in estados.PAPELES] == list(columnas) and sum(p["cantidad"] for p in estados.PAPELES) == 24

    def semaforo(**cambios):
        return estados.analizar(subido | cambios, [], costos)["semaforo"]
    falta = semaforo(columnas=columnas | {"atraso": columnas["atraso"][:5]})
    assert falta["estado"] == "rojo_datos" and "6 columnas" in falta["motivo"]
    assert "col_nada" in semaforo(columnas=columnas | {"cupo": "col_nada"})["motivo"]
    texto = semaforo(tabla=tabla | {"col_age": ["joven"] * 2000})
    assert texto["estado"] == "rojo_datos" and "col_age" in texto["motivo"]
    raro = semaforo(tabla=tabla | {"col_pay_0": ["15"] * 2000})
    assert raro["estado"] == "rojo_modelo" and "col_pay_0" in raro["motivo"]
