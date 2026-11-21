"""El yacimiento del demo: SIMULADO con el mismo modelo generativo (`yacimiento/modelo.py`), semilla fija, 60 sondajes.

Escribe `yacimiento/datos/demo.npz` (covariables, máscara, compósitos, y aparte la verdad escondida y el θ verdadero) y
`datos/demo/sondajes.csv`, una fila por compósito, como lo entregaría una campaña de sondajes. No es ningún yacimiento real.

    uv run python -m yacimiento.demo
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import torch

from yacimiento import modelo as M

SEMILLA = 2026
BLOQUE_M = (25.0, 25.0, 15.0)          # tamaño del bloque en metros: 800 × 800 × 240 m en total
RUTA = Path("yacimiento/datos/demo.npz")


def main() -> None:
    gen = torch.Generator().manual_seed(SEMILLA)
    M.DISENO["sondajes"] = (60, 60)                     # el demo usa el máximo del diseño: es el caso caro para el método lento
    sim = {k: v[0].numpy() for k, v in M.simular(1, gen).items() if k != "recorte"}
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(RUTA, cov=sim["cov"].astype(np.float32), mascara=sim["mascara"].astype(np.float32), y=sim["y"].astype(np.float32),
                        verdad=sim["verdad"].astype(np.float32), theta_verdadero=sim["theta"], semilla=SEMILLA)
    x, y, z = np.nonzero(sim["mascara"])
    with open("datos/demo/sondajes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["este_m", "norte_m", "profundidad_m", "cobre_pct"] + list(M.NOMBRES_COV))
        for i, j, k in zip(x, y, z):
            w.writerow([f"{(i + 0.5) * BLOQUE_M[0]:.1f}", f"{(j + 0.5) * BLOQUE_M[1]:.1f}", f"{(k + 0.5) * BLOQUE_M[2]:.1f}",
                        f"{np.exp(sim['y'][i, j, k]):.3f}"] + [f"{sim['cov'][c, i, j, k]:.3f}" for c in range(M.N_COV)])
    print(f"{len(x)} compósitos; ley mediana {np.exp(np.median(sim['verdad'])):.2f}% Cu; theta verdadero {np.round(sim['theta'], 2)}")


if __name__ == "__main__":
    main()
