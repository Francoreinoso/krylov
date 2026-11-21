"""El andamio de series con el simulador de `cinetica`: exporta, NumPy = torch, el relleno no cambia nada y la pérdida baja."""

import numpy as np
import torch

from motor.cinetica import simular as esp
from motor.comun import series
from nucleo import series as series_np


def _red(pasos: int = 0):
    torch.manual_seed(0)
    red = series.construir(esp)
    series.fijar_escalas(red, esp, lotes=5)
    gen, perdidas = np.random.default_rng(0), []
    optimizador = torch.optim.AdamW(red.parameters(), 1e-3)
    for _ in range(pasos):
        perdida, _ = red.perdida(series.a_tensores(esp.simular(gen, 64)))
        optimizador.zero_grad(); perdida.backward(); optimizador.step()
        perdidas.append(float(perdida.detach()))
    return red.eval(), perdidas


def test_la_perdida_baja():
    _, perdidas = _red(150)
    assert np.isfinite(perdidas).all() and np.mean(perdidas[-20:]) < np.mean(perdidas[:20]) - 0.5


def test_el_relleno_no_cambia_los_resumenes():
    red, _ = _red()
    t = series.a_tensores(esp.simular(np.random.default_rng(1), 2))
    B, U, K, c = t["x"].shape
    relleno = lambda a, forma: torch.cat([torch.cat([a, torch.zeros(B, U, forma[2] - K, *a.shape[3:])], 2),      # noqa: E731
                                          torch.zeros(B, forma[1] - U, forma[2], *a.shape[3:])], 1)
    x2, m2 = relleno(t["x"], (B, U + 5, K + 7)), relleno(t["mascara"], (B, U + 5, K + 7))
    cov2 = torch.cat([t["cov"], torch.zeros(B, 5, t["cov"].shape[-1])], 1)
    with torch.no_grad():
        s_d, s_j = red.codificador(t["x"], t["mascara"], t["cov"], t["tam"])
        s_d2, s_j2 = red.codificador(x2, m2, cov2, t["tam"])
    assert torch.allclose(s_d, s_d2, atol=1e-5) and torch.allclose(s_j, s_j2[:, :U], atol=1e-5) and float(s_j2[:, U:].abs().max()) == 0.0


def test_exporta_y_numpy_da_lo_mismo_que_torch(tmp_path):
    red, _ = _red()
    diferencias = series.exportar(esp, red, tmp_path)
    assert max(diferencias.values()) < 1e-4, diferencias
    # y el camino completo del servicio: ONNX con formas fijas + los dos flujos en NumPy
    r = series_np._red(str(tmp_path))
    sim = esp.simular(np.random.default_rng(2), 1)
    s_d, s_j = series_np.resumir(r, sim["x"][0], sim["mascara"][0], sim["cov"][0], sim["tam"][0])
    with torch.no_grad():
        t = series.a_tensores(sim)
        s_d_t, s_j_t = red.codificador(t["x"], t["mascara"], t["cov"], t["tam"])
    assert np.abs(s_d - s_d_t[0].numpy()).max() < 1e-4 and np.abs(s_j - s_j_t[0].numpy()).max() < 1e-4
    eta, lam = series_np.muestrear_posterior(r, s_d, s_j, m=8, l=4)
    assert eta.shape == (8, 6) and lam.shape == (8, 4, sim["mascara"].shape[1], 2) and np.isfinite(lam).all()


def test_sbc_chico_corre():
    red, _ = _red()
    informe = series.sbc(esp, red, datasets=60, muestras=19, lote=20)
    assert set(informe["globales"]) == set(esp.NOMBRES_ETA) and set(informe["locales"]) == set(esp.NOMBRES_LAM)
    assert 0 <= informe["cobertura_90_decision"] <= 1 and informe["por_tramo"]
