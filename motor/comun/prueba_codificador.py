"""Pruebas del codificador de conjuntos: simetrías, conjunto vacío y exportación a ONNX."""

import pytest
import torch

from motor.comun.codificador import (
    CodificadorConjunto,
    PoolingAtencion,
    PoolingPromedio,
    comparar_con_onnxruntime,
    exportar_onnx,
)

DIM_FILA = 5
TOLERANCIA = 1e-4


def lote_con_relleno(lote: int, n: int, semilla: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    """Lote de conjuntos de largos distintos, rellenados hasta n, con su máscara de relleno."""
    generador = torch.Generator().manual_seed(semilla)
    x = torch.randn(lote, n, DIM_FILA, generator=generador)
    largos = torch.linspace(n, max(1, n // 3), lote).long()
    mascara = (torch.arange(n)[None, :] < largos[:, None]).float()
    return x, mascara


@pytest.fixture(params=["atencion", "promedio"])
def codificador(request) -> CodificadorConjunto:
    torch.manual_seed(0)
    return CodificadorConjunto(DIM_FILA, dim_oculta=32, dim_resumen=16, pooling=request.param).eval()


def test_invariante_a_permutaciones(codificador):
    x, mascara = lote_con_relleno(3, 40)
    orden = torch.randperm(40, generator=torch.Generator().manual_seed(1))
    with torch.no_grad():
        original = codificador(x, mascara)
        permutado = codificador(x[:, orden], mascara[:, orden])
    assert original.shape == (3, 16)
    assert torch.allclose(original, permutado, atol=1e-5)


def test_el_contenido_del_relleno_no_importa(codificador):
    x, mascara = lote_con_relleno(3, 40)
    x_sucio = torch.where(mascara.unsqueeze(-1) > 0, x, torch.full_like(x, 1e4))
    with torch.no_grad():
        assert torch.allclose(codificador(x, mascara), codificador(x_sucio, mascara), atol=1e-5)


@pytest.mark.parametrize("pooling", [PoolingAtencion(8), PoolingPromedio(8)])
def test_conjunto_vacio_da_ceros_sin_nan(pooling):
    h = torch.randn(2, 6, 8, requires_grad=True)
    mascara = torch.ones(2, 6)
    mascara[1] = 0.0  # el segundo conjunto no tiene filas reales
    salida = pooling(h, mascara)
    assert torch.isfinite(salida).all()
    assert (salida[1] == 0).all()
    salida.sum().backward()
    assert torch.isfinite(h.grad).all()


def test_pooling_atencion_con_ejes_delanteros_extra():
    """Forma jerárquica (lote, grupos, filas, dim): igual que agrupar a mano grupo por grupo."""
    torch.manual_seed(0)
    pooling = PoolingAtencion(8, cabezas=4)
    h = torch.randn(2, 3, 7, 8)
    mascara = (torch.rand(2, 3, 7) > 0.3).float()
    mascara[0, 1] = 0.0  # un grupo vacío
    salida = pooling(h, mascara)
    assert salida.shape == (2, 3, pooling.dim_salida) == (2, 3, 32)
    assert torch.isfinite(salida).all()
    aplanado = pooling(h.reshape(6, 7, 8), mascara.reshape(6, 7)).reshape(2, 3, 32)
    assert torch.allclose(salida, aplanado, atol=1e-6)


def test_exporta_a_onnx_con_n_variable(codificador, tmp_path):
    """Se exporta con n = 64 y onnxruntime debe coincidir con torch para otros lotes y n."""
    ruta = str(tmp_path / "codificador.onnx")
    ejes = {"x": {0: "lote", 1: "n"}, "mascara": {0: "lote", 1: "n"}}
    exportar_onnx(codificador, lote_con_relleno(2, 64), ruta, ["x", "mascara"], ejes)
    for lote, n in [(1, 50), (3, 300), (2, 1470)]:
        diferencia = comparar_con_onnxruntime(codificador, ruta, lote_con_relleno(lote, n, semilla=n))
        assert diferencia < TOLERANCIA, (lote, n, diferencia)
    # El conjunto vacío tampoco da NaN en el grafo exportado.
    x, mascara = lote_con_relleno(2, 40)
    mascara[1] = 0.0
    assert comparar_con_onnxruntime(codificador, ruta, (x, mascara)) < TOLERANCIA
