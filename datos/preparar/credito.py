"""Caso de crédito (S-05): deja datos/demo/credito.csv y datos/demo/credito_verdad.csv.

Fuente: «Default of credit card clients», UCI Machine Learning Repository, dataset 350. Licencia CC BY 4.0.
30.000 clientes de tarjetas de crédito en Taiwán (abril a septiembre de 2005), 25 columnas.
https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
Se baja el .zip de UCI a datos/crudo/credito_uci/ (no se sube). Trae un .xls cuya segunda fila son los mismos
encabezados que la copia UCI_Credit_Card.csv; la respuesta se llama `default payment next month` y aquí se
renombra a `default`. No existe PAY_1: de PAY_0 se pasa a PAY_2.

Qué hace:
- Toma una muestra de 2.000 clientes al azar con semilla fija (el contrato pide entre 200 y 2.000 filas).
- Conserva las 25 columnas: los seis meses completos de PAY_*, BILL_AMT* y PAY_AMT*, más cupo, edad y educación.
- Deja vacía la respuesta en un 20% de la muestra, elegido al azar sin mirarla, y guarda esa verdad aparte (id, objetivo).

Uso, desde la raíz del repositorio:
    mkdir -p datos/crudo/credito_uci
    curl -sSL -o datos/crudo/credito_uci/uci_350.zip "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
    unzip -o -d datos/crudo/credito_uci datos/crudo/credito_uci/uci_350.zip
    uv run --no-project --with pandas --with xlrd python datos/preparar/credito.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
N_MUESTRA = 2000
FRACCION_VACIA = 0.20
RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "datos/crudo/credito_uci/default of credit card clients.xls"
SALIDA = RAIZ / "datos/demo/credito.csv"
VERDAD = RAIZ / "datos/demo/credito_verdad.csv"

MESES_ATRASO = ["PAY_6", "PAY_5", "PAY_4", "PAY_3", "PAY_2", "PAY_0"]
MESES_SALDO = [f"BILL_AMT{i}" for i in range(6, 0, -1)]
MESES_PAGO = [f"PAY_AMT{i}" for i in range(6, 0, -1)]
COLUMNAS_DEL_CASO = ["ID", "default", "LIMIT_BAL", "AGE", "EDUCATION", *MESES_ATRASO, *MESES_SALDO, *MESES_PAGO]

d = pd.read_excel(CRUDO, header=1).rename(columns={"default payment next month": "default"})
assert d.shape == (30000, 25), d.shape
faltan = [c for c in COLUMNAS_DEL_CASO if c not in d.columns]
assert not faltan, f"faltan columnas: {faltan}"
assert d["ID"].is_unique and not d.isna().any().any()

rng = np.random.default_rng(SEMILLA)

# 1. Muestra de 2.000 clientes al azar, en el orden original.
muestra = d.iloc[np.sort(rng.choice(len(d), size=N_MUESTRA, replace=False))].reset_index(drop=True)

# 2. Elegir el 20% por posición, sin mirar `default`.
n_vacias = int(round(FRACCION_VACIA * len(muestra)))
elegidas = np.sort(rng.choice(len(muestra), size=n_vacias, replace=False))

verdad = pd.DataFrame({
    "id": muestra["ID"].iloc[elegidas].to_numpy(),
    "objetivo": muestra["default"].iloc[elegidas].to_numpy(),
})
demo = muestra.copy()
demo["default"] = demo["default"].astype("Int64")  # entero con vacío: escribe 0, 1 o nada
demo.loc[elegidas, "default"] = pd.NA

quedan = demo["default"].dropna().value_counts()
assert set(quedan.index) == {0, 1}, quedan
assert set(verdad["objetivo"]) == {0, 1}

SALIDA.parent.mkdir(parents=True, exist_ok=True)
demo.to_csv(SALIDA, index=False)
verdad.to_csv(VERDAD, index=False)

print(f"{SALIDA.relative_to(RAIZ)}: {len(demo)} filas de {len(d)}, {demo.shape[1]} columnas, "
      f"{demo['default'].isna().sum()} por decidir")
print(f"con respuesta: {quedan.to_dict()} (tasa de impago {quedan[1] / quedan.sum():.3f}; "
      f"en el archivo completo {d['default'].mean():.3f})")
print(f"{VERDAD.relative_to(RAIZ)}: {len(verdad)} filas, {verdad['objetivo'].value_counts().to_dict()}")
print(f"saldos negativos en la muestra: {(demo[MESES_SALDO] < 0).to_numpy().sum()} celdas; "
      f"clientes con algún saldo sobre el cupo: {(demo[MESES_SALDO].max(axis=1) > demo['LIMIT_BAL']).mean():.3f}")
