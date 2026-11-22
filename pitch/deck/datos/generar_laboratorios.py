#!/usr/bin/env python3
"""Genera pitch/deck/datos/laboratorios.js: lo que dibuja la lámina W del deck (tecla W).

    python3 pitch/deck/datos/generar_laboratorios.py [/ruta/a/ne_50m_land.geojson]

Dos cosas salen de aquí:

1. Los grupos de investigación. Entran solo los que publican **amortized Bayesian inference** con esas palabras:
   cada grupo está por un trabajo de 2020 en adelante cuyo título o resumen lo dice casi textual («amortized Bayesian
   inference», «amortized inference», «amortized simulation-based inference», «amortized variational inference»,
   «amortized neural posterior estimation»). La frase exacta de cada trabajo va en `frase`, y su identificador, en `fuente`.
   La afiliación es la que el autor firma en ese trabajo, no necesariamente la de hoy. Todo se comprobó el 22-nov-2026 en
   la fuente primaria: la portada del artículo en arXiv, OpenAlex (api.openalex.org/works/doi:…), Crossref o PMLR.
   Lo que no se pudo comprobar no entra, y tampoco lo que usa la palabra para otra cosa (autoencoders, GFlowNets,
   diseño de experimentos): por eso la lista no es exhaustiva. Una institución aparece una sola vez.
   La lista anterior (30 grupos tomados de las citas de un review, con trabajos desde 2012) está en
   pitch/deck/antes_pasada_final/datos/.

2. El mapa. La tierra firme de Natural Earth (ne_50m_land, dominio público, naturalearthdata.com), pasada a una
   rejilla de puntos en proyección de Robinson. El archivo de origen se descarga una vez:
   https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson
   El deck no lo necesita: la rejilla queda dentro de laboratorios.js, como bits en base64. Sin el archivo de origen,
   este programa conserva la rejilla que ya está en laboratorios.js y reescribe solo los grupos.
"""
import base64
import json
import math
import pathlib
import sys
from datetime import date

AQUI = pathlib.Path(__file__).resolve().parent

CRITERIO = {
    "desde": 2020,
    "frase": "amortized Bayesian inference",
    "regla": "Un trabajo de 2020 en adelante que lo dice, casi textual, en su título o en su resumen",
    "comprobado": "2026-11-22",
}

ARXIV = "Portada del artículo en arXiv"
OA = "Afiliación del trabajo, según OpenAlex"


def g(id, institucion, ciudad, pais, iso, continente, parada, lat, lon, cita, anio, titulo, frase, aporte, fuente):
    return dict(id=id, institucion=institucion, ciudad=ciudad, pais=pais, iso=iso, continente=continente, parada=parada,
                lat=lat, lon=lon, cita=cita, anio=anio, titulo=titulo, frase=frase, aporte=aporte, fuente=fuente)


# Los trabajos, una vez cada uno: cita, año, título y la frase que lo hace entrar.
T_CL = ("Tong, Sing-Long y Schiavazzi", 2025, "InVAErt networks for amortized inference and identifiability analysis of lumped-parameter haemodynamic models",
        "InVAErt networks for amortized inference and identifiability analysis", "Inferencia amortizada para modelos de la circulación de la sangre")
T_CR = ("Pasquier y Barboza", 2026, "Amortized Bayesian inference for spatio-temporal extremes: A copula factor model with autoregression",
        "Amortized Bayesian inference for spatio-temporal extremes", "Inferencia bayesiana amortizada para lluvias extremas, en el espacio y en el tiempo")
T_SIM = ("Gloeckler y otros", 2024, "All-in-one simulation-based inference",
         "Amortized Bayesian inference trains neural networks to solve stochastic inference problems using model simulations", "Una sola red que responde cualquier pregunta sobre un mismo simulador")
T_MILA = ("Mittal y otros", 2025, "Amortized In-Context Bayesian Posterior Estimation",
          "Amortized In-Context Bayesian Posterior Estimation", "Una red que entrega la respuesta completa leyendo los datos como contexto")
T_NUS = ("Wang, Evans y Nott", 2026, "Robust Bayesian methods using amortized simulation-based inference",
         "Robust Bayesian methods using amortized simulation-based inference", "Cómo notar que el modelo no calza con los datos, con inferencia amortizada")
T_MULTI = ("Habermann y otros", 2025, "Amortized Bayesian Multilevel Models",
           "the nascent field of amortized Bayesian inference", "Inferencia bayesiana amortizada para modelos jerárquicos")
T_AVI = ("Margossian y Blei", 2024, "Amortized Variational Inference: When and Why?",
         "Amortized Variational Inference: When and Why?", "Cuándo conviene amortizar la inferencia variacional, y por qué")
T_GEO = ("Siahkoohi y otros", 2023, "Reliable amortized variational inference with physics-based latent distribution correction",
         "Reliable amortized variational inference with physics-based latent distribution correction", "Inferencia amortizada confiable para imágenes sísmicas del subsuelo")
T_GP = ("Feng y otros", 2024, "Amortized Bayesian Local Interpolation NetworK: Fast covariance parameter estimation for Gaussian Processes",
        "we propose an Amortized Bayesian Local Interpolation NetworK (A-BLINK) for fast covariance parameter estimation", "Una red bayesiana amortizada para los parámetros de un modelo espacial")
T_ALINE = ("Huang y otros", 2025, "ALINE: Joint Amortization for Bayesian Inference and Active Data Acquisition",
           "a unified framework for amortized Bayesian inference and active data acquisition", "Una red que infiere y además elige qué dato conviene medir después")
T_AALR = ("Hermans, Begy y Louppe", 2020, "Likelihood-free MCMC with Amortized Approximate Ratio Estimators",
          "learning a flexible amortized estimator which approximates the likelihood-to-evidence ratio", "Un estimador amortizado para inferir cuando el modelo no tiene fórmula")
T_EPI = ("Hashemi y otros", 2023, "Amortized Bayesian inference on generative dynamical network models of epilepsy using deep neural density estimators",
         "Amortized Bayesian inference on generative dynamical network models of epilepsy", "Inferencia bayesiana amortizada en modelos del cerebro con epilepsia")
T_COMP = ("Radev y otros", 2021, "Amortized Bayesian Model Comparison With Evidential Deep Learning",
          "Amortized Bayesian Model Comparison With Evidential Deep Learning", "Comparar modelos bayesianos con una red amortizada")
T_BF = ("Radev y otros", 2020, "BayesFlow: Learning Complex Stochastic Models With Invertible Neural Networks",
        "a novel method for globally amortized Bayesian inference based on invertible neural networks", "BayesFlow: inferencia bayesiana amortizada con redes invertibles")
T_MIS = ("Schmitt y otros", 2024, "Detecting Model Misspecification in Amortized Bayesian Inference with Neural Networks",
         "Detecting Model Misspecification in Amortized Bayesian Inference with Neural Networks", "Detectar cuándo el modelo no calza, en inferencia bayesiana amortizada")
T_FALTA = ("Wang, Hasenauer y Schälte", 2024, "Missing data in amortized simulation-based neural posterior estimation",
           "amortized simulation-based inference approaches are applicable even with missing data", "Inferencia amortizada cuando faltan datos")
T_GW = ("Dax y otros", 2023, "Neural Importance Sampling for Rapid and Reliable Gravitational-Wave Inference",
        "We combine amortized neural posterior estimation with importance sampling", "Inferencia amortizada para ondas gravitacionales, corregida con muestreo")
T_REV = ("Zammit-Mangion, Sainsbury-Dale y Huser", 2025, "Neural Methods for Amortized Inference",
         "Neural Methods for Amortized Inference", "El review de los métodos con redes para inferencia amortizada")
T_IITK = ("Shreshtth, Hazra y Mukherjee", 2026, "Neural Architectures for Amortized Bayesian Inference: Statistical Foundations and Empirical Assessments",
          "Neural Architectures for Amortized Bayesian Inference", "Qué arquitecturas de red sirven para inferencia bayesiana amortizada")
T_NEU = ("Liu y otros", 2026, "Assessing the robustness of amortized simulation-based inference to transient noise in gravitational-wave ringdowns",
         "we propose an amortized simulation-based inference strategy to estimate ringdown parameters directly", "Inferencia amortizada para el final de una onda gravitacional, con ruido")
T_USR = ("Moon, Oulasvirta y Lee", 2023, "Amortized Inference with User Simulations",
         "Amortized Inference with User Simulations", "Inferencia amortizada para modelos de cómo se comporta un usuario")

LA, NA, EU, AS, OC = "América Latina", "Norteamérica", "Europa", "Asia", "Oceanía"
GRUPOS = [
    # ----- América Latina -----
    g("puc", "Pontificia Universidad Católica de Chile", "Santiago", "Chile", "CL", LA, "latam", -33.499, -70.613, *T_CL,
      OA + " (doi:10.1098/rsta.2024.0215; Carlos Sing-Long, uno de tres autores)"),
    g("ucr", "Universidad de Costa Rica", "San José", "Costa Rica", "CR", LA, "latam", 9.938, -84.051, *T_CR,
      ARXIV + " y OpenAlex (arXiv:2510.02618; doi:10.1016/j.spasta.2026.101052)"),
    # ----- Norteamérica -----
    g("ubc", "University of British Columbia", "Vancouver", "Canadá", "CA", NA, "norteamerica", 49.261, -123.246, *T_SIM,
      ARXIV + " (arXiv:2404.09636; Weilbach y Wood; ICML 2024)"),
    g("notredame", "University of Notre Dame", "Notre Dame", "Estados Unidos", "US", NA, "norteamerica", 41.705, -86.235, *T_CL,
      OA + " (doi:10.1098/rsta.2024.0215; Tong y Schiavazzi)"),
    g("gatech", "Georgia Institute of Technology", "Atlanta", "Estados Unidos", "US", NA, "norteamerica", 33.776, -84.396, *T_GEO,
      OA + " (doi:10.1190/geo2022-0472.1; arXiv:2207.11640; Siahkoohi, Orozco y Herrmann)"),
    g("ncsu", "North Carolina State University", "Raleigh", "Estados Unidos", "US", NA, "norteamerica", 35.785, -78.682, *T_GP,
      ARXIV + " (arXiv:2411.06324; Feng y Reich; preprint)"),
    g("toronto", "University of Toronto", "Toronto", "Canadá", "CA", NA, "norteamerica", 43.663, -79.396, *T_NUS,
      ARXIV + " (arXiv:2504.09475; doi:10.1007/s11222-026-10998-3; Evans)"),
    g("mila", "Mila · Université de Montréal", "Montreal", "Canadá", "CA", NA, "norteamerica", 45.531, -73.613, *T_MILA,
      ARXIV + " (arXiv:2502.06601; Mittal y Lajoie; preprint)"),
    g("rpi", "Rensselaer Polytechnic Institute", "Troy", "Estados Unidos", "US", NA, "norteamerica", 42.730, -73.679, *T_MULTI,
      OA + " (doi:10.1214/25-BA1570; arXiv:2408.13230; Radev)"),
    g("columbia", "Columbia University", "Nueva York", "Estados Unidos", "US", NA, "norteamerica", 40.808, -73.963, *T_AVI,
      ARXIV + " (arXiv:2307.11018; Blei; UAI 2024. Margossian firma desde el Flatiron Institute, también en Nueva York)"),
    # ----- Europa occidental -----
    g("manchester", "University of Manchester", "Mánchester", "Reino Unido", "GB", EU, "europa_oeste", 53.467, -2.234, *T_ALINE,
      ARXIV + " (arXiv:2506.07259; segunda afiliación de Kaski; NeurIPS 2025)"),
    g("utrecht", "Utrecht University", "Utrecht", "Países Bajos", "NL", EU, "europa_oeste", 52.085, 5.172, *T_GEO,
      OA + " (doi:10.1190/geo2022-0472.1; Rizzuti)"),
    g("lieja", "Université de Liège", "Lieja", "Bélgica", "BE", EU, "europa_oeste", 50.586, 5.560, *T_AALR,
      ARXIV + " (arXiv:1903.04057; Hermans y Louppe; ICML 2020)"),
    g("marsella", "Aix-Marseille Université", "Marsella", "Francia", "FR", EU, "europa_oeste", 43.289, 5.404, *T_EPI,
      OA + " (doi:10.1016/j.neunet.2023.03.040; Institut de Neurosciences des Systèmes)"),
    g("trento", "Università di Trento", "Trento", "Italia", "IT", EU, "europa_oeste", 46.066, 11.122, *T_COMP,
      OA + " (doi:10.1109/TNNLS.2021.3124052; D'Alessandro)"),
    # ----- Alemania y Austria -----
    g("dortmund", "TU Dortmund", "Dortmund", "Alemania", "DE", EU, "alemania_austria", 51.492, 7.414, *T_MULTI,
      OA + " (doi:10.1214/25-BA1570; Habermann, Kühmichel y Bürkner)"),
    g("bonn", "Universität Bonn", "Bonn", "Alemania", "DE", EU, "alemania_austria", 50.727, 7.087, *T_FALTA,
      OA + " (doi:10.1371/journal.pcbi.1012184)"),
    g("heidelberg", "Universität Heidelberg", "Heidelberg", "Alemania", "DE", EU, "alemania_austria", 49.398, 8.672, *T_BF,
      OA + " (doi:10.1109/TNNLS.2020.3042395; arXiv:2003.06281; en línea en 2020, en el volumen de 2022)"),
    g("stuttgart", "Universität Stuttgart", "Stuttgart", "Alemania", "DE", EU, "alemania_austria", 48.745, 9.107, *T_MIS,
      OA + " (doi:10.1007/978-3-031-54605-1_35; arXiv:2112.08866; Schmitt y Bürkner)"),
    g("tubinga", "Universität Tübingen", "Tubinga", "Alemania", "DE", EU, "alemania_austria", 48.524, 9.060, *T_SIM,
      ARXIV + " (arXiv:2404.09636; Gloeckler, Deistler y Macke; ICML 2024)"),
    g("helmholtz", "Helmholtz Munich", "Múnich", "Alemania", "DE", EU, "alemania_austria", 48.221, 11.595, *T_FALTA,
      OA + " (doi:10.1371/journal.pcbi.1012184; segunda afiliación de Hasenauer y Schälte)"),
    g("potsdam", "Max-Planck-Institut für Gravitationsphysik", "Potsdam", "Alemania", "DE", EU, "alemania_austria", 52.416, 12.969, *T_GW,
      OA + " (doi:10.1103/PhysRevLett.130.171403)"),
    g("viena", "Universität Wien", "Viena", "Austria", "AT", EU, "alemania_austria", 48.213, 16.360, *T_AALR,
      ARXIV + " (arXiv:1903.04057; Begy)"),
    # ----- Finlandia -----
    g("aalto", "Aalto-yliopisto", "Espoo", "Finlandia", "FI", EU, "finlandia", 60.187, 24.828, *T_ALINE,
      ARXIV + " (arXiv:2506.07259; Huang, Wen, Bharti y Kaski; NeurIPS 2025)"),
    g("helsinki", "Helsingin yliopisto", "Helsinki", "Finlandia", "FI", EU, "finlandia", 60.205, 24.963, *T_ALINE,
      ARXIV + " (arXiv:2506.07259; Acerbi)"),
    # ----- Asia y Oceanía -----
    g("kaust", "KAUST", "Thuwal", "Arabia Saudita", "SA", AS, "asia_oceania", 22.309, 39.104, *T_REV,
      OA + " (doi:10.1146/annurev-statistics-112723-034123; arXiv:2404.12484; Huser y Sainsbury-Dale)"),
    g("iitk", "Indian Institute of Technology Kanpur", "Kanpur", "India", "IN", AS, "asia_oceania", 26.512, 80.233, *T_IITK,
      ARXIV + " (arXiv:2601.07944; Shreshtth y Hazra; preprint)"),
    g("nus", "National University of Singapore", "Singapur", "Singapur", "SG", AS, "asia_oceania", 1.297, 103.776, *T_NUS,
      ARXIV + " y OpenAlex (arXiv:2504.09475; doi:10.1007/s11222-026-10998-3; Wang y Nott)"),
    g("neu", "Northeastern University", "Shenyang", "China", "CN", AS, "asia_oceania", 41.765, 123.421, *T_NEU,
      OA + " (doi:10.1103/cbk2-178c; es la universidad de Shenyang, no la de Boston)"),
    g("yonsei", "Yonsei University", "Seúl", "Corea del Sur", "KR", AS, "asia_oceania", 37.566, 126.939, *T_USR,
      OA + " (doi:10.1145/3544548.3581439; Moon y Lee; CHI 2023)"),
    g("wollongong", "University of Wollongong", "Wollongong", "Australia", "AU", OC, "asia_oceania", -34.405, 150.878, *T_REV,
      OA + " (doi:10.1146/annurev-statistics-112723-034123; Zammit-Mangion y Sainsbury-Dale)"),
]

# El recorrido: en qué orden pasa la cámara y cómo se llama cada parada en pantalla.
PARADAS = [
    dict(id="latam", nombre="América Latina"),
    dict(id="norteamerica", nombre="Norteamérica"),
    dict(id="europa_oeste", nombre="Europa occidental"),
    dict(id="alemania_austria", nombre="Alemania y Austria"),
    dict(id="finlandia", nombre="Finlandia"),
    dict(id="asia_oceania", nombre="Asia y Oceanía"),
]

# ---------- la proyección de Robinson (tabla de cada 5°) ----------
ROB_X = [1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600, 0.9427, 0.9216, 0.8962,
         0.8679, 0.8350, 0.7986, 0.7597, 0.7186, 0.6732, 0.6213, 0.5722, 0.5322]
ROB_Y = [0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720, 0.4340, 0.4958, 0.5571,
         0.6176, 0.6769, 0.7346, 0.7903, 0.8435, 0.8936, 0.9394, 0.9761, 1.0000]
ANCHO = 36.0                                  # el mundo mide 36 unidades de escena de lado a lado
S = (ANCHO / 2) / (0.8487 * math.pi)
PASO = 0.05                                   # separación de la rejilla de puntos más fina, en unidades de escena
LAT_N, LAT_S = 84.0, -58.0                    # sin los polos ni la Antártica


def _tabla(tabla, lat):
    a = min(abs(lat), 90.0) / 5.0
    i = min(17, int(a))
    return tabla[i] + (tabla[i + 1] - tabla[i]) * (a - i)


def proyectar(lon, lat):
    return 0.8487 * S * _tabla(ROB_X, lat) * math.radians(lon), 1.3523 * S * _tabla(ROB_Y, lat) * (1 if lat >= 0 else -1)


def invertir(x, y):
    yn = abs(y) / (1.3523 * S)
    if yn > 1:
        return None
    i = 0
    while i < 17 and ROB_Y[i + 1] < yn:
        i += 1
    lat = 5.0 * (i + (yn - ROB_Y[i]) / (ROB_Y[i + 1] - ROB_Y[i]))
    lon = math.degrees(x / (0.8487 * S * _tabla(ROB_X, lat)))
    if abs(lon) > 180:
        return None
    return lon, lat if y >= 0 else -lat


# ---------- la tierra firme, en una rejilla de un cuarto de grado ----------
def tierra(ruta):
    RES = 0.25
    W, H = int(360 / RES), int(180 / RES)
    cruces = [[] for _ in range(H)]
    geo = json.loads(pathlib.Path(ruta).read_text())

    def anillo(puntos):
        for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
            if y1 == y2:
                continue
            arriba, abajo = max(y1, y2), min(y1, y2)
            r0 = max(0, math.ceil((90 - arriba) / RES - 0.5))
            r1 = min(H - 1, math.ceil((90 - abajo) / RES - 0.5) - 1)
            for r in range(r0, r1 + 1):
                lat = 90 - (r + 0.5) * RES
                cruces[r].append(x1 + (x2 - x1) * (lat - y1) / (y2 - y1))

    for f in geo["features"]:
        g = f["geometry"]
        for poligono in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            for a in poligono:
                anillo([(p[0], p[1]) for p in a])
    filas = []
    for r in range(H):
        fila = bytearray(W)
        xs = sorted(cruces[r])
        for a, b in zip(xs[0::2], xs[1::2]):
            c0 = max(0, math.ceil((a + 180) / RES - 0.5))
            c1 = min(W - 1, math.ceil((b + 180) / RES - 0.5) - 1)
            for c in range(c0, c1 + 1):
                fila[c] = 1
        filas.append(fila)
    return lambda lon, lat: filas[min(H - 1, max(0, int((90 - lat) / RES)))][min(W - 1, max(0, int((lon + 180) / RES)))]


def main():
    salida = AQUI / "laboratorios.js"
    ids = [x["id"] for x in GRUPOS]
    assert len(set(ids)) == len(ids)
    assert all(x["parada"] in [p["id"] for p in PARADAS] for x in GRUPOS)
    assert all(x["anio"] >= CRITERIO["desde"] and "amortiz" in (x["titulo"] + " " + x["frase"]).lower() for x in GRUPOS)
    if len(sys.argv) < 2:                                   # sin el archivo de Natural Earth: se conserva la rejilla que ya existe
        viejo = salida.read_text()
        viejo = json.loads(viejo[viejo.index("{"):viejo.rindex("}") + 1])
        proyeccion, mapa = viejo["proyeccion"], viejo["mapa"]
    else:
        es_tierra = tierra(sys.argv[1])
        y_n, y_s = proyectar(0, LAT_N)[1], proyectar(0, LAT_S)[1]
        cols, filas = int(round(ANCHO / PASO)), int(math.ceil((y_n - y_s) / PASO))
        bits = bytearray((cols * filas + 7) // 8)
        puntos = 0
        for r in range(filas):
            y = y_n - (r + 0.5) * PASO
            for c in range(cols):
                q = invertir(-ANCHO / 2 + (c + 0.5) * PASO, y)
                if q and es_tierra(*q):
                    k = r * cols + c
                    bits[k >> 3] |= 1 << (k & 7)
                    puntos += 1
        proyeccion = {"nombre": "Robinson", "escala": round(S, 6), "x": ROB_X, "y": ROB_Y}
        mapa = {"cols": cols, "filas": filas, "paso": PASO, "x0": -ANCHO / 2, "y_norte": round(y_n, 5), "puntos": puntos,
                "origen": "Natural Earth, ne_50m_land (dominio público)", "b64": base64.b64encode(bytes(bits)).decode()}
    datos = {
        "generado": date.today().isoformat(),
        "comando": "python3 pitch/deck/datos/generar_laboratorios.py [ne_50m_land.geojson]",
        "criterio": CRITERIO,
        "proyeccion": proyeccion,
        "mapa": mapa,
        "paradas": PARADAS,
        "grupos": GRUPOS,
    }
    salida.write_text(
        "/* Los laboratorios del mapa (lámina W). Lo escribe datos/generar_laboratorios.py: no se edita a mano.\n"
        "   Grupos: los que publican amortized Bayesian inference con esas palabras, de 2020 en adelante (un trabajo por grupo).\n"
        "   Mapa: tierra firme de Natural Earth (dominio público), como rejilla de puntos en proyección de Robinson. */\n"
        "window.KRYLOV_LABORATORIOS = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    paises = sorted({x["pais"] for x in GRUPOS})
    trabajos = sorted({(x["cita"], x["anio"]) for x in GRUPOS})
    print(f"{salida}: {len(GRUPOS)} grupos, {len(paises)} países, {len(trabajos)} trabajos, de {min(t[1] for t in trabajos)} a {max(t[1] for t in trabajos)}")
    print(", ".join(paises))


if __name__ == "__main__":
    main()
