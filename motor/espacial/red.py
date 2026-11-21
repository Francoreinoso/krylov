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

**Atajo de la cabeza de flujo (opcional, `atajo_flujo=True`).** Además de las características
convolucionales, el resumidor recibe estadísticos clásicos calculados directo de los canales:
la regresión de lo medido sobre √dist (de donde sale la tendencia) y el variograma empírico
de los residuos en doce desfases (de donde salen el alcance, la anisotropía y el ruido). Como
entra solo a la cabeza de flujo, la de mapa no cambia: se puede entrenar esta cabeza aparte
sobre el codificador congelado (`entrenar.py --solo-flujo`).

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
ANCHOS = (32, 64, 128)     # canales del codificador en las escalas 32, 16 y 8. Medido en la GPU del M4:
                           # ~520 terrenos/s al entrenar, contra ~300 con (48, 96, 192)
LOG_DESV_MIN, LOG_DESV_MAX = -5.0, 3.0


DESFASES = ((0, 1), (1, 0), (1, 1), (1, -1), (0, 2), (2, 0), (2, 2), (2, -2), (0, 4), (4, 0), (4, 4), (4, -4))   # (filas, columnas)
DIM_MOMENTOS = 6 + 2 * len(DESFASES)


def momentos_espaciales(canales: Tensor) -> Tensor:
    """Estadísticos clásicos de un terreno, (B, 30): tendencia por mínimos cuadrados y variograma de los residuos.

    Sobre los bloques medidos: cuántos son, promedio y dispersión de √dist, covarianza de lo medido con √dist y la
    pendiente que resulta, y la varianza de los residuos. Después, para cada desfase de DESFASES, la semivarianza
    de los residuos entre pares de bloques medidos a ese desfase y qué fracción de los bloques tiene par.
    """
    valor, marca = canales[:, 0], canales[:, 1]
    raiz = canales[:, 2] if canales.shape[1] > 2 else torch.zeros_like(valor)
    n = marca.sum(dim=(1, 2)).clamp(min=1.0)
    media_raiz = (marca * raiz).sum(dim=(1, 2)) / n
    centrada = (raiz - media_raiz[:, None, None]) * marca
    var_raiz = (centrada ** 2).sum(dim=(1, 2)) / n
    covarianza = (valor * centrada).sum(dim=(1, 2)) / n
    pendiente = covarianza / var_raiz.clamp(min=1e-3)
    residuo = valor - pendiente[:, None, None] * centrada                 # cero fuera de lo medido
    partes = [torch.log(n) / 6.0, media_raiz, torch.sqrt(var_raiz), covarianza, pendiente / 4.0, (residuo ** 2).sum(dim=(1, 2)) / n]
    alto, ancho = valor.shape[1], valor.shape[2]
    for df, dc in DESFASES:
        aqui = (slice(None), slice(0, alto - df), slice(max(0, -dc), ancho - max(0, dc)))
        alla = (slice(None), slice(df, alto), slice(max(0, dc), ancho - max(0, -dc)))
        pares = marca[aqui] * marca[alla]
        cuantos = pares.sum(dim=(1, 2))
        partes += [(pares * (residuo[aqui] - residuo[alla]) ** 2).sum(dim=(1, 2)) / (2.0 * cuantos.clamp(min=1.0)), cuantos / n]
    return torch.stack(partes, dim=1)


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

    def __init__(self, canales_entrada: int = 3, anchos: tuple[int, int, int] = ANCHOS):
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

    def __init__(self, anchos: tuple[int, int, int] = ANCHOS):
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

    def __init__(self, anchos: tuple[int, int, int] = ANCHOS, ancho: int = 96, dim_resumen: int = DIM_RESUMEN, atajo: bool = False):
        super().__init__()
        self.atajo = nn.Sequential(nn.Linear(DIM_MOMENTOS, 64), nn.SiLU()) if atajo else None
        self.ramas = nn.ModuleList([
            nn.Sequential(nn.Conv2d(a, ancho, 3, stride=2, padding=1), nn.SiLU(), nn.Conv2d(ancho, ancho, 3, padding=1), nn.SiLU())
            for a in anchos
        ])
        self.mlp = nn.Sequential(nn.Linear(2 * ancho * len(anchos) + (64 if atajo else 0), 256), nn.SiLU(), nn.Linear(256, dim_resumen))

    def forward(self, c1: Tensor, c2: Tensor, c3: Tensor, canales: Tensor | None = None) -> Tensor:
        partes = []
        for rama, c in zip(self.ramas, (c1, c2, c3)):
            h = rama(c)
            media = h.mean(dim=(2, 3))
            partes += [media, torch.sqrt(((h - media[:, :, None, None]) ** 2).mean(dim=(2, 3)) + 1e-4)]
        if self.atajo is not None:
            partes.append(self.atajo(momentos_espaciales(canales)))
        return self.mlp(torch.cat(partes, dim=1))


class RedMapa(nn.Module):
    """Lo que se exporta a ONNX: canales → (media, log_desv, resumen). Sin el flujo."""

    def __init__(self, canales_entrada: int = 3, anchos: tuple[int, int, int] = ANCHOS, atajo_flujo: bool = False):
        super().__init__()
        self.codificador = Codificador(canales_entrada, anchos)
        self.cabeza_mapa = CabezaMapa(anchos)
        self.resumidor = Resumidor(anchos, atajo=atajo_flujo)

    def forward(self, canales: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        c1, c2, c3 = self.codificador(canales)
        media, log_desv = self.cabeza_mapa(c1, c2, c3)
        # Gradiente cortado: lo que sigue no puede cambiar el codificador ni la cabeza de mapa.
        resumen = self.resumidor(c1.detach(), c2.detach(), c3.detach(), canales)
        return media, log_desv, resumen


class RedEspacial(nn.Module):
    """La red completa del motor: `RedMapa` más el flujo condicional sobre θ.

    Con `canales_entrada=2` es la red del salvavidas: sin el canal de tendencia.
    """

    def __init__(self, canales_entrada: int = 3, anchos: tuple[int, int, int] = ANCHOS, atajo_flujo: bool = False):
        super().__init__()
        self.canales_entrada, self.anchos, self.atajo_flujo = canales_entrada, tuple(anchos), atajo_flujo
        self.mapa = RedMapa(canales_entrada, self.anchos, atajo_flujo)
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

    def perdida_solo_flujo(self, lote: dict[str, Tensor]) -> Tensor:
        """Pérdida NPE con el codificador congelado: solo entrena el resumidor y el flujo (`entrenar.py --solo-flujo`)."""
        canales = lote["canales"][:, : self.canales_entrada]
        with torch.no_grad():
            c1, c2, c3 = self.mapa.codificador(canales)
        return -self.flujo.log_prob(lote["theta"], self.mapa.resumidor(c1, c2, c3, canales)).mean()

    def cargar_mapa_de(self, estado_del_modulo: dict[str, Tensor]) -> None:
        """Copia el codificador y la cabeza de mapa de otra red ya entrenada y los congela."""
        for nombre, parte in (("codificador", self.mapa.codificador), ("cabeza_mapa", self.mapa.cabeza_mapa)):
            prefijo = f"mapa.{nombre}."
            parte.load_state_dict({k[len(prefijo):]: v for k, v in estado_del_modulo.items() if k.startswith(prefijo)})
            for p in parte.parameters():
                p.requires_grad_(False)
