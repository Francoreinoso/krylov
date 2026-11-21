"""Red del motor `espacial`: codificador convolucional con saltos, cabeza de mapa y cabeza de flujo.

Entra la grilla de 32 × 32 con tres canales (valor estandarizado, marca de medición,
√dist). El codificador convolucional hace aquí el papel del codificador de conjuntos:
resume el dataset entero. Sobre él hay dos cabezas:

- **Cabeza de mapa**: media y desviación de y(s) en cada bloque, entrenada con la
  verosimilitud gaussiana del campo verdadero. Es el predictivo posterior marginal,
  amortizado: p(y(s) | D) bloque por bloque.
- **Cabeza de flujo**: q(θ | D) con NPE, un flujo de acoplamiento afín condicionado en un
  resumen s(D) de 128 números.

**Gradiente cortado.** La cabeza de flujo recibe las características del codificador
con `detach()`: su pérdida entrena el resumidor y el flujo, pero no toca el codificador
ni la cabeza de mapa. Así la cabeza de mapa entrena exactamente igual que si estuviera
sola (`prueba_red.py` lo comprueba comparando gradientes).

A ONNX se exporta `RedMapa` (codificador + cabeza de mapa + resumidor): devuelve media,
log-desviación y resumen. El flujo va aparte, en `flujo.npz`, y se muestrea en NumPy.
"""

from __future__ import annotations

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from motor.comun.flujo import FlujoCondicional
from motor.espacial.simular import DIM_THETA

DIM_RESUMEN = 128
LOG_DESV_MIN, LOG_DESV_MAX = -5.0, 3.0


class BloqueResidual(nn.Module):
    """Dos convoluciones 3×3 con normalización por grupos y conexión residual."""

    def __init__(self, canales: int):
        super().__init__()
        self.norma1, self.conv1 = nn.GroupNorm(8, canales), nn.Conv2d(canales, canales, 3, padding=1)
        self.norma2, self.conv2 = nn.GroupNorm(8, canales), nn.Conv2d(canales, canales, 3, padding=1)

    def forward(self, x: Tensor) -> Tensor:
        h = self.conv1(F.silu(self.norma1(x)))
        return x + self.conv2(F.silu(self.norma2(h)))


class Codificador(nn.Module):
    """Codificador convolucional en tres escalas (32, 16, 8). Devuelve las características de cada una."""

    def __init__(self, canales_entrada: int = 3, anchos: tuple[int, int, int] = (48, 96, 192)):
        super().__init__()
        a1, a2, a3 = anchos
        self.entrada = nn.Conv2d(canales_entrada, a1, 3, padding=1)
        self.nivel1 = nn.Sequential(BloqueResidual(a1), BloqueResidual(a1))
        self.bajar1 = nn.Conv2d(a1, a2, 3, stride=2, padding=1)
        self.nivel2 = nn.Sequential(BloqueResidual(a2), BloqueResidual(a2))
        self.bajar2 = nn.Conv2d(a2, a3, 3, stride=2, padding=1)
        self.nivel3 = nn.Sequential(BloqueResidual(a3), BloqueResidual(a3))

    def forward(self, canales: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        c1 = self.nivel1(self.entrada(canales))      # (B, a1, 32, 32)
        c2 = self.nivel2(self.bajar1(c1))            # (B, a2, 16, 16)
        c3 = self.nivel3(self.bajar2(c2))            # (B, a3, 8, 8)
        return c1, c2, c3


class CabezaMapa(nn.Module):
    """Decodificador con saltos: de las tres escalas a media y log-desviación de y(s) por bloque."""

    def __init__(self, anchos: tuple[int, int, int] = (48, 96, 192)):
        super().__init__()
        a1, a2, a3 = anchos
        self.subir2 = nn.Conv2d(a3, a2, 3, padding=1)
        self.mezcla2 = nn.Sequential(nn.Conv2d(2 * a2, a2, 1), BloqueResidual(a2))
        self.subir1 = nn.Conv2d(a2, a1, 3, padding=1)
        self.mezcla1 = nn.Sequential(nn.Conv2d(2 * a1, a1, 1), BloqueResidual(a1))
        self.salida = nn.Sequential(nn.GroupNorm(8, a1), nn.SiLU(), nn.Conv2d(a1, 2, 1))

    def forward(self, c1: Tensor, c2: Tensor, c3: Tensor) -> tuple[Tensor, Tensor]:
        h = self.subir2(F.interpolate(c3, scale_factor=2.0, mode="nearest"))
        h = self.mezcla2(torch.cat([h, c2], dim=1))
        h = self.subir1(F.interpolate(h, scale_factor=2.0, mode="nearest"))
        h = self.salida(self.mezcla1(torch.cat([h, c1], dim=1)))
        return h[:, 0], h[:, 1].clamp(LOG_DESV_MIN, LOG_DESV_MAX)


class Resumidor(nn.Module):
    """De las características (ya con el gradiente cortado) al resumen s(D) que condiciona el flujo.

    Tiene sus propias convoluciones en cada escala, y agrega con promedio y desviación
    estándar sobre el espacio. Sus pesos los entrena solo la pérdida NPE.
    """

    def __init__(self, anchos: tuple[int, int, int] = (48, 96, 192), ancho: int = 96, dim_resumen: int = DIM_RESUMEN):
        super().__init__()
        self.ramas = nn.ModuleList([
            nn.Sequential(nn.Conv2d(a, ancho, 3, stride=2, padding=1), nn.SiLU(), nn.Conv2d(ancho, ancho, 3, padding=1), nn.SiLU())
            for a in anchos
        ])
        self.mlp = nn.Sequential(nn.Linear(2 * ancho * len(anchos), 256), nn.SiLU(), nn.Linear(256, dim_resumen))

    def forward(self, c1: Tensor, c2: Tensor, c3: Tensor) -> Tensor:
        partes = []
        for rama, c in zip(self.ramas, (c1, c2, c3)):
            h = rama(c)
            media = h.mean(dim=(2, 3))
            partes += [media, torch.sqrt(((h - media[:, :, None, None]) ** 2).mean(dim=(2, 3)) + 1e-4)]
        return self.mlp(torch.cat(partes, dim=1))


class RedMapa(nn.Module):
    """Lo que se exporta a ONNX: canales → (media, log_desv, resumen). Sin el flujo."""

    def __init__(self, canales_entrada: int = 3):
        super().__init__()
        self.codificador = Codificador(canales_entrada)
        self.cabeza_mapa = CabezaMapa()
        self.resumidor = Resumidor()

    def forward(self, canales: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        c1, c2, c3 = self.codificador(canales)
        media, log_desv = self.cabeza_mapa(c1, c2, c3)
        # Gradiente cortado: lo que sigue no puede cambiar el codificador ni la cabeza de mapa.
        resumen = self.resumidor(c1.detach(), c2.detach(), c3.detach())
        return media, log_desv, resumen


class RedEspacial(nn.Module):
    """La red completa del motor: `RedMapa` más el flujo condicional sobre θ.

    Con `canales_entrada=2` es la red del salvavidas: sin el canal de tendencia.
    """

    def __init__(self, canales_entrada: int = 3):
        super().__init__()
        self.canales_entrada = canales_entrada
        self.mapa = RedMapa(canales_entrada)
        self.flujo = FlujoCondicional(DIM_THETA, DIM_RESUMEN)

    def forward(self, canales: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        return self.mapa(canales[:, : self.canales_entrada])

    def perdidas(self, lote: dict[str, Tensor], con_flujo: bool = True) -> dict[str, Tensor]:
        """Las dos pérdidas de un lote simulado.

        mapa:  −log N(y(s) | media, desv²), promediada sobre todos los bloques (medidos o no).
        flujo: pérdida NPE, −log q(θ | s(D)), promediada sobre los terrenos del lote.
        """
        media, log_desv, resumen = self(lote["canales"])
        error = (lote["campo"] - media) * torch.exp(-log_desv)
        perdidas = {"mapa": (0.5 * error ** 2 + log_desv).mean() + 0.9189385}
        if con_flujo:
            perdidas["flujo"] = -self.flujo.log_prob(lote["theta"], resumen).mean()
        return perdidas
