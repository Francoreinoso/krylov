"""Los textos de la respuesta: plantillas de `casos/textos.yaml` llenadas con los números del motor.

No hay modelo de lenguaje en Krylov: toda frase sale de una plantilla escrita por el equipo
(`contratos/CONTRATO.md`, sección 5) y de números que entregó un motor. Si a una plantilla le
falta un número, la frase no se muestra: nunca se inventa.
"""

from __future__ import annotations

from functools import cache

import yaml

from nucleo.casos import CARPETA_CASOS


@cache
def plantillas() -> dict:
    return yaml.safe_load((CARPETA_CASOS / "textos.yaml").read_text(encoding="utf-8"))


def frase(ruta: str, **valores) -> str | None:
    """La plantilla de `ruta` («titular.verde_o_amarillo.con_duda») con sus variables. None si falta la plantilla o un valor."""
    nodo = plantillas()
    for clave in ruta.split("."):
        if not isinstance(nodo, dict) or clave not in nodo:
            return None
        nodo = nodo[clave]
    if not isinstance(nodo, str) or any(v is None for v in valores.values()):
        return None
    try:
        return nodo.format(**valores)
    except (KeyError, IndexError):
        return None


def minuscula_inicial(texto: str) -> str:
    return texto[:1].lower() + texto[1:]


def numero(valor: float, decimales: int = 0) -> str:
    """Un número como se escribe en Chile: coma decimal, sin decimales por defecto."""
    return f"{valor:.{decimales}f}".replace(".", ",")


def plata(valor: float) -> str:
    """Un monto en palabras, con `formato_plata`: «US$ 850», «cerca de 7 mil dólares», «cerca de 2,7 millones de dólares»."""
    if round(valor) <= 0:
        return frase("formato_plata.cero")
    if valor < 1000:
        return frase("formato_plata.menos_de_mil", valor=round(valor))
    if valor < 1e6:
        return frase("formato_plata.miles", miles=round(valor / 1e3))
    return frase("formato_plata.millones", millones=numero(valor / 1e6, 1))


def titular(caso: dict, semaforo: dict, colores: dict | None, total: float | None) -> str | None:
    estado = semaforo["estado"]
    if estado == "rojo_datos":
        return frase("titular.rojo_datos")
    if estado == "rojo_modelo":
        return frase("titular.rojo_modelo." + ("columna_delata" if semaforo.get("propuesta") else "no_se_parece"))
    if colores is None or total is None:
        return None
    n = colores["en_duda"]
    clave = "sin_duda" if n == 0 or round(total) <= 0 else "una_en_duda" if n == 1 else "con_duda"
    return frase(f"titular.verde_o_amarillo.{clave}", n_en_duda=n, unidad_singular=caso["unidad"]["singular"],
                 unidad_plural=caso["unidad"]["plural"], costo_de_no_saber=plata(total))


def en_palabras(caso: dict, colores: dict | None, factores: list[dict] | None) -> list[str]:
    """Hasta tres frases, en el orden de las plantillas, solo las que apliquen."""
    if colores is None:
        return []
    valores = {"n_actuar": colores["actuar"], "n_no_actuar": colores["no_actuar"], "n_en_duda": colores["en_duda"],
               "unidad_plural": caso["unidad"]["plural"], "unidad_singular": caso["unidad"]["singular"], "actuar_min": minuscula_inicial(caso["rotulos"]["actuar"]),
               "en_duda_min": minuscula_inicial(caso["rotulos"]["en_duda"])}
    factores = factores or []
    frases = []
    def una(n: int) -> str:                                   # la variante en singular de la plantilla, cuando hay una sola
        return "_una" if n == 1 else ""
    if caso["motor"] == "espacial":
        base = "en_palabras.espacial."
        frases += [frase(base + "hay_actuar" + una(colores["actuar"]), **valores)] if colores["actuar"] else []
        frases += [frase(base + "hay_no_actuar", **valores)] if colores["no_actuar"] else []
        frases += [frase(base + "hay_en_duda" + una(colores["en_duda"]), **valores)] if colores["en_duda"] else []
        frases += [frase(base + "manda", factor_min=minuscula_inicial(factores[0]["etiqueta"]))] if factores else []
    else:
        frases += [frase("en_palabras.hay_actuar" + una(colores["actuar"]), **valores)] if colores["actuar"] else []
        frases += [frase("en_palabras.hay_en_duda" + una(colores["en_duda"]), **valores)] if colores["en_duda"] else []
        seguro = next((f for f in factores if f["certeza"] == "seguro"), None)
        dudoso = next((f for f in factores if f["certeza"] == "no_se_sabe"), None)
        frases += [frase("en_palabras.factor_seguro", factor_min=minuscula_inicial(seguro["etiqueta"]))] if seguro else []
        frases += [frase("en_palabras.factor_no_se_sabe", factor=dudoso["etiqueta"])] if dudoso else []
    return [f for f in frases if f][:3]


def examen(caso: dict, bloque: dict | None) -> str | None:
    """La frase del examen con datos reales, armada con los números de `tramos`."""
    if not bloque or not bloque.get("tramos"):
        return None
    if bloque["tipo"] == "puntos_reales_escondidos":
        tramo = bloque["tramos"][0]
        return frase("examen.espacial", n=bloque["n"], k=round(tramo["paso"] * tramo["n"]))
    tramo = max(bloque["tramos"], key=lambda t: t["n"])                      # el tramo con más unidades
    verbo = plantillas().get("examen", {}).get("verbo_por_caso", {}).get(caso["nombre"].removesuffix("_malo"))
    return frase("examen.tabla", unidad_plural=caso["unidad"]["plural"], dijimos=round(100 * tramo["dijimos"]),
                 paso_verbo=verbo, paso=round(100 * tramo["paso"]))


def sello(ficha: dict) -> list[str]:
    """Las oraciones del sello de un motor. Un campo sin medir no genera frase."""
    porcentaje = lambda v: None if v is None else numero(100 * v, 1)             # noqa: E731
    simulaciones = ficha.get("simulaciones_entrenamiento")
    que = plantillas().get("sello", {}).get("casos_simulados_por_motor", {}).get(ficha.get("motor_id"))
    lento_s = ficha.get("mcmc_s_por_dataset")
    frases = [
        frase("sello.practico", millones=numero(simulaciones / 1e6, 1) if simulaciones and simulaciones >= 1e5 else None, casos_simulados=que),
        frase("sello.cobertura", cobertura=porcentaje(ficha.get("cobertura_90"))),
        frase("sello.peor_grupo", peor_grupo=ficha.get("peor_grupo"), cobertura_peor=porcentaje(ficha.get("cobertura_90_peor_grupo"))),
        frase("sello.contra_lento", minutos_lento=round(lento_s / 60) if lento_s and lento_s >= 60 else None, ms=ficha.get("latencia_ms")),
    ]
    return [f for f in frases if f]
