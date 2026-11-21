"""`estados`: el simulador es coherente con el filtro forward, la red corre y exporta a ONNX sin entrenar."""

import numpy as np
import torch

from motor.estados import simular
from motor.estados.exportar import configuracion, exportar
from motor.estados.red import RedEstados, lote_a_tensores
from nucleo import estados


def test_formas_y_prior_ordenado():
    rng = np.random.default_rng(0)
    lote = simular.simular(rng, 4, 300, simular.cargar_covariables_reales())
    assert lote["filas"].shape == (4, 300, estados.DIM_FILA) and lote["theta"].shape == (4, estados.DIM_THETA)
    assert np.isfinite(lote["filas"]).all() and set(np.unique(lote["nivel"])) <= set(range(estados.NIVELES))
    assert 0.1 < np.isnan(lote["impago"]).mean() < 0.3                              # cerca de 20% por decidir
    assert np.abs(lote["x"].mean(axis=1)).max() < 1e-9                              # covariables estandarizadas por cartera
    th = estados.a_restringido(simular.muestrear_prior(rng, 500))
    assert (np.diff(th["d"], axis=-1) > 0).all()                                    # d_1 < d_2 < d_3 en todo el prior
    assert 500 <= simular.muestrear_n(rng) <= 2000
    assert len(simular.config()["prior"]) == estados.DIM_THETA


def test_paso_local_con_theta_verdadero_da_probabilidades_calibradas():
    """Con el θ con que se simuló, el filtro forward da p que coinciden con la frecuencia real de impago."""
    rng = np.random.default_rng(1)
    lote = simular.simular(rng, 40, 1500)
    datos = {k: lote[k] for k in ("nivel", "uso", "pago_cero", "log_pago", "x")}
    p = np.stack([estados.filtro_forward(lote["theta"][i].astype(np.float64), {k: v[i] for k, v in datos.items()})[2] for i in range(40)])
    real = lote["impago_real"]
    assert abs(p.mean() - real.mean()) < 0.01
    for bajo, alto in ((0.0, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 1.0)):
        tramo = (p >= bajo) & (p < alto)
        assert tramo.sum() > 500 and abs(p[tramo].mean() - real[tramo].mean()) < 0.03, (bajo, alto)
    # Y el filtro recupera el estado del mes 7 mejor que el azar.
    acierto = (np.stack([estados.filtro_forward(lote["theta"][i].astype(np.float64), {k: v[i] for k, v in datos.items()})[1].argmax(-1)
                         for i in range(5)]) == lote["estado"][:5, :, 6]).mean()
    assert acierto > 0.5


def test_red_entrena_un_paso_y_exporta(tmp_path):
    torch.manual_seed(0)
    rng = np.random.default_rng(2)
    red = RedEstados()
    filas, theta = lote_a_tensores(simular.simular(rng, 4, 200))
    perdida = red.perdida(filas, theta)
    perdida.backward()
    assert torch.isfinite(perdida) and red.muestrear(filas, 8).shape == (8, 4, estados.DIM_THETA)
    # Invariante al orden de los clientes.
    permutadas = filas[:, torch.randperm(200)]
    assert torch.allclose(red.resumen(filas), red.resumen(permutadas), atol=1e-4)
    medido = exportar(red, tmp_path, configuracion())
    assert max(medido.values()) < 1e-3, medido
