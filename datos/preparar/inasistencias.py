"""Caso de inasistencias (S-N1): deja datos/demo/inasistencias.csv y datos/demo/inasistencias_verdad.csv.

Fuente: «Medical Appointment No Shows» (Kaggle, joniarroba/noshowappointments), 110.527 citas médicas en Vitória,
Brasil, 2016. Licencia CC BY-NC-SA 4.0 (no comercial): **los dos CSV que deja este script no se suben al repositorio**
(están en .gitignore). El caso vive en local y en las respuestas precalculadas, con la atribución en `origen_datos`.
Copia usada: la de GitHub en TokoniK/exploratory-data-analysis (Git LFS), el mismo archivo de Kaggle:
10.739.535 bytes, SHA-256 9132d3e7d0246617df9041d3764f20ad6f08e7b0d9f0997fa254fc5e52eda27d.

Qué hace (casos/inasistencias.yaml, decisión D-26):
- Calcula `dias_de_espera` (días entre ScheduledDay y AppointmentDay) y `dia_semana` (0 = lunes).
- Descarta las esperas negativas (5), las citas en sábado (39) y las edades negativas (1).
- Elige 30 barrios al azar con semilla fija, entre los que tienen al menos 100 citas (74 de 81): un barrio con
  menos no alcanza a tener varios pacientes en la muestra, y el modelo necesita varios pacientes por barrio.
- Dentro de cada barrio toma **pacientes completos** (todas sus citas; cada paciente tiene citas en un solo barrio),
  en orden al azar, hasta 66 citas por barrio: en total, menos de 2.000 (el tope del contrato). Nunca filas sueltas.
- Comprueba que al menos un tercio de los pacientes tenga dos o más citas.
- Deja vacía la respuesta (`No-show`) en un 20% de las citas, elegido al azar sin mirarla, y guarda esa verdad aparte.

Uso, desde la raíz del repositorio:
    mkdir -p datos/crudo/inasistencias
    curl -sSL -o datos/crudo/inasistencias/KaggleV2-May-2016.csv "https://media.githubusercontent.com/media/TokoniK/exploratory-data-analysis/4fd5b76e388ddb693e1ef02f30d4629a0e0daa50/data/Database_No_show_appointments/noshowappointments-kagglev2-may-2016.csv"
    shasum -a 256 datos/crudo/inasistencias/KaggleV2-May-2016.csv   # tiene que dar el SHA-256 de arriba
    uv run python datos/preparar/inasistencias.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
N_BARRIOS = 30
MIN_CITAS_BARRIO = 100
CUOTA_POR_BARRIO = 66          # 30 × 66 = 1.980 citas como máximo
FRACCION_VACIA = 0.20
RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "datos/crudo/inasistencias/KaggleV2-May-2016.csv"
SALIDA = RAIZ / "datos/demo/inasistencias.csv"
VERDAD = RAIZ / "datos/demo/inasistencias_verdad.csv"

COLUMNAS_DEL_CASO = ["AppointmentID", "No-show", "PatientId", "Neighbourhood", "dias_de_espera", "dia_semana",
                     "SMS_received", "Age", "Scholarship", "Hipertension", "Diabetes", "Alcoholism"]

d = pd.read_csv(CRUDO)
assert d.shape == (110527, 14), d.shape
assert d["AppointmentID"].is_unique

# PatientId viene como número decimal; se escribe como texto para no perder dígitos.
d["PatientId"] = d["PatientId"].map(lambda x: f"{x:.0f}" if float(x).is_integer() else repr(x))

agendada = pd.to_datetime(d["ScheduledDay"]).dt.normalize()
cita = pd.to_datetime(d["AppointmentDay"]).dt.normalize()
d["dias_de_espera"] = (cita - agendada).dt.days
d["dia_semana"] = cita.dt.day_of_week

antes = len(d)
d = d[(d["dias_de_espera"] >= 0) & (d["dia_semana"] != 5) & (d["Age"] >= 0)].reset_index(drop=True)
descartadas = antes - len(d)
assert descartadas == 45, descartadas  # 5 esperas negativas + 39 sábados + 1 edad negativa
assert (d.groupby("PatientId")["Neighbourhood"].nunique() == 1).all()

rng = np.random.default_rng(SEMILLA)

# 1. Treinta barrios al azar entre los que tienen al menos 100 citas.
citas_por_barrio = d["Neighbourhood"].value_counts()
elegibles = np.sort(citas_por_barrio[citas_por_barrio >= MIN_CITAS_BARRIO].index.to_numpy())
barrios = rng.choice(elegibles, size=N_BARRIOS, replace=False)

# 2. Dentro de cada barrio, pacientes completos en orden al azar hasta la cuota.
partes = []
for barrio in barrios:
    del_barrio = d[d["Neighbourhood"] == barrio]
    pacientes = rng.permutation(np.sort(del_barrio["PatientId"].unique().astype(str)))
    tamanos = del_barrio.groupby("PatientId").size()
    elegidos, total = [], 0
    for p in pacientes:
        n = int(tamanos[p])
        if total + n <= CUOTA_POR_BARRIO:
            elegidos.append(p)
            total += n
        if total == CUOTA_POR_BARRIO:
            break
    partes.append(del_barrio[del_barrio["PatientId"].isin(elegidos)])
muestra = pd.concat(partes).sort_values("AppointmentID").reset_index(drop=True)

citas_por_paciente = muestra.groupby("PatientId").size()
frac_varias = float((citas_por_paciente >= 2).mean())
assert len(muestra) <= 2000 and muestra["Neighbourhood"].nunique() == N_BARRIOS
assert frac_varias >= 1 / 3, frac_varias
faltan = [c for c in COLUMNAS_DEL_CASO if c not in muestra.columns]
assert not faltan, faltan

# 3. El 20% de las citas, elegido por posición sin mirar `No-show`.
n_vacias = int(round(FRACCION_VACIA * len(muestra)))
vacias = np.sort(rng.choice(len(muestra), size=n_vacias, replace=False))
verdad = pd.DataFrame({
    "id": muestra["AppointmentID"].iloc[vacias].to_numpy(),
    "objetivo": muestra["No-show"].iloc[vacias].to_numpy(),
})
demo = muestra.copy()
demo["No-show"] = demo["No-show"].astype(object)
demo.loc[vacias, "No-show"] = np.nan

quedan = demo["No-show"].dropna().value_counts()
assert set(quedan.index) == {"Yes", "No"} and set(verdad["objetivo"]) == {"Yes", "No"}

SALIDA.parent.mkdir(parents=True, exist_ok=True)
demo.to_csv(SALIDA, index=False)
verdad.to_csv(VERDAD, index=False)

print(f"descartadas: {descartadas} (5 esperas negativas, 39 sábados, 1 edad negativa)")
print(f"{SALIDA.relative_to(RAIZ)}: {len(demo)} citas, {demo['PatientId'].nunique()} pacientes, "
      f"{demo['Neighbourhood'].nunique()} barrios, {demo.shape[1]} columnas, {demo['No-show'].isna().sum()} por decidir")
print(f"pacientes con 2 o más citas: {frac_varias:.3f}; citas por barrio entre "
      f"{muestra.groupby('Neighbourhood').size().min()} y {muestra.groupby('Neighbourhood').size().max()}")
print(f"con respuesta: {quedan.to_dict()} (no llegó {quedan['Yes'] / quedan.sum():.3f}); "
      f"mismo día {float((muestra['dias_de_espera'] == 0).mean()):.3f}; con SMS {float(muestra['SMS_received'].mean()):.3f}")
print(f"{VERDAD.relative_to(RAIZ)}: {len(verdad)} filas, {verdad['objetivo'].value_counts().to_dict()}")
