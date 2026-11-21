"""API HTTP de Krylov (CONTRATO.md, sección 6).

Correr: uv run uvicorn servicio.app:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from servicio import fijos

app = FastAPI(title="Krylov")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PedidoAnalizar(BaseModel):
    caso: str
    transformaciones: list[str] = []
    costos: dict | None = None
    mediciones: list[dict] = []


class PedidoCaso(BaseModel):
    caso: str


class PedidoDondeMedir(BaseModel):
    caso: str
    mediciones: list[dict] = []


class PedidoNube(BaseModel):
    caso: str
    transformaciones: list[str] = []


@app.exception_handler(fijos.PeticionInvalida)
def peticion_invalida(_: Request, e: fijos.PeticionInvalida):
    return JSONResponse(status_code=400, content={"error": e.error, "codigo": e.codigo})


@app.get("/api/salud")
def salud():
    return {"ok": True}


@app.get("/api/casos")
def casos():
    return fijos.casos()


@app.post("/api/analizar")
def analizar(p: PedidoAnalizar):
    return fijos.analizar(p.caso, p.transformaciones, p.mediciones)


@app.post("/api/cartera")
def cartera(p: PedidoCaso):
    return fijos.cartera(p.caso)


@app.post("/api/donde-medir")
def donde_medir(p: PedidoDondeMedir):
    return fijos.donde_medir(p.caso, p.mediciones)


@app.post("/api/nube")
def nube(p: PedidoNube):
    return fijos.nube(p.caso, p.transformaciones)


@app.get("/api/sello")
def sello(motor: str):
    return fijos.sello(motor)
