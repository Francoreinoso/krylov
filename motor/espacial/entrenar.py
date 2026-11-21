"""Entrena la red del motor `espacial` con terrenos simulados al vuelo.

    caffeinate -dims uv run python -m motor.espacial.entrenar --dispositivo mps --hasta 08:30 --guardar-cada-min 10

Pérdida = pérdida de la cabeza de mapa + pérdida NPE de la cabeza de flujo. La segunda
no toca el codificador (gradiente cortado en `red.py`), así que sumarlas no cambia cómo
entrena la cabeza de mapa.

**Solo la cabeza de flujo** (WORKPLAN.md, 11.5: «si hace falta, se entrena aparte de día sobre el
codificador congelado»). Toma el codificador y la cabeza de mapa de un punto de guardado, los
congela, y entrena un resumidor nuevo, con el atajo de estadísticos clásicos, y un flujo nuevo:

    caffeinate -dims uv run python -m motor.espacial.entrenar --solo-flujo --dispositivo mps --minutos 45

Deja sus puntos de guardado en `motor/checkpoints/espacial_flujo/` (red completa: sirve tal cual para
`sello.py --punto` y `exportar.py --punto`). El mapa que entrega es idéntico al del punto de origen.

Se retoma solo: si existe `motor/checkpoints/espacial/ultimo.pt`, sigue desde ahí con el
mismo comando. `--nuevo` lo ignora y parte de cero.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from motor.comun.entrenar import elegir_dispositivo, entrenar
from motor.espacial.exportar import configuracion, red_desde_config
from motor.espacial.red import ANCHOS, RedEspacial
from motor.espacial.simular import Prior, simular

CARPETA = Path("motor/checkpoints/espacial")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--minutos", type=float, default=None, help="presupuesto en minutos")
    p.add_argument("--hasta", type=str, default=None, help="entrenar hasta esta hora, HH:MM")
    p.add_argument("--dispositivo", default="auto", choices=("auto", "cpu", "mps"))
    p.add_argument("--lote", type=int, default=64)
    p.add_argument("--canales", type=int, default=3, choices=(2, 3), help="2 = salvavidas sin canal de tendencia")
    p.add_argument("--guardar-cada-min", type=float, default=10.0)
    p.add_argument("--tasa", type=float, default=5e-4)
    p.add_argument("--carpeta", type=Path, default=CARPETA)
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--nuevo", action="store_true", help="ignora el punto de guardado y parte de cero")
    p.add_argument("--solo-flujo", action="store_true", help="entrena solo la cabeza de flujo, con atajo, sobre el codificador congelado")
    p.add_argument("--desde", type=Path, default=CARPETA / "ultimo.pt", help="con --solo-flujo: de dónde salen el codificador y la cabeza de mapa")
    a = p.parse_args()
    if a.solo_flujo and a.carpeta == CARPETA:
        a.carpeta = CARPETA.parent / "espacial_flujo"

    dispositivo = elegir_dispositivo(a.dispositivo)
    prior = Prior()
    retomar = not a.nuevo and (a.carpeta / "ultimo.pt").exists()
    pasos_previos = 0
    if retomar:   # la arquitectura la manda el punto de guardado, no la línea de comandos
        previo = torch.load(a.carpeta / "ultimo.pt", map_location="cpu", weights_only=False)
        red, pasos_previos = red_desde_config(previo["config"]), previo["pasos"]
        a.canales = red.canales_entrada
    elif a.solo_flujo:
        origen = torch.load(a.desde, map_location="cpu", weights_only=False)
        a.canales = origen["config"]["canales_entrada"]
        torch.manual_seed(a.semilla)
        red = RedEspacial(a.canales, tuple(origen["config"].get("anchos", ANCHOS)), atajo_flujo=True)
        red.cargar_mapa_de(origen["modulo"])
    else:
        torch.manual_seed(a.semilla)
        red = RedEspacial(a.canales)
    if a.solo_flujo and retomar:
        for parte in (red.mapa.codificador, red.mapa.cabeza_mapa):
            for parametro in parte.parameters():
                parametro.requires_grad_(False)

    # Al retomar cambia la semilla: los terrenos que vienen no repiten los de la corrida anterior.
    torch.manual_seed(a.semilla + pasos_previos)
    gen = torch.Generator().manual_seed(a.semilla + pasos_previos)
    if not retomar:
        # Estandarización de θ' para el flujo: media y desviación bajo el prior, con 8.192 terrenos simulados.
        red.flujo.fijar_escala(simular(8192, prior, gen, con_tendencia=a.canales == 3)["theta"])
    red.to(dispositivo)

    def perdida_de_lote():
        lote = simular(a.lote, prior, gen, dispositivo, con_tendencia=a.canales == 3)
        if a.solo_flujo:
            perdida = red.perdida_solo_flujo(lote)
            return perdida, {"flujo": float(perdida.detach())}
        partes = red.perdidas(lote)
        return partes["mapa"] + partes["flujo"], {k: float(v.detach()) for k, v in partes.items()}

    config = configuracion(a.canales, prior, {"anchos": list(red.anchos), "atajo_flujo": red.atajo_flujo, "solo_flujo": a.solo_flujo, "lote": a.lote, "dispositivo": str(dispositivo), "tasa": a.tasa, "semilla": a.semilla})
    print(f"[espacial] dispositivo={dispositivo} lote={a.lote} canales={a.canales} retomar={retomar} carpeta={a.carpeta}", flush=True)
    entrenar(red, perdida_de_lote, datasets_por_paso=a.lote, carpeta=a.carpeta, minutos=a.minutos, hasta=a.hasta,
             guardar_cada_min=a.guardar_cada_min, tasa=a.tasa, retomar=retomar, config=config)


if __name__ == "__main__":
    main()
