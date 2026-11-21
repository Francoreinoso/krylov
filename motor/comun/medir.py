"""Medición de rendimiento común a los motores de tabla (skill `medir-rendimiento`): simulador y pasos de entrenamiento.

Cada motor la llama desde su `medir.py` con dos funciones: una que simula un lote (NumPy, en el procesador) y otra
que arma la red para un dispositivo y devuelve la función de pérdida, con sus parámetros en el atributo `parametros`. Se mide con 20 pasos de calentamiento y, en
la GPU del Mac, sincronizando antes de parar el cronómetro. **Nada entrenando en este computador mientras se mide.**
"""

from __future__ import annotations

import json
import time
from typing import Callable

import torch


def _sincronizar(dispositivo: str) -> None:
    if dispositivo == "mps":
        torch.mps.synchronize()


def medir(motor_id: str, simular_lote: Callable[[], dict], preparar: Callable[[str], Callable[[dict], torch.Tensor]],
          datasets_por_lote: int, dispositivos: list[str], pasos: int = 100) -> list[dict]:
    """Imprime y devuelve una línea por medición: datasets simulados por segundo, y pasos por segundo en cada dispositivo."""
    simular_lote()
    inicio = time.time()
    for _ in range(20):
        simular_lote()
    filas = [{"motor": motor_id, "que": "simulador", "lote": datasets_por_lote, "datasets_por_s": round(20 * datasets_por_lote / (time.time() - inicio))}]
    print(json.dumps(filas[-1]), flush=True)
    for dispositivo in dispositivos:
        if dispositivo == "mps" and not torch.backends.mps.is_available():
            continue
        perdida_de = preparar(dispositivo)
        parametros = perdida_de.parametros
        optimizador = torch.optim.AdamW(parametros, lr=1e-4)

        def paso():
            optimizador.zero_grad(set_to_none=True)
            perdida_de(simular_lote()).backward()
            optimizador.step()

        for _ in range(20):
            paso()
        _sincronizar(dispositivo)
        inicio = time.time()
        for _ in range(pasos):
            paso()
        _sincronizar(dispositivo)
        segundos = time.time() - inicio
        filas.append({"motor": motor_id, "que": "entrenar", "dispositivo": dispositivo, "lote": datasets_por_lote, "pasos": pasos,
                      "pasos_por_s": round(pasos / segundos, 2), "datasets_por_s": round(pasos * datasets_por_lote / segundos)})
        print(json.dumps(filas[-1]), flush=True)
    return filas
