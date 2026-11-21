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


def test_sombreros_suman_uno_y_en_los_enteros_son_el_indicador():
    niveles = torch.tensor(red_sv.NIVELES_ENCUESTA)
    en_enteros = red_sv.sombreros(torch.tensor([1.0, 2.0, 3.0, 4.0]), niveles)
    assert torch.allclose(en_enteros, torch.eye(4), atol=1e-6)
    u = torch.linspace(-2.0, 6.0, 81)
    para_los_anos = red_sv.sombreros(u, torch.tensor(red_sv.NUDOS_ANOS))
    assert (para_los_anos >= 0).all() and torch.allclose(para_los_anos.sum(dim=-1), torch.ones(81), atol=1e-6)
    assert para_los_anos[0, 0] == 1 and para_los_anos[-1, -1] == 1                # fuera de los nudos se queda en el extremo


def test_los_atajos_por_tramos_son_frecuencias():
    """Lo que entra a rho por nivel de encuesta es la frecuencia de cada nivel en la empresa, y los cargos que difieren se ven."""
    lote = simular.simular(np.random.default_rng(1), 3, 400, CONFIG)
    filas, grupo, _ = red_sv.lote_a_tensores(lote)
    codificador = red_sv.construir(CONFIG).codificador.eval()
    with torch.no_grad():
        cruzados = codificador._por_tramos(filas, torch.full((3, 1), 400.0))[0].reshape(3, -1, 4) / red_sv.ESCALA_COVARIANZA
    frecuencias = np.stack([(lote["encuestas"] == nivel).mean(axis=1) for nivel in (1, 2, 3, 4)], axis=-1)        # (3, 4 ítems, 4 niveles)
    np.testing.assert_allclose(cruzados[:, :16, 0].numpy().reshape(3, 4, 4), frecuencias, atol=1e-5)
    renuncias_con_nivel_1 = ((lote["encuestas"][..., 0] == 1) & (lote["evento"] == 1)).mean(axis=1)
    np.testing.assert_allclose(cruzados[:, 0, 1].numpy(), renuncias_con_nivel_1, atol=1e-5)
    for a in (0, 1, 2, 5, 9):                                                                                # hasta 10 años, un tramo por año
        np.testing.assert_allclose(cruzados[:, 16 + a, 0].numpy(), (lote["tiempo"] == a).mean(axis=1), atol=1e-5)


def test_un_punto_de_la_red_anterior_se_carga_y_da_el_mismo_resumen():
    """La primera capa de rho se amplía con ceros: el s(D) no cambia, y el optimizador sembrado calza con la red nueva."""
    red = red_sv.construir(CONFIG).eval()
    anterior = red.codificador.entrada_anterior
    de_antes = {nombre: (pesos[:, :anterior].clone() if nombre == red_sv.CAPA_AMPLIADA else pesos.clone()) for nombre, pesos in red.state_dict().items()
                if not nombre.startswith("promedio.") and nombre not in red_sv.ESCALAS_DE_ATAJOS}
    cargada = red_sv.RedSupervivencia(**red_sv.ARQUITECTURA).eval()
    assert red_sv.cargar_estado(cargada, de_antes, CONFIG) and not red_sv.cargar_estado(cargada, cargada.state_dict())
    assert (cargada.codificador.escala_atajos != 1).any()                       # la escala de las entradas nuevas quedó fijada
    filas, grupo, _ = _tensores(3, 250)
    with torch.no_grad():
        red.codificador.rho[0].weight[:, anterior:] = 0.0                       # la red anterior no miraba las entradas nuevas
        assert (red.codificador(filas, grupo) - cargada.codificador(filas, grupo)).abs().max() < 1e-6
    assert (cargada.state_dict()[red_sv.CAPA_AMPLIADA][:, anterior:] == 0).all()


def test_el_promedio_movil_sigue_a_los_pesos_y_se_puede_usar():
    red = red_sv.construir(CONFIG)
    nombre, pesos = red._pesos()[0]
    antes = pesos.detach().clone()
    with torch.no_grad():
        pesos.add_(1.0)
    red.actualizar_promedio(0.9)
    assert torch.allclose(getattr(red.promedio, nombre), antes + 0.1, atol=1e-6)
    assert not any(p.requires_grad for p in red.promedio.buffers())             # el optimizador no lo toca
    red.usar_promedio()
    assert torch.allclose(pesos, antes + 0.1, atol=1e-6)
