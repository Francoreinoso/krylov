"""La sexta decisión, «¿Dónde está el mineral?»: la red del motor `yacimiento` responde un archivo subido.

El motor vive en `yacimiento/` (D-40) y su red es de `torch`, que no entra al servicio. Aquí corre su cabeza de mapa
exportada a ONNX (`yacimiento/artefactos/mapa.onnx`, que escribe `yacimiento/exportar_onnx.py`) con el mismo
preprocesamiento de `yacimiento.modelo.preparar`, escrito en NumPy; el exportador comprueba que los dos dan lo mismo.
La cabeza de parámetros no se exporta: no pasa su validación (`artefactos/sello.json`) y no se muestra.

**El archivo.** Una fila por bloque del modelo de bloques (32 × 32 × 16 = 16.384 filas): dónde está el bloque, las siete
covariables del modelo geológico (la octava, la profundidad, sale de la posición) y el cobre medido, que viene solo en
los bloques que cruzó una perforación. La red necesita las covariables en todos los bloques, no solo en las muestras.
"""
from __future__ import annotations

import base64
import json
import math
import time
from functools import cache
from pathlib import Path

import numpy as np

from nucleo import api, decision, preproceso
from nucleo.casos import ArchivoNoCalza

MOTOR_ID = "yacimiento"
ARTEFACTOS = Path(__file__).resolve().parent.parent / "yacimiento" / "artefactos"
NX, NY, NZ = 32, 32, 16                     # el modelo de bloques de `yacimiento/modelo.py`
REFERENCIA = math.log(0.5)                  # log de 0,5% de cobre, como en `yacimiento/modelo.py`
MUESTRAS = (120, 960)                       # el diseño con que practicó la red: de 15 a 60 perforaciones, de 8 a 16 muestras cada una
LEY_MIN, LEY_MAX, DESV_MAX = -3.0, 1.5, 1.5  # la escala de un byte de `yacimiento/exportar_deck.py`

_NUMERO = {"tipo": "numero", "cantidad": 1}
PAPELES = [
    {**_NUMERO, "papel": "este", "texto": "Coordenada este",
     "texto_largo": "Dónde está el bloque hacia el este, en metros. El modelo de bloques tiene 32 posiciones distintas."},
    {**_NUMERO, "papel": "norte", "texto": "Coordenada norte",
     "texto_largo": "Dónde está el bloque hacia el norte, en metros. El modelo de bloques tiene 32 posiciones distintas."},
    {**_NUMERO, "papel": "profundidad", "texto": "Profundidad",
     "texto_largo": "A qué profundidad está el bloque, en metros desde la superficie. El modelo de bloques tiene 16 pisos."},
    {**_NUMERO, "papel": "valor", "texto": "Cobre medido",
     "texto_largo": "El porcentaje de cobre de la muestra de roca de ese bloque. Viene vacío en los bloques que ninguna perforación cruzó."},
    {**_NUMERO, "papel": "falla", "texto": "Cercanía a la falla",
     "texto_largo": "Qué tan cerca está el bloque de la falla (una grieta grande de la roca), según el modelo geológico."},
    {**_NUMERO, "papel": "litologia_b", "texto": "Litología B",
     "texto_largo": "1 si el bloque es del segundo tipo de roca del modelo geológico, 0 si no."},
    {**_NUMERO, "papel": "litologia_c", "texto": "Litología C",
     "texto_largo": "1 si el bloque es del tercer tipo de roca del modelo geológico, 0 si no."},
    {**_NUMERO, "papel": "alteracion", "texto": "Alteración",
     "texto_largo": "Cuánto cambió la roca del bloque por los fluidos calientes que trajeron el cobre, según el modelo geológico."},
    {**_NUMERO, "papel": "geofisica_1", "texto": "Geofísica, primer campo",
     "texto_largo": "Una medición hecha desde la superficie, sin perforar, llevada a cada bloque."},
    {**_NUMERO, "papel": "geofisica_2", "texto": "Geofísica, segundo campo",
     "texto_largo": "Otra medición hecha desde la superficie, sin perforar, llevada a cada bloque."},
    {**_NUMERO, "papel": "vetillas", "texto": "Vetillas",
     "texto_largo": "Cuántas vetillas (grietas finas rellenas de mineral) trae la roca del bloque, según el modelo geológico."},
]
_CONTINUAS = ("falla", "alteracion", "geofisica_1", "geofisica_2", "vetillas")    # llegan a la red con media 0 y desviación 1 sobre la grilla


def papeles() -> dict:
    completos = [{**p, "minimo": 1, "maximo": 1} for p in PAPELES]
    return {"motor_id": MOTOR_ID, "caso_base": MOTOR_ID, "papeles": completos,
            "rangos": {"muestras": {"minimo": MUESTRAS[0], "maximo": MUESTRAS[1]},
                       "frase": f"Practiqué con yacimientos de {NX} × {NY} × {NZ} bloques y de {MUESTRAS[0]} a {MUESTRAS[1]} muestras de roca."}}


@cache
def _caso() -> dict:
    """La ley de corte y los dos costos por bloque: supuestos del demo, los mismos del sello (pitch/CIFRAS.md, K-71 a K-73)."""
    return json.loads((ARTEFACTOS / "sello.json").read_text(encoding="utf-8"))["demo"]["caso"]


@cache
def _sesion():
    import onnxruntime as ort
    opciones = ort.SessionOptions()
    opciones.intra_op_num_threads = 1       # el servidor gratuito tiene un procesador y 512 MB
    return ort.InferenceSession(str(ARTEFACTOS / "mapa.onnx"), opciones, providers=["CPUExecutionProvider"])


def preparar(y: np.ndarray, mascara: np.ndarray, cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """`yacimiento.modelo.preparar` en NumPy, para un yacimiento: la entrada de la red (11, X, Y, Z) y la tendencia ajustada.

    Ajusta por mínimos cuadrados (con la misma regularización) la ley contra las covariables en las muestras."""
    X = np.concatenate([np.ones((1, y.size)), cov.reshape(cov.shape[0], -1)]).astype(np.float64)       # (9, N)
    m = mascara.reshape(1, -1).astype(np.float64)
    A = (X * m) @ X.T + 1e-2 * np.eye(X.shape[0])
    coef = np.linalg.solve(A, (X * m) @ y.reshape(-1).astype(np.float64))
    tendencia = (coef @ X).reshape(y.shape)
    residuo = (y - tendencia) * mascara
    x = np.concatenate([residuo[None], mascara[None], (tendencia - REFERENCIA)[None], cov]).astype(np.float32)
    return x, tendencia.astype(np.float32)


def responder(y: np.ndarray, mascara: np.ndarray, cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La cabeza de mapa: media y desviación del log de la ley de cada bloque, (X, Y, Z) cada una."""
    x, tendencia = preparar(y, mascara, cov)
    media, desv = _sesion().run(None, {"x": x[None], "tendencia": tendencia[None]})
    return media[0].astype(np.float64), desv[0].astype(np.float64)


def _b64(a: np.ndarray, lo: float, hi: float) -> str:
    return base64.b64encode(np.clip(np.round((a - lo) / (hi - lo) * 255), 0, 255).astype(np.uint8).tobytes()).decode()


def _columna(tabla: dict[str, list[str]], columnas: dict, papel: dict) -> np.ndarray:
    """La columna que el usuario confirmó para un papel, como números (vacío o texto: NaN), con su transformación si trae."""
    entrada = columnas.get(papel["papel"]) or {}
    elegidas = entrada.get("columnas") if isinstance(entrada, dict) else None
    if not elegidas or elegidas[0] not in tabla:
        raise ArchivoNoCalza(f"Falta decir qué columna es «{papel['texto']}».")
    valores = tabla[elegidas[0]]
    t = entrada.get("transformacion")
    if isinstance(t, dict) and t.get("nombre") in preproceso.TRANSFORMACIONES:
        try:
            valores = preproceso.TRANSFORMACIONES[t["nombre"]](valores, tabla, **{k: v for k, v in t.items() if k != "nombre" and v is not None})
        except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError):
            raise ArchivoNoCalza(f"No se pudo convertir la columna «{elegidas[0]}» a lo que pide «{papel['texto']}».") from None

    def numero(v) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return math.nan
    return np.array([numero(v.strip() if isinstance(v, str) else v) for v in valores], dtype=np.float64)


def _grilla(tabla: dict[str, list[str]], columnas: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """El archivo como lo recibe la red: y (log de % de cobre; cero sin muestra), la máscara de muestras y las 8 covariables."""
    c = {p["papel"]: _columna(tabla, columnas, p) for p in PAPELES}
    filas = len(c["este"])
    miles = lambda n: f"{n:,}".replace(",", ".")              # noqa: E731
    forma = f"Este modelo lee un yacimiento de {NX} × {NY} × {NZ} bloques: {miles(NX * NY * NZ)} filas, una por bloque"
    if filas != NX * NY * NZ:
        raise ArchivoNoCalza(f"{forma}. El archivo trae {miles(filas)} filas.")
    indices = []
    for papel, n, que in (("este", NX, "posiciones hacia el este"), ("norte", NY, "posiciones hacia el norte"), ("profundidad", NZ, "profundidades")):
        if not np.isfinite(c[papel]).all():
            raise ArchivoNoCalza(f"La columna de «{papel}» tiene filas vacías o que no son números: cada bloque necesita su posición.")
        distintos, indice = np.unique(c[papel], return_inverse=True)
        if len(distintos) != n:
            raise ArchivoNoCalza(f"{forma}. El archivo trae {len(distintos)} {que} distintas y el modelo espera {n}.")
        indices.append(indice)
    i, j, k = indices
    if len(np.unique((i * NY + j) * NZ + k)) != filas:
        raise ArchivoNoCalza(f"{forma}. En el archivo hay bloques repetidos y otros que faltan.")
    cov = np.zeros((8, NX, NY, NZ))
    cov[0] = np.linspace(-1.0, 1.0, NZ)                                         # la profundidad, como en el simulador
    for n, papel in enumerate(("falla", "litologia_b", "litologia_c", "alteracion", "geofisica_1", "geofisica_2", "vetillas"), start=1):
        v = c[papel]
        if not np.isfinite(v).all():
            raise ArchivoNoCalza(f"A la columna de «{papel}» le faltan valores: el modelo necesita ese dato en todos los bloques, también en los que no se perforó.")
        if papel in _CONTINUAS:
            if v.std() < 1e-9:
                raise ArchivoNoCalza(f"La columna de «{papel}» trae el mismo valor en todos los bloques: no dice nada del yacimiento.")
            v = (v - v.mean()) / v.std()
        else:
            v = (v > 0.5).astype(np.float64)
        cov[n, i, j, k] = v
    con_muestra = np.isfinite(c["valor"]) & (c["valor"] > 0)
    n_muestras = int(con_muestra.sum())
    if not MUESTRAS[0] <= n_muestras <= MUESTRAS[1]:
        raise ArchivoNoCalza(f"El archivo trae {n_muestras} bloques con cobre medido, y Krylov practicó con yacimientos de {MUESTRAS[0]} a {MUESTRAS[1]} muestras. "
                             + ("Faltan muestras para responder." if n_muestras < MUESTRAS[0] else "Deja el cobre solo en los bloques que cruzó una perforación."))
    y, mascara = np.zeros((NX, NY, NZ)), np.zeros((NX, NY, NZ))
    y[i[con_muestra], j[con_muestra], k[con_muestra]] = np.log(c["valor"][con_muestra])
    mascara[i[con_muestra], j[con_muestra], k[con_muestra]] = 1.0
    return y, mascara, cov


def _datos(media: np.ndarray, desv: np.ndarray, mascara: np.ndarray, latencia_ms: int) -> dict:
    """Lo que dibuja `pitch/deck/yacimiento.html`, con la forma de `yacimiento/exportar_deck.py` y sin examen:
    un archivo subido no trae la respuesta correcta."""
    caso = _caso()
    z = (math.log(caso["ley_de_corte_pct"]) - media) / desv
    p = 0.5 * np.vectorize(math.erfc)(z / math.sqrt(2.0))                   # probabilidad de que el bloque supere la ley de corte
    d = decision.decidir_espacial(p, caso["falso_si"], caso["falso_no"])
    return {"dim": [NX, NY, NZ], "ley_min": LEY_MIN, "ley_max": LEY_MAX, "desv_max": DESV_MAX, "caso": caso,
            "punto_de_corte": decision.punto_de_corte(caso["falso_si"], caso["falso_no"]), "umbral_de_duda": decision.UMBRAL_DE_DUDA,
            "red": {"media": _b64(media, LEY_MIN, LEY_MAX), "desv": _b64(desv, 0, DESV_MAX), "p": _b64(p, 0, 1)},
            "numeros": {"compositos": int(mascara.sum()), "bloques": int(p.size), "covariables": 8, "latencia_ms": latencia_ms,
                        "colores": decision.resumen_colores(d["estado"]), "acierto_decididos": None}}


def analizar_archivo(contenido, columnas: dict) -> dict:
    """Un archivo subido, con las columnas que confirmó el usuario: responde la red, o el semáforo dice por qué no."""
    inicio = time.perf_counter()
    base = {"caso": None, "motor_id": MOTOR_ID, "implementacion": "red", "precalculado": False}
    try:
        y, mascara, cov = _grilla(api.leer_tabla(contenido), columnas)
    except ArchivoNoCalza as e:
        return {**base, "semaforo": {"estado": e.estado, "motivo": e.motivo, "propuesta": None}, "yacimiento": None, "tiempo_ms": 0}
    antes = time.perf_counter()
    media, desv = responder(y, mascara, cov)
    datos = _datos(media, desv, mascara, round(1000 * (time.perf_counter() - antes)))
    return {**base, "semaforo": {"estado": "verde", "motivo": "", "propuesta": None}, "yacimiento": datos,
            "tiempo_ms": round(1000 * (time.perf_counter() - inicio))}
