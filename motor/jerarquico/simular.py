"""Simulador del modelo generativo de `jerarquico` (WORKPLAN.md, 11.3), vectorizado en NumPy.

Genera lotes de datasets completos ya en la forma anidada que lee el codificador:
barrios × pacientes del barrio × citas del paciente, con una máscara que dice qué citas
existen. Prior sobre θ (20 parámetros, en espacio sin restricciones) → efecto u_b de cada
barrio → propensión latente v_i de cada paciente → respuesta de cada cita, borrada en el
20% por decidir.

**Se modela la asignación del SMS**, como en el archivo real: solo reciben SMS las citas con
3 o más días de espera, con una probabilidad al azar por dataset. Ninguna cita del mismo
día lo recibe. Sin eso, el efecto del SMS se confunde con el de la espera.

Las covariables salen mitad de filas reales remuestreadas (citas y pacientes del archivo
del caso, con una perturbación) y mitad de un generador paramétrico. Las citas por
paciente siguen una geométrica. La matriz de diseño de cada cita sale de
`nucleo.jerarquico.matriz_de_diseno`, la misma función que usa el servicio.

Predictivo a priori contra el archivo real (que no se versiona: CC BY-NC-SA):
    uv run python -m motor.jerarquico.simular --revisar
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from nucleo import jerarquico as nucleo_jq
from nucleo.jerarquico import DIM_THETA, NOMBRES_THETA

RAIZ = Path(__file__).resolve().parents[2]
CITAS_MIN, CITAS_MAX = 1000, 3000
BARRIOS_MIN, BARRIOS_MAX = 10, 40
CITAS_POR_PACIENTE_MAX = 8
FRACCION_POR_DECIDIR = 0.2

# (media, desviación) de cada parámetro libre. Mismo orden que NOMBRES_THETA.
PRIOR = {
    "alfa": (-1.2, 1.0),
    **{f"inc_gamma_{m}": (0.0, 0.5) for m in range(2, 7)},                 # caminata: prior de suavidad del efecto de la espera
    "kappa": (-1.5, 1.0),                                                  # salto de «mismo día»
    **{f"dia_{d}": (0.0, 0.3) for d in ("martes", "miercoles", "jueves", "viernes")},
    "rho_0": (0.0, 0.5), "rho_1": (0.0, 0.3),                              # efecto del SMS y cómo cambia con la espera
    **{f"beta_{j}": (0.0, 0.5) for j in range(1, 6)},
    "log_sigma_v": (-0.4, 0.6), "log_sigma_b": (-1.2, 0.6),                # dispersión entre pacientes y entre barrios
}
assert tuple(PRIOR) == tuple(NOMBRES_THETA)
MEDIAS = np.array([PRIOR[n][0] for n in NOMBRES_THETA])
DESVS = np.array([PRIOR[n][1] for n in NOMBRES_THETA])


def muestrear_prior(rng: np.random.Generator, lote: int) -> np.ndarray:
    """θ ~ prior, en espacio sin restricciones: (lote, 20)."""
    return MEDIAS + DESVS * rng.standard_normal((lote, DIM_THETA))


def leer_real(caso: str = "inasistencias") -> dict | None:
    """El archivo real del caso, por columnas del modelo. None si no está (no se versiona)."""
    from nucleo.casos import ErrorKrylov, cargar_caso
    try:
        return nucleo_jq.leer_caso(cargar_caso(caso))
    except ErrorKrylov:
        return None


def _covariables(rng: np.random.Generator, forma: tuple[int, int, int, int], reales: dict | None) -> dict:
    """Covariables por cita (espera, día, SMS) y por paciente (edad, cuatro binarias), en la forma anidada (B, G, P, C)."""
    b, g, p, c = forma
    por_dataset = lambda bajo, alto: rng.uniform(bajo, alto, (b, 1, 1, 1))          # noqa: E731
    # Generador paramétrico: cada dataset tiene su propia mezcla de esperas, días, SMS y pacientes.
    mismo_dia = rng.random(forma) < por_dataset(0.15, 0.5)
    espera = np.clip(np.round(np.exp(por_dataset(1.5, 2.8) + por_dataset(0.8, 1.3) * rng.standard_normal(forma))), 1, 180)
    espera = np.where(mismo_dia, 0.0, espera)
    dia = (rng.random(forma + (1,)) > np.cumsum(rng.dirichlet(np.full(5, 8.0), (b, 1, 1, 1)), axis=-1)[..., :-1]).sum(-1)
    edad = np.clip(por_dataset(25, 50) + por_dataset(15, 26) * rng.standard_normal((b, g, p, 1)), 0, 100)
    tasas = rng.beta(1.5, 12.0, (b, 1, 1, 1, 4))
    binarias = (rng.random((b, g, p, 1, 4)) < tasas).astype(np.float64)
    if reales is not None:                                                            # la mitad de los datasets: remuestreo
        del_archivo = (rng.random((b, 1, 1, 1)) < 0.5)
        citas = rng.integers(0, len(reales["espera"]), forma)
        espera_r = reales["espera"][citas]
        espera_r = np.where(espera_r > 0, np.clip(np.round(espera_r * np.exp(rng.normal(0, 0.15, forma))), 1, 180), 0.0)
        espera, dia = np.where(del_archivo, espera_r, espera), np.where(del_archivo, reales["dia"][citas], dia)
        pacientes = rng.integers(0, len(reales["edad"]), (b, g, p, 1))
        edad = np.where(del_archivo, np.clip(reales["edad"][pacientes] + rng.normal(0, 2.0, (b, g, p, 1)), 0, 100), edad)
        binarias = np.where(del_archivo[..., None], reales["binarias"][pacientes], binarias)
    # Asignación del SMS: solo con 3 o más días de espera, con probabilidad propia de cada dataset.
    sms = ((espera >= 3) & (rng.random(forma) < por_dataset(0.3, 0.8))).astype(np.float64)
    return {"espera": espera, "dia": dia, "sms": sms, "edad": np.broadcast_to(edad, forma),
            "binarias": np.broadcast_to(binarias, forma + (4,))}


def simular(rng: np.random.Generator, lote: int, citas: int, barrios: int, reales: dict | None = None, opcionales: bool = True) -> dict:
    """Un lote de datasets simulados con cerca de `citas` citas en `barrios` barrios cada uno.

    Devuelve `filas` (B, G, P, C, 26) y `mascara` (B, G, P, C) para el codificador, `theta` (B, 20), y lo que
    sirve para validar: `z` (matriz de diseño), `respuesta` (NaN = por decidir), `respuesta_real`, `p_real`.
    """
    theta = muestrear_prior(rng, lote)
    th = nucleo_jq.a_restringido(theta)
    # Estructura: citas por paciente ~ geométrica; pacientes por barrio variables (cada cupo de paciente existe o no).
    exito = rng.uniform(0.45, 0.8, (lote, 1, 1))                                      # media de 1,25 a 2,2 citas por paciente
    por_barrio = citas / barrios / (1.0 / exito.mean())
    cupos = max(4, int(np.ceil(1.4 * por_barrio)))
    forma = (lote, barrios, cupos, CITAS_POR_PACIENTE_MAX)
    existe_paciente = rng.random((lote, barrios, cupos)) < 1 / 1.4
    n_citas = np.minimum(rng.geometric(np.broadcast_to(exito, (lote, barrios, cupos))), CITAS_POR_PACIENTE_MAX)
    mascara = (np.arange(CITAS_POR_PACIENTE_MAX) < n_citas[..., None]) & existe_paciente[..., None]

    cov = _covariables(rng, forma, reales)
    presentes = muestrear_presencia(rng, lote) if opcionales else np.ones((lote, nucleo_jq.DIM_PRESENCIA))
    # Un papel ausente va en cero en la matriz de diseño: los datos no dependen de su coeficiente y su posterior es el prior.
    z = (nucleo_jq.matriz_de_diseno(cov["espera"], cov["dia"], cov["sms"], cov["edad"], cov["binarias"])
         * nucleo_jq.mascara_de_columnas(presentes)[:, None, None, None, :])
    cov["sms"] = cov["sms"] * presentes[:, 1, None, None, None]
    u = th["sigma_b"][:, None, None, None] * rng.standard_normal((lote, barrios, 1, 1))
    v = th["sigma_v"][:, None, None, None] * rng.standard_normal((lote, barrios, cupos, 1))
    p_real = 1 / (1 + np.exp(-((z * th["coef"][:, None, None, None, :]).sum(-1) + u + v)))
    respuesta_real = (rng.random(forma) < p_real).astype(np.float64)
    respuesta = np.where(rng.random(forma) < FRACCION_POR_DECIDIR, np.nan, respuesta_real)
    filas = nucleo_jq.armar_filas(z, respuesta, presentes[:, None, None, None, :]) * mascara[..., None]
    return {"filas": filas.astype(np.float32), "mascara": mascara.astype(np.float32), "theta": theta.astype(np.float32),
            "z": z, "respuesta": respuesta, "respuesta_real": respuesta_real, "p_real": p_real, "presentes": presentes, **cov}


def muestrear_presencia(rng: np.random.Generator, lote: int) -> np.ndarray:
    """Qué papeles opcionales trae cada dataset (D-35), (lote, 7) en el orden de `nucleo.jerarquico.OPCIONALES`.

    La mitad de los datasets trae todo (como el archivo del caso); en la otra mitad cada papel está con probabilidad 0,7.
    """
    completo = rng.random((lote, 1)) < 0.5
    return (completo | (rng.random((lote, nucleo_jq.DIM_PRESENCIA)) < 0.7)).astype(np.float64)


def muestrear_tamano(rng: np.random.Generator) -> tuple[int, int]:
    """(citas, barrios) de este lote: citas log-uniforme entre 1.000 y 3.000, barrios entre 10 y 40."""
    return int(np.exp(rng.uniform(np.log(CITAS_MIN), np.log(CITAS_MAX)))), int(rng.integers(BARRIOS_MIN, BARRIOS_MAX + 1))


def a_filas_sueltas(lote: dict, i: int) -> dict:
    """El dataset i de un lote, como filas sueltas con índices de paciente y barrio: lo que pide el paso local y el MCMC."""
    g, p, c = np.nonzero(lote["mascara"][i] > 0)
    _, paciente = np.unique(g * lote["mascara"].shape[2] + p, return_inverse=True)
    barrio_del_paciente = np.zeros(paciente.max() + 1, dtype=int)
    barrio_del_paciente[paciente] = g
    return {"z": lote["z"][i][g, p, c], "respuesta": lote["respuesta"][i][g, p, c], "respuesta_real": lote["respuesta_real"][i][g, p, c],
            "paciente": paciente, "barrio_del_paciente": barrio_del_paciente}


def resumenes(espera, sms, respuesta, mascara) -> dict[str, np.ndarray]:
    """Resúmenes por dataset para mirar el predictivo a priori contra el archivo real. Ejes delanteros libres, (..., G, P, C)."""
    ejes = (-3, -2, -1)
    conocida = (mascara > 0) & ~np.isnan(respuesta)
    y = np.nan_to_num(respuesta)
    def tasa(filtro):
        return (y * (conocida & filtro)).sum(ejes) / np.maximum((conocida & filtro).sum(ejes), 1)
    todo = mascara > 0
    return {"no_llega": tasa(todo), "no_llega_mismo_dia": tasa(espera == 0), "no_llega_otro_dia": tasa(espera > 0),
            "no_llega_con_sms": tasa(sms == 1), "mismo_dia": ((espera == 0) & todo).sum(ejes) / todo.sum(ejes),
            "con_sms": ((sms == 1) & todo).sum(ejes) / todo.sum(ejes),
            "citas_por_paciente": todo.sum(ejes) / np.maximum(todo.any(-1).sum((-2, -1)), 1)}


def revisar(datasets: int = 1000, semilla: int = 0) -> dict:
    """Percentil de cada resumen del archivo real entre los mismos resúmenes de datasets simulados con el prior."""
    real = leer_real()
    if real is None:
        raise SystemExit("No está datos/demo/inasistencias.csv (no se versiona): se genera con datos/preparar/inasistencias.py")
    _, mascara, posicion = nucleo_jq.anidar(np.zeros((len(real["espera"]), 1), dtype=np.float32), real["barrio"], real["paciente"])
    anidado = {k: np.zeros(mascara.shape) for k in ("espera", "sms", "respuesta")}
    for k in anidado:
        anidado[k][tuple(posicion.T)] = real[k]
    del_real = resumenes(anidado["espera"], anidado["sms"], anidado["respuesta"], mascara)
    rng = np.random.default_rng(semilla)
    sim = simular(rng, datasets, 2000, 30, real, opcionales=False)      # el archivo del caso trae todos los papeles
    simulados = resumenes(sim["espera"], sim["sms"], sim["respuesta"], sim["mascara"])
    return {k: {"real": round(float(v), 3), "percentil_en_lo_simulado": round(float((simulados[k] < v).mean()) * 100, 1),
                "simulado_p05_p50_p95": [round(float(q), 3) for q in np.quantile(simulados[k], [0.05, 0.5, 0.95])]}
            for k, v in del_real.items()}


def config() -> dict:
    return {"motor_id": "jerarquico", "version_preproceso": "jerarquico-2", "nombres_theta": list(NOMBRES_THETA),
            "prior": {n: {"media": m, "desv": s} for n, (m, s) in PRIOR.items()},
            "rangos": {"citas": [CITAS_MIN, CITAS_MAX], "barrios": [BARRIOS_MIN, BARRIOS_MAX]},
            "fraccion_por_decidir": FRACCION_POR_DECIDIR, "sms_solo_con_espera_desde": 3,
            "papeles_opcionales": list(nucleo_jq.OPCIONALES), "version_esquema": "jerarquico-2 (presencia por papel)"}


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--revisar", action="store_true", help="predictivo a priori contra datos/demo/inasistencias.csv")
    if analizador.parse_args().revisar:
        print(json.dumps(revisar(), indent=1, ensure_ascii=False))
