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
REAL = "terreno"          # datos reales públicos: lámina 2 y examen
POCOS = "leyes_pocos"     # el archivo que no alcanza: lámina 6
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
        "caso": nombre, "nx": m["nx"], "ny": m["ny"], "x0": m["x0"], "y0": m["y0"], "lado": m["lado"],
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
        "sello": sello,
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


if __name__ == "__main__":
    main()
