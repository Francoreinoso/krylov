"""Exporta la red de `supervivencia` para el servicio: codificador a ONNX y flujo a `flujo.npz`.

El servicio no tiene torch: corre el codificador con onnxruntime y muestrea el flujo en NumPy
(`nucleo/flujo.py`). Aquí se exporta y se comprueba que las dos copias dan lo mismo que torch:
el codificador con n variable, y el flujo con los mismos pesos y el mismo ruido.

    uv run python -m motor.supervivencia.exportar --prueba     # red sin entrenar, carpeta temporal
    uv run python -m motor.supervivencia.exportar              # desde ultimo.pt a motor/artefactos/supervivencia/
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch

from motor.comun.codificador import comparar_con_onnxruntime, exportar_onnx
from motor.supervivencia import red as red_sv
from motor.supervivencia import simular
from motor.supervivencia.entrenar import CARPETA
from motor.supervivencia.validar import cargar_red
from nucleo import flujo as flujo_np

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "supervivencia"
TOLERANCIA = 1e-3


def exportar(red: red_sv.RedSupervivencia, carpeta: Path, semilla: int = 0) -> dict:
    """Escribe `codificador.onnx` y `flujo.npz` en `carpeta` y devuelve las diferencias máximas con torch."""
    red = red.cpu().eval()
    config = simular.cargar_config()
    rng = np.random.default_rng(semilla)
    ejemplo = red_sv.lote_a_tensores(simular.simular(rng, 2, 64, config))[:2]
    ruta_onnx, ruta_flujo = carpeta / "codificador.onnx", carpeta / "flujo.npz"
    ejes = {"filas": {0: "lote", 1: "n"}, "grupo": {0: "lote", 1: "n"}}
    exportar_onnx(red.codificador, ejemplo, str(ruta_onnx), ["filas", "grupo"], ejes)
    red.flujo.exportar_npz(str(ruta_flujo))

    diferencias = {}
    for lote, n in [(1, 200), (3, 1470), (2, 2000)]:                       # n variable
        entradas = red_sv.lote_a_tensores(simular.simular(rng, lote, n, config))[:2]
        diferencias[f"codificador_n{n}"] = comparar_con_onnxruntime(red.codificador, str(ruta_onnx), entradas)
    with torch.no_grad():
        resumen = red.codificador(*entradas)                                # (2, 128)
        ruido = flujo_np.ruido(semilla, 32, red.flujo.dim_theta)[:, None, :].repeat(2, axis=1)
        con_torch = red.flujo.muestrear_con_ruido(resumen, torch.as_tensor(ruido)).numpy()
    con_numpy = flujo_np.muestrear(flujo_np.cargar(str(ruta_flujo)), resumen.numpy(), ruido)
    diferencias["flujo_numpy_vs_torch"] = float(np.abs(con_numpy - con_torch).max())
    return diferencias


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--prueba", action="store_true", help="red sin entrenar, a una carpeta temporal")
    analizador.add_argument("--punto", default=str(CARPETA / "ultimo.pt"))
    a = analizador.parse_args()

    if a.prueba:
        with tempfile.TemporaryDirectory() as temporal:
            diferencias = exportar(red_sv.construir(), Path(temporal))
    else:
        red, _ = cargar_red(Path(a.punto))
        ARTEFACTOS.mkdir(parents=True, exist_ok=True)
        diferencias = exportar(red, ARTEFACTOS)
        shutil.copyfile(a.punto, ARTEFACTOS / "pesos.pt")
        print(f"→ {ARTEFACTOS}")
    for nombre, valor in diferencias.items():
        print(f"{nombre}: diferencia máxima {valor:.2e}")
    if max(diferencias.values()) > TOLERANCIA:
        raise SystemExit(f"La exportación difiere de torch en más de {TOLERANCIA}")
    print("exportación correcta: onnxruntime y NumPy dan lo mismo que torch")


if __name__ == "__main__":
    principal()
