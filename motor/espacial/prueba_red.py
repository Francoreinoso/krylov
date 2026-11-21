"""La red de `espacial`: gradiente cortado hacia el codificador y exportación a ONNX sin entrenar."""

import torch

from motor.espacial.exportar import configuracion, exportar
from motor.espacial.red import DIM_RESUMEN, RedEspacial
from motor.espacial.simular import Prior, simular
from nucleo.preproceso import LADO


def _red_y_lote(canales: int = 3):
    torch.manual_seed(0)
    gen = torch.Generator().manual_seed(0)
    red = RedEspacial(canales)
    lote = simular(8, Prior(), gen, con_tendencia=canales == 3)
    red.flujo.fijar_escala(simular(512, Prior(), gen)["theta"])
    return red, lote


def test_formas():
    red, lote = _red_y_lote()
    media, log_desv, resumen = red(lote["canales"])
    assert media.shape == log_desv.shape == (8, LADO, LADO) and resumen.shape == (8, DIM_RESUMEN)
    perdidas = red.perdidas(lote)
    assert torch.isfinite(perdidas["mapa"]) and torch.isfinite(perdidas["flujo"])


def test_la_cabeza_de_mapa_entrena_igual_con_y_sin_la_cabeza_de_flujo():
    """La pérdida de mapa y su gradiente son idénticos con la cabeza de flujo sumada o sin ella."""
    red, lote = _red_y_lote()
    del_mapa = list(red.mapa.codificador.parameters()) + list(red.mapa.cabeza_mapa.parameters())

    sola = red.perdidas(lote, con_flujo=False)["mapa"]
    gradiente_sola = torch.autograd.grad(sola, del_mapa)

    juntas = red.perdidas(lote)
    assert torch.equal(juntas["mapa"], sola)
    gradiente_juntas = torch.autograd.grad(juntas["mapa"] + juntas["flujo"], del_mapa)
    for a, b in zip(gradiente_sola, gradiente_juntas):
        assert torch.equal(a, b)

    # La pérdida NPE no llega al codificador ni a la cabeza de mapa; sí al resumidor y al flujo.
    juntas = red.perdidas(lote)
    al_mapa = torch.autograd.grad(juntas["flujo"], del_mapa, allow_unused=True, retain_graph=True)
    assert all(g is None for g in al_mapa)
    al_flujo = torch.autograd.grad(juntas["flujo"], list(red.mapa.resumidor.parameters()) + list(red.flujo.parameters()))
    assert all(g is not None and torch.isfinite(g).all() for g in al_flujo) and any(g.abs().sum() > 0 for g in al_flujo)


def test_exporta_sin_entrenar_y_coincide(tmp_path):
    """onnxruntime da lo mismo que torch (lotes de 1 y de 480), y el flujo en NumPy también."""
    for canales in (3, 2):
        red, _ = _red_y_lote(canales)
        medido = exportar(red, tmp_path / str(canales), configuracion(canales, Prior()))
        assert max(medido.values()) < 1e-3, medido
        assert all((tmp_path / str(canales) / f).exists() for f in ("codificador.onnx", "flujo.npz", "pesos.pt", "config.json"))
