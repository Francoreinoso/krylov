"""Caso `flotacion`: ocho líneas de flotación SIMULADAS, medidas solo en sus primeras celdas.

Qué es: la planta separa el cobre con burbujas en filas de estanques (líneas). La pulpa tarda cerca
de media hora en recorrer una línea de ocho celdas. Un analizador mide cuánto cobre se lleva
recuperado al salir de las primeras celdas; lo que falte por recuperar al final se va al relave.
La pregunta es si, con lo medido al principio, la línea va a terminar bajo la meta.

Por qué es simulado: no encontramos mediciones públicas celda por celda de una planta de cobre.

Sigue las ecuaciones de `WORKPLAN.md`, sección 11.3 (motor `cinetica`): el cobre flota rápido al
principio y cada vez más lento; cada línea tiene su velocidad y su tope. Semilla fija.

Uso:  uv run python datos/preparar/flotacion.py
Deja: datos/demo/flotacion.csv         (una fila por medición: unidad, tiempo en minutos, valor = recuperación acumulada, de 0 a 1)
      datos/demo/flotacion_verdad.csv  (por línea: la recuperación verdadera al final y si queda bajo la meta)
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2026
LINEAS = 8
CELDAS = 8
MIN_POR_CELDA = 3.5       # la línea completa: 28 minutos
META = 0.84               # recuperación mínima aceptable al final de la línea

# Parámetros verdaderos (el motor no los ve)
VELOCIDAD_MEDIANA, VELOCIDAD_DESV_LOG = 0.22, 0.35     # 1/min
TOPE_MEDIANO, TOPE_DESV_LOGIT = 0.94, 0.5
FRACCION_RAPIDA = 0.8
RUIDO = 0.012


def curva(t: np.ndarray, k: float, tope: float) -> np.ndarray:
    return tope * (1 - FRACCION_RAPIDA * np.exp(-k * t) - (1 - FRACCION_RAPIDA) * np.exp(-k * t / 8))


def main() -> None:
    gen = np.random.default_rng(SEMILLA)
    t = MIN_POR_CELDA * np.arange(1, CELDAS + 1)
    k = VELOCIDAD_MEDIANA * np.exp(VELOCIDAD_DESV_LOG * gen.standard_normal(LINEAS))
    logit = np.log(TOPE_MEDIANO / (1 - TOPE_MEDIANO)) + TOPE_DESV_LOGIT * gen.standard_normal(LINEAS)
    tope = 1 / (1 + np.exp(-logit))
    medidas = gen.integers(3, 7, size=LINEAS)             # celdas con medición: de 3 a 6

    demo = RAIZ / "datos" / "demo"
    with open(demo / "flotacion.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "tiempo", "valor"])
        for b in range(LINEAS):
            y = curva(t[: medidas[b]], k[b], tope[b]) + RUIDO * gen.standard_normal(medidas[b])
            for tk, yk in zip(t[: medidas[b]], y):
                w.writerow([f"L-{b + 1}", f"{tk:.1f}", f"{np.clip(yk, 0.001, 0.999):.3f}"])
    final = np.array([curva(t[-1:], k[b], tope[b])[0] for b in range(LINEAS)])
    with open(demo / "flotacion_verdad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "recuperacion_final", "bajo_la_meta"])
        for b in range(LINEAS):
            w.writerow([f"L-{b + 1}", f"{final[b]:.3f}", int(final[b] < META)])

    print(f"{LINEAS} líneas, {int(medidas.sum())} mediciones; recuperación final entre {final.min():.3f} y {final.max():.3f}; "
          f"{int((final < META).sum())} bajo la meta de {META}")


if __name__ == "__main__":
    main()
