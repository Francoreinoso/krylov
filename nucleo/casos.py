"""Los casos de uso (`casos/<nombre>.yaml`) y lo que todos los motores comparten al responder.

Un caso es una pregunta de negocio resuelta con un motor, un archivo de datos y sus
costos (`contratos/CONTRATO.md`, sección 4). Ningún texto de industria va en el código:
sale de estos archivos.
"""

from __future__ import annotations

import csv
import os
from functools import cache
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_CASOS = RAIZ / "casos"
# Los artefactos de cada motor. La variable sirve para probar con una exportación que no es la versionada.
ARTEFACTOS = Path(os.environ.get("KRYLOV_ARTEFACTOS", RAIZ / "motor" / "artefactos"))
# Los cinco de la minería (D-37) y, hasta que se retiren (A-32), los tres anteriores al pivote.
MOTORES = ("espacial", "deformacion", "cinetica", "desgaste", "sismico", "supervivencia", "jerarquico", "estados")


class ErrorKrylov(Exception):
    """Error con una frase en español para la pantalla y un código para el programa."""

    def __init__(self, error: str, codigo: str):
        super().__init__(error)
        self.error, self.codigo = error, codigo

    def a_dict(self) -> dict:
        return {"error": self.error, "codigo": self.codigo}


@cache
def cargar_caso(nombre: str) -> dict:
    ruta = CARPETA_CASOS / f"{nombre}.yaml"
    if not nombre.replace("_", "").isalnum() or not ruta.exists():
        raise ErrorKrylov(f"No conozco el caso «{nombre}».", "caso_desconocido")
    caso = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    if caso.get("motor") not in MOTORES:
        raise ErrorKrylov(f"El caso «{nombre}» no dice con qué motor se responde.", "caso_invalido")
    return caso


def nombres_del_inicio() -> list[str]:
    """Los casos de `casos/INICIO`, en orden: las tarjetas de la primera vista."""
    lineas = (CARPETA_CASOS / "INICIO").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lineas if l.strip() and not l.lstrip().startswith("#")]


def implementacion(motor_id: str) -> str:
    """`red` o `mcmc`, según `KRYLOV_MOTOR_<ID>`. Por defecto `mcmc`: la red se activa al pasar `validar-motor`."""
    valor = os.environ.get(f"KRYLOV_MOTOR_{motor_id.upper()}", "mcmc").strip().lower()
    return valor if valor in ("red", "mcmc") else "mcmc"


def costos_numericos(caso: dict, costos: dict | None) -> dict[str, float]:
    """Los costos del caso con lo que haya movido el usuario encima: {falso_si, falso_no, medicion?}.

    `costos` acepta números sueltos ({"falso_si": 1200}) o el bloque del contrato ({"falso_si": {"valor": 1200}}).
    """
    resultado = {}
    for clave, bloque in caso["costos"].items():
        valor = (costos or {}).get(clave, bloque["valor"])
        if isinstance(valor, dict):
            valor = valor.get("valor", bloque["valor"])
        if valor is None:
            raise ErrorKrylov(f"Al caso «{caso['nombre']}» le falta el costo «{clave}».", "caso_sin_costos")
        resultado[clave] = float(valor)
    if resultado.get("falso_si", 0) <= 0 or resultado.get("falso_no", 0) <= 0:
        raise ErrorKrylov("Los dos costos tienen que ser mayores que cero.", "costos_invalidos")
    return resultado


def bloque_costos(caso: dict, numeros: dict[str, float]) -> dict:
    """Los costos con la forma que pinta la web: valor, extremos del deslizador y etiqueta."""
    salida = {}
    for clave, bloque in caso["costos"].items():
        salida[clave] = {k: bloque[k] for k in ("min", "max", "etiqueta") if k in bloque}
        valor = numeros[clave]
        salida[clave] = {"valor": int(valor) if valor == int(valor) else valor, **salida[clave]}
    return salida


def leer_columnas(ruta: str | Path) -> dict[str, list[str]]:
    """Un CSV como columnas de texto, por nombre de encabezado. Las rutas relativas parten de la raíz del repositorio."""
    ruta = Path(ruta) if Path(ruta).is_absolute() else RAIZ / ruta
    if not ruta.exists():
        raise ErrorKrylov(f"No encuentro el archivo de datos «{ruta.name}».", "sin_datos")
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    return {nombre: [fila[nombre] for fila in filas] for nombre in (filas[0] if filas else {})}


def tabla_del_caso(caso: dict) -> dict[str, list[str]]:
    """Las columnas de datos de un caso, como texto: la tabla subida por el usuario (D-34) o el archivo `dataset` del YAML.

    `api.analizar_archivo` arma un caso en memoria con `caso["tabla"]` (columna → lista de textos) y `caso["columnas"]`
    (papel → nombre de columna). Los motores leen siempre por aquí y no saben de dónde vino la tabla.
    """
    return caso["tabla"] if caso.get("tabla") is not None else leer_columnas(caso["dataset"])


class ArchivoNoCalza(Exception):
    """El archivo no tiene lo que el modelo del motor necesita. `estado` es `rojo_datos` (falta algo o no se puede leer)
    o `rojo_modelo` (se lee, pero no es de la familia de archivos con que practicó la red). El motor lo convierte en semáforo."""

    def __init__(self, motivo: str, estado: str = "rojo_datos"):
        super().__init__(motivo)
        self.motivo, self.estado = motivo, estado
