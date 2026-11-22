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
import re
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


def _sello_resumen(motor_id: str, impl: str) -> dict:
    """El pie de una respuesta: con cuánto practicó la red y su cobertura, del sello del motor. Solo si respondió la red y el sello pasa."""
    ruta = _casos.ARTEFACTOS / str(motor_id) / "sello.json"
    if impl != "red" or not ruta.exists():
        return {"frase": "", "medido": False}
    ficha = json.loads(ruta.read_text(encoding="utf-8"))
    frases = textos.sello(ficha)[:2] if ficha.get("pasa") is True else []      # «practicó con…» y la cobertura del 90%
    return {"frase": " ".join(frases), "medido": bool(frases)}


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
            "empresa_o_industria": caso["tarjeta"]["empresa_o_industria"],
            "quien": caso["tarjeta"].get("quien"), "archivo": caso["tarjeta"].get("archivo"),     # quién decide y qué archivo sube (D-42)
            "motor": caso["motor"], "sintetico": bool(caso.get("sintetico", False)),
            "origen_datos": caso["origen_datos"],
        })
    return {"casos": tarjetas}


@_con_errores
def analizar(caso: str, transformaciones: list[str] = (), costos: dict | None = None, mediciones: list[dict] = ()) -> dict:
    """La respuesta completa de un caso: decisión por unidad (o por bloque), qué pesa, examen y semáforo."""
    inicio = time.perf_counter()
    c = cargar_caso(caso)
    numeros = costos_numericos(c, costos)
    argumentos = {"mediciones": list(mediciones)} if c["motor"] == "espacial" else {}
    propio = _motor(c["motor"], "analizar")(c, list(transformaciones), numeros, **argumentos)
    return _respuesta(c, caso, numeros, propio, inicio)


@_con_errores
def donde_medir(caso: str, mediciones: list[dict] = ()) -> dict:
    """Solo casos espaciales: los tres lugares donde una medición más vale más plata."""
    c = cargar_caso(caso)
    if c["motor"] != "espacial":
        raise ErrorKrylov("«¿Dónde perforo?» solo existe en la decisión con mapa.", "sin_mapa")
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
_SOLO_DEL_DEMO = ("ventana",)                                    # de `columnas` del caso base, lo que describe al archivo del demo y no se hereda:
                                                                 # `sismico` toma la ventana del calce o, si no viene, de la hora del último sismo


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


def _rangos(motor_id: str) -> dict | None:
    """Los tamaños de dataset con que practicó la red (D-38): `RANGOS` del módulo del motor, el mismo diseño de su `config.json`."""
    try:
        return dict(_motor(motor_id, "RANGOS"))
    except ErrorKrylov:
        pass
    ruta = _casos.ARTEFACTOS / motor_id / "config.json"
    prior = json.loads(ruta.read_text(encoding="utf-8")).get("prior", {}) if motor_id == "espacial" and ruta.exists() else {}
    if "n_min" not in prior:
        return None
    return {"muestras": {"minimo": prior["n_min"], "maximo": prior["n_max"]},
            "frase": f"Practiqué con bancos de {prior['n_min']} a {prior['n_max']} muestras."}


@_con_errores
def papeles(motor_id: str) -> dict:
    """Los papeles de columna que recibe la red del motor (cuántas columnas acepta cada uno y de qué tipo) y su caso base."""
    respuesta = {"motor_id": motor_id, "caso_base": _caso_base(motor_id)["nombre"], "papeles": _papeles(motor_id)}
    rangos = _rangos(motor_id)
    return {**respuesta, "rangos": rangos} if rangos else respuesta


def _celda(valor) -> str:
    return "" if valor is None or (isinstance(valor, float) and valor != valor) else str(valor)


_SEPARADORES = (",", ";", "\t")
_NUMERO_CON_COMA = re.compile(r"[-+]?(\d+|\d{1,3}(\.\d{3})+)(,\d+)?")      # 0,85 · 1.234,5 · 12: como lo escribe Excel en español
_NO_ES_CSV = ("Esto no parece un CSV: puede ser un Excel, una imagen o un PDF. En Excel, «Guardar como» y elige "
              "«CSV (delimitado por comas)», y sube ese archivo.")


def _texto_del_archivo(contenido: bytes) -> str:
    """Los bytes de un CSV como texto: UTF-8 (con o sin BOM), UTF-16 (el «texto Unicode» de Excel) o Windows-1252/latin-1."""
    if contenido[:4] == b"PK\x03\x04":                         # un .xlsx es un zip
        raise ArchivoNoCalza(_NO_ES_CSV)
    if contenido[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return contenido.decode("utf-16")
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            return contenido.decode(codificacion)
        except UnicodeDecodeError:
            pass
    return contenido.decode("latin-1")                          # nunca falla: cada byte es una letra


def _decimales_con_punto(columnas: dict[str, list[str]]) -> dict[str, list[str]]:
    """Las columnas escritas con coma decimal (y punto de miles), pasadas a punto decimal. Solo si toda la columna se lee así."""
    for nombre, valores in columnas.items():
        llenos = [v.strip() for v in valores if v.strip()]
        if any("," in v for v in llenos) and all(_NUMERO_CON_COMA.fullmatch(v) for v in llenos):
            columnas[nombre] = [v.strip().replace(".", "").replace(",", ".") for v in valores]
    return columnas


def _leer_csv(texto: str) -> dict[str, list[str]]:
    """Un CSV en texto a columnas. El separador (coma, punto y coma o tabulación) sale de la primera fila."""
    texto = texto.lstrip("\ufeff").replace("\x00", "")
    if not texto.strip():
        raise ArchivoNoCalza("El archivo está vacío: sube un CSV con una fila de encabezados y tus datos debajo.")
    if sum(not (c.isprintable() or c in "\t\r\n") for c in texto[:4096]) > 0.01 * min(len(texto), 4096):
        raise ArchivoNoCalza(_NO_ES_CSV)
    primera = texto.split("\n", 1)[0]
    separador = max(_SEPARADORES, key=primera.count)
    filas = []
    try:
        for n, fila in enumerate(csv.reader(io.StringIO(texto), delimiter=separador), start=1):
            if any(celda.strip() for celda in fila):
                filas.append((n, fila))
    except csv.Error:
        raise ArchivoNoCalza("El archivo no se lee como una tabla: revisa que las comillas estén cerradas.") from None
    encabezado = [nombre.strip() for nombre in filas[0][1]]
    while encabezado and not encabezado[-1]:                      # Excel deja separadores sobrantes al final de la fila
        encabezado.pop()
    if "" in encabezado:
        raise ArchivoNoCalza(f"La columna {encabezado.index('') + 1} no tiene nombre en el encabezado: ponle uno.")
    repetida = next((nombre for nombre in encabezado if encabezado.count(nombre) > 1), None)
    if repetida:
        raise ArchivoNoCalza(f"La columna «{repetida}» aparece dos veces en el encabezado: cambia uno de los nombres.")
    if len(filas) == 1:
        raise ArchivoNoCalza("El archivo trae solo la fila de encabezados, sin datos: agrega tus mediciones debajo.")
    ancho = len(encabezado)
    for n, fila in filas[1:]:
        if len(fila) < ancho or any(celda.strip() for celda in fila[ancho:]):
            nombre_sep = {",": "coma", ";": "punto y coma", "\t": "tabulación"}[separador]
            raise ArchivoNoCalza(f"La fila {n} tiene {len(fila)} valores y el encabezado {ancho} columnas: revisa que todas las filas "
                                 f"usen el mismo separador ({nombre_sep}) y que ningún texto lo lleve adentro sin comillas.")
    return _decimales_con_punto({nombre: [fila[j] for _, fila in filas[1:]] for j, nombre in enumerate(encabezado)})


def leer_tabla(tabla) -> dict[str, list[str]]:
    """La tabla subida como columnas de texto. Acepta el CSV (bytes o texto), un diccionario columna → valores o un DataFrame.

    Lo que no se puede leer lanza `ArchivoNoCalza` con una frase que dice qué pasó y qué hacer. La usan `analizar_archivo`
    y el calce de `servicio/`, así los dos leen el archivo igual."""
    if isinstance(tabla, (bytes, bytearray)):
        tabla = _texto_del_archivo(bytes(tabla))
    if isinstance(tabla, str):
        columnas = _leer_csv(tabla)
    elif hasattr(tabla, "keys"):
        columnas = {str(nombre): [_celda(v) for v in tabla[nombre]] for nombre in tabla.keys()}
    else:
        raise ArchivoNoCalza("El archivo no se lee como una tabla: súbelo como CSV, con una fila de encabezados.")
    largos = {len(valores) for valores in columnas.values()}
    if len(largos) > 1:
        raise ArchivoNoCalza("El archivo no se lee como una tabla: las columnas no tienen el mismo largo. Revisa que cada fila traiga un valor por columna.")
    if not columnas or largos == {0}:
        raise ArchivoNoCalza("El archivo no tiene filas de datos: agrega tus mediciones bajo los encabezados.")
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
    for clave in _SOLO_DEL_DEMO:                                 # p. ej. la ventana observada: la del archivo subido es la suya, no la del demo
        if clave in col and clave not in columnas:
            del col[clave]
    for p in lista:
        pedido, transformacion = columnas.get(p["papel"]), None
        if isinstance(pedido, dict):
            pedido, transformacion = pedido.get("columnas"), pedido.get("transformacion")
        nombres = [] if pedido is None else [pedido] if isinstance(pedido, str) else [n or None for n in pedido]
        presentes = [n for n in nombres if n]
        if not presentes and p["minimo"] > 0:
            raise ArchivoNoCalza(f"Falta la columna de «{p['papel']}» ({textos.minuscula_inicial(p['texto'])}): elige cuál de tus columnas lo trae.")
        if len(presentes) < p["minimo"] or len(nombres) > p["maximo"]:
            cuantas = f"exactamente {p['maximo']}" if p["minimo"] == p["maximo"] else f"entre {p['minimo']} y {p['maximo']}"
            raise ArchivoNoCalza(f"El papel «{p['papel']}» tiene {len(presentes)} columnas y la red practicó con {cuantas}: deja {cuantas} en ese papel.", "rojo_modelo")
        for nombre in presentes:
            lector.columna(tabla, nombre)
        nombre_t = (transformacion or {}).get("nombre")
        if p["papel"] == "valor" and "transformacion" in col and isinstance(columnas.get("valor"), dict) and nombre_t in (*_SIN_TRANSFORMAR, "log"):
            col["transformacion"] = None if nombre_t in _SIN_TRANSFORMAR else nombre_t
        elif nombre_t not in _SIN_TRANSFORMAR:
            if nombre_t not in conocidas:
                raise ArchivoNoCalza(f"La transformación «{nombre_t}» no está entre las que Krylov sabe aplicar: elige otra o ninguna.")
            parametros = {k: v for k, v in transformacion.items() if k != "nombre"}
            for nombre in presentes:
                try:
                    tabla[nombre] = [_celda(v) for v in conocidas[nombre_t](tabla[nombre], tabla, **parametros)]
                except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError):
                    motivo = lector.no_es_numero(nombre, tabla[nombre]) if nombre_t in ("dividir", "log") else None
                    raise ArchivoNoCalza(motivo or f"No se pudo aplicar «{nombre_t}» a la columna «{nombre}»: revisa sus valores y los parámetros.") from None
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


_ESCENA = ("umbral", "horizonte", "tiempo_final", "magnitud_minima", "unidad_tiempo", "unidad_valor", "eje_tiempo", "eje_valor")


def _respuesta(c: dict, nombre: str, numeros: dict, propio: dict, inicio: float) -> dict:
    """Lo común de una respuesta sobre lo propio del motor: costos, punto de corte, total, titular, rótulos y textos.

    La usan `analizar` (un caso del demo) y `analizar_archivo` (un caso en memoria con el archivo subido)."""
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
        "sintetico": bool(c.get("sintetico", False)), "origen_datos": c["origen_datos"],
        # Lo que dibuja la escena del caso (D-42): el límite, el horizonte y los nombres de los ejes, del YAML o del calce.
        "escena": {k: c["columnas"][k] for k in _ESCENA if c["columnas"].get(k) is not None},
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
    if not respuesta["sello_resumen"]["frase"]:
        respuesta["sello_resumen"] = _sello_resumen(motor_id, impl)
    respuesta.pop("costo_total", None)
    respuesta["tiempo_ms"] = round((time.perf_counter() - inicio) * 1000)
    return respuesta


_OTRA_ESCALA = ("Los números del archivo no se parecen a nada con que practicó el modelo: alguna columna parece venir en otra "
                "escala o en otra unidad. Revisa la unidad de cada columna que asignaste (por ejemplo, minutos en vez de horas, "
                "o un porcentaje en vez de una fracción), agrégale la transformación que la lleva a la que pide el papel y "
                "vuelve a intentar.")


def _todo_finito(respuesta: dict) -> bool:
    try:
        json.dumps(respuesta, allow_nan=False)
    except ValueError:
        return False
    return True


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
    c["sintetico"], c["origen_datos"] = False, "Archivo subido por el usuario."
    try:
        c["tabla"], c["columnas"] = _calzar(motor_id, base, leer_tabla(tabla), columnas or {})
        argumentos = {"mediciones": list(mediciones)} if motor_id == "espacial" else {}
        propio = _con_la_nube(motor_id, c, _motor(motor_id, "analizar")(c, [], numeros, **argumentos))
    except ArchivoNoCalza as error:
        propio = {"implementacion": impl, **lector.rojo(c, error)}
    except ErrorKrylov as e:
        if impl != "red" and e.codigo == "no_disponible":
            return ErrorKrylov("Este modelo todavía no responde archivos propios: su red no está validada. Prueba con otra decisión.", "no_disponible").a_dict()
        return e.a_dict()
    except Exception as error:                                   # noqa: BLE001 — contrato: un archivo subido nunca lanza un error al usuario
        propio = {"implementacion": impl, **lector.rojo(c, ArchivoNoCalza("No se pudo leer el archivo con estas columnas: revisa qué columna asignaste a cada papel.")),
                  "registro": [f"error al leer: {type(error).__name__}"]}
    if not _todo_finito(propio):                                 # una columna en otra escala saca a la red de lo que conoce y deja NaN
        propio = {"implementacion": impl, **lector.rojo(c, ArchivoNoCalza(_OTRA_ESCALA, "rojo_modelo"))}
    if motor_id == "espacial":
        propio.setdefault("mapa", None)                          # en rojo el terreno no trae mapa, y la clave existe igual
    return _respuesta(c, base["nombre"], numeros, propio, inicio)
