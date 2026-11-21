"""Exporta a `pitch/deck/datos/datos.js` los datos que anima el deck. No toca nada fuera de `pitch/deck/`.

Desde la raíz del repositorio:

    uv run python pitch/deck/datos/generar.py

Todo sale del repositorio, con la red del motor `espacial` (validada, sello de las 09:39). Desde el pivote a
minería (D-37) el caso estrella es `leyes`, un banco de tronadura simulado; el caso `terreno` (datos reales
públicos) queda para la demostración de tiempos y para el examen con datos reales.

- `terreno`     el caso estrella (`CASO`, hoy `leyes`): api.analizar, con el mapa y sus rótulos. La clave se llama
                `terreno` porque es el terreno que dibujan las láminas 4 y 5, sea cual sea el caso.
                El rango creíble por bloque (5% a 95%) no viene en la respuesta de la API: se calcula aquí con las
                mismas funciones de `nucleo/espacial.py` y se comprueba que la media coincide con la de la API.
- `donde`       api.donde_medir del caso estrella: los tres mejores lugares. Además, `lugares`: todos los lugares
                candidatos con su valor, repitiendo el cálculo de `nucleo/espacial.donde_medir` (se comprueba que
                los tres mejores coinciden con los de la API).
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
- `sello`       copia de `motor/artefactos/espacial/sello.json`.

Tarda unos segundos. No hay que correrlo con un entrenamiento andando más de lo que dura.
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
Z90 = 1.645
ESTADO = {"no_actuar": 0, "en_duda": 1, "actuar": 2}


def mapa_con_rango(nombre: str, mediciones: list[dict]) -> dict:
    """La respuesta de la API más el tope del rango creíble de 90% por bloque, en las unidades del caso."""
    r = api.analizar(nombre, mediciones=mediciones)
    assert r["implementacion"] == "red" and not r["precalculado"], "el mapa tiene que salir de la red"
    m = r["mapa"]

    caso = casos.cargar_caso(nombre)
    terreno = espacial.leer_terreno(caso, mediciones)
    canales, media, escala = espacial.canales_de(terreno["suma"], terreno["cuenta"], terreno["raiz_dist"])
    inf = espacial.inferir(canales[None], terreno["cuenta"][None], "red", espacial._clave(caso, False))
    mu, desv = inf["media"][0], inf["desviacion"][0]

    def a_unidades(v):
        return espacial._a_unidades_del_caso(v, float(media), float(escala), terreno["transformacion"]).reshape(-1)

    centro, alto = a_unidades(mu), a_unidades(mu + Z90 * desv)
    dentro = [i for i, v in enumerate(m["media"]) if v is not None]
    assert np.allclose([m["media"][i] for i in dentro], centro[dentro], rtol=2e-4, atol=0.06), "la media no coincide con la de la API"

    costos = {k: v["valor"] for k, v in r["costos"].items()}
    p = np.array([m["p"][i] for i in dentro])
    estado = decision.decidir_espacial(p, costos["falso_si"], costos["falso_no"])["estado"]
    return {
        "respuesta": r, "dentro": dentro,
        "media": [round(float(centro[i])) for i in dentro],
        "alto": [round(float(alto[i])) for i in dentro],
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
        "dentro": c["dentro"], **capa(c),
        "puntos": [[p["x"], p["y"], p["valor"]] for p in m["puntos"]],
        "orilla": orilla_del_rio(nombre),
        "costos": {k: v["valor"] for k, v in r["costos"].items()},
        "rotulos": r["rotulos"], "unidad": r["unidad"], "examen": examen[0], "origen_datos": r["origen_datos"],
        "sintetico": r["sintetico"], "umbral_de_duda": decision.UMBRAL_DE_DUDA,
        "implementacion": r["implementacion"], "precalculado": r["precalculado"],
    }


def lugares_con_valor(nombre: str, candidatas: list[dict]) -> list[dict]:
    """Todos los lugares candidatos de «¿Dónde perforo?» con lo que vale medir en cada uno.

    La API entrega solo los tres mejores. Aquí se repite el cálculo de `nucleo/espacial.donde_medir`
    con sus mismas funciones, y se comprueba que los tres mejores coinciden con los de la API.
    """
    caso = casos.cargar_caso(nombre)
    costos = casos.costos_numericos(caso, None)
    terreno = espacial.leer_terreno(caso, [])
    dentro, suma, cuenta = terreno["dentro"], terreno["suma"], terreno["cuenta"]
    clave = espacial._clave(caso, False)
    lado = espacial.LADO

    def total_de_duda(sumas, cuentas):
        canales, media, escala = espacial.canales_de(sumas, cuentas, terreno["raiz_dist"])
        r = espacial.inferir(canales, cuentas, "red", clave, espacial.MUESTRAS_POSTERIOR)
        p = espacial.probabilidad_de_superar(r["media"], r["desviacion"], espacial._umbral_estandarizado(terreno, media, escala))
        d = decision.decidir_espacial(p, costos["falso_si"], costos["falso_no"])
        return (d["duda"] * dentro).sum(axis=(1, 2)), d, r, media, escala

    total, d, r, media, escala = total_de_duda(suma[None], cuenta[None])
    lugares = espacial._lugares_candidatos(d["estado"][0], d["duda"][0], cuenta, dentro)
    tau2 = float(np.exp(2 * r["theta"].reshape(-1, len(espacial.NOMBRES_THETA))[:, 4]).mean())
    f, c = np.divmod(lugares, lado)
    k = espacial.RESULTADOS_POR_LUGAR
    desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + tau2)
    cuantil = np.array([espacial._cuantil_normal(q) for q in (np.arange(k) + 0.5) / k])
    resultado = (r["media"][0][f, c][:, None] + desv[:, None] * cuantil[None, :]) * float(escala[0]) + float(media[0])
    n = len(lugares)
    sumas = np.broadcast_to(suma, (n, k, lado, lado)).copy()
    cuentas = np.broadcast_to(cuenta, (n, k, lado, lado)).copy()
    sumas[np.arange(n), :, f, c] += resultado
    cuentas[np.arange(n), :, f, c] += 1
    totales = total_de_duda(sumas.reshape(-1, lado, lado), cuentas.reshape(-1, lado, lado))[0].reshape(n, k)
    valor = float(total[0]) - totales.mean(axis=1)

    geo = terreno["geometria"]
    salida = [{"x": round(geo["x0"] + (c[i] + 0.5) * geo["lado"]), "y": round(geo["y0"] + (f[i] + 0.5) * geo["lado"]),
               "valor_de_medir": round(float(valor[i]))} for i in np.argsort(-valor, kind="stable")]
    for mia, suya in zip(salida, candidatas):
        assert (mia["x"], mia["y"]) == (suya["x"], suya["y"]) and abs(mia["valor_de_medir"] - suya["valor_de_medir"]) <= 1, \
            f"los lugares no coinciden con los de la API: {mia} / {suya}"
    return salida


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


def serie(nombre: str) -> dict:
    """Un caso de series: lo que trae su archivo y, si su motor ya responde, la decisión por unidad."""
    caso = casos.cargar_caso(nombre)
    col = caso["columnas"]
    unidades: dict[str, list] = {}
    with open(RAIZ / caso["dataset"]) as f:
        for fila in csv.DictReader(f):
            unidades.setdefault(fila[col["unidad"]], []).append([round(float(fila[col["tiempo"]]), 3), round(float(fila[col["valor"]]), 3)])
    respuesta = None
    # Si la red de ese motor ya está exportada (motor/artefactos/<motor>/codificador.onnx), responde ella, haya pasado
    # o no su sello: el deck muestra lo que la red dice hoy, y guarda `sello_pasa` para que las notas lo digan.
    artefactos = RAIZ / "motor/artefactos" / caso["motor"]
    sello = json.loads((artefactos / "sello.json").read_text()) if (artefactos / "sello.json").exists() else None
    if (artefactos / "codificador.onnx").exists():
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
            "unidades": {u["id"]: {"estado": u["estado"], "p": u["p"], "curva": u.get("curva")} for u in r["unidades"]},
        }
    return {
        "caso": nombre, "titulo": caso["tarjeta"]["titulo"], "pregunta": caso["pregunta"], "unidad": caso["unidad"],
        "rotulos": caso["rotulos"], "umbral": col.get("umbral"), "horizonte": col.get("horizonte"),
        "unidad_tiempo": col.get("unidad_tiempo"), "unidad_valor": col.get("unidad_valor"),
        "eje_tiempo": col.get("eje_tiempo"), "eje_valor": col.get("eje_valor"),
        "unidades": [{"id": k, "puntos": v} for k, v in unidades.items()],
        "lecturas": sum(len(v) for v in unidades.values()), "respuesta": respuesta,
    }


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
    est, bajo, alto, verdad = a_unidades(m), a_unidades(m - Z90 * desv), a_unidades(m + Z90 * desv), T["valor"][esc]
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


def main() -> None:
    inicio = time.time()
    base = mapa_con_rango(CASO, [])
    r = base["respuesta"]

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
        "terreno": ficha(CASO, base),
        "donde": {
            "candidatas": donde["candidatas"], "analisis_rehechos": donde["analisis_rehechos"],
            "lugares": lugares_con_valor(CASO, donde["candidatas"]), "resultados_por_lugar": espacial.RESULTADOS_POR_LUGAR,
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
        "archivos": {"mapa": archivo_de("leyes"), "series": archivo_de("flota")},
        "prueba_llm": prueba_llm(),
    }
    salida = Path(__file__).with_name("datos.js")
    salida.write_text("// Generado por pitch/deck/datos/generar.py. No editar a mano.\nwindow.KRYLOV_DATOS = "
                      + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
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
    for nombre, c in datos["series"].items():
        print(" ", nombre, "·", len(c["unidades"]), c["unidad"]["plural"], "·", c["lecturas"], "lecturas ·",
              "responde: " + c["respuesta"]["implementacion"] if c["respuesta"] else "su motor todavía no responde: solo datos")


if __name__ == "__main__":
    main()
