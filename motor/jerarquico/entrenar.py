"""Entrena la red de `jerarquico` con NPE sobre datasets simulados al vuelo.

Cada paso simula un lote nuevo de datasets con el modelo generativo (`simular.py`), con 1.000 a
3.000 citas en 10 a 40 barrios, y baja −log q(θ | s(D)). El bucle, los puntos de guardado y el
conteo de datasets simulados son los de `motor/comun/entrenar.py`.

Prueba de humo:
    uv run python -m motor.jerarquico.entrenar --minutos 3 --nuevo
Corrida larga (retoma sola si ya hay un punto de guardado; el MISMO comando sirve para retomar):
    caffeinate -dims uv run python -m motor.jerarquico.entrenar --dispositivo cpu --hasta 11:30 --guardar-cada-min 10

El archivo real de inasistencias no se versiona. Si no está en `datos/demo/`, las covariables salen
solo del generador paramétrico y el programa lo avisa; se genera con `datos/preparar/inasistencias.py`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from motor.comun import entrenar as bucle
from motor.jerarquico import simular
from motor.jerarquico.exportar import configuracion
from motor.jerarquico.red import RedJerarquico, lote_a_tensores

CARPETA = simular.RAIZ / "motor" / "checkpoints" / "jerarquico"


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--minutos", type=float, help="presupuesto de reloj, en minutos")
    analizador.add_argument("--hasta", help="entrenar hasta esta hora, HH:MM")
    analizador.add_argument("--dispositivo", default="cpu", choices=["cpu", "mps", "auto"])
    analizador.add_argument("--guardar-cada-min", type=float, default=10.0)
    analizador.add_argument("--lote", type=int, default=16, help="datasets simulados por paso")
    analizador.add_argument("--tasa", type=float, default=5e-4)
    analizador.add_argument("--hilos", type=int, help="hilos de torch en el procesador")
    analizador.add_argument("--semilla", type=int, default=0)
    analizador.add_argument("--carpeta", default=str(CARPETA))
    analizador.add_argument("--nuevo", action="store_true", help="parte de cero aunque exista un punto de guardado")
    a = analizador.parse_args()

    if a.hilos:
        torch.set_num_threads(a.hilos)
    carpeta = Path(a.carpeta)
    ruta = carpeta / "ultimo.pt"
    ya = int(torch.load(ruta, map_location="cpu", weights_only=False)["pasos"]) if ruta.exists() and not a.nuevo else 0
    torch.manual_seed(a.semilla)
    rng = np.random.default_rng([a.semilla, ya])               # al retomar no se repiten los datasets ya vistos
    reales = simular.leer_real()
    if reales is None:
        print("[aviso] no está datos/demo/inasistencias.csv: las covariables salen solo del generador paramétrico", flush=True)
    dispositivo = bucle.elegir_dispositivo(a.dispositivo)
    red = RedJerarquico().to(dispositivo)

    def perdida_de_lote():
        citas, barrios = simular.muestrear_tamano(rng)
        lote = simular.simular(rng, a.lote, citas, barrios, reales)
        return red.perdida(*lote_a_tensores(lote, dispositivo)), {"citas": citas, "barrios": barrios}

    print(f"[jerarquico] dispositivo {dispositivo}, lote {a.lote}, carpeta {carpeta}", flush=True)
    bucle.entrenar(red, perdida_de_lote, a.lote, carpeta, minutos=a.minutos, hasta=a.hasta, guardar_cada_min=a.guardar_cada_min,
                   tasa=a.tasa, retomar=not a.nuevo,
                   config=configuracion({"lote": a.lote, "semilla": a.semilla, "covariables_reales": reales is not None}))


if __name__ == "__main__":
    principal()
