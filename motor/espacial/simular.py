"""Simulador del modelo generativo del motor `espacial` (WORKPLAN.md, 11.5).

    θ = (a, φ, r, σ², τ², β0, β1)
    y(s) = β0 + β1·√dist(s) + w(s),   w ~ proceso gaussiano de media 0 y covarianza σ²·exp(−h)
    z_j  = y(s_j) + ε_j,              ε_j ~ Normal(0, τ²),  en 30 a 400 lugares

h es la distancia anisotrópica: el alcance es a·√r en la dirección φ y a/√r en la
perpendicular (a es el alcance medio geométrico, en bloques). La dirección y la razón de
anisotropía se parametrizan juntas como e = log r · (cos 2φ, sin 2φ): un vector de dos
números sin restricciones, sin salto en φ = π y sin problema cuando r = 1 (φ deja de
estar identificada y e = 0).

Todo es vectorizado y al vuelo: un lote de terrenos por llamada, nada a disco.
- El campo w sale por transformada de Fourier sobre un toro de TORO × TORO, recortado a
  32 × 32 (inmersión circulante); `prueba_simular.py` lo compara con el método directo.
- El río es una curva suave al azar (un polinomio cúbico por cuatro puntos, rotado) y
  su campo de distancia, normalizado entre 0 y 1.
- En `prob_sin_tendencia` de los terrenos no hay tendencia: el canal va en cero, y no
  entra al campo. Ahí los datos no dicen nada de β1, así que su posterior es el prior.
- Las mediciones caen al azar, agrupadas, o en una franja junto al río.
- Los canales de entrada salen de `nucleo.preproceso.canales_terreno`: la misma función
  que usa el servicio con los datos reales.

Los parámetros que la red aprende van en las unidades estandarizadas de los datos
(lo que la red ve), en espacio sin restricciones:
    θ' = (log a, e1, e2, log(σ/esc), log(τ/esc), (β0 − media)/esc, β1/esc)
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import torch
from torch import Tensor

from nucleo.preproceso import LADO, canales_terreno

TORO = 128           # lado del toro de la inmersión circulante: cuatro veces la grilla (medido: con el
                     # doble, el error de covarianza llega a 0,11 en la esquina del prior; con cuatro, a 0,03)
NOMBRES_THETA = ("log_alcance", "anis_1", "anis_2", "log_sigma", "log_tau", "beta0", "beta1")
DIM_THETA = len(NOMBRES_THETA)


@dataclass(frozen=True)
class Prior:
    """Prior del modelo generativo. Las normales van truncadas a ±`corte` desviaciones."""

    log_alcance_media: float = math.log(4.5)   # alcance a, en bloques
    log_alcance_desv: float = 0.55
    anis_desv: float = 0.5                      # e1, e2 ~ Normal(0, anis_desv²); log r = |e|
    log_sigma_desv: float = 0.4                 # log σ ~ Normal(0, ·): la escala absoluta se estandariza
    log_tau_media: float = math.log(0.35)       # ruido de medición, relativo a σ ≈ 1
    log_tau_desv: float = 0.7
    beta0_desv: float = 1.0
    beta1_desv: float = 3.0
    prob_sin_tendencia: float = 0.2
    n_min: int = 30
    n_max: int = 400
    corte: float = 2.3

    def a_dict(self) -> dict:
        return asdict(self)


def _normal_truncada(forma, corte: float, gen: torch.Generator) -> Tensor:
    """Normal estándar truncada a ±corte, por inversión de la función de distribución."""
    p = 0.5 * (1 + math.erf(corte / math.sqrt(2)))
    u = torch.rand(forma, generator=gen) * (2 * p - 1) + (1 - p)
    return math.sqrt(2) * torch.erfinv(2 * u - 1)


def muestrear_prior(lote: int, prior: Prior, gen: torch.Generator) -> Tensor:
    """θ ~ prior, en espacio sin restricciones: (lote, 7) con el orden de NOMBRES_THETA."""
    z = _normal_truncada((lote, DIM_THETA), prior.corte, gen)
    medias = torch.tensor([prior.log_alcance_media, 0, 0, 0, prior.log_tau_media, 0, 0])
    desvs = torch.tensor([prior.log_alcance_desv, prior.anis_desv, prior.anis_desv, prior.log_sigma_desv,
                          prior.log_tau_desv, prior.beta0_desv, prior.beta1_desv])
    return medias + desvs * z


def metrica_anisotropica(theta: Tensor) -> tuple[Tensor, Tensor, Tensor]:
    """Coeficientes (m11, m12, m22) de h² = m11·dx² + 2·m12·dx·dy + m22·dy², con dx, dy en bloques.

    Es R(φ)·diag(1/(a²r), r/a²)·R(φ)ᵀ escrito con e = log r·(cos 2φ, sin 2φ):
    M = [cosh ρ·I − (sinh ρ/ρ)·(e1·σz + e2·σx)] / a²,  con ρ = |e| = log r.
    """
    a2 = torch.exp(2 * theta[:, 0])
    e1, e2 = theta[:, 1], theta[:, 2]
    rho = torch.sqrt(e1 ** 2 + e2 ** 2).clamp_min(1e-6)
    cosh, sinhc = torch.cosh(rho), torch.sinh(rho) / rho
    return (cosh - sinhc * e1) / a2, (-sinhc * e2) / a2, (cosh + sinhc * e1) / a2


def espectro_toro(theta: Tensor, toro: int = TORO) -> Tensor:
    """Autovalores de la covarianza exp(−h) puesta sobre el toro: (lote, toro, toro), ≥ 0."""
    m11, m12, m22 = (m[:, None, None] for m in metrica_anisotropica(theta))
    desfase = torch.fft.fftfreq(toro, d=1.0 / toro, device=theta.device)      # 0, 1, …, −2, −1
    dy, dx = desfase[None, :, None], desfase[None, None, :]
    h = torch.sqrt((m11 * dx ** 2 + 2 * m12 * dx * dy + m22 * dy ** 2).clamp_min(0))
    return torch.fft.fft2(torch.exp(-h)).real.clamp_min(0)


def campo_fourier(theta: Tensor, gen: torch.Generator, toro: int = TORO) -> Tensor:
    """w/σ: campo gaussiano de varianza 1 y covarianza exp(−h), (lote, LADO, LADO)."""
    espectro = espectro_toro(theta, toro)
    if theta.device.type == "cpu":
        ruido = torch.randn(2, *espectro.shape, generator=gen)
    else:   # en la GPU el ruido se genera ahí mismo (es lo más caro del simulador); la semilla es la global de torch
        ruido = torch.randn(2, *espectro.shape, device=theta.device)
    campo = torch.fft.fft2(torch.sqrt(espectro) * torch.complex(ruido[0], ruido[1])).real / toro
    return campo[:, :LADO, :LADO]


def rio(lote: int, gen: torch.Generator, puntos: int = 96) -> Tensor:
    """Distancia al río, normalizada entre 0 y 1 en cada terreno: (lote, LADO, LADO).

    El río es un polinomio cúbico por cuatro puntos de control al azar, rotado en un
    ángulo al azar. Los puntos de control pueden salir del terreno: así el río a veces
    cruza y a veces corre por un borde, como en el caso real.
    """
    t = torch.linspace(-0.4, 1.4, puntos)
    nodos = torch.tensor([0.0, 1 / 3, 2 / 3, 1.0])
    # Base de Lagrange: fila i = los cuatro polinomios evaluados en t_i.
    base = torch.stack([
        torch.stack([(t - nodos[j]) / (nodos[k] - nodos[j]) for j in range(4) if j != k]).prod(0) for k in range(4)
    ], dim=1)                                                           # (puntos, 4)
    alturas = torch.rand(lote, 4, generator=gen) * 1.6 - 0.3            # entre −0,3 y 1,3
    curva = torch.stack([t.expand(lote, -1), alturas @ base.T], dim=-1) - 0.5    # (lote, puntos, 2), centrada
    angulo = torch.rand(lote, generator=gen) * 2 * math.pi
    c, s = torch.cos(angulo)[:, None], torch.sin(angulo)[:, None]
    curva = torch.stack([c * curva[..., 0] - s * curva[..., 1], s * curva[..., 0] + c * curva[..., 1]], dim=-1) + 0.5
    centros = (torch.arange(LADO) + 0.5) / LADO
    celdas = torch.stack(torch.meshgrid(centros, centros, indexing="xy"), dim=-1).reshape(1, -1, 2)   # (1, LADO², 2)
    distancia = torch.cdist(celdas.expand(lote, -1, -1), curva).amin(dim=-1)                          # (lote, LADO²)
    distancia = distancia - distancia.amin(dim=1, keepdim=True)
    return (distancia / distancia.amax(dim=1, keepdim=True).clamp_min(1e-6)).reshape(lote, LADO, LADO)


def lugares_de_medicion(dist: Tensor, prior: Prior, gen: torch.Generator) -> Tensor:
    """Cuántas mediciones caen en cada bloque: (lote, LADO, LADO), con 30 a 400 bloques medidos.

    Tres diseños, uno por terreno al azar: uniforme, agrupado alrededor de tres centros, o
    restringido a una franja junto al río (el terreno real es una franja así).
    """
    lote = dist.shape[0]
    centros = (torch.arange(LADO) + 0.5)
    fila, columna = torch.meshgrid(centros, centros, indexing="ij")
    celdas = torch.stack([fila, columna], dim=-1).reshape(1, 1, -1, 2)                     # (1, 1, LADO², 2)
    focos = torch.rand(lote, 3, 1, 2, generator=gen) * LADO
    ancho = torch.rand(lote, 3, 1, generator=gen) * 5 + 3
    agrupado = torch.logsumexp(-((celdas - focos) ** 2).sum(-1) / (2 * ancho ** 2), dim=1).clamp_min(-6.0)
    franja = torch.where(dist.reshape(lote, -1) < torch.rand(lote, 1, generator=gen) * 0.65 + 0.25, 0.0, -20.0)
    diseno = torch.randint(0, 3, (lote, 1), generator=gen)
    log_peso = torch.where(diseno == 1, agrupado, torch.where(diseno == 2, franja, torch.zeros_like(agrupado)))

    # n bloques sin reemplazo con esos pesos: los n mayores de log_peso + Gumbel.
    gumbel = -torch.log(-torch.log(torch.rand(lote, LADO * LADO, generator=gen).clamp(1e-12, 1 - 1e-7)))
    u = torch.rand(lote, 1, generator=gen)
    n = torch.exp(math.log(prior.n_min) + u * (math.log(prior.n_max + 1) - math.log(prior.n_min))).floor()
    puesto = torch.argsort(torch.argsort(log_peso + gumbel, dim=1, descending=True), dim=1)
    medido = (puesto < n).float()
    # A veces caen dos o tres mediciones en el mismo bloque: el preprocesamiento las promedia.
    extra = torch.rand(lote, LADO * LADO, generator=gen)
    cuenta = medido * (1 + (extra < 0.15).float() + (extra < 0.03).float())
    return cuenta.reshape(lote, LADO, LADO)


def simular(lote: int, prior: Prior, gen: torch.Generator, dispositivo: torch.device | str = "cpu",
            con_tendencia: bool = True) -> dict[str, Tensor]:
    """Un lote de terrenos simulados con su respuesta: lo que la red ve y lo que tiene que aprender.

    Devuelve, en `dispositivo`:
      canales  (lote, 3, LADO, LADO)  valor estandarizado, marca de medición, √dist
      campo    (lote, LADO, LADO)     y(s) verdadero, estandarizado igual que los datos (blanco de la cabeza de mapa)
      theta    (lote, 7)              θ' en unidades estandarizadas (blanco de la cabeza de flujo)
      theta_original, media, escala, n, tiene_tendencia: para validar por grupos.
    Con `con_tendencia=False` ningún terreno tiene tendencia (la red de dos canales del salvavidas).
    """
    theta = muestrear_prior(lote, prior, gen)
    dist = rio(lote, gen)
    cuenta = lugares_de_medicion(dist, prior, gen)
    if con_tendencia:
        tiene = (torch.rand(lote, generator=gen) >= prior.prob_sin_tendencia).float()
    else:
        tiene = torch.zeros(lote)
    ruido_medicion = torch.randn(lote, LADO, LADO, generator=gen)

    theta, dist, cuenta, tiene, ruido_medicion = (t.to(dispositivo) for t in (theta, dist, cuenta, tiene, ruido_medicion))
    sigma, tau = torch.exp(theta[:, 3])[:, None, None], torch.exp(theta[:, 4])[:, None, None]
    beta0, beta1 = theta[:, 5, None, None], theta[:, 6, None, None]
    raiz_dist = torch.sqrt(dist) * tiene[:, None, None]

    campo = beta0 + beta1 * raiz_dist + sigma * campo_fourier(theta, gen)
    # El promedio de c mediciones en un bloque tiene ruido τ/√c; se acumula como suma y cuenta.
    suma = cuenta * campo + torch.sqrt(cuenta) * tau * ruido_medicion
    (valor, marca, raiz), media, escala = canales_terreno(suma, cuenta, raiz_dist)

    esc = escala[:, 0, 0]
    theta_est = torch.stack([
        theta[:, 0], theta[:, 1], theta[:, 2],
        theta[:, 3] - torch.log(esc), theta[:, 4] - torch.log(esc),
        (theta[:, 5] - media[:, 0, 0]) / esc, theta[:, 6] / esc,
    ], dim=1)
    return {
        "canales": torch.stack([valor, marca, raiz], dim=1),
        "campo": (campo - media) / escala,
        "theta": theta_est,
        "theta_original": theta, "media": media[:, 0, 0], "escala": esc,
        "n": marca.sum((-2, -1)), "tiene_tendencia": tiene,
    }
