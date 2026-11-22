"""Exporta la cabeza de mapa de la red de `yacimiento` a ONNX, para que el servicio responda un archivo subido sin `torch`.

Escribe `yacimiento/artefactos/mapa.onnx` (entradas `x` y `tendencia`; salidas `media` y `desv` del log de la ley de cada
bloque). La cabeza de flujo no se exporta: no pasa su validación (`sello.json`) y no se muestra.

Después comprueba, en el yacimiento del demo, que el camino del servicio (`servicio/yacimiento.py`: el preprocesamiento
en NumPy más onnxruntime) da lo mismo que `RedYacimiento.responder` en `torch`. Si difieren, falla y no deja el archivo.

    uv run --group entrenar python -m yacimiento.exportar_onnx
"""
from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from yacimiento import modelo as M
from yacimiento.red import DIM_RESUMEN, RedYacimiento

ARTEFACTOS = "yacimiento/artefactos"
TOLERANCIA = 2e-3           # en log de % de cobre; la página lo guarda en un byte (pasos de 0,018)


class CabezaDeMapa(nn.Module):
    def __init__(self, red: RedYacimiento):
        super().__init__()
        self.red = red

    def forward(self, x: Tensor, tendencia: Tensor) -> tuple[Tensor, Tensor]:
        media, log_desv, _ = self.red(x, torch.zeros(x.shape[0], DIM_RESUMEN), tendencia)   # el resumen solo alimenta al flujo
        return media, torch.exp(log_desv)


def main() -> None:
    estado = torch.load(f"{ARTEFACTOS}/pesos.pt", map_location="cpu", weights_only=False)
    red = RedYacimiento()
    red.load_state_dict(estado["modulo"])
    red.eval()
    z = np.load("yacimiento/datos/demo.npz")
    t = {k: torch.from_numpy(z[k])[None] for k in ("y", "mascara", "cov")}
    p = M.preparar(t["y"], t["mascara"], t["cov"])
    ruta = f"{ARTEFACTOS}/mapa.onnx"
    torch.onnx.export(CabezaDeMapa(red), (p["x"], p["tendencia"]), ruta, input_names=["x", "tendencia"],
                      output_names=["media", "desv"], opset_version=17, dynamo=False)

    from servicio import yacimiento as servicio            # el camino sin torch, el mismo que corre en el servidor
    servicio._sesion.cache_clear()
    media, desv = servicio.responder(z["y"].astype(np.float64), z["mascara"].astype(np.float64), z["cov"].astype(np.float64))
    r = red.responder(t["y"], t["mascara"], t["cov"])
    d_media = float(np.abs(media - r["media"][0].numpy()).max())
    d_desv = float(np.abs(desv - r["desv"][0].numpy()).max())
    print(f"{ruta}: diferencia máxima con torch, media {d_media:.2e} y desviación {d_desv:.2e} (tolerancia {TOLERANCIA})")
    if max(d_media, d_desv) > TOLERANCIA:
        import os
        os.remove(ruta)
        raise SystemExit("El camino de NumPy y ONNX no da lo mismo que torch: no se deja el archivo.")


if __name__ == "__main__":
    main()
