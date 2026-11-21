"""La interpretación no agrega números (regla 11): uno que no está en el JSON lleva a la plantilla."""

from servicio import interpretar

RESPUESTA = {
    "titular": "49 personas están en duda. No saber te cuesta cerca de 7 mil dólares.",
    "costo_de_no_saber": {"valor": 7420, "moneda": "USD"},
    "resumen_colores": {"actuar": 29, "no_actuar": 42, "en_duda": 49},
    "examen": {"tramos": [{"dijimos": 0.3, "paso": 0.283}]},
    "en_palabras": ["Lo que más pesa son las horas extra."],
}


def _con_texto(monkeypatch, texto):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: (texto, "claude"))
    return interpretar.interpretar(RESPUESTA)


def test_numeros_del_json_pasan(monkeypatch):
    r = _con_texto(monkeypatch, "Hay 49 personas en duda y no saber cuesta US$ 7.420, cerca de 7 mil. Cuando dijimos 30%, pasó el 28%.")
    assert r["origen"] == "modelo" and r["proveedor"] == "claude"


def test_un_numero_inventado_lleva_a_la_plantilla(monkeypatch):
    r = _con_texto(monkeypatch, "Retener a las 29 personas ahorra US$ 12.500.")
    assert r == interpretar.plantilla(RESPUESTA)


def test_sin_modelo_sale_la_plantilla(monkeypatch):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: None)
    assert interpretar.interpretar(RESPUESTA)["texto"] == "Lo que más pesa son las horas extra."


def test_solo_claude_descarta_el_modelo_de_prueba(monkeypatch):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: ("Hay 49 personas en duda.", "groq"))
    assert interpretar.interpretar(RESPUESTA, solo_claude=True)["origen"] == "plantilla"
