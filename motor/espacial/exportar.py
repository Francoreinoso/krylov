"""Exporta la red de `espacial` a los artefactos que usa el servicio (CONTRATO.md, sección 7).

    codificador.onnx   RedMapa: canales → media, log_desv, resumen   (onnxruntime, lote variable)
    flujo.npz          pesos del flujo condicional                   (nucleo/flujo.py, NumPy)
    pesos.pt           la red completa, para seguir entrenando
    config.json        prior, arquitectura y versión del preprocesamiento

Uso:
    uv run python -m motor.espacial.exportar --prueba            # red sin entrenar, a una carpeta temporal
    uv run python -m motor.espacial.exportar                     # desde motor/checkpoints/espacial/ultimo.pt
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
from motor.espacial.red import RedEspacial
from motor.espacial.simular import DIM_THETA, NOMBRES_THETA, Prior, simular
from nucleo import flujo as flujo_numpy
from nucleo.preproceso import LADO, VERSION

ARTEFACTOS = Path("motor/artefactos/espacial")
PUNTO = Path("motor/checkpoints/espacial/ultimo.pt")


def exportar(red: RedEspacial, carpeta: Path, config: dict) -> dict:
    """Escribe los artefactos y devuelve las diferencias medidas entre torch y lo exportado."""
    carpeta.mkdir(parents=True, exist_ok=True)
    red = red.cpu().eval()
    gen = torch.Generator().manual_seed(0)
    canales = simular(2, Prior(), gen)["canales"][:, : red.canales_entrada]

    ruta_onnx = str(carpeta / "codificador.onnx")
    exportar_onnx(red.mapa, (canales,), ruta_onnx, ["canales"], {"canales": {0: "lote"}},
                  nombres_salida=("media", "log_desv", "resumen"))
    red.flujo.exportar_npz(str(carpeta / "flujo.npz"), nombres_theta=np.array(NOMBRES_THETA))
    torch.save({"modulo": red.state_dict(), "config": config}, carpeta / "pesos.pt")
    (carpeta / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    # Verificación: onnxruntime contra torch con lotes de 1 y de 480 (el de «¿Dónde mido?»),
    # y el flujo en NumPy contra torch con el resumen de esos mismos terrenos.
    medido = {}
    for lote in (1, 480):
        entrada = simular(lote, Prior(), gen)["canales"][:, : red.canales_entrada]
        medido[f"onnx_vs_torch_lote_{lote}"] = comparar_con_onnxruntime(red.mapa, ruta_onnx, (entrada,))
    with torch.no_grad():
        resumen = red(entrada)[2]
        ruido = torch.randn(32, lote, DIM_THETA, generator=gen)
        con_torch = red.flujo.muestrear_con_ruido(resumen, ruido).numpy()
    con_numpy = flujo_numpy.muestrear(flujo_numpy.cargar(str(carpeta / "flujo.npz")), resumen.numpy(), ruido.numpy())
    medido["flujo_numpy_vs_torch"] = float(np.abs(con_numpy - con_torch).max())
    return medido


def configuracion(canales_entrada: int, prior: Prior, extra: dict | None = None) -> dict:
    return {
        "motor_id": "espacial", "preproceso": VERSION, "lado": LADO, "canales_entrada": canales_entrada,
        "nombres_theta": list(NOMBRES_THETA), "prior": prior.a_dict(),
        "arquitectura": "codificador convolucional con saltos (48, 96, 192) + cabeza de mapa + NPE con flujo de "
                        "acoplamiento afín (8 capas) sobre un resumen de 128, con el gradiente cortado",
        **(extra or {}),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prueba", action="store_true", help="exporta la red sin entrenar a una carpeta temporal")
    p.add_argument("--canales", type=int, default=3, choices=(2, 3))
    p.add_argument("--punto", type=Path, default=PUNTO)
    p.add_argument("--salida", type=Path, default=ARTEFACTOS)
    a = p.parse_args()

    if a.prueba:
        torch.manual_seed(0)
        red, salida = RedEspacial(a.canales), Path(tempfile.mkdtemp(prefix="krylov_espacial_"))
        config = configuracion(a.canales, Prior(), {"entrenada": False})
    else:
        estado = torch.load(a.punto, map_location="cpu", weights_only=False)
        config = estado["config"]
        red, salida = RedEspacial(config["canales_entrada"]), a.salida
        cargar_punto(a.punto, red)
        config = {**config, "entrenada": True, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
                  "minutos_entrenamiento": round(estado["segundos"] / 60, 1)}
    medido = exportar(red, salida, config)
    print(json.dumps({"carpeta": str(salida), **medido}, indent=2))
    assert max(medido.values()) < 1e-3, "lo exportado no coincide con torch"


if __name__ == "__main__":
    main()
