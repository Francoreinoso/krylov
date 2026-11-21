"""La nube: el AUC por rangos, los dos detectores y la forma del contrato."""

import json
from pathlib import Path

import numpy as np

from nucleo import nube

EJEMPLO = Path(__file__).resolve().parent.parent / "contratos" / "ejemplos" / "nube.json"


def _auc_directo(factor, respuesta):
    """Definición: probabilidad de que un «sí» al azar tenga el factor mayor que un «no» al azar (empates a medias)."""
    si, no = factor[respuesta], factor[~respuesta]
    area = ((si[:, None] > no[None, :]).mean() + 0.5 * (si[:, None] == no[None, :]).mean())
    return max(area, 1 - area)


def test_auc_por_rangos_igual_a_la_definicion():
    rng = np.random.default_rng(0)
    for _ in range(5):
        respuesta = rng.random(300) < 0.2
        factor = np.round(rng.normal(0, 1, 300) + 0.8 * respuesta, 1)             # con empates
        assert abs(nube.auc(factor, respuesta) - _auc_directo(factor, respuesta)) < 1e-12
    assert nube.auc(respuesta.astype(float), respuesta) == 1.0                      # una columna que delata la respuesta
    assert nube.auc(-respuesta.astype(float), respuesta) == 1.0                     # da lo mismo el sentido
    assert nube.auc(np.ones(10), np.zeros(10, dtype=bool)) == 0.5


def _nube_simulada(rng, n=2000, d=16):
    ejes = np.c_[0.5 + np.abs(rng.normal(0.12, 0.06, n)).clip(0, 0.4), rng.beta(3, 12, n)]
    return nube.resumir_simulaciones(ejes, rng.normal(0, 1, (n, d))), d


def test_archivo_que_delata_la_respuesta_cae_fuera_y_corregido_dentro():
    rng = np.random.default_rng(1)
    simulada, d = _nube_simulada(rng)
    respuesta = (rng.random(400) < 0.16).astype(float)
    respuesta[rng.random(400) < 0.2] = np.nan                                       # 20% por decidir
    factores = {"horas_extra": rng.normal(0, 1, 400) + 0.5 * np.nan_to_num(respuesta), "fecha_salida": np.nan_to_num(respuesta)}

    x, y, mejor = nube.ejes_con_nombre(factores, respuesta)
    malo = nube.ubicar(simulada, x, y, mejor, np.zeros(d))             # resumen en el centro: el segundo detector no marca
    assert mejor == "fecha_salida" and x == 1.0
    assert malo["archivo"]["dentro"] is False and malo["detectores"]["ejes_con_nombre"]["dentro"] is False
    assert "fecha_salida" in malo["detectores"]["ejes_con_nombre"]["motivo"]

    factores.pop("fecha_salida")                                                    # la corrección: quitar el factor
    x, y, mejor = nube.ejes_con_nombre(factores, respuesta)
    bueno = nube.ubicar(simulada, x, y, mejor, np.zeros(d))
    assert bueno["archivo"]["dentro"] is True and bueno["detectores"]["ejes_con_nombre"]["motivo"] == ""


def test_segundo_detector_y_forma_del_contrato():
    rng = np.random.default_rng(2)
    simulada, d = _nube_simulada(rng)
    raro = nube.ubicar(simulada, 0.62, 0.2, "x", np.full(d, 6.0))                   # dentro en los ejes, lejos en los resúmenes
    assert raro["detectores"]["ejes_con_nombre"]["dentro"] and not raro["detectores"]["resumenes_aprendidos"]["dentro"]
    assert raro["archivo"]["dentro"] is False
    # Cerca de 1% de las propias simulaciones queda sobre el límite (es el percentil 99).
    distancias = nube.mahalanobis(rng.normal(0, 1, (4000, d)), simulada["media"], simulada["precision"])
    assert 0.002 < (distancias > simulada["limite"]).mean() < 0.03

    ejemplo = json.loads(EJEMPLO.read_text(encoding="utf-8"))
    assert set(raro) == set(ejemplo) - {"_aviso", "caso"}
    assert set(raro["detectores"]["resumenes_aprendidos"]) == set(ejemplo["detectores"]["resumenes_aprendidos"])
    assert raro["ejes"] == ejemplo["ejes"] and len(raro["puntos"]) == 2000 and raro["n_simulaciones"] == 2000
    json.dumps(raro)
