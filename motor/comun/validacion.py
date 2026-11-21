"""Lo común a la validación de los motores (WORKPLAN.md 11.8): cobertura por rangos, umbral del SBC, comparación de posteriores.

SBC (calibración basada en simulación): para un dataset simulado con θ verdadero se sacan L muestras del
posterior amortizado q(θ | D) y se cuenta cuántas quedan bajo el valor verdadero. Ese **rango** toma un
valor entre 0 y L; si q es el posterior exacto, los L + 1 valores son igual de probables.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np


def dentro_del_rango(rangos: np.ndarray, muestras: int, nivel: float = 0.9) -> np.ndarray:
    """¿Cae el valor verdadero en el intervalo central de `nivel` del posterior? Se decide con el rango del SBC.

    Con L muestras hay L + 1 rangos posibles, uniformes si el posterior está calibrado. El intervalo central
    se queda con los rangos del medio: con L = 99 y 90%, de 5 a 94, que son exactamente 90 de 100. Comparar
    contra los cuantiles 5% y 95% de las L muestras da, con un posterior perfecto, (L − 1)·0,9/(L + 1) (0,882
    con L = 99) y no 0,90: por eso la cobertura se cuenta por rangos.
    """
    cola = (1 - nivel) / 2 * (muestras + 1)
    return (np.asarray(rangos) >= cola - 1e-9) & (np.asarray(rangos) <= muestras - cola + 1e-9)


def umbral_chi2(parametros: int, gl: int = 9, nivel: float = 0.01) -> float:
    """Umbral del χ² de uniformidad para que, entre `parametros` pruebas, la probabilidad de una falsa alarma sea `nivel`.

    Con un umbral del 1% por parámetro, un motor de 33 parámetros perfectamente calibrado «fallaría» el SBC
    una de cada cuatro veces (1 − 0,99³³ = 0,28). Corrección de Bonferroni: cada prueba se hace al nivel `nivel`/parámetros.
    """
    from scipy.stats import chi2
    return float(chi2.ppf(1 - nivel / parametros, gl))


def sbc_sin_sesgo(por_parametro: dict, tolerancia_rango: float = 0.03) -> tuple[bool, list[str]]:
    """El criterio «SBC sin sesgo visible»: χ² de uniformidad bajo el umbral corregido y rango medio a menos de 0,03 de 0,5.

    por_parametro: nombre → {"chi2_uniformidad", "rango_medio"}. Devuelve (pasa, parámetros que fallan).
    """
    umbral = umbral_chi2(len(por_parametro))
    fallan = [nombre for nombre, v in por_parametro.items()
              if v["chi2_uniformidad"] >= umbral or abs(v["rango_medio"] - 0.5) >= tolerancia_rango]
    return not fallan, fallan


def desviacion_w(chi2_uniformidad: float, n: int) -> float:
    """Tamaño de la desviación del histograma de rangos respecto del uniforme: w = √(χ²/n) (el «efecto w» de Cohen).

    No depende de cuántos rangos se juntan: con 10 cajas, w·10 es la distancia cuadrática media de cada caja a su 10%,
    en puntos porcentuales (w = 0,1 ↔ las cajas se alejan en promedio 1 punto de 10%). Por convención w < 0,1 es «chico».
    """
    return float(np.sqrt(chi2_uniformidad / n))


def sbc_local_sin_sesgo(por_parametro: dict, tolerancia_w: float = 0.1, tolerancia_rango: float = 0.03) -> tuple[bool, list[str]]:
    """El criterio del SBC local (D-39): desviación w bajo 0,1 y rango medio a menos de 0,03 de 0,5, por parámetro local.

    Los rangos locales se juntan sobre todas las unidades de todos los datasets (decenas de miles), y las unidades de un
    mismo dataset comparten η: no son independientes. La prueba χ² de `sbc_sin_sesgo`, pensada para un rango por dataset,
    con ese n rechaza desviaciones de medio punto por caja que con 2.000 rangos no alcanza a ver, y su umbral supone
    independencia. Aquí se acota el tamaño de la desviación, que no crece con n. La vara es la misma que la del global:
    con 2.000 rangos el umbral del χ² equivale a w ≈ 0,11.

    por_parametro: nombre → {"chi2_uniformidad", "rango_medio", "n"}. Devuelve (pasa, parámetros que fallan).
    """
    fallan = [nombre for nombre, v in por_parametro.items()
              if desviacion_w(v["chi2_uniformidad"], v["n"]) >= tolerancia_w or abs(v["rango_medio"] - 0.5) >= tolerancia_rango]
    return not fallan, fallan


def recuperacion(por_parametro: dict) -> dict:
    """Recuperación de parámetros para el sello: correlación entre el valor verdadero y la media del posterior, en las simulaciones del SBC.

    Cerca de 1, los datos identifican el parámetro y la red lo recupera; cerca de 0, el posterior se queda en el
    prior (el parámetro no se puede saber con un dataset de ese tamaño, o la red no lo aprendió: lo distingue el MCMC).
    """
    valores = {nombre: v["recuperacion"] for nombre, v in por_parametro.items()}
    return {"media": round(sum(valores.values()) / len(valores), 3), "minima": min(valores.values()),
            "parametro_de_la_minima": min(valores, key=valores.get), "por_parametro": valores}


def comparar_posteriores(de_la_red: np.ndarray, del_mcmc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Posterior amortizado contra el de referencia, parámetro por parámetro. Entradas: (muestras, d).

    Devuelve (|diferencia de medias| en desviaciones estándar del posterior del MCMC, razón de desviaciones red/MCMC).
    """
    desv = del_mcmc.std(axis=0)
    return np.abs(de_la_red.mean(axis=0) - del_mcmc.mean(axis=0)) / desv, de_la_red.std(axis=0) / desv


def mejor_de_3(f):
    """(milisegundos de la mejor de tres llamadas, salida de la última)."""
    tiempos = []
    for _ in range(3):
        inicio = time.perf_counter()
        salida = f()
        tiempos.append((time.perf_counter() - inicio) * 1000)
    return round(min(tiempos)), salida


def escribir(carpeta: Path, sello: dict, informe: dict) -> None:
    """Deja `sello.json` (lo que lee el servicio) y `validacion.json` (el detalle de cada chequeo) y dice el veredicto."""
    (carpeta / "sello.json").write_text(json.dumps(sello, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (carpeta / "validacion.json").write_text(json.dumps(informe, indent=1, ensure_ascii=False, default=float) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in sello.items() if k != "limitaciones"}, indent=1, ensure_ascii=False))
    print(f"\n{'PASA' if sello['pasa'] else 'NO PASA'} · {carpeta / 'sello.json'}")
