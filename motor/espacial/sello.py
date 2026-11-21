"""Valida la red de `espacial` y escribe su sello (skill `validar-motor`). **Sin nada entrenando en este computador.**

    uv run python -m motor.espacial.sello                  # completo: unos minutos
    uv run python -m motor.espacial.sello --ensayo         # todo el recorrido en chico, a una carpeta temporal

Hace, en orden, los chequeos de WORKPLAN.md 11.8 y deja `motor/artefactos/espacial/`:

1. Exporta el punto de guardado (`codificador.onnx`, `flujo.npz`, `pesos.pt`, `config.json`) y comprueba que
   onnxruntime y el flujo en NumPy coinciden con torch.
2. Calibración en terrenos simulados nuevos: SBC y cobertura del intervalo de 90%, en total y por grupos.
3. Comparación con el MCMC de referencia en terrenos simulados y en el archivo real: diferencia de medias en
   desviaciones estándar del posterior, y segundos por terreno. Las muestras del real quedan en `mcmc/` (plan B).
4. El método rápido de siempre (kriging con parámetros fijos): su cobertura en los mismos terrenos.
5. Examen con datos reales: cinco particiones que esconden 20% de las mediciones.
6. Latencia: un análisis completo, un lote de 500 grillas y «¿Dónde mido?»; y lo que tardaría rehacer esos
   análisis con el MCMC (segundos por análisis × análisis rehechos): la cifra de amortización del terreno.
7. `sello.json`, con `null` en lo que no se midió, y el veredicto: pasa o no pasa.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

from motor.comun.entrenar import cargar_punto
from motor.espacial import mcmc
from motor.espacial.exportar import ARTEFACTOS, PUNTO, exportar, red_desde_config
from motor.espacial.simular import Prior, simular
from motor.espacial.validar import sbc
from nucleo import casos, espacial

CASO = "terreno"


def comparar_con_mcmc(red, simulados: int, pasos: int, carpeta: Path) -> dict:
    """Red contra NUTS en terrenos simulados y en el archivo real. Guarda las muestras del real: es el plan B."""
    lote = simular(simulados, Prior(), torch.Generator().manual_seed(2026))
    real = espacial.canales_del_caso(CASO)
    # El MCMC recibe cuántas mediciones se promediaron en cada bloque (su ruido es τ²/cuenta); la red no lo ve.
    entradas = ([(f"simulado_{i:02d}", lote["canales"][i].numpy(), lote["cuenta"][i].numpy()) for i in range(simulados)]
                + [(CASO, real["canales"], real["cuenta"])])
    diferencias, segundos, r_hat, filas = [], [], [], []
    for clave, canales, cuenta in entradas:
        r = mcmc.correr(canales, cuenta, calentamiento=pasos, muestras=pasos, semilla=len(filas))
        mcmc.guardar(clave, r, carpeta / "mcmc")
        with torch.no_grad():
            de_la_red = red.flujo.muestrear(red(torch.from_numpy(canales[None]))[2], 1000)[:, 0].numpy()
        diferencia = np.abs(de_la_red.mean(0) - r["theta_est"].mean(0)) / r["theta_est"].std(0)
        razon_de_anchos = de_la_red.std(0) / r["theta_est"].std(0)
        diferencias.append(diferencia)
        segundos.append(r["segundos"])
        r_hat.append(float(np.nanmax(r["r_hat"])))
        filas.append({"clave": clave, "segundos": round(r["segundos"], 1), "r_hat_max": round(r_hat[-1], 3),
                      "diferencia_de_medias": [round(float(v), 2) for v in diferencia],
                      "razon_de_anchos": [round(float(v), 2) for v in razon_de_anchos]})
    diferencias = np.array(diferencias)
    return {"datasets": len(entradas), "s_por_dataset": round(float(np.mean(segundos)), 1), "diferencia_media": round(float(diferencias.mean()), 3),
            "diferencia_maxima": round(float(diferencias.max()), 3), "diferencia_en_el_real": round(float(diferencias[-1].mean()), 3),
            "r_hat_max": round(max(r_hat), 3), "por_dataset": filas}


def metodo_rapido(terrenos: int) -> float:
    """Cobertura del intervalo de 90% del kriging con parámetros fijos (el centro del prior), en bloques sin medición."""
    lote = simular(terrenos, Prior(), torch.Generator().manual_seed(12345))
    fijo = np.array([[Prior().log_alcance_media, 0.0, 0.0, 0.0, Prior().log_tau_media, 0.0, 0.0]])
    fila, columna = (m.reshape(-1).astype(float) for m in np.meshgrid(np.arange(32), np.arange(32), indexing="ij"))
    dentro, total = 0, 0
    for i in range(terrenos):
        canales = lote["canales"][i].numpy()
        medido = canales[1].reshape(-1) > 0
        media, varianza = espacial.kriging(fijo, fila[medido], columna[medido], canales[0].reshape(-1)[medido], canales[2].reshape(-1)[medido],
                                           fila, columna, canales[2].reshape(-1))
        error = np.abs(lote["campo"][i].numpy().reshape(-1) - media[0]) / np.sqrt(varianza[0])
        dentro += int((error[~medido] < 1.645).sum())
        total += int((~medido).sum())
    return round(dentro / total, 3)


def examen_en_particiones(particiones: int = 5) -> dict:
    """Esconder 20% de las mediciones reales y adivinarlas, con `particiones` semillas distintas."""
    caso = casos.cargar_caso(CASO)
    terreno = espacial.leer_terreno(caso)
    n, aciertos, total = len(terreno["x"]), 0, 0
    valor_t = espacial.transformar_valor(terreno["valor"], terreno["transformacion"])
    for semilla in range(particiones):
        escondidas = np.sort(np.random.default_rng(semilla).choice(n, size=round(0.2 * n), replace=False))
        visibles = np.setdiff1d(np.arange(n), escondidas)
        suma, cuenta = espacial.acumular_por_bloque(terreno["fila"][visibles], terreno["columna"][visibles], valor_t[visibles])
        canales, media, escala = espacial.canales_de(suma, cuenta, terreno["raiz_dist"])
        r = espacial.inferir(canales[None], cuenta[None], "red", CASO)
        f, c = terreno["fila"][escondidas], terreno["columna"][escondidas]
        desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + np.exp(2 * r["theta"].reshape(-1, 7)[:, 4]).mean())
        error = (valor_t[escondidas] - float(media)) / float(escala) - r["media"][0][f, c]
        aciertos += int((np.abs(error) < 1.645 * desv).sum())
        total += len(escondidas)
    return {"particiones": particiones, "mediciones_escondidas": total, "dentro_del_rango_de_90": aciertos, "cobertura": round(aciertos / total, 3)}


def latencias() -> dict:
    """Milisegundos de un análisis completo, de un lote de 500 grillas por onnxruntime y de «¿Dónde mido?» (la mejor de 3)."""
    from nucleo import api
    def mejor_de_3(f):
        tiempos = []
        for _ in range(3):
            inicio = time.perf_counter()
            salida = f()
            tiempos.append((time.perf_counter() - inicio) * 1000)
        return round(min(tiempos)), salida
    api.analizar(CASO)                                                    # carga la sesión de onnxruntime
    ms_analizar, respuesta = mejor_de_3(lambda: api.analizar(CASO))
    lote = simular(500, Prior(), torch.Generator().manual_seed(1))["canales"].numpy()
    ms_lote, _ = mejor_de_3(lambda: espacial.inferir(lote, np.ones((500, 32, 32)), "red", CASO))
    ms_donde, donde = mejor_de_3(lambda: api.donde_medir(CASO))
    assert "error" not in respuesta and "error" not in donde, (respuesta, donde)
    return {"analizar_ms": ms_analizar, "lote_500_ms": ms_lote, "donde_medir_ms": ms_donde, "analisis_rehechos": donde["analisis_rehechos"],
            "examen": respuesta["examen"], "factores": respuesta["factores"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--punto", type=Path, default=PUNTO)
    p.add_argument("--salida", type=Path, default=ARTEFACTOS)
    p.add_argument("--sbc", type=int, default=2000)
    p.add_argument("--simulados", type=int, default=5, help="terrenos simulados para comparar con el MCMC")
    p.add_argument("--ensayo", action="store_true", help="recorrido completo en chico, a una carpeta temporal: prueba el programa, no la red")
    a = p.parse_args()
    if a.ensayo:
        a.salida, a.sbc, a.simulados, pasos = Path(tempfile.mkdtemp(prefix="krylov_sello_")) / "espacial", 60, 1, 40
    else:
        pasos = 500

    estado = torch.load(a.punto, map_location="cpu", weights_only=False)
    red = red_desde_config(estado["config"])
    cargar_punto(a.punto, red)
    red.eval()
    config = {**estado["config"], "entrenada": True, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
              "minutos_entrenamiento": round(estado["segundos"] / 60, 1)}
    informe = {"exportacion": exportar(red, a.salida, config)}
    print("[1/6] exportado:", informe["exportacion"], flush=True)
    casos.ARTEFACTOS = a.salida.parent                                    # `nucleo` lee lo recién exportado
    os.environ["KRYLOV_MOTOR_ESPACIAL"] = "red"

    informe["sbc"] = sbc(red, a.sbc)
    print("[2/6] SBC:", informe["sbc"]["cobertura_90_theta_media"], informe["sbc"]["theta_por_grupo"], flush=True)
    informe["mcmc"] = comparar_con_mcmc(red, a.simulados, pasos, a.salida)
    print("[3/6] MCMC:", {k: v for k, v in informe["mcmc"].items() if k != "por_dataset"}, flush=True)
    informe["metodo_rapido_cobertura_90"] = metodo_rapido(min(a.sbc, 200))
    print("[4/6] método rápido:", informe["metodo_rapido_cobertura_90"], flush=True)
    informe["examen"] = examen_en_particiones()
    print("[5/6] examen:", informe["examen"], flush=True)
    informe["latencia"] = latencias()
    print("[6/6] latencia:", {k: v for k, v in informe["latencia"].items() if k.endswith("_ms") or k == "analisis_rehechos"}, flush=True)

    # Veredicto, con los umbrales de WORKPLAN.md 11.8.
    theta, grupos, mapa = informe["sbc"]["theta"], informe["sbc"]["theta_por_grupo"], informe["sbc"]["mapa"]
    coberturas = {**{f"θ · {k}": v["cobertura_90"] for k, v in grupos.items()}, **{f"mapa · {k}": v["cobertura_90"] for k, v in mapa.items() if isinstance(v, dict)}}
    peor = min((k for k in coberturas if "todos" not in k), key=coberturas.get)
    sbc_pasa = all(v["uniforme_al_99"] and abs(v["rango_medio"] - 0.5) < 0.03 for v in theta.values())
    cobertura_theta, cobertura_mapa = informe["sbc"]["cobertura_90_theta_media"], mapa["todos"]["cobertura_90"]
    criterios = {
        "sbc_sin_sesgo": sbc_pasa, "cobertura_theta_entre_85_y_95": 0.85 <= cobertura_theta <= 0.95,
        "cobertura_mapa_entre_85_y_95": 0.85 <= cobertura_mapa <= 0.95, "peor_grupo_sobre_80": coberturas[peor] >= 0.80,
        "mcmc_bajo_0_3": informe["mcmc"]["diferencia_media"] < 0.3, "analisis_bajo_1_s": informe["latencia"]["analizar_ms"] < 1000,
        "lote_500_bajo_2_s": informe["latencia"]["lote_500_ms"] < 2000,
    }
    # Sin la cabeza de flujo, la tarjeta igual puede salir con la cabeza de mapa: se informa aparte.
    mapa_pasa = criterios["cobertura_mapa_entre_85_y_95"] and criterios["lote_500_bajo_2_s"] and criterios["analisis_bajo_1_s"]
    analisis, lat = informe["latencia"]["analisis_rehechos"], informe["latencia"]
    sello = {
        "motor_id": "espacial", "implementacion": "red", "pasa": all(criterios.values()), "pasa_la_cabeza_de_mapa": mapa_pasa, "criterios": criterios,
        "simulaciones_entrenamiento": estado["datasets_simulados"], "entrenamiento_min": round(estado["segundos"] / 60),
        "casos_validacion": a.sbc, "cobertura_90": cobertura_mapa, "cobertura_90_parametros": cobertura_theta,
        "cobertura_90_peor_grupo": coberturas[peor], "peor_grupo": peor, "sbc_pasa": sbc_pasa,
        "cobertura_90_metodo_rapido": informe["metodo_rapido_cobertura_90"], "latencia_ms": lat["analizar_ms"], "latencia_lote_500_ms": lat["lote_500_ms"],
        "mcmc_datasets_comparados": informe["mcmc"]["datasets"], "mcmc_s_por_dataset": informe["mcmc"]["s_por_dataset"],
        "mcmc_diferencia_media": informe["mcmc"]["diferencia_media"],
        "amortizacion": {"que_se_compara": f"rehacer {analisis} análisis completos para «¿Dónde mido?»",
                         "mcmc_s": round(informe["mcmc"]["s_por_dataset"] * analisis, 1), "red_s": round(lat["donde_medir_ms"] / 1000, 2)},
        "examen_5_particiones": informe["examen"], "nube_malo_cae_fuera": None, "minutos_de_punta_a_punta": None,
        "fecha": dt.date.today().isoformat(), "maquina": "MacBook Air M4 16 GB", "ensayo": bool(a.ensayo),
        "limitaciones": ["Terrenos en dos dimensiones, llevados a una grilla de 32 por 32 bloques", "Entre 30 y 400 mediciones",
                         "Una sola tendencia: la raíz de la distancia a un río", "Covarianza exponencial con anisotropía geométrica",
                         "Dos mediciones en el mismo bloque se promedian"],
    }
    (a.salida / "sello.json").write_text(json.dumps(sello, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (a.salida / "validacion.json").write_text(json.dumps(informe, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in sello.items() if k != "limitaciones"}, indent=1, ensure_ascii=False))
    print(f"\n{'PASA' if sello['pasa'] else 'NO PASA'} · cabeza de mapa: {'pasa' if mapa_pasa else 'no pasa'} · {a.salida / 'sello.json'}")


if __name__ == "__main__":
    main()
