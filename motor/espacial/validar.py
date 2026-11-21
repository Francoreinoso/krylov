"""Validación del motor `espacial` en terrenos simulados nuevos: SBC y cobertura.

    uv run python -m motor.espacial.validar --sbc 200

**SBC** (calibración basada en simulación): para cada terreno simulado con θ conocido se
sacan L muestras de q(θ | D) y se cuenta cuántas quedan bajo el valor verdadero. Si el
posterior amortizado está calibrado, ese rango es uniforme entre 0 y L. Se reporta, por
parámetro: el rango medio (0,5 si no hay sesgo), un χ² de uniformidad en 10 tramos, la
cobertura del intervalo de 90% y la contracción del posterior respecto del prior.

Para la cabeza de mapa, sobre los bloques **sin medición**: error cuadrático medio (en
desviaciones estándar de lo medido), cobertura del intervalo de 90% y log-verosimilitud,
en total y por grupos (pocas o muchas mediciones, con o sin tendencia).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

from motor.comun.entrenar import cargar_punto
from motor.comun.validacion import dentro_del_rango
from motor.espacial.exportar import PUNTO, red_desde_config
from motor.espacial.simular import NOMBRES_THETA, Prior, simular

CHI2_99_GL9 = 21.67       # percentil 99 de χ² con 9 grados de libertad


def sbc(red, n_terrenos: int, muestras: int = 99, semilla: int = 12345) -> dict:
    gen = torch.Generator().manual_seed(semilla)
    torch.manual_seed(semilla)
    red = red.cpu().eval()
    lote = simular(n_terrenos, Prior(), gen, con_tendencia=red.canales_entrada == 3)
    with torch.no_grad():
        media, log_desv, resumen = red(lote["canales"])
        posterior = red.flujo.muestrear(resumen, muestras)               # (muestras, n, 7)
    verdad = lote["theta"]

    rangos = (posterior < verdad).sum(0).numpy()                         # (n, 7), entre 0 y `muestras`
    dentro = torch.from_numpy(dentro_del_rango(rangos, muestras)).float()     # cobertura del 90% por rangos: exacta con 99 muestras
    z = ((posterior.mean(0) - verdad) / posterior.std(0)).numpy()
    contraccion = 1 - (posterior.var(0).mean(0) / verdad.var(0)).numpy()
    por_parametro = {}
    for j, nombre in enumerate(NOMBRES_THETA):
        tramos = np.histogram(rangos[:, j], bins=10, range=(0, muestras + 1))[0]
        chi2 = float(((tramos - n_terrenos / 10) ** 2 / (n_terrenos / 10)).sum())
        por_parametro[nombre] = {
            "rango_medio": round(float(rangos[:, j].mean() / muestras), 3),
            "chi2_uniformidad": round(chi2, 1), "uniforme_al_99": chi2 < CHI2_99_GL9,
            "cobertura_90": round(float(dentro[:, j].mean()), 3),
            "z_media": round(float(z[:, j].mean()), 2), "z_desv": round(float(z[:, j].std()), 2),
            "contraccion": round(float(contraccion[j]), 3),
        }

    # Cabeza de mapa, en los bloques sin medición.
    sin_medir = lote["canales"][:, 1] == 0
    error = lote["campo"] - media
    estandarizado = error * torch.exp(-log_desv)
    cubre = (estandarizado.abs() < 1.645).float()
    log_ver = -(0.5 * estandarizado ** 2 + log_desv + 0.9189385)

    def resumen_mapa(filas: torch.Tensor) -> dict:
        m = sin_medir & filas[:, None, None]
        return {"terrenos": int(filas.sum()), "recm": round(float((error[m] ** 2).mean().sqrt()), 3),
                "cobertura_90": round(float(cubre[m].mean()), 3), "log_verosimilitud": round(float(log_ver[m].mean()), 3)}

    todos = torch.ones(n_terrenos, dtype=torch.bool)
    grupos = {"todos": todos, "n_menor_100": lote["n"] < 100, "n_100_o_mas": lote["n"] >= 100,
              "con_tendencia": lote["tiene_tendencia"] == 1, "sin_tendencia": lote["tiene_tendencia"] == 0,
              "muy pocas mediciones (menos de 60)": lote["n"] < 60,
              "mucho ruido (más que la variación del campo)": verdad[:, 4] > verdad[:, 3],
              "alcance largo (más de 9 bloques)": verdad[:, 0] > math.log(9.0)}
    mapa = {nombre: resumen_mapa(filas) for nombre, filas in grupos.items() if filas.any()}
    theta_por_grupo = {nombre: {"terrenos": int(filas.sum()), "cobertura_90": round(float(dentro[filas].mean()), 3)}
                       for nombre, filas in grupos.items() if filas.sum() >= 20}
    # Referencia sin red: predecir en todas partes la media de lo medido (0) con desviación 1.
    mapa["referencia_recm_sin_red"] = round(float((lote["campo"][sin_medir] ** 2).mean().sqrt()), 3)
    return {"terrenos": n_terrenos, "muestras_por_terreno": muestras, "theta": por_parametro, "mapa": mapa,
            "theta_por_grupo": theta_por_grupo,
            "cobertura_90_theta_media": round(float(dentro.mean()), 3)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sbc", type=int, default=200, help="cuántos terrenos simulados nuevos")
    p.add_argument("--punto", type=Path, default=PUNTO)
    a = p.parse_args()
    estado = torch.load(a.punto, map_location="cpu", weights_only=False)
    red = red_desde_config(estado["config"])
    cargar_punto(a.punto, red)
    salida = {"punto": str(a.punto), "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
              "minutos": round(estado["segundos"] / 60, 1), **sbc(red, a.sbc)}
    (a.punto.parent / f"sbc_paso_{estado['pasos']:07d}.json").write_text(json.dumps(salida, indent=2) + "\n")
    print(json.dumps(salida, indent=2))


if __name__ == "__main__":
    main()
