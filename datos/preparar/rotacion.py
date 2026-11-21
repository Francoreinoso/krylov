"""Caso de rotación (S-03): deja datos/demo/rotacion.csv y datos/demo/rotacion_verdad.csv.

Fuente: IBM HR Analytics Employee Attrition, ficticio, creado por IBM. 1.470 filas, 35 columnas, licencia ODbL.
Copia usada: https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/data/emp_attrition.csv
(el mismo archivo de Kaggle, 227.977 bytes). Se baja a datos/crudo/ (no se sube).

Qué hace:
- Conserva las 35 columnas del original, incluidas todas las que nombra casos/rotacion.yaml.
- Deja vacía la respuesta (Attrition) en un 20% de las filas elegido al azar con semilla fija,
  sin mirar la respuesta, y guarda la verdad de esas filas aparte (id, objetivo).
- Con 1.470 filas no hace falta muestrear (el tope es 2.000).

Uso, desde la raíz del repositorio:
    curl -sSL -o datos/crudo/rotacion_ibm.csv https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/data/emp_attrition.csv
    python3 datos/preparar/rotacion.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
FRACCION_VACIA = 0.20
RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "datos/crudo/rotacion_ibm.csv"
SALIDA = RAIZ / "datos/demo/rotacion.csv"
VERDAD = RAIZ / "datos/demo/rotacion_verdad.csv"

COLUMNAS_DEL_CASO = [
    "EmployeeNumber", "Attrition", "YearsAtCompany", "JobRole",
    "OverTime", "DistanceFromHome", "NumCompaniesWorked", "MonthlyIncome",
    "EnvironmentSatisfaction", "JobSatisfaction", "RelationshipSatisfaction", "WorkLifeBalance",
]

d = pd.read_csv(CRUDO, encoding="utf-8-sig")
assert d.shape == (1470, 35), d.shape
faltan = [c for c in COLUMNAS_DEL_CASO if c not in d.columns]
assert not faltan, f"faltan columnas: {faltan}"
assert d["EmployeeNumber"].is_unique

# Elegir el 20% por posición, sin mirar Attrition.
rng = np.random.default_rng(SEMILLA)
n_vacias = int(round(FRACCION_VACIA * len(d)))
elegidas = np.sort(rng.choice(len(d), size=n_vacias, replace=False))

verdad = pd.DataFrame({
    "id": d["EmployeeNumber"].iloc[elegidas].to_numpy(),
    "objetivo": d["Attrition"].iloc[elegidas].to_numpy(),
})
demo = d.copy()
demo["Attrition"] = demo["Attrition"].astype(object)
demo.loc[demo.index[elegidas], "Attrition"] = np.nan

# Las dos clases tienen que seguir presentes en lo que queda y en lo que se dejó vacío.
quedan = demo["Attrition"].dropna().value_counts()
assert set(quedan.index) == {"Yes", "No"}, quedan
assert set(verdad["objetivo"]) == {"Yes", "No"}

SALIDA.parent.mkdir(parents=True, exist_ok=True)
demo.to_csv(SALIDA, index=False)
verdad.to_csv(VERDAD, index=False)

print(f"{SALIDA.relative_to(RAIZ)}: {len(demo)} filas, {demo.shape[1]} columnas, "
      f"{demo['Attrition'].isna().sum()} por decidir")
print(f"con respuesta: {quedan.to_dict()} (tasa de renuncia {quedan['Yes'] / quedan.sum():.3f})")
print(f"{VERDAD.relative_to(RAIZ)}: {len(verdad)} filas, {verdad['objetivo'].value_counts().to_dict()}")
