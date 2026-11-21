"""El bucle común entrena un NPE de juguete, escribe su punto de guardado y lo retoma."""

import torch
from torch import nn

from motor.comun.codificador import CodificadorConjunto
from motor.comun.entrenar import cargar_punto, entrenar
from motor.comun.flujo import FlujoCondicional


class _NPEDeJuguete(nn.Module):
    """θ ~ Normal(0, 1) en 2 dimensiones; D son 20 filas θ + ruido. El posterior es conocido y angosto."""

    def __init__(self):
        super().__init__()
        self.codificador = CodificadorConjunto(dim_fila=2, dim_oculta=32, dim_resumen=16)
        self.flujo = FlujoCondicional(dim_theta=2, dim_contexto=16, capas=4, ocultas=(32, 32))

    def perdida(self, lote: int = 64):
        theta = torch.randn(lote, 2)
        filas = theta[:, None, :] + torch.randn(lote, 20, 2)
        resumen = self.codificador(filas, torch.ones(lote, 20))
        perdida = -self.flujo.log_prob(theta, resumen).mean()
        return perdida, {"npe": float(perdida)}


def test_entrena_guarda_y_retoma(tmp_path):
    torch.manual_seed(0)
    red = _NPEDeJuguete()
    with torch.no_grad():
        antes = float(sum(red.perdida(256)[0] for _ in range(4)) / 4)

    estado = entrenar(red, red.perdida, datasets_por_paso=64, carpeta=tmp_path, minutos=0.08, registrar_cada=20)
    with torch.no_grad():
        despues = float(sum(red.perdida(256)[0] for _ in range(4)) / 4)

    assert (tmp_path / "ultimo.pt").exists() and (tmp_path / "registro.jsonl").exists()
    assert estado["datasets_simulados"] == 64 * estado["pasos"] > 0
    assert despues < antes - 0.5, (antes, despues)       # el prior da ~2,84 nats; el posterior, mucho menos

    # Retomar: una red nueva carga los pesos y el conteo sigue desde donde quedó.
    otra = _NPEDeJuguete()
    guardado = cargar_punto(tmp_path / "ultimo.pt", otra)
    assert guardado["pasos"] == estado["pasos"]
    seguido = entrenar(otra, otra.perdida, datasets_por_paso=64, carpeta=tmp_path, minutos=0.02)
    assert seguido["pasos"] > estado["pasos"]
    assert seguido["datasets_simulados"] == 64 * seguido["pasos"]
