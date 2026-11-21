"""Genera los ejemplos fijos de contratos/ejemplos/ que definen la FORMA de las respuestas.

Son de antes del pivote a minería (D-37): sus textos hablan de personas y empresas, pero la forma es la vigente.
Los ejemplos con contenido minero los genera `generar_mineria.py`.

Todos los números son INVENTADOS: sirven para maquetar la web antes de que existan
los motores. No se muestran en el demo ni en el pitch.

Uso (solo biblioteca estándar):  python3 contratos/ejemplos/generar.py
"""
import json
import math
import random
from pathlib import Path

AQUI = Path(__file__).parent
AVISO = "Ejemplo fijo para maquetar. Todos los números son inventados: no se muestran en el demo ni en el pitch."
rnd = random.Random(26)


def escribir(nombre, obj):
    obj = {"_aviso": AVISO, **obj}
    (AQUI / nombre).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def sigmoide(x):
    return 1 / (1 + math.exp(-x))


# --- La regla de decisión de CONTRATO.md, sección 3 (copia de referencia para los ejemplos) ---
def decidir_tabla(muestras, c_si, c_no):
    corte = c_si / (c_si + c_no)
    p = sum(muestras) / len(muestras)
    actuar = p > corte
    al_otro_lado = sum(1 for m in muestras if (m > corte) != actuar) / len(muestras)
    estado = "en_duda" if al_otro_lado > 0.10 else ("actuar" if actuar else "no_actuar")
    costo = lambda q: min(c_si * (1 - q), c_no * q)
    duda = max(0.0, costo(p) - sum(costo(m) for m in muestras) / len(muestras))
    return p, estado, duda


def decidir_espacial(p, c_si, c_no):
    corte = c_si / (c_si + c_no)
    actuar = p > corte
    error = (1 - p) if actuar else p
    estado = "en_duda" if error > 0.10 else ("actuar" if actuar else "no_actuar")
    return estado, min(c_si * (1 - p), c_no * p)


ROTULOS_ROT = {"actuar": "Conviene retener", "no_actuar": "No hace falta",
               "en_duda": "No sabemos si conviene", "costo_de_no_saber": "Lo que te cuesta no saber"}
COSTOS_ROT = {"falso_si": {"valor": 1500, "min": 200, "max": 5000, "etiqueta": "Costo de un plan de retención"},
              "falso_no": {"valor": 6000, "min": 1000, "max": 20000, "etiqueta": "Costo de reemplazar a alguien"}}

# --- casos.json ---
# Desde el pivote a minería (D-37) lo escribe `generar_mineria.py`, junto con analizar_<caso>.json de los cuatro
# casos de lista. Este archivo sigue generando los ejemplos de forma (analizar_tabla, analizar_espacial, nube, sellos).

# --- analizar_tabla.json (motores de tabla: supervivencia, jerarquico, estados) ---
unidades = []
for i in range(120):
    centro = rnd.gauss(-1.5, 1.0)
    ancho = rnd.uniform(0.15, 0.9)
    muestras = [round(sigmoide(rnd.gauss(centro, ancho)), 2) for _ in range(32)]
    p, estado, duda = decidir_tabla(muestras, 1500, 6000)
    orden = sorted(muestras)
    unidades.append({"id": f"E-{i + 1:03d}", "etiqueta": f"E-{i + 1:03d}", "p": round(p, 3),
                     "rango_bajo": orden[1], "rango_alto": orden[-2], "muestras_p": muestras,
                     "estado": estado, "duda": round(duda, 1)})
unidades.sort(key=lambda u: -u["duda"])
resumen = {e: sum(1 for u in unidades if u["estado"] == e) for e in ("actuar", "no_actuar", "en_duda")}
total = round(sum(u["duda"] for u in unidades))
factores = [
    {"nombre": "OverTime", "etiqueta": "Horas extra", "direccion": "sube", "efecto": 0.94, "rango_bajo": 0.51, "rango_alto": 1.38, "certeza": "seguro"},
    {"nombre": "MonthlyIncome", "etiqueta": "Sueldo", "direccion": "baja", "efecto": -0.41, "rango_bajo": -0.83, "rango_alto": 0.02, "certeza": "probable"},
    {"nombre": "compromiso", "etiqueta": "Compromiso (según las cuatro encuestas)", "direccion": "baja", "efecto": -0.52, "rango_bajo": -0.9, "rango_alto": -0.15, "certeza": "seguro"},
    {"nombre": "DistanceFromHome", "etiqueta": "Distancia a la casa", "direccion": "sube", "efecto": 0.12, "rango_bajo": -0.2, "rango_alto": 0.45, "certeza": "no_se_sabe"},
    {"nombre": "NumCompaniesWorked", "etiqueta": "Empresas anteriores", "direccion": "sube", "efecto": 0.08, "rango_bajo": -0.3, "rango_alto": 0.44, "certeza": "no_se_sabe"},
]
base_reg = {
    "caso": "rotacion", "motor_id": "supervivencia", "implementacion": "red", "precalculado": False,
    "titular": f"{resumen['en_duda']} personas están en duda. No saber te cuesta cerca de {round(total / 1000)} mil dólares.",
    "costo_de_no_saber": {"valor": total, "moneda": "USD"},
    "costos": COSTOS_ROT, "punto_de_corte": 0.2,
    "unidades": unidades, "resumen_colores": resumen, "factores": factores,
    "columnas": {"usadas": [f["nombre"] for f in factores], "disponibles": 35, "elegidas_por": "equipo", "explicacion": ""},
    "semaforo": {"estado": "verde", "motivo": "", "propuesta": None},
    "examen": {"tipo": "datos_reales_reservados", "n": 294,
               "frase": "De las personas a las que les dimos cerca de 30% de riesgo, se fue el 28%.",
               "tramos": [{"dijimos": 0.05, "paso": 0.04, "n": 110}, {"dijimos": 0.15, "paso": 0.17, "n": 96},
                          {"dijimos": 0.3, "paso": 0.28, "n": 58}, {"dijimos": 0.55, "paso": 0.6, "n": 30}]},
    "sello_resumen": {"frase": "Exactitud en medición.", "medido": False},
    "en_palabras": ["Hay un grupo al que conviene ofrecerle un plan de retención desde ya.",
                    "En otro grupo, los datos no alcanzan para saber si conviene.",
                    "Lo que más pesa son las horas extra."],
    "rotulos": ROTULOS_ROT, "registro": ["120 personas por decidir", "9 cargos", "32 versiones creíbles"],
    "tiempo_ms": 310, "sintetico": False, "origen_datos": "Datos públicos de ejemplo",
}
escribir("analizar_tabla.json", base_reg)

# --- decision_prueba.json: mismas entradas, salidas esperadas. Lo leen la prueba de Python y la de TypeScript ---
casos_prueba = []
for u in unidades[:12]:
    for c_si, c_no in ((1500, 6000), (500, 6000), (3000, 3000)):
        p, estado, duda = decidir_tabla(u["muestras_p"], c_si, c_no)
        casos_prueba.append({"regla": "tabla", "muestras_p": u["muestras_p"], "c_si": c_si, "c_no": c_no,
                             "espera": {"p": round(p, 4), "estado": estado, "duda": round(duda, 2)}})
for p in (0.01, 0.08, 0.2, 0.29, 0.3, 0.5, 0.89, 0.91, 0.99):
    estado, duda = decidir_espacial(p, 20000, 50000)
    casos_prueba.append({"regla": "espacial", "p": p, "c_si": 20000, "c_no": 50000,
                         "espera": {"estado": estado, "duda": round(duda, 2)}})
escribir("decision_prueba.json", {"tolerancia": 0.01, "casos": casos_prueba})

# --- analizar_rojo.json ---
escribir("analizar_rojo.json", {
    "caso": "rotacion_malo", "motor_id": "supervivencia", "implementacion": "red", "precalculado": False,
    "titular": "No respondo todavía: una columna delata la respuesta.",
    "costo_de_no_saber": None, "costos": COSTOS_ROT, "punto_de_corte": 0.2,
    "unidades": None, "resumen_colores": None, "factores": None,
    "columnas": {"usadas": ["OverTime", "MonthlyIncome", "JobRole", "fecha_salida"], "disponibles": 36, "elegidas_por": "equipo", "explicacion": ""},
    "semaforo": {"estado": "rojo_modelo",
                 "motivo": "La columna «fecha_salida» solo tiene dato para quienes ya renunciaron. Con ella cualquier análisis parece perfecto y no sirve para decidir.",
                 "propuesta": {"transformacion": "quitar_factor:fecha_salida", "texto": "Propongo sacar esa columna y responder con las demás."}},
    "examen": None, "sello_resumen": {"frase": "Exactitud en medición.", "medido": False},
    "en_palabras": [], "rotulos": ROTULOS_ROT,
    "registro": ["600 filas", "Detectado: fecha_salida adivina sola la respuesta", "Detector de resúmenes aprendidos: dentro"],
    "tiempo_ms": 90, "sintetico": False, "origen_datos": "Datos públicos de ejemplo",
})

# --- nube.json ---
puntos = []
for _ in range(1500):
    x = min(0.97, max(0.5, 0.5 + abs(rnd.gauss(0.12, 0.09))))
    y = min(0.95, max(0.05, rnd.betavariate(2, 4)))
    puntos.append([round(x, 3), round(y, 3)])
escribir("nube.json", {
    "caso": "rotacion_malo", "n_simulaciones": 200000,
    "ejes": {"x": {"nombre": "Qué tan bien adivina la respuesta el mejor factor, solo", "min": 0.5, "max": 1.0},
             "y": {"nombre": "Proporción de «sí»", "min": 0.0, "max": 1.0}},
    "puntos": puntos, "archivo": {"x": 0.995, "y": 0.16, "dentro": False},
    "detectores": {"ejes_con_nombre": {"dentro": False, "motivo": "La columna «fecha_salida» adivina sola la respuesta."},
                   "resumenes_aprendidos": {"dentro": True, "distancia": 2.1, "limite": 4.6}},
})

# --- analizar_espacial.json ---
NX = NY = 32
X0, Y0, LADO = 178600.0, 329700.0, 122.0
p_mapa, media_mapa = [], []
for j in range(NY):
    for i in range(NX):
        fuera = (i + j) > 52 or (i - j) > 22          # esquinas fuera del terreno
        if fuera:
            p_mapa.append(None); media_mapa.append(None); continue
        d = abs(i - 0.5 * j - 4) / 6.0                # distancia a una franja diagonal («el río»)
        nivel = 1300 * math.exp(-d) + 150 + 60 * math.sin(i / 3.0) * math.cos(j / 4.0)
        incert = 0.07 + 0.3 * abs(math.sin(i * 0.7) * math.sin(j * 0.5)) ** 2
        p = sigmoide((math.log(nivel) - math.log(720)) / incert)
        p_mapa.append(round(p, 3)); media_mapa.append(round(nivel, 0))
puntos_medidos = []
for _ in range(155):
    i, j = rnd.randrange(NX), rnd.randrange(NY)
    k = j * NX + i
    if media_mapa[k] is None:
        continue
    puntos_medidos.append({"x": round(X0 + (i + rnd.random()) * LADO), "y": round(Y0 + (j + rnd.random()) * LADO),
                           "valor": round(media_mapa[k] * math.exp(rnd.gauss(0, 0.25)))})
estados = [decidir_espacial(p, 20000, 50000) for p in p_mapa if p is not None]
resumen_e = {e: sum(1 for s, _ in estados if s == e) for e in ("actuar", "no_actuar", "en_duda")}
total_e = round(sum(d for _, d in estados))
ROTULOS_TER = {"actuar": "Hay que limpiar", "no_actuar": "No hace falta limpiar",
               "en_duda": "No sabemos: conviene medir", "costo_de_no_saber": "Lo que te cuesta no saber"}
escribir("analizar_espacial.json", {
    "caso": "terreno", "motor_id": "espacial", "implementacion": "red", "precalculado": False,
    "titular": f"{resumen_e['en_duda']} bloques están en duda. No saber te cuesta cerca de {str(round(total_e / 1e6, 1)).replace('.', ',')} millones de dólares.",
    "costo_de_no_saber": {"valor": total_e, "moneda": "USD"},
    "costos": {"falso_si": {"valor": 20000, "min": 5000, "max": 60000, "etiqueta": "Costo de limpiar un bloque"},
               "falso_no": {"valor": 50000, "min": 10000, "max": 200000, "etiqueta": "Costo de dejar un bloque contaminado"},
               "medicion": {"valor": 3000, "etiqueta": "Costo de una medición"}},
    "punto_de_corte": round(20000 / 70000, 3),
    "unidades": None, "resumen_colores": resumen_e, "columnas": None,
    "factores": [
        {"nombre": "tendencia", "etiqueta": "Cercanía al río", "direccion": "sube", "efecto": 0.58, "rango_bajo": 0.41, "rango_alto": 0.72, "certeza": "seguro"},
        {"nombre": "continuidad", "etiqueta": "Lo que pasa en los bloques vecinos", "direccion": "sube", "efecto": 0.31, "rango_bajo": 0.18, "rango_alto": 0.46, "certeza": "seguro"},
        {"nombre": "ruido", "etiqueta": "Error de cada medición", "direccion": "sube", "efecto": 0.11, "rango_bajo": 0.04, "rango_alto": 0.2, "certeza": "probable"},
    ],
    "mapa": {"nx": NX, "ny": NY, "x0": X0, "y0": Y0, "lado": LADO, "p": p_mapa, "media": media_mapa,
             "puntos": puntos_medidos, "umbral": 720, "unidad_valor": "mg/kg"},
    "semaforo": {"estado": "verde", "motivo": "", "propuesta": None},
    "examen": {"tipo": "puntos_reales_escondidos", "n": 31,
               "frase": "Escondimos 31 mediciones reales y las adivinamos: 28 cayeron dentro del rango que dimos.",
               "tramos": [{"dijimos": 0.9, "paso": 0.903, "n": 31}]},
    "sello_resumen": {"frase": "Exactitud en medición.", "medido": False},
    "en_palabras": ["Hay una franja que hay que limpiar con seguridad.",
                    "Lejos de esa franja, el terreno está limpio.",
                    "Entre medio no se sabe: ahí conviene medir antes de gastar."],
    "rotulos": ROTULOS_TER, "registro": [f"{len(puntos_medidos)} mediciones", "grilla de 32 por 32 bloques"],
    "tiempo_ms": 420, "sintetico": False, "origen_datos": "Datos públicos de ejemplo",
})

# --- donde_medir.json ---
escribir("donde_medir.json", {
    "caso": "terreno",
    "candidatas": [
        {"puesto": 1, "etiqueta": "A", "x": 180186, "y": 331408, "valor_de_medir": 41200, "costo_medicion": 3000, "valor_neto": 38200,
         "resultados_posibles": {"bajo": 240, "medio": 610, "alto": 1480}},
        {"puesto": 2, "etiqueta": "B", "x": 179576, "y": 330920, "valor_de_medir": 22900, "costo_medicion": 3000, "valor_neto": 19900,
         "resultados_posibles": {"bajo": 310, "medio": 700, "alto": 1320}},
        {"puesto": 3, "etiqueta": "C", "x": 181162, "y": 332628, "valor_de_medir": 9100, "costo_medicion": 3000, "valor_neto": 6100,
         "resultados_posibles": {"bajo": 180, "medio": 420, "alto": 990}},
    ],
    "mensaje_parada": None, "analisis_rehechos": 480, "tiempo_ms": 900, "implementacion": "red", "precalculado": False,
})

# --- cartera.json ---
filas = []
for k in range(40):
    n = rnd.randint(25, 400)
    por_unidad = round(rnd.uniform(20, 160) * (60 / (n + 30)) + 15, 1)   # las chicas saben menos
    filas.append({"cliente": f"Empresa {k + 1:03d}", "n_unidades": n, "costo_de_no_saber": round(n * por_unidad),
                  "por_unidad": por_unidad, "en_duda": round(n * rnd.uniform(0.05, 0.3)),
                  "estado": "rojo_datos" if n < 30 else "verde"})
filas.sort(key=lambda f: -f["costo_de_no_saber"])
escribir("cartera.json", {
    "caso": "rotacion", "n_analisis": 1000, "tiempo_ms": 1840, "precalculado": False,
    "_nota": "El ejemplo trae 40 filas de 1.000 para no pesar; el servicio real devuelve todas.",
    "filas": filas, "sintetico": True, "origen_datos": "1.000 empresas simuladas, cada una distinta",
})

# --- sello.json ---
escribir("sello.json", {
    "motor_id": "espacial", "implementacion": "red",
    "simulaciones_entrenamiento": 12000000, "entrenamiento_min": 190, "casos_validacion": 5000,
    "cobertura_90": 0.903, "cobertura_90_peor_grupo": 0.871, "peor_grupo": "muy pocas mediciones",
    "sbc_pasa": True, "cobertura_90_metodo_rapido": 0.74, "latencia_ms": 60,
    "mcmc_datasets_comparados": 8, "mcmc_s_por_dataset": 45.0, "mcmc_diferencia_media": 0.08,
    "amortizacion": {"que_se_compara": "rehacer 480 análisis completos para «¿Dónde mido?»", "mcmc_s": 21600, "red_s": 0.9},
    "nube_malo_cae_fuera": None, "minutos_de_punta_a_punta": 240,
    "fecha": "2026-11-21", "maquina": "MacBook Air M4 16 GB",
    "limitaciones": ["Terrenos en dos dimensiones", "Hasta 400 mediciones", "Grilla de 32 por 32 bloques"],
    "frases": ["Practicó con 12 millones de terrenos simulados.",
               "Cuando da un rango de 90%, acierta 90,3%. El método rápido de siempre acierta 74%.",
               "En el tipo de terreno más difícil acierta 87,1%."],
})

# --- un sello por motor: los de tabla parten sin medir (campos en null) ---
for mid in ("supervivencia", "jerarquico", "estados"):
    escribir(f"sello_{mid}.json", {
        "motor_id": mid, "implementacion": "red",
        "simulaciones_entrenamiento": None, "entrenamiento_min": None, "casos_validacion": None,
        "cobertura_90": None, "cobertura_90_peor_grupo": None, "peor_grupo": None, "sbc_pasa": None,
        "cobertura_90_metodo_rapido": None, "latencia_ms": None,
        "mcmc_datasets_comparados": None, "mcmc_s_por_dataset": None, "mcmc_diferencia_media": None,
        "amortizacion": None, "nube_malo_cae_fuera": None, "minutos_de_punta_a_punta": None,
        "fecha": "2026-11-21", "maquina": None, "limitaciones": [], "frases": [],
    })

print("Ejemplos escritos en", AQUI)
