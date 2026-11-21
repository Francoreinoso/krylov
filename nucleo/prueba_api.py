"""`nucleo/api.py`: las tarjetas, la elección de implementación y lo común de `analizar`."""

import json
import sys
import types
from pathlib import Path

import pytest

from nucleo import api
from nucleo import textos
from nucleo.casos import bloque_costos, cargar_caso, costos_numericos, implementacion

EJEMPLOS = Path(__file__).resolve().parent.parent / "contratos" / "ejemplos"


def test_casos_con_la_forma_del_ejemplo_y_el_orden_del_inicio():
    ejemplo = json.loads((EJEMPLOS / "casos.json").read_text(encoding="utf-8"))["casos"]
    tarjetas = api.casos()["casos"]
    assert [t["nombre"] for t in tarjetas] == ["leyes", "taludes", "flotacion", "flota", "sismicidad"]
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
    assert "18 mil" in textos.plata(18400) and "2,7 millones" in textos.plata(2656390) and "850" in textos.plata(850)
    assert textos.plata(0.2) == textos.frase("formato_plata.cero")


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
    assert r["unidad"] == {"singular": "cliente", "plural": "clientes"}                # pedido de PC 1 (campo nuevo, aprobado por Rodrigo)
    assert r["resumen_colores"] == {"actuar": 1, "no_actuar": 1, "en_duda": 1}
    assert r["costo_de_no_saber"]["valor"] == round(sum(u["duda"] for u in r["unidades"])) > 0
    assert r["titular"] and "1 cliente" in r["titular"]
    assert len(r["en_palabras"]) == 2 and all("client" in f for f in r["en_palabras"])     # una frase por color presente
    assert 0 < r["punto_de_corte"] < 1 and "costo_total" not in r and isinstance(r["tiempo_ms"], int)
    json.dumps(r)                                                 # listo para JSON


def test_sello_con_frases(tmp_path, monkeypatch):
    from nucleo import casos
    (tmp_path / "espacial").mkdir()
    ejemplo = json.loads((EJEMPLOS / "sello.json").read_text(encoding="utf-8"))
    ejemplo.pop("frases")
    ejemplo["cobertura_90_peor_grupo"] = None                               # un campo sin medir no genera frase
    (tmp_path / "espacial" / "sello.json").write_text(json.dumps(ejemplo), encoding="utf-8")
    monkeypatch.setattr(casos, "ARTEFACTOS", tmp_path)
    ficha = api.sello("espacial")
    assert len(ficha["frases"]) == 2 and "12,0 millones" in ficha["frases"][0] and "90,3%" in ficha["frases"][1]
    ejemplo.update(cobertura_90_peor_grupo=0.871, mcmc_s_por_dataset=300.0)
    con_todo = textos.sello(ejemplo)
    assert len(con_todo) == 4 and "87,1%" in con_todo[2] and "5 minutos" in con_todo[3] and "60 milisegundos" in con_todo[3]


def test_textos_sin_numero_no_hay_frase():
    assert textos.frase("examen.espacial", n=31, k=None) is None and textos.frase("no.existe") is None
    caso = cargar_caso("rotacion")
    bloque = {"tipo": "datos_reales_reservados", "n": 294, "tramos": [{"dijimos": 0.05, "paso": 0.04, "n": 110}, {"dijimos": 0.3, "paso": 0.28, "n": 158}]}
    del_examen = textos.examen(caso, bloque)                     # el texto es de PC 3 (casos/textos.yaml); aquí importan los números
    assert "30%" in del_examen and "28%" in del_examen and "se fue" in del_examen
    assert textos.examen(caso, None) is None
    assert textos.titular(caso, {"estado": "rojo_datos"}, None, None) == textos.frase("titular.rojo_datos")
    sin_duda = textos.titular(caso, {"estado": "verde"}, {"actuar": 3, "no_actuar": 9, "en_duda": 0}, 0.0)
    assert sin_duda and "en duda" not in sin_duda.split(".")[0].replace("Ninguna duda", "")


def test_en_palabras_usa_la_variante_en_singular():
    caso = cargar_caso("credito")
    varias = textos.en_palabras(caso, {"actuar": 3, "no_actuar": 5, "en_duda": 2}, [])
    una = textos.en_palabras(caso, {"actuar": 1, "no_actuar": 5, "en_duda": 1}, [])
    assert len(varias) == len(una) == 2 and all(" 1 cliente" in f and "clientes" not in f for f in una)
    assert "3 clientes" in varias[0] and "2 clientes" in varias[1]
