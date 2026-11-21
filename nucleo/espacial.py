"""Motor `espacial` en el servicio: el paso local exacto (kriging dado θ) y la respuesta del terreno.

Modelo (WORKPLAN.md, 11.5), en las unidades estandarizadas de `nucleo.preproceso`:

    y(s) = β0 + β1·√dist(s) + w(s),   w ~ proceso gaussiano de media 0 y covarianza σ²·exp(−h)
    z_j  = y(s_j) + ε_j,              ε_j ~ Normal(0, τ²)

con h la distancia anisotrópica entre bloques. θ = (log a, e1, e2, log σ, log τ, β0, β1),
donde e = log r·(cos 2φ, sin 2φ) junta la razón de anisotropía r y la dirección φ, y el
alcance es a·√r a lo largo de φ y a/√r en la perpendicular (en bloques).

**Kriging dado θ.** Con θ fijo, el predictivo de y(s) dadas las mediciones es gaussiano y
tiene forma cerrada. El posterior de θ llega como muestras (del flujo o del MCMC de
referencia) y el predictivo del mapa es la mezcla de esos gaussianos, bloque por bloque.

Solo NumPy: este módulo corre en el servidor.
"""

from __future__ import annotations

import math

import numpy as np

NOMBRES_THETA = ("log_alcance", "anis_1", "anis_2", "log_sigma", "log_tau", "beta0", "beta1")


def metrica_anisotropica(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Coeficientes (m11, m12, m22) de h² = m11·dx² + 2·m12·dx·dy + m22·dy² (dx en columnas, dy en filas).

    Es R(φ)·diag(1/(a²r), r/a²)·R(φ)ᵀ escrito con e: M = [cosh ρ·I − (sinh ρ/ρ)·(e1·σz + e2·σx)] / a², ρ = |e|.
    La misma fórmula que `motor.espacial.simular.metrica_anisotropica`; una prueba las compara.
    """
    theta = np.asarray(theta, dtype=np.float64)
    a2 = np.exp(2 * theta[..., 0])
    e1, e2 = theta[..., 1], theta[..., 2]
    rho = np.maximum(np.sqrt(e1 ** 2 + e2 ** 2), 1e-6)
    cosh, sinhc = np.cosh(rho), np.sinh(rho) / rho
    return (cosh - sinhc * e1) / a2, (-sinhc * e2) / a2, (cosh + sinhc * e1) / a2


def correlacion(theta: np.ndarray, d_fila: np.ndarray, d_columna: np.ndarray) -> np.ndarray:
    """exp(−h) para desfases (d_fila, d_columna) en bloques. theta: (S, 7) → (S, *desfases)."""
    extra = (slice(None),) + (None,) * np.ndim(d_fila)
    m11, m12, m22 = (m[extra] for m in metrica_anisotropica(np.atleast_2d(theta)))
    h2 = m11 * d_columna ** 2 + 2 * m12 * d_columna * d_fila + m22 * d_fila ** 2
    return np.exp(-np.sqrt(np.maximum(h2, 0.0)))


def kriging(theta, fila_obs, columna_obs, z_obs, raiz_obs, fila_pred, columna_pred, raiz_pred, cuenta_obs=None):
    """Predictivo gaussiano de y en `pred` dadas las mediciones `obs`, para cada muestra de θ.

    theta: (S, 7). Las posiciones son (fila, columna) en bloques; `raiz_*` es √dist ahí.
    `cuenta_obs`: mediciones promediadas en cada bloque medido (su ruido es τ²/cuenta); por defecto 1.
    Devuelve (media, varianza), cada una (S, n_pred). Es el kriging con tendencia conocida:
        media    = t_pred + K_po·(K_oo + τ²/c)⁻¹·(z − t_obs)
        varianza = σ² − diag(K_po·(K_oo + τ²/c)⁻¹·K_op)
    """
    theta = np.atleast_2d(np.asarray(theta, dtype=np.float64))
    fila_obs, columna_obs = np.asarray(fila_obs, dtype=np.float64), np.asarray(columna_obs, dtype=np.float64)
    fila_pred, columna_pred = np.asarray(fila_pred, dtype=np.float64), np.asarray(columna_pred, dtype=np.float64)
    sigma2, tau2 = np.exp(2 * theta[:, 3])[:, None, None], np.exp(2 * theta[:, 4])[:, None]
    beta0, beta1 = theta[:, 5, None], theta[:, 6, None]
    cuenta = np.ones(len(fila_obs)) if cuenta_obs is None else np.asarray(cuenta_obs, dtype=np.float64)

    k_oo = sigma2 * correlacion(theta, fila_obs[:, None] - fila_obs[None, :], columna_obs[:, None] - columna_obs[None, :])
    k_oo = k_oo + (tau2 / cuenta)[:, :, None] * np.eye(len(fila_obs))
    k_po = sigma2 * correlacion(theta, fila_pred[:, None] - fila_obs[None, :], columna_pred[:, None] - columna_obs[None, :])
    residuo = np.asarray(z_obs, dtype=np.float64)[None, :] - (beta0 + beta1 * np.asarray(raiz_obs)[None, :])
    pesos = np.linalg.solve(k_oo, np.swapaxes(k_po, 1, 2))                     # (S, n_obs, n_pred)
    media = beta0 + beta1 * np.asarray(raiz_pred)[None, :] + np.einsum("so,sop->sp", residuo, pesos)
    varianza = sigma2[:, 0] - np.einsum("spo,sop->sp", k_po, pesos)
    return media, np.maximum(varianza, 1e-12)


def _normal_acumulada(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


def mezclar(media: np.ndarray, varianza: np.ndarray, umbral: float) -> dict[str, np.ndarray]:
    """Mezcla sobre las muestras de θ: media y desviación del predictivo, y P(y > umbral), por bloque."""
    media_total = media.mean(axis=0)
    desviacion = np.sqrt(varianza.mean(axis=0) + media.var(axis=0))
    p = _normal_acumulada((media - umbral) / np.sqrt(varianza)).mean(axis=0)
    return {"media": media_total, "desviacion": desviacion, "p": p}


# =========================================================================================
# La respuesta del terreno: de un caso espacial al mapa, «qué manda», el examen y «¿Dónde mido?»
# =========================================================================================

from functools import cache                                           # noqa: E402

from nucleo import decision, flujo as flujo_numpy                    # noqa: E402
from nucleo import casos as _casos                                   # noqa: E402
from nucleo.casos import ErrorKrylov, implementacion, leer_columnas  # noqa: E402
from nucleo.preproceso import (LADO, acumular_por_bloque, canal_tendencia, canales_terreno, geometria_grilla,  # noqa: E402
                               indices_bloque, transformar_valor)

MUESTRAS_POSTERIOR = 32          # muestras de θ por análisis
RESULTADOS_POR_LUGAR = 12        # resultados posibles de una medición, en «¿Dónde mido?»
MAXIMO_DE_LUGARES = 40
ETIQUETAS = {"tendencia": "Cercanía al río", "continuidad": "Lo que pasa en los bloques vecinos",
             "ruido": "Error de cada medición"}
_FILA, _COLUMNA = (m.reshape(-1).astype(np.float64) for m in np.meshgrid(np.arange(LADO), np.arange(LADO), indexing="ij"))


def _numeros(textos: list[str]) -> np.ndarray:
    return np.array([float(t) for t in textos], dtype=np.float64)


def leer_terreno(caso: dict, mediciones: list[dict] = (), sin_tendencia: bool = False) -> dict:
    """Las mediciones del caso (más las simuladas por el usuario) acumuladas por bloque, y la geometría de la grilla."""
    col = caso["columnas"]
    tabla = leer_columnas(caso["dataset"])
    x, y, valor = (_numeros(tabla[col[k]]) for k in ("x", "y", "valor"))
    if mediciones:
        x, y, valor = (np.concatenate([v, [float(m[k]) for m in mediciones]]) for v, k in ((x, "x"), (y, "y"), (valor, "valor")))
    transformacion = col.get("transformacion")
    grilla = None
    if col.get("tendencia") and caso.get("grilla") and not sin_tendencia:
        g = leer_columnas(caso["grilla"])
        grilla = {"x": _numeros(g["x"]), "y": _numeros(g["y"]), "dist": _numeros(g[col["tendencia"]])}
        geo = geometria_grilla(np.concatenate([grilla["x"], x]), np.concatenate([grilla["y"], y]))
        raiz_dist, dentro = canal_tendencia(grilla["x"], grilla["y"], grilla["dist"], geo)
    else:
        if caso.get("grilla"):                 # sin tendencia, la grilla igual define la forma del terreno
            g = leer_columnas(caso["grilla"])
            gx, gy = _numeros(g["x"]), _numeros(g["y"])
            geo = geometria_grilla(np.concatenate([gx, x]), np.concatenate([gy, y]))
            _, dentro = canal_tendencia(gx, gy, np.zeros(len(gx)), geo)
        else:
            geo, dentro = geometria_grilla(x, y), np.ones((LADO, LADO), dtype=bool)
        raiz_dist = np.zeros((LADO, LADO), dtype=np.float32)
    fila, columna = indices_bloque(x, y, geo)
    suma, cuenta = acumular_por_bloque(fila, columna, transformar_valor(valor, transformacion))
    return {"x": x, "y": y, "valor": valor, "fila": fila, "columna": columna, "suma": suma, "cuenta": cuenta,
            "raiz_dist": raiz_dist, "dentro": dentro | (cuenta > 0), "geometria": geo, "transformacion": transformacion,
            "umbral": float(col["umbral"]), "unidad_valor": col.get("unidad_valor", "")}


def canales_de(suma: np.ndarray, cuenta: np.ndarray, raiz_dist: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Canales (..., 3, LADO, LADO) con el preprocesamiento compartido, más la media y la escala de cada grilla."""
    (valor, marca, raiz), media, escala = canales_terreno(suma, cuenta, np.broadcast_to(raiz_dist, suma.shape))
    return np.stack([valor, marca, raiz], axis=-3).astype(np.float32), media[..., 0, 0], escala[..., 0, 0]


def canales_del_caso(nombre: str) -> dict:
    """Para `motor/espacial/mcmc.py`: los canales del archivo real de un caso, con su cuenta, media y escala."""
    terreno = leer_terreno(_casos.cargar_caso(nombre))
    canales, media, escala = canales_de(terreno["suma"], terreno["cuenta"], terreno["raiz_dist"])
    return {"canales": canales, "cuenta": terreno["cuenta"], "media": float(media), "escala": float(escala)}


@cache
def _red(carpeta: str, _version: float):
    """La sesión de onnxruntime del codificador con su cabeza de mapa, y los pesos del flujo."""
    import onnxruntime
    opciones = onnxruntime.SessionOptions()
    opciones.log_severity_level = 3
    sesion = onnxruntime.InferenceSession(f"{carpeta}/codificador.onnx", opciones, providers=["CPUExecutionProvider"])
    return sesion, flujo_numpy.cargar(f"{carpeta}/flujo.npz")


def _cargar_red():
    carpeta = _casos.ARTEFACTOS / "espacial"
    if not (carpeta / "codificador.onnx").exists() or not (carpeta / "flujo.npz").exists():
        raise ErrorKrylov("La red del terreno todavía no está exportada.", "no_disponible")
    return _red(str(carpeta), (carpeta / "codificador.onnx").stat().st_mtime)


def _theta_mcmc(clave: str, cuantas: int) -> np.ndarray:
    ruta = _casos.ARTEFACTOS / "espacial" / "mcmc" / f"{clave}.npz"
    if not ruta.exists():
        raise ErrorKrylov("Este análisis del terreno todavía no está precalculado.", "no_disponible")
    with np.load(ruta) as z:
        theta = z["theta_est"].astype(np.float64)
    elegidas = np.random.default_rng(0).choice(len(theta), size=min(cuantas, len(theta)), replace=False)
    return theta[np.sort(elegidas)]


def theta_del_mcmc() -> bool:
    """`KRYLOV_ESPACIAL_THETA=mcmc`: con la implementación `red`, el mapa sale de la cabeza de mapa y θ del MCMC precalculado.

    Es el salvavidas del plan para el caso en que la cabeza de mapa pasa su validación y la de flujo no: «qué
    manda en el terreno» se lee entonces del MCMC de referencia del archivo del caso, y la respuesta lo dice.
    """
    import os
    return os.environ.get("KRYLOV_ESPACIAL_THETA", "red").strip().lower() == "mcmc"


def inferir(canales: np.ndarray, cuenta: np.ndarray, impl: str, clave: str, muestras: int = MUESTRAS_POSTERIOR) -> dict:
    """El predictivo del mapa y el posterior de θ para un lote de grillas, con la red o con el MCMC precalculado.

    canales: (B, 3, LADO, LADO); cuenta: (B, LADO, LADO). Devuelve, en unidades estandarizadas:
      media, desviacion  (B, LADO, LADO)  predictivo marginal de y(s)
      theta              (S, 7) o (B, S, 7)  muestras del posterior de θ'
    - `red`: la cabeza de mapa entrega media y desviación; el flujo, θ (muestreado en NumPy).
    - `mcmc`: las muestras de θ del MCMC de referencia de `clave`, pasadas por el kriging exacto.
    """
    if impl == "red":
        sesion, pesos_flujo = _cargar_red()
        entrada = canales[:, : sesion.get_inputs()[0].shape[1]]
        media, log_desv, resumen = sesion.run(None, {"canales": entrada})
        if theta_del_mcmc():                          # salvavidas: mapa de la red, parámetros del MCMC precalculado
            theta = _theta_mcmc(clave, muestras)
        else:
            ruido = flujo_numpy.ruido(0, muestras, len(NOMBRES_THETA))
            theta = flujo_numpy.muestrear(pesos_flujo, resumen[:, None, :], np.broadcast_to(ruido, (len(canales),) + ruido.shape))
        return {"media": media.astype(np.float64), "desviacion": np.exp(log_desv.astype(np.float64)), "theta": theta.astype(np.float64)}

    theta = _theta_mcmc(clave, muestras)
    medias, desviaciones = [], []
    for c, n in zip(canales, cuenta):
        medido = c[1].reshape(-1) > 0
        media, varianza = kriging(theta, _FILA[medido], _COLUMNA[medido], c[0].reshape(-1)[medido], c[2].reshape(-1)[medido],
                                  _FILA, _COLUMNA, c[2].reshape(-1), n.reshape(-1)[medido])
        medias.append(media.mean(0).reshape(LADO, LADO))
        desviaciones.append(np.sqrt(varianza.mean(0) + media.var(0)).reshape(LADO, LADO))
    return {"media": np.stack(medias), "desviacion": np.stack(desviaciones), "theta": theta}


def probabilidad_de_superar(media: np.ndarray, desviacion: np.ndarray, umbral: np.ndarray) -> np.ndarray:
    """P(y > umbral) por bloque, con el predictivo gaussiano de la cabeza de mapa (o de la mezcla del kriging)."""
    return 1.0 - _normal_acumulada((np.asarray(umbral)[..., None, None] - media) / desviacion)


def que_manda(theta: np.ndarray, raiz_dist: np.ndarray, dentro: np.ndarray, hay_tendencia: bool) -> list[dict]:
    """«Qué manda en el terreno»: qué parte de la variación explican el río, la continuidad entre vecinos y el ruido.

    Por muestra del posterior: varianza de la tendencia (β1²·Var(√dist) sobre el terreno), del campo (σ²) y del
    ruido de medición (τ²), como fracciones del total. La certeza de la tendencia sale del signo de β1; la de las
    otras dos, de qué fracción de las muestras le da más de 5% de la variación.
    """
    var_raiz = float(np.var(raiz_dist[dentro])) if hay_tendencia else 0.0
    tendencia, campo, ruido = theta[:, 6] ** 2 * var_raiz, np.exp(2 * theta[:, 3]), np.exp(2 * theta[:, 4])
    total = tendencia + campo + ruido
    filas = []
    partes = (("tendencia", tendencia / total, -theta[:, 6]), ("continuidad", campo / total, campo / total - 0.05),
              ("ruido", ruido / total, ruido / total - 0.05))
    for nombre, fraccion, signo in partes:
        if nombre == "tendencia" and not hay_tendencia:
            continue
        filas.append({"nombre": nombre, "etiqueta": ETIQUETAS[nombre], "direccion": "sube" if np.mean(signo) > 0 else "baja",
                      "efecto": round(float(fraccion.mean()), 3), "rango_bajo": round(float(np.quantile(fraccion, 0.05)), 3),
                      "rango_alto": round(float(np.quantile(fraccion, 0.95)), 3), "certeza": decision.certeza(signo)})
    return sorted(filas, key=lambda f: -f["efecto"])


def _a_unidades_del_caso(valor_est, media: float, escala: float, transformacion: str | None):
    """De unidades estandarizadas a las del archivo (deshace la estandarización y la transformación)."""
    crudo = np.asarray(valor_est) * escala + media
    return np.exp(crudo) if transformacion == "log" else crudo


def _umbral_estandarizado(terreno: dict, media, escala):
    return (transformar_valor(terreno["umbral"], terreno["transformacion"]) - media) / escala


def _clave(caso: dict, sin_tendencia: bool, sufijo: str = "") -> str:
    return caso["nombre"] + ("__quitar_tendencia" if sin_tendencia else "") + sufijo


def _examen(caso: dict, terreno: dict, impl: str, sin_tendencia: bool) -> dict | None:
    """Examen con datos reales: esconder 20% de las mediciones, responder con el resto y ver cuántas caen en el rango de 90%."""
    n = len(terreno["x"])
    escondidas = np.sort(np.random.default_rng(0).choice(n, size=max(1, round(0.2 * n)), replace=False))
    visibles = np.setdiff1d(np.arange(n), escondidas)
    valor_t = transformar_valor(terreno["valor"], terreno["transformacion"])
    suma, cuenta = acumular_por_bloque(terreno["fila"][visibles], terreno["columna"][visibles], valor_t[visibles])
    canales, media, escala = canales_de(suma, cuenta, terreno["raiz_dist"])
    try:
        r = inferir(canales[None], cuenta[None], impl, _clave(caso, sin_tendencia, "" if impl == "red" else "__examen"))
    except ErrorKrylov:
        return None                                   # con `mcmc`, el examen necesita su propia corrida precalculada
    theta = r["theta"].reshape(-1, len(NOMBRES_THETA))
    f, c = terreno["fila"][escondidas], terreno["columna"][escondidas]
    # Una medición nueva en el bloque: el predictivo del campo más el ruido de medición.
    desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + np.exp(2 * theta[:, 4]).mean())
    error = (valor_t[escondidas] - float(media)) / float(escala) - r["media"][0][f, c]
    aciertos = int((np.abs(error) < 1.645 * desv).sum())
    return {"tipo": "puntos_reales_escondidos", "n": int(len(escondidas)),
            "frase": f"Escondimos {len(escondidas)} mediciones reales y las adivinamos: {aciertos} cayeron dentro del rango que dimos.",
            "tramos": [{"dijimos": 0.9, "paso": round(aciertos / len(escondidas), 3), "n": int(len(escondidas))}]}


def analizar(caso: dict, transformaciones: list[str], costos: dict, mediciones: list[dict] = ()) -> dict:
    """El mapa del terreno: probabilidad de superar el umbral por bloque, qué manda y el examen."""
    sin_tendencia = "quitar_tendencia" in transformaciones
    impl = implementacion("espacial")
    terreno = leer_terreno(caso, mediciones, sin_tendencia)
    n = len(terreno["x"])
    if n < 30:
        return {"implementacion": impl, "mapa": None, "factores": None,
                "semaforo": {"estado": "rojo_datos", "motivo": f"Hay {n} mediciones y hacen falta al menos 30.", "propuesta": None}}

    canales, media, escala = canales_de(terreno["suma"], terreno["cuenta"], terreno["raiz_dist"])
    r = inferir(canales[None], terreno["cuenta"][None], impl, _clave(caso, sin_tendencia))
    p = probabilidad_de_superar(r["media"], r["desviacion"], _umbral_estandarizado(terreno, media, escala)[None])[0]
    dentro = terreno["dentro"]
    d = decision.decidir_espacial(p, costos["falso_si"], costos["falso_no"])
    theta = r["theta"].reshape(-1, len(NOMBRES_THETA))

    def lista(valores: np.ndarray, decimales: int) -> list:
        return [round(float(v), decimales) if ok else None for v, ok in zip(valores.reshape(-1), dentro.reshape(-1))]

    geo = terreno["geometria"]
    mapa = {"nx": LADO, "ny": LADO, "x0": round(geo["x0"], 1), "y0": round(geo["y0"], 1), "lado": round(geo["lado"], 2),
            "p": lista(p, 3), "media": lista(_a_unidades_del_caso(r["media"][0], float(media), float(escala), terreno["transformacion"]), 1),
            "puntos": [{"x": float(x), "y": float(y), "valor": float(v)} for x, y, v in zip(terreno["x"], terreno["y"], terreno["valor"])],
            "umbral": terreno["umbral"], "unidad_valor": terreno["unidad_valor"]}
    return {
        "implementacion": impl, "mapa": mapa,
        "resumen_colores": decision.resumen_colores(d["estado"][dentro]),
        "costo_total": float(d["duda"][dentro].sum()),
        "factores": que_manda(theta, terreno["raiz_dist"], dentro, hay_tendencia=bool(canales[2].any())),
        "examen": _examen(caso, terreno, impl, sin_tendencia) if not mediciones else None,
        "registro": [f"{n} mediciones", f"grilla de {LADO} por {LADO} bloques", f"{int(dentro.sum())} bloques dentro del terreno"]
                    + (["qué manda en el terreno: precalculado con el método lento"] if impl == "red" and theta_del_mcmc() else []),
    }


def _lugares_candidatos(estado: np.ndarray, duda: np.ndarray, cuenta: np.ndarray, dentro: np.ndarray) -> np.ndarray:
    """Hasta MAXIMO_DE_LUGARES bloques en duda y sin medición, repartidos: de mayor a menor duda, sin vecinos pegados."""
    posibles = np.flatnonzero(((estado == "en_duda") & (cuenta == 0) & dentro).reshape(-1))
    elegidos: list[int] = []
    for i in posibles[np.argsort(-duda.reshape(-1)[posibles], kind="stable")]:
        f, c = divmod(int(i), LADO)
        if all(max(abs(f - e // LADO), abs(c - e % LADO)) >= 2 for e in elegidos):
            elegidos.append(int(i))
            if len(elegidos) == MAXIMO_DE_LUGARES:
                break
    return np.array(elegidos, dtype=int)


def donde_medir(caso: dict, costos: dict, mediciones: list[dict] = ()) -> dict:
    """«¿Dónde mido?»: los tres lugares donde una medición más baja más lo que cuesta no saber.

    Es diseño de experimentos por simulación. Para cada lugar candidato se imaginan
    RESULTADOS_POR_LUGAR resultados posibles de medir ahí (cuantiles equiprobables del
    predictivo actual de una medición en ese bloque) y **se rehace el análisis completo**
    con cada uno: preprocesamiento, red (o kriging con el posterior del MCMC) y decisión.
    El valor de medir en un lugar es cuánto baja, en promedio sobre esos resultados, el
    total de «lo que cuesta no saber». Con la red, todos los análisis van en un solo lote.
    """
    import time
    inicio = time.perf_counter()
    impl = implementacion("espacial")
    terreno = leer_terreno(caso, mediciones)
    dentro, suma, cuenta = terreno["dentro"], terreno["suma"], terreno["cuenta"]
    clave = _clave(caso, False)
    c_si, c_no, c_medir = costos["falso_si"], costos["falso_no"], costos.get("medicion", 0.0)

    def total_de_duda(sumas: np.ndarray, cuentas: np.ndarray, muestras: int):
        canales, media, escala = canales_de(sumas, cuentas, terreno["raiz_dist"])
        r = inferir(canales, cuentas, impl, clave, muestras)
        p = probabilidad_de_superar(r["media"], r["desviacion"], _umbral_estandarizado(terreno, media, escala))
        d = decision.decidir_espacial(p, c_si, c_no)
        return (d["duda"] * dentro).sum(axis=(1, 2)), d, r, media, escala

    total, d, r, media, escala = total_de_duda(suma[None], cuenta[None], MUESTRAS_POSTERIOR)
    lugares = _lugares_candidatos(d["estado"][0], d["duda"][0], cuenta, dentro)
    base = {"caso": caso["nombre"], "implementacion": impl, "precalculado": impl == "mcmc"}
    if len(lugares) == 0:
        return {**base, "candidatas": [], "mensaje_parada": "Con lo que ya sabes, medir más no se paga",
                "analisis_rehechos": 0, "tiempo_ms": round((time.perf_counter() - inicio) * 1000)}

    # Resultados posibles de medir en cada lugar: cuantiles del predictivo de una medición (campo + ruido).
    tau2 = float(np.exp(2 * r["theta"].reshape(-1, len(NOMBRES_THETA))[:, 4]).mean())
    f, c = np.divmod(lugares, LADO)
    desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + tau2)
    niveles = (np.arange(RESULTADOS_POR_LUGAR) + 0.5) / RESULTADOS_POR_LUGAR
    cuantil = np.array([_cuantil_normal(q) for q in niveles])
    resultado_est = r["media"][0][f, c][:, None] + desv[:, None] * cuantil[None, :]          # (lugares, resultados)
    resultado = resultado_est * float(escala[0]) + float(media[0])                             # en la escala transformada

    # Un análisis completo por (lugar, resultado): la grilla con esa medición agregada.
    n_lugares, k = len(lugares), RESULTADOS_POR_LUGAR
    sumas = np.broadcast_to(suma, (n_lugares, k, LADO, LADO)).copy()
    cuentas = np.broadcast_to(cuenta, (n_lugares, k, LADO, LADO)).copy()
    sumas[np.arange(n_lugares), :, f, c] += resultado
    cuentas[np.arange(n_lugares), :, f, c] += 1
    # Con el MCMC cada análisis es un kriging por muestra de θ: se usan 8 muestras.
    totales = total_de_duda(sumas.reshape(-1, LADO, LADO), cuentas.reshape(-1, LADO, LADO),
                            MUESTRAS_POSTERIOR if impl == "red" else 8)[0].reshape(n_lugares, k)
    valor_de_medir = float(total[0]) - totales.mean(axis=1)

    geo, transformacion = terreno["geometria"], terreno["transformacion"]
    def en_unidades(v):                                           # de la escala transformada a la del archivo
        return float(np.exp(v)) if transformacion == "log" else float(v)
    def posible(i: int, q: float) -> float:
        return round(en_unidades(float(media[0]) + float(escala[0]) * (r["media"][0][f[i], c[i]] + desv[i] * _cuantil_normal(q))))

    mejores = np.argsort(-valor_de_medir, kind="stable")[:3]
    candidatas = [{
        "puesto": puesto + 1, "etiqueta": "ABC"[puesto],
        "x": round(geo["x0"] + (c[i] + 0.5) * geo["lado"]), "y": round(geo["y0"] + (f[i] + 0.5) * geo["lado"]),
        "valor_de_medir": round(float(valor_de_medir[i])), "costo_medicion": round(c_medir),
        "valor_neto": round(float(valor_de_medir[i]) - c_medir),
        "resultados_posibles": {"bajo": posible(i, 0.1), "medio": posible(i, 0.5), "alto": posible(i, 0.9)},
    } for puesto, i in enumerate(mejores)]
    ninguna_paga = all(cand["valor_neto"] <= 0 for cand in candidatas)
    return {**base, "candidatas": candidatas,
            "mensaje_parada": "Con lo que ya sabes, medir más no se paga" if ninguna_paga else None,
            "analisis_rehechos": int(n_lugares * k), "tiempo_ms": round((time.perf_counter() - inicio) * 1000)}


def _cuantil_normal(q: float) -> float:
    """Cuantil de la normal estándar por bisección sobre la función de distribución (sin SciPy)."""
    bajo, alto = -8.0, 8.0
    for _ in range(60):
        medio = 0.5 * (bajo + alto)
        if 0.5 * (1.0 + math.erf(medio / math.sqrt(2.0))) < q:
            bajo = medio
        else:
            alto = medio
    return 0.5 * (bajo + alto)
