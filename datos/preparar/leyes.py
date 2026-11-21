"""Caso `leyes`: un banco de tronadura SIMULADO con cobre y arsénico en cada pozo.

Qué es: el piso de una mina a rajo abierto (un «banco») de 240 m por 240 m, perforado con una
malla de pozos de tronadura. De cada pozo se saca una muestra y el laboratorio entrega cuánto
arsénico (ppm) y cuánto cobre (%) trae la roca. Con eso se decide, bloque por bloque, si la roca
va a la planta o se aparta.

Por qué es simulado: no hay datos públicos de pozos de tronadura con arsénico de una mina chilena
(ver `pitch/CIFRAS.md`, sección «Datos de los casos»). La pantalla lo rotula «simulado». El motor
`espacial` que lo responde está validado además con datos reales públicos (caso `terreno`).

El campo sale de la misma familia que el modelo generativo de `motor/espacial/simular.py`
(proceso gaussiano con covarianza exponencial y anisotropía geométrica, sobre el logaritmo de la
ley, más error de laboratorio), con parámetros fijos que el motor no conoce. Semilla fija.

Uso:  uv run python datos/preparar/leyes.py
Deja: datos/demo/leyes.csv         (un pozo por fila: pozo, x, y, as_ppm, cu_pct)
      datos/demo/leyes_verdad.csv  (la ley verdadera de arsénico en cada bloque de 7,5 m; no entra al motor)
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2026
LADO_M = 240.0            # lado del banco, en metros
BLOQUES = 32              # la grilla del motor: bloques de 7,5 m
BURDEN_M, ESPACIAMIENTO_M = 12.0, 14.0     # malla de pozos, trabada (cada fila corrida medio espaciamiento)
DESVIO_M = 1.0            # cuánto se aparta cada pozo de su lugar en la malla

# Parámetros verdaderos del campo (el motor no los ve). Distancias en metros.
ALCANCE_M = 70.0          # alcance de la covarianza exponencial en la dirección de mayor continuidad
RAZON = 2.2               # anisotropía: el alcance en la dirección transversal es ALCANCE_M / RAZON
AZIMUT = np.deg2rad(35.0) # dirección de mayor continuidad, medida desde el eje x
MEDIANA_AS_PPM = 330.0    # mediana de la ley de arsénico
DESV_LOG_AS = 0.9         # desviación del logaritmo de la ley
RUIDO_LOG = 0.15          # error de muestreo y de laboratorio, en logaritmo
MEDIANA_CU_PCT = 0.62     # mediana de la ley de cobre
DESV_LOG_CU = 0.45
CORRELACION = 0.55        # el arsénico acompaña en parte al cobre (minerales como la enargita traen los dos)


def _covarianza(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Covarianza exponencial anisotrópica entre dos conjuntos de puntos (n, 2) y (m, 2)."""
    d = a[:, None, :] - b[None, :, :]
    largo = d[..., 0] * np.cos(AZIMUT) + d[..., 1] * np.sin(AZIMUT)
    ancho = -d[..., 0] * np.sin(AZIMUT) + d[..., 1] * np.cos(AZIMUT)
    return np.exp(-np.sqrt((largo / ALCANCE_M) ** 2 + (ancho / (ALCANCE_M / RAZON)) ** 2))


def _pozos(gen: np.random.Generator) -> np.ndarray:
    filas = []
    for k, y in enumerate(np.arange(BURDEN_M / 2, LADO_M, BURDEN_M)):
        corrimiento = ESPACIAMIENTO_M / 2 if k % 2 else 0.0
        for x in np.arange(ESPACIAMIENTO_M / 2 + corrimiento, LADO_M, ESPACIAMIENTO_M):
            filas.append((x, y))
    pozos = np.array(filas) + gen.normal(0, DESVIO_M, size=(len(filas), 2))
    return np.clip(pozos, 0.5, LADO_M - 0.5)


def main() -> None:
    gen = np.random.default_rng(SEMILLA)
    pozos = _pozos(gen)
    lado = LADO_M / BLOQUES
    centros = np.array([((c + 0.5) * lado, (f + 0.5) * lado) for f in range(BLOQUES) for c in range(BLOQUES)])
    puntos = np.vstack([pozos, centros])

    cov = _covarianza(puntos, puntos) + 1e-8 * np.eye(len(puntos))
    raiz = np.linalg.cholesky(cov)
    campo_as = raiz @ gen.standard_normal(len(puntos))
    campo_propio_cu = raiz @ gen.standard_normal(len(puntos))
    campo_cu = CORRELACION * campo_as + np.sqrt(1 - CORRELACION**2) * campo_propio_cu

    n = len(pozos)
    as_ppm = MEDIANA_AS_PPM * np.exp(DESV_LOG_AS * campo_as[:n] + gen.normal(0, RUIDO_LOG, n))
    cu_pct = MEDIANA_CU_PCT * np.exp(DESV_LOG_CU * campo_cu[:n] + gen.normal(0, RUIDO_LOG, n))
    as_bloque = MEDIANA_AS_PPM * np.exp(DESV_LOG_AS * campo_as[n:])

    demo = RAIZ / "datos" / "demo"
    with open(demo / "leyes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pozo", "x", "y", "as_ppm", "cu_pct"])
        for i in range(n):
            w.writerow([f"P-{i + 1:03d}", f"{pozos[i, 0]:.1f}", f"{pozos[i, 1]:.1f}", f"{as_ppm[i]:.0f}", f"{cu_pct[i]:.2f}"])
    with open(demo / "leyes_verdad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "as_ppm_verdadero"])
        for (x, y), v in zip(centros, as_bloque):
            w.writerow([f"{x:.2f}", f"{y:.2f}", f"{v:.0f}"])

    sobre = int((as_ppm > 500).sum())
    print(f"{n} pozos; arsénico entre {as_ppm.min():.0f} y {as_ppm.max():.0f} ppm (mediana {np.median(as_ppm):.0f}); "
          f"{sobre} pozos sobre 500 ppm ({100 * sobre / n:.0f}%); cobre mediana {np.median(cu_pct):.2f}%")
    print(f"bloques verdaderos sobre 500 ppm: {int((as_bloque > 500).sum())} de {len(as_bloque)}")


if __name__ == "__main__":
    main()
