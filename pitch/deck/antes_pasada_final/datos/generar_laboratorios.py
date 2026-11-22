#!/usr/bin/env python3
"""Genera pitch/deck/datos/laboratorios.js: lo que dibuja la lámina W del deck (tecla W).

    python3 pitch/deck/datos/generar_laboratorios.py /ruta/a/ne_50m_land.geojson

Dos cosas salen de aquí:

1. Los grupos de investigación. Son las instituciones que firman el review «Neural Methods for Amortized Inference»
   (Zammit-Mangion, Sainsbury-Dale y Huser; Annual Review of Statistics and Its Application, 2025;
   doi:10.1146/annurev-statistics-112723-034123; arXiv:2404.12484) y las de los autores de métodos y software que ese
   review cita. La afiliación de cada grupo es la del trabajo citado, no necesariamente la de hoy. Se comprobó el
   21-nov-2026 en el propio review (sus tres autores), en OpenAlex (api.openalex.org/works/doi:…) y, para Tübingen y
   British Columbia, en la portada del artículo (arxiv.org/html/2404.09636). Un grupo cuya afiliación no se pudo
   comprobar no entra: por eso la lista no es exhaustiva. El año es el que lleva la cita en el review.

2. El mapa. La tierra firme de Natural Earth (ne_50m_land, dominio público, naturalearthdata.com), pasada a una
   rejilla de puntos en proyección de Robinson. El archivo de origen se descarga una vez:
   https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson
   El deck no lo necesita: la rejilla queda dentro de laboratorios.js, como bits en base64.
"""
import base64
import json
import math
import pathlib
import sys
from datetime import date

AQUI = pathlib.Path(__file__).resolve().parent

REVIEW = {
    "autores": "Zammit-Mangion, Sainsbury-Dale y Huser",
    "titulo": "Neural Methods for Amortized Inference",
    "revista": "Annual Review of Statistics and Its Application",
    "anio": 2025,
    "doi": "10.1146/annurev-statistics-112723-034123",
    "arxiv": "2404.12484",
}

# El trabajo más antiguo de la lista en que una red entrega la respuesta completa a partir de simulaciones.
PRIMER_TRABAJO = {"cita": "Papamakarios y Murray", "anio": 2016}

OA = "Afiliación del trabajo citado, según OpenAlex"
GRUPOS = [
    # ----- Sudamérica -----
    dict(id="utfsm", institucion="Universidad Técnica Federico Santa María", ciudad="Valparaíso", pais="Chile", iso="CL",
         continente="Sudamérica", parada="chile", lat=-33.035, lon=-71.596, cita="Cranmer, Pavez y Louppe", anio=2015,
         aporte="Coautoría del método que compara hipótesis con un clasificador calibrado",
         fuente=OA + " (arXiv:1506.02169; Juan Pavez)"),
    # ----- Norteamérica -----
    dict(id="ubc", institucion="University of British Columbia", ciudad="Vancouver", pais="Canadá", iso="CA",
         continente="Norteamérica", parada="norteamerica", lat=49.261, lon=-123.246, cita="Glöckler y otros", anio=2024,
         aporte="Una sola red que responde muchas preguntas sobre el mismo simulador",
         fuente="Afiliación impresa en el artículo (arXiv:2404.09636; Weilbach y Wood)"),
    dict(id="berkeley", institucion="University of California, Berkeley", ciudad="Berkeley", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=37.872, lon=-122.259, cita="Chan y otros", anio=2018,
         aporte="Redes que infieren desde simulaciones en genética de poblaciones",
         fuente=OA + " (arXiv:1802.06153)"),
    dict(id="irvine", institucion="University of California, Irvine", ciudad="Irvine", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=33.646, lon=-117.843, cita="Baldi y otros", anio=2016,
         aporte="Redes que reciben los parámetros como entrada, en física de partículas",
         fuente=OA + " (doi:10.1140/epjc/s10052-016-4099-4)"),
    dict(id="mines", institucion="Colorado School of Mines", ciudad="Golden", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=39.751, lon=-105.223, cita="Gerber y Nychka", anio=2021,
         aporte="Redes que estiman los parámetros de modelos espaciales",
         fuente=OA + " (doi:10.1002/sta4.382)"),
    dict(id="missouri", institucion="University of Missouri", ciudad="Columbia", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=38.940, lon=-92.328, cita="Zammit-Mangion y Wikle", anio=2020,
         aporte="Pronósticos en el espacio y en el tiempo con redes",
         fuente=OA + " (doi:10.1016/j.spasta.2020.100408; Wikle)"),
    dict(id="argonne", institucion="Argonne National Laboratory", ciudad="Lemont", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=41.718, lon=-87.979, cita="Rudi y otros", anio=2022,
         aporte="Redes que estiman parámetros de modelos que no tienen fórmula cerrada",
         fuente=OA + " (arXiv:2012.06691; doi:10.1016/j.csda.2023.107762)"),
    dict(id="cmu", institucion="Carnegie Mellon University", ciudad="Pittsburgh", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=40.443, lon=-79.943, cita="Walchessen y otros", anio=2023,
         aporte="Redes para modelos espaciales muy caros de calcular",
         fuente=OA + " (arXiv:2305.04634)"),
    dict(id="nyu", institucion="New York University", ciudad="Nueva York", pais="Estados Unidos", iso="US",
         continente="Norteamérica", parada="norteamerica", lat=40.730, lon=-73.997, cita="Cranmer, Pavez y Louppe", anio=2015,
         aporte="Comparar hipótesis con un clasificador calibrado",
         fuente=OA + " (arXiv:1506.02169)"),
    # ----- Europa occidental -----
    dict(id="edimburgo", institucion="University of Edinburgh", ciudad="Edimburgo", pais="Reino Unido", iso="GB",
         continente="Europa", parada="europa_oeste", lat=55.944, lon=-3.187, cita="Papamakarios y Murray", anio=2016,
         aporte="La red aprende la respuesta completa a partir de simulaciones",
         fuente=OA + " (arXiv:1605.06376; arXiv:1805.07226)"),
    dict(id="warwick", institucion="University of Warwick", ciudad="Coventry", pais="Reino Unido", iso="GB",
         continente="Europa", parada="europa_oeste", lat=52.379, lon=-1.561, cita="Pacchiardi y Dutta", anio=2022,
         aporte="Redes generativas entrenadas con reglas de puntaje",
         fuente=OA + " (arXiv:2205.15784; Dutta. También arXiv:1802.06153)"),
    dict(id="oxford", institucion="University of Oxford", ciudad="Oxford", pais="Reino Unido", iso="GB",
         continente="Europa", parada="europa_oeste", lat=51.755, lon=-1.255, cita="Pacchiardi y Dutta", anio=2022,
         aporte="Redes generativas entrenadas con reglas de puntaje",
         fuente=OA + " (arXiv:2205.15784; Pacchiardi)"),
    dict(id="deepmind", institucion="Google DeepMind", ciudad="Londres", pais="Reino Unido", iso="GB",
         continente="Europa", parada="europa_oeste", lat=51.533, lon=-0.126, cita="Rezende y Mohamed", anio=2015,
         aporte="Los flujos normalizadores, con que una red dibuja distribuciones enteras",
         fuente=OA + " (arXiv:1505.05770; arXiv:1402.0030)"),
    dict(id="amsterdam", institucion="University of Amsterdam", ciudad="Ámsterdam", pais="Países Bajos", iso="NL",
         continente="Europa", parada="europa_oeste", lat=52.355, lon=4.955, cita="Kingma y Welling", anio=2013,
         aporte="El autoencoder variacional; después, el software swyft",
         fuente=OA + " (arXiv:1312.6114; doi:10.21105/joss.04205)"),
    dict(id="lieja", institucion="Université de Liège", ciudad="Lieja", pais="Bélgica", iso="BE",
         continente="Europa", parada="europa_oeste", lat=50.586, lon=5.560, cita="Hermans, Begy y Louppe", anio=2020,
         aporte="Redes que pesan qué explicación calza mejor con los datos; software LAMPE",
         fuente=OA + " (arXiv:1903.04057; arXiv:2110.00449; arXiv:2208.13624)"),
    dict(id="paris", institucion="Institut d'Astrophysique de Paris", ciudad="París", pais="Francia", iso="FR",
         continente="Europa", parada="europa_oeste", lat=48.836, lon=2.336, cita="Charnock, Lavaux y Wandelt", anio=2018,
         aporte="Redes que resumen los datos sin perder información",
         fuente=OA + " (doi:10.1103/PhysRevD.97.083004)"),
    # ----- Alemania y Austria -----
    dict(id="dortmund", institucion="TU Dortmund", ciudad="Dortmund", pais="Alemania", iso="DE",
         continente="Europa", parada="alemania_austria", lat=51.492, lon=7.414, cita="Radev y otros", anio=2023,
         aporte="Coautoría del software BayesFlow",
         fuente=OA + " (doi:10.21105/joss.05702; Bürkner)"),
    dict(id="bonn", institucion="Centro de investigación caesar (Max Planck)", ciudad="Bonn", pais="Alemania", iso="DE",
         continente="Europa", parada="alemania_austria", lat=50.703, lon=7.151, cita="Lueckmann y otros", anio=2017,
         aporte="Inferencia con redes para modelos de neuronas",
         fuente=OA + " (arXiv:1711.01861)"),
    dict(id="heidelberg", institucion="Universität Heidelberg", ciudad="Heidelberg", pais="Alemania", iso="DE",
         continente="Europa", parada="alemania_austria", lat=49.398, lon=8.672, cita="Radev y otros", anio=2022,
         aporte="BayesFlow: redes invertibles que entregan la respuesta completa",
         fuente=OA + " (doi:10.1109/TNNLS.2020.3042395; arXiv:1808.04730)"),
    dict(id="tubinga", institucion="Universität Tübingen", ciudad="Tubinga", pais="Alemania", iso="DE",
         continente="Europa", parada="alemania_austria", lat=48.524, lon=9.060, cita="Glöckler y otros", anio=2024,
         aporte="Una sola red que responde muchas preguntas sobre el mismo simulador",
         fuente="Afiliación impresa en el artículo (arXiv:2404.09636; Glöckler, Deistler y Macke)"),
    dict(id="munich", institucion="Technische Universität München", ciudad="Múnich", pais="Alemania", iso="DE",
         continente="Europa", parada="alemania_austria", lat=48.149, lon=11.568, cita="Tejero-Cantero y otros", anio=2020,
         aporte="El software sbi, para inferir con simulaciones",
         fuente=OA + " (doi:10.21105/joss.02505)"),
    dict(id="viena", institucion="Universität Wien", ciudad="Viena", pais="Austria", iso="AT",
         continente="Europa", parada="alemania_austria", lat=48.213, lon=16.360, cita="Hermans, Begy y Louppe", anio=2020,
         aporte="Coautoría del método de Lieja",
         fuente=OA + " (arXiv:1903.04057; Begy)"),
    # ----- Países nórdicos -----
    dict(id="oslo", institucion="Universitetet i Oslo", ciudad="Oslo", pais="Noruega", iso="NO",
         continente="Europa", parada="nordicos", lat=59.940, lon=10.722, cita="Thomas y otros", anio=2022,
         aporte="Inferir comparando datos simulados con datos reales",
         fuente=OA + " (doi:10.1214/20-BA1238)"),
    dict(id="gotemburgo", institucion="Chalmers tekniska högskola", ciudad="Gotemburgo", pais="Suecia", iso="SE",
         continente="Europa", parada="nordicos", lat=57.690, lon=11.974, cita="Wiqvist, Frellsen y Picchini", anio=2021,
         aporte="Aprender la respuesta y el modelo a la vez, por rondas",
         fuente=OA + " (arXiv:2102.06522; Picchini)"),
    dict(id="lyngby", institucion="Danmarks Tekniske Universitet", ciudad="Kongens Lyngby", pais="Dinamarca", iso="DK",
         continente="Europa", parada="nordicos", lat=55.786, lon=12.523, cita="Wiqvist, Frellsen y Picchini", anio=2021,
         aporte="Aprender la respuesta y el modelo a la vez, por rondas",
         fuente=OA + " (arXiv:2102.06522; Frellsen)"),
    dict(id="lund", institucion="Lunds universitet", ciudad="Lund", pais="Suecia", iso="SE",
         continente="Europa", parada="nordicos", lat=55.712, lon=13.203, cita="Wiqvist, Frellsen y Picchini", anio=2021,
         aporte="Aprender la respuesta y el modelo a la vez, por rondas",
         fuente=OA + " (arXiv:2102.06522; Wiqvist)"),
    dict(id="uppsala", institucion="Uppsala universitet", ciudad="Upsala", pais="Suecia", iso="SE",
         continente="Europa", parada="nordicos", lat=59.850, lon=17.630, cita="Åkesson y otros", anio=2021,
         aporte="Redes convolucionales que resumen los datos",
         fuente=OA + " (doi:10.1109/TCBB.2021.3108695)"),
    dict(id="helsinki", institucion="Helsingin yliopisto", ciudad="Helsinki", pais="Finlandia", iso="FI",
         continente="Europa", parada="nordicos", lat=60.205, lon=24.963, cita="Gutmann y Hyvärinen", anio=2012,
         aporte="Estimar comparando contra ruido, la base de varios de estos métodos",
         fuente=OA + " (JMLR 13, 2012)"),
    # ----- Los autores del review -----
    dict(id="kaust", institucion="KAUST", ciudad="Thuwal", pais="Arabia Saudita", iso="SA",
         continente="Asia", parada="review", lat=22.309, lon=39.104, cita="Zammit-Mangion, Sainsbury-Dale y Huser", anio=2025,
         aporte="Coescribió el review",
         fuente="Afiliación impresa en el review (Huser y Sainsbury-Dale)"),
    dict(id="wollongong", institucion="University of Wollongong", ciudad="Wollongong", pais="Australia", iso="AU",
         continente="Oceanía", parada="review", lat=-34.405, lon=150.878, cita="Zammit-Mangion, Sainsbury-Dale y Huser", anio=2025,
         aporte="Coescribió el review; software NeuralEstimators",
         fuente="Afiliación impresa en el review (Zammit-Mangion y Sainsbury-Dale)"),
]

# El recorrido: en qué orden pasa la cámara y cómo se llama cada parada en pantalla.
PARADAS = [
    dict(id="chile", nombre="Chile"),
    dict(id="norteamerica", nombre="Norteamérica"),
    dict(id="europa_oeste", nombre="Europa occidental"),
    dict(id="alemania_austria", nombre="Alemania y Austria"),
    dict(id="nordicos", nombre="Países nórdicos"),
    dict(id="review", nombre="Los autores del review"),
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
    if len(sys.argv) < 2:
        sys.exit(__doc__)
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
    ids = [g["id"] for g in GRUPOS]
    assert len(set(ids)) == len(ids)
    assert all(g["parada"] in [p["id"] for p in PARADAS] for g in GRUPOS)
    datos = {
        "generado": date.today().isoformat(),
        "comando": "python3 pitch/deck/datos/generar_laboratorios.py ne_50m_land.geojson",
        "review": REVIEW,
        "primer_trabajo": PRIMER_TRABAJO,
        "proyeccion": {"nombre": "Robinson", "escala": round(S, 6), "x": ROB_X, "y": ROB_Y},
        "mapa": {"cols": cols, "filas": filas, "paso": PASO, "x0": -ANCHO / 2, "y_norte": round(y_n, 5), "puntos": puntos,
                 "origen": "Natural Earth, ne_50m_land (dominio público)", "b64": base64.b64encode(bytes(bits)).decode()},
        "paradas": PARADAS,
        "grupos": GRUPOS,
    }
    salida = AQUI / "laboratorios.js"
    salida.write_text(
        "/* Los laboratorios del mapa (lámina W). Lo escribe datos/generar_laboratorios.py: no se edita a mano.\n"
        "   Grupos: instituciones del review «Neural Methods for Amortized Inference» (2025) y de los trabajos que cita.\n"
        "   Mapa: tierra firme de Natural Earth (dominio público), como rejilla de puntos en proyección de Robinson. */\n"
        "window.KRYLOV_LABORATORIOS = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    paises = sorted({g["pais"] for g in GRUPOS})
    print(f"{salida}: {len(GRUPOS)} grupos, {len(paises)} países, {puntos} puntos de tierra, rejilla {cols} x {filas}")
    print(", ".join(paises))


if __name__ == "__main__":
    main()
