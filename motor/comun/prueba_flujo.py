"""El flujo en NumPy (`nucleo/flujo.py`) da la misma muestra que en torch (`motor/comun/flujo.py`)."""

import numpy as np
import pytest
import torch

from motor.comun.flujo import FlujoCondicional
from nucleo import flujo as flujo_np


def _flujo_con_pesos_al_azar(dim_theta: int, dim_contexto: int) -> FlujoCondicional:
    torch.manual_seed(0)
    f = FlujoCondicional(dim_theta, dim_contexto)
    # Pesos lejos de la inicialización, para que la prueba no pase por tener escalas triviales.
    with torch.no_grad():
        for p in f.parameters():
            p.add_(0.05 * torch.randn_like(p))
    f.fijar_escala(torch.randn(500, dim_theta) * torch.linspace(0.5, 3.0, dim_theta) + 1.0)
    return f


@pytest.mark.parametrize("dim_theta", [7, 32])  # impar y par: las dos mitades del acoplamiento cambian de tamaño
def test_numpy_igual_a_torch(tmp_path, dim_theta):
    f = _flujo_con_pesos_al_azar(dim_theta, 128)
    ruta = str(tmp_path / "flujo.npz")
    f.exportar_npz(ruta)
    pesos = flujo_np.cargar(ruta)

    contexto = torch.randn(5, 128)
    ruido = torch.randn(32, 5, dim_theta)          # 32 muestras del posterior para 5 datasets
    con_torch = f.muestrear_con_ruido(contexto, ruido).detach().numpy()
    con_numpy = flujo_np.muestrear(pesos, contexto.numpy(), ruido.numpy())

    assert con_numpy.shape == (32, 5, dim_theta)
    np.testing.assert_allclose(con_numpy, con_torch, rtol=1e-4, atol=1e-4)


def test_un_solo_dataset_y_semilla_fija(tmp_path):
    f = _flujo_con_pesos_al_azar(7, 128)
    ruta = str(tmp_path / "flujo.npz")
    f.exportar_npz(ruta)
    pesos = flujo_np.cargar(ruta)
    contexto = torch.randn(128)
    z = flujo_np.ruido(semilla=7, m=32, dim_theta=7)
    np.testing.assert_array_equal(z, flujo_np.ruido(semilla=7, m=32, dim_theta=7))
    con_numpy = flujo_np.muestrear(pesos, contexto.numpy(), z)
    con_torch = f.muestrear_con_ruido(contexto, torch.from_numpy(z)).detach().numpy()
    np.testing.assert_allclose(con_numpy, con_torch, rtol=1e-4, atol=1e-4)


def test_muestrear_invierte_la_densidad():
    """La muestra hecha con ruido z tiene log q = log N(z) − log|det|: el flujo es coherente consigo mismo."""
    f = _flujo_con_pesos_al_azar(7, 128)
    contexto, ruido = torch.randn(4, 128), torch.randn(4, 7)
    theta = f.muestrear_con_ruido(contexto, ruido)
    z_de_vuelta = f.nice(contexto).transform((theta - f.media_theta) / f.escala_theta)
    np.testing.assert_allclose(z_de_vuelta.detach().numpy(), ruido.numpy(), rtol=1e-3, atol=1e-3)
    assert torch.isfinite(f.log_prob(theta, contexto)).all()


def test_nucleo_no_importa_torch():
    import pathlib, re
    for archivo in pathlib.Path(flujo_np.__file__).parent.glob("*.py"):
        assert not re.search(r"^\s*(import|from)\s+(torch|zuko|jax|numpyro)\b", archivo.read_text(), re.M), archivo
