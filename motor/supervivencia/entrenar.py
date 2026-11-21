"""Entrena la red de `supervivencia` con NPE sobre datasets simulados al vuelo.

Cada paso simula un lote nuevo de empresas con el modelo generativo (`simular.py`), con n al azar
entre 200 y 2.000 personas, y baja −log q(θ | s(D)). El bucle, los puntos de guardado y el conteo de
datasets simulados son los de `motor/comun/entrenar.py`.

Prueba de humo (3 minutos):
    uv run python -m motor.supervivencia.entrenar --minutos 3 --nuevo
Corrida larga (retoma sola si ya hay un punto de guardado):
    caffeinate -dims uv run python -m motor.supervivencia.entrenar --dispositivo cpu --hasta 08:30 --guardar-cada-min 10

Si se cae, el MISMO comando retoma desde `motor/checkpoints/supervivencia/ultimo.pt`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from motor.comun import entrenar as bucle
from motor.supervivencia import red as red_sv
from motor.supervivencia import simular

CARPETA = simular.RAIZ / "motor" / "checkpoints" / "supervivencia"


def pasos_previos(carpeta: Path) -> int:
    """Pasos ya dados según el punto de guardado (0 si no hay): fija la semilla del simulador al retomar."""
    ruta = carpeta / "ultimo.pt"
    return int(torch.load(ruta, map_location="cpu", weights_only=False)["pasos"]) if ruta.exists() else 0


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--minutos", type=float, help="presupuesto de reloj, en minutos")
    analizador.add_argument("--hasta", help="entrenar hasta esta hora, HH:MM")
    analizador.add_argument("--dispositivo", default="cpu", choices=["cpu", "mps", "auto"])
    analizador.add_argument("--guardar-cada-min", type=float, default=10.0)
    analizador.add_argument("--lote", type=int, default=32, help="datasets simulados por paso")
    analizador.add_argument("--tasa", type=float, default=5e-4)
    analizador.add_argument("--hilos", type=int, help="hilos de torch en el procesador (por defecto, los que elija torch)")
    analizador.add_argument("--semilla", type=int, default=0)
    analizador.add_argument("--carpeta", default=str(CARPETA), help="dónde quedan ultimo.pt y registro.jsonl")
    analizador.add_argument("--nuevo", action="store_true", help="parte de cero aunque exista un punto de guardado")
    a = analizador.parse_args()

    if a.hilos:
        torch.set_num_threads(a.hilos)
    carpeta = Path(a.carpeta)
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    if reales is None:
        print("[aviso] no está el archivo del caso (datos/demo/): las covariables salen solo del generador paramétrico", flush=True)

    dispositivo = bucle.elegir_dispositivo(a.dispositivo)
    red = red_sv.construir(config, a.semilla).to(dispositivo)
    ya = 0 if a.nuevo else pasos_previos(carpeta)
    rng = np.random.default_rng([a.semilla, ya])       # al retomar no se repiten los datasets ya vistos

    def perdida_de_lote():
        n = simular.muestrear_n(rng, config)
        lote = simular.simular(rng, a.lote, n, config, reales)
        return red.perdida(*red_sv.lote_a_tensores(lote, dispositivo)), {"n": n}

    print(f"[supervivencia] dispositivo {dispositivo}, lote {a.lote}, carpeta {carpeta}", flush=True)
    bucle.entrenar(
        red, perdida_de_lote, a.lote, carpeta,
        minutos=a.minutos, hasta=a.hasta, guardar_cada_min=a.guardar_cada_min, tasa=a.tasa,
        retomar=not a.nuevo,
        config={"motor_id": "supervivencia", "arquitectura": red_sv.ARQUITECTURA, "simulador": config,
                "lote": a.lote, "semilla": a.semilla, "covariables_reales": reales is not None},
    )


if __name__ == "__main__":
    principal()
