"""Motor `supervivencia` (rotación): piezas en NumPy que comparten el simulador y el servicio.

Modelo generativo: WORKPLAN.md, sección 11.2. Aquí viven
  - el preprocesamiento: la MISMA función para los datasets simulados y para el archivo real,
  - la base B-spline del efecto no lineal del sueldo,
  - el paso entre θ con restricciones y θ libre (el espacio donde trabaja el flujo normalizador),
  - la lectura del CSV de un caso según los papeles de `casos/<nombre>.yaml`.

Solo NumPy y la biblioteca estándar: este módulo lo importa el servicio (sin torch, jax ni numpyro).
"""
from __future__ import annotations

import csv

import numpy as np

# ----------------------------------------------------------------------------------------------
# QUÉ ES «RIESGO» EN ESTE MOTOR (decisión provisoria del equipo, 21-nov).
# Riesgo = p_i = P(δ_i = 1 | t_i, x_i, y_i, cargo, θ): la probabilidad de que la persona YA haya
# renunciado. Es lo único que el examen con datos reservados puede comprobar (ahí se esconde δ).
# Si el equipo lo cambia (por ejemplo a «renuncia dentro del próximo año»), este es el punto:
# cambia esta constante y la función del paso local que la lee (`riesgo`, tarea A-N2). El
# simulador y la red no cambian, porque la red solo entrega el posterior de θ.
RIESGO = "ya_renuncio"
# ----------------------------------------------------------------------------------------------

VERSION_PREPROCESO = "supervivencia-1"

N_EFECTOS = 3      # horas extra, distancia, empresas previas
N_SPLINE = 6       # coeficientes del B-spline cúbico en w
N_ENCUESTAS = 4    # ítems ordinales de 1 a 4
N_CORTES = 3
DIM_THETA = 32
DIM_FILA = 11      # lo que recibe el codificador por persona (ver `armar_filas`)

# Posiciones de θ libre (sin restricciones). El flujo trabaja en este espacio.
I_LOG_K = 0
I_BETA0 = 1
I_BETA = slice(2, 5)
I_GAMMA = slice(5, 11)
I_LOG_TAU = 11
I_LOG_SIGMA_U = 12
I_LAMBDA = 13
I_LOG_A = slice(14, 18)
I_CORTES = slice(18, 30)   # por ítem: c_1, log(c_2 − c_1), log(c_3 − c_2)
I_MU_C = 30
I_LOG_S_C = 31

NOMBRES_THETA = (
    ["log_k", "beta0"]
    + [f"beta_{j}" for j in range(N_EFECTOS)]
    + [f"gamma_{m}" for m in range(N_SPLINE)]
    + ["log_tau", "log_sigma_u", "lambda"]
    + [f"log_a_{j}" for j in range(N_ENCUESTAS)]
    + [f"corte_{j}_{m}" for j in range(N_ENCUESTAS) for m in range(N_CORTES)]
    + ["mu_c", "log_s_c"]
)

# Nudos del B-spline cúbico: 6 funciones sobre w ∈ [−3, 3] (w es el log del sueldo estandarizado).
LIMITE_W = 3.0
NUDOS = np.array([-3, -3, -3, -3, -1, 1, 3, 3, 3, 3], dtype=float)


def base_spline(w: np.ndarray) -> np.ndarray:
    """Base B-spline cúbica evaluada en w. Devuelve (..., 6); cada fila suma 1 (Cox–de Boor)."""
    w = np.clip(np.asarray(w, dtype=float), -LIMITE_W, LIMITE_W - 1e-9)[..., None]
    t = NUDOS
    base = ((w >= t[:-1]) & (w < t[1:])).astype(float)
    for p in range(1, 4):
        d1 = t[p:-1] - t[: -p - 1]
        d2 = t[p + 1 :] - t[1:-p]
        izq = np.where(d1 > 0, (w - t[: -p - 1]) / np.where(d1 > 0, d1, 1.0), 0.0)
        der = np.where(d2 > 0, (t[p + 1 :] - w) / np.where(d2 > 0, d2, 1.0), 0.0)
        base = izq * base[..., :-1] + der * base[..., 1:]
    return base


# ------------------------------------------------------------------------------ preprocesamiento

def estandarizar(efectos: np.ndarray, sueldo: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Covariables crudas → (x, w) con la escala del propio dataset.

    efectos: (..., n, 3) en sus unidades; sueldo: (..., n), positivo.
    x: cada efecto menos su promedio, dividido por su dispersión en el dataset.
    w: log del sueldo estandarizado igual, recortado a [−3, 3] (el dominio del spline).
    """
    efectos = np.asarray(efectos, dtype=float)
    desv = efectos.std(axis=-2, keepdims=True)
    x = (efectos - efectos.mean(axis=-2, keepdims=True)) / np.where(desv > 1e-9, desv, 1.0)
    log_s = np.log(np.maximum(np.asarray(sueldo, dtype=float), 1e-9))
    desv_s = log_s.std(axis=-1, keepdims=True)
    w = (log_s - log_s.mean(axis=-1, keepdims=True)) / np.where(desv_s > 1e-9, desv_s, 1.0)
    return x, np.clip(w, -LIMITE_W, LIMITE_W)


def armar_filas(x, w, encuestas, tiempo, evento) -> np.ndarray:
    """Una fila de 11 números por persona, lista para el codificador. Devuelve float32 (..., n, 11).

    Columnas: x (3) · w (1) · encuestas centradas (4) · log(1 + años) centrado (1) ·
    δ observado (1; cero si está por decidir) · marca «por decidir» (1).
    `evento` trae 1 (renunció), 0 (sigue) o NaN (vacío: la persona está por decidir).
    """
    evento = np.asarray(evento, dtype=float)
    por_decidir = np.isnan(evento)
    return np.concatenate(
        [
            x,
            w[..., None],
            (np.asarray(encuestas, dtype=float) - 2.5) / 1.5,
            (np.log1p(np.asarray(tiempo, dtype=float)) - 1.8)[..., None],
            np.where(por_decidir, 0.0, evento)[..., None],
            por_decidir.astype(float)[..., None],
        ],
        axis=-1,
    ).astype(np.float32)


def preprocesar(efectos, sueldo, encuestas, tiempo, evento) -> np.ndarray:
    """El único preprocesamiento de `supervivencia`: columnas crudas → filas del codificador.

    Lo llaman el simulador (con un lote de datasets, eje inicial B) y el servicio (un dataset).
    """
    x, w = estandarizar(efectos, sueldo)
    return armar_filas(x, w, encuestas, tiempo, evento)


# ------------------------------------------------------------------- θ con restricciones ↔ libre

def a_libre(th: dict) -> np.ndarray:
    """θ con restricciones (diccionario, eje inicial B) → vector libre (B, 32)."""
    c = th["cortes"]                                           # (B, 4, 3), ordenados
    cortes = np.stack(
        [c[..., 0], np.log(c[..., 1] - c[..., 0]), np.log(c[..., 2] - c[..., 1])], axis=-1
    )
    partes = [
        np.log(th["k"])[:, None], th["beta0"][:, None], th["beta"], th["gamma"],
        np.log(th["tau"])[:, None], np.log(th["sigma_u"])[:, None], th["lambda"][:, None],
        np.log(th["a"]), cortes.reshape(len(c), -1),
        th["mu_c"][:, None], np.log(th["s_c"])[:, None],
    ]
    return np.concatenate(partes, axis=1)


def a_restringido(libre: np.ndarray) -> dict:
    """Vector libre (B, 32) → θ con restricciones. Inversa exacta de `a_libre`."""
    libre = np.asarray(libre, dtype=float)
    crudo = libre[:, I_CORTES].reshape(-1, N_ENCUESTAS, N_CORTES)
    c1 = crudo[..., 0]
    c2 = c1 + np.exp(crudo[..., 1])
    c3 = c2 + np.exp(crudo[..., 2])
    return {
        "k": np.exp(libre[:, I_LOG_K]),
        "beta0": libre[:, I_BETA0],
        "beta": libre[:, I_BETA],
        "gamma": libre[:, I_GAMMA],
        "tau": np.exp(libre[:, I_LOG_TAU]),
        "sigma_u": np.exp(libre[:, I_LOG_SIGMA_U]),
        "lambda": libre[:, I_LAMBDA],
        "a": np.exp(libre[:, I_LOG_A]),
        "cortes": np.stack([c1, c2, c3], axis=-1),
        "mu_c": libre[:, I_MU_C],
        "s_c": np.exp(libre[:, I_LOG_S_C]),
    }


# ------------------------------------------------------------------------- lectura de un archivo

_SI = {"yes", "si", "sí", "y", "true", "1"}


def _a_numero(columna: list[str]) -> np.ndarray:
    """Texto → float. Vacío → NaN; «Yes»/«Sí» → 1; cualquier otro texto → 0."""
    salida = np.empty(len(columna))
    for i, valor in enumerate(columna):
        valor = valor.strip()
        if valor == "":
            salida[i] = np.nan
            continue
        try:
            salida[i] = float(valor)
        except ValueError:
            salida[i] = 1.0 if valor.lower() in _SI else 0.0
    return salida


def leer_tabla(ruta, columnas: dict) -> dict:
    """Lee el CSV de un caso con los papeles de `columnas` (casos/<nombre>.yaml).

    Devuelve las columnas crudas que recibe `preprocesar`, más `grupo` (códigos 0..G−1),
    `cargos` (los nombres) e `id`.
    """
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        filas = list(csv.DictReader(archivo))
    col = lambda nombre: [fila[nombre] for fila in filas]
    cargos, grupo = np.unique(np.array(col(columnas["grupo"])), return_inverse=True)
    return {
        "id": col(columnas["id"]),
        "efectos": np.stack([_a_numero(col(c)) for c in columnas["efectos"]], axis=1),
        "sueldo": _a_numero(col(columnas["suave"])),
        "encuestas": np.stack([_a_numero(col(c)) for c in columnas["encuestas"]], axis=1),
        "tiempo": _a_numero(col(columnas["tiempo"])),
        "evento": _a_numero(col(columnas["evento"])),
        "grupo": grupo.astype(np.int64),
        "cargos": [str(c) for c in cargos],
    }
