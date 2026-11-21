"""Pruebas del simulador de terrenos y del preprocesamiento compartido."""

import math

import numpy as np
import torch

from motor.espacial.simular import (DIM_THETA, TORO, Prior, campo_fourier, espectro_toro, lugares_de_medicion,
                                    muestrear_prior, rio, simular)
from nucleo.preproceso import LADO, acumular_por_bloque, canales_terreno, preparar_terreno


def _covarianza_directa(log_a: float, phi: float, r: float, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    """exp(−h) con la definición del modelo, escrita aparte: rotar a los ejes del campo y escalar."""
    a = math.exp(log_a)
    u = dx * math.cos(phi) + dy * math.sin(phi)          # a lo largo de φ: alcance a·√r
    v = -dx * math.sin(phi) + dy * math.cos(phi)         # perpendicular: alcance a/√r
    return np.exp(-np.sqrt((u / (a * math.sqrt(r))) ** 2 + (v * math.sqrt(r) / a) ** 2))


def _theta(log_a: float, phi: float, r: float) -> torch.Tensor:
    rho = math.log(r)
    return torch.tensor([[log_a, rho * math.cos(2 * phi), rho * math.sin(2 * phi), 0.0, 0.0, 0.0, 0.0]])


def test_preproceso_identico_en_numpy_y_torch():
    """El mismo arreglo por los dos caminos (el del servicio y el del simulador) da idéntico."""
    rng = np.random.default_rng(0)
    cuenta = (rng.random((4, LADO, LADO)) < 0.15).astype(np.float32) * rng.integers(1, 4, (4, LADO, LADO))
    suma = (cuenta * rng.normal(5.0, 2.0, (4, LADO, LADO))).astype(np.float32)
    raiz = rng.random((4, LADO, LADO)).astype(np.float32)
    canales_np, media_np, escala_np = canales_terreno(suma, cuenta.astype(np.float32), raiz)
    canales_t, media_t, escala_t = canales_terreno(torch.from_numpy(suma), torch.from_numpy(cuenta.astype(np.float32)),
                                                   torch.from_numpy(raiz))
    for a, b in zip(canales_np, canales_t):
        assert a.dtype == np.float32
        np.testing.assert_allclose(a, b.numpy(), rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(media_np, media_t.numpy(), rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(escala_np, escala_t.numpy(), rtol=1e-5, atol=1e-6)
    # Estandarizado con lo medido: media 0 y desviación 1 sobre los bloques con medición.
    medido = canales_np[1] > 0
    assert abs(canales_np[0][0][medido[0]].mean()) < 1e-4 and abs(canales_np[0][0][medido[0]].std() - 1) < 1e-3


def test_puntos_reales_llegan_a_los_mismos_canales():
    """De puntos con coordenadas (servicio) y de suma y cuenta por bloque (simulador) sale lo mismo."""
    rng = np.random.default_rng(1)
    x, y, valor = rng.uniform(0, 3200, 200), rng.uniform(0, 3200, 200), rng.lognormal(6, 0.5, 200)
    x[:2], y[:2] = [0.0, 3200.0], [0.0, 3200.0]           # fija la geometría: bloques de 100
    listo = preparar_terreno(x, y, valor, transformacion="log")
    fila, columna = (y // 100).clip(0, 31).astype(int), (x // 100).clip(0, 31).astype(int)
    suma, cuenta = acumular_por_bloque(fila, columna, np.log(valor))
    (v, m, r), _, _ = canales_terreno(torch.from_numpy(suma), torch.from_numpy(cuenta), torch.zeros(LADO, LADO))
    np.testing.assert_allclose(listo["canales"], torch.stack([v, m, r]).numpy(), rtol=1e-5, atol=1e-5)
    assert listo["canales"][1].sum() == len(set(zip(fila, columna)))


def test_covarianza_del_campo_coincide_con_la_directa():
    """La covarianza que implica el espectro (ya recortado en cero) contra exp(−h) calculada directo."""
    d = np.arange(-(LADO - 1), LADO)
    dy, dx = np.meshgrid(d, d, indexing="ij")
    for log_a, phi, r, tolerancia in [(math.log(4.5), 0.6, 1.8, 0.01), (math.log(2.0), 2.0, 1.0, 0.01),
                                      (math.log(15.9), 1.2, 3.0, 0.05)]:
        espectro = espectro_toro(_theta(log_a, phi, r))[0]
        implicita = torch.fft.ifft2(espectro).real.numpy()          # covarianza en el toro, por desfase
        directa = _covarianza_directa(log_a, phi, r, dx, dy)
        error = np.abs(implicita[dy % TORO, dx % TORO] - directa).max()
        assert error < tolerancia, (log_a, phi, r, error)


def test_campo_simulado_tiene_la_covarianza_directa():
    """Monte Carlo en una grilla chica: covarianza empírica de 8.000 campos contra la matriz exacta."""
    log_a, phi, r = math.log(4.0), 0.5, 2.0
    gen = torch.Generator().manual_seed(0)
    campos = campo_fourier(_theta(log_a, phi, r).expand(8000, -1), gen)[:, :6, :6].reshape(8000, 36).numpy()
    empirica = campos.T @ campos / len(campos)
    fila, columna = np.divmod(np.arange(36), 6)
    directa = _covarianza_directa(log_a, phi, r, columna[:, None] - columna[None, :], fila[:, None] - fila[None, :])
    assert np.abs(empirica - directa).max() < 0.06
    # Y un campo generado directo (Cholesky de la matriz exacta) tiene la misma covarianza.
    cholesky = np.linalg.cholesky(directa + 1e-9 * np.eye(36))
    directos = np.random.default_rng(0).standard_normal((8000, 36)) @ cholesky.T
    assert np.abs(directos.T @ directos / 8000 - empirica).max() < 0.09


def test_rio_y_lugares_de_medicion():
    gen = torch.Generator().manual_seed(0)
    prior = Prior()
    dist = rio(64, gen)
    assert dist.shape == (64, LADO, LADO) and float(dist.min()) == 0.0 and abs(float(dist.amax((1, 2)).min()) - 1) < 1e-5
    cuenta = lugares_de_medicion(dist, prior, gen)
    n = (cuenta > 0).sum((1, 2))
    assert int(n.min()) >= prior.n_min and int(n.max()) <= prior.n_max and int(cuenta.max()) <= 3


def test_simular_formas_y_coherencia():
    gen = torch.Generator().manual_seed(0)
    prior = Prior()
    lote = simular(128, prior, gen)
    assert lote["canales"].shape == (128, 3, LADO, LADO) and lote["theta"].shape == (128, DIM_THETA)
    assert all(torch.isfinite(v).all() for v in lote.values())
    # Sin tendencia, el canal va en cero; con tendencia, entre 0 y 1.
    sin = lote["tiene_tendencia"] == 0
    assert 0 < int(sin.sum()) < 128 and float(lote["canales"][sin, 2].abs().max()) == 0.0
    assert float(lote["canales"][~sin, 2].amax((1, 2)).min()) > 0.9
    # Los valores medidos están estandarizados, y el campo verdadero en las mismas unidades.
    marca = lote["canales"][:, 1]
    assert float(((lote["canales"][:, 0] * marca).sum((1, 2)) / marca.sum((1, 2))).abs().max()) < 1e-3
    assert float((lote["campo"] * marca).sum() / marca.sum()) < 0.1
    # Misma semilla, mismo lote.
    otra = simular(128, prior, torch.Generator().manual_seed(0))
    assert torch.equal(lote["canales"], otra["canales"])
    assert float(simular(16, prior, gen, con_tendencia=False)["canales"][:, 2].abs().max()) == 0.0
    assert muestrear_prior(1000, prior, gen)[:, 0].exp().max() < 16.5      # alcance truncado
