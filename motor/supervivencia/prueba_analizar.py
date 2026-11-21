"""`analizar`, `nube` y `cartera` de rotación de punta a punta, con la red sin entrenar y con muestras «de MCMC» inventadas.

Prueba la forma de la respuesta y la mecánica (lectura, filas, onnxruntime, flujo en NumPy, paso local,
decisión, examen, semáforo). Los valores no significan nada: la red no está entrenada. No se compara la
redacción de los textos, que sale de `casos/textos.yaml`.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from motor.supervivencia import exportar, nube as generar_nube, red as red_sv, simular
from nucleo import api, cartera as comun, casos, supervivencia as sv

EJEMPLOS = Path(__file__).resolve().parents[2] / "contratos" / "ejemplos"
QUITAR = "quitar_factor:fecha_salida"


@pytest.fixture(scope="module")
def artefactos(tmp_path_factory):
    """Una carpeta de artefactos de prueba: red sin entrenar, nube chica y un «MCMC» que son muestras del prior."""
    carpeta = tmp_path_factory.mktemp("artefactos")
    (carpeta / "supervivencia").mkdir()
    exportar.exportar(red_sv.construir(), carpeta / "supervivencia")
    generar_nube.generar(carpeta / "supervivencia", simulaciones=1000)   # menos no alcanza para una covarianza de 128 × 128
    (carpeta / "supervivencia" / "mcmc").mkdir()
    del_prior = sv.a_libre(simular.muestrear_prior(np.random.default_rng(0), 200, simular.cargar_config()["prior"]))
    for clave in ("rotacion", "rotacion_malo__quitar_factor-fecha_salida"):
        np.savez(carpeta / "supervivencia" / "mcmc" / f"{clave}.npz", theta=del_prior)
    return carpeta


@pytest.fixture
def con(artefactos, monkeypatch):
    def elegir(impl):
        monkeypatch.setattr(casos, "ARTEFACTOS", artefactos)
        monkeypatch.setenv("KRYLOV_MOTOR_SUPERVIVENCIA", impl)
    return elegir


@pytest.mark.parametrize("impl", ["red", "mcmc"])
def test_analizar_rotacion(con, impl):
    con(impl)
    r = api.analizar("rotacion")
    assert "error" not in r, r
    ejemplo = json.loads((EJEMPLOS / "analizar_tabla.json").read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(r), set(ejemplo) - set(r)
    assert r["motor_id"] == "supervivencia" and r["implementacion"] == impl and r["precalculado"] is (impl == "mcmc")
    assert len(r["unidades"]) == 294 and set(r["unidades"][0]) == set(ejemplo["unidades"][0])
    assert all(len(u["muestras_p"]) == 32 and 0 <= u["rango_bajo"] <= u["rango_alto"] <= 1 for u in r["unidades"])
    assert r["unidades"][0]["duda"] >= r["unidades"][-1]["duda"] >= 0
    assert sum(r["resumen_colores"].values()) == 294 and r["costo_de_no_saber"]["valor"] >= 0
    assert [set(f) for f in r["factores"]] == [set(ejemplo["factores"][0])] * 5
    assert {f["nombre"] for f in r["factores"]} == {"OverTime", "DistanceFromHome", "NumCompaniesWorked", "MonthlyIncome", "compromiso"}
    assert {f["etiqueta"] for f in r["factores"]} >= {"Horas extra", "Sueldo"}                # las etiquetas salen del caso
    assert r["examen"]["tipo"] == "datos_reales_reservados" and r["examen"]["n"] == 294 and sum(t["n"] for t in r["examen"]["tramos"]) <= 294
    assert r["registro"][0] == "294 personas por decidir" and "9 cargos" in r["registro"]
    assert r["semaforo"]["estado"] == "verde" and set(r["columnas"]) == set(ejemplo["columnas"])
    json.dumps(r)
    assert api.analizar("rotacion")["unidades"] == r["unidades"]                              # semilla fija
    caros = api.analizar("rotacion", costos={"falso_si": 3000})                              # los costos cambian la decisión, no las p
    assert sorted(u["p"] for u in caros["unidades"]) == sorted(u["p"] for u in r["unidades"])
    assert api.analizar("rotacion", transformaciones=["quitar_factor:OverTime"])["codigo"] == "no_disponible"


@pytest.mark.parametrize("impl", ["red", "mcmc"])
def test_el_archivo_malo_sale_rojo_y_corregido_verde(con, impl):
    con(impl)
    rojo = api.analizar("rotacion_malo")
    ejemplo = json.loads((EJEMPLOS / "analizar_rojo.json").read_text(encoding="utf-8"))
    assert set(ejemplo) - {"_aviso"} <= set(rojo), set(ejemplo) - set(rojo)
    assert rojo["semaforo"]["estado"] == "rojo_modelo" and rojo["semaforo"]["motivo"]
    assert rojo["semaforo"]["propuesta"]["transformacion"] == QUITAR and rojo["semaforo"]["propuesta"]["texto"]
    assert rojo["unidades"] is None and rojo["factores"] is None and rojo["costo_de_no_saber"] is None and rojo["resumen_colores"] is None
    assert "fecha_salida" in rojo["columnas"]["usadas"] and rojo["titular"]
    json.dumps(rojo)

    verde = api.analizar("rotacion_malo", transformaciones=[rojo["semaforo"]["propuesta"]["transformacion"]])
    assert "error" not in verde, verde
    assert verde["semaforo"]["estado"] == "verde" and verde["semaforo"]["propuesta"] is None and len(verde["unidades"]) == 294
    assert "fecha_salida" not in verde["columnas"]["usadas"] and verde["examen"] is None      # el caso malo no trae archivo de verdad
    # El modelo no usa esa columna: corregido, responde lo mismo que el archivo bueno.
    assert sorted(u["p"] for u in verde["unidades"]) == sorted(u["p"] for u in api.analizar("rotacion")["unidades"])


SUBIDA = {"id": "n_empleado", "evento": "renuncio", "tiempo": "anios_en_empresa", "grupo": "cargo", "suave": "sueldo_mensual",
          "efectos": ["horas_extra", "distancia_km", "empresas_previas"], "encuestas": ["enc_ambiente", "enc_trabajo", "enc_relaciones", "enc_equilibrio"]}


def test_el_archivo_del_demo_subido_responde_lo_mismo(con):
    """D-34: `analizar_archivo` con la tabla del demo y sus columnas da las mismas probabilidades que `analizar`, sin examen."""
    con("red")
    caso = casos.cargar_caso("rotacion")
    tabla = casos.leer_columnas(caso["dataset"])
    del_demo = api.analizar("rotacion")
    subido = api.analizar_archivo("supervivencia", tabla, {papel: caso["columnas"][papel] for papel in SUBIDA})
    assert "error" not in subido, subido
    assert set(subido) == set(del_demo) and subido["caso"] == "rotacion" and subido["implementacion"] == "red"
    assert subido["unidades"] == del_demo["unidades"] and subido["factores"] == del_demo["factores"]
    assert subido["examen"] is None and del_demo["examen"] is not None                         # un archivo propio no trae respuestas escondidas
    assert subido["columnas"]["elegidas_por"] == "usuario" and subido["columnas"]["disponibles"] == len(tabla)
    # La forma de D-35 (columnas y transformación por papel), sin transformación, es el mismo calce.
    con_forma = {papel: {"columnas": sv.columnas_del_papel(caso["columnas"], papel), "transformacion": None} for papel in SUBIDA}
    assert api.analizar_archivo("supervivencia", tabla, con_forma)["unidades"] == del_demo["unidades"]
    # Una columna que delata la respuesta, declarada como `extra`: rojo con la misma propuesta que el archivo malo del demo.
    malo = casos.cargar_caso("rotacion_malo")
    rojo = api.analizar_archivo("supervivencia", casos.leer_columnas(malo["dataset"]), {**{p: malo["columnas"][p] for p in SUBIDA}, "extra": ["fecha_salida"]})
    assert rojo["semaforo"]["estado"] == "rojo_modelo" and rojo["semaforo"]["propuesta"]["transformacion"] == QUITAR and rojo["unidades"] is None
    json.dumps(subido)


def test_un_archivo_propio_no_se_responde_con_el_mcmc_del_demo(con):
    con("mcmc")
    caso = casos.cargar_caso("rotacion")
    r = api.analizar_archivo("supervivencia", casos.leer_columnas(caso["dataset"]), {papel: caso["columnas"][papel] for papel in SUBIDA})
    assert r["codigo"] == "no_disponible"                                                     # hay `mcmc/rotacion.npz`, y no es de este archivo


@pytest.mark.parametrize("area, personas, por_decidir, cargos", [("ventas", 446, 89, 3), ("investigacion", 961, 192, 6)])
def test_archivos_de_prueba_de_la_subida(con, monkeypatch, area, personas, por_decidir, cargos):
    """Otras empresas con el mismo esquema (áreas del archivo público, columnas en español y en otro orden): la misma red las responde.

    Con la red sin entrenar el segundo detector de la nube no significa nada: aquí va como aviso, para probar la respuesta.
    """
    con("red")
    monkeypatch.setenv("KRYLOV_NUBE_SEGUNDO_DETECTOR", "aviso")
    crudo = (casos.RAIZ / "datos" / "demo" / f"subida_rotacion_{area}.csv").read_bytes()     # el CSV tal como llega del navegador
    r = api.analizar_archivo("supervivencia", crudo, SUBIDA)
    assert "error" not in r, r
    assert r["semaforo"]["estado"] in ("verde", "amarillo") and len(r["unidades"]) == por_decidir == sum(r["resumen_colores"].values())
    assert r["registro"][:3] == [f"{por_decidir} personas por decidir", f"{personas} en el archivo", f"{cargos} cargos"]
    assert {f["nombre"] for f in r["factores"]} == {"horas_extra", "distancia_km", "empresas_previas", "sueldo_mensual", "compromiso"}
    assert r["costo_de_no_saber"]["valor"] >= 0 and r["titular"] and r["examen"] is None
    assert api.analizar_archivo("supervivencia", crudo, SUBIDA, {"falso_si": 3000})["punto_de_corte"] != r["punto_de_corte"]
    json.dumps(r)


def test_un_archivo_subido_se_ubica_en_la_nube_de_su_tamano(artefactos, con, tmp_path):
    """La nube se simula con el n del archivo: uno subido usa la nube guardada del tamaño más cercano; el del demo, la suya."""
    import shutil
    from nucleo import nube as comun
    copia = tmp_path / "artefactos"
    shutil.copytree(artefactos, copia)
    con("red")
    casos.ARTEFACTOS = copia                                                                  # `con` ya lo dejó bajo monkeypatch
    generada = generar_nube.generar(copia / "supervivencia", simulaciones=1000, personas=450)
    assert generada["personas_por_empresa"] == 450 and Path(generada["ruta"]).name == sv.nube_del_tamano(450)
    de_450, del_caso = (comun.cargar(copia / "supervivencia" / nombre) for nombre in (sv.nube_del_tamano(450), "nube.npz"))
    ventas = {**casos.cargar_caso("rotacion"), "tabla": casos.leer_columnas("datos/demo/subida_rotacion_ventas.csv"), "columnas": SUBIDA}   # 446 personas
    investigacion = {**ventas, "tabla": casos.leer_columnas("datos/demo/subida_rotacion_investigacion.csv")}                              # 961: más cerca de 1.470
    limite = lambda caso: sv.nube(caso, [])["detectores"]["resumenes_aprendidos"]["limite"]   # noqa: E731
    assert round(float(de_450["limite"]), 2) != round(float(del_caso["limite"]), 2)
    assert limite(ventas) == round(float(de_450["limite"]), 2)
    assert limite(investigacion) == limite(casos.cargar_caso("rotacion")) == round(float(del_caso["limite"]), 2)


def test_nube_malo_cae_fuera_y_corregido_dentro(con):
    con("red")
    ejemplo = json.loads((EJEMPLOS / "nube.json").read_text(encoding="utf-8"))
    malo = api.nube("rotacion_malo")
    assert set(malo) == set(ejemplo) - {"_aviso"} and malo["caso"] == "rotacion_malo" and malo["ejes"] == ejemplo["ejes"]
    assert malo["archivo"]["dentro"] is False and malo["archivo"]["x"] == 1.0 and malo["detectores"]["ejes_con_nombre"]["dentro"] is False
    assert "fecha_salida" in malo["detectores"]["ejes_con_nombre"]["motivo"]
    assert malo["n_simulaciones"] == 1000 and len(malo["puntos"]) == 1000 and all(0.5 <= x <= 1 and 0 <= y <= 1 for x, y in malo["puntos"])
    corregido = api.nube("rotacion_malo", [QUITAR])
    assert corregido["detectores"]["ejes_con_nombre"]["dentro"] is True and corregido["archivo"]["x"] < 0.8
    assert corregido["archivo"] == api.nube("rotacion")["archivo"]
    # La nube se generó con este codificador: el segundo detector corre y da una distancia.
    assert corregido["detectores"]["resumenes_aprendidos"]["distancia"] > 0
    json.dumps(malo)


def test_con_otra_red_el_segundo_detector_se_apaga(artefactos, con, tmp_path):
    """`nube.npz` guarda la huella del codificador con que se calculó. Sin codificador, o con otro, solo corren los ejes con nombre."""
    import shutil
    copia = tmp_path / "artefactos"
    shutil.copytree(artefactos, copia)
    con("red")
    casos.ARTEFACTOS = copia                                                                  # `con` ya lo dejó bajo monkeypatch
    (copia / "supervivencia" / "codificador.onnx").unlink()
    generar_nube.generar(copia / "supervivencia", simulaciones=100)                           # nube solo con los ejes
    sin_red = api.nube("rotacion_malo")
    assert sin_red["detectores"]["resumenes_aprendidos"] == {"dentro": True, "distancia": None, "limite": None}
    assert sin_red["archivo"]["dentro"] is False and api.nube("rotacion_malo", [QUITAR])["archivo"]["dentro"] is True
    assert api.analizar("rotacion_malo")["semaforo"]["estado"] == "rojo_modelo"              # el rojo no necesita la red
    shutil.copy(artefactos / "supervivencia" / "codificador.onnx", copia / "supervivencia" / "codificador.onnx")
    assert api.nube("rotacion")["detectores"]["resumenes_aprendidos"]["distancia"] is None    # la nube no es de esta red
    json.dumps(sin_red)


def test_cartera_en_lote(con):
    con("red")
    caso = {**casos.cargar_caso("rotacion"), "cartera": {"modo": "simulada", "n": 60}}
    r = sv.cartera(caso)
    ejemplo = json.loads((EJEMPLOS / "cartera.json").read_text(encoding="utf-8"))
    assert set(r) == {k for k in ejemplo if not k.startswith("_")} and set(r["filas"][0]) == set(ejemplo["filas"][0])
    assert r["n_analisis"] == 60 and len(r["filas"]) == 60 and r["precalculado"] is False and r["sintetico"] is True
    costos = [f["costo_de_no_saber"] for f in r["filas"]]
    assert costos == sorted(costos, reverse=True) and min(costos) >= 0
    assert all(40 <= f["n_unidades"] <= 400 for f in r["filas"])                              # el 20% de 200 a 2.000 personas
    assert len({f["cliente"] for f in r["filas"]}) == 60
    json.dumps(r)
    assert sv.cartera(caso)["filas"] == r["filas"]                                            # semilla fija


def test_cartera_precalculada_con_mcmc(artefactos, con, tmp_path, monkeypatch):
    """Sin `cartera.json` no hay cartera en `mcmc`; con el archivo que deja `cartera_mcmc` (aquí, una empresa y un puñado de pasos), sale rotulada."""
    from motor.supervivencia import cartera_mcmc
    con("mcmc")
    with pytest.raises(casos.ErrorKrylov):
        sv.cartera(casos.cargar_caso("rotacion"))
    monkeypatch.setattr(casos, "ARTEFACTOS", tmp_path)
    escrita = cartera_mcmc.precalcular(1, tmp_path / "supervivencia", calentamiento=20, muestras=20, cadenas=1, profundidad=4)
    r = api.cartera("rotacion")
    ejemplo = json.loads((EJEMPLOS / "cartera.json").read_text(encoding="utf-8"))
    assert set(r) == {k for k in ejemplo if not k.startswith("_")} and set(r["filas"][0]) == set(ejemplo["filas"][0])
    assert r["precalculado"] is True and r["n_analisis"] == 1 and r["filas"] == escrita["filas"] and r["tiempo_ms"] > 0
    # Es una de las empresas de la cartera con la red: mismo nombre y mismas personas por decidir.
    lotes = list(sv.empresas_de_la_cartera(1000))
    assert r["filas"][0]["cliente"].startswith("Empresa ") and r["filas"][0]["n_unidades"] == round(0.2 * min(l["tiempo"].shape[1] for l in lotes))


def test_el_servicio_no_importa_torch():
    assert comun.tamanos_de_lote(1000) == [50] * 20
    codigo = ("import sys, nucleo.api, nucleo.supervivencia, nucleo.cartera, motor.supervivencia.simular, motor.supervivencia.nube; "
              "print(sorted(m for m in ('torch', 'zuko', 'jax', 'numpyro') if m in sys.modules))")
    assert subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=Path(__file__).resolve().parents[2]).stdout.strip() == "[]"
