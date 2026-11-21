# El mismo examen que se toma Krylov (nucleo/espacial._examen): esconder 20% de las muestras del banco de `leyes`,
# responder con el resto y ver cuántas caen dentro del rango de 90%. Aquí se guarda, además, lo que dijo para cada una.
import csv, json, sys, time
import numpy as np
from nucleo import casos, espacial
from nucleo.espacial import (leer_terreno, transformar_valor, acumular_por_bloque, canales_de, inferir, _clave, NOMBRES_THETA)
salida = sys.argv[1]            # carpeta donde dejar a/, b/ y krylov.csv
caso = casos.cargar_caso("leyes")
T = leer_terreno(caso, (), False)
n = len(T["x"])
esc = np.sort(np.random.default_rng(0).choice(n, size=max(1, round(0.2 * n)), replace=False))
vis = np.setdiff1d(np.arange(n), esc)
valor_t = transformar_valor(T["valor"], T["transformacion"])
t0 = time.perf_counter()
suma, cuenta = acumular_por_bloque(T["fila"][vis], T["columna"][vis], valor_t[vis])
canales, media, escala = canales_de(suma, cuenta, T["raiz_dist"])
r = inferir(canales[None], cuenta[None], "red", _clave(caso, False))
ms = (time.perf_counter() - t0) * 1000
theta = r["theta"].reshape(-1, len(NOMBRES_THETA))
f, c = T["fila"][esc], T["columna"][esc]
desv = np.sqrt(r["desviacion"][0][f, c] ** 2 + np.exp(2 * theta[:, 4]).mean())
m = r["media"][0][f, c]
a_ppm = lambda z: np.exp(z * float(escala) + float(media))          # la transformación del caso es log
pred, bajo, alto = a_ppm(m), a_ppm(m - 1.645 * desv), a_ppm(m + 1.645 * desv)
verdad = T["valor"][esc]
dentro = int(((verdad >= bajo) & (verdad <= alto)).sum())
for carpeta in ("a", "b"):
    with open(f"{salida}/{carpeta}/muestras.csv", "w", newline="") as g:
        w = csv.writer(g); w.writerow(["pozo", "x", "y", "as_ppm"])
        for i in vis: w.writerow([f"P-{i + 1:03d}", T["x"][i], T["y"][i], int(T["valor"][i])])
    with open(f"{salida}/{carpeta}/puntos.csv", "w", newline="") as g:
        w = csv.writer(g); w.writerow(["pozo", "x", "y"])
        for i in esc: w.writerow([f"P-{i + 1:03d}", T["x"][i], T["y"][i]])
with open(f"{salida}/krylov.csv", "w", newline="") as g:
    w = csv.writer(g); w.writerow(["pozo", "as_ppm", "bajo", "alto", "verdad"])
    for k, i in enumerate(esc): w.writerow([f"P-{i + 1:03d}", round(float(pred[k]), 1), round(float(bajo[k]), 1), round(float(alto[k]), 1), int(verdad[k])])
print(json.dumps({"n": n, "escondidas": len(esc), "krylov_dentro": dentro, "krylov_ms": round(ms, 1), "umbral": T["umbral"],
                  "error_medio": round(float(np.abs(pred - verdad).mean()), 1), "sobre_limite_bien": int(((pred > T["umbral"]) == (verdad > T["umbral"])).sum())}))
