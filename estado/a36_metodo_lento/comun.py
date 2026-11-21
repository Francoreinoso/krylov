"""Lo común del MCMC de referencia (NUTS, NumPyro) de los motores de series: correr, diagnosticar, guardar.

Cada motor aporta un módulo con: MOTOR_ID, modelo(**datos), inicial (dict o None), datos_del_caso(nombre),
datos_simulados(i) y a_eta_lam(muestras, datos) → (eta (n, d), lam (n, U, d_local)), en el mismo espacio sin
restricciones y el mismo orden que NOMBRES_ETA y NOMBRES_LAM de la red.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import jax
import numpy as np
import numpyro
from numpyro.infer import MCMC, NUTS, init_to_median, init_to_value

numpyro.enable_x64()
SALIDA = Path(__file__).resolve().parent / "salida"


def correr(mod, datos: dict, calentamiento: int = 500, muestras: int = 500, cadenas: int = 4, semilla: int = 0) -> dict:
    inicial = getattr(mod, "inicial", None)
    estrategia = init_to_value(values=inicial(datos)) if inicial else init_to_median(num_samples=15)
    nucleo = NUTS(mod.modelo, init_strategy=estrategia, target_accept_prob=getattr(mod, "ACEPTACION", 0.9),
                  max_tree_depth=getattr(mod, "PROFUNDIDAD", 10))
    mcmc = MCMC(nucleo, num_warmup=calentamiento, num_samples=muestras, num_chains=cadenas, chain_method="vectorized", progress_bar=False)
    inicio = time.time()
    mcmc.run(jax.random.PRNGKey(semilla), **datos, extra_fields=("diverging",))
    por_cadena = {k: np.asarray(v) for k, v in mcmc.get_samples(group_by_chain=True).items()}
    segundos = time.time() - inicio
    planas = {k: v.reshape((-1,) + v.shape[2:]) for k, v in por_cadena.items()}
    eta, lam = mod.a_eta_lam(planas, datos)
    eta_c = eta.reshape((cadenas, muestras) + eta.shape[1:])
    continuas = lam[..., : getattr(mod, "LAM_CONTINUAS", lam.shape[-1])]
    lam_c = continuas.reshape((cadenas, muestras) + continuas.shape[1:])
    d = numpyro.diagnostics.summary({"eta": eta_c, "lam": lam_c}, group_by_chain=True)
    r_hat = np.concatenate([np.ravel(d["eta"]["r_hat"]), np.ravel(d["lam"]["r_hat"])])
    n_eff = np.concatenate([np.ravel(d["eta"]["n_eff"]), np.ravel(d["lam"]["n_eff"])])
    return {"eta": eta, "lam": lam, "segundos": segundos, "r_hat": r_hat, "n_eff": n_eff,
            "r_hat_eta": np.ravel(d["eta"]["r_hat"]), "divergencias": int(np.asarray(mcmc.get_extra_fields()["diverging"]).sum())}


def guardar(motor_id: str, clave: str, r: dict, **extra) -> Path:
    carpeta = SALIDA / motor_id
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{clave}.npz"
    np.savez(ruta, eta=r["eta"].astype(np.float32), lam=r["lam"].astype(np.float32), segundos=r["segundos"], r_hat=r["r_hat"],
             r_hat_eta=r["r_hat_eta"], n_eff=r["n_eff"], divergencias=r["divergencias"], **extra)
    return ruta


def principal(mod) -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--caso", default=None)
    p.add_argument("--simulado", type=int, default=None, help="índice del dataset simulado (semilla [2026, i])")
    p.add_argument("--muestras", type=int, default=500)
    p.add_argument("--calentamiento", type=int, default=500)
    p.add_argument("--cadenas", type=int, default=4)
    p.add_argument("--sin-guardar", action="store_true")
    a = p.parse_args()
    if a.caso:
        clave, (datos, tensores, extra) = a.caso, mod.datos_del_caso(a.caso)
    else:
        clave, (datos, tensores, extra) = f"simulado_{a.simulado:02d}", mod.datos_simulados(a.simulado)
    r = correr(mod, datos, a.calentamiento, a.muestras, a.cadenas, semilla=a.simulado or 0)
    linea = {"motor": mod.MOTOR_ID, "clave": clave, "segundos": round(r["segundos"], 1), "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3),
             "r_hat_max_eta": round(float(np.nanmax(r["r_hat_eta"])), 3), "n_eff_min": round(float(np.nanmin(r["n_eff"]))),
             "divergencias": r["divergencias"], "unidades": int(r["lam"].shape[1]),
             "r_hat_eta": [round(float(v), 3) for v in r["r_hat_eta"]]}
    if "eta_verdadero" in extra:      # dónde cae la verdad dentro del posterior de η (rango de 0 a 1)
        linea["rango_verdad_eta"] = [round(float((r["eta"][:, i] < extra["eta_verdadero"][i]).mean()), 2) for i in range(r["eta"].shape[1])]
    if not a.sin_guardar:
        linea["ruta"] = str(guardar(mod.MOTOR_ID, clave, r, **tensores, **extra))
    print(json.dumps(linea))
