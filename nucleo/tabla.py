"""Lo común a los tres motores de tabla al armar la respuesta de `analizar`: unidades, examen y lectura de la verdad.

Cada motor entrega `muestras_p`: por unidad por decidir, una probabilidad por cada muestra
del posterior de θ, ya pasada por su paso local exacto. De ahí en adelante todo es igual.
"""

from __future__ import annotations

import numpy as np

from nucleo import decision
from nucleo.casos import ArchivoNoCalza, leer_columnas

MUESTRAS = 32
TRAMOS = ((0.0, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 1.01))
_SI_NO = {"yes": 1.0, "si": 1.0, "sí": 1.0, "1": 1.0, "1.0": 1.0, "true": 1.0, "no": 0.0, "0": 0.0, "0.0": 0.0, "false": 0.0}


def si_no(texto: str) -> float:
    """Una respuesta sí/no escrita como en los archivos de los casos (Yes/No, 1/0) a 1.0 o 0.0; vacío es NaN."""
    texto = texto.strip().lower()
    return _SI_NO[texto] if texto else float("nan")


def unidades(ids: list[str], muestras_p: np.ndarray, costos: dict) -> list[dict]:
    """La lista `unidades` del contrato, ordenada de mayor a menor duda. muestras_p: (unidades, muestras)."""
    d = decision.decidir_tabla(muestras_p, costos["falso_si"], costos["falso_no"])
    bajo, alto = np.quantile(muestras_p, [0.05, 0.95], axis=1)
    filas = [{"id": str(ids[i]), "etiqueta": str(ids[i]), "p": round(float(d["p"][i]), 3),
              "rango_bajo": round(float(bajo[i]), 3), "rango_alto": round(float(alto[i]), 3),
              "muestras_p": [round(float(v), 2) for v in muestras_p[i]], "estado": str(d["estado"][i]), "duda": round(float(d["duda"][i]), 2)}
             for i in range(len(ids))]
    return sorted(filas, key=lambda u: -u["duda"])


def examen(caso: dict, ids: list[str], p: np.ndarray) -> dict | None:
    """Examen con datos reales reservados: lo que Krylov dijo de cada unidad por decidir contra lo que pasó.

    Lee `caso["verdad"]` (columnas `id`, `objetivo`). Devuelve tramos de probabilidad con lo dicho (promedio de p)
    y lo que pasó (frecuencia real). La frase la escribe el servicio con estos números. None si el caso no trae verdad.
    """
    if not caso.get("verdad"):
        return None
    tabla = leer_columnas(caso["verdad"])
    verdad = {i: si_no(v) for i, v in zip(tabla["id"], tabla["objetivo"]) if v.strip()}
    pares = np.array([(p[j], verdad[str(i)]) for j, i in enumerate(ids) if str(i) in verdad])
    if len(pares) == 0:
        return None
    tramos = []
    for bajo, alto in TRAMOS:
        en = (pares[:, 0] >= bajo) & (pares[:, 0] < alto)
        if en.sum() >= 10:
            tramos.append({"dijimos": round(float(pares[en, 0].mean()), 3), "paso": round(float(pares[en, 1].mean()), 3), "n": int(en.sum())})
    return {"tipo": "datos_reales_reservados", "n": int(len(pares)), "frase": "", "tramos": tramos}


def rojo_datos(caso: dict, motivo: str, **numeros) -> dict:
    """La respuesta propia de un motor cuando faltan datos: `motivo` es `pocas_filas` o `casi_ningun_si` (casos/textos.yaml)."""
    from nucleo import textos
    texto = textos.frase(f"semaforo.rojo_datos.{motivo}", unidad_plural=caso["unidad"]["plural"], **numeros) or ""
    return {"unidades": None, "factores": None, "semaforo": {"estado": "rojo_datos", "motivo": texto, "propuesta": None}}


# ------------------------------------------------------------------------------ leer una tabla que puede no calzar (D-34)

def nombres_del_papel(col: dict, papel: str, cantidad: int) -> list[str]:
    """Los nombres de columna asignados a un papel, exigiendo la cantidad que la red del motor recibe."""
    valor = col.get(papel)
    nombres = [] if valor is None else list(valor) if isinstance(valor, (list, tuple)) else [valor]
    if len(nombres) != cantidad:
        cuantas = "una columna" if cantidad == 1 else f"{cantidad} columnas"
        raise ArchivoNoCalza(f"El papel «{papel}» necesita {cuantas} y tiene {len(nombres)}: asígnale {cuantas} al confirmar las columnas.")
    return nombres


def columna(tabla: dict, nombre: str) -> list[str]:
    if nombre not in tabla:
        raise ArchivoNoCalza(f"El archivo no trae la columna «{nombre}»: elige una de las columnas que sí trae.")
    return tabla[nombre]


def no_es_numero(nombre: str, valores: list[str]) -> str | None:
    """La frase que dice cuál es la primera celda de la columna que no es un número (o está vacía); None si todas lo son."""
    for n, v in enumerate(valores, start=1):
        try:
            if np.isfinite(float(v)):
                continue
        except ValueError:
            pass
        dice = f"dice «{v.strip()}»" if v.strip() else "está vacía"
        return f"La columna «{nombre}» tiene que traer solo números, y en la fila {n} de datos {dice}: corrige ese valor o borra la fila."
    return None


def numeros(tabla: dict, nombre: str, minimo: float | None = None, maximo: float | None = None, enteros: bool = False) -> np.ndarray:
    """Una columna como números, sin vacíos. Si no se puede leer: `rojo_datos`; si se sale del rango que el modelo conoce: `rojo_modelo`."""
    texto = columna(tabla, nombre)
    motivo = no_es_numero(nombre, texto)
    if motivo:
        raise ArchivoNoCalza(motivo)
    valores = np.array([float(v) for v in texto])
    fuera = (valores < minimo if minimo is not None else False) | (valores > maximo if maximo is not None else False)
    if np.any(fuera) or (enteros and np.any(valores != np.round(valores))):
        rango = f"entre {minimo:g} y {maximo:g}" if minimo is not None and maximo is not None else f"desde {minimo:g}" if minimo is not None else f"hasta {maximo:g}"
        raise ArchivoNoCalza(f"La columna «{nombre}» tiene valores que el modelo no conoce: espera {'enteros ' if enteros else ''}{rango}.", "rojo_modelo")
    return valores


def respuesta_si_no(tabla: dict, nombre: str) -> np.ndarray:
    """La columna de respuesta: 1, 0 o NaN (vacío = por decidir). Acepta Yes/No, sí/no, 1/0."""
    try:
        return np.array([si_no(v) for v in columna(tabla, nombre)])
    except KeyError:
        raise ArchivoNoCalza(f"La columna «{nombre}» tiene que ser sí o no (o 1 y 0), y vacía donde hay que decidir.") from None


def rojo(caso: dict, error: ArchivoNoCalza) -> dict:
    """La respuesta propia de un motor cuando el archivo no calza con su modelo: semáforo rojo con el motivo."""
    return {"unidades": None, "factores": None, "semaforo": {"estado": error.estado, "motivo": error.motivo, "propuesta": None}}
