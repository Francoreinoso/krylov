"""Caso `sismicidad`: ocho sectores SIMULADOS de una mina subterránea, en las horas que siguen a una tronadura.

Qué es: bajo tierra, después de cada tronadura la roca se reacomoda y produce temblores chicos.
Una red de sensores registra la hora y la magnitud de cada uno. Cada temblor sube por un rato la
probabilidad del siguiente, y los grandes más. La pregunta es en qué sectores puede volver a entrar
la gente: qué tan probable es un temblor fuerte en las próximas horas.

Por qué es simulado: no hay un catálogo público de sismos de una mina subterránea de este tipo.

Sigue las ecuaciones de `WORKPLAN.md`, sección 11.5 (motor `sismico`): un proceso de Hawkes temporal
por sector, con la tronadura como primer gatillo y magnitudes de Gutenberg-Richter. Semilla fija.

Uso:  uv run python datos/preparar/sismicidad.py
Deja: datos/demo/sismicidad.csv         (una fila por sismo: unidad, tiempo en horas desde la tronadura, valor = magnitud)
      datos/demo/sismicidad_verdad.csv  (por sector: cuántos sismos fuertes hubo de verdad en el horizonte)
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2026
SECTORES = 8
VENTANA_H = 6.0           # horas observadas desde la tronadura
HORIZONTE_H = 6.0         # se decide sobre las 6 horas siguientes
MAGNITUD_MINIMA = -1.0    # la más chica que la red registra completa
MAGNITUD_FUERTE = 1.0     # desde aquí el sismo importa para la seguridad

# Parámetros verdaderos (el motor no los ve)
FONDO_MEDIANO, FONDO_DESV_LOG = 0.6, 0.5        # sismos por hora sin gatillo
RAMIFICACION = 0.45                             # sismos nuevos que gatilla, en promedio, cada sismo
ALFA = 1.0                                      # cuánto más gatilla uno grande
APAGADO = 1.2                                   # 1/h: qué tan rápido se apaga el efecto
B = 1.0                                         # Gutenberg-Richter
TRONADURA_MEDIANA, TRONADURA_DESV_LOG = 8.0, 0.6   # sismos que gatilla directamente la tronadura


def _magnitudes(gen: np.random.Generator, n: int) -> np.ndarray:
    return MAGNITUD_MINIMA + gen.exponential(1 / (B * np.log(10)), size=n)


def _sector(gen: np.random.Generator, fondo: float, tronadura: float) -> tuple[np.ndarray, np.ndarray]:
    """Un sector hasta VENTANA_H + HORIZONTE_H, por ramificación: fondo, hijos de la tronadura, hijos de cada sismo."""
    total = VENTANA_H + HORIZONTE_H
    beta = B * np.log(10)
    normaliza = beta / (beta - ALFA)                                   # E[exp(ALFA·(m − m0))]
    t = np.concatenate([gen.uniform(0, total, gen.poisson(fondo * total)),
                        gen.exponential(1 / APAGADO, gen.poisson(tronadura))])
    m = _magnitudes(gen, len(t))
    generacion_t, generacion_m = t, m
    while len(generacion_t):
        hijos = gen.poisson(RAMIFICACION * np.exp(ALFA * (generacion_m - MAGNITUD_MINIMA)) / normaliza)
        nuevos_t = np.repeat(generacion_t, hijos) + gen.exponential(1 / APAGADO, int(hijos.sum()))
        nuevos_m = _magnitudes(gen, len(nuevos_t))
        t, m = np.concatenate([t, nuevos_t]), np.concatenate([m, nuevos_m])
        generacion_t, generacion_m = nuevos_t, nuevos_m
    dentro = t < total
    orden = np.argsort(t[dentro])
    return t[dentro][orden], m[dentro][orden]


def main() -> None:
    gen = np.random.default_rng(SEMILLA)
    fondo = FONDO_MEDIANO * np.exp(FONDO_DESV_LOG * gen.standard_normal(SECTORES))
    tronadura = TRONADURA_MEDIANA * np.exp(TRONADURA_DESV_LOG * gen.standard_normal(SECTORES))

    demo = RAIZ / "datos" / "demo"
    filas, verdad = 0, []
    with open(demo / "sismicidad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "tiempo", "valor"])
        for s in range(SECTORES):
            t, m = _sector(gen, fondo[s], tronadura[s])
            visto = t < VENTANA_H
            for tk, mk in zip(t[visto], m[visto]):
                w.writerow([f"Sector {s + 1}", f"{tk:.3f}", f"{mk:.2f}"])
                filas += 1
            fuertes = int(((~visto) & (m >= MAGNITUD_FUERTE)).sum())
            verdad.append((f"Sector {s + 1}", int(visto.sum()), fuertes))
    with open(demo / "sismicidad_verdad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "sismos_fuertes_en_el_horizonte", "hubo_sismo_fuerte"])
        for nombre, _, fuertes in verdad:
            w.writerow([nombre, fuertes, int(fuertes > 0)])

    print(f"{SECTORES} sectores, {filas} sismos en {VENTANA_H:.0f} h (por sector: {[v[1] for v in verdad]}); "
          f"sectores con sismo fuerte en las {HORIZONTE_H:.0f} h siguientes: {sum(v[2] > 0 for v in verdad)}")


if __name__ == "__main__":
    main()
