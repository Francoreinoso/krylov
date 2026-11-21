"""Genera la nube de `estados`: el predictivo a priori del modelo generativo, resumido (WORKPLAN.md, 11.9).

    uv run python -m motor.estados.nube                    # después de exportar: escribe motor/artefactos/estados/nube.npz

Simula carteras con el prior y con el n del archivo del caso, y de cada una guarda (a) los dos ejes con
nombre (AUC del mejor factor por sí solo y proporción de impago) y (b) el resumen s(D) del codificador
exportado, el mismo `codificador.onnx` que usa el servicio. `nucleo.estados.nube` ubica el archivo ahí.
No importa `torch`: el simulador es NumPy y el codificador corre con onnxruntime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime

from motor.estados import simular
from nucleo import estados as nucleo_es, nube as comun
from nucleo.casos import cargar_caso

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "estados"
CASO = "credito"


def generar(carpeta: Path = ARTEFACTOS, simulaciones: int = 5000, semilla: int = 7, por_lote: int = 50) -> dict:
    """Escribe `carpeta/nube.npz` desde `simulaciones` carteras del predictivo a priori. Devuelve un resumen de lo guardado."""
    caso = cargar_caso(CASO)
    reales = simular.cargar_covariables_reales(CASO)
    n = len(reales) if reales is not None else 2000                       # el n del archivo del caso
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    sesion = onnxruntime.InferenceSession(str(carpeta / "codificador.onnx"), opciones, providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(semilla)
    ejes, resumenes = [], []
    for inicio in range(0, simulaciones, por_lote):
        lote = simular.simular(rng, min(por_lote, simulaciones - inicio), n, reales)
        resumenes.append(sesion.run(None, {"x": lote["filas"], "mascara": np.ones(lote["filas"].shape[:2], dtype=np.float32)})[0])
        for i in range(len(lote["theta"])):
            factores = nucleo_es.factores_nube({k: lote[k][i] for k in nucleo_es.VARIABLES}, caso["columnas"])
            ejes.append(comun.ejes_con_nombre(factores, lote["impago"][i])[:2])
    nube = comun.resumir_simulaciones(np.array(ejes), np.concatenate(resumenes))
    np.savez(carpeta / "nube.npz", **nube)
    return {"ruta": str(carpeta / "nube.npz"), "n_simulaciones": int(nube["n_simulaciones"]), "clientes_por_cartera": int(n),
            "x_maximo": round(float(nube["x_maximo"]), 3), "y_minimo": round(float(nube["y_minimo"]), 3),
            "y_maximo": round(float(nube["y_maximo"]), 3), "limite_mahalanobis": round(float(nube["limite"]), 2)}


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--carpeta", type=Path, default=ARTEFACTOS, help="donde está codificador.onnx y donde queda nube.npz")
    analizador.add_argument("--simulaciones", type=int, default=5000)
    a = analizador.parse_args()
    print(json.dumps(generar(a.carpeta, a.simulaciones), indent=1))
