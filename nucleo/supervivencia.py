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


def _integrar(th: dict, d: dict, nodos: int, nodos_persona: int, pasos: int) -> np.ndarray:
    """El paso local con un eje delantero E en θ y en los datos. Devuelve P(δ = 1 | lo observado, θ), (E, n).

    th: θ con restricciones, cada parámetro con eje delantero E. d: `x` (E, n, 3), `w`, `tiempo`, `evento`, `grupo` (E, n)
    y `encuestas` (E, n, 4). Con una empresa y E muestras de θ, los datos se repiten; en la cartera, E empresas distintas.
    """
    E, n = d["tiempo"].shape
    k, lam, sigma = th["k"][:, None], th["lambda"][:, None], th["sigma_u"][:, None]
    base = th["beta0"][:, None] + np.einsum("enj,ej->en", d["x"], th["beta"]) + np.einsum("enm,em->en", base_spline(d["w"]), th["gamma"])
    t, evento, grupo = d["tiempo"], d["evento"], d["grupo"][..., None]
    renuncio, sigue = evento == 1, evento == 0
    tk_0, tk_medio, tk_1 = ((t + mas) ** k for mas in (0.0, 0.5, 1.0))                  # t^k, (t+½)^k, (t+1)^k
    salto = tk_1 - tk_0
    # La censura solo depende de los años, que son enteros: se tabula por valor distinto de t.
    anos, cual = np.unique(t, return_inverse=True)
    def s_c(mas):
        return np.take_along_axis(supervivencia_censura(anos[None, :] + mas, th["mu_c"][:, None], th["s_c"][:, None]), cual.reshape(E, n), axis=1)
    log_a1, log_a0 = np.log(np.maximum(s_c(0.5), 1e-300)), np.log(np.maximum(s_c(0.0) - s_c(1.0), 1e-300))
    pertenece = (grupo == np.arange(CARGOS_MAX)).astype(np.float64)                   # (E, n, G)
    # Los dos cortes que encierran la respuesta de cada persona a cada encuesta: P(y) = logistic(c_alto − a z) − logistic(c_bajo − a z).
    # Con e = exp(a z) esa resta es (1 − ρ)·e / [(1 + κ e)(e + ν)], con κ = exp(−c_alto), ν = exp(c_bajo) y ρ = κ ν:
    # una exponencial por encuesta, sin restar números parecidos, y con los cortes ±∞ de los extremos dando κ = 0 o ν = 0.
    infinito = np.full((E, N_ENCUESTAS, 1), np.inf)
    cortes = np.concatenate([-infinito, th["cortes"], infinito], axis=2)[:, None]      # (E, 1, 4, 5)
    y = d["encuestas"][..., None] - 1                                                  # (E, n, 4, 1)
    kappa, nu = np.exp(-np.take_along_axis(cortes, y + 1, axis=3)), np.exp(np.take_along_axis(cortes, y, axis=3))    # (E, n, 4, 1)
    uno_menos_rho = 1.0 - kappa * nu
    a_item = th["a"][:, None, :, None]                                                  # (E, 1, 4, 1)
    a1, a0 = np.exp(log_a1), np.exp(log_a0)

    def log_persona(z):
        """log[φ(z) · p(las cuatro encuestas | z)] en los nodos z de cada persona: (E, n, K)."""
        e = np.exp(np.clip(a_item * z[:, :, None, :], -300.0, 300.0))                   # (E, n, 4, K)
        p = (uno_menos_rho * e / ((1.0 + kappa * e) * (e + nu))).prod(axis=2)
        return -0.5 * z ** 2 - _LOG_2PI_MEDIO + np.log(np.maximum(p, 1e-300))

    def ubicar_z(centro_u, m, vueltas):
        """Dónde vive el integrando en z de cada persona, con u en el centro de su cargo: máximo y ancho, (E, n).

        Newton sobre F(z) = log φ(z) + Σ log P(encuesta | z) + log p(años y evento | u, z). Con v = log h = cte − λ z,
        las derivadas del último término respecto de v son: si sigue, −h(t+½)^k las dos; si renunció,
        −h t^k + q y −h t^k + q(1 − x − q), con x = h·[(t+1)^k − t^k] y q = x / (e^x − 1); si falta, la mezcla de las dos.
        """
        log_h_u = base + np.take_along_axis(centro_u, grupo[..., 0], axis=1)
        for _ in range(vueltas):
            e = np.exp(np.clip(a_item[..., 0] * m[..., None], -300.0, 300.0))            # (E, n, 4)
            alto, bajo = 1.0 / (1.0 + kappa[..., 0] * e), nu[..., 0] / (e + nu[..., 0])  # las dos logísticas
            d_bajo, d_alto = bajo * (1 - bajo), alto * (1 - alto)
            p = np.maximum(uno_menos_rho[..., 0] * e * alto / (e + nu[..., 0]), 1e-300)
            g_encuestas = -a_item[..., 0] * (d_alto - d_bajo) / p
            h_encuestas = a_item[..., 0] ** 2 * (d_alto * (1 - 2 * alto) - d_bajo * (1 - 2 * bajo)) / p - g_encuestas ** 2
            h = np.exp(np.clip(log_h_u - lam * m, -700.0, 46.0))
            x = np.maximum(h * salto, 1e-12)
            q = x / np.expm1(x)
            g1, g0 = -h * tk_0 + q, -h * tk_medio
            h1 = -h * tk_0 + q * (1 - x - q)
            log_1 = log_a1 - h * tk_0 + np.log(np.maximum(-np.expm1(-x), 1e-300))
            r1 = np.where(renuncio, 1.0, np.where(sigue, 0.0, _logistica(np.clip(log_1 - (log_a0 - h * tk_medio), -700.0, 700.0))))
            g_v = r1 * g1 + (1 - r1) * g0
            h_v = r1 * (h1 + g1 ** 2) + (1 - r1) * (g0 + g0 ** 2) - g_v ** 2
            primera = -m + g_encuestas.sum(axis=2) - lam * g_v
            segunda = -1.0 + h_encuestas.sum(axis=2) + lam ** 2 * h_v
            segunda = np.where(segunda < -1e-6, segunda, -1.0)                          # sin máximo a la vista: la curvatura del prior
            m = m + np.clip(-primera / segunda, -1.5, 1.5)
        return m, np.clip(1.0 / np.sqrt(-segunda), 0.02, 1.0)

    def newton_u(centro, e_z, w):
        """Un paso de Newton hacia el máximo de log p(u | datos del cargo), con las integrales en z ya en sus nodos: nuevo centro y ancho, (E, G).

        Como h ∝ e^u, derivar respecto de u es derivar respecto de log h: de cada término e^{−hτ} salen −hτ·e^{−hτ} y (h²τ² − hτ)·e^{−hτ}.
        """
        e_u = np.exp(np.minimum(base + np.take_along_axis(centro, grupo[..., 0], axis=1), 300.0))[..., None]
        h = np.minimum(e_u * e_z, 1e20)                                                 # (E, n, Kz)
        sobre_el_minimo = h - h.min(axis=2, keepdims=True)
        x = h * salto[..., None]
        en_t = np.exp(-sobre_el_minimo * tk_0[..., None]) * w                           # e^{−h t^k}, sin el factor común de la persona
        en_t1 = en_t * np.exp(-x)
        en_medio = np.exp(-sobre_el_minimo * tk_0[..., None] - h * (tk_medio - tk_0)[..., None]) * w
        h0, h1, hm = h * tk_0[..., None], h * tk_1[..., None], h * tk_medio[..., None]
        con_1, con_0 = a1 * ~sigue, a0 * ~renuncio                                      # quien está por decidir lleva los dos términos
        ver = con_1 * (en_t * -np.expm1(-x)).sum(axis=2) + con_0 * en_medio.sum(axis=2)
        primera = con_1 * (h1 * en_t1 - h0 * en_t).sum(axis=2) - con_0 * (hm * en_medio).sum(axis=2)
        segunda = con_1 * ((h0 ** 2 - h0) * en_t - (h1 ** 2 - h1) * en_t1).sum(axis=2) + con_0 * ((hm ** 2 - hm) * en_medio).sum(axis=2)
        ver = np.maximum(ver, 1e-300)
        g = primera / ver
        pendiente = np.einsum("eng,en->eg", pertenece, g) - centro / sigma ** 2
        curvatura = np.einsum("eng,en->eg", pertenece, segunda / ver - g ** 2) - 1.0 / sigma ** 2
        curvatura = np.where(curvatura < -1e-9, curvatura, -1.0 / sigma ** 2)
        return centro + np.clip(-pendiente / curvatura, -3.0, 3.0), np.minimum(1.0 / np.sqrt(-curvatura), sigma)

    def nodos_de_persona(m, s, nodos_z):
        """Gauss-Hermite centrada en (m, s) de cada persona: exp(−λ z) en sus nodos y el peso de cada nodo, (E, n, Kz) los dos."""
        puntos, pesos = np.polynomial.hermite.hermgauss(nodos_z)
        z = m[..., None] + np.sqrt(2.0) * s[..., None] * puntos
        log_w = log_persona(z) + np.log(pesos) + puntos ** 2
        # El peso va dividido por su máximo: la constante de cada persona no depende de u y se cancela.
        return np.exp(np.clip(-lam[..., None] * z, -300.0, 300.0)), np.exp(log_w - log_w.max(axis=2, keepdims=True))

    def por_nivel(u, e_z, w):
        """En los nodos u (E, G, Ku) de cada cargo: log p(u | datos del cargo) + cte (E, G, Ku) y P(δ = 1 | t, encuestas, u) (E, n, Ku).

        Para no desbordar, de cada exponente se saca su máximo sobre los nodos de z (el del menor riesgo h) y se repone en el logaritmo.
        """
        e_u = np.exp(np.minimum(base[..., None] + np.take_along_axis(u, grupo, axis=1), 300.0))    # (E, n, Ku)
        e_z_minimo = e_z.min(axis=2, keepdims=True)
        h_minimo = e_u * e_z_minimo                                                     # (E, n, Ku)
        h = e_u[..., None] * e_z[:, :, None, :]                                         # (E, n, Ku, Kz)
        sobre_el_minimo = e_u[..., None] * (e_z - e_z_minimo)[:, :, None, :]
        s1 = np.einsum("enuk,enk->enu", np.exp(-sobre_el_minimo * tk_0[..., None, None]) * -np.expm1(-h * salto[..., None, None]), w)
        s0 = np.einsum("enuk,enk->enu", np.exp(-sobre_el_minimo * tk_medio[..., None, None]), w)
        log_m1 = log_a1[..., None] - h_minimo * tk_0[..., None] + np.log(np.maximum(s1, 1e-300))
        log_m0 = log_a0[..., None] - h_minimo * tk_medio[..., None] + np.log(np.maximum(s0, 1e-300))
        log_ver = np.where(renuncio[..., None], log_m1, np.where(sigue[..., None], log_m0, np.logaddexp(log_m1, log_m0)))
        log_post = np.einsum("eng,enu->egu", pertenece, log_ver) - 0.5 * (u / sigma[..., None]) ** 2
        return log_post, 1.0 / (1.0 + np.exp(np.minimum(log_m0 - log_m1, 700.0)))

    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        # 1. Ubicar el posterior de u en cada cargo con pasos de Newton, hasta que ningún centro se mueva. Con un θ compatible
        #    con los datos son dos o tres pasos; con uno absurdo el posterior queda lejos del prior y son más.
        centro = np.zeros((E, CARGOS_MAX))
        m, s = ubicar_z(centro, np.zeros((E, n)), 3)
        en_z = nodos_de_persona(m, s, _NODOS_AL_UBICAR)
        for _ in range(pasos):
            anterior = centro
            centro, ancho = newton_u(centro, *en_z)
            movimiento = np.abs(centro - anterior)
            if (movimiento < 0.1 * ancho).all():
                break
            if movimiento.max() > 1.0:                                                  # el cargo se movió: los nodos de persona también
                m, s = ubicar_z(centro, m, 2)
                en_z = nodos_de_persona(m, s, _NODOS_AL_UBICAR)
        # 2. Cuadratura de Gauss-Hermite centrada y escalada en ese posterior, con todos los nodos de persona.
        m, s = ubicar_z(centro, m, 1)
        puntos_u, pesos_u = np.polynomial.hermite.hermgauss(nodos)
        u = centro[..., None] + np.sqrt(2.0) * ancho[..., None] * puntos_u
        log_post, dado_u = por_nivel(u, *nodos_de_persona(m, s, nodos_persona))
        log_peso = log_post + np.log(pesos_u) + puntos_u ** 2
        peso = np.exp(log_peso - log_peso.max(axis=2, keepdims=True))
        peso /= peso.sum(axis=2, keepdims=True)                                         # p(u_j | datos del cargo), (E, G, Ku)
        return np.clip((dado_u * np.take_along_axis(peso, grupo, axis=1)).sum(axis=2), 0.0, 1.0)


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


def paso_local_por_empresa(libre, datos: dict, nodos: int = NODOS_CARGO, nodos_persona: int = NODOS_PERSONA, pasos: int = 20) -> np.ndarray:
    """Lo mismo para E empresas distintas de n personas, cada una con su θ: libre (E, 32), datos (E, n, ...) → (E, n)."""
    libre = np.asarray(libre, dtype=np.float64)
    E, n = np.shape(datos["tiempo"])
    tanda = max(1, _ELEMENTOS_POR_TANDA // (n * nodos * nodos_persona))
    return np.concatenate([_integrar(a_restringido(libre[i:i + tanda]), {c: np.asarray(datos[c])[i:i + tanda] for c in _DATOS},
                                     nodos, nodos_persona, pasos) for i in range(0, E, tanda)], axis=0)
