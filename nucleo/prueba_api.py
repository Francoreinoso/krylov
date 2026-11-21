"""`nucleo/api.py`: las tarjetas, la elección de implementación y lo común de `analizar`."""

import json
import sys
import types
from pathlib import Path

import pytest

from nucleo import api
from nucleo.casos import bloque_costos, cargar_caso, costos_numericos, en_plata, implementacion

EJEMPLOS = Path(__file__).resolve().parent.parent / "contratos" / "ejemplos"


def test_casos_con_la_forma_del_ejemplo_y_el_orden_del_inicio():
    ejemplo = json.loads((EJEMPLOS / "casos.json").read_text(encoding="utf-8"))["casos"]
    tarjetas = api.casos()["casos"]
    assert [t["nombre"] for t in tarjetas] == ["rotacion", "terreno", "inasistencias", "credito"]
    assert all(set(t) == set(ejemplo[0]) for t in tarjetas)
    assert {t["nombre"]: t["motor"] for t in tarjetas} == {e["nombre"]: e["motor"] for e in ejemplo}


def test_implementacion_por_variable_de_entorno(monkeypatch):
    monkeypatch.delenv("KRYLOV_MOTOR_ESPACIAL", raising=False)
    assert implementacion("espacial") == "mcmc"                  # por defecto, el plan B
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    assert implementacion("espacial") == "red"
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "cualquier cosa")
    assert implementacion("espacial") == "mcmc"


def test_costos_del_caso_y_del_usuario():
    caso = cargar_caso("rotacion")
    assert costos_numericos(caso, None) == {"falso_si": 1500.0, "falso_no": 6000.0}
    movidos = costos_numericos(caso, {"falso_si": 500, "falso_no": {"valor": 9000}})
    assert movidos == {"falso_si": 500.0, "falso_no": 9000.0}
    assert bloque_costos(caso, movidos)["falso_si"] == {"valor": 500, "min": 200, "max": 5000, "etiqueta": "Costo de un plan de retención"}
    assert en_plata(18400, "USD") == "18 mil dólares" and en_plata(2656390, "USD") == "2,7 millones de dólares"


def test_errores_en_espanol_y_sin_traza():
    assert api.analizar("no_existe")["codigo"] == "caso_desconocido"
    assert api.analizar("../secreto")["codigo"] == "caso_desconocido"
    assert api.donde_medir("rotacion")["codigo"] == "sin_mapa"
    assert api.sello("no_es_un_motor")["codigo"] == "sin_sello"
    assert api.analizar("rotacion", costos={"falso_si": 0})["codigo"] == "costos_invalidos"


@pytest.fixture
def motor_de_juguete(monkeypatch):
    """Un motor `estados` falso, para probar lo que agrega `api.analizar` sin depender de ningún motor real."""
    modulo = types.ModuleType("nucleo.estados")
    def analizar(caso, transformaciones, costos):
        from nucleo import decision
        r = decision.decidir_tabla([[0.1] * 32, [0.05] * 16 + [0.6] * 16, [0.9] * 32], costos["falso_si"], costos["falso_no"])
        unidades = [{"id": str(i), "etiqueta": str(i), "p": float(r["p"][i]), "muestras_p": [], "estado": str(r["estado"][i]),
                     "duda": float(r["duda"][i])} for i in range(3)]
        return {"unidades": unidades, "factores": [], "implementacion": "mcmc", "registro": ["3 clientes"]}
    modulo.analizar = analizar
    monkeypatch.setitem(sys.modules, "nucleo.estados", modulo)


def test_analizar_agrega_lo_comun(motor_de_juguete):
    r = api.analizar("credito")
    ejemplo = json.loads((EJEMPLOS / "analizar_tabla.json").read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(r), set(ejemplo) - set(r)
    assert r["motor_id"] == "estados" and r["implementacion"] == "mcmc" and r["precalculado"] is True
    assert r["resumen_colores"] == {"actuar": 1, "no_actuar": 1, "en_duda": 1}
    assert r["costo_de_no_saber"]["valor"] == round(sum(u["duda"] for u in r["unidades"])) > 0
    assert r["titular"].startswith("1 cliente está en duda. No saber te cuesta cerca de ")
    assert 0 < r["punto_de_corte"] < 1 and "costo_total" not in r and isinstance(r["tiempo_ms"], int)
    json.dumps(r)                                                 # listo para JSON


def test_sello_con_frases(tmp_path, monkeypatch):
    from nucleo import casos
    (tmp_path / "espacial").mkdir()
    ejemplo = json.loads((EJEMPLOS / "sello.json").read_text(encoding="utf-8"))
    ejemplo.pop("frases")
    ejemplo["cobertura_90_peor_grupo"] = None                               # un campo sin medir no genera frase
    (tmp_path / "espacial" / "sello.json").write_text(json.dumps(ejemplo), encoding="utf-8")
    monkeypatch.setattr(api, "ARTEFACTOS", tmp_path)
    ficha = api.sello("espacial")
    assert ficha["frases"] == ["Practicó con 12,0 millones de casos simulados.",
                               "Cuando da un rango de 90%, acierta 90,3% en casos simulados nuevos. El método rápido de siempre acierta 74,0%.",
                               "Para rehacer 480 análisis completos para «¿Dónde mido?», el método lento de siempre tarda 360 minutos; Krylov, 0,9 segundos."]
