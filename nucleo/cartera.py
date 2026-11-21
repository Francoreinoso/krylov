"""La cartera: cientos o miles de empresas analizadas de una vez, ordenadas por lo que les cuesta no saber.

Es donde se ve la amortización: la red ya pagó el costo de cálculo, así que mil análisis
completos (resumen del dataset, posterior de θ, paso local exacto y decisión) caben en segundos.
Con `cartera.modo: simulada`, las empresas salen del simulador del motor del caso, es decir, del
mismo modelo generativo con que se entrenó la red, cada una con sus parámetros, sus covariables
y su tamaño; la pantalla lo dice.

Esta parte es común a los motores de tabla. Cada motor aporta una función que analiza un lote
de empresas simuladas y devuelve, por empresa, las `muestras_p` de sus unidades por decidir.
Si el motor está en `mcmc`, la cartera es la que se alcanzó a precalcular
(`motor/artefactos/<motor_id>/cartera.json`), y sale rotulada.
"""

from __future__ import annotations

import json
import time
from typing import Callable, Iterable

import numpy as np

from nucleo import casos as _casos, decision
from nucleo.casos import ErrorKrylov, implementacion

MUESTRAS = 8          # muestras de θ por empresa (WORKPLAN.md, 11.6: presupuesto de la cartera)


def fila(nombre: str, muestras_p: np.ndarray, costos: dict) -> dict:
    """La fila de una empresa: cuántas unidades decide, cuánto le cuesta no saber y cuántas quedan en duda."""
    d = decision.decidir_tabla(muestras_p, costos["falso_si"], costos["falso_no"])
    total = float(d["duda"].sum())
    return {"cliente": nombre, "n_unidades": int(len(muestras_p)), "costo_de_no_saber": round(total),
            "por_unidad": round(total / max(len(muestras_p), 1), 1), "en_duda": int((d["estado"] == "en_duda").sum()), "estado": "verde"}


def responder(caso: dict, analizar_lotes: Callable[[int, int], Iterable[tuple[int, list[np.ndarray]]]]) -> dict:
    """La respuesta de `cartera` de un caso.

    analizar_lotes(n_empresas, muestras) entrega, lote por lote, las `muestras_p` (unidades por decidir × muestras)
    de cada empresa simulada. Aquí se decide, se ordena y se mide el tiempo de punta a punta.
    """
    motor_id, configuracion = caso["motor"], caso["cartera"]
    if implementacion(motor_id) == "mcmc":
        ruta = _casos.ARTEFACTOS / motor_id / "cartera.json"
        if not ruta.exists():
            raise ErrorKrylov("La cartera todavía no está precalculada.", "no_disponible")
        return {**json.loads(ruta.read_text(encoding="utf-8")), "precalculado": True}

    costos = _casos.costos_numericos(caso, None)
    n_empresas = int(configuracion.get("n", 1000))
    nombre = configuracion.get("nombre", "Empresa")
    inicio = time.perf_counter()
    filas = []
    for _, empresas in analizar_lotes(n_empresas, MUESTRAS):
        for muestras_p in empresas:
            filas.append(fila(f"{nombre} {len(filas) + 1:0{len(str(n_empresas))}d}", muestras_p, costos))
    filas.sort(key=lambda f: -f["costo_de_no_saber"])
    return {"caso": caso["nombre"], "n_analisis": len(filas), "tiempo_ms": round((time.perf_counter() - inicio) * 1000),
            "precalculado": False, "filas": filas, "sintetico": True,
            "origen_datos": f"{len(filas):,}".replace(",", ".") + f" {configuracion.get('que', 'empresas')} simuladas, cada una distinta"}


def tamanos_de_lote(n_empresas: int, por_lote: int = 50) -> list[int]:
    """Cómo se reparten las empresas en lotes: cada lote comparte tamaño de dataset, y así va en una sola pasada de la red."""
    return [por_lote] * (n_empresas // por_lote) + ([n_empresas % por_lote] if n_empresas % por_lote else [])
