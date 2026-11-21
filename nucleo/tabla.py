"""Lo común a los tres motores de tabla al armar la respuesta de `analizar`: unidades, examen y lectura de la verdad.

Cada motor entrega `muestras_p`: por unidad por decidir, una probabilidad por cada muestra
del posterior de θ, ya pasada por su paso local exacto. De ahí en adelante todo es igual.
"""

from __future__ import annotations

import numpy as np

from nucleo import decision
from nucleo.casos import leer_columnas

MUESTRAS = 32
TRAMOS = ((0.0, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 1.01))


def unidades(ids: list[str], muestras_p: np.ndarray, costos: dict) -> list[dict]:
    """La lista `unidades` del contrato, ordenada de mayor a menor duda. muestras_p: (unidades, muestras)."""
    d = decision.decidir_tabla(muestras_p, costos["falso_si"], costos["falso_no"])
    bajo, alto = np.quantile(muestras_p, [0.05, 0.95], axis=1)
    filas = [{"id": str(ids[i]), "etiqueta": str(ids[i]), "p": round(float(d["p"][i]), 3),
              "rango_bajo": round(float(bajo[i]), 3), "rango_alto": round(float(alto[i]), 3),
              "muestras_p": [round(float(v), 2) for v in muestras_p[i]], "estado": str(d["estado"][i]), "duda": round(float(d["duda"][i]), 2)}
             for i in range(len(ids))]
    return sorted(filas, key=lambda u: -u["duda"])


def examen(caso: dict, ids: list[str], p: np.ndarray) -> dict | None:
    """Examen con datos reales reservados: lo que Krylov dijo de cada unidad por decidir contra lo que pasó.

    Lee `caso["verdad"]` (columnas `id`, `objetivo`). Devuelve tramos de probabilidad con lo dicho (promedio de p)
    y lo que pasó (frecuencia real). La frase la escribe el servicio con estos números. None si el caso no trae verdad.
    """
    if not caso.get("verdad"):
        return None
    tabla = leer_columnas(caso["verdad"])
    verdad = {i: float(v) for i, v in zip(tabla["id"], tabla["objetivo"]) if v != ""}
    pares = np.array([(p[j], verdad[str(i)]) for j, i in enumerate(ids) if str(i) in verdad])
    if len(pares) == 0:
        return None
    tramos = []
    for bajo, alto in TRAMOS:
        en = (pares[:, 0] >= bajo) & (pares[:, 0] < alto)
        if en.sum() >= 10:
            tramos.append({"dijimos": round(float(pares[en, 0].mean()), 3), "paso": round(float(pares[en, 1].mean()), 3), "n": int(en.sum())})
    return {"tipo": "datos_reales_reservados", "n": int(len(pares)), "frase": "", "tramos": tramos}


def rojo_datos(motivo: str) -> dict:
    """La respuesta propia de un motor cuando faltan datos para responder."""
    return {"unidades": None, "factores": None, "semaforo": {"estado": "rojo_datos", "motivo": motivo, "propuesta": None}}
