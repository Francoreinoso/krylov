"""Calibración de la red de `supervivencia` en simulaciones nuevas: SBC y cobertura.

SBC (simulation-based calibration): para cada dataset simulado nuevo se conoce el θ verdadero; si
q(θ | D) está calibrado, el rango del valor verdadero entre las muestras del posterior es uniforme,
parámetro por parámetro. Se reporta además la cobertura del intervalo de 90%, por grupos de n, y
cuánto se contrae el posterior respecto del prior (0 = no aprendió nada, 1 = lo sabe exacto).

    uv run python -m motor.supervivencia.validar --sbc 200

Lee el punto de guardado `motor/checkpoints/supervivencia/ultimo.pt` y escribe `sbc.json` al lado.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from motor.supervivencia import red as red_sv
from motor.supervivencia import simular
from motor.supervivencia.entrenar import CARPETA
from nucleo import supervivencia as nucleo_sv

N_CHICO = 600          # frontera entre «n chico» y «n grande» para la cobertura por grupos


def cargar_red(ruta: Path) -> tuple[red_sv.RedSupervivencia, dict]:
    """Red en modo evaluación desde un punto de guardado del bucle común."""
    estado = torch.load(ruta, map_location="cpu", weights_only=False)
    red = red_sv.RedSupervivencia(**red_sv.ARQUITECTURA)
    red.load_state_dict(estado["modulo"])
    return red.eval(), estado


def sbc(red: red_sv.RedSupervivencia, datasets: int, muestras: int = 200, semilla: int = 10_000,
        lote: int = 25) -> dict:
    """SBC y cobertura sobre `datasets` simulaciones nuevas (semilla distinta a la del entrenamiento)."""
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    rangos, dentro, tamanos, varianza_post = [], [], [], []
    for _ in range(int(np.ceil(datasets / lote))):
        n = simular.muestrear_n(rng, config)
        filas, grupo, theta = red_sv.lote_a_tensores(simular.simular(rng, lote, n, config, reales))
        post = red.muestrear(filas, grupo, muestras).numpy()             # (muestras, lote, 32)
        verdad = theta.numpy()
        rangos.append((post < verdad).sum(axis=0))                        # 0..muestras
        bajo, alto = np.quantile(post, [0.05, 0.95], axis=0)
        dentro.append((verdad >= bajo) & (verdad <= alto))
        varianza_post.append(post.var(axis=0))
        tamanos.append(np.full(lote, n))
    rangos, dentro = np.concatenate(rangos)[:datasets], np.concatenate(dentro)[:datasets]
    tamanos, varianza_post = np.concatenate(tamanos)[:datasets], np.concatenate(varianza_post)[:datasets]

    # Distancia de Kolmogorov-Smirnov de los rangos a la uniforme, por parámetro (límite al 5%: 1,36/√N).
    u = np.sort((rangos + 0.5) / (muestras + 1), axis=0)
    grilla = (np.arange(1, len(u) + 1) / len(u))[:, None]
    ks = np.maximum(np.abs(grilla - u), np.abs(grilla - 1 / len(u) - u)).max(axis=0)
    limite_ks = 1.36 / np.sqrt(len(u))
    contraccion = 1.0 - varianza_post.mean(axis=0) / red.flujo.escala_theta.numpy() ** 2
    cobertura = dentro.mean(axis=0)

    grupos = {f"n hasta {N_CHICO}": tamanos <= N_CHICO, f"n sobre {N_CHICO}": tamanos > N_CHICO}
    por_grupo = {nombre: float(dentro[m].mean()) for nombre, m in grupos.items() if m.any()}
    peor = min(por_grupo, key=por_grupo.get)
    return {
        "casos_validacion": int(len(u)), "muestras_por_dataset": muestras,
        "cobertura_90": float(cobertura.mean()),
        "cobertura_90_peor_grupo": por_grupo[peor], "peor_grupo": peor, "cobertura_90_por_grupo": por_grupo,
        "cobertura_90_peor_parametro": {"nombre": nucleo_sv.NOMBRES_THETA[int(cobertura.argmin())],
                                        "valor": float(cobertura.min())},
        "ks_limite": float(limite_ks), "parametros_con_ks_sobre_el_limite": int((ks > limite_ks).sum()),
        "contraccion_media": float(contraccion.mean()),
        "por_parametro": {nombre: {"cobertura_90": round(float(c), 3), "ks": round(float(k), 3),
                                   "contraccion": round(float(r), 3)}
                          for nombre, c, k, r in zip(nucleo_sv.NOMBRES_THETA, cobertura, ks, contraccion)},
    }


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--sbc", type=int, default=200, help="datasets simulados nuevos")
    analizador.add_argument("--muestras", type=int, default=200, help="muestras del posterior por dataset")
    analizador.add_argument("--punto", default=str(CARPETA / "ultimo.pt"), help="punto de guardado a validar")
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)

    red, estado = cargar_red(Path(a.punto))
    resultado = sbc(red, a.sbc, a.muestras)
    resultado.update(pasos=estado["pasos"], simulaciones_entrenamiento=estado["datasets_simulados"],
                     entrenamiento_min=round(estado["segundos"] / 60, 1))
    salida = Path(a.punto).with_name("sbc.json")
    salida.write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
    for nombre, v in resultado["por_parametro"].items():
        print(f"{nombre:>12}  cobertura90 {v['cobertura_90']:.2f}  ks {v['ks']:.2f}  contracción {v['contraccion']:+.2f}")
    resumen = {k: v for k, v in resultado.items() if k != "por_parametro"}
    print(json.dumps(resumen, indent=1, ensure_ascii=False))
    print(f"→ {salida}")


if __name__ == "__main__":
    principal()
