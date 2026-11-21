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

import csv
import importlib
import io
import json
import os
import time

from nucleo import casos as _casos, decision, tabla as lector, textos
from nucleo.casos import MOTORES, ArchivoNoCalza, ErrorKrylov, bloque_costos, cargar_caso, costos_numericos, implementacion, nombres_del_inicio


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
    ruta = _casos.ARTEFACTOS / str(motor_id) / "sello.json"       # se lee al llamar: las pruebas y el sello cambian la carpeta
    if motor_id not in MOTORES or not ruta.exists():
        raise ErrorKrylov(f"El motor «{motor_id}» todavía no tiene sello.", "sin_sello")
    ficha = json.loads(ruta.read_text(encoding="utf-8"))
    ficha.setdefault("frases", textos.sello(ficha))
    return ficha


# =========================================================================================
# Un archivo propio (D-34, D-35): los papeles de columna de cada motor y `analizar_archivo`
# =========================================================================================
#
# El motor no depende del caso, pero sí del esquema: cada red practicó con datasets de ciertos papeles
# (el tiempo, el evento, el grupo, los factores…). `papeles` los publica; `analizar_archivo` arma un caso
# en memoria con el caso base del motor (rótulos, unidad, costos), la tabla subida y las columnas que el
# usuario confirmó para cada papel, y llama al mismo `analizar` del motor. Lo que no calza vuelve como
# semáforo rojo con su motivo, nunca como una excepción.

_AJENO_AL_ARCHIVO = ("dataset", "verdad", "grilla")              # del caso base, lo que habla del archivo del demo
_SIN_TRANSFORMAR = (None, "", "ninguna")


def _caso_base(motor_id: str) -> dict:
    """El primer caso del inicio que usa el motor: de ahí salen los rótulos, la unidad y los costos por omisión."""
    if motor_id not in MOTORES:
        raise ErrorKrylov(f"No conozco el modelo «{motor_id}».", "motor_desconocido")
    for nombre in nombres_del_inicio():
        if cargar_caso(nombre)["motor"] == motor_id:
            return cargar_caso(nombre)
    raise ErrorKrylov(f"El modelo «{motor_id}» no tiene un caso en el inicio.", "no_disponible")


def _papeles(motor_id: str) -> list[dict]:
    """`PAPELES` del módulo del motor con todos los campos del contrato; lo que un módulo no trae se completa aquí."""
    completos = []
    for p in _motor(motor_id, "PAPELES"):
        maximo = p.get("maximo", p.get("cantidad"))
        completos.append({"papel": p["papel"], "cantidad": maximo, "minimo": p.get("minimo", maximo), "maximo": maximo,
                          "tipo": p["tipo"], "texto": p["texto"], "texto_largo": p.get("texto_largo", p["texto"])})
    return completos


@_con_errores
def papeles(motor_id: str) -> dict:
    """Los papeles de columna que recibe la red del motor (cuántas columnas acepta cada uno y de qué tipo) y su caso base."""
    return {"motor_id": motor_id, "caso_base": _caso_base(motor_id)["nombre"], "papeles": _papeles(motor_id)}


def _celda(valor) -> str:
    return "" if valor is None or (isinstance(valor, float) and valor != valor) else str(valor)


def _columnas_de_texto(tabla) -> dict[str, list[str]]:
    """La tabla subida como columnas de texto. Acepta el CSV (bytes o texto), un diccionario columna → valores o un DataFrame."""
    if isinstance(tabla, (bytes, bytearray)):
        try:
            tabla = bytes(tabla).decode("utf-8-sig")
        except UnicodeDecodeError:
            tabla = bytes(tabla).decode("latin-1")
    if isinstance(tabla, str):
        primera = tabla.lstrip("\ufeff").split("\n", 1)[0]
        filas = list(csv.reader(io.StringIO(tabla.lstrip("\ufeff")), delimiter=";" if primera.count(";") > primera.count(",") else ","))
        filas = [fila for fila in filas if any(celda.strip() for celda in fila)]
        encabezado = [nombre.strip() for nombre in filas[0]] if filas else []
        if any(len(fila) != len(encabezado) for fila in filas):
            raise ArchivoNoCalza("El archivo no se lee como una tabla: hay filas con otra cantidad de celdas que el encabezado.")
        columnas = {nombre: [fila[j] for fila in filas[1:]] for j, nombre in enumerate(encabezado)}
    elif hasattr(tabla, "keys"):
        columnas = {str(nombre): [_celda(v) for v in tabla[nombre]] for nombre in tabla.keys()}
    else:
        raise ArchivoNoCalza("El archivo no se lee como una tabla.")
    largos = {len(valores) for valores in columnas.values()}
    if len(largos) > 1:
        raise ArchivoNoCalza("El archivo no se lee como una tabla: las columnas no tienen el mismo largo.")
    if not columnas or largos == {0}:
        raise ArchivoNoCalza("El archivo no tiene filas.")
    return columnas


def _calzar(motor_id: str, base: dict, tabla: dict[str, list[str]], columnas: dict) -> tuple[dict, dict]:
    """El calce que confirmó el usuario, validado: (tabla con las transformaciones aplicadas, columnas papel → nombre o lista).

    `columnas` trae por papel un nombre, una lista (una posición vacía va en None) o, desde D-35,
    `{"columnas": [...], "transformacion": {"nombre": ..., ...}}`. Las transformaciones son las de la lista cerrada de
    `nucleo/preproceso.py` (`TRANSFORMACIONES`: nombre → función de la columna, la tabla y sus parámetros); aquí solo se
    las llama. Un papel sin columnas bajo su mínimo es `rojo_datos`; con una cantidad que la red no practicó, `rojo_modelo`.

    El terreno es aparte: la transformación del valor medido (`log` o ninguna) la aplica el motor, que pasa el umbral por
    la misma y devuelve el mapa en las unidades del archivo. Ahí el calce no toca la tabla: fija `columnas.transformacion`.
    """
    from nucleo import preproceso
    conocidas = preproceso.TRANSFORMACIONES
    tabla = dict(tabla)
    lista = _papeles(motor_id)
    de_papel = {p["papel"] for p in lista} | {"tendencia", "extra", "disponibles", "elegidas_por"}
    # Lo que el caso base trae en `columnas` y no es un papel (en el terreno: umbral, unidad y transformación del valor) se conserva,
    # y el usuario puede cambiarlo. `tendencia` no pasa: un terreno subido no trae la distancia al río de cada bloque.
    col = {clave: columnas.get(clave, valor) for clave, valor in base["columnas"].items() if clave not in de_papel}
    for p in lista:
        pedido, transformacion = columnas.get(p["papel"]), None
        if isinstance(pedido, dict):
            pedido, transformacion = pedido.get("columnas"), pedido.get("transformacion")
        nombres = [] if pedido is None else [pedido] if isinstance(pedido, str) else [n or None for n in pedido]
        presentes = [n for n in nombres if n]
        if not presentes and p["minimo"] > 0:
            raise ArchivoNoCalza(f"Falta el papel «{p['papel']}»: {textos.minuscula_inicial(p['texto'])}.")
        if len(presentes) < p["minimo"] or len(nombres) > p["maximo"]:
            cuantas = f"exactamente {p['maximo']}" if p["minimo"] == p["maximo"] else f"entre {p['minimo']} y {p['maximo']}"
            raise ArchivoNoCalza(f"El papel «{p['papel']}» tiene {len(presentes)} columnas y la red practicó con {cuantas}.", "rojo_modelo")
        for nombre in presentes:
            lector.columna(tabla, nombre)
        nombre_t = (transformacion or {}).get("nombre")
        if p["papel"] == "valor" and "transformacion" in col and isinstance(columnas.get("valor"), dict) and nombre_t in (*_SIN_TRANSFORMAR, "log"):
            col["transformacion"] = None if nombre_t in _SIN_TRANSFORMAR else nombre_t
        elif nombre_t not in _SIN_TRANSFORMAR:
            if nombre_t not in conocidas:
                raise ArchivoNoCalza(f"La transformación «{nombre_t}» no está entre las que Krylov sabe aplicar.")
            parametros = {k: v for k, v in transformacion.items() if k != "nombre"}
            for nombre in presentes:
                try:
                    tabla[nombre] = [_celda(v) for v in conocidas[nombre_t](tabla[nombre], tabla, **parametros)]
                except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError):
                    raise ArchivoNoCalza(f"No se pudo aplicar «{nombre_t}» a la columna «{nombre}»: revisa sus valores y los parámetros.") from None
        if presentes:
            col[p["papel"]] = presentes[0] if p["maximo"] == 1 else nombres
    extra = [n for n in columnas.get("extra") or [] if n]
    for nombre in extra:
        lector.columna(tabla, nombre)
    return tabla, {**col, "extra": extra, "disponibles": len(tabla), "elegidas_por": "usuario"}


def _con_la_nube(motor_id: str, c: dict, propio: dict) -> dict:
    """Los dos detectores de la nube también sobre un archivo subido (D-34): si uno marca, `rojo_modelo` y no se responde.

    Un archivo propio cae fuera de lo que la red conoce mucho más seguido que uno del demo. Se consulta la `nube` del
    motor con el mismo caso en memoria; si el motor no tiene nube o todavía no está calculada, la respuesta no cambia.
    Igual que en rotación, `KRYLOV_NUBE_SEGUNDO_DETECTOR=aviso` deja en amarillo cuando solo marca el segundo detector.
    """
    if propio.get("semaforo", {"estado": "verde"})["estado"] != "verde":
        return propio
    try:
        donde = _motor(motor_id, "nube")(c, [])
    except ErrorKrylov:
        return propio
    if donde["archivo"]["dentro"]:
        return propio
    con_nombre = donde["detectores"]["ejes_con_nombre"]
    motivo = con_nombre["motivo"] or textos.frase("semaforo.rojo_modelo.no_se_parece") or ""
    if con_nombre["dentro"] and os.environ.get("KRYLOV_NUBE_SEGUNDO_DETECTOR", "rojo").strip().lower() == "aviso":
        return {**propio, "semaforo": {"estado": "amarillo", "motivo": motivo, "propuesta": None}}
    return {**propio, "unidades": None, "mapa": None, "factores": None, "examen": None,
            "semaforo": {"estado": "rojo_modelo", "motivo": motivo, "propuesta": None}}


def _respuesta(c: dict, nombre: str, numeros: dict, propio: dict, inicio: float) -> dict:
    """Lo común de una respuesta sobre lo propio del motor: el mismo armado que hace `analizar`, para un caso en memoria."""
    motor_id = c["motor"]
    impl = propio.get("implementacion", implementacion(motor_id))
    respuesta = {
        "caso": nombre, "motor_id": motor_id, "implementacion": impl, "precalculado": impl == "mcmc",
        "titular": None, "costo_de_no_saber": None,
        "costos": bloque_costos(c, numeros),
        "punto_de_corte": round(decision.punto_de_corte(numeros["falso_si"], numeros["falso_no"]), 3),
        "unidades": None, "resumen_colores": None, "factores": None, "columnas": None,
        "semaforo": {"estado": "verde", "motivo": "", "propuesta": None}, "examen": None,
        "sello_resumen": {"frase": "", "medido": False}, "en_palabras": [],
        "rotulos": c["rotulos"], "unidad": c["unidad"], "registro": [],
        "sintetico": False, "origen_datos": "Archivo subido por el usuario.",
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
    if respuesta["titular"] is None:
        respuesta["titular"] = textos.titular(c, respuesta["semaforo"], respuesta["resumen_colores"], total)
    if not respuesta["en_palabras"]:
        respuesta["en_palabras"] = textos.en_palabras(c, respuesta["resumen_colores"], respuesta["factores"])
    if respuesta["examen"] and not respuesta["examen"].get("frase"):
        respuesta["examen"]["frase"] = textos.examen(c, respuesta["examen"]) or ""
    respuesta.pop("costo_total", None)
    respuesta["tiempo_ms"] = round((time.perf_counter() - inicio) * 1000)
    return respuesta


def analizar_archivo(motor_id: str, tabla, columnas: dict, costos: dict | None = None, mediciones: list[dict] = ()) -> dict:
    """La respuesta de un archivo subido, con la forma de `analizar`: la misma red del motor, sobre las columnas del usuario.

    `tabla` es el archivo (CSV en bytes o texto, diccionario de columnas o DataFrame) y `columnas` el calce confirmado
    (papel → columna, lista de columnas o `{"columnas", "transformacion"}`). El caso en memoria es el caso base del motor
    sin su archivo ni sus respuestas reservadas (no hay examen: un archivo propio no trae respuestas escondidas) y, en el
    terreno, sin grilla ni tendencia. Si el archivo no calza, el semáforo sale `rojo_datos` o `rojo_modelo` con su motivo.
    Un archivo propio lo responde solo la red: con el motor en `mcmc` no hay nada precalculado para él y se dice.
    """
    inicio = time.perf_counter()
    try:
        base = _caso_base(motor_id)
        numeros = costos_numericos(base, costos)
    except ErrorKrylov as e:
        return e.a_dict()
    impl = implementacion(motor_id)
    c = {clave: valor for clave, valor in base.items() if clave not in _AJENO_AL_ARCHIVO}
    c["nombre"] = f"{base['nombre']}__archivo"                   # otra clave: nunca se sirve el MCMC precalculado del archivo del demo
    try:
        c["tabla"], c["columnas"] = _calzar(motor_id, base, _columnas_de_texto(tabla), columnas or {})
        argumentos = {"mediciones": list(mediciones)} if motor_id == "espacial" else {}
        propio = _con_la_nube(motor_id, c, _motor(motor_id, "analizar")(c, [], numeros, **argumentos))
    except ArchivoNoCalza as error:
        propio = {"implementacion": impl, **lector.rojo(c, error)}
    except ErrorKrylov as e:
        if impl != "red" and e.codigo == "no_disponible":
            return ErrorKrylov("Este modelo todavía no responde archivos propios: su red no está validada.", "no_disponible").a_dict()
        return e.a_dict()
    except Exception as error:                                   # noqa: BLE001 — contrato: un archivo subido nunca lanza un error al usuario
        propio = {"implementacion": impl, **lector.rojo(c, ArchivoNoCalza("No se pudo leer el archivo con estas columnas.")),
                  "registro": [f"error al leer: {type(error).__name__}"]}
    if motor_id == "espacial":
        propio.setdefault("mapa", None)                          # en rojo el terreno no trae mapa, y la clave existe igual
    return _respuesta(c, base["nombre"], numeros, propio, inicio)
