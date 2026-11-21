"""Lo que `amortizacion` le entrega a `producto` (`contratos/CONTRATO.md`, sección 2).

Funciones puras que devuelven diccionarios listos para convertir a JSON, con la forma de
los ejemplos de `contratos/ejemplos/`. Solo NumPy, PyYAML y onnxruntime: aquí no entran
torch, zuko, jax ni numpyro.

Cada motor vive en `nucleo/<motor_id>.py` y expone `analizar(caso, transformaciones, costos)`
(el espacial recibe además `mediciones`), donde `caso` es el diccionario del YAML y
`costos` son números ya resueltos. Devuelve lo propio del motor: `unidades` o `mapa`,
`factores`, `examen`, `semaforo`, `registro`, `implementacion`. Esta capa agrega lo
común: costos, punto de corte, total de «lo que cuesta no saber», titular, rótulos.

Un motor responde con su red (`red`) o con el posterior del MCMC de referencia
precalculado (`mcmc`, rotulado «precalculado»), según `KRYLOV_MOTOR_<ID>`.

Si algo no se puede responder, la función devuelve `{"error": frase, "codigo": ...}` y
`producto` sigue con el ejemplo fijo.
"""

from __future__ import annotations

import importlib
import json
import time

from nucleo import decision, textos
from nucleo.casos import ARTEFACTOS, MOTORES, ErrorKrylov, bloque_costos, cargar_caso, costos_numericos, implementacion, nombres_del_inicio


def _motor(motor_id: str, funcion: str):
    """La función `funcion` del módulo del motor, o un error en español si todavía no existe."""
    try:
        return getattr(importlib.import_module(f"nucleo.{motor_id}"), funcion)
    except (ModuleNotFoundError, AttributeError):
        raise ErrorKrylov(f"El motor «{motor_id}» todavía no responde «{funcion}».", "no_disponible") from None


def _con_errores(f):
    def envuelta(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ErrorKrylov as e:
            return e.a_dict()
    envuelta.__name__, envuelta.__doc__ = f.__name__, f.__doc__
    return envuelta


@_con_errores
def casos() -> dict:
    """Las tarjetas del inicio, en el orden de `casos/INICIO`."""
    tarjetas = []
    for nombre in nombres_del_inicio():
        caso = cargar_caso(nombre)
        if caso["tarjeta"].get("oculto"):
            continue
        tarjetas.append({
            "nombre": caso["nombre"], "titulo": caso["tarjeta"]["titulo"],
            "empresa_o_industria": caso["tarjeta"]["empresa_o_industria"], "sponsor": caso["tarjeta"].get("sponsor"),
            "motor": caso["motor"], "sintetico": bool(caso.get("sintetico", False)),
            "origen_datos": caso["origen_datos"], "tiene_cartera": "cartera" in caso,
        })
    return {"casos": tarjetas}


@_con_errores
def analizar(caso: str, transformaciones: list[str] = (), costos: dict | None = None, mediciones: list[dict] = ()) -> dict:
    """La respuesta completa de un caso: decisión por unidad (o por bloque), qué pesa, examen y semáforo."""
    inicio = time.perf_counter()
    c = cargar_caso(caso)
    motor_id = c["motor"]
    numeros = costos_numericos(c, costos)
    argumentos = {"mediciones": list(mediciones)} if motor_id == "espacial" else {}
    propio = _motor(motor_id, "analizar")(c, list(transformaciones), numeros, **argumentos)

    impl = propio.get("implementacion", implementacion(motor_id))
    respuesta = {
        "caso": caso, "motor_id": motor_id, "implementacion": impl, "precalculado": impl == "mcmc",
        "titular": None, "costo_de_no_saber": None,
        "costos": bloque_costos(c, numeros),
        "punto_de_corte": round(decision.punto_de_corte(numeros["falso_si"], numeros["falso_no"]), 3),
        "unidades": None, "resumen_colores": None, "factores": None, "columnas": None,
        "semaforo": {"estado": "verde", "motivo": "", "propuesta": None}, "examen": None,
        "sello_resumen": {"frase": "", "medido": False}, "en_palabras": [],
        "rotulos": c["rotulos"], "unidad": c["unidad"], "registro": [],
        "sintetico": bool(c.get("sintetico", False)), "origen_datos": c["origen_datos"],
    }
    respuesta.update(propio)

    total = None
    if not respuesta["semaforo"]["estado"].startswith("rojo"):
        total = propio.get("costo_total")
        if total is None and respuesta["unidades"] is not None:
            total = sum(u["duda"] for u in respuesta["unidades"])
        if respuesta["resumen_colores"] is None and respuesta["unidades"] is not None:
            respuesta["resumen_colores"] = decision.resumen_colores([u["estado"] for u in respuesta["unidades"]])
        if total is not None:
            respuesta["costo_de_no_saber"] = {"valor": round(total), "moneda": c["moneda"]}
    # Los textos salen de las plantillas de casos/textos.yaml, llenadas con estos números. Lo que el motor ya trajo, se respeta.
    if respuesta["titular"] is None:
        respuesta["titular"] = textos.titular(c, respuesta["semaforo"], respuesta["resumen_colores"], total)
    if not respuesta["en_palabras"]:
        respuesta["en_palabras"] = textos.en_palabras(c, respuesta["resumen_colores"], respuesta["factores"])
    if respuesta["examen"] and not respuesta["examen"].get("frase"):
        respuesta["examen"]["frase"] = textos.examen(c, respuesta["examen"]) or ""
    respuesta.pop("costo_total", None)
    respuesta["tiempo_ms"] = round((time.perf_counter() - inicio) * 1000)
    return respuesta


@_con_errores
def cartera(caso: str) -> dict:
    """Todas las empresas de una cartera, analizadas de una vez y ordenadas por lo que les cuesta no saber."""
    c = cargar_caso(caso)
    if "cartera" not in c:
        raise ErrorKrylov(f"El caso «{caso}» no tiene cartera.", "sin_cartera")
    return _motor(c["motor"], "cartera")(c)


@_con_errores
def donde_medir(caso: str, mediciones: list[dict] = ()) -> dict:
    """Solo casos espaciales: los tres lugares donde una medición más vale más plata."""
    c = cargar_caso(caso)
    if c["motor"] != "espacial":
        raise ErrorKrylov("«¿Dónde mido?» solo existe para casos con mapa.", "sin_mapa")
    return _motor("espacial", "donde_medir")(c, costos_numericos(c, None), list(mediciones))


@_con_errores
def nube(caso: str, transformaciones: list[str] = ()) -> dict:
    """Dónde cae el archivo respecto de las simulaciones con que practicó el motor."""
    c = cargar_caso(caso)
    return _motor(c["motor"], "nube")(c, list(transformaciones))


@_con_errores
def sello(motor_id: str) -> dict:
    """La ficha técnica de un motor: `motor/artefactos/<motor_id>/sello.json` más `frases`."""
    ruta = ARTEFACTOS / str(motor_id) / "sello.json"
    if motor_id not in MOTORES or not ruta.exists():
        raise ErrorKrylov(f"El motor «{motor_id}» todavía no tiene sello.", "sin_sello")
    ficha = json.loads(ruta.read_text(encoding="utf-8"))
    ficha.setdefault("frases", textos.sello(ficha))
    return ficha
