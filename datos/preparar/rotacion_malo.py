"""Archivo malo del demo (S-08): deja datos/demo/rotacion_malo.csv.

Es `datos/demo/rotacion.csv` con una columna más, `fecha_salida`, inventada por nosotros: tiene fecha solo para las
personas que renunciaron, **incluidas las 294 cuya respuesta quedó vacía**. Por eso delata la respuesta: es la columna
que un archivo real traería por error (se llenó después de que la persona se fue). Va declarada en
`columnas.extra` de `casos/rotacion_malo.yaml`; no entra a la red y la detecta la nube (D-26).
El caso dice en `origen_datos` que la columna la agregamos nosotros.

Las fechas se sortean con semilla fija entre el 1 de noviembre de 2025 y el 31 de octubre de 2026. Solo importa que
existan para quien se fue y falten para quien sigue.

Uso, desde la raíz del repositorio (lee solo archivos versionados):
    python3 datos/preparar/rotacion_malo.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
RAIZ = Path(__file__).resolve().parents[2]
ROTACION = RAIZ / "datos/demo/rotacion.csv"
VERDAD = RAIZ / "datos/demo/rotacion_verdad.csv"
SALIDA = RAIZ / "datos/demo/rotacion_malo.csv"

d = pd.read_csv(ROTACION)
verdad = pd.read_csv(VERDAD).set_index("id")["objetivo"]
assert d.shape == (1470, 35), d.shape

# La respuesta verdadera de todas las filas: la del archivo y, donde quedó vacía, la guardada aparte.
renuncio = d["Attrition"].copy()
vacias = renuncio.isna()
renuncio[vacias] = d.loc[vacias, "EmployeeNumber"].map(verdad)
assert renuncio.notna().all()

rng = np.random.default_rng(SEMILLA)
inicio = np.datetime64("2025-11-01")
dias = rng.integers(0, 365, size=len(d))
fechas = pd.Series((inicio + dias.astype("timedelta64[D]")).astype(str), index=d.index)

malo = d.copy()
malo["fecha_salida"] = fechas.where(renuncio == "Yes")

SALIDA.parent.mkdir(parents=True, exist_ok=True)
malo.to_csv(SALIDA, index=False)

con_fecha = malo["fecha_salida"].notna()
print(f"{SALIDA.relative_to(RAIZ)}: {len(malo)} filas, {malo.shape[1]} columnas")
print(f"con fecha_salida: {con_fecha.sum()} (= renunciaron: {(renuncio == 'Yes').sum()}); "
      f"de las {vacias.sum()} por decidir, {int((con_fecha & vacias).sum())} traen fecha: la columna delata la respuesta")
