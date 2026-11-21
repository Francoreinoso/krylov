"""Genera la nube de `supervivencia`: el predictivo a priori del modelo generativo, resumido (WORKPLAN.md, 11.9).

    uv run python -m motor.supervivencia.nube                         # escribe motor/artefactos/supervivencia/nube.npz
    uv run python -m motor.supervivencia.nube --carpeta <carpeta>     # otra carpeta de artefactos (una exportación de prueba)

Simula empresas con el prior y con el n del archivo del caso, y de cada una guarda (a) los dos ejes con nombre
(AUC del mejor factor por sí solo y proporción de renuncias entre las personas con respuesta) y (b) el resumen
s(D) del codificador exportado, el mismo `codificador.onnx` que usa el servicio. `nucleo.supervivencia.nube`
ubica el archivo ahí.

Si en la carpeta no hay `codificador.onnx`, guarda solo los ejes con nombre: alcanza para el primer detector
(una columna que delata la respuesta) y el segundo queda apagado. Con codificador, `nube.npz` guarda su huella;
si después se exporta otra red, el servicio apaga el segundo detector hasta que la nube se genere de nuevo.

No importa `torch`: el simulador es NumPy y el codificador corre con onnxruntime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from motor.supervivencia import simular
from nucleo import nube as comun, supervivencia as nucleo_sv
from nucleo.casos import cargar_caso

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "supervivencia"
CASO = "rotacion"


def generar(carpeta: Path = ARTEFACTOS, simulaciones: int = 5000, semilla: int = 7, por_lote: int = 50) -> dict:
    """Escribe `carpeta/nube.npz` desde `simulaciones` empresas del predictivo a priori. Devuelve un resumen de lo guardado."""
    caso, config = cargar_caso(CASO), simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    n = len(reales["tiempo"]) if reales is not None else 1470              # el n del archivo del caso
    sesion, huella = None, ""
    if (carpeta / "codificador.onnx").exists():
        import onnxruntime
        opciones = onnxruntime.SessionOptions()
        opciones.log_severity_level = 3
        sesion = onnxruntime.InferenceSession(str(carpeta / "codificador.onnx"), opciones, providers=["CPUExecutionProvider"])
        huella = hashlib.sha256((carpeta / "codificador.onnx").read_bytes()).hexdigest()
    rng = np.random.default_rng(semilla)
    ejes, resumenes = [], []
    for inicio in range(0, simulaciones, por_lote):
        lote = simular.simular(rng, min(por_lote, simulaciones - inicio), n, config, reales)
        if sesion is not None:
            resumenes.append(sesion.run(None, {"filas": lote["filas"], "grupo": lote["grupo"]})[0])
        for i in range(len(lote["theta"])):
            factores = nucleo_sv.factores_nube({c: lote[c][i] for c in ("efectos", "sueldo", "encuestas")}, caso["columnas"])
            ejes.append(comun.ejes_con_nombre(factores, lote["evento"][i])[:2])
    ejes = np.array(ejes)
    if sesion is not None:
        nube = comun.resumir_simulaciones(ejes, np.concatenate(resumenes))
    else:                                                                  # solo los ejes: sin media, precisión ni límite
        nube = {**comun.resumir_simulaciones(ejes, rng.normal(size=(len(ejes), 2))), "media": np.zeros(0), "precision": np.zeros((0, 0)), "limite": np.nan}
    carpeta.mkdir(parents=True, exist_ok=True)
    np.savez(carpeta / "nube.npz", **nube, huella_codificador=np.array(huella))
    return {"ruta": str(carpeta / "nube.npz"), "n_simulaciones": int(nube["n_simulaciones"]), "personas_por_empresa": int(n),
            "con_resumenes_aprendidos": sesion is not None, "x_maximo": round(float(nube["x_maximo"]), 3),
            "y_minimo": round(float(nube["y_minimo"]), 3), "y_maximo": round(float(nube["y_maximo"]), 3),
            "limite_mahalanobis": round(float(nube["limite"]), 2) if sesion is not None else None}


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--carpeta", type=Path, default=ARTEFACTOS, help="donde está codificador.onnx (si hay) y donde queda nube.npz")
    analizador.add_argument("--simulaciones", type=int, default=5000)
    a = analizador.parse_args()
    print(json.dumps(generar(a.carpeta, a.simulaciones), indent=1))
