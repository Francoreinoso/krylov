"""Lo común a los cuatro motores de series al responder (`deformacion`, `cinetica`, `desgaste`, `sismico`).

Un archivo de series es largo: una fila por medición, con `unidad`, `tiempo` y `valor`
(`contratos/CONTRATO.md`, sección 1). El modelo de cada motor es jerárquico, con parámetros
globales η de la faena y locales λ_j de cada unidad, y el posterior amortizado está
factorizado (`WORKPLAN.md`, 11.1):

    p(η, λ_1..J | D)  ≈  q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D))

Aquí vive lo que no depende del motor: leer el archivo, revisar que su tamaño esté dentro
del diseño con que la red practicó, llevarlo a tensores con relleno y máscara, correr el
codificador (ONNX) y los dos flujos (NumPy), y armar `unidades`, `curva`, `factores` y el
examen del contrato. Cada motor (`nucleo/<motor_id>.py`) aporta su preprocesamiento, su
diseño de tamaños y su función «lo que se decide». Solo NumPy y onnxruntime.
"""

from __future__ import annotations

import json
from functools import cache

import numpy as np

from nucleo import casos as _casos, flujo as _flujo, tabla as lector
from nucleo.casos import ArchivoNoCalza, ErrorKrylov, implementacion, leer_columnas, tabla_del_caso

MUESTRAS_ETA = lector.MUESTRAS      # versiones creíbles de la faena: las 32 de `muestras_p`
MUESTRAS_LOCALES = 32               # por cada una, muestras de lo propio de cada unidad
SEMILLA = 0
TRAMOS_EXAMEN = ((0.0, 0.1), (0.1, 0.5), (0.5, 1.01))
MAX_PUNTOS_CURVA, PUNTOS_BANDA = 60, 12
CUANTILES = 64                      # con cuántos cuantiles se resume la posteriori de lo que se decide en cada unidad


# ------------------------------------------------------------------------------ leer el archivo largo

def leer(caso: dict, extras: tuple[str, ...] = ()) -> dict:
    """El archivo del caso por unidad: {"ids", "t": [arreglo por unidad], "y": [...], "extras": {papel: arreglo por unidad}}.

    Las unidades quedan en el orden en que aparecen y sus lecturas ordenadas por tiempo. Un papel de `extras`
    (una covariable repetida en las filas de la unidad) se lee de su primera fila.
    """
    col, tabla = caso["columnas"], tabla_del_caso(caso)
    unidad = lector.columna(tabla, lector.nombres_del_papel(col, "unidad", 1)[0])
    t = lector.numeros(tabla, lector.nombres_del_papel(col, "tiempo", 1)[0])
    y = lector.numeros(tabla, lector.nombres_del_papel(col, "valor", 1)[0])
    de_extras = {papel: lector.numeros(tabla, lector.nombres_del_papel(col, papel, 1)[0]) for papel in extras}
    ids = list(dict.fromkeys(u.strip() for u in unidad))
    filas = {i: [] for i in ids}
    for n, u in enumerate(unidad):
        filas[u.strip()].append(n)
    ts, ys, ex = [], [], {papel: [] for papel in extras}
    for i in ids:
        idx = np.array(filas[i])
        idx = idx[np.argsort(t[idx], kind="stable")]
        ts.append(t[idx]); ys.append(y[idx])
        for papel in extras:
            ex[papel].append(float(de_extras[papel][idx[0]]))
    return {"ids": ids, "t": ts, "y": ys, "extras": {papel: np.array(v) for papel, v in ex.items()}}


def revisar_tamano(caso: dict, series: dict, diseno: dict, practica: str) -> tuple[dict, str | None]:
    """El archivo contra el diseño de tamaños con que practicó la red (`DISENO` del motor, el mismo de su `config.json`).

    Bajo el mínimo de unidades, o sin ninguna unidad con el mínimo de lecturas: `rojo_datos`, con el motivo en palabras.
    Sobre el máximo: se responde con una submuestra de semilla fija (unidades al azar; lecturas adelgazadas de forma
    regular) y un aviso. Devuelve (series, aviso o None). `practica` es la frase «practiqué con …» del motor.
    """
    (u_min, u_max), (k_min, k_max) = diseno["unidades"], diseno["lecturas"]
    plural = caso["unidad"]["plural"]
    con_lecturas = [j for j, t in enumerate(series["t"]) if len(t) >= k_min]
    if len(series["ids"]) < u_min:
        cuantas = f"Hay 1 {caso['unidad']['singular']}" if len(series["ids"]) == 1 else f"Hay {len(series['ids'])} {plural}"
        raise ArchivoNoCalza(f"{cuantas} y {practica}: sube un archivo con más {plural}.")
    if len(con_lecturas) < u_min:
        raise ArchivoNoCalza(f"Solo {len(con_lecturas)} {plural} tienen al menos {k_min} mediciones, y {practica}: sube más mediciones de cada {caso['unidad']['singular']}.")
    avisos = []
    cortas = len(series["ids"]) - len(con_lecturas)
    if cortas:
        avisos.append(f"{cortas} {plural} quedaron fuera por tener menos de {k_min} mediciones")
    elegidas = con_lecturas
    if len(elegidas) > u_max:
        elegidas = sorted(np.random.default_rng(SEMILLA).choice(elegidas, size=u_max, replace=False).tolist())
        avisos.append(f"el archivo trae {len(con_lecturas)} {plural} y respondo sobre {u_max} elegidas al azar")
    def adelgazar(a: np.ndarray) -> np.ndarray:
        return a if len(a) <= k_max else a[np.round(np.linspace(0, len(a) - 1, k_max)).astype(int)]
    if any(len(series["t"][j]) > k_max for j in elegidas):
        avisos.append(f"las series de más de {k_max} mediciones se adelgazaron a {k_max}")
    nuevo = {"ids": [series["ids"][j] for j in elegidas],
             "t": [adelgazar(series["t"][j]) for j in elegidas], "y": [adelgazar(series["y"][j]) for j in elegidas],
             "extras": {papel: v[elegidas] for papel, v in series["extras"].items()}}
    return nuevo, ("; ".join(avisos).capitalize() + "." if avisos else None)


def con_relleno(arreglos: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Series de largo distinto a una matriz (unidades, lecturas) con relleno de ceros y su máscara (1 = lectura real)."""
    k = max(len(a) for a in arreglos)
    valores, mascara = np.zeros((len(arreglos), k), dtype=np.float32), np.zeros((len(arreglos), k), dtype=np.float32)
    for j, a in enumerate(arreglos):
        valores[j, : len(a)], mascara[j, : len(a)] = a, 1.0
    return valores, mascara


# ------------------------------------------------------------------------------ el posterior amortizado, sin torch

@cache
def _red(carpeta: str) -> dict:
    import onnxruntime
    from pathlib import Path
    carpeta = Path(carpeta)
    config = json.loads((carpeta / "config.json").read_text(encoding="utf-8"))
    opciones = onnxruntime.SessionOptions()
    opciones.enable_cpu_mem_arena = False        # el servidor tiene 512 MB: la memoria de cada análisis se devuelve al terminar
    sesion = onnxruntime.InferenceSession(str(carpeta / "codificador.onnx"), opciones, providers=["CPUExecutionProvider"])
    return {"config": config, "sesion": sesion, "flujo": _flujo.cargar(str(carpeta / "flujo.npz")),
            "local": _flujo.cargar(str(carpeta / "flujo_local.npz"))}


def red(motor_id: str) -> dict:
    carpeta = _casos.ARTEFACTOS / motor_id
    if not (carpeta / "codificador.onnx").exists():
        raise ErrorKrylov(f"El motor «{motor_id}» todavía no tiene una red exportada.", "no_disponible")
    return _red(str(carpeta))


def resumir(r: dict, x: np.ndarray, mascara: np.ndarray, cov: np.ndarray, tam: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """El codificador sobre un dataset: (s(D) de (c,), s_j de (unidades, c_j)). Rellena hasta las formas fijas del ONNX.

    x (U, K, canales), mascara (U, K), cov (U, c_cov), tam (c_tam). El relleno no cambia el resultado: cada capa
    multiplica por la máscara (`motor/comun/prueba_series.py` lo exige).
    """
    u_max, k_max = r["config"]["max_unidades"], r["config"]["max_lecturas"]
    u, k = mascara.shape
    X = np.zeros((1, u_max, k_max, x.shape[-1]), dtype=np.float32); X[0, :u, :k] = x
    M = np.zeros((1, u_max, k_max), dtype=np.float32); M[0, :u, :k] = mascara
    C = np.zeros((1, u_max, cov.shape[-1]), dtype=np.float32); C[0, :u] = cov
    s_d, s_j = r["sesion"].run(None, {"x": X, "mascara": M, "cov": C, "tam": tam[None].astype(np.float32)})
    return s_d[0], s_j[0, :u]


def muestrear_posterior(r: dict, s_d: np.ndarray, s_j: np.ndarray, m: int = MUESTRAS_ETA, l: int = MUESTRAS_LOCALES,
                        semilla: int = SEMILLA) -> tuple[np.ndarray, np.ndarray]:
    """Muestras de q(η | s(D)) y, por cada una, de q(λ_j | η, s_j, s(D)): η (m, d) y λ (m, l, unidades, d_local)."""
    gen = np.random.default_rng(semilla)
    d, d_local, u = len(r["flujo"]["media_theta"]), len(r["local"]["media_theta"]), len(s_j)
    eta = _flujo.muestrear(r["flujo"], s_d, gen.standard_normal((m, d)).astype(np.float32))
    contexto = contexto_local(r["flujo"], eta[:, None, None, :], s_j[None, None], s_d[None, None, None], (m, l, u))
    lam = muestrear_locales(r["local"], contexto, gen.standard_normal((m, l, u, d_local)).astype(np.float32), gen.random((m, l, u)).astype(np.float32))
    return eta, lam


def muestrear_locales(local: dict, contexto: np.ndarray, ruido: np.ndarray, uniforme: np.ndarray) -> np.ndarray:
    """λ_j dado su contexto. Si el motor tiene estado discreto (la cabeza `clase_*` viene en `flujo_local.npz`),
    z_j = 1 donde `uniforme` < P(z_j = 1 | contexto); el flujo se condiciona en z_j y z_j sale como última columna."""
    if "clase_n" not in local:
        return _flujo.muestrear(local, contexto, ruido)
    n = int(local["clase_n"])
    logit = _flujo._mlp(contexto, [local[f"clase_W{j}"] for j in range(n)], [local[f"clase_b{j}"] for j in range(n)])[..., 0]
    z = (uniforme < 1.0 / (1.0 + np.exp(-logit))).astype(np.float32)[..., None]
    return np.concatenate([_flujo.muestrear(local, np.concatenate([contexto, z], axis=-1), ruido), z], axis=-1)


def contexto_local(flujo_global: dict, eta: np.ndarray, s_j: np.ndarray, s_d: np.ndarray, forma: tuple[int, ...]) -> np.ndarray:
    """El contexto del flujo local: [η estandarizado, s_j, s(D)], difundido a `forma` + (c,). Igual que en `motor/comun/series.py`."""
    eta_z = (eta - flujo_global["media_theta"]) / flujo_global["escala_theta"]
    partes = [np.broadcast_to(p, forma + (p.shape[-1],)) for p in (eta_z, s_j, s_d)]
    return np.concatenate(partes, axis=-1).astype(np.float32)


def posterior(motor_id: str, caso: dict, x, mascara, cov, tam) -> tuple[np.ndarray, np.ndarray, str]:
    """(η, λ, implementación) para el archivo del caso: de la red, o del MCMC de referencia precalculado si el motor está en `mcmc`.

    El MCMC precalculado vive en `motor/artefactos/<motor_id>/mcmc/<caso>.npz` con `eta` (m, d) y `lam` (m, unidades, d_local),
    en el mismo espacio sin restricciones que la red; solo existe para archivos del demo.
    """
    if implementacion(motor_id) == "red":
        r = red(motor_id)
        return (*muestrear_posterior(r, *resumir(r, x, mascara, cov, tam)), "red")
    ruta = _casos.ARTEFACTOS / motor_id / "mcmc" / f"{caso['nombre']}.npz"
    if not ruta.exists():
        raise ErrorKrylov(f"El caso «{caso['nombre']}» todavía no tiene su respuesta precalculada.", "no_disponible")
    with np.load(ruta) as z:
        eta, lam = z["eta"], z["lam"]
    if lam.shape[1] != mascara.shape[0]:
        raise ErrorKrylov(f"La respuesta precalculada de «{caso['nombre']}» es de otro archivo.", "no_disponible")
    idx = np.round(np.linspace(0, len(eta) - 1, MUESTRAS_ETA * MUESTRAS_LOCALES)).astype(int).reshape(MUESTRAS_ETA, MUESTRAS_LOCALES)
    return eta[idx[:, 0]], lam[idx], "mcmc"      # cada «versión de la faena» agrupa muestras vecinas de la cadena adelgazada


# ------------------------------------------------------------------------------ hacia el contrato

def curva(t: np.ndarray, y: np.ndarray, t_banda: np.ndarray, muestras: np.ndarray, caso: dict, limite: float | None,
          marca: dict | None = None, decimales: int = 3) -> dict:
    """La `curva` de una unidad: lo medido (hasta 60 puntos) y el rango de 90% de lo que viene. muestras: (n, len(t_banda))."""
    if len(t) > MAX_PUNTOS_CURVA:
        idx = np.round(np.linspace(0, len(t) - 1, MAX_PUNTOS_CURVA)).astype(int)
        t, y = t[idx], y[idx]
    bajo, medio, alto = np.quantile(muestras, [0.05, 0.5, 0.95], axis=0)
    r = lambda a: [round(float(v), decimales) for v in a]     # noqa: E731
    col = caso["columnas"]
    return {"t": r(t), "y": r(y), "ahora": round(float(t[-1]), decimales), "t_banda": r(t_banda),
            "bajo": r(bajo), "medio": r(medio), "alto": r(alto), "limite": limite,
            "eje_t": col.get("eje_tiempo", ""), "eje_y": col.get("eje_valor", ""), "marca": marca}


def posteriori(muestras: np.ndarray) -> dict:
    """La posteriori de lo que se decide en una unidad, desde sus muestras: el rango de 90% (cuantiles 5% y 95%), la
    mediana y 64 cuantiles equiespaciados, con 4 decimales. Es lo que dibuja la distribución completa de la unidad."""
    v = np.asarray(muestras, dtype=np.float64).reshape(-1)
    bajo, medio, alto = np.quantile(v, [0.05, 0.5, 0.95])
    cuantiles = np.quantile(v, (np.arange(CUANTILES) + 0.5) / CUANTILES)
    return {"bajo": round(float(bajo), 4), "medio": round(float(medio), 4), "alto": round(float(alto), 4),
            "muestras": int(v.size), "cuantiles": [round(float(q), 4) for q in cuantiles]}


def unidades(ids: list[str], muestras_p: np.ndarray, costos: dict, curvas: list[dict],
             se_decide: list[np.ndarray | None], medidas: list[tuple[np.ndarray, np.ndarray]]) -> list[dict]:
    """`unidades` del contrato con su `curva`, su `posteriori` y su `serie` (D-42), alineadas con `ids`.

    Con más de 60 unidades, la curva va solo en las 24 con más duda y en las de `actuar`. `se_decide` trae, por unidad,
    las muestras de lo que se decide (o None: esa unidad va sin posteriori); `medidas`, sus lecturas (tiempo, valor) tal
    como las leyó el motor, ordenadas por tiempo.
    """
    por_id = dict(zip(ids, zip(curvas, se_decide, medidas)))
    filas = lector.unidades(ids, muestras_p, costos)                 # ya ordenadas de mayor a menor duda
    for n, u in enumerate(filas):
        curva, muestras, (t, y) = por_id[u["id"]]
        u["curva"] = curva if len(filas) <= 60 or n < 24 or u["estado"] == "actuar" else None
        if muestras is not None:
            u["posteriori"] = posteriori(muestras)
        u["serie"] = [[round(float(a), 3), round(float(b), 3)] for a, b in zip(t, y)]
    return filas


def factores(caso: dict, globales: dict[str, tuple[np.ndarray, float, float]]) -> list[dict]:
    """«Qué pesa»: cada parámetro global con nombre en `etiquetas`, comparado con la faena típica del prior.

    globales: nombre → (muestras del posterior, media del prior, desviación del prior). `efecto` es la diferencia con la
    media del prior en desviaciones del prior; `certeza` sale de cuántas versiones creíbles coinciden en el signo
    (95%: seguro; 80%: probable), como en `contratos/CONTRATO.md`, sección 3.
    """
    salida = []
    for nombre, etiqueta in (caso.get("etiquetas") or {}).items():
        if nombre not in globales:
            continue
        muestras, media, desv = globales[nombre]
        z = (np.asarray(muestras) - media) / desv
        acuerdo = max(float((z > 0).mean()), float((z < 0).mean()))
        bajo, alto = np.quantile(z, [0.05, 0.95])
        salida.append({"nombre": nombre, "etiqueta": etiqueta, "direccion": "sube" if z.mean() > 0 else "baja",
                       "efecto": round(float(z.mean()), 2), "rango_bajo": round(float(bajo), 2), "rango_alto": round(float(alto), 2),
                       "certeza": "seguro" if acuerdo >= 0.95 else "probable" if acuerdo >= 0.80 else "no_se_sabe"})
    return sorted(salida, key=lambda f: -abs(f["efecto"]))


def examen(caso: dict, ids: list[str], p: np.ndarray) -> dict | None:
    """Examen con la verdad escondida: lo que Krylov dijo de cada unidad contra lo que pasó (`<caso>_verdad.csv`).

    El archivo de verdad nunca entra al motor. Devuelve tramos de probabilidad con lo dicho (promedio de p) y lo que
    pasó (frecuencia). La frase la escribe `nucleo/textos.py` con estos números. None si el caso no trae verdad.
    """
    if not caso.get("verdad") or not caso.get("verdad_columna"):
        return None
    tabla = leer_columnas(caso["verdad"])
    verdad = {u.strip(): float(v) for u, v in zip(tabla["unidad"], tabla[caso["verdad_columna"]]) if v.strip()}
    pares = np.array([(p[j], verdad[i]) for j, i in enumerate(ids) if i in verdad])
    if len(pares) == 0:
        return None
    tramos = []
    for bajo, alto in TRAMOS_EXAMEN:
        en = (pares[:, 0] >= bajo) & (pares[:, 0] < alto)
        if en.any():
            tramos.append({"dijimos": round(float(pares[en, 0].mean()), 3), "paso": round(float(pares[en, 1].mean()), 3), "n": int(en.sum())})
    return {"tipo": "verdad_escondida", "n": int(len(pares)), "frase": "", "tramos": tramos}


def numero(n: int) -> str:
    return f"{n:,}".replace(",", ".")
