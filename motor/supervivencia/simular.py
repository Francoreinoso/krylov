"""Simulador del modelo generativo de `supervivencia` (WORKPLAN.md, 11.2), vectorizado en NumPy.

Genera lotes de datasets completos: prior sobre θ (32 parámetros globales) → efecto por cargo u_g →
compromiso latente z_i por persona → cuatro encuestas ordinales, tiempo hasta la renuncia (Weibull)
y censura (LogNormal) → años enteros observados t_i y evento δ_i, con δ borrado en el 20% por
decidir. Las covariables salen mitad de filas reales remuestreadas y mitad de un generador
paramétrico (cópula gaussiana). El preprocesamiento es `nucleo.supervivencia.preprocesar`, el mismo
que usa el servicio con el archivo real.

Revisar el predictivo a priori contra un archivo real:
    uv run python -m motor.supervivencia.simular --revisar datos/demo/rotacion.csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from nucleo import supervivencia as nucleo_sv

RAIZ = Path(__file__).resolve().parents[2]
RUTA_CONFIG = RAIZ / "motor" / "artefactos" / "supervivencia" / "config.json"
CARGOS_MAX = 12


def cargar_config() -> dict:
    return json.loads(RUTA_CONFIG.read_text(encoding="utf-8"))


def cargar_filas_reales(config: dict) -> dict | None:
    """Covariables del archivo del caso (versionado en datos/demo/), para la mitad por remuestreo.

    Devuelve None si el archivo no está: entonces todo sale del generador paramétrico.
    """
    import yaml

    caso = yaml.safe_load((RAIZ / "casos" / f"{config['caso_remuestreo']}.yaml").read_text(encoding="utf-8"))
    ruta = RAIZ / caso["dataset"]
    if not ruta.exists():
        return None
    return nucleo_sv.leer_tabla(ruta, caso["columnas"])


# ------------------------------------------------------------------------------------- el prior

def muestrear_prior(rng: np.random.Generator, B: int, prior: dict) -> dict:
    """B muestras de θ con restricciones, según el prior de `config.json`."""
    tau = np.abs(rng.normal(size=B)) * prior["tau_escala"]
    pasos = rng.normal(size=(B, nucleo_sv.N_SPLINE))
    pasos[:, 0] *= prior["gamma1_desv"]
    pasos[:, 1:] *= tau[:, None]                               # prior de suavidad: paseo al azar
    return {
        "k": np.exp(rng.normal(size=B) * prior["k_log_desv"]),
        "beta0": prior["beta0_media"] + rng.normal(size=B) * prior["beta0_desv"],
        "beta": rng.normal(size=(B, nucleo_sv.N_EFECTOS)) * prior["beta_desv"],
        "gamma": np.cumsum(pasos, axis=1),
        "tau": tau,
        "sigma_u": np.abs(rng.normal(size=B)) * prior["sigma_u_escala"],
        "lambda": rng.normal(size=B) * prior["lambda_desv"],
        "a": np.exp(rng.normal(size=(B, nucleo_sv.N_ENCUESTAS)) * prior["a_log_desv"]),
        "cortes": np.sort(
            rng.normal(size=(B, nucleo_sv.N_ENCUESTAS, nucleo_sv.N_CORTES)) * prior["cortes_desv"], axis=-1
        ),
        "mu_c": prior["mu_c_media"] + rng.normal(size=B) * prior["mu_c_desv"],
        "s_c": np.abs(rng.normal(size=B)) * prior["s_c_escala"],
    }


# ---------------------------------------------------------------------------------- covariables

def _covariables_generador(rng, B, n, rango_cargos):
    """Generador paramétrico: cópula gaussiana con correlaciones y marginales al azar por dataset."""
    A = rng.normal(size=(B, 4, 4))
    cov = A @ A.transpose(0, 2, 1) + 2.0 * np.eye(4)
    d = np.sqrt(np.einsum("bii->bi", cov))
    L = np.linalg.cholesky(cov / (d[:, :, None] * d[:, None, :]))
    e = rng.normal(size=(B, n, 4)) @ L.transpose(0, 2, 1)       # marginales N(0, 1), correlacionadas

    n_cargos = rng.integers(rango_cargos[0], rango_cargos[1] + 1, size=B)
    pesos = rng.gamma(1.5, size=(B, CARGOS_MAX)) * (np.arange(CARGOS_MAX) < n_cargos[:, None])
    acumulado = np.cumsum(pesos / pesos.sum(axis=1, keepdims=True), axis=1)
    grupo = (rng.random((B, n, 1)) > acumulado[:, None, :]).sum(axis=-1)
    grupo = np.minimum(grupo, n_cargos[:, None] - 1)

    # El cargo desplaza el sueldo (en el archivo real los cargos explican buena parte del sueldo).
    desplazamiento = rng.normal(size=(B, CARGOS_MAX)) * rng.uniform(0.0, 1.5, size=(B, 1))
    sueldo = np.exp(e[..., 3] + np.take_along_axis(desplazamiento, grupo, axis=1))

    tasa = rng.uniform(0.1, 0.6, size=B)                         # proporción con horas extra
    umbral = np.take_along_axis(np.sort(e[..., 0], axis=1), (tasa * n).astype(int)[:, None], axis=1)
    horas_extra = (e[..., 0] < umbral).astype(float)
    distancia = np.exp(rng.uniform(0.3, 1.0, size=(B, 1)) * e[..., 1])
    empresas = np.floor(np.exp(0.5 + rng.uniform(0.4, 1.0, size=(B, 1)) * e[..., 2]))
    return np.stack([horas_extra, distancia, empresas], axis=-1), sueldo, grupo


def _covariables_remuestreo(rng, B, n, reales):
    """Filas reales del archivo del caso, remuestreadas con reposición y perturbadas."""
    idx = rng.integers(len(reales["sueldo"]), size=(B, n))
    efectos = reales["efectos"][idx].copy()
    efectos[..., 1] *= np.exp(rng.normal(size=(B, n)) * 0.1)     # distancia
    sueldo = reales["sueldo"][idx] * np.exp(rng.normal(size=(B, n)) * 0.1)
    return efectos, sueldo, np.minimum(reales["grupo"][idx], CARGOS_MAX - 1)


# ----------------------------------------------------------------------------------- el modelo

def simular(rng: np.random.Generator, B: int, n: int, config: dict, reales: dict | None = None) -> dict:
    """Un lote de B datasets de n personas cada uno, con su θ verdadero.

    Devuelve `filas` (B, n, 11) float32 y `grupo` (B, n) para el codificador, `theta` (B, 32)
    float32 en espacio libre para la pérdida NPE, y las columnas crudas y los latentes para pruebas.
    """
    efectos, sueldo, grupo = _covariables_generador(rng, B, n, config["rangos"]["cargos"])
    if reales is not None:
        ef_r, su_r, gr_r = _covariables_remuestreo(rng, B, n, reales)
        real = rng.random(B) < config["fraccion_remuestreo"]
        efectos = np.where(real[:, None, None], ef_r, efectos)
        sueldo = np.where(real[:, None], su_r, sueldo)
        grupo = np.where(real[:, None], gr_r, grupo)
    x, w = nucleo_sv.estandarizar(efectos, sueldo)

    th = muestrear_prior(rng, B, config["prior"])
    u = rng.normal(size=(B, CARGOS_MAX)) * th["sigma_u"][:, None]          # efecto por cargo
    z = rng.normal(size=(B, n))                                            # compromiso latente

    # Encuestas: logit ordenado, P(y ≤ m) = logistic(c_m − a·z).
    p_acum = 1.0 / (1.0 + np.exp(-(th["cortes"][:, None] - th["a"][:, None, :, None] * z[:, :, None, None])))
    encuestas = 1 + (rng.random((B, n, nucleo_sv.N_ENCUESTAS, 1)) > p_acum).sum(axis=-1)

    # Evento: Weibull con S(t) = exp(−exp(η) t^k). Censura: LogNormal.
    eta = (
        th["beta0"][:, None]
        + (x * th["beta"][:, None, :]).sum(axis=-1)
        + (nucleo_sv.base_spline(w) * th["gamma"][:, None, :]).sum(axis=-1)
        + np.take_along_axis(u, grupo, axis=1)
        - th["lambda"][:, None] * z
    )
    T = np.exp(np.clip((np.log(rng.exponential(size=(B, n))) - eta) / th["k"][:, None], -20.0, 20.0))
    C = np.exp(np.clip(th["mu_c"][:, None] + th["s_c"][:, None] * rng.normal(size=(B, n)), -20.0, 20.0))
    tiempo = np.floor(np.minimum(T, C))
    delta = (T <= C).astype(float)

    # δ se borra en el 20% por decidir, al azar y sin mirar la respuesta (CONTRATO.md, sección 1).
    rango = np.argsort(rng.random((B, n)), axis=1)
    evento = np.where(rango < round(config["fraccion_por_decidir"] * n), np.nan, delta)

    return {
        "filas": nucleo_sv.armar_filas(x, w, encuestas, tiempo, evento),
        "grupo": grupo.astype(np.int64),
        "theta": nucleo_sv.a_libre(th).astype(np.float32),
        "efectos": efectos, "sueldo": sueldo, "encuestas": encuestas, "tiempo": tiempo,
        "evento": evento, "delta": delta, "restringido": th, "eta": eta,
    }


def muestrear_n(rng: np.random.Generator, config: dict) -> int:
    """Tamaño del dataset de un lote: log-uniforme en el rango del caso."""
    bajo, alto = config["rangos"]["n"]
    return int(round(np.exp(rng.uniform(np.log(bajo), np.log(alto)))))


# ------------------------------------------------------- predictivo a priori contra el archivo real

def revisar(ruta_csv: str, datasets: int = 2000, semilla: int = 0) -> dict:
    """Compara la tasa de renuncia y la mediana de años del archivo real con el predictivo a priori."""
    import yaml

    config = cargar_config()
    caso = yaml.safe_load((RAIZ / "casos" / f"{config['caso_remuestreo']}.yaml").read_text(encoding="utf-8"))
    real = nucleo_sv.leer_tabla(ruta_csv, caso["columnas"])
    n = len(real["tiempo"])
    rng = np.random.default_rng(semilla)
    tasas, medianas, maximos = [], [], []
    for _ in range(datasets // 50):
        lote = simular(rng, 50, n, config, cargar_filas_reales(config))
        tasas.append(lote["delta"].mean(axis=1))
        medianas.append(np.median(lote["tiempo"], axis=1))
        maximos.append(lote["tiempo"].max(axis=1))
    resumen = {}
    for nombre, sim, valor in [
        ("tasa de renuncia", np.concatenate(tasas), float(np.nanmean(real["evento"]))),
        ("mediana de años", np.concatenate(medianas), float(np.median(real["tiempo"]))),
        ("máximo de años", np.concatenate(maximos), float(real["tiempo"].max())),
    ]:
        cuantiles = np.quantile(sim, [0.05, 0.25, 0.5, 0.75, 0.95])
        percentil = float((sim < valor).mean())
        resumen[nombre] = {"real": valor, "simulado_q05_q25_q50_q75_q95": cuantiles.round(3).tolist(),
                           "percentil_del_real": round(percentil, 3)}
        print(f"{nombre}: real {valor:.3f} · simulado q05..q95 {cuantiles.round(3).tolist()} "
              f"· el real cae en el percentil {100 * percentil:.1f}")
    return resumen


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--revisar", metavar="CSV", required=True,
                            help="archivo real del caso, con los papeles de casos/rotacion.yaml")
    analizador.add_argument("--datasets", type=int, default=2000)
    argumentos = analizador.parse_args()
    revisar(argumentos.revisar, argumentos.datasets)
