"""`api.papeles` y `api.analizar_archivo` (D-34, D-35): los papeles de los cuatro motores y un archivo que no calza por motor.

Nada de aquí necesita una red: un archivo que no calza se responde antes de llegar a ella. Que un archivo que sí
calza responda igual que el del demo lo prueba cada motor con su red sin entrenar (`motor/<id>/prueba_analizar.py`).
No se compara la redacción de los motivos, solo que existan.
"""

import json
from pathlib import Path

import pytest

from nucleo import api
from nucleo.casos import MOTORES, cargar_caso, leer_columnas

ROJO = json.loads((Path(__file__).resolve().parent.parent / "contratos" / "ejemplos" / "analizar_rojo.json").read_text(encoding="utf-8"))


def _es_rojo(r: dict, estado: str) -> bool:
    """Semáforo rojo con motivo, sin unidades, con todas las claves de una respuesta de `analizar` y convertible a JSON."""
    assert "error" not in r, r
    assert set(ROJO) - {"_aviso"} <= set(r), set(ROJO) - set(r)
    assert r["semaforo"]["estado"] == estado and r["semaforo"]["motivo"] and r["titular"], r["semaforo"]
    assert r["unidades"] is None and r["factores"] is None and r["costo_de_no_saber"] is None and r["examen"] is None
    json.dumps(r)
    return True


def _del_demo(caso: str, motor_id: str) -> tuple[dict, dict]:
    """La tabla del archivo del demo y sus columnas por papel, como las mandaría el chat."""
    c = cargar_caso(caso)
    return leer_columnas(c["dataset"]), {p["papel"]: c["columnas"][p["papel"]] for p in api.papeles(motor_id)["papeles"]}


def test_papeles_de_los_cuatro_motores():
    for motor_id in MOTORES:
        r = api.papeles(motor_id)
        assert r["motor_id"] == motor_id and cargar_caso(r["caso_base"])["motor"] == motor_id
        for p in r["papeles"]:
            assert list(p) == ["papel", "cantidad", "minimo", "maximo", "tipo", "texto", "texto_largo"]
            assert 0 <= p["minimo"] <= p["maximo"] == p["cantidad"] and p["tipo"] in ("texto", "si_no", "entero", "numero")
            assert p["texto"] and p["texto_largo"]
        json.dumps(r)
    cantidades = lambda motor_id: {p["papel"]: (p["minimo"], p["maximo"]) for p in api.papeles(motor_id)["papeles"]}   # noqa: E731
    assert cantidades("supervivencia") == {"id": (1, 1), "evento": (1, 1), "tiempo": (1, 1), "grupo": (1, 1), "efectos": (3, 3), "suave": (1, 1), "encuestas": (4, 4)}
    assert cantidades("espacial") == {"x": (1, 1), "y": (1, 1), "valor": (1, 1)}
    assert cantidades("estados")["transiciones"] == (0, 3) and cantidades("jerarquico")["efectos"] == (0, 5)   # papeles opcionales (D-35)
    assert api.papeles("regresion")["codigo"] == "motor_desconocido"
    assert api.analizar_archivo("regresion", {"a": ["1"]}, {})["codigo"] == "motor_desconocido"


def test_rotacion_archivo_que_no_calza():
    tabla = leer_columnas("datos/demo/subida_rotacion_ventas.csv")
    col = {"id": "n_empleado", "evento": "renuncio", "tiempo": "anios_en_empresa", "grupo": "cargo", "suave": "sueldo_mensual",
           "efectos": ["horas_extra", "distancia_km", "empresas_previas"], "encuestas": ["enc_ambiente", "enc_trabajo", "enc_relaciones", "enc_equilibrio"]}
    def responder(tabla=tabla, **cambios):
        return api.analizar_archivo("supervivencia", tabla, {**col, **cambios})
    assert _es_rojo(responder(tiempo=None), "rojo_datos")                                    # falta un papel
    assert _es_rojo(responder(suave="no_existe"), "rojo_datos")                              # la columna no está en el archivo
    assert _es_rojo(responder(suave="area"), "rojo_datos")                                   # texto donde va un número
    assert _es_rojo(responder(efectos=col["efectos"][:2]), "rojo_modelo")                    # esquema fijo: la red practicó con tres factores
    assert _es_rojo(responder(encuestas=col["encuestas"] + ["edad"]), "rojo_modelo")
    assert _es_rojo(responder({**tabla, "enc_trabajo": ["5"] * len(tabla["cargo"])}), "rojo_modelo")   # una encuesta de 1 a 5
    assert _es_rojo(responder({**tabla, "sueldo_mensual": ["0"] * len(tabla["cargo"])}), "rojo_modelo")
    # D-35: la forma con transformación se acepta; una transformación que no está en la lista cerrada es rojo_datos con motivo.
    assert _es_rojo(responder(tiempo={"columnas": ["anios_en_empresa"], "transformacion": {"nombre": "elevar_al_cubo"}}), "rojo_datos")
    assert _es_rojo(api.analizar_archivo("supervivencia", b"", col), "rojo_datos")           # un archivo vacío
    assert _es_rojo(api.analizar_archivo("supervivencia", b"a,b\n1,2,3\n", col), "rojo_datos")   # no se lee como tabla
    assert _es_rojo(api.analizar_archivo("supervivencia", 7, col), "rojo_datos")
    assert api.analizar_archivo("supervivencia", tabla, col, {"falso_si": -1})["codigo"] == "costos_invalidos"


def test_rrhh_tiene_pocas_personas():
    """El área de RR. HH. del archivo público (63 personas) calza con los papeles, pero no alcanza: «faltan datos»."""
    col = {"id": "n_empleado", "evento": "renuncio", "tiempo": "anios_en_empresa", "grupo": "cargo", "suave": "sueldo_mensual",
           "efectos": ["horas_extra", "distancia_km", "empresas_previas"], "encuestas": ["enc_ambiente", "enc_trabajo", "enc_relaciones", "enc_equilibrio"]}
    crudo = (Path(__file__).resolve().parent.parent / "datos" / "demo" / "subida_rotacion_rrhh.csv").read_bytes()
    assert _es_rojo(api.analizar_archivo("supervivencia", crudo, col), "rojo_datos")         # el CSV tal como llega del navegador


def test_credito_archivo_que_no_calza():
    tabla, col = _del_demo("credito", "estados")
    assert _es_rojo(api.analizar_archivo("estados", tabla, {**col, "atraso": col["atraso"][:5]}), "rojo_modelo")    # cinco meses de historial
    assert _es_rojo(api.analizar_archivo("estados", {**tabla, "PAY_0": ["11"] * len(tabla["ID"])}, col), "rojo_modelo")
    assert _es_rojo(api.analizar_archivo("estados", tabla, {**col, "cupo": None}), "rojo_datos")


def test_terreno_archivo_que_no_calza():
    tabla, col = _del_demo("terreno", "espacial")
    assert set(col) == {"x", "y", "valor"}
    negativo = api.analizar_archivo("espacial", {**tabla, col["valor"]: ["-1"] * len(tabla["x"])}, col)   # el valor se lee en logaritmo
    assert _es_rojo(negativo, "rojo_modelo") and negativo["mapa"] is None
    assert _es_rojo(api.analizar_archivo("espacial", {k: v[:10] for k, v in tabla.items()}, col), "rojo_datos")   # diez mediciones
    assert _es_rojo(api.analizar_archivo("espacial", tabla, {"x": "x", "valor": col["valor"]}), "rojo_datos")


def test_inasistencias_archivo_que_no_calza():
    """Con una tabla inventada aquí: el archivo de inasistencias no se versiona (licencia no comercial)."""
    n = 300
    tabla = {"cita": [str(i) for i in range(n)], "falto": ["1" if i % 5 == 0 else "0" for i in range(n)], "persona": [str(i // 2) for i in range(n)],
             "sede": [str(i % 7) for i in range(n)], "espera": [str(i % 30) for i in range(n)]}
    col = {"id": "cita", "objetivo": "falto", "paciente": "persona", "grupo": "sede", "suave": "espera"}
    assert _es_rojo(api.analizar_archivo("jerarquico", tabla, {**col, "paciente": None}), "rojo_datos")
    assert _es_rojo(api.analizar_archivo("jerarquico", {**tabla, "espera": ["mucho"] * n}, col), "rojo_datos")
    assert _es_rojo(api.analizar_archivo("jerarquico", {**tabla, "sede": [str(i % 60) for i in range(n)]}, col), "rojo_modelo")   # 60 grupos
    assert _es_rojo(api.analizar_archivo("jerarquico", tabla, {**col, "efectos": ["espera"] * 6}), "rojo_modelo")


def test_transformacion_de_la_lista_cerrada(monkeypatch):
    """Las transformaciones viven en `nucleo/preproceso.py`; `analizar_archivo` solo las llama por nombre, antes de leer."""
    from nucleo import preproceso
    tabla, col = _del_demo("terreno", "espacial")
    llamadas = []
    def dividir(valores, tabla, por):
        llamadas.append(por)
        return [float(v) / por for v in valores]
    monkeypatch.setattr(preproceso, "TRANSFORMACIONES", {"dividir": dividir}, raising=False)
    en_miles = {**col, "valor": {"columnas": [col["valor"]], "transformacion": {"nombre": "dividir", "por": -1000}}}
    assert _es_rojo(api.analizar_archivo("espacial", tabla, en_miles), "rojo_modelo") and llamadas == [-1000]   # el zinc quedó negativo
    assert _es_rojo(api.analizar_archivo("espacial", tabla, {**col, "valor": {"columnas": [col["valor"]], "transformacion": {"nombre": "dividir", "por": 0}}}), "rojo_datos")
