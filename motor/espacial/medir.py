"""Mide el rendimiento real del motor `espacial` en este computador (skill `medir-rendimiento`).

    uv run python -m motor.espacial.medir --que simulador
    uv run python -m motor.espacial.medir --que entrenar --dispositivo mps --lote 128 --pasos 200
    uv run python -m motor.espacial.medir --que entrenar --dispositivo mps --segundos 120     # sostenido
"""

from __future__ import annotations

import argparse
import json
import time

import torch

from motor.espacial.red import RedEspacial
from motor.espacial.simular import Prior, simular


def _sincronizar(dispositivo: str) -> None:
    if dispositivo == "mps":
        torch.mps.synchronize()      # sin esto el cronómetro para antes de que la GPU termine


def medir_simulador(dispositivo: str, lote: int, repeticiones: int = 20) -> dict:
    gen, prior = torch.Generator().manual_seed(0), Prior()
    simular(lote, prior, gen, dispositivo)
    _sincronizar(dispositivo)
    inicio = time.time()
    for _ in range(repeticiones):
        simular(lote, prior, gen, dispositivo)
    _sincronizar(dispositivo)
    return {"que": "simulador", "dispositivo": dispositivo, "lote": lote,
            "terrenos_por_s": round(lote * repeticiones / (time.time() - inicio))}


def medir_entrenamiento(dispositivo: str, lote: int, pasos: int | None, segundos: float | None) -> dict:
    torch.manual_seed(0)
    gen, prior = torch.Generator().manual_seed(0), Prior()
    red = RedEspacial().to(dispositivo)
    optimizador = torch.optim.AdamW(red.parameters(), lr=1e-4)

    def paso():
        partes = red.perdidas(simular(lote, prior, gen, dispositivo))
        optimizador.zero_grad(set_to_none=True)
        (partes["mapa"] + partes["flujo"]).backward()
        optimizador.step()

    for _ in range(20):                      # calentamiento
        paso()
    _sincronizar(dispositivo)
    marcas, inicio = [], time.time()
    while (pasos is not None and len(marcas) < pasos) or (segundos is not None and time.time() - inicio < segundos):
        paso()
        _sincronizar(dispositivo)
        marcas.append(time.time() - inicio)
    total = marcas[-1]
    salida = {"que": "entrenar", "dispositivo": dispositivo, "lote": lote, "pasos": len(marcas),
              "pasos_por_s": round(len(marcas) / total, 2), "terrenos_por_s": round(lote * len(marcas) / total)}
    if total >= 90:                          # caída por temperatura: últimos 30 s contra primeros 30 s
        primeros, ultimos = sum(m <= 30 for m in marcas) / 30, sum(m > total - 30 for m in marcas) / 30
        salida.update({"pasos_por_s_primeros_30s": round(primeros, 2), "pasos_por_s_ultimos_30s": round(ultimos, 2),
                       "caida": round(1 - ultimos / primeros, 3)})
    return salida


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--que", choices=("simulador", "entrenar"), required=True)
    p.add_argument("--dispositivo", default="cpu", choices=("cpu", "mps"))
    p.add_argument("--lote", type=int, default=64)
    p.add_argument("--pasos", type=int, default=None)
    p.add_argument("--segundos", type=float, default=None)
    a = p.parse_args()
    if a.que == "simulador":
        print(json.dumps(medir_simulador(a.dispositivo, a.lote)))
    else:
        if a.pasos is None and a.segundos is None:
            a.pasos = 200
        print(json.dumps(medir_entrenamiento(a.dispositivo, a.lote, a.pasos, a.segundos)))


if __name__ == "__main__":
    main()
