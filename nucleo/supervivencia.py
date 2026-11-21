"""Motor `supervivencia` (rotación): piezas en NumPy que comparten el simulador y el servicio.

Modelo generativo: WORKPLAN.md, sección 11.2. Aquí viven
  - el preprocesamiento: la MISMA función para los datasets simulados y para el archivo real,
  - la base B-spline del efecto no lineal del sueldo,
  - el paso entre θ con restricciones y θ libre (el espacio donde trabaja el flujo normalizador),
  - los papeles de columna que recibe la red (`PAPELES`) y la lectura de una tabla según esos papeles:
    el archivo de `casos/<nombre>.yaml` o el que subió el usuario (D-34).

Solo NumPy, la biblioteca estándar y los módulos de `nucleo/`: este módulo lo importa el servicio
(sin torch, jax ni numpyro).
"""
from __future__ import annotations

import csv
import hashlib
import os
from functools import cache

import numpy as np

from nucleo import casos as _casos, decision, flujo as flujo_numpy, tabla
from nucleo.casos import ArchivoNoCalza, ErrorKrylov, implementacion, tabla_del_caso

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

# Los papeles de columna que recibe la red (D-34), con la forma de `contratos/CONTRATO.md`, sección 2.
# La red de la noche se entrenó con esquema fijo: en todos, `minimo` = `maximo` (D-35: sin papeles opcionales).
PAPELES = [
    {"papel": "id", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "texto", "texto": "Identificador de la persona",
     "texto_largo": "Un código o número que distingue a cada persona; no entra al modelo, solo nombra a quién se refiere cada respuesta"},
    {"papel": "evento", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "si_no", "texto": "Renunció (vacío en las personas por decidir)",
     "texto_largo": "Si la persona ya se fue de la empresa: sí o no (o 1 y 0). Va vacío en las personas sobre las que hay que decidir"},
    {"papel": "tiempo", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "numero", "texto": "Años en la empresa",
     "texto_largo": "Cuánto lleva o llevó la persona en la empresa, en años; si se fue, hasta que se fue. Se cuenta en años cumplidos"},
    {"papel": "grupo", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "texto", "texto": "Cargo o grupo de la persona",
     "texto_largo": "El cargo, equipo o área de la persona: cada grupo tiene su propio nivel de riesgo. La red practicó con 3 a 12 grupos"},
    {"papel": "efectos", "cantidad": N_EFECTOS, "minimo": N_EFECTOS, "maximo": N_EFECTOS, "tipo": "numero", "texto": "Tres factores de la persona",
     "texto_largo": "Tres datos de la persona que pueden mover el riesgo de irse, cada uno un número o un sí o no "
                    "(por ejemplo horas extra, distancia a la casa, empresas anteriores). La red practicó con exactamente tres"},
    {"papel": "suave", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "numero", "texto": "Sueldo",
     "texto_largo": "El sueldo de la persona, mayor que cero, en cualquier moneda. Su efecto no tiene por qué ser parejo: se lee en logaritmo"},
    {"papel": "encuestas", "cantidad": N_ENCUESTAS, "minimo": N_ENCUESTAS, "maximo": N_ENCUESTAS, "tipo": "entero",
     "texto": "Cuatro preguntas de encuesta, de 1 a 4",
     "texto_largo": "Cuatro preguntas de una encuesta de clima o satisfacción, cada una respondida con un entero de 1 (lo peor) a 4 (lo mejor). "
                    "De ellas sale el compromiso de la persona, que no se ve en los datos. La red practicó con exactamente cuatro"},
]
PERSONAS_MINIMO, PERSONAS_MAXIMO = 200, 2000      # el rango del simulador; con más filas se toma una muestra (contrato, sección 1)
# La nube se simula con el n del archivo (WORKPLAN.md 11.9). Para un archivo subido, de cualquier tamaño, hay nubes
# guardadas en esta grilla (`motor/supervivencia/nube.py`) y se usa la del tamaño más cercano, en escala logarítmica.
TAMANOS_DE_NUBE = (200, 300, 450, 650, 950, 1400, 2000)


def nube_del_tamano(personas: int) -> str:
    return f"nube_n{personas:04d}.npz"


def columnas_del_papel(col: dict, papel: str) -> list[str]:
    """Los nombres de columna asignados a un papel: en el YAML y en `analizar_archivo` van como un nombre o como una lista."""
    valor = col.get(papel)
    return [] if valor is None else list(valor) if isinstance(valor, (list, tuple)) else [valor]


def nombres_por_papel(col: dict) -> dict[str, list[str]]:
    """Las columnas de cada papel de `PAPELES`, exigiendo las cantidades con que practicó la red.

    Un papel sin columnas es `rojo_datos` (falta algo); uno con otra cantidad es `rojo_modelo`: la red se entrenó
    con esquema fijo y un archivo con dos factores o cinco encuestas no es de la familia que conoce (D-34).
    """
    nombres = {}
    for p in PAPELES:
        asignadas = columnas_del_papel(col, p["papel"])
        if not asignadas:
            raise ArchivoNoCalza(f"Falta el papel «{p['papel']}»: {p['texto'][:1].lower() + p['texto'][1:]}.")
        if len(asignadas) != p["maximo"]:
            raise ArchivoNoCalza(f"El papel «{p['papel']}» tiene {len(asignadas)} columnas y la red de rotación practicó con exactamente {p['maximo']}.", "rojo_modelo")
        nombres[p["papel"]] = asignadas
    return nombres


def _numero_o_si_no(t: dict, nombre: str) -> np.ndarray:
    """Un factor de la persona: números, o sí y no leídos como 1 y 0. Sin celdas vacías."""
    valores = np.empty(len(tabla.columna(t, nombre)))
    for i, texto in enumerate(t[nombre]):
        try:
            valores[i] = float(texto)
        except ValueError:
            try:
                valores[i] = tabla.si_no(texto)
            except KeyError:
                valores[i] = np.nan
    if not np.isfinite(valores).all():
        raise ArchivoNoCalza(f"La columna «{nombre}» tiene celdas vacías o que no son un número ni un sí o no.")
    return valores


def columnas_crudas(t: dict, col: dict) -> dict:
    """Una tabla (columna → lista de textos) leída con los papeles de `col`: las columnas crudas que recibe `preprocesar`.

    Devuelve además `grupo` (códigos 0..G−1), `cargos` (los nombres) e `id`. Lanza `ArchivoNoCalza` si falta un papel,
    una columna no se puede leer o trae valores que el modelo no conoce.
    """
    nombres = nombres_por_papel(col)
    cargos, grupo = np.unique(np.array(tabla.columna(t, nombres["grupo"][0])), return_inverse=True)
    sueldo = tabla.numeros(t, nombres["suave"][0])
    if (sueldo <= 0).any():
        raise ArchivoNoCalza(f"La columna «{nombres['suave'][0]}» se lee en logaritmo y tiene que ser mayor que cero.", "rojo_modelo")
    return {
        "id": tabla.columna(t, nombres["id"][0]),
        "efectos": np.stack([_numero_o_si_no(t, c) for c in nombres["efectos"]], axis=1),
        "sueldo": sueldo,
        "encuestas": np.stack([tabla.numeros(t, c, minimo=1, maximo=4, enteros=True) for c in nombres["encuestas"]], axis=1),
        "tiempo": np.floor(tabla.numeros(t, nombres["tiempo"][0], minimo=0)),      # años cumplidos: t = ⌊min(T, C)⌋ (WORKPLAN.md 11.2)
        "evento": tabla.respuesta_si_no(t, nombres["evento"][0]),
        "grupo": grupo.astype(np.int64),
        "cargos": [str(c) for c in cargos],
    }


def leer_tabla(ruta, columnas: dict) -> dict:
    """Lee el CSV de un caso con los papeles de `columnas` (casos/<nombre>.yaml). Ver `columnas_crudas`."""
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        filas = list(csv.DictReader(archivo))
    return columnas_crudas({nombre: [fila[nombre] for fila in filas] for nombre in (filas[0] if filas else {})}, columnas)


# =========================================================================================
# Paso local exacto: P(renunció | lo observado, θ) con cuadratura de Gauss-Hermite anidada
# =========================================================================================
#
# Dado θ, de una persona con el evento vacío falta saber dos cosas, cada una de una dimensión: el
# efecto de su cargo u_g y su compromiso z_i. La verosimilitud por intervalos de WORKPLAN.md 11.2,
# con h = exp(η) y η = β0 + x·β + s(w) + u − λ z, es
#
#     δ = 1:   f1 = [S_T(t) − S_T(t+1)] · S_C(t+½)          S_T(t) = exp(−h t^k)
#     δ = 0:   f0 = S_T(t+½) · [S_C(t) − S_C(t+1)]          S_C = supervivencia de la censura LogNormal
#     δ vacío: f1 + f0                                       (la persona aporta sus años igual)
#
# Las cuatro encuestas dependen solo de z. Integrando z por persona:
#
#     M1_i(u) = ∫ f1 · p(encuestas | z) φ(z) dz,     M0_i(u) = ∫ f0 · p(encuestas | z) φ(z) dz
#     L_i(u)  = M1_i si renunció, M0_i si sigue, M1_i + M0_i si está por decidir
#     p(u_g | datos del cargo, θ) ∝ Normal(u; 0, σ_u) · Π_{i en g} L_i(u)
#     p_i = ∫ p(u_g | datos del cargo, θ) · M1_i(u) / (M1_i(u) + M0_i(u)) du
#
# Las dos cuadraturas son ADAPTATIVAS: los nodos de Gauss-Hermite se centran y se escalan en el
# integrando, no en el prior. Un cargo junta hasta cientos de personas y deja el posterior de u_g
# mucho más angosto que el prior (con los nodos del prior caería entre dos nodos); y una persona con
# muchos años, o con un θ poco compatible con sus datos, tiene su compromiso lejos de cero. Cada
# integrando se ubica con pasos de Newton sobre su logaritmo (derivadas analíticas): el centro es
# el máximo y el ancho sale de la curvatura. Ubicar mal solo cuesta nodos: la cuadratura que sigue
# converge al mismo valor con cualquier centro.

CARGOS_MAX = 12            # los mismos que ve el codificador; los cargos de más se juntan en el último
NODOS_CARGO, NODOS_PERSONA = 8, 12
_NODOS_AL_UBICAR = 6                    # nodos de persona mientras se busca dónde está el posterior de cada cargo
_NODOS_AL_UBICAR_RAPIDO, _TOLERANCIA_RAPIDA, _PASOS_RAPIDO = 7, 0.3, 4     # en el modo de la cartera: nodos de persona al ubicar, cuánto puede moverse un centro (en anchos) para darlo por ubicado, y tope de pasos
_ELEMENTOS_POR_TANDA = 600_000          # tope de (muestras × personas × nodos²) por tanda: acota la memoria del servidor
_LOG_2PI_MEDIO = 0.9189385332046727
_erfc = np.frompyfunc(__import__("math").erfc, 1, 1)


def supervivencia_censura(c, mu_c, s_c) -> np.ndarray:
    """S_C(c) = P(C > c) con C ~ LogNormal(μ_c, s_c). Exacta (math.erfc); S_C(0) = 1. Las formas se difunden."""
    c = np.asarray(c, dtype=np.float64)
    with np.errstate(divide="ignore"):
        x = (np.log(c) - mu_c) / s_c
    return 0.5 * _erfc(x / np.sqrt(2.0)).astype(np.float64)


def variables_del_modelo(tabla: dict) -> dict:
    """De las columnas crudas (`leer_tabla` o el simulador) a lo que usa el paso local: x, w, encuestas, tiempo, evento, grupo."""
    x, w = estandarizar(tabla["efectos"], tabla["sueldo"])
    return {"x": x, "w": w, "encuestas": np.clip(np.rint(tabla["encuestas"]), 1, 4).astype(int),
            "tiempo": np.maximum(np.asarray(tabla["tiempo"], dtype=np.float64), 0.0),
            "evento": np.asarray(tabla["evento"], dtype=np.float64), "grupo": np.minimum(tabla["grupo"], CARGOS_MAX - 1)}


def _logistica(x):
    return 1.0 / (1.0 + np.exp(-x))


def _integrar(th: dict, d: dict, nodos: int, nodos_persona: int, pasos: int, rapido: bool = False) -> np.ndarray:
    """El paso local con un eje delantero E en θ y en los datos. Devuelve P(δ = 1 | lo observado, θ), (E, n).

    th: θ con restricciones, cada parámetro con eje delantero E. d: `x` (E, n, 3), `w`, `tiempo`, `evento`, `grupo` (E, n)
    y `encuestas` (E, n, 4). Con una empresa y E muestras de θ, los datos se repiten; en la cartera, E empresas distintas.
    Si d trae `base_w` (la base B-spline de w, que no depende de θ), no se recalcula.

    rapido=True es el modo de la cartera, para θ compatibles con los datos (una red entrenada sobre empresas del simulador):
    el posterior de cada cargo se aproxima por la gaussiana que deja Newton (Laplace: centro en el máximo, ancho por la
    curvatura), buscada con los nodos del prior de z; y la cuadratura final, con nodos adaptados a cada persona, corre
    solo sobre las personas por decidir. Las demás devuelven NaN.
    """
    E, n = d["tiempo"].shape
    k, lam, sigma = th["k"][:, None], th["lambda"][:, None], th["sigma_u"][:, None]
    t, evento = d["tiempo"], d["evento"]
    # Las potencias de los años y la censura solo dependen de los años, que son enteros: se tabulan por valor distinto de t.
    anos, cual = np.unique(t, return_inverse=True)
    cual = cual.reshape(E, n)
    tk_0, tk_medio, tk_1 = (np.take_along_axis((anos[None, :] + mas) ** k, cual, axis=1) for mas in (0.0, 0.5, 1.0))    # t^k, (t+½)^k, (t+1)^k
    def s_c(mas):
        return np.take_along_axis(supervivencia_censura(anos[None, :] + mas, th["mu_c"][:, None], th["s_c"][:, None]), cual, axis=1)
    log_a1, log_a0 = np.log(np.maximum(s_c(0.5), 1e-300)), np.log(np.maximum(s_c(0.0) - s_c(1.0), 1e-300))
    # Los dos cortes que encierran la respuesta de cada persona a cada encuesta: P(y) = logistic(c_alto − a z) − logistic(c_bajo − a z).
    # Con e = exp(a z) esa resta es (1 − ρ)·e / [(1 + κ e)(e + ν)], con κ = exp(−c_alto), ν = exp(c_bajo) y ρ = κ ν:
    # una exponencial por encuesta, sin restar números parecidos, y con los cortes ±∞ de los extremos dando κ = 0 o ν = 0.
    infinito = np.full((E, N_ENCUESTAS, 1), np.inf)
    cortes = np.concatenate([-infinito, th["cortes"], infinito], axis=2)[:, None]      # (E, 1, 4, 5)
    y = d["encuestas"][..., None] - 1                                                  # (E, n, 4, 1)
    kappa, nu = np.take_along_axis(np.exp(-cortes), y + 1, axis=3), np.take_along_axis(np.exp(cortes), y, axis=3)    # (E, n, 4, 1)
    a_item = th["a"][:, None, :, None]                                                  # (E, 1, 4, 1)
    # Lo que se sabe de cada persona, (E, n, ...): los cierres de abajo lo reciben entero o solo de las personas por decidir.
    todas = {
        "base": th["beta0"][:, None] + np.einsum("enj,ej->en", d["x"], th["beta"])
                + np.einsum("enm,em->en", d["base_w"] if "base_w" in d else base_spline(d["w"]), th["gamma"]),
        "grupo": d["grupo"], "renuncio": evento == 1, "sigue": evento == 0, "tk_0": tk_0, "tk_medio": tk_medio, "tk_1": tk_1, "salto": tk_1 - tk_0,
        "log_a1": log_a1, "log_a0": log_a0, "a1": np.exp(log_a1), "a0": np.exp(log_a0), "kappa": kappa, "nu": nu, "uno_menos_rho": 1.0 - kappa * nu,
    }
    cargo_plano = (d["grupo"] + CARGOS_MAX * np.arange(E)[:, None]).ravel()            # el cargo de cada persona, numerado a través de las E empresas

    def por_cargo(v):
        """Suma sobre las personas de cada cargo: (E, n) → (E, G)."""
        return np.bincount(cargo_plano, weights=v.ravel(), minlength=E * CARGOS_MAX).reshape(E, CARGOS_MAX)

    def log_persona(p, z):
        """log[φ(z) · p(las cuatro encuestas | z)] en los nodos z de cada persona: (E, n, K)."""
        e = np.exp(np.clip(a_item * z[:, :, None, :], -300.0, 300.0))                   # (E, n, 4, K)
        ver = (p["uno_menos_rho"] * e / ((1.0 + p["kappa"] * e) * (e + p["nu"]))).prod(axis=2)
        return -0.5 * z ** 2 - _LOG_2PI_MEDIO + np.log(np.maximum(ver, 1e-300))

    def ubicar_z(p, centro_u, m, vueltas):
        """Dónde vive el integrando en z de cada persona, con u en el centro de su cargo: máximo y ancho, (E, n).

        Newton sobre F(z) = log φ(z) + Σ log P(encuesta | z) + log p(años y evento | u, z). Con v = log h = cte − λ z,
        las derivadas del último término respecto de v son: si sigue, −h(t+½)^k las dos; si renunció,
        −h t^k + q y −h t^k + q(1 − x − q), con x = h·[(t+1)^k − t^k] y q = x / (e^x − 1); si falta, la mezcla de las dos.
        """
        log_h_u = p["base"] + np.take_along_axis(centro_u, p["grupo"], axis=1)
        kappa_, nu_, a_ = p["kappa"][..., 0], p["nu"][..., 0], a_item[..., 0]
        for _ in range(vueltas):
            e = np.exp(np.clip(a_ * m[..., None], -300.0, 300.0))                       # (E, n, 4)
            alto, bajo = 1.0 / (1.0 + kappa_ * e), nu_ / (e + nu_)                      # las dos logísticas
            d_bajo, d_alto = bajo * (1 - bajo), alto * (1 - alto)
            ver = np.maximum(p["uno_menos_rho"][..., 0] * e * alto / (e + nu_), 1e-300)
            g_encuestas = -a_ * (d_alto - d_bajo) / ver
            h_encuestas = a_ ** 2 * (d_alto * (1 - 2 * alto) - d_bajo * (1 - 2 * bajo)) / ver - g_encuestas ** 2
            h = np.exp(np.clip(log_h_u - lam * m, -700.0, 46.0))
            x = np.maximum(h * p["salto"], 1e-12)
            q = x / np.expm1(x)
            g1, g0 = -h * p["tk_0"] + q, -h * p["tk_medio"]
            h1 = -h * p["tk_0"] + q * (1 - x - q)
            log_1 = p["log_a1"] - h * p["tk_0"] + np.log(np.maximum(-np.expm1(-x), 1e-300))
            r1 = np.where(p["renuncio"], 1.0, np.where(p["sigue"], 0.0, _logistica(np.clip(log_1 - (p["log_a0"] - h * p["tk_medio"]), -700.0, 700.0))))
            g_v = r1 * g1 + (1 - r1) * g0
            h_v = r1 * (h1 + g1 ** 2) + (1 - r1) * (g0 + g0 ** 2) - g_v ** 2
            primera = -m + g_encuestas.sum(axis=2) - lam * g_v
            segunda = -1.0 + h_encuestas.sum(axis=2) + lam ** 2 * h_v
            segunda = np.where(segunda < -1e-6, segunda, -1.0)                          # sin máximo a la vista: la curvatura del prior
            m = m + np.clip(-primera / segunda, -1.5, 1.5)
        return m, np.clip(1.0 / np.sqrt(-segunda), 0.02, 1.0)

    def nodos_de_persona(p, m, s, nodos_z):
        """Gauss-Hermite centrada en (m, s) de cada persona: exp(−λ z) en sus nodos y el peso de cada nodo, (E, n, Kz) los dos."""
        puntos, pesos = np.polynomial.hermite.hermgauss(nodos_z)
        z = m[..., None] + np.sqrt(2.0) * s[..., None] * puntos
        log_w = log_persona(p, z) + np.log(pesos) + puntos ** 2
        # El peso va dividido por su máximo: la constante de cada persona no depende de u y se cancela.
        return np.exp(np.clip(-lam[..., None] * z, -300.0, 300.0)), np.exp(log_w - log_w.max(axis=2, keepdims=True))

    def nodos_del_prior(nodos_z):
        """Gauss-Hermite con los nodos del prior de z, los mismos para todas las personas: exp(−λ z) (E, Kz) y pesos (E, n, Kz).

        Es lo más barato: p(encuesta | z) se tabula por nivel de respuesta y cada persona solo busca los suyos. Alcanza para
        ubicar el posterior de un cargo (una suma sobre muchas personas), no para la probabilidad de una persona.
        """
        puntos, pesos = np.polynomial.hermite.hermgauss(nodos_z)
        z = np.sqrt(2.0) * puntos
        acumulada = 1.0 / (1.0 + np.exp(np.clip(th["a"][:, :, None, None] * z - th["cortes"][:, :, :, None], -300.0, 300.0)))   # (E, 4 ítems, 3 cortes, Kz)
        borde = np.ones_like(acumulada[:, :, :1])
        por_respuesta = np.concatenate([acumulada, borde], axis=2) - np.concatenate([0 * borde, acumulada], axis=2)                # (E, 4, 4 niveles, Kz)
        w = np.take_along_axis(por_respuesta[:, None], y[..., None], axis=3)[:, :, :, 0, :].prod(axis=2) * pesos                   # (E, n, Kz)
        return np.exp(np.clip(-lam * z, -300.0, 300.0)), w / w.max(axis=2, keepdims=True)

    def newton_u_con_el_prior(p, centro, e_z, w):
        """El mismo paso de Newton que `newton_u`, cuando los nodos de z son los del prior y todas las personas los comparten: e_z es (E, Kz).

        Con h = e^{base+u}·e_z, las sumas Σ_k h^j·e^{−hτ}·w que piden las derivadas son e^{j(base+u)} por un producto de matrices
        con las potencias de e_z: tres exponenciales y tres productos por paso, en vez de una veintena de pasadas por los nodos.
        """
        e_u = np.minimum(np.exp(np.minimum(p["base"] + np.take_along_axis(centro, p["grupo"], axis=1), 300.0)), 1e20 / e_z.max(axis=1, keepdims=True))
        sobre_el_minimo = e_u[..., None] * (e_z - e_z.min(axis=1, keepdims=True))[:, None, :]      # (E, n, Kz)
        h = e_u[..., None] * e_z[:, None, :]
        en_t = np.exp(-sobre_el_minimo * p["tk_0"][..., None]) * w
        potencias = np.stack([np.ones_like(e_z), e_z, e_z ** 2], axis=2)                 # (E, Kz, 3)
        de_t = en_t @ potencias                                                         # Σ_k e_z^j · e^{−h t^k} · w, j = 0, 1, 2: (E, n, 3)
        de_t1 = (en_t * np.exp(-h * p["salto"][..., None])) @ potencias
        de_medio = (np.exp(-sobre_el_minimo * p["tk_0"][..., None] - h * (p["tk_medio"] - p["tk_0"])[..., None]) * w) @ potencias
        con_1, con_0 = p["a1"] * ~p["sigue"], p["a0"] * ~p["renuncio"]
        h0, h1, hm = e_u * p["tk_0"], e_u * p["tk_1"], e_u * p["tk_medio"]
        ver = np.maximum(con_1 * (de_t[..., 0] - de_t1[..., 0]) + con_0 * de_medio[..., 0], 1e-300)
        primera = con_1 * (h1 * de_t1[..., 1] - h0 * de_t[..., 1]) - con_0 * hm * de_medio[..., 1]
        segunda = (con_1 * (h0 ** 2 * de_t[..., 2] - h0 * de_t[..., 1] - h1 ** 2 * de_t1[..., 2] + h1 * de_t1[..., 1])
                   + con_0 * (hm ** 2 * de_medio[..., 2] - hm * de_medio[..., 1]))
        g = primera / ver
        pendiente = por_cargo(g) - centro / sigma ** 2
        curvatura = por_cargo(segunda / ver - g ** 2) - 1.0 / sigma ** 2
        curvatura = np.where(curvatura < -1e-9, curvatura, -1.0 / sigma ** 2)
        return centro + np.clip(-pendiente / curvatura, -3.0, 3.0), np.minimum(1.0 / np.sqrt(-curvatura), sigma)

    def newton_u(p, centro, e_z, w):
        """Un paso de Newton hacia el máximo de log p(u | datos del cargo), con las integrales en z ya en sus nodos: nuevo centro y ancho, (E, G).

        Como h ∝ e^u, derivar respecto de u es derivar respecto de log h: de cada término e^{−hτ} salen −hτ·e^{−hτ} y (h²τ² − hτ)·e^{−hτ}.
        """
        e_u = np.exp(np.minimum(p["base"] + np.take_along_axis(centro, p["grupo"], axis=1), 300.0))[..., None]
        h = np.minimum(e_u * e_z, 1e20)                                                 # (E, n, Kz)
        sobre_el_minimo = h - h.min(axis=2, keepdims=True)
        x = h * p["salto"][..., None]
        en_t = np.exp(-sobre_el_minimo * p["tk_0"][..., None]) * w                      # e^{−h t^k}, sin el factor común de la persona
        en_t1 = en_t * np.exp(-x)
        en_medio = np.exp(-sobre_el_minimo * p["tk_0"][..., None] - h * (p["tk_medio"] - p["tk_0"])[..., None]) * w
        h0, h1, hm = h * p["tk_0"][..., None], h * p["tk_1"][..., None], h * p["tk_medio"][..., None]
        con_1, con_0 = p["a1"] * ~p["sigue"], p["a0"] * ~p["renuncio"]                  # quien está por decidir lleva los dos términos
        ver = con_1 * (en_t * -np.expm1(-x)).sum(axis=2) + con_0 * en_medio.sum(axis=2)
        primera = con_1 * (h1 * en_t1 - h0 * en_t).sum(axis=2) - con_0 * (hm * en_medio).sum(axis=2)
        segunda = con_1 * ((h0 ** 2 - h0) * en_t - (h1 ** 2 - h1) * en_t1).sum(axis=2) + con_0 * ((hm ** 2 - hm) * en_medio).sum(axis=2)
        ver = np.maximum(ver, 1e-300)
        g = primera / ver
        pendiente = por_cargo(g) - centro / sigma ** 2
        curvatura = por_cargo(segunda / ver - g ** 2) - 1.0 / sigma ** 2
        curvatura = np.where(curvatura < -1e-9, curvatura, -1.0 / sigma ** 2)
        return centro + np.clip(-pendiente / curvatura, -3.0, 3.0), np.minimum(1.0 / np.sqrt(-curvatura), sigma)

    def por_nivel(p, u, e_z, w):
        """En los nodos u (E, G, Ku) de cada cargo: log L_i(u) + cte de la persona y P(δ = 1 | t, encuestas, u), (E, n, Ku) los dos.

        Para no desbordar, de cada exponente se saca su máximo sobre los nodos de z (el del menor riesgo h) y se repone en el logaritmo.
        """
        e_u = np.exp(np.minimum(p["base"][..., None] + np.take_along_axis(u, p["grupo"][..., None], axis=1), 300.0))    # (E, n, Ku)
        e_z_minimo = e_z.min(axis=2, keepdims=True)
        h_minimo = e_u * e_z_minimo                                                     # (E, n, Ku)
        h = e_u[..., None] * e_z[:, :, None, :]                                         # (E, n, Ku, Kz)
        sobre_el_minimo = e_u[..., None] * (e_z - e_z_minimo)[:, :, None, :]
        s1 = np.einsum("enuk,enk->enu", np.exp(-sobre_el_minimo * p["tk_0"][..., None, None]) * -np.expm1(-h * p["salto"][..., None, None]), w)
        s0 = np.einsum("enuk,enk->enu", np.exp(-sobre_el_minimo * p["tk_medio"][..., None, None]), w)
        log_m1 = p["log_a1"][..., None] - h_minimo * p["tk_0"][..., None] + np.log(np.maximum(s1, 1e-300))
        log_m0 = p["log_a0"][..., None] - h_minimo * p["tk_medio"][..., None] + np.log(np.maximum(s0, 1e-300))
        log_ver = np.where(p["renuncio"][..., None], log_m1, np.where(p["sigue"][..., None], log_m0, np.logaddexp(log_m1, log_m0)))
        return log_ver, 1.0 / (1.0 + np.exp(np.minimum(log_m0 - log_m1, 700.0)))

    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        # 1. Ubicar el posterior de u en cada cargo con pasos de Newton, hasta que ningún centro se mueva. Con un θ compatible
        #    con los datos son dos o tres pasos; con uno absurdo el posterior queda lejos del prior y son más.
        centro = np.zeros((E, CARGOS_MAX))
        if rapido:
            en_z = nodos_del_prior(_NODOS_AL_UBICAR_RAPIDO)
        else:
            m, s = ubicar_z(todas, centro, np.zeros((E, n)), 3)
            en_z = nodos_de_persona(todas, m, s, _NODOS_AL_UBICAR)
        for _ in range(_PASOS_RAPIDO if rapido else pasos):
            anterior = centro
            centro, ancho = (newton_u_con_el_prior if rapido else newton_u)(todas, centro, *en_z)
            movimiento = np.abs(centro - anterior)
            if (movimiento < (_TOLERANCIA_RAPIDA if rapido else 0.1) * ancho).all():
                break
            if not rapido and movimiento.max() > 1.0:                                   # el cargo se movió: los nodos de persona también
                m, s = ubicar_z(todas, centro, m, 2)
                en_z = nodos_de_persona(todas, m, s, _NODOS_AL_UBICAR)
        puntos_u, pesos_u = np.polynomial.hermite.hermgauss(nodos)
        u = centro[..., None] + np.sqrt(2.0) * ancho[..., None] * puntos_u               # (E, G, Ku)
        por_decidir = np.isnan(evento)
        cuantas = por_decidir.sum(axis=1)
        if rapido and (cuantas == cuantas[0]).all():
            # 2 (cartera). Laplace en el cargo: p(u | datos) ≈ Normal(centro, ancho), así que los pesos son los de Gauss-Hermite.
            #    La integral se hace solo para las personas por decidir (las mismas por empresa: el 20%).
            cuales = np.argsort(~por_decidir, axis=1, kind="stable")[:, :cuantas[0]]     # (E, m)
            def de(v):
                return np.take_along_axis(v, cuales.reshape(cuales.shape + (1,) * (v.ndim - 2)), axis=1)
            ellas = {c: de(v) for c, v in todas.items()}
            _, dado_u = por_nivel(ellas, u, *nodos_de_persona(ellas, *ubicar_z(ellas, centro, np.zeros(cuales.shape), 3), nodos_persona))
            p = np.full((E, n), np.nan)
            np.put_along_axis(p, cuales, np.clip(dado_u @ (pesos_u / pesos_u.sum()), 0.0, 1.0), axis=1)
            return p
        # 2. Cuadratura de Gauss-Hermite centrada y escalada en ese posterior, con todos los nodos de persona.
        log_ver, dado_u = por_nivel(todas, u, *nodos_de_persona(todas, *ubicar_z(todas, centro, m, 1), nodos_persona))
        log_post = np.stack([por_cargo(log_ver[..., j]) for j in range(nodos)], axis=2) - 0.5 * (u / sigma[..., None]) ** 2
        log_peso = log_post + np.log(pesos_u) + puntos_u ** 2
        peso = np.exp(log_peso - log_peso.max(axis=2, keepdims=True))
        peso /= peso.sum(axis=2, keepdims=True)                                         # p(u_j | datos del cargo), (E, G, Ku)
        return np.clip((dado_u * np.take_along_axis(peso, d["grupo"][..., None], axis=1)).sum(axis=2), 0.0, 1.0)


_DATOS = ("x", "w", "encuestas", "tiempo", "evento", "grupo")


def paso_local(libre, datos: dict, nodos: int = NODOS_CARGO, nodos_persona: int = NODOS_PERSONA, pasos: int = 20) -> np.ndarray:
    """`muestras_p` de una empresa: P(ya renunció | años, covariables, encuestas, datos del cargo, θ_s). Devuelve (n, S).

    libre: muestras de θ sin restricciones, (S, 32). datos: `variables_del_modelo` de la empresa, con ejes (n, ...).
    El valor solo significa algo en las personas con el evento vacío; en las demás es P(δ = 1) como si no se supiera.
    Las muestras van por tandas para acotar la memoria (el servidor tiene 512 MB).
    """
    libre = np.atleast_2d(np.asarray(libre, dtype=np.float64))
    n = len(datos["tiempo"])
    tanda = max(1, _ELEMENTOS_POR_TANDA // (n * nodos * nodos_persona))
    salida = []
    for i in range(0, len(libre), tanda):
        th = a_restringido(libre[i:i + tanda])
        e = len(th["k"])
        d = {c: np.broadcast_to(np.asarray(datos[c]), (e,) + np.shape(datos[c])) for c in _DATOS}
        salida.append(_integrar(th, d, nodos, nodos_persona, pasos))
    return np.concatenate(salida, axis=0).T


def paso_local_por_empresa(libre, datos: dict, nodos: int = NODOS_CARGO, nodos_persona: int = NODOS_PERSONA, pasos: int = 20,
                           rapido: bool = False, elementos_por_tanda: int | None = None) -> np.ndarray:
    """Lo mismo para E empresas distintas de n personas, cada una con su θ: libre (E, 32), datos (E, n, ...) → (E, n).

    `datos` puede traer `base_w` ya calculada (sirve para todas las muestras de θ de las mismas empresas).
    rapido=True es el modo de la cartera (ver `_integrar`): devuelve NaN en las personas que no están por decidir.
    """
    libre = np.asarray(libre, dtype=np.float64)
    E, n = np.shape(datos["tiempo"])
    tanda = max(1, (elementos_por_tanda or _ELEMENTOS_POR_TANDA) // (n * nodos * nodos_persona))
    columnas = _DATOS + (("base_w",) if "base_w" in datos else ())
    return np.concatenate([_integrar(a_restringido(libre[i:i + tanda]), {c: np.asarray(datos[c])[i:i + tanda] for c in columnas},
                                     nodos, nodos_persona, pasos, rapido) for i in range(0, E, tanda)], axis=0)


# =========================================================================================
# La respuesta de un caso de rotación: analizar, cartera y nube
# =========================================================================================

NODOS_CARTERA = (4, 6)       # nodos de cargo y de persona en la cartera (WORKPLAN.md 11.6: menos nodos y 8 muestras)
# Tandas más grandes que en `analizar`: con arreglos grandes NumPy suelta el candado de Python por más tiempo y los hilos rinden
# (medido: 6,4 s de paso local con 1,5 millones contra 9,2 s con 300 mil). Son unos 25 MB por hilo en los lotes de 2.000 personas.
_ELEMENTOS_POR_TANDA_CARTERA = 1_500_000


def leer_caso(caso: dict) -> dict:
    """El archivo de un caso, o la tabla subida (D-34): columnas crudas (`columnas_crudas`), variables del modelo y filas del codificador.

    Con más de 2.000 filas se toma una muestra con semilla fija (contrato, sección 1); `elegidas` dice cuáles.
    Lanza `ArchivoNoCalza` si la tabla no calza con los papeles del modelo.
    """
    t = tabla_del_caso(caso)
    cruda = columnas_crudas(t, caso["columnas"])
    for nombre in caso["columnas"].get("extra") or []:           # las columnas `extra` no entran al modelo, pero la nube las mira
        tabla.columna(t, nombre)
    n = len(cruda["id"])
    elegidas = np.sort(np.random.default_rng(0).choice(n, size=PERSONAS_MAXIMO, replace=False)) if n > PERSONAS_MAXIMO else np.arange(n)
    cruda = {c: ([v[i] for i in elegidas] if c == "id" else v if c == "cargos" else v[elegidas]) for c, v in cruda.items()}
    variables = variables_del_modelo(cruda)
    filas = armar_filas(variables["x"], variables["w"], variables["encuestas"], variables["tiempo"], variables["evento"])
    return {**cruda, "variables": variables, "filas": filas, "elegidas": elegidas}


def factores_nube(cruda: dict, col: dict) -> dict[str, np.ndarray]:
    """Los factores con nombre de una empresa para los ejes de la nube: los tres efectos, el sueldo y las cuatro encuestas.

    La misma función sirve para el archivo del caso y para cada empresa simulada (`motor/supervivencia/nube.py`).
    """
    factores = {nombre: np.asarray(cruda["efectos"])[:, j] for j, nombre in enumerate(columnas_del_papel(col, "efectos"))}
    factores[columnas_del_papel(col, "suave")[0]] = np.asarray(cruda["sueldo"])
    factores.update({nombre: np.asarray(cruda["encuestas"])[:, j] for j, nombre in enumerate(columnas_del_papel(col, "encuestas"))})
    return factores


@cache
def _red(carpeta: str, _version: float):
    """La sesión de onnxruntime del codificador, los pesos del flujo y la huella del codificador (para saber si la nube es de esta red)."""
    import onnxruntime
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    ruta = f"{carpeta}/codificador.onnx"
    with open(ruta, "rb") as archivo:
        huella = hashlib.sha256(archivo.read()).hexdigest()
    return onnxruntime.InferenceSession(ruta, opciones, providers=["CPUExecutionProvider"]), flujo_numpy.cargar(f"{carpeta}/flujo.npz"), huella


def _red_exportada():
    carpeta = _casos.ARTEFACTOS / "supervivencia"
    if not (carpeta / "codificador.onnx").exists():
        raise ErrorKrylov("La red de rotación todavía no está exportada.", "no_disponible")
    return _red(str(carpeta), (carpeta / "codificador.onnx").stat().st_mtime)


def posterior(filas: np.ndarray, grupo: np.ndarray, impl: str, clave: str, muestras: int = tabla.MUESTRAS) -> np.ndarray:
    """Muestras del posterior de θ, (muestras, 32): del flujo condicionado en s(D) (`red`) o del MCMC precalculado (`mcmc`)."""
    if impl == "red":
        sesion, pesos, _ = _red_exportada()
        resumen = sesion.run(None, {"filas": filas[None], "grupo": grupo[None].astype(np.int64)})[0][0]
        return flujo_numpy.muestrear(pesos, resumen, flujo_numpy.ruido(0, muestras, DIM_THETA)).astype(np.float64)
    ruta = _casos.ARTEFACTOS / "supervivencia" / "mcmc" / f"{clave}.npz"
    if not ruta.exists():
        raise ErrorKrylov("Este análisis de rotación todavía no está precalculado.", "no_disponible")
    with np.load(ruta) as archivo:
        theta = archivo["theta"].astype(np.float64)
    return theta[np.sort(np.random.default_rng(0).choice(len(theta), size=min(muestras, len(theta)), replace=False))]


def _ubicar_en_la_nube(caso: dict, transformaciones: list[str], datos: dict) -> dict | None:
    """Dónde cae el archivo respecto del predictivo a priori (`nube.npz`): la respuesta de `nube` y el mejor factor. None si no hay nube.

    El segundo detector (distancia de Mahalanobis del resumen s(D)) solo corre si la nube se calculó con el
    codificador que está exportado ahora: `nube.npz` guarda su huella. Con otra red, esas distancias no significan nada.
    """
    from nucleo import nube as comun
    carpeta = _casos.ARTEFACTOS / "supervivencia"
    if not (carpeta / "nube.npz").exists():
        return None
    simulada = comun.cargar(carpeta / "nube.npz")
    if caso.get("tabla") is not None:                            # un archivo subido: la nube de empresas de su tamaño, si está generada
        n = len(datos["id"])
        del_tamano = [(abs(np.log(t / n)), carpeta / nube_del_tamano(t)) for t in TAMANOS_DE_NUBE if (carpeta / nube_del_tamano(t)).exists()]
        if del_tamano and min(del_tamano)[0] < abs(np.log(int(simulada.get("personas", 1470)) / n)):
            simulada = comun.cargar(min(del_tamano)[1])
    extra = {nombre: valores[datos["elegidas"]] for nombre, valores in comun.columnas_extra(caso, transformaciones).items()}
    x, y, mejor = comun.ejes_con_nombre({**factores_nube(datos, caso["columnas"]), **extra}, datos["evento"])
    resumen = None
    if (carpeta / "codificador.onnx").exists():
        sesion, _, huella = _red_exportada()
        if str(simulada.get("huella_codificador", "")) == huella:
            resumen = sesion.run(None, {"filas": datos["filas"][None], "grupo": datos["variables"]["grupo"][None].astype(np.int64)})[0][0]
    donde = comun.ubicar(simulada, x, y, mejor, resumen)
    if resumen is None:
        donde["detectores"]["resumenes_aprendidos"]["limite"] = None
    return {"nube": donde, "mejor_factor": mejor, "es_extra": mejor in extra}


def nube(caso: dict, transformaciones: list[str]) -> dict:
    """Dónde cae la empresa del caso respecto de las simulaciones con que practicó la red: ejes con nombre y resumen s(D)."""
    try:
        donde = _ubicar_en_la_nube(caso, transformaciones, leer_caso(caso))
    except ArchivoNoCalza as error:                              # una tabla subida que no calza no tiene dónde caer
        raise ErrorKrylov(error.motivo, "archivo_no_calza") from None
    if donde is None:
        raise ErrorKrylov("La nube de rotación todavía no está calculada.", "no_disponible")
    return {"caso": caso["nombre"], **donde["nube"]}


def _semaforo(caso: dict, transformaciones: list[str], donde: dict | None) -> dict:
    """El semáforo que sale de la nube. `rojo_modelo` si un detector marca; si lo que delata es una columna `extra`, propone quitarla.

    `KRYLOV_NUBE_SEGUNDO_DETECTOR=aviso` deja en amarillo (responde, con el motivo) cuando solo marca el detector de
    resúmenes aprendidos; por defecto es rojo, como dice el contrato.
    """
    from nucleo import textos
    if donde is None or donde["nube"]["archivo"]["dentro"]:
        corregido = any(t.removeprefix("quitar_factor:") in (caso["columnas"].get("extra") or []) for t in transformaciones)
        motivo = (textos.frase("semaforo.despues_de_corregir") or "") if corregido and donde is not None else ""
        return {"estado": "verde", "motivo": motivo, "propuesta": None}
    con_nombre = donde["nube"]["detectores"]["ejes_con_nombre"]
    if not con_nombre["dentro"] and donde["es_extra"]:
        columna = donde["mejor_factor"]
        return {"estado": "rojo_modelo", "motivo": textos.frase("semaforo.rojo_modelo.columna_delata", columna=columna) or con_nombre["motivo"],
                "propuesta": {"transformacion": f"quitar_factor:{columna}",
                              "texto": textos.frase("semaforo.propuesta.quitar_columna", columna=columna) or f"Quitar la columna «{columna}»."}}
    motivo = textos.frase("semaforo.rojo_modelo.no_se_parece") or con_nombre["motivo"]
    solo_el_segundo = con_nombre["dentro"]
    if solo_el_segundo and os.environ.get("KRYLOV_NUBE_SEGUNDO_DETECTOR", "rojo").strip().lower() == "aviso":
        return {"estado": "amarillo", "motivo": motivo, "propuesta": None}
    return {"estado": "rojo_modelo", "motivo": motivo, "propuesta": None}


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """A qué personas por decidir conviene retener: p de que ya haya renunciado por muestra del posterior, decisión, qué pesa y examen."""
    col = caso["columnas"]
    impl = implementacion("supervivencia")
    try:
        datos = leer_caso(caso)
    except ArchivoNoCalza as error:                              # un archivo subido que no calza con el modelo: rojo con su motivo
        return {"implementacion": impl, **tabla.rojo(caso, error)}
    nombres = nombres_por_papel(col)
    del_modelo = {c for papel in ("tiempo", "grupo", "suave", "efectos", "encuestas") for c in nombres[papel]}
    quitadas = {t.removeprefix("quitar_factor:") for t in transformaciones if t.startswith("quitar_factor:")}
    if quitadas & del_modelo:
        raise ErrorKrylov("Ese factor es parte del modelo de rotación y no se puede quitar.", "no_disponible")
    variables = datos["variables"]
    por_decidir = np.isnan(variables["evento"])
    conocidos = variables["evento"][~por_decidir]
    n = len(por_decidir)
    propio = {"implementacion": impl,
              "columnas": {"usadas": [*nombres["efectos"], *nombres["suave"], *nombres["grupo"], *nombres["encuestas"], *[e for e in col.get("extra") or [] if e not in quitadas]],
                           "disponibles": col.get("disponibles"), "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""}}
    if n < PERSONAS_MINIMO:
        return {**propio, **tabla.rojo_datos(caso, "pocas_filas", n=len(conocidos))}
    if conocidos.sum() < 10 or (1 - conocidos).sum() < 10:
        return {**propio, **tabla.rojo_datos(caso, "casi_ningun_si", k=int(conocidos.sum()), n=len(conocidos))}
    registro = [f"{int(por_decidir.sum())} {caso['unidad']['plural']} por decidir", f"{n} en el archivo", f"{len(datos['cargos'])} cargos"]

    semaforo = _semaforo(caso, transformaciones, _ubicar_en_la_nube(caso, transformaciones, datos))
    if semaforo["estado"] == "rojo_modelo":
        return {**propio, "unidades": None, "factores": None, "semaforo": semaforo, "registro": registro}

    clave = caso["nombre"] + "".join("__" + t.replace(":", "-") for t in transformaciones)
    theta = posterior(datos["filas"], variables["grupo"], impl, clave)
    muestras_p = paso_local(theta, variables)[por_decidir]
    ids = [i for i, falta in zip(datos["id"], por_decidir) if falta]

    etiquetas = caso.get("etiquetas", {})
    def fila(nombre, muestras):
        return decision.factor(nombre, etiquetas.get(nombre, nombre), muestras)
    # Todo en la escala del riesgo (η): cada efecto por una desviación estándar de su columna; el sueldo, de una desviación bajo
    # el promedio a una sobre el promedio, s(1) − s(−1), con el posterior del spline; el compromiso entra con −λ.
    contraste = base_spline(1.0) - base_spline(-1.0)
    factores = ([fila(nombre, theta[:, I_BETA][:, j]) for j, nombre in enumerate(nombres["efectos"])]
                + [fila(nombres["suave"][0], theta[:, I_GAMMA] @ contraste), fila("compromiso", -theta[:, I_LAMBDA])])
    return {**propio, "unidades": tabla.unidades(ids, muestras_p, costos), "factores": sorted(factores, key=lambda f: -abs(f["efecto"])),
            "semaforo": semaforo, "examen": tabla.examen(caso, ids, muestras_p.mean(axis=1)),
            "registro": registro + [f"{len(theta)} versiones creíbles"]}


def empresas_de_la_cartera(n_empresas: int):
    """Las empresas simuladas de la cartera, lote por lote y siempre las mismas (semilla fija): cada lote es la salida de `simular`.

    Salen del generador paramétrico de covariables (WORKPLAN.md 11.6). Las usan la cartera con la red y la que se
    precalcula con el MCMC (`motor/supervivencia/cartera_mcmc.py`), así una empresa tiene el mismo nombre en las dos.
    """
    import importlib

    from nucleo import cartera as comun
    simular = importlib.import_module("motor.supervivencia.simular")         # el simulador es NumPy puro
    config = simular.cargar_config()
    rng = np.random.default_rng(2026)
    for b in comun.tamanos_de_lote(n_empresas):
        yield simular.simular(rng, b, simular.muestrear_n(rng, config), config)


def cartera(caso: dict) -> dict:
    """Mil empresas simuladas con el modelo generativo, analizadas en lote con la red (ver `nucleo/cartera.py`).

    Cada lote de 50 empresas comparte tamaño y pasa de una vez por el codificador y por el flujo. El paso local
    necesita a todas las personas de cada cargo (las que ya tienen respuesta ubican el efecto del cargo), pero solo
    se devuelven las probabilidades de las personas por decidir. Cada muestra de θ de cada lote es una tarea de un
    grupo de hilos, y el hilo principal sigue simulando y resumiendo los lotes siguientes mientras tanto.
    """
    from concurrent.futures import ThreadPoolExecutor

    from nucleo import cartera as comun

    def analizar_lotes(n_empresas: int, muestras: int):
        sesion, pesos, _ = _red_exportada()
        ruido = flujo_numpy.ruido(0, muestras, DIM_THETA)
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as hilos:
            pendientes = []
            for lote in empresas_de_la_cartera(n_empresas):
                b = len(lote["theta"])
                resumen = sesion.run(None, {"filas": lote["filas"], "grupo": lote["grupo"]})[0]
                theta = flujo_numpy.muestrear(pesos, resumen[None], np.broadcast_to(ruido[:, None, :], (muestras, b, DIM_THETA))).astype(np.float64)
                variables = variables_del_modelo(lote)
                variables["base_w"] = base_spline(variables["w"])            # no depende de θ: una vez por lote
                tareas = [hilos.submit(paso_local_por_empresa, th, variables, *NODOS_CARTERA, rapido=True, elementos_por_tanda=_ELEMENTOS_POR_TANDA_CARTERA) for th in theta]
                pendientes.append((np.isnan(lote["evento"]), tareas))
            for i, (falta, tareas) in enumerate(pendientes):
                p = np.stack([t.result() for t in tareas], axis=-1)          # (b, n, muestras)
                yield i, [p[e][falta[e]] for e in range(len(falta))]

    return comun.responder(caso, analizar_lotes)
