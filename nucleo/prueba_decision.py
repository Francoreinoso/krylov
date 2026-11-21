"""La regla de decisión da lo mismo que `contratos/ejemplos/decision_prueba.json` (la prueba común con TypeScript)."""

import json
from pathlib import Path

import numpy as np

from nucleo import decision

EJEMPLO = Path(__file__).resolve().parent.parent / "contratos" / "ejemplos" / "decision_prueba.json"


def test_decision_igual_al_contrato():
    datos = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    tolerancia, vistos = datos["tolerancia"], set()
    for caso in datos["casos"]:
        espera = caso["espera"]
        if caso["regla"] == "tabla":
            r = decision.decidir_tabla([caso["muestras_p"]], caso["c_si"], caso["c_no"])
            assert abs(r["p"][0] - espera["p"]) <= tolerancia
            estado, duda = r["estado"][0], r["duda"][0]
        else:
            r = decision.decidir_espacial(caso["p"], caso["c_si"], caso["c_no"])
            estado, duda = str(r["estado"]), float(r["duda"])
        assert estado == espera["estado"], caso
        assert abs(duda - espera["duda"]) <= tolerancia, caso
        vistos.add((caso["regla"], estado))
    assert len(datos["casos"]) == 45 and len(vistos) == 6        # las dos reglas, los tres colores


def test_vectorizado_y_sin_duda_negativa():
    rng = np.random.default_rng(0)
    muestras = rng.beta(2, 5, size=(500, 32))
    r = decision.decidir_tabla(muestras, 1500, 6000)
    assert r["p"].shape == r["estado"].shape == r["duda"].shape == (500,) and (r["duda"] >= 0).all()
    assert sum(decision.resumen_colores(r["estado"]).values()) == 500
    # Sin incertidumbre sobre p no hay nada que averiguar: la duda vale cero.
    assert np.allclose(decision.decidir_tabla(np.full((3, 32), 0.3), 1500, 6000)["duda"], 0)
    mapa = decision.decidir_espacial(rng.random((32, 32)), 20000, 50000)
    assert mapa["estado"].shape == (32, 32)


def test_certeza():
    assert decision.certeza(np.r_[np.ones(96), -np.ones(4)]) == "seguro"
    assert decision.certeza(np.r_[np.ones(85), -np.ones(15)]) == "probable"
    assert decision.certeza(np.r_[np.ones(60), -np.ones(40)]) == "no_se_sabe"
    assert decision.factor("x", "X", [-1.0, -2.0, -3.0])["direccion"] == "baja"
