"""La red contra el MCMC de referencia, dataset por dataset: |diferencia de medias| de η en desviaciones del MCMC
(la misma medida que el sello de `espacial`), razón de desviaciones, y lo mismo para los λ continuos."""
import json, os, sys
from pathlib import Path
import numpy as np
AQUI = Path(__file__).resolve().parent
motor = sys.argv[1]
os.environ[f"KRYLOV_MOTOR_{motor.upper()}"] = "red"
from nucleo import series
from motor.comun.validacion import comparar_posteriores
r = series.red(motor)
filas = []
for ruta in sorted((AQUI / "salida" / motor).glob("*.npz")):
    z = np.load(ruta, allow_pickle=True)
    s_d, s_j = series.resumir(r, z["x"], z["mascara"], z["cov"], z["tam"])
    eta, lam = series.muestrear_posterior(r, s_d, s_j, m=2000, l=1)
    lam = lam[:, 0]
    d_eta, raz_eta = comparar_posteriores(eta, z["eta"])
    dl = z["lam"].shape[-1] - (1 if motor == "deformacion" else 0)
    d_lam, raz_lam = comparar_posteriores(lam[..., :dl].reshape(len(lam), -1), z["lam"][..., :dl].reshape(len(z["lam"]), -1))
    fila = {"clave": ruta.stem, "unidades": int(z["lam"].shape[1]), "segundos": round(float(z["segundos"]), 1),
            "r_hat_max": round(float(np.nanmax(z["r_hat"])), 3), "divergencias": int(z["divergencias"]),
            "dif_eta": [round(float(v), 2) for v in d_eta], "dif_eta_media": round(float(d_eta.mean()), 3),
            "razon_desv_eta": [round(float(v), 2) for v in raz_eta], "dif_lam_media": round(float(np.nanmean(d_lam)), 3),
            "razon_desv_lam_mediana": round(float(np.nanmedian(raz_lam)), 2)}
    if motor == "deformacion":
        fila["z_red"] = [round(float(v), 2) for v in lam[..., -1].mean(0)]; fila["z_mcmc"] = [round(float(v), 2) for v in z["lam"][..., -1].mean(0)]
    filas.append(fila); print(json.dumps(fila))
conv = [f for f in filas if f["r_hat_max"] <= 1.05]
print(json.dumps({"motor": motor, "mcmc_datasets_comparados": len(filas), "convergieron": len(conv),
                  "mcmc_s_por_dataset": round(float(np.mean([f["segundos"] for f in filas])), 1) if filas else None,
                  "mcmc_diferencia_media": round(float(np.mean([f["dif_eta_media"] for f in filas])), 3) if filas else None,
                  "mcmc_r_hat_max": max(f["r_hat_max"] for f in filas) if filas else None}))
