"""Un archivo subido por un extraño nunca cae el servidor: cada caso raro responde con una frase que dice qué pasó y qué hacer.

Se sube `subida_flota.csv` (el archivo de prueba de `flota`) en las formas en que puede llegar desde un computador
cualquiera. El calce no usa el modelo de lenguaje (sin clave), así la prueba no sale a internet.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from servicio.app import MAX_BYTES, app

FLOTA = (Path(__file__).resolve().parent.parent / "web" / "public" / "pruebas" / "subida_flota.csv").read_text(encoding="utf-8")
COLUMNAS = {"unidad": {"columnas": ["camion"]}, "tiempo": {"columnas": ["horas_operacion"]},
            "valor": {"columnas": ["hierro_ppm"], "transformacion": {"nombre": "dividir", "por": 120}},
            "covariables": {"columnas": ["exigencia_ruta"]}, "horizonte_por_unidad": {"columnas": ["horas_a_mantencion"]}}
EXCEL = FLOTA.replace(",", ";").replace(".", ",")          # como lo guarda Excel en español: punto y coma y coma decimal


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("KRYLOV_MOTOR_DESGASTE", "red")
    for clave in ("ANTHROPIC_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(clave, raising=False)
    return TestClient(app, raise_server_exceptions=False)


def _calce(cliente, contenido: bytes):
    return cliente.post("/api/calce", files={"archivo": ("a.csv", contenido, "text/csv")}, data={"motor_id": "desgaste", "caso": "flota"})


def _analizar(cliente, contenido: bytes, columnas: dict = COLUMNAS):
    return cliente.post("/api/analizar_archivo", files={"archivo": ("a.csv", contenido, "text/csv")},
                        data={"motor_id": "desgaste", "columnas": json.dumps(columnas)})


@pytest.mark.parametrize("contenido", [
    EXCEL.encode("utf-8"),
    EXCEL.replace("\n", ";\r\n").encode("cp1252"),           # con separador sobrante al final de cada fila y fin de línea de Windows
    b"\xef\xbb\xbf" + FLOTA.encode(),                         # UTF-8 con BOM
    FLOTA.encode("utf-16"),                                   # «texto Unicode» de Excel
    "\n".join(f + (",turno,nota" if i == 0 else f",A,fila {i}") for i, f in enumerate(FLOTA.strip().split("\n"))).encode(),
], ids=["excel_es", "excel_es_windows", "bom", "utf16", "columnas_de_mas"])
def test_formas_de_un_mismo_archivo_responden_igual(cliente, contenido):
    calce = _calce(cliente, contenido)
    assert calce.status_code == 200 and calce.json()["calce"]["unidad"]["columnas"] == ["camion"]
    assert calce.json()["propuesto_por"] == {"tipo": "regla", "proveedor": None, "modelo": None}
    r = _analizar(cliente, contenido)
    assert r.status_code == 200 and r.json()["semaforo"]["estado"] == "verde", r.json()["semaforo"]


def test_latin1_con_tildes_en_el_encabezado(cliente):
    contenido = FLOTA.replace("camion", "camión").encode("latin-1")
    assert _calce(cliente, contenido).json()["calce"]["unidad"]["columnas"] == ["camión"]
    assert _analizar(cliente, contenido, {**COLUMNAS, "unidad": {"columnas": ["camión"]}}).json()["semaforo"]["estado"] == "verde"


@pytest.mark.parametrize("contenido, dice", [
    (b"", "vacío"),
    (FLOTA.split("\n")[0].encode() + b"\n", "solo la fila de encabezados"),
    (b"PK\x03\x04" + bytes(range(256)) * 4, "Guardar como"),
    ((FLOTA + "CAEX-99,12\n").encode(), "La fila"),
], ids=["vacio", "solo_encabezado", "excel_xlsx", "fila_corta"])
def test_lo_que_no_se_lee_lo_dice(cliente, contenido, dice):
    calce = _calce(cliente, contenido)
    assert calce.status_code == 400 and calce.json()["codigo"] == "archivo_ilegible" and dice in calce.json()["error"]
    r = _analizar(cliente, contenido)
    assert r.status_code == 200 and r.json()["semaforo"]["estado"] == "rojo_datos" and dice in r.json()["semaforo"]["motivo"]


def test_un_archivo_de_6_mb_se_rechaza_con_su_motivo(cliente):
    filas = FLOTA.strip().split("\n")
    grande = (filas[0] + "\n" + "\n".join(filas[1:]) * (6 * 1024 * 1024 // len(FLOTA) + 1)).encode()
    assert len(grande) > MAX_BYTES
    for r in (_calce(cliente, grande), _analizar(cliente, grande)):
        assert r.status_code == 400 and r.json()["codigo"] == "archivo_grande" and "5 MB" in r.json()["error"]


def test_otra_escala_dice_que_hacer(cliente):
    # Sin dividir el hierro por 120, el desgaste llega a 100 cuando el camión falla en 1.
    r = _analizar(cliente, FLOTA.encode(), {**COLUMNAS, "valor": {"columnas": ["hierro_ppm"]}})
    assert r.status_code == 200
    semaforo = r.json()["semaforo"]
    assert semaforo["estado"] == "rojo_modelo" and "divídela" in semaforo["motivo"]


def test_una_celda_que_no_es_numero_se_nombra(cliente):
    r = _analizar(cliente, FLOTA.replace("7.2", "n/a", 1).encode())
    assert r.json()["semaforo"]["estado"] == "rojo_datos" and "«n/a»" in r.json()["semaforo"]["motivo"]


def test_una_peticion_incompleta_tiene_la_forma_del_contrato(cliente):
    r = cliente.post("/api/analizar_archivo", files={"archivo": ("a.csv", b"x", "text/csv")}, data={"columnas": "{}"})
    assert r.status_code == 400 and r.json()["codigo"] == "peticion_invalida" and "motor_id" in r.json()["error"]
