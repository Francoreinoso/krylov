"""Exporta a `pitch/deck/datos/datos.js` los datos que anima el deck. No toca nada fuera de `pitch/deck/`.

Desde la raíz del repositorio:

    uv run python pitch/deck/datos/generar.py

Todo sale del repositorio, con la red del motor `espacial` (validada, sello de las 09:39):

- `terreno`     api.analizar("terreno"): el mapa real (155 mediciones de zinc junto al río Mosa).
                El rango creíble por bloque (5% a 95%) no viene en la respuesta de la API: se calcula
                aquí con las mismas funciones de `nucleo/espacial.py` (media y desviación de la cabeza
                de mapa), y se comprueba que la media coincide con la de la API.
- `donde`       api.donde_medir("terreno"): los tres lugares donde medir vale más. Además, `lugares`: todos los
                lugares candidatos con su valor, repitiendo el cálculo de `nucleo/espacial.donde_medir` (se comprueba
                que los tres mejores coinciden con los de la API).
- `mediciones`  api.analizar("terreno", mediciones=[...]) para cada pin y cada resultado posible
                (bajo, medio, alto): el mapa rehecho por la red. En el deck se anima este resultado.
- `nube`        api.nube("rotacion_malo") y la misma con la corrección `quitar_factor:fecha_salida`.
- `simulados`   256 terrenos del simulador `motor/espacial/simular.py` (semilla 2026), el campo
                verdadero de cada uno llevado a 0..255. En pantalla van rotulados «terrenos simulados».
- `sello`       copia de `motor/artefactos/espacial/sello.json`.

Tarda unos segundos. Si en este computador hay un entrenamiento corriendo, igual se puede correr.
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

SEMILLA = 2026
TERRENOS_SIMULADOS = 256
Z90 = 1.645
ESTADO = {"no_actuar": 0, "en_duda": 1, "actuar": 2}


def mapa_con_rango(mediciones: list[dict]) -> dict:
    """La respuesta de la API más el rango creíble de 90% por bloque, en mg/kg."""
    r = api.analizar("terreno", mediciones=mediciones)
    assert r["implementacion"] == "red" and not r["precalculado"], "el mapa tiene que salir de la red"
    m = r["mapa"]

    caso = casos.cargar_caso("terreno")
    terreno = espacial.leer_terreno(caso, mediciones)
    canales, media, escala = espacial.canales_de(terreno["suma"], terreno["cuenta"], terreno["raiz_dist"])
    inf = espacial.inferir(canales[None], terreno["cuenta"][None], "red", espacial._clave(caso, False))
    mu, desv = inf["media"][0], inf["desviacion"][0]

    def a_unidades(v):
        return espacial._a_unidades_del_caso(v, float(media), float(escala), terreno["transformacion"]).reshape(-1)

    centro, bajo, alto = a_unidades(mu), a_unidades(mu - Z90 * desv), a_unidades(mu + Z90 * desv)
    dentro = [i for i, v in enumerate(m["media"]) if v is not None]
    assert np.allclose([m["media"][i] for i in dentro], centro[dentro], atol=0.06), "la media no coincide con la de la API"

    costos = {k: v["valor"] for k, v in r["costos"].items()}
    p = np.array([m["p"][i] for i in dentro])
    estado = decision.decidir_espacial(p, costos["falso_si"], costos["falso_no"])["estado"]
    return {
        "respuesta": r, "dentro": dentro,
        "media": [round(float(centro[i])) for i in dentro],
        "bajo": [round(float(bajo[i])) for i in dentro],
        "alto": [round(float(alto[i])) for i in dentro],
        "p": [m["p"][i] for i in dentro],
        "estado": [ESTADO[e] for e in estado],
        "colores": r["resumen_colores"],
        "costo_de_no_saber": r["costo_de_no_saber"]["valor"],
    }


def capa(c: dict) -> dict:
    return {k: c[k] for k in ("media", "bajo", "alto", "p", "estado", "colores", "costo_de_no_saber")}


def lugares_con_valor(candidatas: list[dict]) -> list[dict]:
    """Todos los lugares candidatos de «¿Dónde mido?» con lo que vale medir en cada uno.

    La API entrega solo los tres mejores. Aquí se repite el cálculo de `nucleo/espacial.donde_medir`
    con sus mismas funciones, y se comprueba que los tres mejores coinciden con los de la API.
    """
    caso = casos.cargar_caso("terreno")
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


def orilla_del_rio() -> list[list[float]]:
    """Celdas de la grilla fina pegadas al río (distancia 0): se dibujan como la orilla."""
    with open(RAIZ / "datos/demo/terreno_grilla.csv") as f:
        return [[float(fila["x"]), float(fila["y"])] for fila in csv.DictReader(f) if float(fila["dist"]) == 0.0]


def terrenos_simulados() -> str:
    import torch

    from motor.espacial.simular import Prior, simular

    gen = torch.Generator().manual_seed(SEMILLA)
    campo = simular(TERRENOS_SIMULADOS, Prior(), gen)["campo"].numpy()
    lo = np.quantile(campo, 0.01, axis=(1, 2), keepdims=True)
    hi = np.quantile(campo, 0.99, axis=(1, 2), keepdims=True)
    gris = np.clip((campo - lo) / np.maximum(hi - lo, 1e-6), 0, 1)
    return base64.b64encode((gris * 255).round().astype(np.uint8).tobytes()).decode()


def main() -> None:
    inicio = time.time()
    base = mapa_con_rango([])
    r, m = base["respuesta"], base["respuesta"]["mapa"]

    donde = api.donde_medir("terreno")
    assert donde["implementacion"] == "red" and not donde["precalculado"]

    mediciones = {}
    for c in donde["candidatas"]:
        mediciones[c["etiqueta"]] = {
            nivel: capa(mapa_con_rango([{"x": c["x"], "y": c["y"], "valor": valor}]))
            for nivel, valor in c["resultados_posibles"].items()
        }

    malo, corregido = api.nube("rotacion_malo"), api.nube("rotacion_malo", ["quitar_factor:fecha_salida"])
    sello = json.loads((RAIZ / "motor/artefactos/espacial/sello.json").read_text())

    datos = {
        "generado": time.strftime("%Y-%m-%d %H:%M"),
        "comando": "uv run python pitch/deck/datos/generar.py",
        "terreno": {
            "nx": m["nx"], "ny": m["ny"], "x0": m["x0"], "y0": m["y0"], "lado": m["lado"],
            "umbral": m["umbral"], "unidad_valor": m["unidad_valor"], "punto_de_corte": r["punto_de_corte"],
            "dentro": base["dentro"], **capa(base),
            "puntos": [[p["x"], p["y"], p["valor"]] for p in m["puntos"]],
            "orilla": orilla_del_rio(),
            "costos": {k: v["valor"] for k, v in r["costos"].items()},
            "rotulos": r["rotulos"], "unidad": r["unidad"], "examen": r["examen"]["tramos"][0], "origen_datos": r["origen_datos"],
            "umbral_de_duda": decision.UMBRAL_DE_DUDA,
            "implementacion": r["implementacion"], "precalculado": r["precalculado"],
        },
        "donde": {
            "candidatas": donde["candidatas"], "analisis_rehechos": donde["analisis_rehechos"],
            "lugares": lugares_con_valor(donde["candidatas"]), "resultados_por_lugar": espacial.RESULTADOS_POR_LUGAR,
            "implementacion": donde["implementacion"], "precalculado": donde["precalculado"],
        },
        "mediciones": mediciones,
        "nube": {
            "n_simulaciones": malo["n_simulaciones"], "ejes": malo["ejes"], "puntos": malo["puntos"],
            "malo": malo["archivo"], "motivo": malo["detectores"]["ejes_con_nombre"]["motivo"],
            "corregido": corregido["archivo"],
        },
        "simulados": {"n": TERRENOS_SIMULADOS, "lado": 32, "semilla": SEMILLA, "b64": terrenos_simulados()},
        "sello": sello,
    }
    salida = Path(__file__).with_name("datos.js")
    salida.write_text("// Generado por pitch/deck/datos/generar.py. No editar a mano.\nwindow.KRYLOV_DATOS = "
                      + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"{salida.relative_to(RAIZ)}: {salida.stat().st_size / 1e3:.0f} kB en {time.time() - inicio:.1f} s")
    print("colores", base["colores"], "· cuesta no saber", base["costo_de_no_saber"])
    for c in donde["candidatas"]:
        print(c["etiqueta"], c["valor_de_medir"], {k: (v["colores"], v["costo_de_no_saber"]) for k, v in mediciones[c["etiqueta"]].items()})
    print("lugares candidatos:", len(datos["donde"]["lugares"]), "×", datos["donde"]["resultados_por_lugar"], "resultados =",
          len(datos["donde"]["lugares"]) * datos["donde"]["resultados_por_lugar"], "análisis · API:", donde["analisis_rehechos"])
    print("nube", malo["archivo"], "→", corregido["archivo"], "·", datos["nube"]["motivo"])


if __name__ == "__main__":
    main()
