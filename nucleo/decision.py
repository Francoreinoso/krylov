"""Capa de decisión: de probabilidades a tres colores y a «lo que cuesta no saber».

Es la copia de referencia de `contratos/CONTRATO.md`, sección 3 (la otra copia es
`web/src/decision.ts`). Las dos leen `contratos/ejemplos/decision_prueba.json`.

Los colores son **decisiones**, no pronósticos. Con C_si = costo de actuar sobre una
unidad que no lo necesitaba y C_no = costo de no actuar sobre una que sí:

    punto de corte = C_si / (C_si + C_no)        se actúa si p supera el punto de corte
    en duda        = hay más de 10% de probabilidad de que la decisión cambie al saber más

- Motores de tabla: cada unidad trae muestras de p, una por muestra del posterior de θ.
  La decisión usa el promedio; está en duda si más de 10% de las muestras caen al otro
  lado del punto de corte. Lo que cuesta no saber es el valor esperado de la
  información perfecta sobre θ:  min(C_si(1−p), C_no·p) − E_s[min(C_si(1−p_s), C_no·p_s)].
- Espacial: cada bloque trae p = P(valor > umbral). La probabilidad de equivocarse es
  1−p si se actúa y p si no; está en duda si supera 10%. Medir el bloque despeja toda
  la duda, así que lo que cuesta no saber es min(C_si(1−p), C_no·p).
"""

from __future__ import annotations

import numpy as np

UMBRAL_DE_DUDA = 0.10
ESTADOS = ("actuar", "no_actuar", "en_duda")


def punto_de_corte(c_si: float, c_no: float) -> float:
    return c_si / (c_si + c_no)


def _costo_esperado(p: np.ndarray, c_si: float, c_no: float) -> np.ndarray:
    """Costo esperado de la mejor decisión con probabilidad p: el menor entre actuar y no actuar."""
    return np.minimum(c_si * (1 - p), c_no * p)


def _estados(actuar: np.ndarray, en_duda: np.ndarray) -> np.ndarray:
    return np.where(en_duda, "en_duda", np.where(actuar, "actuar", "no_actuar"))


def decidir_tabla(muestras_p, c_si: float, c_no: float) -> dict[str, np.ndarray]:
    """muestras_p: (unidades, muestras). Devuelve p, estado y duda, uno por unidad."""
    muestras_p = np.atleast_2d(np.asarray(muestras_p, dtype=np.float64))
    corte = punto_de_corte(c_si, c_no)
    p = muestras_p.mean(axis=1)
    actuar = p > corte
    al_otro_lado = ((muestras_p > corte) != actuar[:, None]).mean(axis=1)
    duda = _costo_esperado(p, c_si, c_no) - _costo_esperado(muestras_p, c_si, c_no).mean(axis=1)
    return {"p": p, "estado": _estados(actuar, al_otro_lado > UMBRAL_DE_DUDA), "duda": np.maximum(duda, 0.0)}


def decidir_espacial(p, c_si: float, c_no: float) -> dict[str, np.ndarray]:
    """p: probabilidad de superar el umbral, por bloque. Devuelve estado y duda con la misma forma."""
    p = np.asarray(p, dtype=np.float64)
    actuar = p > punto_de_corte(c_si, c_no)
    equivocarse = np.where(actuar, 1 - p, p)
    return {"p": p, "estado": _estados(actuar, equivocarse > UMBRAL_DE_DUDA), "duda": _costo_esperado(p, c_si, c_no)}


def resumen_colores(estado) -> dict[str, int]:
    estado = np.asarray(estado)
    return {e: int((estado == e).sum()) for e in ESTADOS}


def certeza(muestras) -> str:
    """Etiqueta de «qué pesa»: qué fracción de las muestras del posterior coincide en el signo."""
    muestras = np.asarray(muestras, dtype=np.float64)
    acuerdo = max((muestras > 0).mean(), (muestras < 0).mean())
    return "seguro" if acuerdo >= 0.95 else "probable" if acuerdo >= 0.80 else "no_se_sabe"


def factor(nombre: str, etiqueta: str, muestras) -> dict:
    """Una fila de `factores` desde las muestras del posterior de un efecto."""
    muestras = np.asarray(muestras, dtype=np.float64)
    efecto = float(muestras.mean())
    return {"nombre": nombre, "etiqueta": etiqueta, "direccion": "sube" if efecto > 0 else "baja",
            "efecto": round(efecto, 3), "rango_bajo": round(float(np.quantile(muestras, 0.05)), 3),
            "rango_alto": round(float(np.quantile(muestras, 0.95)), 3), "certeza": certeza(muestras)}
