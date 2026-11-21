"""Piso de la cabeza de mapa: kriging exacto con el θ verdadero, en los mismos terrenos simulados.

    uv run python -m motor.espacial.piso_kriging [punto de guardado]

Con θ conocido, el predictivo de y(s) es gaussiano y se calcula exacto (kriging simple).
Ninguna red puede tener, en promedio, menor pérdida de mapa que ese cálculo: es el piso.
Sirve para leer la pérdida de la cabeza de mapa: qué fracción cerró del camino entre lo
trivial (media 0, desviación 1) y el piso. El kriging trata cada bloque medido como una
sola medición, así que el piso es algo pesimista donde se promediaron dos o tres.
"""
import sys

import numpy as np
import torch

from motor.espacial.simular import simular, Prior, metrica_anisotropica
from motor.espacial.exportar import red_desde_config
from motor.comun.entrenar import cargar_punto
N = 60
L = simular(N, Prior(), torch.Generator().manual_seed(777))
RUTA = sys.argv[1] if len(sys.argv) > 1 else "motor/checkpoints/espacial/ultimo.pt"
est = torch.load(RUTA, map_location="cpu", weights_only=False)
red = red_desde_config(est["config"]); cargar_punto(RUTA, red); red.eval()
with torch.no_grad(): media, log_desv, _ = red(L["canales"])
th = L["theta_original"].double(); m11, m12, m22 = metrica_anisotropica(th)
c = torch.arange(32.0, dtype=torch.float64); fy, fx = torch.meshgrid(c, c, indexing="ij"); fy, fx = fy.reshape(-1), fx.reshape(-1)
dx, dy = fx[:, None] - fx[None, :], fy[:, None] - fy[None, :]
res = {"kriging": [], "red": [], "trivial": []}
for i in range(N):
    K = torch.exp(2 * th[i, 3]) * torch.exp(-torch.sqrt((m11[i] * dx**2 + 2 * m12[i] * dx * dy + m22[i] * dy**2).clamp_min(0)))
    marca = L["canales"][i, 1].reshape(-1).bool(); raiz = L["canales"][i, 2].reshape(-1).double()
    esc, med = L["escala"][i].double(), L["media"][i].double()
    tend = th[i, 5] + th[i, 6] * raiz
    z = L["canales"][i, 0].reshape(-1).double()[marca] * esc + med            # valores medidos, sin estandarizar
    Koo = K[marca][:, marca] + torch.exp(2 * th[i, 4]) * torch.eye(int(marca.sum()), dtype=torch.float64)
    A = torch.linalg.solve(Koo, K[marca]).T                      # (1024, n)
    mu = tend + A @ (z - tend[marca]); var = (torch.diagonal(K) - (A * K[:, marca]).sum(1)).clamp_min(1e-9)
    y = L["campo"][i].reshape(-1).double()                                      # estandarizado
    mu_e, sd_e = (mu - med) / esc, var.sqrt() / esc
    nll = lambda m, s: float((0.5 * ((y - m) / s) ** 2 + torch.log(s) + 0.9189385).mean())
    sin = ~marca
    res["kriging"].append((nll(mu_e, sd_e), float(((y - mu_e)[sin] ** 2).mean())))
    res["red"].append((nll(media[i].reshape(-1).double(), log_desv[i].reshape(-1).double().exp()), float(((y - media[i].reshape(-1))[sin] ** 2).mean())))
    res["trivial"].append((nll(torch.zeros_like(y), torch.ones_like(y)), float((y[sin] ** 2).mean())))
print("pasos", est["pasos"])
for k, v in res.items():
    v = np.array(v); print(f"{k:8s} pérdida de mapa (NLL medio por bloque) {v[:,0].mean():.3f} | RECM en bloques sin medir {np.sqrt(v[:,1].mean()):.3f}")
