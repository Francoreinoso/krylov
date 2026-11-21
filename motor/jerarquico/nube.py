"""Genera la nube de `jerarquico`: el predictivo a priori del modelo generativo, resumido (WORKPLAN.md, 11.9).

    uv run python -m motor.jerarquico.nube                 # después de exportar: escribe motor/artefactos/jerarquico/nube.npz

Simula datasets con el prior y con el tamaño del archivo del caso (citas y barrios), y de cada uno guarda
(a) los dos ejes con nombre (AUC del mejor factor por sí solo y proporción de citas a las que no se llegó)
y (b) el resumen s(D) del codificador exportado, el mismo `codificador.onnx` que usa el servicio.
`nucleo.jerarquico.nube` ubica el archivo ahí. No importa `torch`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import onnxruntime

from motor.jerarquico import simular
from nucleo import jerarquico as nucleo_jq, nube as comun
from nucleo.casos import cargar_caso

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "jerarquico"
CASO = "inasistencias"
CITAS_SIN_ARCHIVO, BARRIOS_SIN_ARCHIVO = 1980, 30          # el tamaño del archivo del caso (casos/inasistencias.yaml), si no está en este computador


def generar(carpeta: Path = ARTEFACTOS, simulaciones: int = 2000, semilla: int = 7, por_lote: int = 20) -> dict:
    """Escribe `carpeta/nube.npz` desde `simulaciones` datasets del predictivo a priori. Devuelve un resumen de lo guardado."""
    caso = cargar_caso(CASO)
    reales = simular.leer_real(CASO)                                      # None si el CSV no está (no se versiona)
    citas = len(reales["espera"]) if reales is not None else CITAS_SIN_ARCHIVO
    barrios = int(reales["barrio"].max()) + 1 if reales is not None else BARRIOS_SIN_ARCHIVO
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    sesion = onnxruntime.InferenceSession(str(carpeta / "codificador.onnx"), opciones, providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(semilla)
    ejes, resumenes = [], []
    for inicio in range(0, simulaciones, por_lote):
        lote = simular.simular(rng, min(por_lote, simulaciones - inicio), citas, barrios, reales)
        resumenes.append(sesion.run(None, {"filas": lote["filas"], "mascara": lote["mascara"]})[0])
        for i in range(len(lote["theta"])):
            existe = lote["mascara"][i] > 0
            factores = nucleo_jq.factores_nube({k: lote[k][i][existe] for k in ("espera", "dia", "sms", "edad", "binarias")}, caso["columnas"])
            ejes.append(comun.ejes_con_nombre(factores, lote["respuesta"][i][existe])[:2])
    nube = comun.resumir_simulaciones(np.array(ejes), np.concatenate(resumenes))
    np.savez(carpeta / "nube.npz", **nube)
    return {"ruta": str(carpeta / "nube.npz"), "n_simulaciones": int(nube["n_simulaciones"]), "citas": int(citas), "barrios": int(barrios),
            "con_el_archivo_real": reales is not None, "x_maximo": round(float(nube["x_maximo"]), 3), "y_minimo": round(float(nube["y_minimo"]), 3),
            "y_maximo": round(float(nube["y_maximo"]), 3), "limite_mahalanobis": round(float(nube["limite"]), 2)}


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--carpeta", type=Path, default=ARTEFACTOS, help="donde está codificador.onnx y donde queda nube.npz")
    analizador.add_argument("--simulaciones", type=int, default=2000)
    a = analizador.parse_args()
    print(json.dumps(generar(a.carpeta, a.simulaciones), indent=1))
