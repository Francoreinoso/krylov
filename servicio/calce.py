"""El calce de columnas: qué columna del archivo cumple cada papel del modelo (CONTRATO.md, secciones 5 y 6; D-35).

En los cuatro casos del demo el calce lo eligió el equipo y está escrito en `casos/<nombre>.yaml`
(`origen: "equipo"`). En un archivo propio lo propone el modelo de lenguaje (`origen: "modelo"`) o, sin
él, una regla por nombre y tipo de columna (`origen: "regla"`). Las dos formas son iguales, para que el
chat las muestre igual.
"""

import csv
import json
import re

from nucleo import api, preproceso
from nucleo.casos import ArchivoNoCalza, cargar_caso
from servicio import lenguaje
from servicio.fijos import RAIZ, PeticionInvalida


def _encabezado(caso: dict) -> list[str]:
    """Las columnas del CSV del caso; vacío si el archivo no está en este computador (inasistencias)."""
    ruta = RAIZ / caso.get("dataset", "")
    if not ruta.is_file():
        return []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f), [])


def calce_del_demo(nombre: str) -> dict:
    caso = cargar_caso(nombre)
    elegidas = caso["columnas"]
    papeles = api.papeles(caso["motor"])
    calce = {}
    for p in papeles["papeles"]:
        valor = elegidas.get(p["papel"])
        columnas = [valor] if isinstance(valor, str) else list(valor or [])
        transformacion = None
        if caso["motor"] == "espacial" and p["papel"] == "valor" and elegidas.get("transformacion"):
            transformacion = {"nombre": elegidas["transformacion"]}
        calce[p["papel"]] = {"columnas": columnas, "transformacion": transformacion,
                             "motivo": "Elegida por el equipo para este caso", "confianza": "alta"}
    usadas = {c for v in calce.values() for c in v["columnas"]}
    columnas = _encabezado(caso)
    return {"caso": nombre, "motor_id": caso["motor"], "calce": calce,
            "columnas": columnas, "no_usadas": [c for c in columnas if c not in usadas],
            "origen": "equipo", "precalculado": True}


# ------------------------------------------------------------------------------------------------
# El calce de un archivo propio (POST /api/calce, D-35): lo propone el modelo de lenguaje leyendo un
# resumen de cada columna, nunca las filas; sin modelo, o si su propuesta no valida, una regla por
# nombre y tipo de columna. En los dos casos el usuario lo ve y lo confirma antes de analizar.
# ------------------------------------------------------------------------------------------------

_SI_NO = {"si", "sí", "no", "yes", "y", "n", "true", "false", "verdadero", "falso", "1", "0"}
_COMPATIBLES = {"texto": {"texto", "numero", "entero", "si_no", "fecha"}, "si_no": {"si_no"},
                "numero": {"numero", "entero", "si_no"}, "entero": {"entero", "si_no"}}
EJEMPLOS_POR_COLUMNA = 3

SISTEMA_CALCE = """Eres Krylov, un data scientist artificial. Un modelo estadístico recibe columnas en papeles fijos. Te doy los papeles del modelo y un resumen de cada columna del archivo del usuario (nombre, tipo, valores distintos, rango, porcentaje vacío y tres ejemplos). Propón qué columna cumple cada papel.

Reglas:
- Cada papel lleva entre `minimo` y `maximo` columnas. Un papel con mínimo 0 es opcional: déjalo vacío si ninguna columna sirve.
- Una columna va en un solo papel. Las que no uses van en `no_usadas`.
- Una columna que solo tiene dato cuando la respuesta ya se sabe delata la respuesta: no la uses como factor.
- La transformación de un papel se aplica a todas sus columnas: si una columna no la necesita, no pongas transformación en ese papel.
- Usa una transformación solo para llevar la columna a las unidades que pide el papel (minutos a horas: `dividir` por 60; un porcentaje a una fracción entre 0 y 1: `dividir` por 100; una escala donde el límite es 120 a una donde es 1: `dividir` por 120), nunca para mejorar el modelo: el modelo ya considera efectos no lineales. Si la columna ya está en esas unidades, `ninguna`. Los parámetros que no usa la transformación van en null.
- Si viene `caso`, el papel `valor` es la columna que mide `lo_que_mide_el_valor` (no otra medida parecida) y lleva la `transformacion_del_valor` cuando viene una.
- `motivo`: una frase corta, sin jerga, que diga por qué esa columna cumple el papel.
- `confianza`: alta si el nombre y los valores calzan sin duda, media si es probable, baja si es una adivinanza."""


def _normalizar(texto: str) -> str:
    return texto.lower().translate(str.maketrans("áéíóúüñ", "aeiouun"))


def _tipo(valores: list[str]) -> str:
    if valores and all(v.lower() in _SI_NO for v in valores):
        return "si_no"
    try:
        numeros = [float(v.replace(",", ".")) for v in valores]
    except ValueError:
        return "fecha" if valores and all(re.fullmatch(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}", v) for v in valores) else "texto"
    return "entero" if all(n.is_integer() for n in numeros) else "numero"


def resumen_columnas(columnas: dict[str, list[str]]) -> list[dict]:
    """Por columna: nombre, tipo, valores distintos, rango, porcentaje vacío y tres ejemplos. Nunca filas completas."""
    resumen = []
    for nombre, valores in columnas.items():
        llenos = [v.strip() for v in valores if v.strip()]
        tipo = _tipo(llenos)
        numeros = [float(v.replace(",", ".")) for v in llenos] if tipo in ("numero", "entero") else []
        resumen.append({"nombre": nombre, "tipo": tipo, "distintos": len(set(llenos)),
                        "rango": [min(numeros), max(numeros)] if numeros else None,
                        "vacio_pct": round(100 * (1 - len(llenos) / max(len(valores), 1))),
                        "ejemplos": list(dict.fromkeys(llenos))[:EJEMPLOS_POR_COLUMNA]})
    return resumen


def _entrada(columnas: list[str], motivo: str, confianza: str, transformacion: dict | None = None) -> dict:
    return {"columnas": columnas, "transformacion": transformacion, "motivo": motivo, "confianza": confianza}


def calce_por_regla(papeles: list[dict], resumen: list[dict], pistas: dict[str, str] | None = None) -> dict:
    """Sin modelo de lenguaje: primero por el nombre de la columna, después por su tipo, en el orden de los papeles.

    `pistas` suma palabras a un papel (papel → texto), por ejemplo la unidad del valor que trae el YAML del caso."""
    libres = {c["nombre"]: c for c in resumen}
    calce = {}

    def tomar(p: dict, candidatas: list[str], motivo: str, confianza: str, hasta: int) -> None:
        elegidas = candidatas[:hasta]
        for nombre in elegidas:
            libres.pop(nombre)
        calce[p["papel"]] = _entrada(calce[p["papel"]]["columnas"] + elegidas if p["papel"] in calce else elegidas, motivo, confianza)

    def calza_el_nombre(nombre: str, palabras: set[str]) -> bool:
        partes = re.findall(r"[a-z]{3,}", _normalizar(nombre))
        return any(w.startswith(t) or t.startswith(w) for w in palabras for t in partes)

    for p in papeles:
        palabras = set(re.findall(r"[a-z]{4,}", _normalizar(f"{p['papel']} {p['texto']} {(pistas or {}).get(p['papel'], '')}")))
        por_nombre = [n for n, c in libres.items() if c["tipo"] in _COMPATIBLES[p["tipo"]] and calza_el_nombre(n, palabras)]
        tomar(p, por_nombre, "El nombre de la columna calza con lo que pide el papel", "media", p["maximo"])
    for p in papeles:
        faltan = p["minimo"] - len(calce[p["papel"]]["columnas"])
        if faltan <= 0:
            continue
        candidatas = [n for n, c in libres.items() if c["tipo"] in _COMPATIBLES[p["tipo"]]]
        familias: dict[str, list[str]] = {}               # PAGO_1 … PAGO_6: columnas que solo cambian en el número final
        for n in candidatas:
            familias.setdefault(re.sub(r"[_\s]*\d+$", "", n), []).append(n)
        familia = next((f for f in familias.values() if len(f) >= faltan > 1), None)
        if familia:
            tomar(p, familia, "Son columnas de la misma familia, una por período", "baja", faltan)
            continue
        if p["tipo"] == "texto":                      # el identificador distingue a cada fila; el grupo tiene pocos valores
            candidatas.sort(key=lambda n: libres[n]["distintos"], reverse=p["papel"] == "id")
        tomar(p, candidatas, f"Es la columna de tipo {p['tipo'].replace('_', ' o ')} que quedaba libre", "baja", faltan)
    return calce


def _nombre_dice(nombre: str, *raices: str) -> bool:
    partes = re.findall(r"[a-z]+", _normalizar(nombre))
    return any(t.startswith(r) for t in partes for r in raices)


def unidades_por_regla(papeles: list[dict], resumen: list[dict], calce: dict, tabla: dict[str, list[str]]) -> dict:
    """Sin modelo de lenguaje, dos conversiones de unidades que se leen en el nombre de la columna: un porcentaje
    cuando el papel pide una fracción entre 0 y 1 (÷ 100) y minutos cuando el papel pide horas (÷ 60)."""
    por_nombre = {c["nombre"]: c for c in resumen}
    for p in papeles:
        entrada = calce.get(p["papel"])
        if not entrada or len(entrada["columnas"]) != 1 or entrada["transformacion"]:
            continue
        columna = entrada["columnas"][0]
        pide = _normalizar(f"{p['texto']} {p['texto_largo']}")
        rango = por_nombre[columna]["rango"]
        if re.search(r"de 0 a 1|entre 0 y 1", pide) and (
                _nombre_dice(columna, "pct", "porc") or (rango and 1 < rango[1] <= 100)):
            t, motivo = {"nombre": "dividir", "por": 100}, "La columna viene en porcentaje y el papel pide una fracción: se divide por 100"
        elif re.search(r"\bhoras?\b", pide) and _nombre_dice(columna, "minut"):
            t, motivo = {"nombre": "dividir", "por": 60}, "La columna viene en minutos y el papel pide horas: se divide por 60"
        else:
            continue
        if _se_puede_aplicar(t, [columna], tabla):
            calce[p["papel"]] = _entrada([columna], motivo, "media", t)
    return calce


def _esquema_calce(papeles: list[dict], nombres: list[str]) -> dict:
    nulo = lambda tipo: {"anyOf": [tipo, {"type": "null"}]}   # noqa: E731
    transformacion = {
        "type": "object", "additionalProperties": False, "required": ["nombre", "por", "hasta", "desde", "de", "a"],
        "properties": {"nombre": {"type": "string", "enum": ["ninguna", *preproceso.TRANSFORMACIONES]},
                       "por": nulo({"type": "number"}), "hasta": nulo({"type": "string"}), "desde": nulo({"type": "string"}),
                       "de": nulo({"type": "array", "items": {"type": "number"}}), "a": nulo({"type": "array", "items": {"type": "number"}})}}
    papel = {"type": "object", "additionalProperties": False, "required": ["columnas", "transformacion", "motivo", "confianza"],
             "properties": {"columnas": {"type": "array", "items": {"type": "string", "enum": nombres}},
                            "transformacion": transformacion, "motivo": {"type": "string"},
                            "confianza": {"type": "string", "enum": ["alta", "media", "baja"]}}}
    return {"type": "object", "additionalProperties": False, "required": [*(p["papel"] for p in papeles), "no_usadas"],
            "properties": {**{p["papel"]: papel for p in papeles},
                           "no_usadas": {"type": "array", "items": {"type": "string", "enum": nombres}}}}


def _transformacion_valida(t: dict | None, nombres: set[str]) -> dict | None:
    """La transformación sin parámetros vacíos, o None si no hace falta o le falta lo que necesita."""
    if not isinstance(t, dict) or t.get("nombre") not in preproceso.TRANSFORMACIONES:
        return None
    t = {k: v for k, v in t.items() if v is not None}
    necesita = {"dividir": ("por",), "dias_entre": ("desde",), "reescalar_ordinal": ("de", "a")}.get(t["nombre"], ())
    if any(k not in t for k in necesita) or t.get("por") == 0 or ("desde" in t and t["desde"] not in nombres):
        return None
    return t


def _se_puede_aplicar(t: dict, columnas: list[str], tabla: dict[str, list[str]]) -> bool:
    """La transformación corre sobre cada columna del papel (la misma prueba que hará `analizar_archivo`)."""
    parametros = {k: v for k, v in t.items() if k != "nombre"}
    try:
        for nombre in columnas:
            preproceso.TRANSFORMACIONES[t["nombre"]](tabla[nombre], tabla, **parametros)
    except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError):
        return False
    return True


def validar(propuesto: dict, papeles: list[dict], tabla: dict[str, list[str]]) -> dict | None:
    """El calce del modelo, revisado por el código: columnas que existen, sin repetir, dentro de mínimo y máximo,
    y transformaciones que corren sobre sus columnas (la que no corre se descarta)."""
    existentes, usadas, calce = set(tabla), set(), {}
    for p in papeles:
        entrada = propuesto.get(p["papel"])
        if not isinstance(entrada, dict):
            return None
        columnas = [c for c in entrada.get("columnas") or [] if isinstance(c, str)]
        if not set(columnas) <= existentes or usadas & set(columnas) or len(set(columnas)) != len(columnas):
            return None
        if not p["minimo"] <= len(columnas) <= p["maximo"]:
            return None
        usadas |= set(columnas)
        confianza = entrada.get("confianza") if entrada.get("confianza") in ("alta", "media", "baja") else "baja"
        transformacion = _transformacion_valida(entrada.get("transformacion"), existentes)
        if transformacion and not _se_puede_aplicar(transformacion, columnas, tabla):
            transformacion = None
        calce[p["papel"]] = _entrada(columnas, str(entrada.get("motivo") or ""), confianza, transformacion)
    return calce


def _calce_por_modelo(papeles: list[dict], resumen: list[dict], tabla: dict[str, list[str]],
                      pistas: dict[str, str]) -> tuple[dict, str] | None:
    nombres = [c["nombre"] for c in resumen]
    pedido = {"papeles": [{k: p[k] for k in ("papel", "minimo", "maximo", "tipo", "texto_largo")} for p in papeles],
              "columnas": resumen}
    if pistas:                                                 # sin esto, en leyes elige el cobre en vez del arsénico
        pedido["caso"] = {"lo_que_mide_el_valor": pistas.get("valor"), "transformacion_del_valor": pistas.get("transformacion_valor")}
    escrito = lenguaje.pedir(SISTEMA_CALCE, json.dumps(pedido, ensure_ascii=False), _esquema_calce(papeles, nombres))
    if escrito is None:
        return None
    try:
        propuesto = json.loads(escrito[0])
    except json.JSONDecodeError:
        return None
    calce = validar(propuesto, papeles, tabla) if isinstance(propuesto, dict) else None
    return (calce, escrito[1]) if calce else None


def _pistas(caso: str | None, motor_id: str) -> dict[str, str]:
    """Lo que el YAML del caso dice del valor medido (`columnas.unidad_valor`, «ppm de arsénico», y su transformación):
    ayuda a la regla."""
    if not caso:
        return {}
    try:
        datos = cargar_caso(caso)
    except Exception:                                          # noqa: BLE001 — un caso desconocido solo deja sin pista
        return {}
    columnas = datos.get("columnas") or {}
    if datos.get("motor") != motor_id:
        return {}
    pistas = {"valor": columnas["unidad_valor"]} if isinstance(columnas.get("unidad_valor"), str) else {}
    if columnas.get("transformacion"):                         # en el terreno: la del valor medido del caso (`log`)
        pistas["transformacion_valor"] = columnas["transformacion"]
    return pistas


def proponer_calce(motor_id: str, contenido: bytes, caso: str | None = None) -> dict:
    """El calce de un archivo subido, con la forma de `calce_del_demo`. Lanza `PeticionInvalida` si el archivo no se lee.

    `caso` es la tarjeta elegida en el chat: de su YAML sale una pista para la regla (el modelo de lenguaje no la necesita)."""
    respuesta = api.papeles(motor_id)
    if "error" in respuesta:
        raise PeticionInvalida(respuesta["error"], respuesta["codigo"])
    try:
        columnas = api._columnas_de_texto(contenido)                 # el mismo lector que usa `analizar_archivo`
    except ArchivoNoCalza as e:
        raise PeticionInvalida(e.motivo, "archivo_ilegible") from None
    resumen = resumen_columnas(columnas)
    pistas = _pistas(caso, motor_id)
    del_modelo = _calce_por_modelo(respuesta["papeles"], resumen, columnas, pistas)
    if del_modelo:
        (calce, proveedor), origen = del_modelo, "modelo"
    else:
        calce = calce_por_regla(respuesta["papeles"], resumen, pistas)
        valor = calce.get("valor")
        if pistas.get("transformacion_valor") and valor and valor["columnas"]:
            valor["transformacion"] = {"nombre": pistas["transformacion_valor"]}
            valor["motivo"] = "El nombre calza con lo que mide el caso; se usa la misma escala que en el archivo del demo"
        calce, proveedor, origen = unidades_por_regla(respuesta["papeles"], resumen, calce, columnas), None, "regla"
    usadas = {c for v in calce.values() for c in v["columnas"]}
    nombres = list(columnas)
    return {"caso": None, "motor_id": motor_id, "calce": calce, "columnas": nombres,
            "no_usadas": [c for c in nombres if c not in usadas], "origen": origen, "proveedor": proveedor,
            "precalculado": False}
