"""Deja en `pitch/deck/datos/yacimiento.js` lo que muestra `pitch/deck/yacimiento.html`: la respuesta de la red para el
yacimiento del demo, la del método lento si ya se corrió, la verdad escondida y los números medidos (del sello).

    uv run python -m yacimiento.exportar_deck
"""
from __future__ import annotations

import base64
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

from nucleo import decision
from yacimiento import modelo as M
from yacimiento.validar import ARTEFACTOS, CASO, cargar, demo

SALIDA = Path("pitch/deck/datos/yacimiento.js")
LEY_MIN, LEY_MAX = -3.0, 1.5           # log de % de cobre, para guardar en un byte
DESV_MAX = 1.5


def _b64(a: np.ndarray, lo: float, hi: float) -> str:
    return base64.b64encode(np.clip(np.round((a - lo) / (hi - lo) * 255), 0, 255).astype(np.uint8).tobytes()).decode()


def main() -> None:
    red, progreso = cargar("cpu")
    resumen, r = demo(red)
    z = np.load("yacimiento/datos/demo.npz")
    log_corte = math.log(CASO["ley_de_corte_pct"])
    es_mineral = z["verdad"] > log_corte
    decidido = r["estado"] != "en_duda"
    acierto = float(((r["estado"] == "actuar") == es_mineral)[decidido].mean())
    datos = {"dim": [M.NX, M.NY, M.NZ], "ley_min": LEY_MIN, "ley_max": LEY_MAX, "desv_max": DESV_MAX, "caso": CASO,
             "punto_de_corte": decision.punto_de_corte(CASO["falso_si"], CASO["falso_no"]), "umbral_de_duda": decision.UMBRAL_DE_DUDA,
             "red": {"media": _b64(r["media"], LEY_MIN, LEY_MAX), "desv": _b64(r["desv"], 0, DESV_MAX), "p": _b64(r["p"], 0, 1)},
             "verdad": _b64(z["verdad"], LEY_MIN, LEY_MAX), "mascara": _b64(z["mascara"], 0, 1), "y": _b64(z["y"], LEY_MIN, LEY_MAX),
             "numeros": {"compositos": resumen["compositos"], "bloques": resumen["bloques"], "covariables": M.N_COV, "latencia_ms": resumen["latencia_ms"],
                         "simulaciones": int(progreso["datasets_simulados"]), "entrenamiento_min": round(progreso["segundos"] / 60),
                         "colores": resumen["colores"], "costo_de_no_saber": resumen["costo_de_no_saber"],
                         "acierto_decididos": round(acierto, 3), "decididos": int(decidido.sum())}, "mcmc": None}
    ruta = ARTEFACTOS / "mcmc" / "demo.npz"
    if not ruta.exists():
        ruta = ARTEFACTOS / "mcmc_demo.npz"                             # la copia liviana versionada
    if ruta.exists():
        m = np.load(ruta)
        p = norm.sf((log_corte - m["medias"]) / m["desvs"]).mean(0).reshape(M.NX, M.NY, M.NZ)
        e = decision.decidir_espacial(p, CASO["falso_si"], CASO["falso_no"])["estado"]
        datos["mcmc"] = {"media": _b64(m["media"], LEY_MIN, LEY_MAX), "desv": _b64(m["desv"], 0, DESV_MAX), "p": _b64(p, 0, 1),
                         "segundos": round(float(m["segundos"]) + float(m["segundos_mapa"])), "r_hat_max": round(float(m["r_hat"].max()), 3),
                         "misma_decision": round(float((e == r["estado"]).mean()), 3)}
    SALIDA.write_text("// Generado por yacimiento/exportar_deck.py. Yacimiento SIMULADO; no editar a mano.\nwindow.YACIMIENTO = "
                      + json.dumps(datos, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(json.dumps(datos["numeros"], ensure_ascii=False), "mcmc:", {k: v for k, v in (datos["mcmc"] or {}).items() if k not in ("media", "desv", "p")})


if __name__ == "__main__":
    main()
