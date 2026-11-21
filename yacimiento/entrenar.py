"""Entrena la red de `yacimiento` con yacimientos simulados al vuelo (cada lote es nuevo; se cuentan).

    uv run python -m yacimiento.entrenar --minutos 75 --dispositivo mps

Guarda `yacimiento/checkpoints/ultimo.pt` cada 5 minutos y al terminar (Ctrl-C también guarda); sin `--nuevo`, retoma.
"""
from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import torch

from yacimiento import modelo as M
from yacimiento.red import RedYacimiento

CARPETA = Path("yacimiento/checkpoints")


def _simulador(cola, lote: int, semilla: int) -> None:
    """Un proceso aparte que simula lotes sin parar: así el procesador simula mientras la GPU entrena."""
    torch.set_num_threads(1)
    gen = torch.Generator().manual_seed(semilla)
    while True:
        cola.put({k: v.numpy() for k, v in M.simular(lote, gen, "cpu").items()})


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--minutos", type=float, default=75.0)
    p.add_argument("--dispositivo", default="mps")
    p.add_argument("--lote", type=int, default=24)
    p.add_argument("--tasa", type=float, default=4e-4)
    p.add_argument("--guardar-cada-min", type=float, default=5.0)
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--simuladores", type=int, default=4, help="procesos que simulan en paralelo")
    p.add_argument("--nuevo", action="store_true")
    a = p.parse_args()

    torch.manual_seed(a.semilla)
    red = RedYacimiento()
    estado = {"pasos": 0, "datasets_simulados": 0, "segundos": 0.0}
    punto = CARPETA / "ultimo.pt"
    if punto.exists() and not a.nuevo:
        guardado = torch.load(punto, map_location="cpu", weights_only=False)
        red.load_state_dict(guardado["modulo"])
        estado = {k: guardado[k] for k in estado}
    else:
        red.flujo.fijar_escala(M.prior(20000, torch.Generator().manual_seed(a.semilla)))
    red.to(a.dispositivo)
    opt = torch.optim.AdamW(red.parameters(), lr=a.tasa, weight_decay=1e-5)
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    cola = ctx.Queue(maxsize=8)
    base = a.semilla * 1000003 + estado["pasos"] * 101                                  # al retomar no se repiten simulaciones
    procesos = [ctx.Process(target=_simulador, args=(cola, a.lote, base + i), daemon=True) for i in range(a.simuladores)]
    for proceso in procesos:
        proceso.start()
    CARPETA.mkdir(parents=True, exist_ok=True)

    def guardar() -> None:
        torch.save({"modulo": red.state_dict(), **estado}, punto)

    inicio, ultimo, total = time.time(), time.time(), a.minutos * 60
    previos = estado["segundos"]
    try:
        while (transcurrido := time.time() - inicio) < total:
            for grupo in opt.param_groups:        # calentamiento de 200 pasos y coseno hasta el final del tiempo pedido
                grupo["lr"] = a.tasa * min(1.0, (estado["pasos"] + 1) / 200) * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * transcurrido / total)))
            sim = {k: torch.from_numpy(v).to(a.dispositivo) for k, v in cola.get().items()}
            perdida, partes = red.perdida(sim)
            if not torch.isfinite(perdida):
                print("pérdida no finita: lote descartado", flush=True)
                continue
            opt.zero_grad(set_to_none=True)
            perdida.backward()
            torch.nn.utils.clip_grad_norm_(red.parameters(), 5.0)
            opt.step()
            estado["pasos"] += 1
            estado["datasets_simulados"] += a.lote
            estado["segundos"] = previos + time.time() - inicio
            if estado["pasos"] % 50 == 0:
                print(f"paso {estado['pasos']}  {estado['datasets_simulados']} yacimientos  {transcurrido / 60:.1f} min  "
                      f"mapa {partes['mapa']:.3f}  flujo {partes['flujo']:.2f}  {estado['datasets_simulados'] / estado['segundos']:.1f}/s", flush=True)
            if time.time() - ultimo > a.guardar_cada_min * 60:
                guardar(); ultimo = time.time()
    except KeyboardInterrupt:
        print("interrumpido: guardando", flush=True)
    guardar()
    print(f"terminado: {estado['pasos']} pasos, {estado['datasets_simulados']} yacimientos simulados, {estado['segundos'] / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
