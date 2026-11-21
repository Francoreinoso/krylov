"""Calibración de la red de `supervivencia` en simulaciones nuevas: SBC y cobertura.

SBC (simulation-based calibration): para cada dataset simulado nuevo se conoce el θ verdadero; si
q(θ | D) está calibrado, el rango del valor verdadero entre las muestras del posterior es uniforme,
parámetro por parámetro. Se reporta además la cobertura del intervalo de 90% (por rangos), por
grupos de n y de número de cargos, y cuánto se contrae el posterior respecto del prior (0 = no
aprendió nada, 1 = lo sabe exacto).

    uv run python -m motor.supervivencia.validar --sbc 200
    uv run python -m motor.supervivencia.validar --sbc 200 --contra-mcmc      # además, contra las muestras de MCMC ya guardadas

Lee el punto de guardado `motor/checkpoints/supervivencia/ultimo.pt` y escribe `sbc.json` al lado.

El SBC no ve todo: una red que devuelve el prior sale calibrada. Lo que le falta lo muestra la comparación con el
MCMC de referencia, empresa por empresa. Correr el MCMC tarda minutos y no puede ir encima de un entrenamiento;
`--contra-mcmc` usa las muestras que dejó el último sello (`mcmc/*.npz`), así la comparación tarda segundos y sirve
para mirar un punto de guardado a mitad de camino. Solo vale si el prior es el mismo con que corrió ese MCMC.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from motor.comun.validacion import comparar_posteriores, dentro_del_rango
from motor.supervivencia import red as red_sv
from motor.supervivencia import simular
from motor.supervivencia.entrenar import CARPETA
from nucleo import casos, supervivencia as nucleo_sv

N_CHICO = 600          # frontera entre «n chico» y «n grande» para la cobertura por grupos
CARGOS_POCOS = 6       # y entre pocos y muchos cargos
CHI2_99_GL9 = 21.67    # percentil 99 de un χ² con 9 grados de libertad
MCMC_GUARDADO = simular.RAIZ / "motor" / "artefactos" / "supervivencia" / "mcmc"
# Grupos de parámetros para leer la comparación con el MCMC (posiciones de `nucleo.supervivencia.NOMBRES_THETA`).
GRUPOS = {"k y beta0": [0, 1], "efectos": [2, 3, 4], "spline": list(range(5, 11)), "tau": [11], "sigma_u": [12], "lambda": [13],
          "cargas": list(range(14, 18)), "cortes": list(range(18, 30)), "censura": [30, 31]}


def mismo_prior(estado: dict) -> bool:
    """¿El punto de guardado se entrenó con el prior vigente (`simular.cargar_config`)? Validar contra otro prior no dice nada."""
    del_punto = (estado.get("config") or {}).get("simulador", {}).get("prior")
    return del_punto is None or del_punto == simular.cargar_config()["prior"]


def cargar_red(ruta: Path, promedio: bool = True) -> tuple[red_sv.RedSupervivencia, dict]:
    """Red en modo evaluación desde un punto de guardado del bucle común (también uno anterior a los atajos nuevos).

    Con `promedio` (lo normal: así se valida y se exporta) los pesos son su promedio móvil; sin él, los del último paso.
    """
    estado = torch.load(ruta, map_location="cpu", weights_only=False)
    red = red_sv.RedSupervivencia(**red_sv.ARQUITECTURA)
    red_sv.cargar_estado(red, estado["modulo"])
    if promedio:
        red.usar_promedio()
    if not mismo_prior(estado):
        print(f"[aviso] {ruta} se entrenó con otro prior que {simular.ruta_config()}: pon KRYLOV_SUPERVIVENCIA_CONFIG con el suyo", flush=True)
    return red.eval(), estado


def sbc(red: red_sv.RedSupervivencia, datasets: int, muestras: int = 99, semilla: int = 10_000, lote: int = 25) -> dict:
    """SBC y cobertura sobre `datasets` simulaciones nuevas (semilla distinta a la del entrenamiento).

    Por parámetro: rango medio (0,5 sin sesgo), χ² de uniformidad de los rangos en 10 tramos, cobertura del intervalo
    de 90% (contada por rangos: exacta con 99 muestras), contracción respecto del prior y recuperación (correlación entre
    el valor verdadero y la media del posterior). La cobertura va también por grupos: empresas chicas y grandes, con pocos
    y con muchos cargos.
    """
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    rangos, tamanos, cargos, varianza_post, medias, verdades = [], [], [], [], [], []
    for _ in range(int(np.ceil(datasets / lote))):
        n = simular.muestrear_n(rng, config)
        simulado = simular.simular(rng, lote, n, config, reales)
        filas, grupo, theta = red_sv.lote_a_tensores(simulado)
        post = red.muestrear(filas, grupo, muestras).numpy()             # (muestras, lote, 32)
        rangos.append((post < theta.numpy()).sum(axis=0))                 # 0..muestras
        varianza_post.append(post.var(axis=0))
        medias.append(post.mean(axis=0)), verdades.append(theta.numpy())
        tamanos.append(np.full(lote, n))
        cargos.append(np.array([len(np.unique(g)) for g in simulado["grupo"]]))
    rangos, tamanos = np.concatenate(rangos)[:datasets], np.concatenate(tamanos)[:datasets]
    cargos, varianza_post = np.concatenate(cargos)[:datasets], np.concatenate(varianza_post)[:datasets]
    medias, verdades = np.concatenate(medias)[:datasets], np.concatenate(verdades)[:datasets]
    dentro = dentro_del_rango(rangos, muestras)
    # La varianza del prior se mide con el prior vigente: la escala guardada en el flujo es la del prior con que se construyó la red.
    del_prior = nucleo_sv.a_libre(simular.muestrear_prior(np.random.default_rng(semilla), 20_000, config["prior"]))
    contraccion = 1.0 - varianza_post.mean(axis=0) / del_prior.var(axis=0)

    por_parametro = {}
    for j, nombre in enumerate(nucleo_sv.NOMBRES_THETA):
        tramos = np.histogram(rangos[:, j], bins=10, range=(0, muestras + 1))[0]
        chi2 = float(((tramos - len(rangos) / 10) ** 2 / (len(rangos) / 10)).sum())
        por_parametro[nombre] = {"rango_medio": round(float(rangos[:, j].mean() / muestras), 3), "chi2_uniformidad": round(chi2, 1),
                                 "uniforme_al_99": chi2 < CHI2_99_GL9, "cobertura_90": round(float(dentro[:, j].mean()), 3),
                                 "contraccion": round(float(contraccion[j]), 3),
                                 "recuperacion": round(float(np.corrcoef(verdades[:, j], medias[:, j])[0, 1]), 3)}
    grupos = {f"n hasta {N_CHICO}": tamanos <= N_CHICO, f"n sobre {N_CHICO}": tamanos > N_CHICO,
              f"hasta {CARGOS_POCOS} cargos": cargos <= CARGOS_POCOS, f"más de {CARGOS_POCOS} cargos": cargos > CARGOS_POCOS}
    por_grupo = {nombre: round(float(dentro[m].mean()), 3) for nombre, m in grupos.items() if m.any()}
    peor = min(por_grupo, key=por_grupo.get)
    coberturas = [v["cobertura_90"] for v in por_parametro.values()]
    return {
        "casos_validacion": int(len(rangos)), "muestras_por_dataset": muestras,
        "cobertura_90": round(float(np.mean(coberturas)), 3),
        "cobertura_90_peor_grupo": por_grupo[peor], "peor_grupo": peor, "cobertura_90_por_grupo": por_grupo,
        "cobertura_90_peor_parametro": {"nombre": min(por_parametro, key=lambda k: por_parametro[k]["cobertura_90"]), "valor": min(coberturas)},
        "parametros_uniformes_al_99": int(sum(v["uniforme_al_99"] for v in por_parametro.values())),
        "contraccion_media": round(float(contraccion.mean()), 3), "theta": por_parametro,
    }


def contra_mcmc(red: red_sv.RedSupervivencia, carpeta: Path = MCMC_GUARDADO, muestras: int = 2000, caso: str = "rotacion") -> dict:
    """La red contra las muestras de MCMC guardadas: las empresas simuladas de referencia y el archivo real del caso.

    Por empresa y por parámetro, la diferencia de medias en desviaciones del posterior del MCMC (lo que el sello
    exige bajo 0,3 de promedio) y la razón de anchos red/MCMC; resumidas por grupo de parámetros. No corre MCMC.
    """
    simuladas = sorted(carpeta.glob("simulado_*.npz"))
    lote = simular.empresas_de_referencia(len(simuladas)) if simuladas else None
    variables = nucleo_sv.variables_del_modelo(lote) if simuladas else {}
    entradas = [(ruta, {c: v[i] for c, v in variables.items()}) for i, ruta in enumerate(simuladas)]
    if (carpeta / f"{caso}.npz").exists():
        del_caso = casos.cargar_caso(caso)
        entradas.append((carpeta / f"{caso}.npz", nucleo_sv.variables_del_modelo(nucleo_sv.leer_tabla(casos.RAIZ / del_caso["dataset"], del_caso["columnas"]))))
    if not entradas:
        raise SystemExit(f"No hay muestras de MCMC en {carpeta}")
    torch.manual_seed(0)
    diferencias, anchos, claves = [], [], []
    for ruta, datos in entradas:
        with np.load(ruta) as archivo:
            del_mcmc = archivo["theta"].astype(np.float64)
            if "theta_verdadero" in archivo and not np.allclose(archivo["theta_verdadero"], lote["theta"][len(claves)], atol=1e-5):
                raise SystemExit(f"{ruta} no es de la empresa de referencia: ¿se generó con otro prior? (KRYLOV_SUPERVIVENCIA_CONFIG)")
        filas = nucleo_sv.armar_filas(datos["x"], datos["w"], datos["encuestas"], datos["tiempo"], datos["evento"])
        with torch.no_grad():
            de_la_red = red.muestrear(torch.from_numpy(filas[None]), torch.from_numpy(np.asarray(datos["grupo"])[None]), muestras)[:, 0].numpy().astype(np.float64)
        diferencia, razon = comparar_posteriores(de_la_red, del_mcmc)
        diferencias.append(diferencia), anchos.append(razon), claves.append(ruta.stem)
    diferencias, anchos = np.array(diferencias), np.array(anchos)
    es_simulada = np.array([c.startswith("simulado_") for c in claves])

    def partes(valores: np.ndarray) -> dict:
        salida = {"todas": round(float(valores.mean()), 3)}
        if es_simulada.any():
            salida["simuladas"] = round(float(valores[es_simulada].mean()), 3)
        if (~es_simulada).any():
            salida["real"] = round(float(valores[~es_simulada].mean()), 3)
        return salida

    return {
        "carpeta": str(carpeta), "empresas": claves,
        "diferencia_media": round(float(diferencias.mean()), 3), "bajo_0_3": bool(diferencias.mean() < 0.3),
        "diferencia_por_empresa": dict(zip(claves, diferencias.mean(axis=1).round(3).tolist())),
        "diferencia_por_grupo": {g: partes(diferencias[:, idx]) for g, idx in GRUPOS.items()},
        "razon_de_anchos_por_grupo": {g: partes(anchos[:, idx]) for g, idx in GRUPOS.items()},
        "diferencia_por_parametro": {nombre: partes(diferencias[:, j]) for j, nombre in enumerate(nucleo_sv.NOMBRES_THETA)},
    }


def principal() -> None:
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analizador.add_argument("--sbc", type=int, default=200, help="datasets simulados nuevos")
    analizador.add_argument("--muestras", type=int, default=99, help="muestras del posterior por dataset")
    analizador.add_argument("--punto", default=str(CARPETA / "ultimo.pt"), help="punto de guardado a validar")
    analizador.add_argument("--contra-mcmc", nargs="?", const=str(MCMC_GUARDADO), default=None, metavar="CARPETA",
                            help="además, comparar con las muestras de MCMC de esa carpeta (por defecto, las del último sello)")
    analizador.add_argument("--sin-promedio", action="store_true", help="validar los pesos del último paso y no su promedio móvil")
    analizador.add_argument("--hilos", type=int)
    a = analizador.parse_args()
    if a.hilos:
        torch.set_num_threads(a.hilos)

    red, estado = cargar_red(Path(a.punto), promedio=not a.sin_promedio)
    resultado = sbc(red, a.sbc, a.muestras)
    resultado.update(pasos=estado["pasos"], simulaciones_entrenamiento=estado["datasets_simulados"],
                     entrenamiento_min=round(estado["segundos"] / 60, 1))
    from motor.comun.validacion import sbc_sin_sesgo
    resultado["sbc_sin_sesgo"], resultado["sbc_parametros_que_fallan"] = sbc_sin_sesgo(resultado["theta"])
    if a.contra_mcmc:
        resultado["mcmc"] = contra_mcmc(red, Path(a.contra_mcmc))
    salida = Path(a.punto).with_name("sbc.json")
    salida.write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
    for nombre, v in resultado["theta"].items():
        print(f"{nombre:>12}  rango medio {v['rango_medio']:.2f}  χ² {v['chi2_uniformidad']:5.1f}  cobertura90 {v['cobertura_90']:.2f}  contracción {v['contraccion']:+.2f}  recuperación {v['recuperacion']:+.2f}")
    resumen = {k: v for k, v in resultado.items() if k not in ("theta", "mcmc")}
    print(json.dumps(resumen, indent=1, ensure_ascii=False))
    if a.contra_mcmc:
        del_mcmc = resultado["mcmc"]
        print(f"\ncontra el MCMC guardado ({del_mcmc['carpeta']}): diferencia media {del_mcmc['diferencia_media']} "
              f"({'bajo' if del_mcmc['bajo_0_3'] else 'sobre'} 0,3) · por empresa {del_mcmc['diferencia_por_empresa']}")
        for grupo, v in del_mcmc["diferencia_por_grupo"].items():
            print(f"{grupo:>12}  diferencia {v}  ·  ancho red/MCMC {del_mcmc['razon_de_anchos_por_grupo'][grupo]}")
    print(f"→ {salida}")


if __name__ == "__main__":
    principal()
