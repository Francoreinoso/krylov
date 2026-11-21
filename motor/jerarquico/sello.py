"""Valida la red de `jerarquico` y escribe su sello (skill `validar-motor`). **Sin nada entrenando en este computador.**

    uv run python -m motor.jerarquico.sello                # completo: SBC con 2.000 datasets y MCMC en 5 simulados más el real
    uv run python -m motor.jerarquico.sello --ensayo       # todo el recorrido en chico, a una carpeta temporal

Necesita `datos/demo/inasistencias.csv`, que no se versiona (se genera con `datos/preparar/inasistencias.py`).
Hace, en orden, los chequeos de WORKPLAN.md 11.8 y deja `motor/artefactos/jerarquico/` completo:

1. Exporta el punto de guardado (`codificador.onnx`, `flujo.npz`, `pesos.pt`, `config.json`) y comprueba que
   onnxruntime y el flujo en NumPy coinciden con torch.
2. SBC y cobertura del intervalo de 90% de θ en datasets simulados nuevos, en total y por grupos (pocos y muchos
   barrios, pocas y muchas citas).
3. Lo que se decide, en datasets simulados nuevos: ¿el rango de 90% de la probabilidad de no llegar de cada cita por
   decidir contiene a la probabilidad que da la cuadratura anidada con el θ verdadero? Para la red y para el método
   rápido de siempre (regresión logística simple, `motor/comun/rapido.py`), con los mismos datasets.
4. Comparación con el MCMC de referencia (NUTS, con los efectos de barrio y de paciente muestreados) en datasets
   simulados y en el archivo real: diferencia de medias del posterior en desviaciones estándar, y segundos por
   dataset. Las muestras del real quedan en `mcmc/` (plan B).
5. La nube del predictivo a priori (`nube.npz`) y dónde cae el archivo real.
6. Examen con los datos reales reservados, de la red y del método rápido, y la latencia de un análisis completo.
7. `sello.json`, con `null` en lo que no se midió, y el veredicto: pasa o no pasa.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import tempfile
from pathlib import Path

import numpy as np
import torch

from motor.comun import rapido, validacion
from motor.comun.entrenar import cargar_punto
from motor.jerarquico import mcmc, nube, simular
from motor.jerarquico.exportar import ARTEFACTOS, PUNTO, configuracion, exportar
from motor.jerarquico.red import RedJerarquico
from motor.jerarquico.validar import sbc
from nucleo import casos, jerarquico as nucleo_jq, tabla

CASO = "inasistencias"
PUNTO_DE_HUMO = PUNTO.parent.parent / "jerarquico_humo" / "ultimo.pt"
GRUPOS = {"menos_de_20_barrios": "datasets con menos de 20 barrios", "20_barrios_o_mas": "datasets con 20 barrios o más",
          "menos_de_1700_citas": "datasets con menos de 1.700 citas", "1700_citas_o_mas": "datasets con 1.700 citas o más"}


def _real(caso: dict | None = None) -> dict:
    """El archivo real en filas sueltas, con su matriz de diseño `z` y lo que entra al codificador (`tensor`, `mascara`)."""
    d = nucleo_jq.leer_caso(caso or casos.cargar_caso(CASO))
    d["z"] = nucleo_jq.matriz_de_diseno(d["espera"], d["dia"], d["sms"], d["edad"], d["binarias"])
    d["filas"] = nucleo_jq.armar_filas(d["z"], d["respuesta"])
    d["tensor"], d["mascara"], _ = nucleo_jq.anidar(d["filas"], d["barrio"], d["paciente"])
    return d


def filas_reales(caso: dict | None = None) -> tuple[np.ndarray, list[str]]:
    """Las filas del codificador (una por cita) y los ids del archivo real del caso (lo que pide `motor.comun.rapido`)."""
    d = _real(caso)
    return d["filas"], d["id"]


def _p(theta: np.ndarray, d: dict) -> np.ndarray:
    """P(no llega) de las citas por decidir de un dataset en filas sueltas, por muestra de θ: (citas por decidir, muestras)."""
    return nucleo_jq.paso_local(theta, d["z"], d["respuesta"], d["paciente"], d["barrio_del_paciente"])[np.isnan(d["respuesta"])]


def calibracion_de_unidades(red: RedJerarquico, datasets: int, muestras: int = 39, semilla: int = 20_000) -> dict:
    """Cobertura del rango de 90% de la probabilidad de no llegar, cita por cita, en datasets simulados nuevos.

    El blanco es la probabilidad que da el paso local exacto (cuadratura anidada) con el θ verdadero del dataset:
    lo mejor que se puede saber con esas respuestas. Para la red, el rango sale de 39 muestras del posterior
    pasadas por la cuadratura (cobertura por rangos: de 2 a 37 son 36 de 40); para el método rápido, de su
    intervalo de Wald. También Brier y AUC de las dos, y del θ verdadero, contra lo que pasó en la simulación.
    """
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    reales = simular.leer_real()
    dentro_red, dentro_rapido, p_red, p_rapido, p_verdad, paso = [], [], [], [], [], []
    for _ in range(datasets):
        lote = simular.simular(rng, 1, *simular.muestrear_tamano(rng), reales)
        with torch.no_grad():
            posterior = red.muestrear(torch.from_numpy(lote["filas"]), torch.from_numpy(lote["mascara"]), muestras)[:, 0].numpy().astype(np.float64)
        d = simular.a_filas_sueltas(lote, 0)
        falta = np.isnan(d["respuesta"])
        de_la_red = _p(posterior, d)
        con_theta_verdadero = _p(lote["theta"][:1].astype(np.float64), d)[:, 0]
        dentro_red.append(validacion.dentro_del_rango((de_la_red < con_theta_verdadero[:, None]).sum(axis=1), muestras))
        p, bajo, alto = rapido.ajustar_y_predecir(lote["filas"][0][lote["mascara"][0] > 0])
        dentro_rapido.append((con_theta_verdadero >= bajo) & (con_theta_verdadero <= alto))
        p_red.append(de_la_red.mean(axis=1)), p_rapido.append(p), p_verdad.append(con_theta_verdadero), paso.append(d["respuesta_real"][falta])
    paso = np.concatenate(paso)
    return {"datasets": datasets, "citas_por_decidir": int(len(paso)),
            "cobertura_90_red": round(float(np.concatenate(dentro_red).mean()), 3),
            "cobertura_90_metodo_rapido": round(float(np.concatenate(dentro_rapido).mean()), 3),
            "contra_lo_que_paso": {"red": rapido.metricas(np.concatenate(p_red), paso), "metodo_rapido": rapido.metricas(np.concatenate(p_rapido), paso),
                                   "theta_verdadero": rapido.metricas(np.concatenate(p_verdad), paso)}}


def comparar_con_mcmc(red: RedJerarquico, simulados: int, pasos: int, carpeta: Path, citas: int = 2000, barrios: int = 30,
                      cadenas: int = 4, profundidad: int = 10) -> dict:
    """Red contra NUTS en datasets simulados y en el archivo real. Guarda las muestras del real: es el plan B de la tarjeta."""
    lote = simular.simular(np.random.default_rng(2026), simulados, citas, barrios, simular.leer_real())
    entradas = [(f"simulado_{i:02d}", simular.a_filas_sueltas(lote, i), lote["filas"][i], lote["mascara"][i]) for i in range(simulados)]
    real = _real()
    entradas.append((CASO, real, real["tensor"], real["mascara"]))
    diferencias, filas_informe = [], []
    for clave, d, tensor, mascara in entradas:
        r = mcmc.correr(d, calentamiento=pasos, muestras=pasos, cadenas=cadenas, semilla=len(filas_informe), profundidad=profundidad)
        mcmc.guardar(clave, r, carpeta / "mcmc")
        with torch.no_grad():
            de_la_red = red.muestrear(torch.from_numpy(tensor[None]), torch.from_numpy(mascara[None]), 1000)[:, 0].numpy().astype(np.float64)
        diferencia, razon_de_anchos = validacion.comparar_posteriores(de_la_red, r["theta"])
        en_p = np.abs(_p(de_la_red[:32], d).mean(axis=1) - _p(r["theta"][:: max(1, len(r["theta"]) // 32)][:32].astype(np.float64), d).mean(axis=1))
        diferencias.append(diferencia)
        filas_informe.append({"clave": clave, "citas": int(len(d["respuesta"])), "segundos": round(r["segundos"], 1), "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3),
                              "n_eff_min": round(float(np.nanmin(r["n_eff"]))), "diferencia_media": round(float(diferencia.mean()), 3),
                              "diferencia_maxima": round(float(diferencia.max()), 3), "parametro_de_la_maxima": nucleo_jq.NOMBRES_THETA[int(diferencia.argmax())],
                              "razon_de_anchos_media": round(float(razon_de_anchos.mean()), 2),
                              "diferencia_media_en_p": round(float(en_p.mean()), 4), "diferencia_maxima_en_p": round(float(en_p.max()), 4)})
    diferencias = np.array(diferencias)
    return {"datasets": len(entradas), "pasos_por_cadena": pasos, "cadenas": cadenas,
            "s_por_dataset": round(float(np.mean([f["segundos"] for f in filas_informe])), 1), "s_en_el_real": filas_informe[-1]["segundos"],
            "diferencia_media": round(float(diferencias.mean()), 3), "diferencia_maxima": round(float(diferencias.max()), 3),
            "diferencia_en_el_real": round(float(diferencias[-1].mean()), 3), "r_hat_max": max(f["r_hat_max"] for f in filas_informe),
            "por_dataset": filas_informe}


def examen_y_latencia() -> dict:
    """El examen con los datos reales reservados, de la red y del método rápido, y los milisegundos de un análisis (la mejor de 3)."""
    from nucleo import api
    api.analizar(CASO)                                                    # carga la sesión de onnxruntime
    ms, respuesta = validacion.mejor_de_3(lambda: api.analizar(CASO))
    assert "error" not in respuesta, respuesta
    caso = casos.cargar_caso(CASO)
    del_rapido = rapido.examen(caso, *filas_reales(caso))
    verdad = {i: tabla.si_no(v) for i, v in zip(*(casos.leer_columnas(caso["verdad"])[k] for k in ("id", "objetivo")))}
    pares = np.array([(u["p"], verdad[u["id"]]) for u in respuesta["unidades"] if u["id"] in verdad])
    return {"analizar_ms": ms, "examen_red": {"tramos": respuesta["examen"]["tramos"], "metricas": rapido.metricas(pares[:, 0], pares[:, 1])},
            "examen_metodo_rapido": del_rapido, "resumen_colores": respuesta["resumen_colores"], "factores": respuesta["factores"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--punto", type=Path, default=PUNTO)
    p.add_argument("--salida", type=Path, default=ARTEFACTOS)
    p.add_argument("--sbc", type=int, default=2000, help="datasets simulados nuevos para el SBC")
    p.add_argument("--unidades", type=int, default=100, help="datasets simulados para la cobertura de lo que se decide")
    p.add_argument("--simulados", type=int, default=5, help="datasets simulados para comparar con el MCMC")
    p.add_argument("--nube", type=int, default=2000, help="simulaciones del predictivo a priori para la nube")
    p.add_argument("--maquina", default="MacBook Air M3 16 GB", help="dónde se corre (se entrena y se valida en PC 3)")
    p.add_argument("--ensayo", action="store_true", help="recorrido completo en chico, a una carpeta temporal: prueba el programa, no la red")
    a = p.parse_args()
    if simular.leer_real() is None:
        raise SystemExit("Falta datos/demo/inasistencias.csv (no se versiona): se genera con datos/preparar/inasistencias.py")
    del_mcmc = {"pasos": 500}
    if a.ensayo:
        a.salida, a.sbc, a.unidades, a.simulados, a.nube = Path(tempfile.mkdtemp(prefix="krylov_sello_")) / "jerarquico", 60, 6, 1, 200
        del_mcmc = {"pasos": 20, "citas": 300, "barrios": 5, "cadenas": 2, "profundidad": 4}
        if not a.punto.exists():
            a.punto = PUNTO_DE_HUMO

    red = RedJerarquico()
    estado = cargar_punto(a.punto, red)
    red.eval()
    config = configuracion({"entrenada": True, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
                            "minutos_entrenamiento": round(estado["segundos"] / 60, 1)})
    informe = {"punto": str(a.punto), "exportacion": exportar(red, a.salida, config)}
    print("[1/6] exportado:", informe["exportacion"], flush=True)
    casos.ARTEFACTOS = a.salida.parent                                    # `nucleo` lee lo recién exportado
    os.environ["KRYLOV_MOTOR_JERARQUICO"] = "red"

    informe["sbc"] = sbc(red, a.sbc)
    print("[2/6] SBC:", {k: v for k, v in informe["sbc"].items() if k not in ("theta", "no_llega_por_decidir")}, flush=True)
    informe["unidades"] = calibracion_de_unidades(red, a.unidades)
    print("[3/6] lo que se decide:", informe["unidades"], flush=True)
    informe["mcmc"] = comparar_con_mcmc(red, a.simulados, carpeta=a.salida, **del_mcmc)
    print("[4/6] MCMC:", {k: v for k, v in informe["mcmc"].items() if k != "por_dataset"}, flush=True)
    informe["nube"] = {"generada": nube.generar(a.salida, a.nube), "archivo_real": {k: v for k, v in nucleo_jq.nube(casos.cargar_caso(CASO), []).items()
                                                                                    if k in ("archivo", "detectores")}}
    print("[5/6] nube:", informe["nube"], flush=True)
    informe["real"] = examen_y_latencia()
    print("[6/6] examen y latencia:", {k: informe["real"][k] for k in ("analizar_ms", "examen_red", "examen_metodo_rapido")}, flush=True)

    # Veredicto, con los umbrales de WORKPLAN.md 11.8.
    grupos = {k: v for k, v in informe["sbc"]["cobertura_90_por_grupo"].items() if v is not None}
    peor = min(grupos, key=grupos.get)
    sbc_pasa, fallan = validacion.sbc_sin_sesgo(informe["sbc"]["theta"])
    cobertura_theta, cobertura_p = informe["sbc"]["cobertura_90_media"], informe["unidades"]["cobertura_90_red"]
    criterios = {
        "sbc_sin_sesgo": sbc_pasa, "cobertura_parametros_entre_85_y_95": 0.85 <= cobertura_theta <= 0.95,
        "cobertura_de_lo_que_se_decide_entre_85_y_95": 0.85 <= cobertura_p <= 0.95, "peor_grupo_sobre_80": grupos[peor] >= 0.80,
        "mcmc_bajo_0_3": informe["mcmc"]["diferencia_media"] < 0.3, "analisis_bajo_1_s": informe["real"]["analizar_ms"] < 1000,
    }
    citas = informe["mcmc"]["por_dataset"][-1]["citas"]
    sello = {
        "motor_id": "jerarquico", "implementacion": "red", "pasa": all(criterios.values()), "criterios": criterios,
        "simulaciones_entrenamiento": estado["datasets_simulados"], "entrenamiento_min": round(estado["segundos"] / 60),
        "casos_validacion": a.sbc, "cobertura_90": cobertura_p, "cobertura_90_parametros": cobertura_theta,
        "cobertura_90_peor_grupo": grupos[peor], "peor_grupo": GRUPOS[peor],
        "sbc_pasa": sbc_pasa, "sbc_parametros_que_fallan": fallan,
        "recuperacion": validacion.recuperacion(informe["sbc"]["theta"]),
        "cobertura_90_metodo_rapido": informe["unidades"]["cobertura_90_metodo_rapido"], "latencia_ms": informe["real"]["analizar_ms"],
        "mcmc_datasets_comparados": informe["mcmc"]["datasets"], "mcmc_s_por_dataset": informe["mcmc"]["s_por_dataset"],
        "mcmc_diferencia_media": informe["mcmc"]["diferencia_media"], "mcmc_r_hat_max": informe["mcmc"]["r_hat_max"],
        "amortizacion": {"que_se_compara": "un análisis completo del archivo del caso (" + f"{citas:,}".replace(",", ".") + " citas)",
                         "mcmc_s": informe["mcmc"]["s_en_el_real"], "red_s": round(informe["real"]["analizar_ms"] / 1000, 3)},
        "examen": informe["real"]["examen_red"], "examen_metodo_rapido": informe["real"]["examen_metodo_rapido"],
        "nube_malo_cae_fuera": None, "nube_archivo_real_dentro": informe["nube"]["archivo_real"]["archivo"]["dentro"],
        "minutos_de_punta_a_punta": None, "fecha": dt.date.today().isoformat(), "maquina": a.maquina, "ensayo": bool(a.ensayo),
        "limitaciones": ["Entre 1.000 y 3.000 citas en 10 a 40 barrios; hasta 8 citas por paciente",
                         "Un solo nivel de grupo (el barrio) sobre el paciente; cada paciente va a un solo barrio",
                         "El recordatorio por SMS solo se asigna a citas con 3 o más días de espera, como en el archivo del caso: no es un experimento",
                         "La espera se recorta a 180 días; sábados y domingos no entran",
                         "Las covariables simuladas salen mitad del archivo del caso y mitad de un generador paramétrico: la red generaliza hasta donde llega ese generador"],
    }
    validacion.escribir(a.salida, sello, informe)


if __name__ == "__main__":
    main()
