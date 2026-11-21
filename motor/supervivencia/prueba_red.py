"""Pruebas de la red de `supervivencia`: codificador jerárquico, pérdida NPE y exportación."""
import numpy as np
import torch

from motor.supervivencia import exportar, red as red_sv, simular

CONFIG = simular.cargar_config()


def _tensores(B, n, semilla=0):
    return red_sv.lote_a_tensores(simular.simular(np.random.default_rng(semilla), B, n, CONFIG))


def test_resumen_invariante_al_orden_de_las_filas_y_al_nombre_de_los_cargos():
    red = red_sv.construir(CONFIG).eval()
    filas, grupo, _ = _tensores(4, 300)
    orden = torch.randperm(300, generator=torch.Generator().manual_seed(0))
    with torch.no_grad():
        resumen = red.codificador(filas, grupo)
        assert resumen.shape == (4, 128)
        assert (resumen - red.codificador(filas[:, orden], grupo[:, orden])).abs().max() < 1e-4
        renombrado = (grupo + 5) % simular.CARGOS_MAX
        assert (resumen - red.codificador(filas, renombrado)).abs().max() < 1e-4


def test_la_perdida_npe_baja():
    torch.manual_seed(0)
    torch.set_num_threads(2)
    red = red_sv.construir(CONFIG)
    optimizador = torch.optim.Adam(red.parameters(), lr=5e-4)
    rng, perdidas = np.random.default_rng(0), []
    for _ in range(60):
        lote = simular.simular(rng, 16, 300, CONFIG)
        perdida = red.perdida(*red_sv.lote_a_tensores(lote))
        optimizador.zero_grad(); perdida.backward(); optimizador.step()
        perdidas.append(perdida.item())
    assert np.isfinite(perdidas).all()
    assert np.mean(perdidas[-10:]) < np.mean(perdidas[:10]) - 1.0


def test_exporta_sin_entrenar_con_n_variable(tmp_path):
    """Codificador en onnxruntime y flujo en NumPy dan lo mismo que torch."""
    diferencias = exportar.exportar(red_sv.construir(CONFIG), tmp_path)
    assert max(diferencias.values()) < exportar.TOLERANCIA, diferencias
