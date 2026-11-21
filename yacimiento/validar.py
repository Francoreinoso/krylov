"""Valida la red de `yacimiento` sin MCMC y escribe su sello (`yacimiento/artefactos/sello.json`).

1. En yacimientos simulados nuevos: cobertura del rango de 90% de la ley de cada bloque (cabeza de mapa), en total,
   en bloques sin compósito y por tramos del número de sondajes; error contra la tendencia lineal sola; y calibración
   basada en simulación (SBC) de los 15 parámetros (cabeza de flujo): χ² de uniformidad del rango, cobertura y recuperación.
2. Latencia de un análisis completo (16.384 bloques y 200 muestras de θ), en el procesador.
3. El yacimiento del demo: examen contra la verdad escondida y la decisión por bloque (`nucleo/decision.py`).
4. Si existe `artefactos/mcmc/*.npz`, la comparación con el MCMC de referencia (`comparar`).

    uv run python -m yacimiento.validar [--datasets 400]
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from scipy.stats import norm

from nucleo import decision
from yacimiento import modelo as M
from yacimiento.red import RedYacimiento

ARTEFACTOS = Path("yacimiento/artefactos")
CASO = {"ley_de_corte_pct": 0.5, "falso_si": 40000.0, "falso_no": 90000.0}      # supuestos del demo (pitch/CIFRAS.md, K-71 a K-73)
Z90 = 1.6449


def cargar(dispositivo: str = "cpu") -> tuple[RedYacimiento, dict]:
    estado = torch.load("yacimiento/checkpoints/ultimo.pt", map_location="cpu", weights_only=False)
    red = RedYacimiento()
    red.load_state_dict(estado["modulo"])
    return red.eval().to(dispositivo), {k: estado[k] for k in ("pasos", "datasets_simulados", "segundos")}


@torch.no_grad()
def en_simulaciones(red: RedYacimiento, datasets: int, dispositivo: str, lote: int = 20, muestras: int = 99, semilla: int = 12345) -> dict:
    gen = torch.Generator().manual_seed(semilla)
    dentro, dentro_sin, n_sond, err_red, err_lin, rangos, verdad_t, media_t, z_todos = [], [], [], [], [], [], [], [], []
    for _ in range(math.ceil(datasets / lote)):
        sim = {k: v.to(dispositivo) for k, v in M.simular(lote, gen).items()}
        p = M.preparar(sim["y"], sim["mascara"], sim["cov"])
        media, log_desv, ctx = red(p["x"], p["resumen"], p["tendencia"])
        z = (sim["verdad"] - media) * torch.exp(-log_desv)
        ok = (z.abs() < Z90).float()
        sin = 1.0 - sim["mascara"]
        dentro.append(ok.mean((1, 2, 3)).cpu()); dentro_sin.append(((ok * sin).sum((1, 2, 3)) / sin.sum((1, 2, 3))).cpu())
        n_sond.append(sim["mascara"][:, :, :, 0].sum((1, 2)).cpu())                      # collares: bloques de superficie con compósito
        err_red.append(((sim["verdad"] - media) ** 2).mean((1, 2, 3)).cpu()); err_lin.append(((sim["verdad"] - p["tendencia"]) ** 2).mean((1, 2, 3)).cpu())
        theta = red.flujo.muestrear(ctx, muestras)                                        # (m, B, 15)
        rangos.append((theta < sim["theta"][None]).sum(0).cpu()); verdad_t.append(sim["theta"].cpu()); media_t.append(theta.mean(0).cpu())
        z_todos.append(z.flatten()[:: 97].cpu())
    dentro, dentro_sin, n_sond, err_red, err_lin = (torch.cat(v).numpy() for v in (dentro, dentro_sin, n_sond, err_red, err_lin))
    rangos, verdad_t, media_t = (torch.cat(v).numpy() for v in (rangos, verdad_t, media_t))
    z_todos = torch.cat(z_todos).numpy()
    por_tramo = []
    for nombre, lo, hi in (("15 a 24 sondajes", 0, 24), ("25 a 38 sondajes", 25, 38), ("39 a 60 sondajes", 39, 99)):
        en = (n_sond >= lo) & (n_sond <= hi)
        if en.sum() >= 20:
            por_tramo.append({"tramo": nombre, "datasets": int(en.sum()), "cobertura_90_mapa": round(float(dentro[en].mean()), 4)})
    parametros = {}
    for i, nombre in enumerate(M.NOMBRES_THETA):
        cajas = np.histogram(rangos[:, i], bins=10, range=(0, muestras + 1))[0]
        esperado = len(rangos) / 10
        parametros[nombre] = {"chi2_uniformidad": round(float(((cajas - esperado) ** 2 / esperado).sum()), 2),
                              "rango_medio": round(float(rangos[:, i].mean() / muestras), 4),
                              "cobertura_90": round(float(((rangos[:, i] >= 5) & (rangos[:, i] <= 94)).mean()), 4),
                              "recuperacion": round(float(np.corrcoef(verdad_t[:, i], media_t[:, i])[0, 1]), 3)}
    return {"datasets": int(len(dentro)), "cobertura_90_mapa": round(float(dentro.mean()), 4), "cobertura_90_mapa_sin_composito": round(float(dentro_sin.mean()), 4),
            "cobertura_50_mapa": round(float((np.abs(z_todos) < 0.6745).mean()), 4), "por_tramo": por_tramo,
            "error_cuadratico_red": round(float(err_red.mean()), 4), "error_cuadratico_tendencia_lineal": round(float(err_lin.mean()), 4),
            "cobertura_90_parametros": round(float(np.mean([v["cobertura_90"] for v in parametros.values()])), 4),
            "sbc_chi2_max": max(v["chi2_uniformidad"] for v in parametros.values()),
            "sbc_pasa": all(v["chi2_uniformidad"] < 21.67 and abs(v["rango_medio"] - 0.5) < 0.03 for v in parametros.values()),   # χ²(9) al 1%, como D-32
            "parametros": parametros}


@torch.no_grad()
def demo(red: RedYacimiento) -> tuple[dict, dict]:
    """La respuesta de la red para el yacimiento del demo, su latencia y el examen contra la verdad escondida."""
    z = np.load("yacimiento/datos/demo.npz")
    t = {k: torch.from_numpy(z[k])[None] for k in ("y", "mascara", "cov")}
    red.responder(t["y"], t["mascara"], t["cov"], 200)                                    # en frío no se cronometra
    tiempos = []
    for _ in range(5):
        inicio = time.perf_counter(); r = red.responder(t["y"], t["mascara"], t["cov"], 200); tiempos.append(time.perf_counter() - inicio)
    media, desv = r["media"][0].numpy().astype(np.float64), r["desv"][0].numpy().astype(np.float64)
    log_corte = math.log(CASO["ley_de_corte_pct"])
    p = norm.sf((log_corte - media) / desv)
    d = decision.decidir_espacial(p, CASO["falso_si"], CASO["falso_no"])
    es_mineral = z["verdad"] > log_corte
    examen = {estado: {"bloques": int((d["estado"] == estado).sum()), "eran_mineral": int(es_mineral[d["estado"] == estado].sum())} for estado in decision.ESTADOS}
    tramos = []
    for lo, hi in ((0, 0.1), (0.1, 0.5), (0.5, 0.9), (0.9, 1.01)):
        en = (p >= lo) & (p < hi)
        if en.any():
            tramos.append({"dijimos": round(float(p[en].mean()), 3), "paso": round(float(es_mineral[en].mean()), 3), "n": int(en.sum())})
    resumen = {"compositos": int(z["mascara"].sum()), "bloques": int(p.size), "latencia_ms": round(1000 * float(np.median(tiempos))),
               "colores": decision.resumen_colores(d["estado"]), "costo_de_no_saber": round(float(d["duda"].sum())),
               "cobertura_90_demo": round(float((np.abs((z["verdad"] - media) / desv) < Z90).mean()), 4), "examen": examen, "tramos": tramos, "caso": CASO}
    return resumen, {"media": media, "desv": desv, "p": p, "estado": d["estado"], "duda": d["duda"], "theta": r["theta"][:, 0].numpy()}


def comparar(red: RedYacimiento) -> dict | None:
    """La red contra el MCMC de referencia en cada `artefactos/mcmc/*.npz`: parámetros, mapa y decisiones."""
    filas = []
    for ruta in sorted((ARTEFACTOS / "mcmc").glob("*.npz")):
        m = np.load(ruta)
        z = np.load("yacimiento/datos/demo.npz") if ruta.stem == "demo" else m
        t = {k: torch.from_numpy(np.asarray(z[k], dtype=np.float32))[None] for k in ("y", "mascara", "cov")}
        with torch.no_grad():
            r = red.responder(t["y"], t["mascara"], t["cov"], 2000)
        theta, media, desv = r["theta"][:, 0].numpy(), r["media"][0].numpy(), r["desv"][0].numpy()
        dif = np.abs(theta.mean(0) - m["theta"].mean(0)) / m["theta"].std(0)
        log_corte = math.log(CASO["ley_de_corte_pct"])
        p_red = norm.sf((log_corte - media) / desv)
        p_mcmc = norm.sf((log_corte - m["medias"]) / m["desvs"]).mean(0).reshape(media.shape)
        e_red = decision.decidir_espacial(p_red, CASO["falso_si"], CASO["falso_no"])["estado"]
        e_mcmc = decision.decidir_espacial(p_mcmc, CASO["falso_si"], CASO["falso_no"])["estado"]
        filas.append({"clave": ruta.stem, "segundos_nuts": round(float(m["segundos"]), 1), "segundos_mapa": round(float(m["segundos_mapa"]), 1),
                      "r_hat_max": round(float(m["r_hat"].max()), 3), "divergencias": int(m["divergencias"]),
                      "dif_theta_media": round(float(dif.mean()), 3), "dif_theta_max": round(float(dif.max()), 3),
                      "parametro_de_la_max": M.NOMBRES_THETA[int(dif.argmax())],
                      "razon_desv_theta_mediana": round(float(np.median(theta.std(0) / m["theta"].std(0))), 2),
                      "mapa_dif_media_en_desv": round(float(np.mean(np.abs(media - m["media"]) / m["desv"])), 3),
                      "mapa_razon_desv_mediana": round(float(np.median(desv / m["desv"])), 3),
                      "mapa_dif_p_media": round(float(np.abs(p_red - p_mcmc).mean()), 4),
                      "bloques_con_la_misma_decision": round(float((e_red == e_mcmc).mean()), 4)})
    if not filas:
        return None
    return {"datasets": filas, "mcmc_datasets_comparados": len(filas), "mcmc_s_por_dataset": round(float(np.mean([f["segundos_nuts"] + f["segundos_mapa"] for f in filas])), 1),
            "mcmc_diferencia_media": round(float(np.mean([f["dif_theta_media"] for f in filas])), 3), "mcmc_r_hat_max": max(f["r_hat_max"] for f in filas)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasets", type=int, default=400)
    p.add_argument("--dispositivo", default="mps")
    a = p.parse_args()
    red, progreso = cargar(a.dispositivo)
    sims = en_simulaciones(red, a.datasets, a.dispositivo)
    red = red.to("cpu")
    del_demo, _ = demo(red)
    mcmc = comparar(red)
    criterios = {"cobertura_mapa_entre_85_y_95": 0.85 <= sims["cobertura_90_mapa"] <= 0.95,
                 "peor_tramo_sobre_80": min(t["cobertura_90_mapa"] for t in sims["por_tramo"]) >= 0.80 if sims["por_tramo"] else False,
                 "cobertura_parametros_entre_85_y_95": 0.85 <= sims["cobertura_90_parametros"] <= 0.95,
                 "sbc_sin_sesgo": bool(sims["sbc_pasa"]), "analisis_bajo_1_s": del_demo["latencia_ms"] < 1000}
    if mcmc:
        criterios["mcmc_bajo_0_3"] = mcmc["mcmc_diferencia_media"] < 0.3
    sello = {"motor_id": "yacimiento", "pasa": all(criterios.values()), "criterios": criterios,
             "simulaciones_entrenamiento": int(progreso["datasets_simulados"]), "entrenamiento_min": round(progreso["segundos"] / 60),
             "casos_validacion": sims["datasets"], "validacion": sims, "demo": del_demo, "mcmc": mcmc,
             "fecha": time.strftime("%Y-%m-%d"), "hora": time.strftime("%H:%M"),
             "limitaciones": ["Motor fuera del producto congelado a las 18:00: no tiene tarjeta en la app.",
                              "Datos simulados con el mismo modelo; no se probó con sondajes reales.",
                              "La cabeza de mapa entrega el predictivo marginal de cada bloque como una normal; no entrega correlación entre bloques."]}
    ARTEFACTOS.mkdir(parents=True, exist_ok=True)
    (ARTEFACTOS / "sello.json").write_text(json.dumps(sello, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    resumen = {k: sims[k] for k in sims if k != "parametros"}
    print(json.dumps({"pasa": sello["pasa"], "criterios": criterios, **resumen, "demo": del_demo, "mcmc": mcmc}, indent=1, ensure_ascii=False))
    print({k: (v["chi2_uniformidad"], v["rango_medio"], v["cobertura_90"], v["recuperacion"]) for k, v in sims["parametros"].items()})


if __name__ == "__main__":
    main()
