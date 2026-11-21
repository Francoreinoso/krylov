"""Caso de leyes con datos REALES: ley de cobre de 91 sondajes en una franja horizontal de un yacimiento.

Qué es: un «sondaje» es un pozo de exploración del que se sacan muestras de roca a distintas
profundidades; el laboratorio entrega cuánto cobre trae cada una (en ppm: partes por millón;
10.000 ppm = 1%). Aquí se toma una franja horizontal de 30 m de alto (un «banco» grueso) y se deja
un número por sondaje: la ley media de cobre de sus muestras dentro de la franja.

Fuente (datos reales, licencia CC BY 4.0):
    Hoffimann, J., Augusto, J., Resende, L., Mathias, M., Mazzinghy, D., Bianchetti, M., Mendes, M.,
    Souza, T., Andrade, V., Domingues, T., Silva, W., Silva, R., Couto, D., Fonseca, E. y
    Gonçalves, K. (2022). «GeoMet dataset» [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7051975
    (acompaña al artículo «Modeling geospatial uncertainty of geometallurgical variables with
    Bayesian models and Hilbert-Kriging», de los mismos autores).
Descarga (0,36 MB): https://zenodo.org/api/records/7051975/files/drillholes.csv/content
Archivo: drillholes.csv, 2.000 muestras de 119 sondajes. Columnas: HOLEID, X, Y, Z (metros, en un
    sistema local centrado: el registro no dice qué mina es) y 18 elementos en ppm (entre ellos «Cu ppm»).

Qué se hace: se toman las muestras con cota Z entre Z_MIN y Z_MAX (la franja de 30 m que cortan más
sondajes), y por sondaje se promedia la ley de cobre y la posición (x, y) de esas muestras (los
sondajes son inclinados: su (x, y) cambia con la profundidad). El archivo no trae el largo de cada
muestra (no hay columnas «desde/hasta»), así que el promedio es simple, no ponderado por largo; en
esta franja 2 de cada 3 sondajes tienen una sola muestra. No se filtra ni se corrige ningún valor.

Uso:  python datos/preparar/leyes_cobre_real.py <ruta a drillholes.csv> [carpeta de salida]
Deja: datos/demo/leyes_cobre_real.csv  (un sondaje por fila: pozo, x, y, cu_pct)
Los datos crudos NO se copian al repositorio.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
Z_MIN, Z_MAX = 120.0, 150.0        # la franja: cota entre 120 m (incluida) y 150 m (excluida)
PPM_POR_CIENTO = 10_000.0          # 10.000 ppm = 1%


def preparar(ruta: Path) -> list[tuple[str, str, str, str]]:
    """Una fila por sondaje con muestras dentro de la franja: (pozo, x, y, cu_pct)."""
    por_pozo: dict[int, list[tuple[float, float, float]]] = {}
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            try:
                x, y, z, cu = (float(fila[k]) for k in ("X", "Y", "Z", "Cu ppm"))
            except (ValueError, KeyError):
                continue                                   # fila sin número en alguna de las cuatro columnas
            if np.isfinite([x, y, z, cu]).all() and Z_MIN <= z < Z_MAX:
                por_pozo.setdefault(int(float(fila["HOLEID"])), []).append((x, y, cu))
    filas = []
    for pozo in sorted(por_pozo):
        x, y, cu = np.mean(por_pozo[pozo], axis=0)         # promedio simple de las muestras del sondaje en la franja
        filas.append((f"DH-{pozo:03d}", f"{x:.1f}", f"{y:.1f}", f"{cu / PPM_POR_CIENTO:.3f}"))
    return filas


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "datos" / "demo"
    filas = preparar(Path(sys.argv[1]))
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "leyes_cobre_real.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("pozo", "x", "y", "cu_pct"))
        w.writerows(filas)
    cu = np.array([float(fila[3]) for fila in filas])
    xs, ys = (np.array([float(fila[k]) for fila in filas]) for k in (1, 2))
    print(f"Franja: cota {Z_MIN:.0f} a {Z_MAX:.0f} m · sondajes: {len(filas)}")
    print(f"Ley de cobre (%): mínimo {cu.min():.3f} · mediana {np.median(cu):.3f} · media {cu.mean():.3f} · máximo {cu.max():.3f}")
    print(f"Extensión: x de {xs.min():.0f} a {xs.max():.0f} m · y de {ys.min():.0f} a {ys.max():.0f} m")


if __name__ == "__main__":
    main()
