"""Caso `taludes` con datos REALES: prismas topográficos de un rajo abierto antes de una falla de talud.

Qué es: en la pared («talud») de un rajo abierto (el registro no nombra la mina; los archivos de clima
que trae son del servicio meteorológico de Australia) se instalaron prismas (espejos que una
estación total —un teodolito robotizado— mide varias veces al día). Si la pared se mueve, la distancia
al prisma cambia. Entre febrero y abril de 2014 la pared suroeste de ese rajo falló de manera
progresiva (hasta 20 metros de desplazamiento acumulado a agosto; no fue un derrumbe instantáneo).
El primer evento es el 16-feb-2014, día en que cayeron 115 mm de lluvia (estación del BOM incluida
en el zip): varios prismas saltan entre 40 y 200 mm en un día y el sector pasa de unos 5 mm/día a
30-45 mm/día. Este guion recorta una ventana de 25 días que termina el 14-feb a las 00:00, ANTES
de ese evento, para que la pregunta «¿este prisma falla en las próximas H horas?» siga abierta, y
deja aparte lo que pasó después (la «verdad»), que no entra al motor.

Fuente (datos reales, licencia CC BY 4.0):
    de Wit, Tjaart (2025). «Data used for the study of time-lapse velocity variations during an
    open-pit mine slope failure using seismic noise interferometry» [Data set]. Zenodo.
    https://doi.org/10.5281/zenodo.15003054
Descarga (8,9 MB): https://zenodo.org/api/records/15003054/files/Data.zip/content
Archivo usado dentro del zip: radar-deformation-data/South_West_Corner_06082014.csv
    (exportado con Quikslope5 el 6-ago-2014; pese al nombre de la carpeta son PRISMAS, no radar).
    Columnas: Prism, Date, Time, Easting, Northing, Height [m], Adjusted Distance Diff,
    Unadjusted Slope Distance Diff, Easting Diff, Northing Diff, Height Diff [mm, respecto de la
    primera lectura de cada prisma]. 82.401 lecturas de 160 prismas, 1-ene a 6-ago-2014.

Qué se usa como desplazamiento: «Adjusted Distance Diff», el cambio de la distancia inclinada
estación-prisma en su versión «ajustada» por el programa del equipo (el registro de Zenodo no
documenta el ajuste; es la medida más limpia: ~1 mm de ruido entre lecturas, contra ~9 mm del
desplazamiento 3D, y en estas fechas viene redondeada al milímetro). Viene negativa cuando el
prisma se acerca a la estación (la pared se mueve hacia el rajo); aquí se le cambia el signo y se
vuelve a referir a la primera lectura de la ventana. No se suaviza ni se corrige nada más.
OJO: es la componente a lo largo de la línea de vista. El desplazamiento 3D total es mayor: casi
igual en los prismas del pie de la pared y hasta 2,5 veces en los de la cresta oeste.

Definición de «falla» (la verdad): después del fin de la ventana, la primera lectura en que la
velocidad media del prisma, medida contra la lectura más reciente que esté al menos 24 horas antes,
llega a UMBRAL_MM_DIA (24 mm/día = 1 mm/hora; es un supuesto del demo, no un umbral de esa mina).
Se mira durante SEGUIMIENTO_H horas; `fallo_en_horizonte` vale 1 si eso pasa dentro de HORIZONTE_H
horas. `horas_hasta_falla` es la hora de la primera lectura que lo confirma: el 16-feb hubo pocas
lecturas, así que el evento pudo ocurrir hasta ~30 horas antes de lo que dice esa columna.

Uso:  python datos/preparar/taludes_real.py <ruta a Data.zip o al CSV ya extraído> [carpeta de salida]
Deja: datos/demo/taludes_real.csv         (unidad, tiempo [h desde el inicio de la ventana], valor [mm])
      datos/demo/taludes_real_verdad.csv  (unidad, fallo_en_horizonte, horas_hasta_falla; no entra al motor)
Los datos crudos NO se copian al repositorio.
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
MIEMBRO_ZIP = "radar-deformation-data/South_West_Corner_06082014.csv"

INICIO = datetime(2014, 1, 20)     # inicio de la ventana (hora local de la mina, como viene en el archivo)
DIAS_VENTANA = 25                  # la ventana termina el 14-feb-2014 a las 00:00
HORIZONTE_H = 120.0                # H: «¿falla en las próximas 120 horas?»
SEGUIMIENTO_H = 240.0              # cuánto se mira después de la ventana para escribir la verdad
UMBRAL_MM_DIA = 24.0               # velocidad que se llama «falla» (1 mm por hora)
BASE_MIN_H = 24.0                  # la velocidad se mide contra una lectura al menos 24 h anterior
MIN_LECTURAS, MAX_LECTURAS = 48, 144   # lecturas por prisma dentro de la ventana (si hay más, se ralea)
HUECO_MAX_H = 96.0                 # se descartan prismas con un hueco mayor dentro de la ventana
MISMO_PUNTO_M = 0.10               # dos prismas a menos de 10 cm son el mismo punto con dos nombres
MESES = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def _texto(ruta: Path) -> str:
    """Devuelve el CSV como texto, venga suelto o dentro del Data.zip de Zenodo."""
    if ruta.suffix.lower() == ".zip":
        with zipfile.ZipFile(ruta) as z:
            return z.read(MIEMBRO_ZIP).decode("ascii", errors="replace")
    return ruta.read_text(encoding="ascii", errors="replace")


def _fecha(dia: str, hora: str) -> datetime:
    """'16-Feb-14', '21:34:23' -> datetime (sin depender del idioma del sistema)."""
    d, m, a = dia.split("-")
    h, mi, s = hora.split(":")
    return datetime(2000 + int(a), MESES[m], int(d), int(h), int(mi), int(s))


def leer(ruta: Path) -> tuple[dict[str, dict[str, np.ndarray]], int]:
    """Lee el archivo crudo. Devuelve {prisma: {t [h desde INICIO], d [mm], xyz [m]}} y cuántas lecturas se botaron."""
    filas = csv.reader(io.StringIO(_texto(ruta)))
    for fila in filas:                       # las tres primeras líneas son un encabezado del programa
        if fila and fila[0].strip() == "Prism":
            break
    crudo: dict[str, list[tuple[float, float, float, float, float]]] = {}
    botadas = 0
    for fila in filas:
        if len(fila) < 7:
            continue
        try:
            t = (_fecha(fila[1], fila[2]) - INICIO).total_seconds() / 3600.0
            este, norte, cota, dist = (float(fila[k]) for k in (3, 4, 5, 6))
        except (ValueError, KeyError):
            botadas += 1
            continue
        if not np.isfinite([este, norte, cota, dist]).all():   # lecturas vacías o no numéricas
            botadas += 1
            continue
        crudo.setdefault(fila[0].strip(), []).append((t, -dist, este, norte, cota))   # signo: positivo = hacia el rajo
    prismas = {}
    for nombre, lecturas in crudo.items():
        a = np.array(sorted(lecturas))
        prismas[nombre] = {"t": a[:, 0], "d": a[:, 1], "xyz": a[:, 2:5]}
    return prismas, botadas


def hora_de_falla(t: np.ndarray, d: np.ndarray, desde: float, hasta: float) -> float | None:
    """Horas (desde `desde`) hasta la primera lectura con velocidad >= UMBRAL_MM_DIA; None si no ocurre."""
    for i in np.flatnonzero((t > desde) & (t <= hasta)):
        j = np.searchsorted(t, t[i] - BASE_MIN_H, side="right") - 1      # lectura más reciente >= 24 h antes
        if j >= 0 and (d[i] - d[j]) / (t[i] - t[j]) * 24.0 >= UMBRAL_MM_DIA:
            return float(t[i] - desde)
    return None


def preparar(ruta: Path) -> tuple[list[tuple], list[tuple], list[dict], int]:
    prismas, botadas = leer(ruta)
    fin = DIAS_VENTANA * 24.0
    candidatos = []
    for nombre, p in prismas.items():
        t, d = p["t"], p["d"]
        dentro = (t >= 0.0) & (t < fin)
        if dentro.sum() < MIN_LECTURAS:
            continue
        tv = t[dentro]
        if np.diff(np.concatenate([[0.0], tv, [fin]])).max() > HUECO_MAX_H:   # huecos, incluidos los bordes
            continue
        if not (t > fin + HORIZONTE_H).any():        # dejó de reportar antes del horizonte: no hay verdad
            continue
        candidatos.append({"unidad": nombre, "n": int(dentro.sum()), "t": tv, "d": d[dentro],
                           "pos": p["xyz"][dentro][0], "falla": hora_de_falla(t, d, fin, fin + SEGUIMIENTO_H)})

    # Un mismo punto medido con dos nombres (o desde dos estaciones): se queda el de más lecturas.
    candidatos.sort(key=lambda c: (-c["n"], c["unidad"]))
    elegidos: list[dict] = []
    for c in candidatos:
        if all(np.linalg.norm(c["pos"] - e["pos"]) > MISMO_PUNTO_M for e in elegidos):
            elegidos.append(c)
    elegidos.sort(key=lambda c: c["unidad"])

    lecturas, verdad = [], []
    for c in elegidos:
        t, d = c["t"], c["d"]
        if len(t) > MAX_LECTURAS:                    # raleo regular: se conservan la primera y la última
            idx = np.unique(np.round(np.linspace(0, len(t) - 1, MAX_LECTURAS)).astype(int))
            t, d = t[idx], d[idx]
        d = d - d[0]                                 # desplazamiento respecto de la primera lectura de la ventana
        c["t"], c["d"] = t, d
        lecturas += [(c["unidad"], f"{ti:.2f}", f"{di:.1f}") for ti, di in zip(t, d)]
        f = c["falla"]
        verdad.append((c["unidad"], int(f is not None and f <= HORIZONTE_H), "" if f is None else f"{f:.1f}"))
    return lecturas, verdad, elegidos, botadas


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "datos" / "demo"
    lecturas, verdad, elegidos, botadas = preparar(Path(sys.argv[1]))
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, encabezado, filas in (("taludes_real.csv", ("unidad", "tiempo", "valor"), lecturas),
                                      ("taludes_real_verdad.csv", ("unidad", "fallo_en_horizonte", "horas_hasta_falla"), verdad)):
        with open(salida / nombre, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(encabezado)
            w.writerows(filas)

    fin = INICIO + timedelta(days=DIAS_VENTANA)
    print(f"Ventana: {INICIO:%d-%m-%Y %H:%M} a {fin:%d-%m-%Y %H:%M} · horizonte {HORIZONTE_H:.0f} h · umbral {UMBRAL_MM_DIA:.0f} mm/día")
    print(f"Prismas: {len(elegidos)} · lecturas: {len(lecturas)} · lecturas botadas por vacías o no numéricas: {botadas}")
    print(f"Fallan dentro del horizonte: {sum(v[1] for v in verdad)} · fallan después (hasta {SEGUIMIENTO_H:.0f} h): "
          f"{sum(1 for v in verdad if v[2] and not v[1])} · no fallan: {sum(1 for v in verdad if not v[2])}")
    print("unidad     n  último_mm  vel_último_día_mm/d  horas_hasta_falla")
    for c, v in zip(elegidos, verdad):
        t, d = c["t"], c["d"]
        j = max(np.searchsorted(t, t[-1] - 24.0, side="right") - 1, 0)
        print(f"{c['unidad']:8s} {len(t):4d} {d[-1]:9.1f} {(d[-1] - d[j]) / (t[-1] - t[j]) * 24.0:12.1f}   {v[2] or '-':>8s}")


if __name__ == "__main__":
    main()
