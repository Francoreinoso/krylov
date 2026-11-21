"""El plan B de la cartera de rotación: unas pocas empresas analizadas con el MCMC de referencia, precalculadas.

    uv run python -m motor.supervivencia.cartera_mcmc --empresas 5        # sin nada entrenando: minutos por empresa

Si `supervivencia` queda en `mcmc`, `nucleo.cartera` sirve `motor/artefactos/supervivencia/cartera.json` tal cual, con
`precalculado: true` (contrato, sección 6: «la cartera trae solo las empresas que se alcanzaron a precalcular»). Las empresas
son las mismas de la cartera con la red (`nucleo.supervivencia.empresas_de_la_cartera`), con el mismo nombre; se toman del
lote más chico, que es el que menos tarda. Cada una pasa por NUTS, por el paso local exacto con 32 muestras del posterior y
por la misma regla de decisión. `tiempo_ms` es lo que tardó de verdad: es la otra mitad de la cifra de amortización.

Nunca corre encima de un entrenamiento.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from motor.supervivencia import mcmc, simular
from nucleo import cartera as comun, casos, supervivencia as nucleo_sv, tabla

ARTEFACTOS = simular.RAIZ / "motor" / "artefactos" / "supervivencia"
CASO = "rotacion"


def precalcular(empresas: int, carpeta: Path = ARTEFACTOS, **del_mcmc) -> dict:
    """Escribe `carpeta/cartera.json` con `empresas` empresas de la cartera, respondidas con el MCMC. Devuelve lo escrito."""
    caso = casos.cargar_caso(CASO)
    costos = casos.costos_numericos(caso, None)
    total = int(caso["cartera"].get("n", 1000))
    lotes = list(nucleo_sv.empresas_de_la_cartera(total))
    cual = min(range(len(lotes)), key=lambda i: lotes[i]["tiempo"].shape[1])           # el lote de empresas más chicas
    lote, primera = lotes[cual], sum(len(l["theta"]) for l in lotes[:cual])
    variables = nucleo_sv.variables_del_modelo(lote)
    filas, segundos, r_hat = [], 0.0, []
    for e in range(min(empresas, len(lote["theta"]))):
        datos = {c: v[e] for c, v in variables.items()}
        r = mcmc.correr(datos, semilla=e, **del_mcmc)
        elegidas = np.sort(np.random.default_rng(0).choice(len(r["theta"]), size=min(tabla.MUESTRAS, len(r["theta"])), replace=False))
        muestras_p = nucleo_sv.paso_local(r["theta"][elegidas].astype(np.float64), datos)[np.isnan(datos["evento"])]
        nombre = f"{caso['cartera'].get('nombre', 'Empresa')} {primera + e + 1:0{len(str(total))}d}"
        filas.append(comun.fila(nombre, muestras_p, costos))
        segundos += r["segundos"]
        r_hat.append(float(np.nanmax(r["r_hat"])))
        print(json.dumps({"empresa": nombre, "personas": int(len(datos["tiempo"])), "segundos": round(r["segundos"], 1), "r_hat_max": round(r_hat[-1], 3)}), flush=True)
    filas.sort(key=lambda f: -f["costo_de_no_saber"])
    respuesta = {"caso": CASO, "n_analisis": len(filas), "tiempo_ms": round(segundos * 1000), "precalculado": True, "filas": filas, "sintetico": True,
                 "origen_datos": f"{len(filas)} empresas simuladas, cada una distinta"}
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "cartera.json").write_text(json.dumps(respuesta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return respuesta


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--empresas", type=int, default=5)
    analizador.add_argument("--carpeta", type=Path, default=ARTEFACTOS)
    a = analizador.parse_args()
    r = precalcular(a.empresas, a.carpeta)
    print(f"{r['n_analisis']} empresas en {r['tiempo_ms'] / 1000:.0f} s → {a.carpeta / 'cartera.json'}")
