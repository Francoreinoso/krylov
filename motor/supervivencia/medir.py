"""Mide cuánto simula y entrena este computador con la red real de `supervivencia`.

    uv run python -m motor.supervivencia.medir                      # simulador + cpu + mps, ~1 minuto
    uv run python -m motor.supervivencia.medir --dispositivos cpu   # solo procesador

Imprime datasets simulados por segundo y pasos de entrenamiento por segundo, por dispositivo y por
tamaño de lote. No debe haber nada entrenando en el computador mientras corre.
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import torch

from motor.supervivencia import red as red_sv
from motor.supervivencia import simular


def medir_simulador(config: dict, reales, lote: int, repeticiones: int = 40) -> float:
    """Datasets simulados por segundo (NumPy, un proceso), con n al azar en el rango del caso."""
    rng = np.random.default_rng(0)
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        simular.simular(rng, lote, simular.muestrear_n(rng, config), config, reales)
    return lote * repeticiones / (time.perf_counter() - inicio)


def medir_entrenamiento(config: dict, reales, dispositivo: str, lote: int, pasos: int) -> float:
    """Pasos por segundo del entrenamiento completo (simular + red), tras 20 pasos de calentamiento."""
    red = red_sv.construir(config).to(dispositivo)
    optimizador = torch.optim.AdamW(red.parameters(), lr=5e-4)
    rng = np.random.default_rng(0)
    for paso in range(20 + pasos):
        if paso == 20:
            if dispositivo == "mps":
                torch.mps.synchronize()
            inicio = time.perf_counter()
        lote_np = simular.simular(rng, lote, simular.muestrear_n(rng, config), config, reales)
        perdida = red.perdida(*red_sv.lote_a_tensores(lote_np, dispositivo))
        optimizador.zero_grad(set_to_none=True)
        perdida.backward()
        optimizador.step()
    if dispositivo == "mps":
        torch.mps.synchronize()
    return pasos / (time.perf_counter() - inicio)


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--dispositivos", nargs="+", default=["cpu", "mps"])
    analizador.add_argument("--lotes", nargs="+", type=int, default=[32, 64])
    analizador.add_argument("--pasos", type=int, default=200)
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    print(f"torch {torch.__version__}, hilos {torch.get_num_threads()}")
    for lote in a.lotes:
        print(f"simulador · lote {lote}: {medir_simulador(config, reales, lote):,.0f} datasets/s")
    for dispositivo in a.dispositivos:
        if dispositivo == "mps" and not torch.backends.mps.is_available():
            print("mps no está disponible en este computador")
            continue
        for lote in a.lotes:
            pasos_s = medir_entrenamiento(config, reales, dispositivo, lote, a.pasos)
            print(f"entrenar · {dispositivo} · lote {lote}: {pasos_s:.1f} pasos/s = {pasos_s * lote:,.0f} datasets/s")


if __name__ == "__main__":
    principal()
