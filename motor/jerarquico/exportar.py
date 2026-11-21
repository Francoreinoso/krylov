"""Exporta la red de `jerarquico` a los artefactos del servicio (CONTRATO.md, sección 7).

    codificador.onnx   filas (lote, barrios, pacientes, citas, 19) y máscara → resumen   (onnxruntime, ejes variables)
    flujo.npz          pesos del flujo condicional                                        (nucleo/flujo.py, NumPy)
    pesos.pt, config.json

    uv run python -m motor.jerarquico.exportar --prueba       # red sin entrenar, a una carpeta temporal
    uv run python -m motor.jerarquico.exportar                # desde motor/checkpoints/jerarquico/ultimo.pt
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
import torch

from motor.comun.codificador import comparar_con_onnxruntime, exportar_onnx
from motor.comun.entrenar import cargar_punto
from motor.jerarquico import simular
from motor.jerarquico.red import ARQUITECTURA, RedJerarquico
from nucleo import flujo as flujo_numpy
from nucleo.jerarquico import DIM_THETA, NOMBRES_THETA

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "jerarquico"
PUNTO = simular.RAIZ / "motor" / "checkpoints" / "jerarquico" / "ultimo.pt"


def exportar(red: RedJerarquico, carpeta: Path, config: dict) -> dict:
    """Escribe los artefactos y devuelve las diferencias medidas entre torch y lo exportado."""
    carpeta.mkdir(parents=True, exist_ok=True)
    red = red.cpu().eval()
    rng = np.random.default_rng(0)
    ejemplo = simular.simular(rng, 2, 300, 5)
    ruta = str(carpeta / "codificador.onnx")
    ejes = {0: "lote", 1: "barrios", 2: "pacientes", 3: "citas"}
    exportar_onnx(red.codificador, (torch.from_numpy(ejemplo["filas"]), torch.from_numpy(ejemplo["mascara"])), ruta,
                  ["filas", "mascara"], {"filas": ejes, "mascara": ejes})
    red.flujo.exportar_npz(str(carpeta / "flujo.npz"), nombres_theta=np.array(NOMBRES_THETA))
    torch.save({"modulo": red.state_dict(), "config": config}, carpeta / "pesos.pt")
    (carpeta / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    medido = {}
    for lote, citas, barrios in ((1, 1000, 12), (3, 3000, 40)):          # tamaños distintos del ejemplo: los ejes son dinámicos de verdad
        sim = simular.simular(rng, lote, citas, barrios)
        filas, mascara = torch.from_numpy(sim["filas"]), torch.from_numpy(sim["mascara"])
        medido[f"onnx_vs_torch_lote_{lote}_barrios_{barrios}"] = comparar_con_onnxruntime(red.codificador, ruta, (filas, mascara))
    with torch.no_grad():
        resumen = red.codificador(filas, mascara)
        ruido = torch.randn(32, lote, DIM_THETA, generator=torch.Generator().manual_seed(0))
        con_torch = red.flujo.muestrear_con_ruido(resumen, ruido).numpy()
    con_numpy = flujo_numpy.muestrear(flujo_numpy.cargar(str(carpeta / "flujo.npz")), resumen.numpy(), ruido.numpy())
    medido["flujo_numpy_vs_torch"] = float(np.abs(con_numpy - con_torch).max())
    return medido


def configuracion(extra: dict | None = None) -> dict:
    return {**simular.config(), "arquitectura": ARQUITECTURA, **(extra or {})}


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--prueba", action="store_true", help="red sin entrenar, a una carpeta temporal")
    analizador.add_argument("--punto", default=str(PUNTO))
    analizador.add_argument("--salida", default=str(ARTEFACTOS))
    a = analizador.parse_args()
    red = RedJerarquico()
    if a.prueba:
        salida, config = Path(tempfile.mkdtemp(prefix="krylov_jerarquico_")), configuracion({"entrenada": False})
    else:
        estado = cargar_punto(Path(a.punto), red)
        salida = Path(a.salida)
        config = configuracion({"entrenada": True, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
                                "minutos_entrenamiento": round(estado["segundos"] / 60, 1)})
    medido = exportar(red, salida, config)
    print(json.dumps({"carpeta": str(salida), **medido}, indent=2))
    assert max(medido.values()) < 1e-3, "lo exportado no coincide con torch"


if __name__ == "__main__":
    principal()
