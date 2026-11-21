"""Archivos de prueba para la subida del chat (D-34): datos/demo/subida_rotacion_<area>.csv y su _verdad.csv.

**Qué son, dicho como es:** subconjuntos reales del mismo archivo público de IBM (ficticio, 1.470 personas), uno por
área, presentados como si fueran otra empresa. No son otra empresa real. Sirven para mostrar que la misma red responde
un archivo que no es el del demo: otro tamaño, otros cargos, otras columnas y otros nombres de columnas.

- `ventas`: el área Sales (446 personas, 3 cargos). Dentro de lo que practicó la red (200 a 2.000 personas, 3 a 12 cargos).
- `investigacion`: el área Research & Development (961 personas, 6 cargos). Dentro.
- `rrhh`: el área Human Resources (63 personas, 2 cargos). **Fuera a propósito:** con tan pocas filas Krylov no
  responde (`rojo_datos`); sirve para mostrar que lo dice.

Cambios respecto del archivo del demo, para que asignar las columnas en el chat tenga sentido:
- Columnas con nombres en español, en otro orden, con dos columnas que el modelo no usa (`edad`, `area`).
- Sí y No en español; cargos traducidos.
- La respuesta (`renuncio`) queda vacía en un 20% elegido al azar con otra semilla (2027), sin mirarla; la verdad va aparte.

Uso, desde la raíz del repositorio (necesita el crudo de IBM; ver datos/preparar/rotacion.py):
    python3 datos/preparar/prueba_subida.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2027
FRACCION_VACIA = 0.20
RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "datos/crudo/rotacion_ibm.csv"

AREAS = {"ventas": "Sales", "investigacion": "Research & Development", "rrhh": "Human Resources"}
CARGOS = {
    "Sales Executive": "Ejecutivo de ventas", "Sales Representative": "Representante de ventas", "Manager": "Gerente",
    "Healthcare Representative": "Representante de salud", "Laboratory Technician": "Técnico de laboratorio",
    "Manufacturing Director": "Director de manufactura", "Research Director": "Director de investigación",
    "Research Scientist": "Científico investigador", "Human Resources": "Analista de personas",
}
AREAS_ES = {"Sales": "Ventas", "Research & Development": "Investigación y desarrollo", "Human Resources": "Personas"}
# nombre en el archivo de prueba ← columna original (en el orden en que quedan)
COLUMNAS = {
    "n_empleado": "EmployeeNumber", "area": "Department", "cargo": "JobRole", "edad": "Age",
    "sueldo_mensual": "MonthlyIncome", "horas_extra": "OverTime", "anios_en_empresa": "YearsAtCompany",
    "enc_trabajo": "JobSatisfaction", "enc_ambiente": "EnvironmentSatisfaction", "distancia_km": "DistanceFromHome",
    "enc_equilibrio": "WorkLifeBalance", "empresas_previas": "NumCompaniesWorked", "enc_relaciones": "RelationshipSatisfaction",
    "renuncio": "Attrition",
}

d = pd.read_csv(CRUDO, encoding="utf-8-sig")
assert d.shape == (1470, 35), d.shape
rng = np.random.default_rng(SEMILLA)

for nombre, area in AREAS.items():
    parte = d[d["Department"] == area].reset_index(drop=True)
    salida = pd.DataFrame({nuevo: parte[viejo] for nuevo, viejo in COLUMNAS.items()})
    salida["cargo"] = salida["cargo"].map(CARGOS)
    salida["area"] = salida["area"].map(AREAS_ES)
    for col in ("horas_extra", "renuncio"):
        salida[col] = salida[col].map({"Yes": "Sí", "No": "No"})
    assert salida.notna().all().all()

    vacias = np.sort(rng.choice(len(salida), size=int(round(FRACCION_VACIA * len(salida))), replace=False))
    verdad = pd.DataFrame({"id": salida["n_empleado"].iloc[vacias].to_numpy(),
                           "objetivo": salida["renuncio"].iloc[vacias].to_numpy()})
    salida["renuncio"] = salida["renuncio"].astype(object)
    salida.loc[vacias, "renuncio"] = np.nan

    archivo = RAIZ / f"datos/demo/subida_rotacion_{nombre}.csv"
    salida.to_csv(archivo, index=False)
    verdad.to_csv(RAIZ / f"datos/demo/subida_rotacion_{nombre}_verdad.csv", index=False)
    quedan = salida["renuncio"].dropna().value_counts()
    print(f"{archivo.relative_to(RAIZ)}: {len(salida)} personas, {salida['cargo'].nunique()} cargos, "
          f"{len(vacias)} por decidir; con respuesta {quedan.to_dict()}")
