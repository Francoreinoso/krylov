"""Motor `jerarquico` (inasistencias): regresión logística jerárquica con dos niveles de efectos aleatorios.

Modelo generativo (WORKPLAN.md, 11.3). Para la cita c del paciente i en el barrio b:

    logit P(no llega) = α + f(espera) + κ·1[mismo día] + d_día + (ρ0 + ρ1·(t − 2,5))·SMS + x_i·β + v_i + u_b
    v_i ~ Normal(0, σ_v)     propensión latente del paciente, común a todas sus citas
    u_b ~ Normal(0, σ_b)     efecto del barrio

con t = log(1 + días de espera) y f un B-spline cúbico en t con f(0) = 0.

**Dos ajustes de parametrización** respecto del texto del plan, sin cambiar el modelo:
- El primer coeficiente del spline se fija en 0. La base B-spline suma 1, así que con seis
  coeficientes libres y un intercepto α habría una dirección no identificada. Con f(0) = 0,
  α es el nivel de una cita que no es del mismo día y κ el salto de «mismo día».
- Los otros cinco coeficientes son una caminata: γ_m = γ_{m−1} + incremento (prior de suavidad
  con escala fija), y las dos dispersiones van en logaritmo. Así θ son 20 números sin
  restricciones con prior normal independiente, que comparten el simulador y el MCMC.

Todo lo fijo es lineal: η = Z·coef, con Z la **matriz de diseño** de la cita. `matriz_de_diseno`
es el único preprocesamiento del motor: la usan el simulador, el servicio y el MCMC.

**Paso local exacto.** Dado θ, lo que falta saber de una cita por decidir son u_b y v_i, de una
dimensión cada uno: se integran con cuadratura de Gauss-Hermite anidada (barrio → paciente),
condicionando en las respuestas conocidas de ese paciente y de ese barrio.

Solo NumPy: este módulo corre en el servidor.
"""

from __future__ import annotations

import numpy as np

T_MAXIMO = float(np.log1p(180.0))              # la espera se recorta a 180 días
NUDOS = np.array([0, 0, 0, 0, T_MAXIMO / 3, 2 * T_MAXIMO / 3, T_MAXIMO, T_MAXIMO, T_MAXIMO, T_MAXIMO])
T_CENTRO = 2.5                                 # ρ0 es el efecto del SMS con unos 11 días de espera
EDAD_CENTRO, EDAD_ESCALA = 38.0, 23.0
NOMBRES_COEF = (["alfa"] + [f"gamma_{m}" for m in range(2, 7)] + ["kappa"] + [f"dia_{d}" for d in ("martes", "miercoles", "jueves", "viernes")]
                + ["rho_0", "rho_1"] + [f"beta_{j}" for j in range(1, 6)])
NOMBRES_THETA = (["alfa"] + [f"inc_gamma_{m}" for m in range(2, 7)] + NOMBRES_COEF[6:] + ["log_sigma_v", "log_sigma_b"])
DIM_COEF, DIM_THETA = len(NOMBRES_COEF), len(NOMBRES_THETA)          # 18 y 20
DIM_FILA = DIM_COEF - 1 + 2                                           # 19: Z sin la constante, respuesta y marca


def base_spline(t) -> np.ndarray:
    """Base B-spline cúbica de 6 funciones en t ∈ [0, T_MAXIMO] (Cox–de Boor). Devuelve (..., 6); cada fila suma 1."""
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, T_MAXIMO - 1e-9)[..., None]
    k = NUDOS
    base = ((t >= k[:-1]) & (t < k[1:])).astype(np.float64)
    for p in range(1, 4):
        d1, d2 = k[p:-1] - k[: -p - 1], k[p + 1:] - k[1:-p]
        izquierda = np.where(d1 > 0, (t - k[: -p - 1]) / np.where(d1 > 0, d1, 1.0), 0.0)
        derecha = np.where(d2 > 0, (k[p + 1:] - t) / np.where(d2 > 0, d2, 1.0), 0.0)
        base = izquierda * base[..., :-1] + derecha * base[..., 1:]
    return base


def matriz_de_diseno(espera, dia, sms, edad, binarias) -> np.ndarray:
    """La matriz de diseño Z de cada cita, (..., 18): η = Z·coef. El único preprocesamiento de `jerarquico`.

    espera: días entre agendar y la cita. dia: 0 = lunes … 4 = viernes. sms: 0/1. edad: años.
    binarias: (..., 4) beca, hipertensión, diabetes, alcoholismo. Acepta cualquier forma delantera.
    Columnas, en el orden de NOMBRES_COEF: constante · spline de la espera sin su primera función (5) ·
    mismo día · día de la semana, lunes de base (4) · SMS · SMS × (t − 2,5) · edad estandarizada · binarias (4).
    """
    espera = np.clip(np.asarray(espera, dtype=np.float64), 0.0, 180.0)
    t = np.log1p(espera)
    sms = np.asarray(sms, dtype=np.float64)
    return np.concatenate([
        np.ones_like(t)[..., None], base_spline(t)[..., 1:], (espera == 0).astype(np.float64)[..., None],
        (np.asarray(dia)[..., None] == np.arange(1, 5)).astype(np.float64),
        sms[..., None], (sms * (t - T_CENTRO))[..., None],
        ((np.asarray(edad, dtype=np.float64) - EDAD_CENTRO) / EDAD_ESCALA)[..., None], np.asarray(binarias, dtype=np.float64),
    ], axis=-1)


def armar_filas(z, respuesta) -> np.ndarray:
    """La fila de cada cita para el codificador, (..., 19): Z sin la constante, la respuesta (0 si falta) y la marca «por decidir»."""
    respuesta = np.asarray(respuesta, dtype=np.float64)
    por_decidir = np.isnan(respuesta)
    return np.concatenate([np.asarray(z)[..., 1:], np.where(por_decidir, 0.0, respuesta)[..., None],
                           por_decidir.astype(np.float64)[..., None]], axis=-1).astype(np.float32)


def a_restringido(libre, xp=np) -> dict:
    """De θ sin restricciones (..., 20) a `coef` (..., 18), `sigma_v` y `sigma_b`."""
    coef = xp.concatenate([libre[..., 0:1], xp.cumsum(libre[..., 1:6], axis=-1), libre[..., 6:18]], axis=-1)
    return {"coef": coef, "sigma_v": xp.exp(libre[..., 18]), "sigma_b": xp.exp(libre[..., 19])}


def anidar(filas: np.ndarray, barrio: np.ndarray, paciente: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """De filas sueltas a la forma anidada que lee el codificador jerárquico. Solo datos reales.

    filas: (n, F). barrio, paciente: (n,) índices enteros (cada paciente pertenece a un solo barrio).
    Devuelve (tensor (G, P, C, F), máscara (G, P, C), posición (n, 3) de cada fila): barrios × pacientes del
    barrio × citas del paciente, con relleno en cero donde no hay cita.
    """
    barrios, g = np.unique(barrio, return_inverse=True)
    posicion = np.zeros((len(filas), 3), dtype=int)
    posicion[:, 0] = g
    for b in range(len(barrios)):
        del_barrio = np.flatnonzero(g == b)
        _, p = np.unique(paciente[del_barrio], return_inverse=True)
        posicion[del_barrio, 1] = p
        for q in range(p.max() + 1):
            posicion[del_barrio[p == q], 2] = np.arange((p == q).sum())
    forma = tuple(posicion.max(axis=0) + 1)
    tensor, mascara = np.zeros(forma + (filas.shape[1],), dtype=np.float32), np.zeros(forma, dtype=np.float32)
    tensor[tuple(posicion.T)] = filas
    mascara[tuple(posicion.T)] = 1.0
    return tensor, mascara, posicion


# ------------------------------------------------------------------------------ paso local: cuadratura anidada

def _log_logistica(x):
    return -np.logaddexp(0.0, -x)


def paso_local(libre, z, respuesta, paciente, barrio_del_paciente, nodos: int = 12) -> np.ndarray:
    """P(no llega) de cada cita, integrando u_b y v_i dado lo observado: cuadratura de Gauss-Hermite anidada.

    libre: muestras de θ sin restricciones, (S, 20). z: matriz de diseño (n, 18). respuesta: (n,) con 1, 0 o NaN.
    paciente: (n,) índice del paciente de cada cita, en 0..P−1. barrio_del_paciente: (P,) índice del barrio, en 0..G−1.
    Devuelve (n, S): para cada cita y cada muestra de θ,

        p = ∫∫ logistic(η + v + u) · p(v, u | respuestas conocidas del paciente y del barrio, θ) dv du

    El condicional se arma por niveles: la verosimilitud del paciente L_i(u) integra v; la del barrio es el
    producto de las L_i(u) de sus pacientes. Para una cita con respuesta conocida, su propia respuesta también
    condiciona (sirve para comprobar; lo que se decide son las citas con NaN).
    """
    libre = np.atleast_2d(np.asarray(libre, dtype=np.float64))
    th = a_restringido(libre)
    respuesta = np.asarray(respuesta, dtype=np.float64)
    conocida = ~np.isnan(respuesta)
    signo = np.where(conocida, 2 * np.nan_to_num(respuesta) - 1, 0.0)            # +1 no llegó, −1 llegó, 0 sin respuesta
    puntos, pesos = np.polynomial.hermite.hermgauss(nodos)
    log_pesos = np.log(pesos / np.sqrt(np.pi))
    n_pacientes, n_barrios = len(barrio_del_paciente), int(np.max(barrio_del_paciente)) + 1
    eta = z @ th["coef"].T                                                        # (n, S)
    salida = np.empty_like(eta)
    for s in range(libre.shape[0]):
        u = np.sqrt(2.0) * th["sigma_b"][s] * puntos                              # nodos del barrio
        v = np.sqrt(2.0) * th["sigma_v"][s] * puntos                              # nodos del paciente
        logit = eta[:, s, None, None] + u[None, :, None] + v[None, None, :]       # (n, Ku, Kv)
        log_ver_cita = np.where(conocida[:, None, None], _log_logistica(signo[:, None, None] * logit), 0.0)
        log_ver_paciente = np.zeros((n_pacientes, nodos, nodos))
        np.add.at(log_ver_paciente, paciente, log_ver_cita)                       # producto sobre las citas del paciente
        log_ver_paciente += log_pesos[None, None, :]
        tope = log_ver_paciente.max(axis=2, keepdims=True)
        log_l = tope[..., 0] + np.log(np.exp(log_ver_paciente - tope).sum(axis=2))   # log L_i(u): (P, Ku)
        # Predicción de la cita dado u: E_v[logistic(η + u + v) | respuestas del paciente].
        dado_u = (np.exp(_log_logistica(logit) + log_ver_paciente[paciente] - tope[paciente]).sum(axis=2)
                  / np.exp(log_l[paciente] - tope[paciente][..., 0]))                # (n, Ku)
        log_ver_barrio = np.zeros((n_barrios, nodos))
        np.add.at(log_ver_barrio, barrio_del_paciente, log_l)                     # producto sobre los pacientes del barrio
        log_ver_barrio += log_pesos[None, :]
        peso_u = np.exp(log_ver_barrio - log_ver_barrio.max(axis=1, keepdims=True))
        peso_u /= peso_u.sum(axis=1, keepdims=True)                               # p(u_j | datos del barrio)
        salida[:, s] = (dado_u * peso_u[barrio_del_paciente[paciente]]).sum(axis=1)
    return salida
