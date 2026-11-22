"""La interpretación de una respuesta: un texto corto escrito por el modelo de lenguaje desde el JSON del motor (D-34).

El modelo no agrega números. Cada número del texto tiene que estar en el JSON, tal cual o redondeado (también como
porcentaje, en miles o en millones); si uno no está, o si no hay modelo que responda, se devuelve la plantilla: las
frases de `en_palabras`, que ya llenó `nucleo/` con las plantillas de `casos/textos.yaml` (regla 11 de AGENTS.md).
"""

from __future__ import annotations

import json
import re

from servicio import lenguaje

SISTEMA = """Eres la voz de Krylov, un data scientist artificial. Recibes el JSON de una respuesta que ya calculó un motor estadístico y escribes su interpretación: dos o tres frases cortas, en español de Chile, para alguien que no sabe estadística ni conoce la operación. Si usas una palabra técnica del rubro que trae el JSON, explícala en pocas palabras.

Reglas:
- Usa solo números que aparecen en el JSON. Puedes redondearlos y escribir una proporción como porcentaje (0,28 es 28%). No calcules números nuevos: ni sumas, ni restas, ni diferencias, ni promedios.
- Escribe los miles con punto (7.420) y los decimales con coma (2,7). La plata va con su moneda, como en el JSON (US$ 7.420).
- Los colores son decisiones, no pronósticos. Usa los rótulos de `rotulos` tal cual. Nunca afirmes que algo va a pasar o que va a fallar: di lo que conviene hacer.
- Si la decisión toca la seguridad de personas, Krylov apoya la decisión del especialista: no la reemplaza ni promete evitar accidentes.
- «Lo que te cuesta no saber» es la plata que se ahorraría, en promedio, si la duda se despejara antes de decidir.
- Si un factor tiene certeza «no_se_sabe», di que con estos datos no se puede saber si sube o baja el riesgo.
- Sin jerga. No digas posterior, bayesiano, MCMC, red neuronal, intervalo, calibración, modelo generativo, regresión, coeficiente ni umbral (di «punto de corte»).
- Si el semáforo es rojo, explica en una frase por qué no se responde y qué propone Krylov.
- No recomiendes nada que no esté en el JSON. Sin saludos, sin listas y sin títulos.

Responde solo con el texto."""

UNIDADES_PARA_LEER = 5
_NUMERO = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?")


def reducir(respuesta: dict) -> dict:
    """Lo que el modelo necesita leer: sin `muestras_p`, sin el mapa y solo las unidades de más riesgo."""
    claves = ("titular", "costo_de_no_saber", "resumen_colores", "punto_de_corte", "costos", "factores",
              "semaforo", "examen", "unidad", "rotulos", "en_palabras", "implementacion", "origen_datos")
    reducida = {k: respuesta[k] for k in claves if respuesta.get(k) is not None}
    unidades = sorted(respuesta.get("unidades") or [], key=lambda u: -u.get("p", 0))
    if unidades:
        reducida["unidades_de_mas_riesgo"] = [
            {k: u[k] for k in ("etiqueta", "p", "rango_bajo", "rango_alto", "estado") if k in u}
            for u in unidades[:UNIDADES_PARA_LEER]]
        reducida["n_unidades"] = len(unidades)
    return reducida


def _numeros_del_json(obj) -> list[float]:
    if isinstance(obj, bool):
        return []
    if isinstance(obj, (int, float)):
        return [float(obj)]
    if isinstance(obj, dict):
        return [x for v in obj.values() for x in _numeros_del_json(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in _numeros_del_json(v)]
    if isinstance(obj, str):
        return [n for n, _ in numeros_del_texto(obj)]
    return []


def numeros_permitidos(respuesta: dict) -> list[float]:
    """Cada número del JSON y sus formas escritas: como porcentaje, en miles y en millones. El 1 siempre vale («1 persona»)."""
    base = _numeros_del_json(respuesta) + [1.0]
    return base + [100 * x for x in base if abs(x) <= 1] + [x / 1_000 for x in base] + [x / 1_000_000 for x in base]


def numeros_del_texto(texto: str) -> list[tuple[float, int]]:
    """Los números escritos en formato chileno, con cuántos decimales trae cada uno: «7.420» → (7420, 0), «2,7» → (2.7, 1)."""
    numeros = []
    for m in _NUMERO.finditer(texto):
        escrito = m.group().replace(".", "")
        entero, _, decimales = escrito.partition(",")
        numeros.append((float(f"{entero}.{decimales}" if decimales else entero), len(decimales)))
    return numeros


def solo_numeros_del_json(texto: str, respuesta: dict) -> bool:
    permitidos = numeros_permitidos(respuesta)
    return all(any(round(x, decimales) == valor for x in permitidos) for valor, decimales in numeros_del_texto(texto))


def plantilla(respuesta: dict) -> dict:
    texto = " ".join(respuesta.get("en_palabras") or []) or respuesta.get("titular") or ""
    return {"texto": texto, "origen": "plantilla", "proveedor": None,
            "propuesto_por": lenguaje.propuesto_por(None, "plantilla"), "precalculado": False}


def interpretar(respuesta: dict, solo_claude: bool = False) -> dict:
    """`{texto, origen, proveedor, propuesto_por, precalculado}`. Con `solo_claude`, lo que no escribió Claude sale como plantilla."""
    reducida = reducir(respuesta)
    escrito = lenguaje.pedir(SISTEMA, json.dumps(reducida, ensure_ascii=False))
    if escrito is None or (solo_claude and escrito.proveedor != "claude"):
        return plantilla(respuesta)
    if not solo_numeros_del_json(escrito.texto, reducida):
        return plantilla(respuesta)
    return {"texto": escrito.texto, "origen": "modelo", "proveedor": escrito.proveedor,
            "propuesto_por": lenguaje.propuesto_por(escrito, "plantilla"), "precalculado": False}
