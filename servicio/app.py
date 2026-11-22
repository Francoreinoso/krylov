"""API HTTP de Krylov (CONTRATO.md, sección 6).

Correr: uv run uvicorn servicio.app:app --reload

El servidor gratuito tiene 512 MB y cada análisis pide memoria para sus muestras: los análisis van de a uno
(`_de_a_uno`), y los que llegan mientras tanto esperan su turno en vez de sumarse. Lo que no calcula (la salud,
los papeles, los textos) no espera.
"""

import json
import threading

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from nucleo import api as nucleo
from servicio import fijos, respuestas
from servicio.calce import calce_del_demo, proponer_calce
from servicio.interpretar import interpretar as interpretar_respuesta

MAX_BYTES = 5 * 1024 * 1024
_UN_ANALISIS = threading.Lock()


def _de_a_uno(funcion, *args):
    """Corre un análisis cuando termina el anterior: con varias pestañas a la vez, la memoria no se suma."""
    with _UN_ANALISIS:
        return funcion(*args)

app = FastAPI(title="Krylov")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PedidoAnalizar(BaseModel):
    caso: str
    transformaciones: list[str] = []
    costos: dict | None = None
    mediciones: list[dict] = []


class PedidoDondeMedir(BaseModel):
    caso: str
    mediciones: list[dict] = []


class PedidoNube(BaseModel):
    caso: str
    transformaciones: list[str] = []


@app.exception_handler(fijos.PeticionInvalida)
def peticion_invalida(_: Request, e: fijos.PeticionInvalida):
    return JSONResponse(status_code=400, content={"error": e.error, "codigo": e.codigo})


@app.exception_handler(RequestValidationError)
def peticion_incompleta(_: Request, e: RequestValidationError):
    """Un campo que falta o no tiene la forma pedida: la misma forma de error del contrato, no la de FastAPI."""
    campos = sorted({str(error["loc"][-1]) for error in e.errors() if error.get("loc")})
    que = f": revisa «{'», «'.join(campos)}»" if campos else ""
    return JSONResponse(status_code=400, content={"error": f"A la petición le falta un campo o trae uno con otra forma{que}.",
                                                  "codigo": "peticion_invalida"})


@app.exception_handler(Exception)
def error_inesperado(_: Request, e: Exception):
    """Lo que no se previó: una frase y un código, nunca una traza (CONTRATO.md, sección 6)."""
    return JSONResponse(status_code=500, content={"error": "Algo falló de nuestro lado al responder. Prueba de nuevo en un rato.",
                                                  "codigo": "error_interno"})


@app.get("/api/salud")
def salud():
    return {"ok": True}


@app.get("/api/casos")
def casos():
    return _de_a_uno(respuestas.inicio)              # la primera vez analiza cada tarjeta; después sale de la memoria


@app.post("/api/analizar")
def analizar(p: PedidoAnalizar):
    return _de_a_uno(respuestas.analizar, p.caso, p.transformaciones, p.costos, p.mediciones)


@app.post("/api/donde-medir")
def donde_medir(p: PedidoDondeMedir):
    return _de_a_uno(respuestas.donde_medir, p.caso, p.mediciones)


@app.post("/api/nube")
def nube(p: PedidoNube):
    return _de_a_uno(respuestas.nube, p.caso, p.transformaciones)


@app.get("/api/papeles/{motor_id}")
def papeles(motor_id: str):
    respuesta = nucleo.papeles(motor_id)
    if "error" in respuesta:
        return JSONResponse(status_code=400, content=respuesta)
    return respuesta


@app.get("/api/calce/{caso}")
def calce(caso: str):
    """El calce de un archivo del demo, elegido por el equipo (el de un archivo propio llega con POST)."""
    fijos.casos_del_demo_o_error(caso)
    return calce_del_demo(caso)


@app.get("/api/sello")
def sello(motor: str):
    return respuestas.sello(motor)


@app.get("/api/textos")
def textos():
    return respuestas.textos()


async def _leer_archivo(archivo: UploadFile) -> bytes:
    contenido = await archivo.read(MAX_BYTES + 1)
    if len(contenido) > MAX_BYTES:
        raise fijos.PeticionInvalida("El archivo pesa más de 5 MB, el máximo que recibe Krylov. Sube una parte: menos filas "
                                     "(por ejemplo, el último período) o solo las columnas que usa el modelo.", "archivo_grande")
    return contenido


def _json_de_formulario(texto: str | None, campo: str) -> dict | None:
    if not texto:
        return None
    try:
        valor = json.loads(texto)
    except json.JSONDecodeError:
        raise fijos.PeticionInvalida(f"«{campo}» no es un JSON válido.", "peticion_invalida") from None
    if not isinstance(valor, dict):
        raise fijos.PeticionInvalida(f"«{campo}» tiene que ser un objeto.", "peticion_invalida")
    return valor


@app.post("/api/calce")
async def calce_propio(archivo: UploadFile = File(...), motor_id: str = Form(...), caso: str | None = Form(None)):
    """El calce de un archivo subido: lo propone el modelo de lenguaje con un resumen de columnas, o la regla por tipo.
    Va en otro hilo: la llamada al modelo de lenguaje tarda segundos y no puede detener al servidor."""
    return await run_in_threadpool(proponer_calce, motor_id, await _leer_archivo(archivo), caso)


@app.post("/api/analizar_archivo")
async def analizar_archivo(archivo: UploadFile = File(...), motor_id: str = Form(...),
                           columnas: str = Form(...), costos: str | None = Form(None)):
    """Un archivo subido, con el calce que confirmó el usuario: responde la red del motor, con la forma de `analizar`."""
    contenido = await _leer_archivo(archivo)
    respuesta = await run_in_threadpool(_de_a_uno, nucleo.analizar_archivo, motor_id, contenido,
                                        _json_de_formulario(columnas, "columnas") or {}, _json_de_formulario(costos, "costos"))
    if "error" in respuesta:
        return JSONResponse(status_code=400, content=respuesta)
    return respuesta


@app.post("/api/interpretar")
def interpretar(respuesta: dict):
    """El texto corto que acompaña a una respuesta; sus números salen del JSON o se usa la plantilla."""
    return interpretar_respuesta(respuesta)
