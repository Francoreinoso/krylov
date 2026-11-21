"""Predictivo a priori de `espacial` contra el archivo real del caso, antes de entrenar.

    uv run python -m motor.espacial.predictivo

Calcula unos pocos resúmenes del terreno real (ya pasado por `nucleo.preproceso`) y dice
en qué percentil caen entre los mismos resúmenes de terrenos simulados con el prior. Si
el archivo real cae fuera de lo simulado, la red lo vería como algo que nunca practicó:
ahí se ajusta el prior, no después.
"""

from __future__ import annotations

import csv
import json

import numpy as np
import torch

from motor.espacial.simular import Prior, simular
from nucleo.preproceso import preparar_terreno


def resumenes(canales: np.ndarray) -> dict[str, np.ndarray]:
    """Resúmenes por terreno de un lote de canales (B, 3, 32, 32)."""
    valor, marca, raiz = canales[:, 0], canales[:, 1], canales[:, 2]
    n = marca.sum((1, 2))
    # Fuerza de la tendencia: correlación entre lo medido y √dist en los bloques medidos.
    r_media = (raiz * marca).sum((1, 2)) / n
    r_centrada = (raiz - r_media[:, None, None]) * marca
    r_desv = np.sqrt((r_centrada ** 2).sum((1, 2)) / n)
    correlacion = (valor * r_centrada).sum((1, 2)) / n / np.maximum(r_desv, 1e-6)
    # Continuidad: semivarianza entre bloques medidos vecinos (a un bloque), en unidades de la varianza de lo medido.
    pares_h, pares_v = marca[:, :, 1:] * marca[:, :, :-1], marca[:, 1:, :] * marca[:, :-1, :]
    dif = ((valor[:, :, 1:] - valor[:, :, :-1]) ** 2 * pares_h).sum((1, 2)) + ((valor[:, 1:, :] - valor[:, :-1, :]) ** 2 * pares_v).sum((1, 2))
    pares = pares_h.sum((1, 2)) + pares_v.sum((1, 2))
    return {
        "bloques_medidos": n, "correlacion_con_raiz_dist": correlacion, "raiz_dist_media_en_lo_medido": r_media,
        "semivarianza_vecinos": np.where(pares >= 5, 0.5 * dif / np.maximum(pares, 1), np.nan),
        "pares_de_vecinos": pares, "valor_maximo_abs": np.abs(valor).max((1, 2)),
    }


def leer_csv(ruta: str) -> dict[str, np.ndarray]:
    with open(ruta) as f:
        filas = list(csv.DictReader(f))
    return {k: np.array([float(fila[k]) for fila in filas]) for k in filas[0]}


def main() -> None:
    puntos, grilla = leer_csv("datos/demo/terreno.csv"), leer_csv("datos/demo/terreno_grilla.csv")
    real = preparar_terreno(puntos["x"], puntos["y"], puntos["zinc"], transformacion="log", grilla=grilla)
    del_real = {k: float(v[0]) for k, v in resumenes(real["canales"][None]).items()}

    simulados = simular(4000, Prior(), torch.Generator().manual_seed(0))
    con_tendencia = (simulados["tiene_tendencia"] == 1).numpy()
    de_simulados = resumenes(simulados["canales"].numpy()[con_tendencia])

    salida = {"geometria": real["geometria"], "bloques_del_terreno": int(real["dentro"].sum()),
              "media_log": round(real["media"], 3), "escala_log": round(real["escala"], 3), "resumenes": {}}
    for k, v in del_real.items():
        s = de_simulados[k][~np.isnan(de_simulados[k])]
        salida["resumenes"][k] = {"real": round(v, 3), "percentil_en_lo_simulado": round(float((s < v).mean()) * 100, 1),
                                  "simulado_p05_p50_p95": [round(float(q), 3) for q in np.quantile(s, [0.05, 0.5, 0.95])]}
    print(json.dumps(salida, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
