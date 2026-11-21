# Compara lo que respondió cada corrida del LLM con lo que respondió Krylov, contra las 68 muestras escondidas.
#   python3 pitch/deck/datos/prueba_llm/medir.py        (escribe resultado.json en esta carpeta)
import csv, json, pathlib
AQUI = pathlib.Path(__file__).parent
LIMITE = 500
def leer(ruta): return {f["pozo"]: f for f in csv.DictReader(open(AQUI / ruta))}
K = leer("krylov.csv"); pozos = list(K); verdad = {p: float(K[p]["verdad"]) for p in pozos}
res, est = {}, {}
def medir(nombre, R, segundos=None):
    pr = {p: float(R[p]["as_ppm"]) for p in pozos}; lo = {p: float(R[p]["bajo"]) for p in pozos}; hi = {p: float(R[p]["alto"]) for p in pozos}
    res[nombre] = dict(n=len(pozos), dentro=sum(lo[p] <= verdad[p] <= hi[p] for p in pozos),
                       ancho_medio=round(sum(hi[p] - lo[p] for p in pozos) / len(pozos)),
                       error_medio=round(sum(abs(pr[p] - verdad[p]) for p in pozos) / len(pozos)),
                       lado_del_limite_bien=sum((pr[p] > LIMITE) == (verdad[p] > LIMITE) for p in pozos),
                       en_duda=sum(lo[p] <= LIMITE <= hi[p] for p in pozos), segundos=segundos)
    est[nombre] = pr
medir("krylov", K)
for c in "ab":
    medir("llm_" + c, leer(f"{c}/respuesta.csv"), int((AQUI / c / "fin.txt").read_text()) - int((AQUI / c / "inicio.txt").read_text()))
a, b = est["llm_a"], est["llm_b"]
res["entre_corridas"] = dict(diferencia_media_ppm=round(sum(abs(a[p] - b[p]) for p in pozos) / len(pozos)),
                             diferencia_maxima_ppm=round(max(abs(a[p] - b[p]) for p in pozos)),
                             cambia_de_lado_del_limite=sum((a[p] > LIMITE) != (b[p] > LIMITE) for p in pozos))
(AQUI / "resultado.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(res, indent=1, ensure_ascii=False))
