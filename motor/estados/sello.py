"""Valida la red de `estados` y escribe su sello (skill `validar-motor`). **Sin nada entrenando en este computador.**

    uv run python -m motor.estados.sello                   # completo: SBC con 2.000 carteras y MCMC en 5 simuladas más la real
    uv run python -m motor.estados.sello --ensayo          # todo el recorrido en chico, a una carpeta temporal

Hace, en orden, los chequeos de WORKPLAN.md 11.8 y deja `motor/artefactos/estados/` completo:

1. Exporta el punto de guardado (`codificador.onnx`, `flujo.npz`, `pesos.pt`, `config.json`) y comprueba que
   onnxruntime y el flujo en NumPy coinciden con torch.
2. SBC y cobertura del intervalo de 90% de θ en carteras simuladas nuevas, en total y por grupos (carteras chicas y grandes).
3. Lo que se decide, en carteras simuladas nuevas: ¿el rango de 90% de la probabilidad de impago de cada cliente por
   decidir contiene a la probabilidad que da el filtro forward con el θ verdadero? Para la red y para el método rápido
   de siempre (regresión logística simple, `motor/comun/rapido.py`), con las mismas carteras.
4. Comparación con el MCMC de referencia (NUTS) en carteras simuladas y en el archivo real: diferencia de medias del
   posterior en desviaciones estándar, y segundos por cartera. Las muestras del real quedan en `mcmc/` (plan B).
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
from motor.estados import mcmc, nube, simular
from motor.estados.exportar import ARTEFACTOS, PUNTO, configuracion, exportar
from motor.estados.red import RedEstados
from motor.estados.validar import sbc
from nucleo import casos, estados as nucleo_es, tabla
from nucleo.estados import VARIABLES

CASO = "credito"
PUNTO_DE_HUMO = PUNTO.parent.parent / "estados_humo" / "ultimo.pt"


def filas_reales(caso: dict | None = None) -> tuple[np.ndarray, list[str]]:
    """Las filas del codificador y los ids del archivo real del caso (lo que pide `motor.comun.rapido`)."""
    datos = nucleo_es.leer_caso(caso or casos.cargar_caso(CASO))
    return nucleo_es.armar_filas(*(datos[k] for k in VARIABLES), datos["impago"]), datos["id"]


def calibracion_de_unidades(red: RedEstados, carteras: int, muestras: int = 99, semilla: int = 20_000) -> dict:
    """Cobertura del rango de 90% de la probabilidad de impago, cliente por cliente, en carteras simuladas nuevas.

    El blanco es la probabilidad que da el paso local exacto con el θ verdadero de la cartera (lo mejor que se
    puede saber con ese historial). Para la red, el rango sale de las muestras del posterior pasadas por el filtro
    forward (cobertura por rangos); para el método rápido, de su intervalo de Wald. También Brier y AUC de las
    dos, y del θ verdadero, contra lo que pasó en la simulación.
    """
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    reales = simular.cargar_covariables_reales()
    dentro_red, dentro_rapido, p_red, p_rapido, p_verdad, paso = [], [], [], [], [], []
    for inicio in range(0, carteras, 10):
        b = min(10, carteras - inicio)
        lote = simular.simular(rng, b, simular.muestrear_n(rng), reales)
        with torch.no_grad():
            posterior = red.muestrear(torch.from_numpy(lote["filas"]), muestras).numpy().astype(np.float64)       # (muestras, b, 33)
        for i in range(b):
            falta = np.isnan(lote["impago"][i])
            datos = {k: lote[k][i][falta] for k in VARIABLES}
            de_la_red = nucleo_es.probabilidad_de_impago(posterior[:, i], datos)                                  # (clientes, muestras)
            con_theta_verdadero = nucleo_es.probabilidad_de_impago(lote["theta"][i], datos)[:, 0]
            dentro_red.append(validacion.dentro_del_rango((de_la_red < con_theta_verdadero[:, None]).sum(axis=1), muestras))
            p, bajo, alto = rapido.ajustar_y_predecir(lote["filas"][i])
            dentro_rapido.append((con_theta_verdadero >= bajo) & (con_theta_verdadero <= alto))
            p_red.append(de_la_red.mean(axis=1)), p_rapido.append(p), p_verdad.append(con_theta_verdadero), paso.append(lote["impago_real"][i][falta])
    paso = np.concatenate(paso)
    return {"carteras": carteras, "clientes_por_decidir": int(len(paso)),
            "cobertura_90_red": round(float(np.concatenate(dentro_red).mean()), 3),
            "cobertura_90_metodo_rapido": round(float(np.concatenate(dentro_rapido).mean()), 3),
            "contra_lo_que_paso": {"red": rapido.metricas(np.concatenate(p_red), paso), "metodo_rapido": rapido.metricas(np.concatenate(p_rapido), paso),
                                   "theta_verdadero": rapido.metricas(np.concatenate(p_verdad), paso)}}


def comparar_con_mcmc(red: RedEstados, simulados: int, pasos: int, carpeta: Path, n: int = 1000, cadenas: int = 4, profundidad: int = 10) -> dict:
    """Red contra NUTS en carteras simuladas y en el archivo real. Guarda las muestras del real: es el plan B de la tarjeta."""
    lote = simular.simular(np.random.default_rng(2026), simulados, n, simular.cargar_covariables_reales())
    entradas = [(f"simulado_{i:02d}", {k: lote[k][i] for k in VARIABLES}, lote["impago"][i], lote["filas"][i]) for i in range(simulados)]
    real = simular.variables_del_caso(CASO)
    entradas.append((CASO, {k: real[k] for k in VARIABLES}, real["impago"], filas_reales()[0]))
    diferencias, filas_informe = [], []
    for clave, datos, impago, filas in entradas:
        r = mcmc.correr(datos, impago, calentamiento=pasos, muestras=pasos, cadenas=cadenas, semilla=len(filas_informe), profundidad=profundidad)
        mcmc.guardar(clave, r, carpeta / "mcmc")
        with torch.no_grad():
            de_la_red = red.muestrear(torch.from_numpy(filas[None]), 1000)[:, 0].numpy().astype(np.float64)
        diferencia, razon_de_anchos = validacion.comparar_posteriores(de_la_red, r["theta"])
        falta = np.isnan(impago)
        por_decidir = {k: datos[k][falta] for k in VARIABLES}
        en_p = np.abs(nucleo_es.probabilidad_de_impago(de_la_red[:200], por_decidir).mean(axis=1)
                      - nucleo_es.probabilidad_de_impago(r["theta"][:: max(1, len(r["theta"]) // 200)], por_decidir).mean(axis=1))
        diferencias.append(diferencia)
        filas_informe.append({"clave": clave, "clientes": int(len(impago)), "segundos": round(r["segundos"], 1), "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3),
                              "n_eff_min": round(float(np.nanmin(r["n_eff"]))), "diferencia_media": round(float(diferencia.mean()), 3),
                              "diferencia_maxima": round(float(diferencia.max()), 3), "parametro_de_la_maxima": nucleo_es.NOMBRES_THETA[int(diferencia.argmax())],
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
    p.add_argument("--sbc", type=int, default=2000, help="carteras simuladas nuevas para el SBC")
    p.add_argument("--unidades", type=int, default=200, help="carteras simuladas para la cobertura de lo que se decide")
    p.add_argument("--simulados", type=int, default=5, help="carteras simuladas para comparar con el MCMC")
    p.add_argument("--nube", type=int, default=5000, help="simulaciones del predictivo a priori para la nube")
    p.add_argument("--maquina", default="MacBook Air M4 16 GB")
    p.add_argument("--ensayo", action="store_true", help="recorrido completo en chico, a una carpeta temporal: prueba el programa, no la red")
    a = p.parse_args()
    del_mcmc = {"pasos": 500}
    if a.ensayo:
        a.salida, a.sbc, a.unidades, a.simulados, a.nube = Path(tempfile.mkdtemp(prefix="krylov_sello_")) / "estados", 60, 20, 1, 200
        del_mcmc = {"pasos": 20, "n": 300, "cadenas": 2, "profundidad": 4}
        if not a.punto.exists():
            a.punto = PUNTO_DE_HUMO

    red = RedEstados()
    estado = cargar_punto(a.punto, red)
    red.eval()
    config = configuracion({"entrenada": True, "pasos": estado["pasos"], "datasets_simulados": estado["datasets_simulados"],
                            "minutos_entrenamiento": round(estado["segundos"] / 60, 1)})
    informe = {"punto": str(a.punto), "exportacion": exportar(red, a.salida, config)}
    print("[1/6] exportado:", informe["exportacion"], flush=True)
    casos.ARTEFACTOS = a.salida.parent                                    # `nucleo` lee lo recién exportado
    os.environ["KRYLOV_MOTOR_ESTADOS"] = "red"

    informe["sbc"] = sbc(red, a.sbc)
    print("[2/6] SBC:", {k: v for k, v in informe["sbc"].items() if k not in ("theta", "impago_por_decidir")}, flush=True)
    informe["unidades"] = calibracion_de_unidades(red, a.unidades)
    print("[3/6] lo que se decide:", informe["unidades"], flush=True)
    informe["mcmc"] = comparar_con_mcmc(red, a.simulados, carpeta=a.salida, **del_mcmc)
    print("[4/6] MCMC:", {k: v for k, v in informe["mcmc"].items() if k != "por_dataset"}, flush=True)
    informe["nube"] = {"generada": nube.generar(a.salida, a.nube), "archivo_real": {k: v for k, v in nucleo_es.nube(casos.cargar_caso(CASO), []).items()
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
    clientes = informe["mcmc"]["por_dataset"][-1]["clientes"]
    sello = {
        "motor_id": "estados", "implementacion": "red", "pasa": all(criterios.values()), "criterios": criterios,
        "simulaciones_entrenamiento": estado["datasets_simulados"], "entrenamiento_min": round(estado["segundos"] / 60),
        "casos_validacion": a.sbc, "cobertura_90": cobertura_p, "cobertura_90_parametros": cobertura_theta,
        "cobertura_90_peor_grupo": grupos[peor], "peor_grupo": {"n_menor_1000": "carteras de menos de 1.000 clientes", "n_1000_o_mas": "carteras de 1.000 clientes o más"}[peor],
        "sbc_pasa": sbc_pasa, "sbc_parametros_que_fallan": fallan,
        "cobertura_90_metodo_rapido": informe["unidades"]["cobertura_90_metodo_rapido"], "latencia_ms": informe["real"]["analizar_ms"],
        "mcmc_datasets_comparados": informe["mcmc"]["datasets"], "mcmc_s_por_dataset": informe["mcmc"]["s_por_dataset"],
        "mcmc_diferencia_media": informe["mcmc"]["diferencia_media"], "mcmc_r_hat_max": informe["mcmc"]["r_hat_max"],
        "amortizacion": {"que_se_compara": f"un análisis completo de la cartera del caso ({clientes} clientes)".replace("2000", "2.000"),
                         "mcmc_s": informe["mcmc"]["s_en_el_real"], "red_s": round(informe["real"]["analizar_ms"] / 1000, 3)},
        "examen": informe["real"]["examen_red"], "examen_metodo_rapido": informe["real"]["examen_metodo_rapido"],
        "nube_malo_cae_fuera": None, "nube_archivo_real_dentro": informe["nube"]["archivo_real"]["archivo"]["dentro"],
        "minutos_de_punta_a_punta": None, "fecha": dt.date.today().isoformat(), "maquina": a.maquina, "ensayo": bool(a.ensayo),
        "limitaciones": ["Carteras de 500 a 2.000 clientes, con seis meses de historial por cliente",
                         "Tres estados ocultos; el atraso va en cinco niveles (los códigos 1 y 2 juntos)",
                         "El uso del cupo se modela como normal por estado: el real tiene ceros y un grupo pegado al cupo",
                         "Las transiciones dependen solo de cupo, edad y educación",
                         "Las covariables simuladas salen mitad del archivo del caso y mitad de un generador paramétrico: la red generaliza hasta donde llega ese generador"],
    }
    validacion.escribir(a.salida, sello, informe)


if __name__ == "__main__":
    main()
