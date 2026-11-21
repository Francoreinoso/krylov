"""Muestreo en NumPy del flujo normalizador condicional de acoplamiento afín.

Es la copia, sin torch, de `motor/comun/flujo.py`: lee `flujo.npz` y convierte ruido
normal estándar en muestras del posterior amortizado q(θ | s(D)). El servidor solo
tiene NumPy y onnxruntime, así que el flujo se muestrea aquí.

Cada capa de acoplamiento parte θ en dos mitades fijas (a, b). Al entrenar, la capa
lleva θ hacia el ruido:  z_b = θ_b · exp(e) + d,  con (d, e) = MLP(θ_a, s).
Muestrear es recorrer las capas al revés:  θ_b = (z_b − d) / exp(e).
Como θ_a no cambia dentro de la capa, el MLP se evalúa una sola vez: son productos
de matrices.

`motor/comun/prueba_flujo.py` exige que esta función y la de torch den la misma
muestra con los mismos pesos y el mismo ruido (tolerancia de float32).
"""

from __future__ import annotations

import numpy as np


def cargar(ruta: str) -> dict:
    """Lee `flujo.npz` a un diccionario con las capas ya ordenadas."""
    with np.load(ruta) as z:
        datos = {k: z[k] for k in z.files}
    capas = []
    for i in range(int(datos["n_capas"])):
        mascara = datos[f"capa{i}_mascara"].astype(bool)
        n = int(datos[f"capa{i}_n_lineales"])
        capas.append({
            "idx_a": np.flatnonzero(mascara),      # mitad que pasa intacta y condiciona
            "idx_b": np.flatnonzero(~mascara),     # mitad que se transforma
            "W": [datos[f"capa{i}_W{j}"].astype(np.float32) for j in range(n)],
            "b": [datos[f"capa{i}_b{j}"].astype(np.float32) for j in range(n)],
        })
    extra = {k: v for k, v in datos.items() if not k.startswith("capa") and k != "n_capas"}
    return {"capas": capas, **extra}


def ruido(semilla: int, m: int, dim_theta: int) -> np.ndarray:
    """Ruido normal estándar con semilla fija: misma entrada, misma respuesta."""
    return np.random.default_rng(semilla).standard_normal((m, dim_theta)).astype(np.float32)


def _mlp(x: np.ndarray, W: list[np.ndarray], b: list[np.ndarray]) -> np.ndarray:
    for j, (Wj, bj) in enumerate(zip(W, b)):
        x = x @ Wj.T + bj
        if j < len(W) - 1:
            x = np.maximum(x, 0.0)  # ReLU
    return x


def muestrear(flujo: dict, contexto: np.ndarray, ruido: np.ndarray) -> np.ndarray:
    """Muestras de q(θ | s) en espacio sin restricciones.

    contexto: (..., c), el resumen s(D) del codificador.
    ruido:    (m, ..., d) o (..., d), normal estándar.
    Devuelve un arreglo con la forma de `ruido`.
    """
    theta = np.array(ruido, dtype=np.float32)
    contexto = np.broadcast_to(np.asarray(contexto, dtype=np.float32), theta.shape[:-1] + (contexto.shape[-1],))
    log_pendiente = abs(np.log(np.float32(flujo["pendiente_minima"])))
    for capa in reversed(flujo["capas"]):
        a, b = capa["idx_a"], capa["idx_b"]
        phi = _mlp(np.concatenate([theta[..., a], contexto], axis=-1), capa["W"], capa["b"])
        phi = phi.reshape(phi.shape[:-1] + (len(b), 2))
        desplazamiento, e = phi[..., 0], phi[..., 1]
        log_escala = e / (1.0 + np.abs(e) / log_pendiente)   # acota la escala, igual que zuko
        theta[..., b] = (theta[..., b] - desplazamiento) / np.exp(log_escala)
    return theta * flujo["escala_theta"] + flujo["media_theta"]
