"""Bucle de entrenamiento común a los cuatro motores: NPE con datasets simulados al vuelo.

Cada paso pide un lote nuevo al simulador del motor (nada se guarda en disco), calcula
la pérdida y actualiza la red. El bucle se ocupa de lo que no depende del motor:

- **Puntos de guardado** cada `guardar_cada_min` minutos y al detenerse (Ctrl-C o `kill`),
  escritos de forma atómica en `carpeta/ultimo.pt`. Con `retomar=True` sigue desde ahí.
- **Conteo de datasets simulados**: la cifra «practicó con N millones» sale de aquí.
- Presupuesto por reloj (`minutos` o `hasta` una hora HH:MM), con tasa de aprendizaje
  en coseno sobre la fracción de tiempo transcurrida.
- Pasos con pérdida no finita se saltan y se cuentan; con 50 seguidos se detiene.

Uso desde un motor: ver `motor/espacial/entrenar.py`.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import signal
import time
from pathlib import Path
from typing import Callable

import torch
from torch import Tensor, nn

PerdidaDeLote = Callable[[], tuple[Tensor, dict[str, float]]]


def elegir_dispositivo(nombre: str) -> torch.device:
    """`cpu`, `mps` o `auto` (mps si existe). Se decide midiendo, motor por motor (`medir-rendimiento`)."""
    if nombre == "auto":
        nombre = "mps" if torch.backends.mps.is_available() else "cpu"
    return torch.device(nombre)


def segundos_hasta(hora: str) -> float:
    """Segundos desde ahora hasta la próxima vez que el reloj marque HH:MM."""
    ahora = dt.datetime.now()
    h, m = map(int, hora.split(":"))
    meta = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
    if meta <= ahora:
        meta += dt.timedelta(days=1)
    return (meta - ahora).total_seconds()


def guardar_punto(ruta: Path, estado: dict) -> None:
    """Escritura atómica: si el proceso muere a mitad, el punto de guardado anterior sigue entero."""
    temporal = ruta.with_suffix(".tmp")
    torch.save(estado, temporal)
    os.replace(temporal, ruta)


def cargar_punto(ruta: Path, modulo: nn.Module, optimizador: torch.optim.Optimizer | None = None) -> dict:
    estado = torch.load(ruta, map_location="cpu", weights_only=False)
    modulo.load_state_dict(estado["modulo"])
    if optimizador is not None and "optimizador" in estado:
        optimizador.load_state_dict(estado["optimizador"])
    return estado


def entrenar(
    modulo: nn.Module,
    perdida_de_lote: PerdidaDeLote,
    datasets_por_paso: int,
    carpeta: str | Path,
    *,
    minutos: float | None = None,
    hasta: str | None = None,
    guardar_cada_min: float = 10.0,
    tasa: float = 1e-3,
    tasa_final: float = 0.05,
    norma_maxima: float = 5.0,
    registrar_cada: int = 100,
    retomar: bool = True,
    config: dict | None = None,
) -> dict:
    """Entrena `modulo` hasta agotar el presupuesto de reloj. Devuelve el último estado guardado.

    perdida_de_lote: simula un lote nuevo y devuelve (pérdida, partes para el registro).
    datasets_por_paso: tamaño del lote, para el conteo de datasets simulados.
    """
    if (minutos is None) == (hasta is None):
        raise ValueError("Indica `minutos` o `hasta`, uno de los dos")
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta, bitacora = carpeta / "ultimo.pt", carpeta / "registro.jsonl"

    optimizador = torch.optim.AdamW(modulo.parameters(), lr=tasa, weight_decay=1e-5)
    progreso = {"pasos": 0, "datasets_simulados": 0, "segundos": 0.0, "pasos_saltados": 0}
    if retomar and ruta.exists():
        progreso.update({k: v for k, v in cargar_punto(ruta, modulo, optimizador).items() if k in progreso})
        print(f"[retomar] {ruta}: paso {progreso['pasos']}, {progreso['datasets_simulados']:,} datasets simulados", flush=True)

    presupuesto = minutos * 60 if minutos is not None else segundos_hasta(hasta)
    ya_entrenado = progreso["segundos"]            # lo de corridas anteriores cuenta para el coseno
    total = ya_entrenado + presupuesto

    def punto(motivo: str) -> dict:
        estado = {
            "modulo": modulo.state_dict(), "optimizador": optimizador.state_dict(), **progreso,
            "config": config or {}, "guardado": dt.datetime.now().isoformat(timespec="seconds"), "motivo": motivo,
        }
        guardar_punto(ruta, estado)
        print(f"[punto de guardado · {motivo}] paso {progreso['pasos']}, "
              f"{progreso['datasets_simulados']:,} datasets, {progreso['segundos'] / 60:.1f} min → {ruta}", flush=True)
        return estado

    detener = {"pedido": False}
    def _pedir_parada(*_):                           # deja terminar el paso en curso y guarda
        detener["pedido"] = True
    for senal in (signal.SIGINT, signal.SIGTERM):
        signal.signal(senal, _pedir_parada)

    modulo.train()
    inicio = ultimo_guardado = ultimo_registro = time.time()
    pasos_al_registrar, seguidos_malos, media_movil = progreso["pasos"], 0, None
    estado = None
    while not detener["pedido"]:
        transcurrido = time.time() - inicio
        if transcurrido >= presupuesto:
            break
        fraccion = (ya_entrenado + transcurrido) / total
        for grupo in optimizador.param_groups:
            grupo["lr"] = tasa * (tasa_final + (1 - tasa_final) * 0.5 * (1 + math.cos(math.pi * fraccion)))

        perdida, partes = perdida_de_lote()
        if not torch.isfinite(perdida):
            progreso["pasos_saltados"] += 1
            seguidos_malos += 1
            if seguidos_malos >= 50:
                print("[detenido] 50 pasos seguidos con pérdida no finita", flush=True)
                break
            continue
        seguidos_malos = 0
        optimizador.zero_grad(set_to_none=True)
        perdida.backward()
        nn.utils.clip_grad_norm_(modulo.parameters(), norma_maxima)
        optimizador.step()

        progreso["pasos"] += 1
        progreso["datasets_simulados"] += datasets_por_paso
        progreso["segundos"] = ya_entrenado + (time.time() - inicio)

        if progreso["pasos"] % registrar_cada == 0:
            ahora = time.time()
            valor = float(perdida)
            media_movil = valor if media_movil is None else 0.9 * media_movil + 0.1 * valor
            linea = {
                "paso": progreso["pasos"], "datasets": progreso["datasets_simulados"],
                "min": round(progreso["segundos"] / 60, 2), "perdida": round(valor, 4),
                "media_movil": round(media_movil, 4), **{k: round(float(v), 4) for k, v in partes.items()},
                "pasos_por_s": round((progreso["pasos"] - pasos_al_registrar) / (ahora - ultimo_registro), 2),
                "tasa": optimizador.param_groups[0]["lr"],
            }
            ultimo_registro, pasos_al_registrar = ahora, progreso["pasos"]
            with open(bitacora, "a") as f:
                f.write(json.dumps(linea) + "\n")
            print(json.dumps(linea), flush=True)

        if time.time() - ultimo_guardado >= guardar_cada_min * 60:
            estado = punto("periódico")
            ultimo_guardado = time.time()

    return punto("parada pedida" if detener["pedido"] else "fin del presupuesto")
