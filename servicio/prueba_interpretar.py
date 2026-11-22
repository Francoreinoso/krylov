"""La interpretación no agrega números (regla 11): uno que no está en el JSON lleva a la plantilla."""

from servicio import interpretar
from servicio.lenguaje import Escrito

RESPUESTA = {
    "titular": "49 personas están en duda. No saber te cuesta cerca de 7 mil dólares.",
    "costo_de_no_saber": {"valor": 7420, "moneda": "USD"},
    "resumen_colores": {"actuar": 29, "no_actuar": 42, "en_duda": 49},
    "examen": {"tramos": [{"dijimos": 0.3, "paso": 0.283}]},
    "en_palabras": ["Lo que más pesa son las horas extra."],
}


def _con_texto(monkeypatch, texto):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: Escrito(texto, "claude", "claude-opus-5-5"))
    return interpretar.interpretar(RESPUESTA)


def test_numeros_del_json_pasan(monkeypatch):
    r = _con_texto(monkeypatch, "Hay 49 unidades en duda. Cuando dijimos 30%, pasó el 28%.")
    assert r["origen"] == "modelo" and r["proveedor"] == "claude"
    assert r["propuesto_por"] == {"tipo": "modelo", "proveedor": "Anthropic", "modelo": "claude-opus-5-5"}


def test_la_plata_no_va_en_el_texto(monkeypatch):
    """Los costos son supuestos del demo: el modelo no los lee, y un texto que los nombre sale como plantilla (D-42)."""
    r = _con_texto(monkeypatch, "Hay 49 unidades en duda y no saber cuesta US$ 7.420.")
    assert r == interpretar.plantilla(RESPUESTA)


def test_un_numero_inventado_lleva_a_la_plantilla(monkeypatch):
    r = _con_texto(monkeypatch, "Retener a las 29 personas ahorra US$ 12.500.")
    assert r == interpretar.plantilla(RESPUESTA)


def test_sin_modelo_sale_la_plantilla(monkeypatch):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: None)
    r = interpretar.interpretar(RESPUESTA)
    assert r["texto"] == "Lo que más pesa son las horas extra."
    assert r["propuesto_por"] == {"tipo": "plantilla", "proveedor": None, "modelo": None}


def test_solo_claude_descarta_el_modelo_de_prueba(monkeypatch):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: Escrito("Hay 49 personas en duda.", "groq", "openai/gpt-oss-120b"))
    assert interpretar.interpretar(RESPUESTA, solo_claude=True)["origen"] == "plantilla"


def test_groq_se_rotula_groq(monkeypatch):
    monkeypatch.setattr(interpretar.lenguaje, "pedir", lambda *a, **k: Escrito("Hay 49 personas en duda.", "groq", "openai/gpt-oss-120b"))
    assert interpretar.interpretar(RESPUESTA)["propuesto_por"] == {"tipo": "modelo", "proveedor": "Groq", "modelo": "openai/gpt-oss-120b"}
