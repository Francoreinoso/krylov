"""Sexto motor, `yacimiento`: un yacimiento en 3D leído desde sondajes, con ocho covariables del modelo geológico.

Vive aparte de los cinco motores del producto (`nucleo/`, `motor/`): no los importa para escribir ni los modifica.
Solo reutiliza, leyendo, el flujo normalizador de `motor/comun/flujo.py`.

**Modelo generativo.** El dominio es un modelo de bloques de 32 × 32 × 16 (16.384 bloques). La ley, en log de % de cobre:

    Z(x) = β0 + Σ_k β_k·c_k(x) + W(x),      W ~ proceso gaussiano de media cero y covarianza σ²·exp(−h(x, x')),
    h² = (Δx, Δy)·M(a, e1, e2)·(Δx, Δy)ᵀ + (Δz / a_z)²        (anisotropía geométrica: horizontal con rumbo, y vertical),
    y_i = Z(x_i) + ε_i,  ε_i ~ Normal(0, τ)                    (compósitos de sondaje: error de muestreo y de laboratorio).

c_1..c_8 son covariables conocidas en todos los bloques (modelo geológico y geofísica): profundidad, cercanía a una
falla, dos indicadores de litología, alteración, dos campos geofísicos y densidad de vetillas.
θ = (log a, e1, e2, log a_z, log σ, log τ, β0, β_1..β_8): 15 parámetros, en espacio sin restricciones.

**Diseño del dataset** (se sortea en cada simulación): de 15 a 60 sondajes, con collar al azar en superficie,
inclinados hasta unos 27° de la vertical, de 8 a 16 compósitos cada uno (uno por banco). De 120 a 960 muestras.

**Simulación exacta y barata.** El campo W se sortea en toda la grilla por *circulant embedding* (FFT sobre un toro de
64 × 64 × 32): cuesta O(N log N) y no una factorización de Cholesky. Dentro de la ventana de 32 × 32 × 16 todos los
desfases son menores que medio toro, así que la covarianza es la exponencial del modelo, salvo por el recorte a cero de
los valores propios negativos del toro (se mide en `prueba_modelo.py`).
"""
from __future__ import annotations

import math

import torch
from torch import Tensor

NX, NY, NZ = 32, 32, 16
PX, PY, PZ = 64, 64, 32
N_COV = 8
NOMBRES_COV = ("profundidad", "cercania_falla", "litologia_B", "litologia_C", "alteracion", "geofisica_1", "geofisica_2", "vetillas")
NOMBRES_THETA = ("log_a", "e1", "e2", "log_az", "log_sigma", "log_tau", "beta0") + tuple(f"beta_{n}" for n in NOMBRES_COV)
DIM_THETA = len(NOMBRES_THETA)
REFERENCIA = math.log(0.5)              # log de 0,5% de cobre: el centro del prior de β0
PRIOR_MEDIA = torch.tensor([math.log(4.0), 0.0, 0.0, math.log(2.5), math.log(0.5), math.log(0.15), REFERENCIA] + [0.0] * N_COV)
PRIOR_DESV = torch.tensor([0.30, 0.30, 0.30, 0.30, 0.30, 0.40, 0.40] + [0.20] * N_COV)
DISENO = {"sondajes": (15, 60), "compositos": (8, 16), "inclinacion": 0.5}
MAX_SONDAJES = DISENO["sondajes"][1]


def prior(lote: int, gen: torch.Generator) -> Tensor:
    return PRIOR_MEDIA + PRIOR_DESV * torch.randn(lote, DIM_THETA, generator=gen)


def _desfases(n: int, dispositivo) -> Tensor:
    i = torch.arange(n, device=dispositivo, dtype=torch.float32)
    return torch.where(i < n / 2, i, i - n)


def metrica(theta: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    """(m11, m12, m22, 1/a_z²) de la distancia anisotrópica; la parte horizontal es la de `motor/espacial`."""
    a2 = torch.exp(2 * theta[..., 0])
    e1, e2 = theta[..., 1], theta[..., 2]
    rho = torch.sqrt(e1**2 + e2**2 + 1e-12)
    cosh, sinhc = torch.cosh(rho), torch.sinh(rho) / rho
    return (cosh - sinhc * e1) / a2, (-sinhc * e2) / a2, (cosh + sinhc * e1) / a2, torch.exp(-2 * theta[..., 3])


def _campo(m11, m12, m22, mz, ruido: Tensor) -> tuple[Tensor, Tensor]:
    """Campos gaussianos de varianza 1 en la ventana, por circulant embedding. Las métricas son (B,); ruido (B, PX, PY, PZ) complejo.
    Devuelve (campo (B, NX, NY, NZ), fracción de varianza recortada (B,))."""
    d = ruido.device
    dx, dy, dz = _desfases(PX, d)[:, None, None], _desfases(PY, d)[None, :, None], _desfases(PZ, d)[None, None, :]
    v = lambda t: t[:, None, None, None]            # noqa: E731
    h2 = v(m11) * dx**2 + 2 * v(m12) * dx * dy + v(m22) * dy**2 + v(mz) * dz**2
    valores = torch.fft.fftn(torch.exp(-torch.sqrt(h2.clamp_min(0.0))), dim=(1, 2, 3)).real
    recorte = (-valores.clamp_max(0.0)).sum((1, 2, 3)) / valores.clamp_min(0.0).sum((1, 2, 3))
    campo = torch.fft.fftn(torch.sqrt(valores.clamp_min(0.0) / (PX * PY * PZ)) * ruido, dim=(1, 2, 3)).real
    return campo[:, :NX, :NY, :NZ], recorte


def _ruido_complejo(forma, gen, dispositivo) -> Tensor:
    return torch.complex(torch.randn(forma, generator=gen), torch.randn(forma, generator=gen)).to(dispositivo)


def covariables(lote: int, gen: torch.Generator, dispositivo="cpu") -> Tensor:
    """Las ocho covariables en toda la grilla, (B, 8, NX, NY, NZ): campos suaves al azar, una falla y la profundidad.
    Las continuas quedan con media 0 y desviación 1 sobre la grilla (así llegan también las de un archivo)."""
    B = lote
    # Cinco campos suaves isotrópicos en horizontal, con alcance propio: litología, alteración, dos geofísicos, vetillas.
    alcance = torch.exp(torch.stack([torch.empty(B).uniform_(math.log(lo), math.log(hi), generator=gen)
                                     for lo, hi in ((6, 12), (4, 9), (8, 14), (8, 14), (2, 4))], dim=1)).reshape(-1).to(dispositivo)
    g, _ = _campo(1 / alcance**2, torch.zeros_like(alcance), 1 / alcance**2, 4 / alcance**2, _ruido_complejo((B * 5, PX, PY, PZ), gen, dispositivo))
    g = g.reshape(B, 5, NX, NY, NZ)
    g = (g - g.mean((2, 3, 4), keepdim=True)) / g.std((2, 3, 4), keepdim=True).clamp_min(1e-6)
    corte = torch.empty(B, 2).uniform_(0.3, 0.9, generator=gen).to(dispositivo)
    lito_b = (g[:, 0] > corte[:, 0, None, None, None]).float()
    lito_c = (g[:, 0] < -corte[:, 1, None, None, None]).float()
    z = torch.linspace(-1.0, 1.0, NZ, device=dispositivo).expand(B, NX, NY, NZ)
    # Falla: un plano casi vertical con rumbo al azar; la covariable es la cercanía, exp(−distancia / 4 bloques).
    rumbo = torch.empty(B).uniform_(0, math.pi, generator=gen).to(dispositivo)
    punto = torch.empty(B, 2).uniform_(8, 24, generator=gen).to(dispositivo)
    manteo = torch.empty(B).uniform_(-0.3, 0.3, generator=gen).to(dispositivo)
    x = torch.arange(NX, device=dispositivo, dtype=torch.float32)[None, :, None, None]
    y = torch.arange(NY, device=dispositivo, dtype=torch.float32)[None, None, :, None]
    k = torch.arange(NZ, device=dispositivo, dtype=torch.float32)[None, None, None, :]
    v = lambda t: t[:, None, None, None]            # noqa: E731
    dist = (torch.cos(v(rumbo)) * (x - v(punto[:, 0])) + torch.sin(v(rumbo)) * (y - v(punto[:, 1])) + v(manteo) * k).abs()
    falla = torch.exp(-dist / 4.0)
    falla = (falla - falla.mean((1, 2, 3), keepdim=True)) / falla.std((1, 2, 3), keepdim=True).clamp_min(1e-6)
    return torch.stack([z, falla, lito_b, lito_c, g[:, 1], g[:, 2], g[:, 3], g[:, 4]], dim=1)


def sondajes(lote: int, gen: torch.Generator, dispositivo="cpu") -> Tensor:
    """La máscara de bloques con compósito, (B, NX, NY, NZ): cada sondaje baja desde la superficie (z = 0), algo inclinado."""
    s_min, s_max = DISENO["sondajes"]
    cuantos = torch.exp(torch.empty(lote).uniform_(math.log(s_min), math.log(s_max + 1), generator=gen)).floor().clamp(max=s_max)
    activo = torch.arange(MAX_SONDAJES)[None, :] < cuantos[:, None]                                    # (B, S)
    collar = torch.empty(lote, MAX_SONDAJES, 2).uniform_(0, NX, generator=gen)
    paso = torch.empty(lote, MAX_SONDAJES, 2).uniform_(-DISENO["inclinacion"], DISENO["inclinacion"], generator=gen)
    largo = torch.randint(DISENO["compositos"][0], DISENO["compositos"][1] + 1, (lote, MAX_SONDAJES), generator=gen)
    k = torch.arange(NZ)[None, None, :]                                                              # (1, 1, K)
    x = torch.round(collar[..., 0, None] + paso[..., 0, None] * k).long()
    y = torch.round(collar[..., 1, None] + paso[..., 1, None] * k).long()
    vale = activo[..., None] & (k < largo[..., None]) & (x >= 0) & (x < NX) & (y >= 0) & (y < NY)
    mascara = torch.zeros(lote, NX, NY, NZ)
    b = torch.arange(lote)[:, None, None].expand_as(vale)
    mascara[b[vale], x[vale], y[vale], k.expand_as(vale)[vale]] = 1.0
    return mascara.to(dispositivo)


def simular(lote: int, gen: torch.Generator, dispositivo="cpu") -> dict[str, Tensor]:
    """Un lote de yacimientos: theta (B, 15), cov (B, 8, X, Y, Z), mascara, y (ceros donde no hay compósito) y la verdad Z."""
    theta = prior(lote, gen).to(dispositivo)
    cov = covariables(lote, gen, dispositivo)
    mascara = sondajes(lote, gen, dispositivo)
    w, recorte = _campo(*metrica(theta), _ruido_complejo((lote, PX, PY, PZ), gen, dispositivo))
    v = lambda t: t[:, None, None, None]            # noqa: E731
    verdad = v(theta[:, 6]) + (theta[:, 7:, None, None, None] * cov).sum(1) + v(torch.exp(theta[:, 4])) * w
    ruido = torch.randn(lote, NX, NY, NZ, generator=gen).to(dispositivo)
    y = (verdad + v(torch.exp(theta[:, 5])) * ruido) * mascara
    return {"theta": theta, "cov": cov, "mascara": mascara, "y": y, "verdad": verdad, "recorte": recorte}


def preparar(y: Tensor, mascara: Tensor, cov: Tensor) -> dict[str, Tensor]:
    """El único preprocesamiento: lo usan el simulador y quien responde un archivo.

    Ajusta por mínimos cuadrados (con una regularización chica) la ley contra las covariables en los compósitos y entrega
      x (B, 11, X, Y, Z) = [residuo en los compósitos, máscara, tendencia ajustada − referencia, las 8 covariables];
      resumen (B, 12)    = [los 9 coeficientes ajustados (el primero menos la referencia), log de la desviación del residuo,
                            log del número de compósitos − 6, fracción de bloques con compósito × 10];
      tendencia (B, X, Y, Z): la tendencia ajustada, que la cabeza de mapa corrige.
    """
    B = y.shape[0]
    unos = torch.ones_like(mascara)[:, None]
    X = torch.cat([unos, cov], dim=1).reshape(B, N_COV + 1, -1)                 # (B, 9, N)
    m = mascara.reshape(B, 1, -1)
    Xm = X * m
    A = Xm @ X.transpose(1, 2) + 1e-2 * torch.eye(N_COV + 1, device=y.device)
    b = Xm @ y.reshape(B, -1, 1)
    coef = torch.linalg.solve(A.cpu(), b.cpu()).to(y.device)                    # (B, 9, 1); en CPU: MPS no trae `solve`
    tendencia = (coef.transpose(1, 2) @ X).reshape(y.shape)
    residuo = (y - tendencia) * mascara
    n = mascara.sum((1, 2, 3))
    desv = torch.sqrt((residuo**2).sum((1, 2, 3)) / n.clamp_min(1.0)).clamp_min(1e-4)
    c = coef[..., 0].clone()
    c[:, 0] = c[:, 0] - REFERENCIA
    resumen = torch.cat([c, torch.log(desv)[:, None], (torch.log(n.clamp_min(1.0)) - 6.0)[:, None], (n / (NX * NY * NZ) * 10.0)[:, None]], dim=1)
    x = torch.cat([residuo[:, None], mascara[:, None], (tendencia - REFERENCIA)[:, None], cov], dim=1)
    return {"x": x, "resumen": resumen, "tendencia": tendencia}
