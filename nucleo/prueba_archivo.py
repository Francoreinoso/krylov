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


def test_la_lista_cerrada_de_transformaciones():
    """D-35: las siete transformaciones que el calce puede nombrar. Textos entran, textos salen; una celda vacía sigue vacía."""
    from nucleo.preproceso import TRANSFORMACIONES as t
    assert set(t) == {"dividir", "anios_desde_fecha", "dias_entre", "si_no_a_binario", "reescalar_ordinal", "log", "categoria_a_codigo"}
    assert t["dividir"](["30", "", "6.0"], {}, por=12) == ["2.5", "", "0.5"]                                   # meses a años
    assert t["anios_desde_fecha"](["2020-06-30", "", "01/01/2026"], {}, hasta="2026-06-30") == ["6", "", "0.49"]
    assert t["anios_desde_fecha"](["2024-01-01", "2026-01-01"], {}) == ["2", "0"]                              # sin `hasta`: la fecha más reciente
    salida = {"salida": ["2025-12-31", ""]}                                                                    # `hasta` puede ser otra columna
    assert t["anios_desde_fecha"](["2020-06-30", "2024-01-01"], salida, hasta="salida") == ["5.5", "2"]
    agendo = {"agendo": ["2026-01-05", "05/01/2026", ""]}
    assert t["dias_entre"](["2026-01-15", "20/01/2026", "2026-02-01"], agendo, desde="agendo") == ["10", "15", ""]
    assert t["si_no_a_binario"](["Sí", "no", "", "TRUE", "0"], {}) == ["1", "0", "", "1", "0"]
    assert t["reescalar_ordinal"](["1", "2", "3", "4", "5", ""], {}, de=[1, 5], a=[1, 4]) == ["1", "2", "3", "3", "4", ""]
    assert t["log"](["1", ""], {}) == ["0", ""] and abs(float(t["log"](["10"], {})[0]) - 2.302585) < 1e-6
    assert t["categoria_a_codigo"](["norte", "sur", "", "centro", "sur"], {}) == ["1", "2", "", "0", "2"]
    for nombre, columna, parametros in (("dividir", ["x"], {"por": 2}), ("dividir", ["4"], {"por": 0}), ("log", ["0"], {}), ("si_no_a_binario", ["quizás"], {}),
                                        ("anios_desde_fecha", ["ayer"], {}), ("reescalar_ordinal", ["7"], {"de": [1, 5], "a": [1, 4]}),
                                        ("dias_entre", ["2026-01-01"], {"desde": "no_existe"})):
        with pytest.raises((ValueError, KeyError, ZeroDivisionError)):                                         # `analizar_archivo` lo vuelve rojo_datos
            t[nombre](columna, {}, **parametros)


def test_una_transformacion_que_falla_es_rojo_con_motivo():
    """`analizar_archivo` aplica la transformación antes de que el motor lea; si no se puede aplicar, `rojo_datos`."""
    tabla, col = _del_demo("terreno", "espacial")
    con = lambda **transformacion: {**col, "x": {"columnas": [col["x"]], "transformacion": transformacion}}   # noqa: E731
    assert _es_rojo(api.analizar_archivo("espacial", tabla, con(nombre="dividir", por=0)), "rojo_datos")
    assert _es_rojo(api.analizar_archivo("espacial", tabla, con(nombre="dividir")), "rojo_datos")              # falta el parámetro
    assert _es_rojo(api.analizar_archivo("espacial", tabla, con(nombre="anios_desde_fecha")), "rojo_datos")   # una coordenada no es una fecha
    assert _es_rojo(api.analizar_archivo("espacial", tabla, con(nombre="dias_entre", desde="no_existe")), "rojo_datos")
    en_negativo = {**col, "valor": {"columnas": [col["valor"]], "transformacion": {"nombre": "dividir", "por": -1000}}}
    assert _es_rojo(api.analizar_archivo("espacial", tabla, en_negativo), "rojo_modelo")                      # se aplicó: el zinc quedó negativo


def test_en_el_terreno_el_logaritmo_del_valor_lo_aplica_el_motor(monkeypatch):
    """El calce del demo nombra `log` para el zinc. No se aplica a la tabla (el motor lo haría otra vez y el umbral quedaría
    en otra escala): fija la transformación del caso. Con la red validada de `motor/artefactos/espacial/`."""
    from nucleo import casos
    if not (casos.ARTEFACTOS / "espacial" / "codificador.onnx").exists():
        pytest.skip("la red de espacial no está exportada en este computador")
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    tabla, col = _del_demo("terreno", "espacial")
    de_d34 = api.analizar_archivo("espacial", tabla, col)
    con_log = api.analizar_archivo("espacial", tabla, {papel: {"columnas": [nombre], "transformacion": {"nombre": "log"} if papel == "valor" else None}
                                                       for papel, nombre in col.items()})
    sin_log = api.analizar_archivo("espacial", tabla, {**col, "valor": {"columnas": [col["valor"]], "transformacion": None}})
    assert "error" not in de_d34 and de_d34["semaforo"]["estado"] != "rojo_modelo", de_d34
    assert con_log["mapa"] == de_d34["mapa"] and con_log["resumen_colores"] == de_d34["resumen_colores"]
    assert sin_log["mapa"] != de_d34["mapa"]                                                                   # sin logaritmo es otro análisis
