"""Entrena la red de `supervivencia` con NPE sobre datasets simulados al vuelo.

Cada paso simula un lote nuevo de empresas con el modelo generativo (`simular.py`), con n al azar
entre 200 y 2.000 personas, y baja −log q(θ | s(D)). El bucle, los puntos de guardado y el conteo de
datasets simulados son los de `motor/comun/entrenar.py`.

Prueba de humo (3 minutos):
    uv run python -m motor.supervivencia.entrenar --minutos 3 --nuevo
Corrida larga (retoma sola si ya hay un punto de guardado):
    caffeinate -dims uv run python -m motor.supervivencia.entrenar --dispositivo cpu --hasta 08:30 --guardar-cada-min 10

Afinar desde una red ya exportada (por ejemplo la de la noche), en otra carpeta y con un prior candidato:
    KRYLOV_SUPERVIVENCIA_CONFIG=<config.json candidato> caffeinate -dims uv run python -m motor.supervivencia.entrenar \
        --carpeta motor/checkpoints/supervivencia_afinado --desde motor/artefactos/supervivencia/pesos.pt --hasta 14:45

Si se cae, el MISMO comando retoma desde `ultimo.pt` de su carpeta (`--desde` solo actúa si la carpeta está vacía).
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


def sembrar(desde: Path, carpeta: Path) -> None:
    """Deja en `carpeta/ultimo.pt` el punto de guardado `desde`, listo para que el bucle común lo retome.

    Si viene de la red anterior a los atajos nuevos del codificador, la primera capa de rho se amplía con columnas en
    cero (`red.cargar_estado`) y los momentos de AdamW de esa capa, igual: el resto del optimizador se conserva. El
    conteo de pasos, de simulaciones y de minutos sigue desde donde quedó: la cifra «practicó con N» los suma.
    """
    estado = torch.load(desde, map_location="cpu", weights_only=False)
    red = red_sv.RedSupervivencia(**red_sv.ARQUITECTURA)
    if red_sv.cargar_estado(red, estado["modulo"]):
        columnas = red.state_dict()[red_sv.CAPA_AMPLIADA].shape[1]
        indice = [nombre for nombre, _ in red.named_parameters()].index(red_sv.CAPA_AMPLIADA)
        momentos = estado.get("optimizador", {}).get("state", {}).get(indice, {})
        for clave in ("exp_avg", "exp_avg_sq"):
            if clave in momentos:
                momentos[clave] = red_sv.ampliar(momentos[clave], columnas)
        print(f"[sembrar] {desde} es de la red anterior: primera capa de rho ampliada a {columnas} entradas, con las nuevas en cero", flush=True)
    estado["modulo"] = red.state_dict()
    estado["motivo"] = f"sembrado desde {desde}"
    carpeta.mkdir(parents=True, exist_ok=True)
    bucle.guardar_punto(carpeta / "ultimo.pt", estado)


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
    analizador.add_argument("--promedio", type=float, default=red_sv.DECAIMIENTO_PROMEDIO, help="decaimiento del promedio móvil de los pesos")
    analizador.add_argument("--desde", type=Path, help="punto de guardado del que partir si la carpeta no tiene uno (por ejemplo, el pesos.pt exportado)")
    a = analizador.parse_args()

    if a.hilos:
        torch.set_num_threads(a.hilos)
    carpeta = Path(a.carpeta)
    if a.desde and not a.nuevo and not (carpeta / "ultimo.pt").exists():
        sembrar(a.desde, carpeta)
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    if reales is None:
        print("[aviso] no está el archivo del caso (datos/demo/): las covariables salen solo del generador paramétrico", flush=True)

    dispositivo = bucle.elegir_dispositivo(a.dispositivo)
    red = red_sv.construir(config, a.semilla).to(dispositivo)
    ya = 0 if a.nuevo else pasos_previos(carpeta)
    rng = np.random.default_rng([a.semilla, ya])       # al retomar no se repiten los datasets ya vistos

    def perdida_de_lote():
        red.actualizar_promedio(a.promedio)             # con los pesos que dejó el paso anterior
        n = simular.muestrear_n(rng, config)
        lote = simular.simular(rng, a.lote, n, config, reales)
        return red.perdida(*red_sv.lote_a_tensores(lote, dispositivo)), {"n": n}

    print(f"[supervivencia] dispositivo {dispositivo}, lote {a.lote}, carpeta {carpeta}, prior de {simular.ruta_config()}", flush=True)
    bucle.entrenar(
        red, perdida_de_lote, a.lote, carpeta,
        minutos=a.minutos, hasta=a.hasta, guardar_cada_min=a.guardar_cada_min, tasa=a.tasa,
        retomar=not a.nuevo,
        config={"motor_id": "supervivencia", "arquitectura": red_sv.ARQUITECTURA, "simulador": config,
                "lote": a.lote, "semilla": a.semilla, "covariables_reales": reales is not None, "promedio": a.promedio},
    )


if __name__ == "__main__":
    principal()
