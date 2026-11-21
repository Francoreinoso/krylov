"""Validación del motor `estados` en carteras simuladas nuevas: SBC y cobertura.

    uv run python -m motor.estados.validar --sbc 200

SBC (calibración basada en simulación): para cada cartera simulada con θ conocido se sacan
L muestras de q(θ | D) y se cuenta cuántas quedan bajo el valor verdadero; si el posterior
amortizado está calibrado, ese rango es uniforme. Por parámetro: rango medio (0,5 sin
sesgo), χ² de uniformidad en 10 tramos, cobertura del intervalo de 90%, contracción y recuperación (correlación entre el
valor verdadero y la media del posterior)
respecto del prior. La cobertura se da también por grupos: carteras chicas y grandes.
Además, lo que se decide: la probabilidad de impago de los clientes por decidir, con el
filtro forward sobre las muestras de θ, contra lo que pasó en la simulación.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from motor.comun.entrenar import cargar_punto
from motor.comun.validacion import dentro_del_rango
from motor.estados import simular
from motor.estados.red import RedEstados
from nucleo import estados as nucleo_es
from nucleo.estados import NOMBRES_THETA

PUNTO = simular.RAIZ / "motor" / "checkpoints" / "estados" / "ultimo.pt"
CHI2_99_GL9 = 21.67


def sbc(red: RedEstados, carteras: int, muestras: int = 99, semilla: int = 10_000) -> dict:
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    red = red.cpu().eval()
    reales = simular.cargar_covariables_reales()
    rangos, dentro, anchos, n_de, calibracion = [], [], [], [], []
    medias, verdades = [], []
    for inicio in range(0, carteras, 10):                         # de a 10 carteras, cada tanda con su n
        b, n = min(10, carteras - inicio), simular.muestrear_n(rng)
        lote = simular.simular(rng, b, n, reales)
        with torch.no_grad():
            posterior = red.muestrear(torch.from_numpy(lote["filas"]), muestras).numpy()      # (muestras, b, 33)
        verdad = lote["theta"]
        rangos.append((posterior < verdad).sum(0))
        dentro.append(dentro_del_rango(rangos[-1], muestras))            # cobertura del 90% por rangos: exacta con 99 muestras
        anchos.append(posterior.var(0))
        medias.append(posterior.mean(0)), verdades.append(verdad)
        n_de += [n] * b
        # Lo que se decide, en la primera cartera de la tanda: p de impago de los clientes por decidir.
        datos = {k: lote[k][0] for k in ("nivel", "uso", "pago_cero", "log_pago", "x")}
        p = nucleo_es.probabilidad_de_impago(posterior[:32, 0], datos).mean(axis=1)
        por_decidir = np.isnan(lote["impago"][0])
        calibracion.append(np.c_[p[por_decidir], lote["impago_real"][0][por_decidir]])
    medias, verdades = np.concatenate(medias), np.concatenate(verdades)
    rangos, dentro, anchos, n_de = np.concatenate(rangos), np.concatenate(dentro), np.concatenate(anchos), np.array(n_de)
    calibracion = np.concatenate(calibracion)

    por_parametro = {}
    for j, nombre in enumerate(NOMBRES_THETA):
        tramos = np.histogram(rangos[:, j], bins=10, range=(0, muestras + 1))[0]
        chi2 = float(((tramos - carteras / 10) ** 2 / (carteras / 10)).sum())
        por_parametro[nombre] = {"rango_medio": round(float(rangos[:, j].mean() / muestras), 3), "chi2_uniformidad": round(chi2, 1),
                                 "uniforme_al_99": chi2 < CHI2_99_GL9, "cobertura_90": round(float(dentro[:, j].mean()), 3),
                                 "contraccion": round(float(1 - anchos[:, j].mean() / simular.DESVS[j] ** 2), 3),
                                 "recuperacion": round(float(np.corrcoef(verdades[:, j], medias[:, j])[0, 1]), 3)}
    tramos_p = []
    for bajo, alto in ((0, 0.1), (0.1, 0.2), (0.2, 0.35), (0.35, 0.6), (0.6, 1.01)):
        en = (calibracion[:, 0] >= bajo) & (calibracion[:, 0] < alto)
        if en.sum() >= 30:
            tramos_p.append({"dijimos": round(float(calibracion[en, 0].mean()), 3), "paso": round(float(calibracion[en, 1].mean()), 3), "n": int(en.sum())})
    coberturas = [v["cobertura_90"] for v in por_parametro.values()]
    return {"carteras": carteras, "muestras_por_cartera": muestras, "cobertura_90_media": round(float(np.mean(coberturas)), 3),
            "cobertura_90_peor_parametro": [min(por_parametro, key=lambda k: por_parametro[k]["cobertura_90"]), min(coberturas)],
            "parametros_uniformes_al_99": int(sum(v["uniforme_al_99"] for v in por_parametro.values())),
            "contraccion_media": round(float(np.mean([v["contraccion"] for v in por_parametro.values()])), 3),
            "cobertura_90_por_grupo": {"n_menor_1000": round(float(dentro[n_de < 1000].mean()), 3) if (n_de < 1000).any() else None,
                                       "n_1000_o_mas": round(float(dentro[n_de >= 1000].mean()), 3) if (n_de >= 1000).any() else None},
            "impago_por_decidir": tramos_p, "theta": por_parametro}


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--sbc", type=int, default=200, help="carteras simuladas nuevas")
    analizador.add_argument("--punto", default=str(PUNTO))
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)
    red = RedEstados()
    estado = cargar_punto(Path(a.punto), red)
    salida = {"punto": a.punto, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
              "minutos": round(estado["segundos"] / 60, 1), **sbc(red, a.sbc)}
    (Path(a.punto).parent / f"sbc_paso_{estado['pasos']:07d}.json").write_text(json.dumps(salida, indent=2) + "\n")
    print(json.dumps(salida, indent=2))


if __name__ == "__main__":
    principal()
