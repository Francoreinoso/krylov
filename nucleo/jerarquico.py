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


def paso_local(libre, z, respuesta, paciente, barrio_del_paciente, nodos: int = 8, nodos_paciente: int = 20) -> np.ndarray:
    """P(no llega) de cada cita, integrando u_b y v_i dado lo observado: cuadratura de Gauss-Hermite anidada.

    libre: muestras de θ sin restricciones, (S, 20). z: matriz de diseño (n, 18). respuesta: (n,) con 1, 0 o NaN.
    paciente: (n,) índice del paciente de cada cita, en 0..P−1. barrio_del_paciente: (P,) índice del barrio, en 0..G−1.
    Devuelve (n, S): para cada cita y cada muestra de θ,

        p = ∫∫ logistic(η + v + u) · p(v, u | respuestas conocidas del paciente y del barrio, θ) dv du

    El condicional se arma por niveles: la verosimilitud del paciente L_i(u) integra v; la del barrio es el
    producto de las L_i(u) de sus pacientes.

    - **Paciente:** nodos de Gauss-Hermite del prior Normal(0, σ_v). Un paciente tiene pocas citas y su
      posterior se parece al prior.
    - **Barrio: cuadratura adaptativa.** Un barrio junta decenas de pacientes y el posterior de u_b queda
      mucho más angosto que el prior: con los nodos del prior caería entre dos nodos. Primero se ubica el
      posterior de cada barrio (una grilla gruesa y una parábola por su máximo en escala logarítmica) y
      después los nodos se centran y se escalan ahí.
    """
    libre = np.atleast_2d(np.asarray(libre, dtype=np.float64))
    th = a_restringido(libre)
    respuesta = np.asarray(respuesta, dtype=np.float64)
    conocida = ~np.isnan(respuesta)
    signo = np.where(conocida, 2 * np.nan_to_num(respuesta) - 1, 0.0)            # +1 no llegó, −1 llegó, 0 sin respuesta
    barrio = np.asarray(barrio_del_paciente)[paciente]                            # barrio de cada cita
    n_pacientes, n_barrios = len(barrio_del_paciente), int(np.max(barrio_del_paciente)) + 1
    eta = z @ th["coef"].T                                                        # (n, S)

    def gauss_hermite(k):
        puntos, pesos = np.polynomial.hermite.hermgauss(k)
        return puntos, pesos
    puntos_v, pesos_v = gauss_hermite(nodos_paciente)
    puntos_v8, pesos_v8 = gauss_hermite(8)
    puntos_u, pesos_u = gauss_hermite(nodos)
    grilla = np.linspace(-4.0, 4.0, 9)                                            # en unidades de σ_b

    def por_nivel(eta_s, u, v, log_pesos_v, con_prediccion):
        """Para nodos u (G, Ku) propios de cada barrio y v (Kv,): log L_i(u) (P, Ku) y, si se pide, E_v[p | u] (n, Ku)."""
        logit = eta_s[:, None, None] + u[barrio][:, :, None] + v[None, None, :]   # (n, Ku, Kv)
        log_ver_cita = np.where(conocida[:, None, None], _log_logistica(signo[:, None, None] * logit), 0.0)
        log_ver_paciente = np.zeros((n_pacientes, u.shape[1], len(v)))
        np.add.at(log_ver_paciente, paciente, log_ver_cita)                       # producto sobre las citas del paciente
        log_ver_paciente += log_pesos_v
        tope = log_ver_paciente.max(axis=2, keepdims=True)
        suma = np.exp(log_ver_paciente - tope).sum(axis=2)
        log_l = tope[..., 0] + np.log(suma)                                       # log L_i(u)
        if not con_prediccion:
            return log_l, None
        dado_u = np.exp(_log_logistica(logit) + (log_ver_paciente - tope)[paciente]).sum(axis=2) / suma[paciente]
        return log_l, dado_u

    def log_posterior_barrio(log_l, u, sigma_b):
        """log p(u | datos del barrio) + constante, en los nodos u (G, Ku)."""
        total = np.zeros((n_barrios, u.shape[1]))
        np.add.at(total, barrio_del_paciente, log_l)                              # producto sobre los pacientes del barrio
        return total - 0.5 * (u / sigma_b) ** 2

    salida = np.empty_like(eta)
    filas = np.arange(n_barrios)
    for s in range(libre.shape[0]):
        sigma_v, sigma_b = th["sigma_v"][s], th["sigma_b"][s]
        # 1. Ubicar el posterior de u en cada barrio: grilla gruesa y parábola por el máximo del logaritmo.
        u0 = np.broadcast_to(grilla * sigma_b, (n_barrios, len(grilla)))
        log_l, _ = por_nivel(eta[:, s], u0, np.sqrt(2.0) * sigma_v * puntos_v8, np.log(pesos_v8), False)
        lp = log_posterior_barrio(log_l, u0, sigma_b)
        m = np.clip(lp.argmax(axis=1), 1, len(grilla) - 2)
        paso = (grilla[1] - grilla[0]) * sigma_b
        curvatura = (lp[filas, m - 1] - 2 * lp[filas, m] + lp[filas, m + 1]) / paso ** 2
        con_maximo = curvatura < -1e-9
        centro = np.where(con_maximo, u0[filas, m] - (lp[filas, m + 1] - lp[filas, m - 1]) / (2 * paso * np.where(con_maximo, curvatura, -1.0)), 0.0)
        ancho = np.where(con_maximo, 1.0 / np.sqrt(np.where(con_maximo, -curvatura, 1.0)), sigma_b)
        centro, ancho = np.clip(centro, -5 * sigma_b, 5 * sigma_b), np.clip(ancho, 1e-3 * sigma_b, sigma_b)
        # 2. Cuadratura de Gauss-Hermite centrada y escalada en ese posterior.
        u = centro[:, None] + np.sqrt(2.0) * ancho[:, None] * puntos_u[None, :]   # (G, Ku)
        log_l, dado_u = por_nivel(eta[:, s], u, np.sqrt(2.0) * sigma_v * puntos_v, np.log(pesos_v), True)
        log_peso = log_posterior_barrio(log_l, u, sigma_b) + np.log(pesos_u) + puntos_u ** 2
        peso = np.exp(log_peso - log_peso.max(axis=1, keepdims=True))
        peso /= peso.sum(axis=1, keepdims=True)                                   # p(u_j | datos del barrio), por barrio
        salida[:, s] = (dado_u * peso[barrio]).sum(axis=1)
    return salida


# =========================================================================================
# La respuesta de un caso de inasistencias
# =========================================================================================

from nucleo.casos import leer_columnas          # noqa: E402

from nucleo.tabla import si_no                  # noqa: E402


def leer_caso(caso: dict) -> dict:
    """El archivo de un caso por columnas del modelo, con pacientes y barrios como índices.

    Devuelve `espera`, `dia`, `sms`, `edad`, `binarias` (n, 4), `respuesta` (1 = no llegó, NaN = por decidir), `id`,
    `paciente` (n,) en 0..P−1, `barrio` (n,) y `barrio_del_paciente` (P,) en 0..G−1.
    """
    col, t = caso["columnas"], leer_columnas(caso["dataset"])
    def numeros(nombre):
        return np.array([float(v) for v in t[nombre]])
    _, paciente = np.unique(np.array(t[col["paciente"]]), return_inverse=True)
    _, barrio = np.unique(np.array(t[col["grupo"]]), return_inverse=True)
    barrio_del_paciente = np.zeros(paciente.max() + 1, dtype=int)
    barrio_del_paciente[paciente] = barrio
    efectos = col["efectos"]
    return {"espera": numeros(col["suave"]), "dia": numeros(col["categoria"]).astype(int), "sms": numeros(col["tratamiento"]),
            "edad": numeros(efectos[0]), "binarias": np.stack([numeros(e) for e in efectos[1:]], axis=1),
            "respuesta": np.array([si_no(v) for v in t[col["objetivo"]]]),
            "id": t[col["id"]], "paciente": paciente, "barrio": barrio, "barrio_del_paciente": barrio_del_paciente}


from functools import cache                                   # noqa: E402

from nucleo import casos as _casos, decision, flujo as flujo_numpy, tabla   # noqa: E402
from nucleo.casos import ErrorKrylov, implementacion          # noqa: E402


@cache
def _red(carpeta: str, _version: float):
    import onnxruntime
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    return (onnxruntime.InferenceSession(f"{carpeta}/codificador.onnx", opciones, providers=["CPUExecutionProvider"]),
            flujo_numpy.cargar(f"{carpeta}/flujo.npz"))


def posterior(z, datos: dict, impl: str, clave: str, muestras: int = tabla.MUESTRAS) -> np.ndarray:
    """Muestras del posterior de θ, (muestras, 20): del flujo condicionado en s(D) (`red`) o del MCMC precalculado (`mcmc`)."""
    carpeta = _casos.ARTEFACTOS / "jerarquico"
    if impl == "red":
        if not (carpeta / "codificador.onnx").exists():
            raise ErrorKrylov("La red de inasistencias todavía no está exportada.", "no_disponible")
        sesion, pesos = _red(str(carpeta), (carpeta / "codificador.onnx").stat().st_mtime)
        tensor, mascara, _ = anidar(armar_filas(z, datos["respuesta"]), datos["barrio"], datos["paciente"])
        resumen = sesion.run(None, {"filas": tensor[None], "mascara": mascara[None]})[0][0]
        return flujo_numpy.muestrear(pesos, resumen, flujo_numpy.ruido(0, muestras, DIM_THETA)).astype(np.float64)
    ruta = carpeta / "mcmc" / f"{clave}.npz"
    if not ruta.exists():
        raise ErrorKrylov("Este análisis de inasistencias todavía no está precalculado.", "no_disponible")
    with np.load(ruta) as archivo:
        theta = archivo["theta"].astype(np.float64)
    return theta[np.sort(np.random.default_rng(0).choice(len(theta), size=min(muestras, len(theta)), replace=False))]


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """Qué citas por decidir conviene confirmar: p de no llegar por muestra del posterior, decisión, qué pesa y examen."""
    col = caso["columnas"]
    del_modelo = {col["suave"], col["categoria"], col["tratamiento"], *col["efectos"]}
    for t in transformaciones:
        if t.removeprefix("quitar_factor:") in del_modelo:
            raise ErrorKrylov("Ese factor es parte del modelo de inasistencias y no se puede quitar.", "no_disponible")
    impl = implementacion("jerarquico")
    datos = leer_caso(caso)
    por_decidir = np.isnan(datos["respuesta"])
    conocidas = datos["respuesta"][~por_decidir]
    n = len(por_decidir)
    if n < 200:
        return {"implementacion": impl, **tabla.rojo_datos(f"Hay {n} citas y hacen falta al menos 200.")}
    if conocidas.sum() < 10 or (1 - conocidas).sum() < 10:
        return {"implementacion": impl, **tabla.rojo_datos("Casi todas las citas tienen la misma respuesta: no hay de dónde aprender.")}

    z = matriz_de_diseno(datos["espera"], datos["dia"], datos["sms"], datos["edad"], datos["binarias"])
    clave = caso["nombre"] + "".join("__" + t.replace(":", "-") for t in transformaciones)
    theta = posterior(z, datos, impl, clave)
    muestras_p = paso_local(theta, z, datos["respuesta"], datos["paciente"], datos["barrio_del_paciente"])[por_decidir]
    ids = [i for i, falta in zip(datos["id"], por_decidir) if falta]

    th = a_restringido(theta)
    etiquetas = caso.get("etiquetas", {})
    def fila(nombre, muestras):
        return decision.factor(nombre, etiquetas.get(nombre, nombre), muestras)
    # Espera: el riesgo a 30 días de espera contra 1 día, f(log 31) − f(log 2), con el posterior del spline.
    contraste = (base_spline(np.log1p(30.0)) - base_spline(np.log1p(1.0)))[1:]
    factores = ([fila(col["suave"], th["coef"][:, 1:6] @ contraste), fila(col["tratamiento"], th["coef"][:, 11])]
                + [fila(nombre, th["coef"][:, 13 + j]) for j, nombre in enumerate(col["efectos"])])
    return {
        "implementacion": impl, "unidades": tabla.unidades(ids, muestras_p, costos),
        "factores": sorted(factores, key=lambda f: -abs(f["efecto"])),
        "columnas": {"usadas": [col["suave"], col["categoria"], col["tratamiento"], *col["efectos"]],
                     "disponibles": col.get("disponibles"), "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "examen": tabla.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{int(por_decidir.sum())} {caso['unidad']['plural']} por decidir", f"{len(datos['barrio_del_paciente'])} pacientes",
                     f"{int(datos['barrio'].max()) + 1} barrios", f"{len(theta)} versiones creíbles"],
    }
