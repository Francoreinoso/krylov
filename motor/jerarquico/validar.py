"""Validación del motor `jerarquico` en datasets simulados nuevos: SBC y cobertura.

    uv run python -m motor.jerarquico.validar --sbc 200

SBC (calibración basada en simulación): para cada dataset simulado con θ conocido se sacan L
muestras de q(θ | D) y se cuenta cuántas quedan bajo el valor verdadero; si el posterior
amortizado está calibrado, ese rango es uniforme. Por parámetro: rango medio (0,5 sin sesgo), χ²
de uniformidad en 10 tramos, cobertura del intervalo de 90% y contracción respecto del prior.
La cobertura se da también por grupos: pocos y muchos barrios, pocas y muchas citas.
Además, lo que se decide: la probabilidad de no llegar de las citas por decidir (muestras de θ
pasadas por la cuadratura anidada) contra lo que pasó en la simulación.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from motor.comun.entrenar import cargar_punto
from motor.comun.validacion import dentro_del_rango
from motor.jerarquico import simular
from motor.jerarquico.red import RedJerarquico
from nucleo import jerarquico as nucleo_jq
from nucleo.jerarquico import NOMBRES_THETA

PUNTO = simular.RAIZ / "motor" / "checkpoints" / "jerarquico" / "ultimo.pt"
CHI2_99_GL9 = 21.67


def sbc(red: RedJerarquico, datasets: int, muestras: int = 99, semilla: int = 10_000) -> dict:
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    red = red.cpu().eval()
    reales = simular.leer_real()
    rangos, dentro, anchos, citas_de, barrios_de, calibracion = [], [], [], [], [], []
    for inicio in range(0, datasets, 10):                         # de a 10 datasets, cada tanda con su tamaño
        b = min(10, datasets - inicio)
        citas, barrios = simular.muestrear_tamano(rng)
        lote = simular.simular(rng, b, citas, barrios, reales)
        with torch.no_grad():
            posterior = red.muestrear(torch.from_numpy(lote["filas"]), torch.from_numpy(lote["mascara"]), muestras).numpy()
        verdad = lote["theta"]
        rangos.append((posterior < verdad).sum(0))
        dentro.append(dentro_del_rango(rangos[-1], muestras))            # cobertura del 90% por rangos: exacta con 99 muestras
        anchos.append(posterior.var(0))
        citas_de += [citas] * b
        barrios_de += [barrios] * b
        if inicio % 50 == 0:                                      # lo que se decide, en un dataset de cada cinco tandas
            d = simular.a_filas_sueltas(lote, 0)
            p = nucleo_jq.paso_local(posterior[:32, 0].astype(np.float64), d["z"], d["respuesta"], d["paciente"], d["barrio_del_paciente"]).mean(axis=1)
            falta = np.isnan(d["respuesta"])
            calibracion.append(np.c_[p[falta], d["respuesta_real"][falta]])
    rangos, dentro, anchos = np.concatenate(rangos), np.concatenate(dentro), np.concatenate(anchos)
    citas_de, barrios_de, calibracion = np.array(citas_de), np.array(barrios_de), np.concatenate(calibracion)

    por_parametro = {}
    for j, nombre in enumerate(NOMBRES_THETA):
        tramos = np.histogram(rangos[:, j], bins=10, range=(0, muestras + 1))[0]
        chi2 = float(((tramos - datasets / 10) ** 2 / (datasets / 10)).sum())
        por_parametro[nombre] = {"rango_medio": round(float(rangos[:, j].mean() / muestras), 3), "chi2_uniformidad": round(chi2, 1),
                                 "uniforme_al_99": chi2 < CHI2_99_GL9, "cobertura_90": round(float(dentro[:, j].mean()), 3),
                                 "contraccion": round(float(1 - anchos[:, j].mean() / simular.DESVS[j] ** 2), 3)}
    tramos_p = []
    for bajo, alto in ((0, 0.1), (0.1, 0.2), (0.2, 0.35), (0.35, 0.6), (0.6, 1.01)):
        en = (calibracion[:, 0] >= bajo) & (calibracion[:, 0] < alto)
        if en.sum() >= 30:
            tramos_p.append({"dijimos": round(float(calibracion[en, 0].mean()), 3), "paso": round(float(calibracion[en, 1].mean()), 3), "n": int(en.sum())})
    coberturas = [v["cobertura_90"] for v in por_parametro.values()]
    def grupo(filtro):
        return round(float(dentro[filtro].mean()), 3) if filtro.any() else None
    return {"datasets": datasets, "muestras_por_dataset": muestras, "cobertura_90_media": round(float(np.mean(coberturas)), 3),
            "cobertura_90_peor_parametro": [min(por_parametro, key=lambda k: por_parametro[k]["cobertura_90"]), min(coberturas)],
            "parametros_uniformes_al_99": int(sum(v["uniforme_al_99"] for v in por_parametro.values())),
            "contraccion_media": round(float(np.mean([v["contraccion"] for v in por_parametro.values()])), 3),
            "cobertura_90_por_grupo": {"menos_de_20_barrios": grupo(barrios_de < 20), "20_barrios_o_mas": grupo(barrios_de >= 20),
                                       "menos_de_1700_citas": grupo(citas_de < 1700), "1700_citas_o_mas": grupo(citas_de >= 1700)},
            "no_llega_por_decidir": tramos_p, "theta": por_parametro}


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--sbc", type=int, default=200, help="datasets simulados nuevos")
    analizador.add_argument("--punto", default=str(PUNTO))
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)
    red = RedJerarquico()
    estado = cargar_punto(Path(a.punto), red)
    salida = {"punto": a.punto, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
              "minutos": round(estado["segundos"] / 60, 1), **sbc(red, a.sbc)}
    (Path(a.punto).parent / f"sbc_paso_{estado['pasos']:07d}.json").write_text(json.dumps(salida, indent=2) + "\n")
    print(json.dumps(salida, indent=2))


if __name__ == "__main__":
    principal()
