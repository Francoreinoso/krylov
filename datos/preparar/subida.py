"""Archivos de prueba para subir en el chat (S-24): datos/demo/subida_<caso>.csv y su _verdad.csv.

Qué son, dicho como es: SIMULADOS con la misma física que el archivo del demo de cada caso (se usa
el mismo generador de esta carpeta, `datos/preparar/<caso>.py`), pero con otra semilla, otro tamaño
y otros nombres de columnas y unidades, como los traería el archivo de otra faena. No son de
ninguna faena real. Sirven para mostrar que la misma red responde un archivo que no es el del demo,
y para que asignar cada columna a su papel en el chat tenga sentido.

Cada archivo queda dentro de los tamaños que su motor conoce (`contratos/CONTRATO.md`, tabla
«Rangos que el motor conoce»; D-38).

| Archivo | Tamaño | Qué cambia respecto del demo | Calce esperado |
|---|---|---|---|
| subida_leyes.csv | cerca de 250 pozos | malla 14 × 16 m, otra dirección de continuidad, columnas en otro orden y una que el modelo no usa (`turno`) | x = `este_m`, y = `norte_m`, valor = `arsenico_ppm` |
| subida_taludes.csv | 20 sectores, 36 horas | el tiempo viene en minutos | unidad = `prisma`, tiempo = `minutos` dividido por 60, valor = `desplazamiento_mm` |
| subida_flotacion.csv | 5 líneas de 10 celdas | la recuperación viene en porcentaje | unidad = `linea`, tiempo = `minuto`, valor = `recuperacion_pct` dividido por 100 |
| subida_flota.csv | 24 camiones | el indicador viene como hierro en el aceite, en ppm (120 ppm = falla; lo que el error de medición dejaría bajo cero se informa como 0) | unidad = `camion`, tiempo = `horas_operacion`, valor = `hierro_ppm` dividido por 120 |
| subida_sismicidad.csv | 5 sectores, 8 horas | otros nombres de columnas | unidad = `sector`, tiempo = `hora`, valor = `magnitud` |

Uso, desde la raíz del repositorio:
    uv run python datos/preparar/subida.py
"""

from __future__ import annotations

import csv
import importlib.util
import tempfile
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SEMILLA = 2027
HIERRO_FALLA_PPM = 120.0

# Por caso: constantes del generador que cambian, nombres nuevos de las columnas (en el orden en
# que quedan) y el factor por el que se multiplica cada columna numérica.
CASOS = {
    "leyes": dict(
        cambios=dict(BURDEN_M=14.0, ESPACIAMIENTO_M=16.0, AZIMUT=np.deg2rad(120.0), MEDIANA_AS_PPM=280.0),
        columnas={"pozo": "id_pozo", "y": "norte_m", "x": "este_m", "cu_pct": "cobre_pct", "as_ppm": "arsenico_ppm"},
        factores={},
    ),
    "taludes": dict(
        cambios=dict(SECTORES=20, VENTANA_H=36.0),
        columnas={"unidad": "prisma", "tiempo": "minutos", "valor": "desplazamiento_mm"},
        factores={"tiempo": (60.0, "{:.0f}")},
    ),
    "flotacion": dict(
        cambios=dict(LINEAS=5, CELDAS=10, MIN_POR_CELDA=3.0),
        columnas={"unidad": "linea", "tiempo": "minuto", "valor": "recuperacion_pct"},
        factores={"valor": (100.0, "{:.1f}")},
    ),
    "flota": dict(
        cambios=dict(CAMIONES=24),
        columnas={"unidad": "camion", "tiempo": "horas_operacion", "valor": "hierro_ppm",
                  "exigencia": "exigencia_ruta", "horas_a_mantencion": "horas_a_mantencion"},
        factores={"valor": (HIERRO_FALLA_PPM, "{:.1f}")},
    ),
    "sismicidad": dict(
        cambios=dict(SECTORES=5, VENTANA_H=8.0),
        columnas={"unidad": "sector", "tiempo": "hora", "valor": "magnitud"},
        factores={},
    ),
}


def _generar(caso: str, cambios: dict, carpeta: Path) -> None:
    """Corre el generador del caso con otra semilla y otro tamaño, escribiendo en una carpeta temporal."""
    spec = importlib.util.spec_from_file_location(f"preparar_{caso}", AQUI / f"{caso}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    modulo.RAIZ = carpeta
    modulo.SEMILLA = SEMILLA
    for nombre, valor in cambios.items():
        assert hasattr(modulo, nombre), f"{caso}.py ya no tiene {nombre}"
        setattr(modulo, nombre, valor)
    modulo.main()


def main() -> None:
    demo = RAIZ / "datos" / "demo"
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        (carpeta / "datos" / "demo").mkdir(parents=True)
        for caso, c in CASOS.items():
            _generar(caso, c["cambios"], carpeta)
            with open(carpeta / "datos" / "demo" / f"{caso}.csv", newline="", encoding="utf-8") as f:
                filas = list(csv.DictReader(f))
            turnos = np.random.default_rng(SEMILLA).choice(["A", "B"], size=len(filas))
            with open(demo / f"subida_{caso}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(list(c["columnas"].values()) + (["turno"] if caso == "leyes" else []))
                for i, fila in enumerate(filas):
                    salida = []
                    for vieja in c["columnas"]:
                        v = fila[vieja]
                        if vieja in c["factores"]:
                            factor, formato = c["factores"][vieja]
                            v = float(v) * factor
                            if caso == "flota":
                                v = max(v, 0.0)          # un laboratorio no informa hierro negativo
                            v = formato.format(v)
                        salida.append(v)
                    w.writerow(salida + ([turnos[i]] if caso == "leyes" else []))
            verdad = (carpeta / "datos" / "demo" / f"{caso}_verdad.csv").read_text(encoding="utf-8")
            (demo / f"subida_{caso}_verdad.csv").write_text(verdad, encoding="utf-8")
            print(f"datos/demo/subida_{caso}.csv: {len(filas)} filas")


if __name__ == "__main__":
    main()
