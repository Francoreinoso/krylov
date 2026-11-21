"""Calibración de la red de `supervivencia` en simulaciones nuevas: SBC y cobertura.

SBC (simulation-based calibration): para cada dataset simulado nuevo se conoce el θ verdadero; si
q(θ | D) está calibrado, el rango del valor verdadero entre las muestras del posterior es uniforme,
parámetro por parámetro. Se reporta además la cobertura del intervalo de 90% (por rangos), por
grupos de n y de número de cargos, y cuánto se contrae el posterior respecto del prior (0 = no
aprendió nada, 1 = lo sabe exacto).

    uv run python -m motor.supervivencia.validar --sbc 200

Lee el punto de guardado `motor/checkpoints/supervivencia/ultimo.pt` y escribe `sbc.json` al lado.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from motor.comun.validacion import dentro_del_rango
from motor.supervivencia import red as red_sv
from motor.supervivencia import simular
from motor.supervivencia.entrenar import CARPETA
from nucleo import supervivencia as nucleo_sv

N_CHICO = 600          # frontera entre «n chico» y «n grande» para la cobertura por grupos
CARGOS_POCOS = 6       # y entre pocos y muchos cargos
CHI2_99_GL9 = 21.67    # percentil 99 de un χ² con 9 grados de libertad


def cargar_red(ruta: Path) -> tuple[red_sv.RedSupervivencia, dict]:
    """Red en modo evaluación desde un punto de guardado del bucle común."""
    estado = torch.load(ruta, map_location="cpu", weights_only=False)
    red = red_sv.RedSupervivencia(**red_sv.ARQUITECTURA)
    red.load_state_dict(estado["modulo"])
    return red.eval(), estado


def sbc(red: red_sv.RedSupervivencia, datasets: int, muestras: int = 99, semilla: int = 10_000, lote: int = 25) -> dict:
    """SBC y cobertura sobre `datasets` simulaciones nuevas (semilla distinta a la del entrenamiento).

    Por parámetro: rango medio (0,5 sin sesgo), χ² de uniformidad de los rangos en 10 tramos, cobertura del intervalo
    de 90% (contada por rangos: exacta con 99 muestras) y contracción respecto del prior. La cobertura va también por
    grupos: empresas chicas y grandes, con pocos y con muchos cargos.
    """
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    rangos, tamanos, cargos, varianza_post = [], [], [], []
    for _ in range(int(np.ceil(datasets / lote))):
        n = simular.muestrear_n(rng, config)
        simulado = simular.simular(rng, lote, n, config, reales)
        filas, grupo, theta = red_sv.lote_a_tensores(simulado)
        post = red.muestrear(filas, grupo, muestras).numpy()             # (muestras, lote, 32)
        rangos.append((post < theta.numpy()).sum(axis=0))                 # 0..muestras
        varianza_post.append(post.var(axis=0))
        tamanos.append(np.full(lote, n))
        cargos.append(np.array([len(np.unique(g)) for g in simulado["grupo"]]))
    rangos, tamanos = np.concatenate(rangos)[:datasets], np.concatenate(tamanos)[:datasets]
    cargos, varianza_post = np.concatenate(cargos)[:datasets], np.concatenate(varianza_post)[:datasets]
    dentro = dentro_del_rango(rangos, muestras)
    contraccion = 1.0 - varianza_post.mean(axis=0) / red.flujo.escala_theta.numpy() ** 2

    por_parametro = {}
    for j, nombre in enumerate(nucleo_sv.NOMBRES_THETA):
        tramos = np.histogram(rangos[:, j], bins=10, range=(0, muestras + 1))[0]
        chi2 = float(((tramos - len(rangos) / 10) ** 2 / (len(rangos) / 10)).sum())
        por_parametro[nombre] = {"rango_medio": round(float(rangos[:, j].mean() / muestras), 3), "chi2_uniformidad": round(chi2, 1),
                                 "uniforme_al_99": chi2 < CHI2_99_GL9, "cobertura_90": round(float(dentro[:, j].mean()), 3),
                                 "contraccion": round(float(contraccion[j]), 3)}
    grupos = {f"n hasta {N_CHICO}": tamanos <= N_CHICO, f"n sobre {N_CHICO}": tamanos > N_CHICO,
              f"hasta {CARGOS_POCOS} cargos": cargos <= CARGOS_POCOS, f"más de {CARGOS_POCOS} cargos": cargos > CARGOS_POCOS}
    por_grupo = {nombre: round(float(dentro[m].mean()), 3) for nombre, m in grupos.items() if m.any()}
    peor = min(por_grupo, key=por_grupo.get)
    coberturas = [v["cobertura_90"] for v in por_parametro.values()]
    return {
        "casos_validacion": int(len(rangos)), "muestras_por_dataset": muestras,
        "cobertura_90": round(float(np.mean(coberturas)), 3),
        "cobertura_90_peor_grupo": por_grupo[peor], "peor_grupo": peor, "cobertura_90_por_grupo": por_grupo,
        "cobertura_90_peor_parametro": {"nombre": min(por_parametro, key=lambda k: por_parametro[k]["cobertura_90"]), "valor": min(coberturas)},
        "parametros_uniformes_al_99": int(sum(v["uniforme_al_99"] for v in por_parametro.values())),
        "contraccion_media": round(float(contraccion.mean()), 3), "theta": por_parametro,
    }


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--sbc", type=int, default=200, help="datasets simulados nuevos")
    analizador.add_argument("--muestras", type=int, default=99, help="muestras del posterior por dataset")
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
    for nombre, v in resultado["theta"].items():
        print(f"{nombre:>12}  rango medio {v['rango_medio']:.2f}  χ² {v['chi2_uniformidad']:5.1f}  cobertura90 {v['cobertura_90']:.2f}  contracción {v['contraccion']:+.2f}")
    resumen = {k: v for k, v in resultado.items() if k != "theta"}
    print(json.dumps(resumen, indent=1, ensure_ascii=False))
    print(f"→ {salida}")


if __name__ == "__main__":
    principal()
