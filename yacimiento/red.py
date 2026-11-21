"""La red del motor `yacimiento`: una U-Net 3D con dos cabezas, como el motor `espacial` pero en volumen.

- **Cabeza de mapa:** para cada bloque, la media y la desviación del predictivo posterior marginal de la ley Z(x)
  (normal; se entrena con la log-verosimilitud de la ley verdadera del bloque simulado). La media es la tendencia
  ajustada por mínimos cuadrados más una corrección que aprende la red.
- **Cabeza de flujo:** q(θ | D), un flujo de acoplamiento condicional (`motor/comun/flujo.py`, NPE) sobre los 15 parámetros,
  condicionado en el resumen del volumen (promedio y máximo del nivel más profundo) y en el resumen del ajuste lineal.
"""
from __future__ import annotations

import torch
from torch import Tensor, nn

from motor.comun.flujo import FlujoCondicional
from yacimiento import modelo as M

CANALES = 3 + M.N_COV
DIM_RESUMEN = 12


def _bloque(entra: int, sale: int) -> nn.Sequential:
    return nn.Sequential(nn.Conv3d(entra, sale, 3, padding=1), nn.GroupNorm(8, sale), nn.SiLU(),
                         nn.Conv3d(sale, sale, 3, padding=1), nn.GroupNorm(8, sale), nn.SiLU())


class RedYacimiento(nn.Module):
    def __init__(self, ancho: int = 48):
        super().__init__()
        a = ancho
        # A resolución completa (16.384 bloques) solo una convolución de entrada y el bloque final: el trabajo va a media y a un cuarto.
        self.entrada = nn.Sequential(nn.Conv3d(CANALES, 16, 3, padding=1), nn.SiLU())
        self.baja1, self.baja2 = nn.Conv3d(16, a, 2, stride=2), nn.Conv3d(a, 2 * a, 2, stride=2)
        self.e2, self.e3 = _bloque(a, a), _bloque(2 * a, 2 * a)
        self.sube2, self.sube1 = nn.ConvTranspose3d(2 * a, a, 2, stride=2), nn.ConvTranspose3d(a, 16, 2, stride=2)
        self.d2 = _bloque(2 * a, a)
        self.d1 = nn.Sequential(nn.Conv3d(32, 24, 3, padding=1), nn.SiLU())
        self.mapa = nn.Conv3d(24, 2, 1)
        self.contexto = nn.Sequential(nn.Linear(4 * a + DIM_RESUMEN, 256), nn.SiLU(), nn.Linear(256, 128))
        self.flujo = FlujoCondicional(M.DIM_THETA, 128, capas=8, ocultas=(128, 128))

    def forward(self, x: Tensor, resumen: Tensor, tendencia: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        """x (B, 11, X, Y, Z) → media y log-desviación por bloque (B, X, Y, Z) y el contexto del flujo (B, 128)."""
        h1 = self.entrada(x)
        h2 = self.e2(self.baja1(h1))
        h3 = self.e3(self.baja2(h2))
        u2 = self.d2(torch.cat([self.sube2(h3), h2], dim=1))
        u1 = self.d1(torch.cat([self.sube1(u2), h1], dim=1))
        salida = self.mapa(u1)
        media = tendencia + salida[:, 0]
        log_desv = salida[:, 1].clamp(-6.0, 3.0) - 0.7
        ctx = self.contexto(torch.cat([h3.mean((2, 3, 4)), h3.amax((2, 3, 4)), resumen], dim=1))
        return media, log_desv, ctx

    def perdida(self, sim: dict[str, Tensor]) -> tuple[Tensor, dict[str, float]]:
        p = M.preparar(sim["y"], sim["mascara"], sim["cov"])
        media, log_desv, ctx = self(p["x"], p["resumen"], p["tendencia"])
        mapa = (log_desv + 0.5 * ((sim["verdad"] - media) * torch.exp(-log_desv)) ** 2).mean()
        flujo = -self.flujo.log_prob(sim["theta"], ctx).mean()
        return mapa + flujo / M.DIM_THETA, {"mapa": float(mapa.detach()), "flujo": float(flujo.detach())}

    @torch.no_grad()
    def responder(self, y: Tensor, mascara: Tensor, cov: Tensor, muestras: int = 0) -> dict[str, Tensor]:
        p = M.preparar(y, mascara, cov)
        media, log_desv, ctx = self(p["x"], p["resumen"], p["tendencia"])
        r = {"media": media, "desv": torch.exp(log_desv)}
        if muestras:
            r["theta"] = self.flujo.muestrear(ctx, muestras)
        return r
