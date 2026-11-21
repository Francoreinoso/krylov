"""Caso `flota`: cuarenta camiones SIMULADOS, con un desgaste que no se ve y deja huella en lo que se mide.

Qué es: cada camión minero acumula desgaste en un componente (por ejemplo el motor). No se puede
mirar adentro: cada cierto tiempo se toma una muestra de aceite y se mide un indicador que sube con
el desgaste. Cuando el desgaste cruza un límite, el camión falla. La pregunta es qué camiones no
van a llegar a su próxima mantención programada.

Por qué es simulado: no hay datos públicos de análisis de aceite de una flota minera.

Sigue las ecuaciones de `WORKPLAN.md`, sección 11.4 (motor `desgaste`): cada camión tiene su ritmo,
las rutas exigentes desgastan más, el desgaste avanza a saltos y nunca retrocede (proceso gamma), y
cada medición trae error. El indicador está normalizado: 1,0 es la falla. Los camiones del archivo
siguen en servicio: si una trayectoria simulada ya cruzó el límite, se sortea de nuevo. Semilla fija.

Uso:  uv run python datos/preparar/flota.py
Deja: datos/demo/flota.csv         (una fila por medición: unidad, tiempo en horas de operación, valor,
                                    y dos datos del camión repetidos en sus filas: exigencia, horas_a_mantencion)
      datos/demo/flota_verdad.csv  (por camión: su desgaste verdadero hoy y si falla antes de la mantención)
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2026
CAMIONES = 40
CADA_H = 250.0            # una muestra de aceite cada 250 horas, más o menos

# Parámetros verdaderos (el motor no los ve). El tiempo va en miles de horas dentro del modelo.
RITMO_MEDIANO, RITMO_DESV_LOG = 0.26, 0.35      # desgaste por mil horas
EN_SERVICIO_BAJO = 0.92                         # los camiones del archivo siguen andando: su desgaste de hoy está bajo este valor
EFECTO_RUTA = 0.3                               # cuánto acelera el desgaste una ruta exigente
SALTOS = 0.3                                    # qué tan a saltos avanza
RUIDO = 0.04


def main() -> None:
    gen = np.random.default_rng(SEMILLA)
    exigencia = gen.standard_normal(CAMIONES)
    ritmo = RITMO_MEDIANO * np.exp(EFECTO_RUTA * exigencia + RITMO_DESV_LOG * gen.standard_normal(CAMIONES))
    n_muestras = gen.integers(4, 11, size=CAMIONES)
    a_mantencion = gen.choice([250.0, 500.0, 750.0], size=CAMIONES)

    demo = RAIZ / "datos" / "demo"
    verdad = []
    with open(demo / "flota.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "tiempo", "valor", "exigencia", "horas_a_mantencion"])
        for i in range(CAMIONES):
            while True:
                pasos = CADA_H * (1 + 0.15 * gen.standard_normal(n_muestras[i])).clip(0.5, 1.5)
                t = np.cumsum(pasos)                                         # horas de operación en cada muestra
                saltos = gen.gamma(shape=ritmo[i] * (pasos / 1000) / SALTOS**2, scale=SALTOS**2)
                x = np.cumsum(saltos)                                        # desgaste verdadero en cada muestra
                if x[-1] < EN_SERVICIO_BAJO:
                    break
            y = x + RUIDO * gen.standard_normal(n_muestras[i])
            nombre = f"CAEX-{i + 1:02d}"
            for tk, yk in zip(t, y):
                w.writerow([nombre, f"{tk:.0f}", f"{yk:.3f}", f"{exigencia[i]:.2f}", f"{a_mantencion[i]:.0f}"])
            futuro = gen.gamma(shape=ritmo[i] * (a_mantencion[i] / 1000) / SALTOS**2, scale=SALTOS**2)
            verdad.append((nombre, x[-1], int(x[-1] + futuro >= 1.0)))
    with open(demo / "flota_verdad.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["unidad", "desgaste_hoy", "falla_antes_de_la_mantencion"])
        for nombre, x, falla in verdad:
            w.writerow([nombre, f"{x:.3f}", falla])

    hoy = np.array([v[1] for v in verdad])
    print(f"{CAMIONES} camiones, {int(n_muestras.sum())} mediciones; desgaste hoy entre {hoy.min():.2f} y {hoy.max():.2f}; "
          f"{sum(v[2] for v in verdad)} fallan antes de su mantención")


if __name__ == "__main__":
    main()
