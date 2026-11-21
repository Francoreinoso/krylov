"""Caso `taludes`: un muro SIMULADO, medido por un radar, con algunos sectores acelerándose.

Qué es: la pared de un rajo (o el muro de un tranque de relaves) dividida en 36 sectores. Un radar
mide cada 30 minutos cuántos milímetros se ha movido cada sector. La mayoría se mueve lento y parejo;
unos pocos se están acelerando, que es lo que pasa antes de que un muro ceda.

Por qué es simulado: el archivo del demo necesita una respuesta correcta escondida. El motor se prueba
además con datos reales abiertos de un rajo que falló (`taludes_real.py`).

Sigue las ecuaciones de `WORKPLAN.md`, sección 11.2 (motor `deformacion`): velocidad de fondo por
sector, ley de velocidad inversa en los sectores que se aceleran, ruido de cada lectura y un «modo
común» (la atmósfera mueve la lectura de todos los sectores a la vez). Semilla fija.

Uso:  uv run python datos/preparar/taludes.py
Deja: datos/demo/taludes.csv         (una fila por lectura: unidad, tiempo en horas, valor en mm)
      datos/demo/taludes_verdad.csv  (por sector: si se acelera, cuántas horas faltan y si cede dentro del horizonte)
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2026
SECTORES = 36
VENTANA_H = 48.0          # horas de historia
CADA_H = 0.5              # una lectura cada 30 minutos
HORIZONTE_H = 12.0        # se decide sobre las próximas 12 horas
FALTANTES = 0.05          # fracción de lecturas que el radar no entregó

# Parámetros verdaderos (el motor no los ve)
FRACCION_ACELERANDO = 0.2
VELOCIDAD_MEDIANA, VELOCIDAD_DESV_LOG = 0.08, 0.6      # mm/h
FALTA_MEDIANA_H, FALTA_DESV_LOG = 18.0, 0.7            # horas que faltan para ceder, en los que se aceleran
ACELERACION_MEDIANA_MM, ACELERACION_DESV_LOG = 5.0, 0.5
RUIDO_MM = 0.25
MODO_COMUN_MM, MODO_COMUN_RHO = 0.6, 0.9               # efecto de la atmósfera, igual para todos en cada lectura


def main() -> None:
    gen = np.random.default_rng(SEMILLA)
    t = np.arange(CADA_H, VENTANA_H + 1e-9, CADA_H)
    acelera = np.zeros(SECTORES, dtype=bool)
    acelera[gen.permutation(SECTORES)[: round(FRACCION_ACELERANDO * SECTORES)]] = True
    v = VELOCIDAD_MEDIANA * np.exp(VELOCIDAD_DESV_LOG * gen.standard_normal(SECTORES))
    falta = FALTA_MEDIANA_H * np.exp(FALTA_DESV_LOG * gen.standard_normal(SECTORES))
    a = ACELERACION_MEDIANA_MM * np.exp(ACELERACION_DESV_LOG * gen.standard_normal(SECTORES))
    t_falla = VENTANA_H + falta

    comun = np.zeros(len(t))
    for k in range(1, len(t)):
        comun[k] = MODO_COMUN_RHO * comun[k - 1] + MODO_COMUN_MM * np.sqrt(1 - MODO_COMUN_RHO**2) * gen.standard_normal()

    demo = RAIZ / "datos" / "demo"
    n_lecturas = 0
    with open(demo / "taludes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "tiempo", "valor"])
        for j in range(SECTORES):
            d = v[j] * t
            if acelera[j]:
                d = d + a[j] * np.log(t_falla[j] / (t_falla[j] - t))
            y = d + comun + RUIDO_MM * gen.standard_normal(len(t))
            presente = gen.random(len(t)) > FALTANTES
            for k in np.flatnonzero(presente):
                w.writerow([f"S-{j + 1:02d}", f"{t[k]:.1f}", f"{y[k]:.2f}"])
                n_lecturas += 1
    with open(demo / "taludes_verdad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "acelerando", "horas_hasta_ceder", "cede_en_el_horizonte"])
        for j in range(SECTORES):
            cede = bool(acelera[j] and falta[j] <= HORIZONTE_H)
            w.writerow([f"S-{j + 1:02d}", int(acelera[j]), f"{falta[j]:.1f}" if acelera[j] else "", int(cede)])

    ceden = int((acelera & (falta <= HORIZONTE_H)).sum())
    print(f"{SECTORES} sectores, {n_lecturas} lecturas; {int(acelera.sum())} se aceleran y {ceden} ceden dentro de {HORIZONTE_H:.0f} h")


if __name__ == "__main__":
    main()
