"""Valida la red de `supervivencia` y escribe su sello (skill `validar-motor`). **Sin nada entrenando en este computador.**

    uv run python -m motor.supervivencia.sello                        # completo: SBC con 2.000 empresas y MCMC en 5 simuladas más la real
    uv run python -m motor.supervivencia.sello --sin-mcmc             # todo menos el MCMC (si hay un entrenamiento corriendo al lado)
    uv run python -m motor.supervivencia.sello --ensayo --sin-mcmc    # el recorrido en chico, a una carpeta temporal: prueba el programa, no la red

Parte del punto de guardado que vio más simulaciones (`motor/checkpoints/supervivencia/ultimo.pt` o el `pesos.pt` ya exportado)
y hace, en orden, los chequeos de WORKPLAN.md 11.8. Deja `motor/artefactos/supervivencia/` completo:

1. Exporta (`codificador.onnx`, `flujo.npz`, `pesos.pt`) y comprueba que onnxruntime y el flujo en NumPy coinciden con torch.
2. SBC y cobertura del intervalo de 90% de θ en empresas simuladas nuevas, en total y por grupos (chicas y grandes; pocos y muchos cargos).
3. Lo que se decide, en empresas simuladas nuevas: ¿el rango de 90% de la probabilidad de cada persona por decidir contiene a la
   que da el paso local con el θ verdadero? Para la red y para el método rápido de siempre (regresión logística simple,
   `motor/comun/rapido.py`), con las mismas empresas.
4. Comparación con el MCMC de referencia (NUTS) en empresas simuladas y en el archivo real: diferencia de medias del posterior en
   desviaciones estándar, y segundos por empresa. Las muestras del real quedan en `mcmc/`: son el plan B de la tarjeta.
5. La nube del predictivo a priori (`nube.npz`, con los resúmenes de esta red): el archivo real tiene que caer dentro;
   `rotacion_malo`, fuera, y con la corrección que propone el semáforo, dentro.
6. Examen con los datos reales reservados, de la red y del método rápido; latencia de un análisis completo y de la cartera.
7. `sello.json`, con `null` en lo que no se midió, y el veredicto: pasa o no pasa.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

from motor.comun import rapido, validacion
from motor.supervivencia import exportar, mcmc, nube, simular
from motor.supervivencia.entrenar import CARPETA
from motor.supervivencia.red import lote_a_tensores
from motor.supervivencia.validar import cargar_red, sbc
from nucleo import casos, supervivencia as nucleo_sv, tabla

CASO, CASO_MALO = "rotacion", "rotacion_malo"
# Archivos de prueba de la subida (D-34): otras empresas con el mismo esquema, con las columnas que asignaría el usuario.
SUBIDOS = ("ventas", "investigacion")
COLUMNAS_SUBIDOS = {"id": "n_empleado", "evento": "renuncio", "tiempo": "anios_en_empresa", "grupo": "cargo", "suave": "sueldo_mensual",
                    "efectos": ["horas_extra", "distancia_km", "empresas_previas"], "encuestas": ["enc_ambiente", "enc_trabajo", "enc_relaciones", "enc_equilibrio"]}
ARTEFACTOS = exportar.ARTEFACTOS


def punto_mas_entrenado() -> Path:
    """Entre el punto de guardado local y el `pesos.pt` exportado, el que vio más simulaciones.

    La red se entrena en PC 3 y llega a los otros computadores como `pesos.pt`; en PC 2 queda además un `ultimo.pt` viejo, de la prueba de humo.
    """
    candidatos = [ruta for ruta in (CARPETA / "ultimo.pt", ARTEFACTOS / "pesos.pt") if ruta.exists()]
    if not candidatos:
        raise SystemExit("No hay punto de guardado: ni motor/checkpoints/supervivencia/ultimo.pt ni motor/artefactos/supervivencia/pesos.pt")
    return max(candidatos, key=lambda ruta: torch.load(ruta, map_location="cpu", weights_only=False)["datasets_simulados"])


def filas_reales(caso: dict | None = None) -> tuple[np.ndarray, list[str]]:
    """Las filas del codificador y los ids del archivo real del caso (lo que pide `motor.comun.rapido`)."""
    datos = nucleo_sv.leer_caso(caso or casos.cargar_caso(CASO))
    return datos["filas"], datos["id"]


def calibracion_de_unidades(red, empresas: int, muestras: int = 99, semilla: int = 20_000) -> dict:
    """Cobertura del rango de 90% de la probabilidad de haber renunciado, persona por persona, en empresas simuladas nuevas.

    El blanco es la probabilidad que da el paso local exacto con el θ verdadero de la empresa (lo mejor que se puede
    saber con esos datos). Para la red, el rango sale de las muestras del posterior pasadas por el paso local
    (cobertura por rangos); para el método rápido, de su intervalo de Wald. También Brier y AUC de las dos, y del
    θ verdadero, contra lo que pasó en la simulación.
    """
    config = simular.cargar_config()
    reales = simular.cargar_filas_reales(config)
    rng = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    dentro_red, dentro_rapido, p_red, p_rapido, p_verdad, paso = [], [], [], [], [], []
    for inicio in range(0, empresas, 10):
        b = min(10, empresas - inicio)
        lote = simular.simular(rng, b, simular.muestrear_n(rng, config), config, reales)
        filas, grupo, _ = lote_a_tensores(lote)
        posterior = red.muestrear(filas, grupo, muestras).numpy().astype(np.float64)                 # (muestras, b, 32)
        variables = nucleo_sv.variables_del_modelo(lote)
        con_theta_verdadero = nucleo_sv.paso_local_por_empresa(lote["theta"].astype(np.float64), variables)
        for i in range(b):
            falta = np.isnan(lote["evento"][i])
            de_la_red = nucleo_sv.paso_local(posterior[:, i], {c: v[i] for c, v in variables.items()})[falta]   # (personas, muestras)
            verdad = con_theta_verdadero[i][falta]
            dentro_red.append(validacion.dentro_del_rango((de_la_red < verdad[:, None]).sum(axis=1), muestras))
            p, bajo, alto = rapido.ajustar_y_predecir(lote["filas"][i])
            dentro_rapido.append((verdad >= bajo) & (verdad <= alto))
            p_red.append(de_la_red.mean(axis=1)), p_rapido.append(p), p_verdad.append(verdad), paso.append(lote["delta"][i][falta])
    paso = np.concatenate(paso)
    return {"empresas": empresas, "personas_por_decidir": int(len(paso)),
            "cobertura_90_red": round(float(np.concatenate(dentro_red).mean()), 3),
            "cobertura_90_metodo_rapido": round(float(np.concatenate(dentro_rapido).mean()), 3),
            "contra_lo_que_paso": {"red": rapido.metricas(np.concatenate(p_red), paso), "metodo_rapido": rapido.metricas(np.concatenate(p_rapido), paso),
                                   "theta_verdadero": rapido.metricas(np.concatenate(p_verdad), paso)}}


def comparar_con_mcmc(red, simulados: int, pasos: int, carpeta: Path, n: int = 1470, cadenas: int = 4, profundidad: int = 10) -> dict:
    """Red contra NUTS en empresas simuladas y en el archivo real. Guarda las muestras del real: es el plan B de la tarjeta.

    El archivo malo, ya corregido, tiene los mismos datos del modelo que el real: sus muestras se guardan con su clave.
    """
    entradas = [(f"simulado_{i:02d}", datos, verdadero) for i, (datos, verdadero) in enumerate(mcmc.simulados(simulados, n))]
    entradas.append((CASO, mcmc.datos_del_caso(CASO), None))
    diferencias, informe = [], []
    for clave, datos, verdadero in entradas:
        r = mcmc.correr(datos, calentamiento=pasos, muestras=pasos, cadenas=cadenas, semilla=len(informe), profundidad=profundidad)
        extra = {} if verdadero is None else {"theta_verdadero": verdadero}
        for una in ([CASO, f"{CASO_MALO}__quitar_factor-fecha_salida"] if clave == CASO else [clave]):
            mcmc.guardar(una, r, carpeta / "mcmc", **extra)
        filas = nucleo_sv.armar_filas(datos["x"], datos["w"], datos["encuestas"], datos["tiempo"], datos["evento"])
        de_la_red = red.muestrear(torch.from_numpy(filas[None]), torch.from_numpy(np.asarray(datos["grupo"])[None]), 1000)[:, 0].numpy().astype(np.float64)
        diferencia, razon_de_anchos = validacion.comparar_posteriores(de_la_red, r["theta"])
        falta = np.isnan(datos["evento"])
        en_p = np.abs(nucleo_sv.paso_local(de_la_red[:100], datos)[falta].mean(axis=1)
                      - nucleo_sv.paso_local(r["theta"][:: max(1, len(r["theta"]) // 100)].astype(np.float64), datos)[falta].mean(axis=1))
        diferencias.append(diferencia)
        informe.append({"clave": clave, "personas": int(len(falta)), "segundos": round(r["segundos"], 1), "r_hat_max": round(float(np.nanmax(r["r_hat"])), 3),
                        "n_eff_min": round(float(np.nanmin(r["n_eff"]))), "diferencia_media": round(float(diferencia.mean()), 3),
                        "diferencia_maxima": round(float(diferencia.max()), 3), "parametro_de_la_maxima": nucleo_sv.NOMBRES_THETA[int(diferencia.argmax())],
                        "razon_de_anchos_media": round(float(razon_de_anchos.mean()), 2),
                        "diferencia_media_en_p": round(float(en_p.mean()), 4), "diferencia_maxima_en_p": round(float(en_p.max()), 4)})
    diferencias = np.array(diferencias)
    return {"datasets": len(entradas), "pasos_por_cadena": pasos, "cadenas": cadenas,
            "s_por_dataset": round(float(np.mean([f["segundos"] for f in informe])), 1), "s_en_el_real": informe[-1]["segundos"],
            "diferencia_media": round(float(diferencias.mean()), 3), "diferencia_maxima": round(float(diferencias.max()), 3),
            "diferencia_en_el_real": round(float(diferencias[-1].mean()), 3), "r_hat_max": max(f["r_hat_max"] for f in informe),
            "por_dataset": informe}


def nube_y_archivos(carpeta: Path, simulaciones: int) -> dict:
    """Genera la nube con esta red y ubica los tres archivos del arco del demo: el real, el malo y el malo corregido.

    Genera también las nubes por tamaño para los archivos subidos (D-34) y ubica en ellas los archivos de prueba de la
    subida, que son más chicos que el del caso. Eso no entra al veredicto: va al informe.
    """
    generada = nube.generar(carpeta, simulaciones)
    por_tamano = nube.generar_por_tamano(carpeta, max(500, simulaciones * 2 // 5))
    def resumen(nombre, transformaciones):
        donde = nucleo_sv.nube(casos.cargar_caso(nombre), transformaciones)
        return {k: donde[k] for k in ("archivo", "detectores")}
    real, malo = resumen(CASO, []), resumen(CASO_MALO, [])
    propuesta = (nucleo_sv.analizar(casos.cargar_caso(CASO_MALO), [], {"falso_si": 1.0, "falso_no": 1.0})["semaforo"].get("propuesta") or {}).get("transformacion")
    corregido = resumen(CASO_MALO, [propuesta]) if propuesta else None
    subidos = {}
    for area in SUBIDOS:
        ruta = casos.RAIZ / "datos" / "demo" / f"subida_rotacion_{area}.csv"
        if ruta.exists():
            en_memoria = {**casos.cargar_caso(CASO), "nombre": f"subida_{area}", "tabla": casos.leer_columnas(ruta), "columnas": COLUMNAS_SUBIDOS}
            donde = nucleo_sv.nube(en_memoria, [])
            subidos[area] = {"personas": len(en_memoria["tabla"]["cargo"]), "archivo": donde["archivo"], "detectores": donde["detectores"]}
    return {"generada": generada, "archivo_real": real, "archivo_malo": malo, "propuesta_del_semaforo": propuesta, "archivo_malo_corregido": corregido,
            "por_tamano": por_tamano, "archivos_subidos": subidos}


def examen_y_latencia(empresas_de_la_cartera: int | None) -> dict:
    """El examen con los datos reales reservados, de la red y del método rápido; los milisegundos de un análisis (la mejor de 3) y la cartera."""
    from nucleo import api
    api.analizar(CASO)                                                    # carga la sesión de onnxruntime
    ms, respuesta = validacion.mejor_de_3(lambda: api.analizar(CASO))
    assert "error" not in respuesta, respuesta
    caso = casos.cargar_caso(CASO)
    salida = {"analizar_ms": ms, "semaforo": respuesta["semaforo"], "resumen_colores": respuesta["resumen_colores"], "factores": respuesta["factores"],
              "examen_red": None, "examen_metodo_rapido": rapido.examen(caso, *filas_reales(caso))}
    if respuesta["unidades"] is not None:
        verdad = {i: tabla.si_no(v) for i, v in zip(*(casos.leer_columnas(caso["verdad"])[k] for k in ("id", "objetivo")))}
        pares = np.array([(u["p"], verdad[u["id"]]) for u in respuesta["unidades"] if u["id"] in verdad])
        salida["examen_red"] = {"tramos": respuesta["examen"]["tramos"], "metricas": rapido.metricas(pares[:, 0], pares[:, 1])}
    if empresas_de_la_cartera is not None:
        caso = {**caso, "cartera": {**caso["cartera"], "n": empresas_de_la_cartera}}
    cartera = nucleo_sv.cartera(caso)
    salida["cartera"] = {"empresas": cartera["n_analisis"], "ms": cartera["tiempo_ms"], "personas_por_decidir": sum(f["n_unidades"] for f in cartera["filas"]),
                         "muestras_por_empresa": 8, "nodos": list(nucleo_sv.NODOS_CARTERA)}
    return salida


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--punto", type=Path, default=None, help="punto de guardado; por defecto, el más entrenado entre ultimo.pt y el pesos.pt exportado")
    p.add_argument("--salida", type=Path, default=ARTEFACTOS)
    p.add_argument("--sbc", type=int, default=2000, help="empresas simuladas nuevas para el SBC")
    p.add_argument("--unidades", type=int, default=100, help="empresas simuladas para la cobertura de lo que se decide")
    p.add_argument("--simulados", type=int, default=5, help="empresas simuladas para comparar con el MCMC")
    p.add_argument("--nube", type=int, default=5000, help="simulaciones del predictivo a priori para la nube")
    p.add_argument("--sin-mcmc", action="store_true", help="salta la comparación con el MCMC (queda sin medir y el sello no pasa)")
    p.add_argument("--maquina", default="MacBook Air M4 16 GB")
    p.add_argument("--ensayo", action="store_true", help="recorrido completo en chico, a una carpeta temporal: prueba el programa, no la red")
    a = p.parse_args()
    inicio = time.time()
    del_mcmc, empresas_de_la_cartera = {"pasos": 500}, None
    if a.ensayo:
        a.salida, a.sbc, a.unidades, a.simulados, a.nube = Path(tempfile.mkdtemp(prefix="krylov_sello_")) / "supervivencia", 100, 10, 1, 1500
        del_mcmc, empresas_de_la_cartera = {"pasos": 20, "n": 300, "cadenas": 2, "profundidad": 4}, 50
    if a.punto is None:
        a.punto = punto_mas_entrenado()

    red, estado = cargar_red(a.punto)
    a.salida.mkdir(parents=True, exist_ok=True)
    informe = {"punto": str(a.punto), "exportacion": exportar.exportar(red, a.salida)}
    for origen, destino in ((a.punto, a.salida / "pesos.pt"), (simular.RUTA_CONFIG, a.salida / "config.json")):
        if origen.resolve() != destino.resolve():
            shutil.copyfile(origen, destino)
    print(f"[1/6] {a.punto} ({estado['datasets_simulados']:,} simulaciones) exportado:".replace(",", "."), informe["exportacion"], flush=True)
    casos.ARTEFACTOS = a.salida.parent                                    # `nucleo` lee lo recién exportado
    os.environ["KRYLOV_MOTOR_SUPERVIVENCIA"] = "red"

    with torch.no_grad():
        informe["sbc"] = sbc(red, a.sbc)
        print("[2/6] SBC:", {k: v for k, v in informe["sbc"].items() if k != "theta"}, flush=True)
        informe["unidades"] = calibracion_de_unidades(red, a.unidades)
        print("[3/6] lo que se decide:", informe["unidades"], flush=True)
        informe["mcmc"] = None if a.sin_mcmc else comparar_con_mcmc(red, a.simulados, carpeta=a.salida, **del_mcmc)
        print("[4/6] MCMC:", "sin correr" if a.sin_mcmc else {k: v for k, v in informe["mcmc"].items() if k != "por_dataset"}, flush=True)
    informe["nube"] = nube_y_archivos(a.salida, a.nube)
    print("[5/6] nube:", {k: v for k, v in informe["nube"].items() if k != "por_tamano"}, flush=True)
    informe["real"] = examen_y_latencia(empresas_de_la_cartera)
    print("[6/6] examen y latencia:", {k: informe["real"][k] for k in ("analizar_ms", "semaforo", "examen_red", "examen_metodo_rapido", "cartera")}, flush=True)

    # Veredicto, con los umbrales de WORKPLAN.md 11.8 y los criterios comunes de los motores de tabla (motor/comun/validacion.py).
    del_sbc, del_mcmc_, nubes, real = informe["sbc"], informe["mcmc"], informe["nube"], informe["real"]
    sbc_pasa, fallan = validacion.sbc_sin_sesgo(del_sbc["theta"])
    cobertura_theta, cobertura_p = del_sbc["cobertura_90"], informe["unidades"]["cobertura_90_red"]
    malo_fuera = (not nubes["archivo_malo"]["archivo"]["dentro"]) and bool(nubes["archivo_malo_corregido"]) and nubes["archivo_malo_corregido"]["archivo"]["dentro"]
    criterios = {
        "sbc_sin_sesgo": sbc_pasa, "cobertura_parametros_entre_85_y_95": 0.85 <= cobertura_theta <= 0.95,
        "cobertura_de_lo_que_se_decide_entre_85_y_95": 0.85 <= cobertura_p <= 0.95, "peor_grupo_sobre_80": del_sbc["cobertura_90_peor_grupo"] >= 0.80,
        "mcmc_bajo_0_3": None if del_mcmc_ is None else del_mcmc_["diferencia_media"] < 0.3, "analisis_bajo_1_s": real["analizar_ms"] < 1000,
        "archivo_malo_fuera_y_corregido_dentro": malo_fuera, "archivo_real_dentro": nubes["archivo_real"]["archivo"]["dentro"],
    }
    sello = {
        "motor_id": "supervivencia", "implementacion": "red", "pasa": all(v is True for v in criterios.values()), "criterios": criterios,
        "simulaciones_entrenamiento": estado["datasets_simulados"], "entrenamiento_min": round(estado["segundos"] / 60),
        "casos_validacion": a.sbc, "cobertura_90": cobertura_p, "cobertura_90_parametros": cobertura_theta,
        "cobertura_90_peor_grupo": del_sbc["cobertura_90_peor_grupo"], "peor_grupo": {"n hasta 600": "empresas de hasta 600 personas", "n sobre 600": "empresas de más de 600 personas"}.get(del_sbc["peor_grupo"], "empresas con " + del_sbc["peor_grupo"]),
        "sbc_pasa": sbc_pasa, "sbc_parametros_que_fallan": fallan, "recuperacion": validacion.recuperacion(del_sbc["theta"]),
        "cobertura_90_metodo_rapido": informe["unidades"]["cobertura_90_metodo_rapido"], "latencia_ms": real["analizar_ms"],
        "mcmc_datasets_comparados": del_mcmc_ and del_mcmc_["datasets"], "mcmc_s_por_dataset": del_mcmc_ and del_mcmc_["s_por_dataset"],
        "mcmc_diferencia_media": del_mcmc_ and del_mcmc_["diferencia_media"], "mcmc_r_hat_max": del_mcmc_ and del_mcmc_["r_hat_max"],
        "amortizacion": {"que_se_compara": "un análisis completo de la empresa del caso (1.470 personas)",
                         "mcmc_s": del_mcmc_ and del_mcmc_["s_en_el_real"], "red_s": round(real["analizar_ms"] / 1000, 3)},
        "cartera": real["cartera"], "examen": real["examen_red"], "examen_metodo_rapido": real["examen_metodo_rapido"],
        "nube_malo_cae_fuera": malo_fuera, "nube_archivo_real_dentro": nubes["archivo_real"]["archivo"]["dentro"],
        "minutos_de_punta_a_punta": None, "fecha": dt.date.today().isoformat(), "maquina": a.maquina, "ensayo": bool(a.ensayo),
        "limitaciones": ["Empresas de 200 a 2.000 personas y de 3 a 12 cargos",
                         "«Riesgo» es la probabilidad de que la persona ya haya renunciado a la fecha de los datos, no de que renuncie en adelante",
                         "Los años en la empresa vienen en enteros: la verosimilitud es por intervalos de un año",
                         "Tres efectos lineales, el sueldo con un spline y cuatro encuestas de 1 a 4; otras columnas no entran al modelo",
                         "La censura (cuánto lleva cada persona al momento de la foto) se modela como LogNormal",
                         "Las covariables simuladas salen mitad del archivo del caso y mitad de un generador paramétrico: la red generaliza hasta donde llega ese generador"],
    }
    informe["minutos_del_sello"] = round((time.time() - inicio) / 60, 1)     # cuánto tardó esta validación, de exportar al veredicto
    validacion.escribir(a.salida, sello, informe)
    print(f"{informe['minutos_del_sello']} min", flush=True)


if __name__ == "__main__":
    main()
