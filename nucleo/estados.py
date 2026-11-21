"""Motor `estados` (crédito): cadena de estados ocultos por cliente, y su paso local exacto (filtro forward).

Modelo generativo (WORKPLAN.md, 11.4). Cada cliente pasa mes a mes por tres estados que
no se ven: 1 al día, 2 apretado, 3 en problemas. Los seis meses de atraso, uso del cupo y
pago son emisiones de ese estado, y el impago del mes siguiente depende del estado del mes 7.

    s_1 ~ Categorical(π)
    P(s_{t+1} = k | s_t = j, x_i) = softmax_k( A_jk + (k − j)·x_i·ψ ),   A_jj = 0
    atraso_t | s_t = k:  logit ordenado,  P(nivel ≤ l) = logistic(c_l − m_k),  m_1 = 0 < m_2 < m_3
    uso_t    | s_t = k:  Normal(μu_k, σu_k)
    pago_t   | s_t = k:  cero con probabilidad q_k; si no, log(pago/cupo) ~ Normal(μp_k, σp)
    impago   | s_7 = k:  Bernoulli(d_k),  d_1 < d_2 < d_3

El intercambio de estados se rompe en el prior: m y d van ordenados por construcción.

**Ajuste que impusieron los datos:** el archivo real no registra el código de atraso 1 en
los cinco meses más antiguos (0%) y sí en el más reciente (12%). Por eso los códigos 1 y 2
van juntos en un nivel, y el atraso tiene 5 niveles: −2, −1, 0, 1 o 2, 3 o más. Con eso θ
tiene 33 parámetros libres (el plan contaba 35 con seis niveles).

**Paso local exacto.** Dado θ, la cadena de cada cliente se integra con el filtro forward:
p_i = Σ_k P(s_i7 = k | historial, θ)·d_k. Las funciones de verosimilitud reciben el módulo
de arreglos (`xp`): con NumPy las usa el servicio; con `jax.numpy`, el MCMC de referencia
(`motor/estados/mcmc.py`). Es una sola implementación de la verosimilitud.

Solo NumPy: este módulo corre en el servidor.
"""

from __future__ import annotations

import numpy as np

ESTADOS, MESES, NIVELES = 3, 6, 5
DIM_FILA = MESES * (NIVELES + 3) + 3 + 2          # 53: historial aplanado + covariables + respuesta y marca
NOMBRES_THETA = (
    ["logit_pi_2", "logit_pi_3"] + [f"A_{j}{k}" for j in (1, 2, 3) for k in (1, 2, 3) if j != k]
    + ["psi_cupo", "psi_edad", "psi_educacion", "log_inc_m_2", "log_inc_m_3", "corte_1"]
    + [f"log_inc_corte_{l}" for l in (2, 3, 4)] + [f"mu_uso_{k}" for k in (1, 2, 3)] + [f"log_sigma_uso_{k}" for k in (1, 2, 3)]
    + [f"logit_q_{k}" for k in (1, 2, 3)] + [f"mu_pago_{k}" for k in (1, 2, 3)] + ["log_sigma_pago", "logit_d_1", "log_inc_d_2", "log_inc_d_3"]
)
DIM_THETA = len(NOMBRES_THETA)                    # 33
_FUERA_DE_DIAGONAL = [(j, k) for j in range(3) for k in range(3) if j != k]
CENTRO_PAGO, ESCALA_PAGO = -3.8, 1.3              # para llevar log(pago/cupo) a una escala cómoda para la red


# ------------------------------------------------------------------------------ θ libre → θ con restricciones

def a_restringido(libre, xp=np) -> dict:
    """De θ en espacio sin restricciones (..., 33) a los parámetros del modelo, cada uno con ejes delanteros (...)."""
    cero = xp.zeros_like(libre[..., :1])
    logits_pi = xp.concatenate([cero, libre[..., 0:2]], axis=-1)
    pi = xp.exp(logits_pi - _logsumexp(logits_pi, -1, xp)[..., None])
    a = libre[..., 2:8]
    # Matriz A con ceros en la diagonal: filas = estado de salida, columnas = estado de llegada.
    filas = [xp.stack([cero[..., 0] if j == k else a[..., _FUERA_DE_DIAGONAL.index((j, k))] for k in range(3)], axis=-1) for j in range(3)]
    m_2 = xp.exp(libre[..., 11])
    posicion = xp.stack([cero[..., 0], m_2, m_2 + xp.exp(libre[..., 12])], axis=-1)
    cortes = xp.cumsum(xp.concatenate([libre[..., 13:14], xp.exp(libre[..., 14:17])], axis=-1), axis=-1)
    logit_d = xp.cumsum(xp.concatenate([libre[..., 30:31], xp.exp(libre[..., 31:33])], axis=-1), axis=-1)
    return {
        "pi": pi, "A": xp.stack(filas, axis=-2), "psi": libre[..., 8:11], "posicion": posicion, "cortes": cortes,
        "mu_uso": libre[..., 17:20], "sigma_uso": xp.exp(libre[..., 20:23]), "q": _logistica(libre[..., 23:26], xp),
        "mu_pago": libre[..., 26:29], "sigma_pago": xp.exp(libre[..., 29]), "d": _logistica(logit_d, xp),
    }


def _logistica(x, xp=np):
    return 1.0 / (1.0 + xp.exp(-x))


def _logsumexp(x, eje, xp=np):
    maximo = xp.max(x, axis=eje, keepdims=True)
    return xp.squeeze(maximo, axis=eje) + xp.log(xp.sum(xp.exp(x - maximo), axis=eje))


# ------------------------------------------------------------------------------ preprocesamiento (uno solo)

def variables_del_modelo(atraso_codigo, saldo, pago, cupo, covariables) -> dict:
    """De las columnas crudas del archivo a las variables del modelo. Solo datos reales.

    atraso_codigo: (n, 6) códigos −2 a 8, del mes más antiguo al más reciente. saldo, pago: (n, 6). cupo: (n,).
    covariables: (n, 3) cupo, edad y educación crudos; el cupo va en logaritmo y las tres se estandarizan.
    """
    codigo = np.asarray(atraso_codigo, dtype=np.float64)
    nivel = np.where(codigo <= 0, np.clip(codigo, -2, 0) + 2, np.where(codigo <= 2, 3, 4)).astype(int)
    cupo = np.asarray(cupo, dtype=np.float64)[:, None]
    pago = np.asarray(pago, dtype=np.float64)
    x = np.asarray(covariables, dtype=np.float64).copy()
    x[:, 0] = np.log(x[:, 0])
    x = (x - x.mean(axis=0)) / np.maximum(x.std(axis=0), 1e-9)
    return {"nivel": nivel, "uso": np.clip(np.asarray(saldo, dtype=np.float64) / cupo, -0.2, 1.5),
            "pago_cero": pago <= 0, "log_pago": np.where(pago > 0, np.log(np.maximum(pago, 1e-9) / cupo), 0.0), "x": x}


def armar_filas(nivel, uso, pago_cero, log_pago, x, impago) -> np.ndarray:
    """Una fila de 53 números por cliente: su historial aplanado, listo para el codificador de conjuntos.

    Es el único preprocesamiento de `estados`: lo llaman el simulador (lote de datasets, ejes delanteros) y el servicio.
    Columnas: nivel de atraso en uno-de-cinco por mes (30) · uso (6) · pago cero (6) · log del pago centrado (6) ·
    covariables (3) · impago observado (cero si está por decidir) · marca «por decidir».
    `impago` trae 1, 0 o NaN (vacío: el cliente está por decidir).
    """
    impago = np.asarray(impago, dtype=np.float64)
    por_decidir = np.isnan(impago)
    uno_de_cinco = (np.asarray(nivel)[..., None] == np.arange(NIVELES)).astype(np.float64)
    pago_cero = np.asarray(pago_cero, dtype=bool)
    return np.concatenate([
        uno_de_cinco.reshape(uno_de_cinco.shape[:-2] + (MESES * NIVELES,)),
        np.asarray(uso, dtype=np.float64), pago_cero.astype(np.float64),
        np.where(pago_cero, 0.0, (np.asarray(log_pago, dtype=np.float64) - CENTRO_PAGO) / ESCALA_PAGO),
        np.asarray(x, dtype=np.float64), np.where(por_decidir, 0.0, impago)[..., None], por_decidir.astype(np.float64)[..., None],
    ], axis=-1).astype(np.float32)


# ------------------------------------------------------------------------------ verosimilitud y filtro forward

def log_emision(th: dict, nivel, uso, pago_cero, log_pago, xp=np):
    """log p(emisiones del mes | estado), para cada cliente, mes y estado: (..., n, 6, 3).

    Los parámetros de `th` traen ejes delanteros (...) (las muestras de θ); los datos, (n, 6).
    """
    def por_estado(v):                    # (..., 3) → (..., 1, 1, 3): se alinea con (n, 6, estado)
        return v[..., None, None, :]
    # Atraso: logit ordenado. P(nivel ≤ l | k) = logistic(c_l − m_k); se agregan −∞ y +∞ en los extremos.
    cortes = th["cortes"][..., None, None, None, :] - th["posicion"][..., None, None, :, None]      # (..., 1, 1, 3, 4)
    acumulada = _logistica(cortes, xp)
    unos, ceros = xp.ones_like(acumulada[..., :1]), xp.zeros_like(acumulada[..., :1])
    por_nivel = xp.concatenate([acumulada, unos], axis=-1) - xp.concatenate([ceros, acumulada], axis=-1)   # (..., 1, 1, 3, 5)
    elegido = (xp.asarray(nivel)[..., None, None] == xp.arange(NIVELES))                                  # (n, 6, 1, 5)
    log_atraso = xp.log(xp.sum(por_nivel * elegido, axis=-1) + 1e-300)

    sigma_u = por_estado(th["sigma_uso"])
    log_uso = -0.5 * ((xp.asarray(uso)[..., None] - por_estado(th["mu_uso"])) / sigma_u) ** 2 - xp.log(sigma_u) - 0.9189385332046727

    q, sigma_p = por_estado(th["q"]), th["sigma_pago"][..., None, None, None]
    log_pago_no_cero = (xp.log1p(-q) - 0.5 * ((xp.asarray(log_pago)[..., None] - por_estado(th["mu_pago"])) / sigma_p) ** 2
                        - xp.log(sigma_p) - 0.9189385332046727)
    log_del_pago = xp.where(xp.asarray(pago_cero)[..., None], xp.log(q), log_pago_no_cero)
    return log_atraso + log_uso + log_del_pago


def transiciones(th: dict, x, xp=np):
    """Matriz de transición de cada cliente, (..., n, 3, 3): filas = estado de este mes, columnas = el del siguiente."""
    efecto = xp.sum(xp.asarray(x) * th["psi"][..., None, :], axis=-1)                       # (..., n): x_i·ψ
    salto = xp.arange(ESTADOS)[None, :] - xp.arange(ESTADOS)[:, None]                         # (k − j)
    logits = th["A"][..., None, :, :] + salto * efecto[..., None, None]
    return xp.exp(logits - _logsumexp(logits, -1, xp)[..., None])


def filtro_forward(libre, datos: dict, xp=np):
    """Filtro forward de la cadena oculta, marginalizando los estados de los seis meses.

    libre: θ sin restricciones, (..., 33). datos: `nivel`, `uso`, `pago_cero`, `log_pago` (n, 6) y `x` (n, 3).
    Devuelve (log_verosimilitud del historial (..., n), P(s_7 = k | historial) (..., n, 3), p de impago (..., n)).
    En cada mes se normaliza y se acumula el logaritmo de la constante: no hay desbordes con seis meses ni con sesenta.
    """
    th = a_restringido(libre, xp)
    emision = xp.exp(log_emision(th, datos["nivel"], datos["uso"], datos["pago_cero"], datos["log_pago"], xp))   # (..., n, 6, 3)
    paso = transiciones(th, datos["x"], xp)                                                                       # (..., n, 3, 3)
    alfa = th["pi"][..., None, :] * emision[..., 0, :]
    constante = xp.sum(alfa, axis=-1)
    log_ver, alfa = xp.log(constante), alfa / constante[..., None]
    for t in range(1, MESES):
        alfa = xp.sum(alfa[..., :, None] * paso, axis=-2) * emision[..., t, :]
        constante = xp.sum(alfa, axis=-1)
        log_ver, alfa = log_ver + xp.log(constante), alfa / constante[..., None]
    estado_7 = xp.sum(alfa[..., :, None] * paso, axis=-2)                 # un paso más, sin emisión: el mes siguiente
    return log_ver, estado_7, xp.sum(estado_7 * th["d"][..., None, :], axis=-1)


def log_verosimilitud(libre, datos: dict, impago, xp=np):
    """log p(dataset | θ): el historial de cada cliente y, donde se conoce, su impago del mes siguiente. (...,)"""
    log_ver, _, p = filtro_forward(libre, datos, xp)
    impago = xp.asarray(impago)
    conocido = ~xp.isnan(impago)
    y = xp.where(conocido, impago, 0.0)
    del_impago = xp.where(conocido, y * xp.log(p + 1e-300) + (1 - y) * xp.log1p(-p + 1e-300), 0.0)
    return xp.sum(log_ver + del_impago, axis=-1)


def probabilidad_de_impago(libre, datos: dict) -> np.ndarray:
    """`muestras_p`: P(impago el mes siguiente | historial, θ_s) por cliente y por muestra del posterior. (n, S)"""
    return np.moveaxis(filtro_forward(np.atleast_2d(np.asarray(libre, dtype=np.float64)), datos)[2], 0, -1)


# =========================================================================================
# La respuesta de un caso de crédito
# =========================================================================================

from functools import cache                                   # noqa: E402

from nucleo import casos as _casos, decision, flujo as flujo_numpy, tabla   # noqa: E402
from nucleo.casos import ErrorKrylov, implementacion, leer_columnas          # noqa: E402

VARIABLES = ("nivel", "uso", "pago_cero", "log_pago", "x")


def leer_caso(caso: dict) -> dict:
    """Las variables del modelo del archivo de un caso, más `impago` (NaN = por decidir) e `id`."""
    col, t = caso["columnas"], leer_columnas(caso["dataset"])
    def numeros(nombres):
        return np.array([[float(v) for v in t[n]] for n in nombres]).T
    datos = variables_del_modelo(numeros(col["atraso"]), numeros(col["saldo"]), numeros(col["pago"]),
                                 numeros([col["cupo"]])[:, 0], numeros(col["transiciones"]))
    datos["impago"] = np.array([float(v) if v != "" else np.nan for v in t[col["objetivo"]]])
    datos["id"] = t[col["id"]]
    return datos


@cache
def _red(carpeta: str, _version: float):
    import onnxruntime
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    return (onnxruntime.InferenceSession(f"{carpeta}/codificador.onnx", opciones, providers=["CPUExecutionProvider"]),
            flujo_numpy.cargar(f"{carpeta}/flujo.npz"))


def posterior(filas: np.ndarray, impl: str, clave: str, muestras: int = tabla.MUESTRAS) -> np.ndarray:
    """Muestras del posterior de θ, (muestras, 33): del flujo condicionado en s(D) (`red`) o del MCMC precalculado (`mcmc`)."""
    carpeta = _casos.ARTEFACTOS / "estados"
    if impl == "red":
        if not (carpeta / "codificador.onnx").exists():
            raise ErrorKrylov("La red de crédito todavía no está exportada.", "no_disponible")
        sesion, pesos = _red(str(carpeta), (carpeta / "codificador.onnx").stat().st_mtime)
        resumen = sesion.run(None, {"x": filas[None], "mascara": np.ones((1, len(filas)), dtype=np.float32)})[0][0]
        return flujo_numpy.muestrear(pesos, resumen, flujo_numpy.ruido(0, muestras, DIM_THETA)).astype(np.float64)
    ruta = carpeta / "mcmc" / f"{clave}.npz"
    if not ruta.exists():
        raise ErrorKrylov("Este análisis de crédito todavía no está precalculado.", "no_disponible")
    with np.load(ruta) as z:
        theta = z["theta"].astype(np.float64)
    return theta[np.sort(np.random.default_rng(0).choice(len(theta), size=min(muestras, len(theta)), replace=False))]


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """A qué clientes por decidir conviene no aprobar: p de impago por muestra del posterior, decisión, qué pesa y examen."""
    col = caso["columnas"]
    del_modelo = set(col["atraso"]) | set(col["saldo"]) | set(col["pago"]) | set(col["transiciones"]) | {col["cupo"]}
    for t in transformaciones:
        if t.removeprefix("quitar_factor:") in del_modelo:
            raise ErrorKrylov("Ese factor es parte del modelo de crédito y no se puede quitar.", "no_disponible")
    impl = implementacion("estados")
    datos = leer_caso(caso)
    por_decidir = np.isnan(datos["impago"])
    conocidos = datos["impago"][~por_decidir]
    n = len(datos["impago"])
    if n < 200:
        return {"implementacion": impl, **tabla.rojo_datos(f"Hay {n} clientes y hacen falta al menos 200.")}
    if conocidos.sum() < 10 or (1 - conocidos).sum() < 10:
        return {"implementacion": impl, **tabla.rojo_datos("Casi todos los clientes tienen la misma respuesta: no hay de dónde aprender.")}
    if n > 2000:                                            # el contrato: con más filas, una muestra con semilla fija
        elegidos = np.sort(np.random.default_rng(0).choice(n, size=2000, replace=False))
        datos = {k: (np.asarray(v)[elegidos] if k != "id" else [v[i] for i in elegidos]) for k, v in datos.items()}
        por_decidir = np.isnan(datos["impago"])

    filas = armar_filas(*(datos[k] for k in VARIABLES), datos["impago"])
    clave = caso["nombre"] + "".join("__" + t.replace(":", "-") for t in transformaciones)
    theta = posterior(filas, impl, clave)
    muestras_p = probabilidad_de_impago(theta, {k: datos[k][por_decidir] for k in VARIABLES})
    ids = [i for i, falta in zip(datos["id"], por_decidir) if falta]
    lista = tabla.unidades(ids, muestras_p, costos)

    etiquetas = caso.get("etiquetas", {})
    psi = theta[:, 8:11]                                    # efecto de cada covariable sobre empeorar de estado
    factores = [decision.factor(nombre, etiquetas.get(nombre, nombre), psi[:, j]) for j, nombre in enumerate(col["transiciones"])]
    return {
        "implementacion": impl, "unidades": lista,
        "factores": sorted(factores, key=lambda f: -abs(f["efecto"])),
        "columnas": {"usadas": list(col["atraso"]) + list(col["saldo"]) + list(col["pago"]) + list(col["transiciones"]),
                     "disponibles": col.get("disponibles"), "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "examen": tabla.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{int(por_decidir.sum())} {caso['unidad']['plural']} por decidir", f"{len(por_decidir)} en el archivo",
                     f"{len(theta)} versiones creíbles"],
    }
