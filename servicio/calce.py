"""El calce de columnas de los archivos del demo (CONTRATO.md, secciones 5 y 6; D-35).

En los cuatro casos del demo el calce lo eligió el equipo y está escrito en `casos/<nombre>.yaml`.
Se entrega con la misma forma que `POST /api/calce`, con `origen: "equipo"`, para que el chat
lo muestre igual que el de un archivo propio.
"""

import csv

from nucleo import api
from nucleo.casos import cargar_caso
from servicio.fijos import RAIZ


def _encabezado(caso: dict) -> list[str]:
    """Las columnas del CSV del caso; vacío si el archivo no está en este computador (inasistencias)."""
    ruta = RAIZ / caso.get("dataset", "")
    if not ruta.is_file():
        return []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f), [])


def calce_del_demo(nombre: str) -> dict:
    caso = cargar_caso(nombre)
    elegidas = caso["columnas"]
    papeles = api.papeles(caso["motor"])
    calce = {}
    for p in papeles["papeles"]:
        valor = elegidas.get(p["papel"])
        columnas = [valor] if isinstance(valor, str) else list(valor or [])
        transformacion = None
        if caso["motor"] == "espacial" and p["papel"] == "valor" and elegidas.get("transformacion"):
            transformacion = {"nombre": elegidas["transformacion"]}
        calce[p["papel"]] = {"columnas": columnas, "transformacion": transformacion,
                             "motivo": "Elegida por el equipo para este caso", "confianza": "alta"}
    usadas = {c for v in calce.values() for c in v["columnas"]}
    columnas = _encabezado(caso)
    return {"caso": nombre, "motor_id": caso["motor"], "calce": calce,
            "columnas": columnas, "no_usadas": [c for c in columnas if c not in usadas],
            "origen": "equipo", "precalculado": True}
