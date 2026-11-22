"""Exporta a `pitch/deck/datos/datos.js` los datos que anima el deck. No toca nada fuera de `pitch/deck/`.

Desde la raíz del repositorio:

    uv run python pitch/deck/datos/generar.py

Todo sale del repositorio, con la red del motor `espacial` (validada, sello de las 09:39). Desde el pivote a
minería (D-37) el caso estrella es `leyes`, un banco de tronadura simulado; el caso `terreno` (datos reales
públicos) queda para la demostración de tiempos y para el examen con datos reales.

- `terreno`     el caso estrella (`CASO`, hoy `leyes`): api.analizar, con el mapa y sus rótulos. La clave se llama
                `terreno` porque es el terreno que dibujan las láminas 4 y 5, sea cual sea el caso.
                El rango creíble por bloque (5% a 95%) es el de la respuesta de la API (`mapa.bajo` y `mapa.alto`, D-42).
- `donde`       api.donde_medir del caso estrella: los tres mejores lugares y, en `lugares`, todos los lugares
                candidatos con su valor, tal como los entrega la API (D-42).
- `mediciones`  api.analizar(CASO, mediciones=[...]) para cada letra y cada resultado posible (bajo, medio, alto):
                el mapa rehecho por la red. En el deck se anima este resultado.
- `real`        api.analizar("terreno"): el mapa del terreno real (155 mediciones de zinc junto al río Mosa) y su
                examen. Lo usan la lámina 2 (es el encargo de los 228 análisis, M-08 a M-10) y la de arquitectura.
- `pocos`       api.analizar("leyes_pocos"): el archivo que no alcanza. Krylov no responde y dice por qué.
- `practica`    cuántas muestras tenía cada uno de 3.000 terrenos del simulador `motor/espacial/simular.py`
                (semilla 2026): con qué se parece o no un archivo nuevo. Y los límites del motor (30 y 400).
- `simulados`   256 terrenos del mismo simulador, el campo verdadero de cada uno llevado a 0..255.
- `rafaga`      32 bancos del simulador y lo que la red respondió para cada uno (media y probabilidad de superar
                un límite fijo): es la lámina 2, donde entra un archivo y sale un mapa, uno tras otro.
- `series`      los otros cuatro casos de D-37 (taludes, flotacion, flota, sismicidad): las series de su archivo
                de demo, sus rótulos y, **si su motor ya responde**, la decisión por unidad y su curva. Mientras
                no responda, la lámina dibuja solo los datos; al volver a correr este script, aparece la respuesta.
                Con respuesta, además `posteriori`: por unidad, 64 cuantiles de la posteriori de lo que se decide
                (horas que faltan, cobre al final de la línea, riesgo de que el camión falle antes de su mantención,
                riesgo de un temblor fuerte). Es la `posteriori` de cada unidad en la respuesta de la API (D-42), que
                el motor arma con las mismas muestras con que decide: aquí no se vuelve a muestrear ni se ajusta ninguna
                curva. Es lo que dibuja el zoom de cada lámina (`js/zoom.js`).
- `sello`       copia de `motor/artefactos/espacial/sello.json`.

Tarda unos segundos. No hay que correrlo con un entrenamiento andando más de lo que dura.

    uv run python pitch/deck/datos/generar.py --series

rehace solo `series` (los cuatro casos de lista y su `posteriori`) y deja el resto de `datos.js` como estaba: no usa
`torch` ni vuelve a medir tiempos, así que se puede correr con un entrenamiento andando.
"""

from __future__ import annotations

import base64
import csv
import json
import os
import sys
import time
from pathlib import Path

os.environ["KRYLOV_MOTOR_ESPACIAL"] = "red"
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import numpy as np  # noqa: E402

from nucleo import api, casos, decision, espacial  # noqa: E402

CASO = "leyes"            # el caso estrella: láminas 4 y 5
REAL = "terreno"          # datos reales públicos: el encargo de los 228 análisis (M-08 a M-10) y el examen
POCOS = "leyes_pocos"     # el archivo que no alcanza
SERIES = ("taludes", "flotacion", "flota", "sismicidad")   # las otras cuatro decisiones de la mina
BANCOS_RAFAGA = 32
LIMITE_RAFAGA = 0.7       # el límite fijo, en unidades estandarizadas, con que se pintan los mapas de la ráfaga
SEMILLA = 2026
TERRENOS_SIMULADOS = 256
TERRENOS_PRACTICA = 3000
ESTADO = {"no_actuar": 0, "en_duda": 1, "actuar": 2}


def mapa_con_rango(nombre: str, mediciones: list[dict]) -> dict:
    """La respuesta de la API con su mapa por bloque: la media y el rango creíble de 90% (`mapa.bajo`, `mapa.alto`), en las unidades del caso."""
    r = api.analizar(nombre, mediciones=mediciones)
    assert r["implementacion"] == "red" and not r["precalculado"], "el mapa tiene que salir de la red"
    m = r["mapa"]
    dentro = [i for i, v in enumerate(m["media"]) if v is not None]
    assert all(m["bajo"][i] <= m["media"][i] <= m["alto"][i] for i in dentro), "la media tiene que quedar dentro de su rango"

    costos = {k: v["valor"] for k, v in r["costos"].items()}
    p = np.array([m["p"][i] for i in dentro])
    estado = decision.decidir_espacial(p, costos["falso_si"], costos["falso_no"])["estado"]
    return {
        "respuesta": r, "dentro": dentro,
        "media": [round(m["media"][i]) for i in dentro],
        "alto": [round(m["alto"][i]) for i in dentro],
        "bajo": [round(m["bajo"][i]) for i in dentro],           # el otro extremo del intervalo de credibilidad de 90%
        "p": [m["p"][i] for i in dentro],
        "estado": [ESTADO[e] for e in estado],
        "colores": r["resumen_colores"],
        "costo_de_no_saber": r["costo_de_no_saber"]["valor"],
    }


def capa(c: dict) -> dict:
    return {k: c[k] for k in ("media", "alto", "p", "estado", "colores", "costo_de_no_saber")}


def ficha(nombre: str, c: dict) -> dict:
    """Lo que las láminas necesitan de un caso espacial: geometría, mapa, puntos, rótulos y de dónde vienen los datos."""
    r, m = c["respuesta"], c["respuesta"]["mapa"]
    examen = (r.get("examen") or {}).get("tramos") or [None]
    return {
        "caso": nombre, "titulo": casos.cargar_caso(nombre)["tarjeta"]["titulo"],
        "nx": m["nx"], "ny": m["ny"], "x0": m["x0"], "y0": m["y0"], "lado": m["lado"],
        "umbral": m["umbral"], "unidad_valor": m["unidad_valor"], "punto_de_corte": r["punto_de_corte"],
        "dentro": c["dentro"], **capa(c), "bajo": c["bajo"],
        "puntos": [[p["x"], p["y"], p["valor"]] for p in m["puntos"]],
        "orilla": orilla_del_rio(nombre),
        "costos": {k: v["valor"] for k, v in r["costos"].items()},
        "rotulos": r["rotulos"], "unidad": r["unidad"], "examen": examen[0], "origen_datos": r["origen_datos"],
        "sintetico": r["sintetico"], "umbral_de_duda": decision.UMBRAL_DE_DUDA,
        "implementacion": r["implementacion"], "precalculado": r["precalculado"],
    }


def lugares_con_valor(donde: dict) -> list[dict]:
    """Todos los lugares candidatos de «¿Dónde perforo?» con lo que vale medir en cada uno, de la respuesta de la API.
    Se comprueba que los tres primeros son las tres candidatas."""
    lugares = donde["lugares"]
    for mia, suya in zip(lugares, donde["candidatas"]):
        assert (mia["x"], mia["y"], mia["valor_de_medir"]) == (suya["x"], suya["y"], suya["valor_de_medir"]), \
            f"los lugares no coinciden con las candidatas: {mia} / {suya}"
    return lugares


def orilla_del_rio(nombre: str) -> list[list[float]]:
    """Solo si el caso trae grilla con distancia a un río: las celdas pegadas a la orilla (distancia 0)."""
    grilla = casos.cargar_caso(nombre).get("grilla")
    if not grilla:
        return []
    with open(RAIZ / grilla) as f:
        return [[float(fila["x"]), float(fila["y"])] for fila in csv.DictReader(f) if float(fila["dist"]) == 0.0]


def simulador() -> tuple[str, list[int]]:
    """Del simulador del motor: 256 campos para dibujar y cuántas muestras tenían 3.000 terrenos de práctica."""
    import torch

    from motor.espacial.simular import Prior, simular

    gen = torch.Generator().manual_seed(SEMILLA)
    prior = Prior()
    campo = simular(TERRENOS_SIMULADOS, prior, gen)["campo"].numpy()
    lo = np.quantile(campo, 0.01, axis=(1, 2), keepdims=True)
    hi = np.quantile(campo, 0.99, axis=(1, 2), keepdims=True)
    gris = np.clip((campo - lo) / np.maximum(hi - lo, 1e-6), 0, 1)
    muestras: list[int] = []
    while len(muestras) < TERRENOS_PRACTICA:
        muestras += [int(v) for v in simular(500, prior, gen)["n"].tolist()]
    return base64.b64encode((gris * 255).round().astype(np.uint8).tobytes()).decode(), muestras[:TERRENOS_PRACTICA], prior


def rafaga() -> dict:
    """Bancos del simulador y la respuesta de la red para cada uno: los mapas que salen, uno tras otro, en la lámina 2."""
    import torch

    from motor.espacial.simular import Prior, simular

    gen = torch.Generator().manual_seed(SEMILLA + 1)
    d = simular(BANCOS_RAFAGA, Prior(), gen, con_tendencia=False)
    canales, cuenta = d["canales"].numpy().astype(np.float32), d["cuenta"].numpy().astype(np.float32)
    inicio = time.perf_counter()
    r = espacial.inferir(canales, cuenta, "red", "rafaga")
    ms = (time.perf_counter() - inicio) * 1000 / BANCOS_RAFAGA
    p = espacial.probabilidad_de_superar(r["media"], r["desviacion"], np.full(BANCOS_RAFAGA, LIMITE_RAFAGA))
    b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
    return {
        "n": BANCOS_RAFAGA, "lado": espacial.LADO, "limite": LIMITE_RAFAGA, "ms_por_banco_aqui": round(ms, 1),
        "media": b64(np.clip((r["media"] + 2.5) / 5 * 255, 0, 255).round().astype(np.uint8)),      # de −2,5 a 2,5
        "p": b64((np.clip(p, 0, 1) * 255).round().astype(np.uint8)),
        "muestras": b64(np.packbits(cuenta.reshape(BANCOS_RAFAGA, -1) > 0, axis=1)),
    }


def posteriori(nombre: str, r: dict) -> dict:
    """Por unidad, la posteriori de lo que se decide: la `posteriori` que trae cada unidad en la respuesta de la API (D-42).

    - taludes: horas que faltan para ceder, entre las muestras en que el sector se acelera (lo mismo que su `marca`);
      solo los sectores que se aceleran en al menos la mitad de las muestras;
    - flotacion: el último punto del abanico de su curva (el cobre al final de la línea);
    - sismicidad y flota: el riesgo que muestra su gráfico de intervalos (un temblor fuerte en el horizonte; que el
      camión falle antes de su mantención), uno por cada versión creíble de la faena (las `muestras_p` con que se decide).
    Se comprueba contra lo que la API publicó para esa unidad.
    """
    salida = {}
    for u in r["unidades"]:
        q, curva = u.get("posteriori"), u.get("curva")
        if q is None:
            continue
        if nombre == "taludes":
            assert abs(q["bajo"] - curva["marca"]["bajo"]) < 0.06 and abs(q["alto"] - curva["marca"]["alto"]) < 0.06, "las horas no coinciden con la marca de la API"
        elif nombre in ("sismicidad", "flota"):
            assert abs(float(np.median(u["muestras_p"])) - q["medio"]) < 0.006, "la posteriori no sale de las `muestras_p` de la API"
        elif curva:
            assert abs(q["bajo"] - curva["bajo"][-1]) < 2e-3 and abs(q["alto"] - curva["alto"][-1]) < 2e-3, "el final del abanico no coincide con la curva de la API"
        salida[u["id"]] = q
    return salida


def serie(nombre: str) -> dict:
    """Un caso de series: lo que trae su archivo y, si su motor ya responde, la decisión por unidad."""
    caso = casos.cargar_caso(nombre)
    col = caso["columnas"]
    unidades: dict[str, list] = {}
    with open(RAIZ / caso["dataset"]) as f:
        for fila in csv.DictReader(f):
            unidades.setdefault(fila[col["unidad"]], []).append([round(float(fila[col["tiempo"]]), 3), round(float(fila[col["valor"]]), 3)])
    verdad = {}
    if caso.get("verdad") and (RAIZ / caso["verdad"]).exists():
        with open(RAIZ / caso["verdad"]) as f:
            verdad = {fila[col["unidad"]] if col["unidad"] in fila else fila["unidad"]: fila for fila in csv.DictReader(f)}
    respuesta = None
    # Responde la red de ese motor solo si está exportada (motor/artefactos/<motor>/codificador.onnx) y pasó su sello
    # (regla 5 de AGENTS.md): si no pasó, la lámina dibuja el archivo y no muestra cifras.
    artefactos = RAIZ / "motor/artefactos" / caso["motor"]
    sello = json.loads((artefactos / "sello.json").read_text()) if (artefactos / "sello.json").exists() else None
    if (artefactos / "codificador.onnx").exists() and sello and sello.get("pasa"):
        os.environ["KRYLOV_MOTOR_" + caso["motor"].upper()] = "red"
    r = api.analizar(nombre)
    if "error" not in r and r.get("unidades") and r.get("implementacion") in ("red", "mcmc") and not r["semaforo"]["estado"].startswith("rojo"):
        respuesta = {
            "implementacion": r["implementacion"], "precalculado": r["precalculado"], "colores": r["resumen_colores"],
            "costo_de_no_saber": (r.get("costo_de_no_saber") or {}).get("valor"),
            "costos": {k: v.get("valor") for k, v in (r.get("costos") or {}).items()},
            "examen": r.get("examen"), "titular": r.get("titular"),
            "sello_pasa": bool(sello and sello.get("pasa")),
            "sello": {k: sello.get(k) for k in ("simulaciones_entrenamiento", "entrenamiento_min", "cobertura_90", "latencia_ms", "criterios")} if sello else None,
            "punto_de_corte": r.get("punto_de_corte"),
            # de cada unidad: su decisión, el riesgo que estima la red y su intervalo de credibilidad de 90%, y su curva
            "unidades": {u["id"]: {"estado": u["estado"], "p": u["p"], "rango": [u.get("rango_bajo"), u.get("rango_alto")], "curva": u.get("curva")} for u in r["unidades"]},
            "posteriori": posteriori(nombre, r),
        }
        # El examen de las decisiones: de las unidades donde decidió (actuar o no actuar), en cuántas acertó según la
        # verdad escondida del archivo simulado. Las que dejó «en duda» no cuentan: ahí dijo que no sabía.
        if verdad and caso.get("verdad_columna"):
            si = lambda v: str(v).strip().lower() in ("1", "true", "sí", "si")  # noqa: E731
            decididas = [u for u in r["unidades"] if u["estado"] != "en_duda" and u["id"] in verdad]
            correctas = sum((u["estado"] == "actuar") == si(verdad[u["id"]][caso["verdad_columna"]]) for u in decididas)
            respuesta["aciertos"] = {"decididas": len(decididas), "correctas": int(correctas)}
    return {
        "caso": nombre, "titulo": caso["tarjeta"]["titulo"], "pregunta": caso["pregunta"], "unidad": caso["unidad"],
        "rotulos": caso["rotulos"], "umbral": col.get("umbral"), "horizonte": col.get("horizonte"),
        "unidad_tiempo": col.get("unidad_tiempo"), "unidad_valor": col.get("unidad_valor"),
        "eje_tiempo": col.get("eje_tiempo"), "eje_valor": col.get("eje_valor"),
        "unidades": [{"id": k, "puntos": v} for k, v in unidades.items()],
        "lecturas": sum(len(v) for v in unidades.values()), "respuesta": respuesta,
        "verdad": {k: {c: v for c, v in fila.items() if c != "unidad"} for k, fila in verdad.items()},
        "tiempo_final": col.get("tiempo_final"),
    }


def modelo_de(nombre: str) -> dict:
    """Qué archivo pide el modelo de un caso: sus columnas, con el papel de cada una, y cuántas unidades y filas trae el de demo.
    Sale de casos/<caso>.yaml: el formato del archivo lo define el modelo bayesiano de esa decisión."""
    caso = casos.cargar_caso(nombre)
    col = caso["columnas"]
    with open(RAIZ / caso["dataset"]) as g:
        filas = list(csv.DictReader(g))
    papeles = [(col[k], k) for k in ("unidad", "x", "y", "tiempo", "valor") if k in col]
    papeles += [(c, "covariable") for c in col.get("covariables", [])]
    if col.get("horizonte_por_unidad"):
        papeles.append((col["horizonte_por_unidad"], "horizonte"))
    return {"caso": nombre, "motor": caso["motor"], "archivo": caso["dataset"].split("/")[-1], "filas": len(filas),
            "unidades": len({f[col["unidad"]] for f in filas}) if "unidad" in col else None,
            "unidad": caso["unidad"], "columnas": [{"nombre": n, "papel": q} for n, q in papeles],
            "primera": {n: filas[0][n] for n, _ in papeles}}


def examen_de_puntos(nombre: str) -> dict:
    """El examen que Krylov se toma con el archivo (nucleo/espacial._examen), guardando lo que dijo de cada muestra
    escondida: su estimación, el rango de 90% y el valor verdadero. Es lo que dibuja la lámina «¿Cómo sé que acierta?»."""
    caso = casos.cargar_caso(nombre)
    T = espacial.leer_terreno(caso, (), False)
    n = len(T["x"])
    esc = np.sort(np.random.default_rng(0).choice(n, size=max(1, round(0.2 * n)), replace=False))
    vis = np.setdiff1d(np.arange(n), esc)
    valor_t = espacial.transformar_valor(T["valor"], T["transformacion"])
    suma, cuenta = espacial.acumular_por_bloque(T["fila"][vis], T["columna"][vis], valor_t[vis])
    canales, media, escala = espacial.canales_de(suma, cuenta, T["raiz_dist"])
    r = espacial.inferir(canales[None], cuenta[None], "red", espacial._clave(caso, False))
    theta = r["theta"].reshape(-1, len(espacial.NOMBRES_THETA))
    f, c = T["fila"][esc], T["columna"][esc]
    desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + np.exp(2 * theta[:, 4]).mean())
    m = r["media"][0][f, c]
    assert T["transformacion"] == "log"
    a_unidades = lambda z: np.exp(z * float(escala) + float(media))  # noqa: E731
    est, bajo, alto, verdad = a_unidades(m), a_unidades(m - espacial.Z90 * desv), a_unidades(m + espacial.Z90 * desv), T["valor"][esc]
    return {"n": int(len(esc)), "dentro": int(((verdad >= bajo) & (verdad <= alto)).sum()), "limite": float(T["umbral"]),
            "unidad": T["unidad_valor"], "puntos": [[round(float(e), 1), round(float(b), 1), round(float(h), 1), float(v)]
                                                    for e, b, h, v in zip(est, bajo, alto, verdad)]}


def archivo_de(nombre: str, filas: int = 5) -> dict:
    """Cómo es el archivo que recibe un caso: sus primeras filas tal cual y qué columna cumple cada papel."""
    caso = casos.cargar_caso(nombre)
    with open(RAIZ / caso["dataset"]) as g:
        lector = csv.reader(g)
        cabecera = next(lector)
        todas = list(lector)
    col = caso["columnas"]
    papeles = {col[k]: k for k in ("x", "y", "valor", "unidad", "tiempo") if k in col}
    return {"archivo": caso["dataset"].split("/")[-1], "cabecera": cabecera, "filas": todas[:filas], "n": len(todas), "papeles": papeles}


def prueba_llm() -> dict | None:
    """La prueba de «el mismo archivo, a un LLM con 3 minutos» (pitch/deck/datos/prueba_llm/). Si no está, la lámina no muestra cifras."""
    ruta = Path(__file__).with_name("prueba_llm") / "resultado.json"
    return json.loads(ruta.read_text()) if ruta.exists() else None


def escribir(datos: dict) -> Path:
    salida = Path(__file__).with_name("datos.js")
    salida.write_text("// Generado por pitch/deck/datos/generar.py. No editar a mano.\nwindow.KRYLOV_DATOS = "
                      + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return salida


def informar_series(datos: dict) -> None:
    for nombre, c in datos["series"].items():
        print(" ", nombre, "·", len(c["unidades"]), c["unidad"]["plural"], "·", c["lecturas"], "lecturas ·",
              "responde: " + c["respuesta"]["implementacion"] if c["respuesta"] else "su motor todavía no responde: solo datos")


def solo_series() -> None:
    """Rehace `series` y deja lo demás de datos.js como estaba."""
    texto = Path(__file__).with_name("datos.js").read_text()
    datos = json.loads(texto[texto.index("{"):texto.rindex("}") + 1])
    datos["series"] = {nombre: serie(nombre) for nombre in SERIES}
    datos["series_generadas"] = time.strftime("%Y-%m-%d %H:%M")
    salida = escribir(datos)
    print(f"{salida.relative_to(RAIZ)}: solo `series`, {salida.stat().st_size / 1e3:.0f} kB")
    informar_series(datos)


def main() -> None:
    inicio = time.time()
    base = mapa_con_rango(CASO, [])
    r = base["respuesta"]
    caso_base = casos.cargar_caso(CASO)
    examen_bloques = espacial.examen_de_bloques(caso_base, {k: v["valor"] for k, v in r["costos"].items()})

    donde = api.donde_medir(CASO)
    assert donde["implementacion"] == "red" and not donde["precalculado"]

    mediciones = {}
    for c in donde["candidatas"]:
        mediciones[c["etiqueta"]] = {
            nivel: capa(mapa_con_rango(CASO, [{"x": c["x"], "y": c["y"], "valor": valor}]))
            for nivel, valor in c["resultados_posibles"].items()
        }

    real = mapa_con_rango(REAL, [])
    pocos = api.analizar(POCOS)
    assert pocos["semaforo"]["estado"].startswith("rojo"), "el archivo que no alcanza tendría que salir rojo"
    campos, muestras, prior = simulador()
    sello = json.loads((RAIZ / "motor/artefactos/espacial/sello.json").read_text())

    datos = {
        "generado": time.strftime("%Y-%m-%d %H:%M"),
        "comando": "uv run python pitch/deck/datos/generar.py",
        "terreno": {**ficha(CASO, base), "examen_bloques": examen_bloques},
        "donde": {
            "candidatas": donde["candidatas"], "analisis_rehechos": donde["analisis_rehechos"],
            "lugares": lugares_con_valor(donde), "resultados_por_lugar": espacial.RESULTADOS_POR_LUGAR,
            "implementacion": donde["implementacion"], "precalculado": donde["precalculado"], "tiempo_ms_aqui": donde["tiempo_ms"],
        },
        "mediciones": mediciones,
        "real": ficha(REAL, real),
        "pocos": {
            "caso": POCOS, "semaforo": pocos["semaforo"], "titular": pocos["titular"],
            "muestras": sum(1 for _ in open(RAIZ / casos.cargar_caso(POCOS)["dataset"])) - 1,
        },
        "practica": {"muestras": muestras, "minimo": prior.n_min, "maximo": espacial.MEDICIONES_MAXIMO, "semilla": SEMILLA},
        "simulados": {"n": TERRENOS_SIMULADOS, "lado": 32, "semilla": SEMILLA, "b64": campos},
        "rafaga": rafaga(),
        "series": {nombre: serie(nombre) for nombre in SERIES},
        "sello": sello,
        "examen_puntos": examen_de_puntos(CASO),
        "modelos": [modelo_de(n) for n in (CASO,) + SERIES],
        "prueba_llm": prueba_llm(),
    }
    salida = escribir(datos)
    print(f"{salida.relative_to(RAIZ)}: {salida.stat().st_size / 1e3:.0f} kB en {time.time() - inicio:.1f} s")
    print(CASO, "· colores", base["colores"], "· cuesta no saber", base["costo_de_no_saber"], "·", r["origen_datos"])
    for c in donde["candidatas"]:
        print(" ", c["etiqueta"], c["valor_de_medir"], c["resultados_posibles"],
              {k: v["costo_de_no_saber"] for k, v in mediciones[c["etiqueta"]].items()})
    print("  lugares candidatos:", len(datos["donde"]["lugares"]), "×", espacial.RESULTADOS_POR_LUGAR, "=",
          len(datos["donde"]["lugares"]) * espacial.RESULTADOS_POR_LUGAR, "análisis · API:", donde["analisis_rehechos"],
          "·", donde["tiempo_ms"], "ms en este computador")
    print(REAL, "· colores", real["colores"], "· examen", datos["real"]["examen"])
    print(POCOS, "·", datos["pocos"]["muestras"], "muestras ·", pocos["semaforo"]["motivo"])
    print("práctica:", len(muestras), "terrenos, de", min(muestras), "a", max(muestras), "muestras")
    print("ráfaga:", BANCOS_RAFAGA, "bancos ·", datos["rafaga"]["ms_por_banco_aqui"], "ms por banco en este computador (en lote)")
    informar_series(datos)


if __name__ == "__main__":
    solo_series() if "--series" in sys.argv else main()
