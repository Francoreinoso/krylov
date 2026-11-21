"""«Responde la red» solo si el sello del motor pasa (AGENTS.md, regla 5): si no, sale el ejemplo fijo, con `_aviso`."""

from servicio import respuestas


def _leyes(monkeypatch, sello):
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    monkeypatch.setattr(respuestas.nucleo, "sello", lambda motor_id: sello)
    return respuestas.analizar("leyes")


def test_con_sello_que_pasa_responde_la_red(monkeypatch):
    r = _leyes(monkeypatch, {"motor_id": "espacial", "pasa": True})
    assert r["implementacion"] == "red" and "_aviso" not in r


def test_con_sello_que_no_pasa_sale_el_ejemplo(monkeypatch):
    assert "_aviso" in _leyes(monkeypatch, {"motor_id": "espacial", "pasa": False})


def test_rojo_datos_sale_aunque_el_sello_no_pase(monkeypatch):
    # El archivo que no alcanza se rechaza antes de la red: el sello no cambia lo que se dice.
    monkeypatch.setenv("KRYLOV_MOTOR_ESPACIAL", "red")
    monkeypatch.setattr(respuestas.nucleo, "sello", lambda motor_id: {"motor_id": "espacial", "pasa": False})
    r = respuestas.analizar("leyes_pocos")
    assert "_aviso" not in r and r["semaforo"]["estado"] == "rojo_datos"
