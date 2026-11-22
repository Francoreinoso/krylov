"""Genera los ejemplos fijos de los casos mineros (pivote D-37): casos.json y analizar_<caso>.json.

Todos los números de las respuestas son INVENTADOS: sirven para maquetar la web (la lista en tres
colores y la curva con su abanico) antes de que existan los motores `deformacion`, `cinetica`,
`desgaste` y `sismico`. En pantalla llevan el rótulo «ejemplo». No se muestran en el pitch.

Lo que sí es cierto en estos archivos: las unidades, los puntos medidos de cada curva (salen de
`datos/demo/<caso>.csv`) y los textos, costos y rótulos (salen de `casos/<caso>.yaml`).

Uso:  uv run python contratos/ejemplos/generar_mineria.py
"""

import csv
import json
import math
import random
from pathlib import Path

import yaml

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
AVISO = "Ejemplo fijo para maquetar. Todos los números son inventados: no se muestran en el demo ni en el pitch."
ORDEN = ["leyes", "taludes", "flotacion", "flota", "sismicidad"]
rnd = random.Random(37)


def escribir(nombre, obj):
    (AQUI / nombre).write_text(json.dumps({"_aviso": AVISO, **obj}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def caso(nombre):
    return yaml.safe_load((RAIZ / "casos" / f"{nombre}.yaml").read_text(encoding="utf-8"))


def filas(ruta):
    with open(RAIZ / ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def decidir(muestras, c_si, c_no):
    """La regla de lista de CONTRATO.md, sección 3 (copia de referencia para los ejemplos)."""
    corte = c_si / (c_si + c_no)
    p = sum(muestras) / len(muestras)
    actuar = p > corte
    al_otro_lado = sum(1 for m in muestras if (m > corte) != actuar) / len(muestras)
    estado = "en_duda" if al_otro_lado > 0.10 else ("actuar" if actuar else "no_actuar")
    costo = lambda q: min(c_si * (1 - q), c_no * q)
    return p, estado, max(0.0, costo(p) - sum(costo(m) for m in muestras) / len(muestras))


def muestras_alrededor(p, ancho):
    """32 versiones creíbles de una probabilidad: inventadas, centradas en p."""
    logit = math.log(max(p, 1e-3) / max(1 - p, 1e-3))
    return [round(1 / (1 + math.exp(-(logit + rnd.gauss(0, ancho)))), 2) for _ in range(32)]


def adelgazar(t, y, maximo=60):
    paso = max(1, math.ceil(len(t) / maximo))
    return t[::paso], y[::paso]


def plata(valor):
    if valor >= 1e6:
        return f"cerca de {valor / 1e6:.1f} millones de dólares".replace(".", ",")
    return f"cerca de {round(valor / 1000)} mil dólares" if valor >= 1000 else f"US$ {round(valor)}"


# --- Lo inventado de cada caso: probabilidad por unidad y abanico de su curva ---

def de_taludes(c, t, y, verdad):
    ahora, h = t[-1], c["columnas"]["horizonte"]
    acelera, cede = verdad["acelerando"] == "1", verdad["cede_en_el_horizonte"] == "1"
    dudoso = not acelera and int(verdad["unidad"][-2:]) % 6 == 0          # unos pocos sectores estables con lecturas ruidosas
    p = 0.86 if cede else 0.22 if acelera else 0.04 if dudoso else 0.008
    velocidad = max(0.02, (y[-1] - y[-8]) / (t[-1] - t[-8]))
    tb = [round(ahora + h * i / 12, 2) for i in range(13)]
    empuje = 3.0 if cede else 1.4 if acelera else 1.0
    medio = [round(y[-1] + velocidad * empuje * (u - ahora) * (1 + (empuje - 1) * (u - ahora) / h), 2) for u in tb]
    bajo = [round(y[-1] + velocidad * 0.6 * (u - ahora), 2) for u in tb]
    alto = [round(y[-1] + (m - y[-1]) * (1.9 if acelera else 1.5) + 0.6, 2) for m in medio]
    marca = None
    if acelera:
        falta = float(verdad["horas_hasta_ceder"])
        marca = {"texto": f"Faltan entre {round(falta * 0.6)} y {round(falta * 1.7)} horas", "bajo": round(falta * 0.6, 1), "medio": round(falta, 1), "alto": round(falta * 1.7, 1)}
    return p, 0.5 if cede else 1.3 if acelera else 1.1 if dudoso else 0.6, (tb, bajo, medio, alto), None, marca


def de_flotacion(c, t, y, verdad):
    final, tf, meta = float(verdad["recuperacion_final"]), c["columnas"]["tiempo_final"], c["columnas"]["umbral"]
    p = min(0.99, max(0.01, 1 / (1 + math.exp(-(meta - final) * 120))))
    tb = [round(t[-1] + (tf - t[-1]) * i / 8, 1) for i in range(9)]
    medio = [round(y[-1] + (final - y[-1]) * (1 - math.exp(-3 * i / 8)) / (1 - math.exp(-3)), 3) for i in range(9)]
    ancho = 0.012 + 0.006 * (8 - len(t))
    bajo = [round(m - ancho * i / 2.5, 3) for i, m in enumerate(medio)]
    alto = [round(min(0.99, m + ancho * i / 2.5), 3) for i, m in enumerate(medio)]
    return p, 0.9, (tb, bajo, medio, alto), meta, None


def de_flota(c, t, y, verdad, a_mantencion):
    hoy, falla = float(verdad["desgaste_hoy"]), verdad["falla_antes_de_la_mantencion"] == "1"
    ritmo = max(1e-5, hoy / max(t[-1], 1.0))                    # desgaste por hora de operación
    esperado = hoy + ritmo * a_mantencion
    p = min(0.97, max(0.01, 1 / (1 + math.exp(-(esperado - 0.93) * 11)) * (1.15 if falla else 0.85)))
    tb = [round(t[-1] + a_mantencion * i / 8) for i in range(9)]
    medio = [round(hoy + ritmo * (u - t[-1]), 3) for u in tb]
    bajo = [round(hoy + ritmo * 0.45 * (u - t[-1]), 3) for u in tb]
    alto = [round(hoy + ritmo * 2.1 * (u - t[-1]) + 0.02, 3) for u in tb]
    return p, 0.8, (tb, bajo, medio, alto), c["columnas"]["umbral"], None


def de_sismicidad(c, t, y, verdad):
    ahora, h = c["columnas"]["horizonte"], c["columnas"]["horizonte"]          # la ventana observada dura lo mismo que el horizonte
    acumulado = list(range(1, len(t) + 1))
    recientes = sum(1 for u in t if u > ahora - 2)
    esperados = 1.5 + recientes * 0.9
    p = min(0.6, 1 - math.exp(-esperados * 0.012 * (3 if verdad["hubo_sismo_fuerte"] == "1" else 1)))
    tb = [round(ahora + h * i / 8, 2) for i in range(9)]
    medio = [round(len(t) + esperados * (1 - math.exp(-1.6 * i / 8)) / (1 - math.exp(-1.6)), 1) for i in range(9)]
    bajo = [round(len(t) + (m - len(t)) * 0.45, 1) for m in medio]
    alto = [round(len(t) + (m - len(t)) * 2.2 + 0.4 * i, 1) for i, m in enumerate(medio)]
    return p, 0.9, (tb, bajo, medio, alto), None, None, (t, acumulado)


FACTORES = {
    "taludes": [("fraccion_acelerando", "sube", "seguro", 0.21), ("velocidad_fondo", "sube", "probable", 0.4), ("ruido", "sube", "no_se_sabe", 0.05)],
    "flotacion": [("velocidad", "baja", "seguro", -0.6), ("tope", "baja", "seguro", -0.8), ("fraccion_rapida", "baja", "no_se_sabe", -0.1)],
    "flota": [("exigencia", "sube", "seguro", 0.31), ("ritmo", "sube", "seguro", 0.5), ("saltos", "sube", "no_se_sabe", 0.06)],
    "sismicidad": [("contagio", "sube", "seguro", 0.44), ("apagado", "baja", "probable", -0.3), ("fondo", "sube", "no_se_sabe", 0.08)],
}


def analizar(nombre):
    c = caso(nombre)
    col = c["columnas"]
    datos = filas(c["dataset"])
    verdad = {f["unidad"]: f for f in filas(c["verdad"])}
    por_unidad = {}
    for f in datos:
        por_unidad.setdefault(f[col["unidad"]], []).append(f)
    c_si, c_no = c["costos"]["falso_si"]["valor"], c["costos"]["falso_no"]["valor"]
    unidades = []
    for unidad, lecturas in por_unidad.items():
        t = [float(f[col["tiempo"]]) for f in lecturas]
        y = [float(f[col["valor"]]) for f in lecturas]
        medido = (t, y)
        if nombre == "taludes":
            p, ancho, banda, limite, marca = de_taludes(c, t, y, verdad[unidad])
        elif nombre == "flotacion":
            p, ancho, banda, limite, marca = de_flotacion(c, t, y, verdad[unidad])
        elif nombre == "flota":
            p, ancho, banda, limite, marca = de_flota(c, t, y, verdad[unidad], float(lecturas[0][col["horizonte_por_unidad"]]))
        else:
            p, ancho, banda, limite, marca, medido = de_sismicidad(c, t, y, verdad[unidad])
        muestras = muestras_alrededor(p, ancho)
        p_media, estado, duda = decidir(muestras, c_si, c_no)
        orden = sorted(muestras)
        mt, my = adelgazar(*medido)
        unidades.append({
            "id": unidad, "etiqueta": unidad, "p": round(p_media, 3), "rango_bajo": orden[1], "rango_alto": orden[-2],
            "muestras_p": muestras, "estado": estado, "duda": round(duda, 1),
            "curva": {"t": mt, "y": my, "ahora": medido[0][-1] if nombre != "sismicidad" else col["horizonte"],
                      "t_banda": banda[0], "bajo": banda[1], "medio": banda[2], "alto": banda[3], "limite": limite,
                      "eje_t": col["eje_tiempo"], "eje_y": col["eje_valor"], "marca": marca},
        })
    unidades.sort(key=lambda u: -u["duda"])
    colores = {k: sum(1 for u in unidades if u["estado"] == k) for k in ("actuar", "no_actuar", "en_duda")}
    total = round(sum(u["duda"] for u in unidades))
    dijeron_si = [u for u in unidades if u["estado"] == "actuar"]
    paso = sum(1 for u in dijeron_si if verdad[u["id"]][c["verdad_columna"]] == "1")
    plural, singular = c["unidad"]["plural"], c["unidad"]["singular"]
    return {
        "caso": nombre, "motor_id": c["motor"], "implementacion": "red", "precalculado": False,
        "titular": f"{colores['en_duda']} {plural} están en duda. No saber te cuesta {plata(total)}.",
        "costo_de_no_saber": {"valor": total, "moneda": c["moneda"]},
        "costos": {k: {q: v[q] for q in ("valor", "min", "max", "etiqueta")} for k, v in c["costos"].items()},
        "punto_de_corte": round(c_si / (c_si + c_no), 3),
        "unidad": c["unidad"],
        "unidades": unidades, "resumen_colores": colores,
        "factores": [{"nombre": n, "etiqueta": c["etiquetas"][n], "direccion": d, "efecto": e, "rango_bajo": round(e - 0.2, 2),
                      "rango_alto": round(e + 0.2, 2), "certeza": cert} for n, d, cert, e in FACTORES[nombre]],
        "columnas": {"usadas": [col["unidad"], col["tiempo"], col["valor"]] + col.get("covariables", []), "disponibles": len(datos[0]),
                     "elegidas_por": "equipo", "explicacion": ""},
        "semaforo": {"estado": "verde", "motivo": "", "propuesta": None},
        "examen": {"tipo": "verdad_escondida", "n": len(unidades),
                   "frase": f"De {len(dijeron_si)} {plural} en que dijimos «{c['rotulos']['actuar'].lower()}», en {paso} pasó de verdad. Con datos simulados.",
                   "tramos": [{"dijimos": 0.05, "paso": 0.04, "n": max(1, colores["no_actuar"])},
                              {"dijimos": 0.35, "paso": 0.33, "n": max(1, colores["en_duda"])},
                              {"dijimos": 0.85, "paso": round(paso / max(1, len(dijeron_si)), 2), "n": max(1, len(dijeron_si))}]},
        "sello_resumen": {"frase": "", "medido": False},
        "en_palabras": [f"En {colores['actuar']} {plural}, {c['rotulos']['actuar'].lower()}, y saber más no cambiaría la decisión.",
                        f"En {colores['en_duda']} {plural} los datos no alcanzan para decidir: {c['rotulos']['en_duda'].lower()}."],
        "rotulos": c["rotulos"],
        "registro": [f"{len(unidades)} {plural}", f"{len(datos)} mediciones", "32 versiones creíbles"],
        "tiempo_ms": 240, "sintetico": True, "origen_datos": c["origen_datos"],
    }


escribir("casos.json", {"casos": [
    {"nombre": c["nombre"], "titulo": c["tarjeta"]["titulo"], "empresa_o_industria": c["tarjeta"]["empresa_o_industria"],
     "quien": c["tarjeta"].get("quien"), "archivo": c["tarjeta"].get("archivo"), "motor": c["motor"], "sintetico": bool(c.get("sintetico")), "origen_datos": c["origen_datos"]}
    for c in map(caso, ORDEN)]})
for nombre in ORDEN[1:]:
    respuesta = analizar(nombre)
    escribir(f"analizar_{nombre}.json", respuesta)
    print(nombre, respuesta["resumen_colores"], respuesta["costo_de_no_saber"]["valor"], "|", respuesta["examen"]["frase"])
