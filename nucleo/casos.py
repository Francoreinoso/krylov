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
MOTORES = ("supervivencia", "jerarquico", "estados", "espacial")
MONEDAS = {"USD": "dólares", "CLP": "pesos"}


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


def en_plata(valor: float, moneda: str) -> str:
    """Un monto dicho en palabras, redondeado: «18 mil dólares», «2,7 millones de dólares»."""
    nombre = MONEDAS.get(moneda, moneda)
    if valor >= 1e6:
        return f"{valor / 1e6:.1f}".replace(".", ",") + f" millones de {nombre}"
    if valor >= 1e3:
        return f"{round(valor / 1e3)} mil {nombre}"
    return f"{round(valor)} {nombre}"


def leer_columnas(ruta: str | Path) -> dict[str, list[str]]:
    """Un CSV como columnas de texto, por nombre de encabezado. Las rutas relativas parten de la raíz del repositorio."""
    ruta = Path(ruta) if Path(ruta).is_absolute() else RAIZ / ruta
    if not ruta.exists():
        raise ErrorKrylov(f"No encuentro el archivo de datos «{ruta.name}».", "sin_datos")
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    return {nombre: [fila[nombre] for fila in filas] for nombre in (filas[0] if filas else {})}
