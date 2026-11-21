"""`jerarquico`: el simulador es coherente con el paso local, la red corre y exporta a ONNX sin entrenar."""

import numpy as np
import torch

from motor.jerarquico import simular
from motor.jerarquico.exportar import configuracion, exportar
from motor.jerarquico.red import RedJerarquico, lote_a_tensores
from nucleo import jerarquico as jq


def test_formas_y_asignacion_del_sms():
    rng = np.random.default_rng(0)
    lote = simular.simular(rng, 6, 1500, 20, simular.leer_real())
    b, g, p, c = lote["mascara"].shape
    assert (b, g, c) == (6, 20, simular.CITAS_POR_PACIENTE_MAX) and lote["filas"].shape == (6, 20, p, c, jq.DIM_FILA)
    citas = lote["mascara"].sum((1, 2, 3))
    assert (citas > 900).all() and (citas < 2400).all()
    assert (lote["sms"][lote["espera"] < 3] == 0).all() and lote["sms"].mean() > 0.1       # SMS solo con 3 o más días de espera
    assert (lote["filas"][lote["mascara"] == 0] == 0).all() and np.isfinite(lote["filas"]).all()
    # Las citas de un paciente son contiguas desde la primera: la máscara no tiene huecos.
    assert (np.diff(lote["mascara"], axis=-1) <= 0).all()
    assert len(simular.config()["prior"]) == jq.DIM_THETA
    citas, barrios = simular.muestrear_tamano(rng)
    assert 1000 <= citas <= 3000 and 10 <= barrios <= 40


def test_paso_local_con_theta_verdadero_da_probabilidades_calibradas():
    """Con el θ con que se simuló, la cuadratura anidada da p que coinciden con lo que pasó en las citas por decidir."""
    rng = np.random.default_rng(1)
    lote = simular.simular(rng, 12, 2000, 20)
    p, real = [], []
    for i in range(12):
        d = simular.a_filas_sueltas(lote, i)
        salida = jq.paso_local(lote["theta"][i][None].astype(np.float64), d["z"], d["respuesta"], d["paciente"], d["barrio_del_paciente"])[:, 0]
        falta = np.isnan(d["respuesta"])
        p.append(salida[falta]); real.append(d["respuesta_real"][falta])
    p, real = np.concatenate(p), np.concatenate(real)
    assert abs(p.mean() - real.mean()) < 0.015
    for bajo, alto in ((0.0, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.0)):
        tramo = (p >= bajo) & (p < alto)
        assert tramo.sum() > 200 and abs(p[tramo].mean() - real[tramo].mean()) < 0.04, (bajo, alto, p[tramo].mean(), real[tramo].mean())


def test_red_entrena_un_paso_y_exporta(tmp_path):
    torch.manual_seed(0)
    rng = np.random.default_rng(2)
    red = RedJerarquico()
    filas, mascara, theta = lote_a_tensores(simular.simular(rng, 3, 1000, 10))
    perdida = red.perdida(filas, mascara, theta)
    perdida.backward()
    assert torch.isfinite(perdida) and red.muestrear(filas, mascara, 8).shape == (8, 3, jq.DIM_THETA)
    # Invariante al orden de los barrios y de los pacientes dentro de cada barrio.
    orden_g, orden_p = torch.randperm(filas.shape[1]), torch.randperm(filas.shape[2])
    permutado = red.codificador(filas[:, orden_g][:, :, orden_p], mascara[:, orden_g][:, :, orden_p])
    assert torch.allclose(red.codificador(filas, mascara), permutado, atol=2e-4)
    medido = exportar(red, tmp_path, configuracion())
    assert max(medido.values()) < 1e-3, medido
    assert sorted(f.name for f in tmp_path.iterdir()) == ["codificador.onnx", "config.json", "flujo.npz", "pesos.pt"]


def test_papeles_opcionales_en_el_simulador():
    """D-35: cada dataset sortea qué papeles opcionales trae; el ausente va en cero en Z y su marca entra a las filas."""
    from nucleo import jerarquico as jq
    lote = simular.simular(np.random.default_rng(3), 40, 300, 5)
    presentes = lote["presentes"]
    assert presentes.shape == (40, 7) and 0.3 < (presentes.min(axis=1) == 1).mean() < 0.9 and (presentes == 0).any(axis=0).all()
    i = int(np.flatnonzero(presentes[:, 1] == 0)[0])                          # un dataset sin recordatorio
    existe = lote["mascara"][i] > 0
    assert (lote["z"][i][..., [11, 12]] == 0).all() and (lote["filas"][i][existe][:, 17 + 1] == 0).all() and (lote["sms"][i] == 0).all()
    assert (lote["filas"][i][existe][:, 17:24] == presentes[i]).all() and lote["filas"].shape[-1] == jq.DIM_FILA == 26
    completo = simular.simular(np.random.default_rng(3), 5, 300, 5, opcionales=False)
    assert (completo["presentes"] == 1).all()
