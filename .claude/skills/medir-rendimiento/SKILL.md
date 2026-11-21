---
name: medir-rendimiento
description: Mide en 8 minutos cuánto simula y entrena de verdad el MacBook Air M4 (sin ventilador) con la red espacial real, y decide procesador contra GPU del Mac. Úsala en PC 2 antes de lanzar el entrenamiento nocturno, o si un entrenamiento va más lento de lo previsto.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Medir rendimiento y elegir dispositivo

Rol: `amortizacion` (PC 2). Duración: 8 minutos, no más. Se mide con la red real, no con una de juguete: por eso va después de escribir el simulador y la red (tareas A-02 y A-03) y justo antes de lanzar (A-04).

## Antes

- Enchufado, **tapa abierta**, brillo al mínimo, superficie dura. Modo de bajo consumo apagado.
- Entorno: `uv sync --group entrenar`. Confirma Accelerate con `uv run python -c "import numpy; numpy.show_config()"`.

## Pasos

Los comandos son orientativos: ajústalos al código real.

1. **Simulador (1 min).** Terrenos por segundo en lotes de 256, en procesador y en la GPU del Mac.
   `uv run python -m motor.medir --que simulador`
2. **Entrenamiento en procesador (2 min).** 20 pasos de calentamiento y 200 cronometrados, lotes de 128 y 256.
   `uv run python -m motor.medir --que entrenar --dispositivo cpu`
3. **Entrenamiento en la GPU del Mac (2 min).** Lo mismo con `--dispositivo mps`, todo en `float32`. Llama a `torch.mps.synchronize()` antes de parar el cronómetro; sin eso el número es falso. Anota cualquier aviso de operaciones que caen al procesador.
4. **Sostenido (2 min).** El ganador sin parar. Compara los últimos 30 s con los primeros 30 s: esa es la caída por temperatura.
5. **Registra** en `estado/amortizacion.md` → Números medidos, con hora. De aquí sale la estimación de cuántos terrenos simulados verá la red en la noche.

## Cómo decidir

- **Dispositivo:** la GPU del Mac solo si supera al procesador por más de 1,5 veces y sin avisos de caída. Si no, procesador.
- **Si el sostenido cae más de 30%:** baja el tamaño de lote o usa el procesador. Una noche a ritmo parejo sirve más que una que se ahoga.
- **Nube:** no se decide ahora. Solo si en H1 el entrenamiento nocturno no sirve (`STACK.md`, 3.3).

## Terminado cuando

Los números están en el estado con hora y el dispositivo está elegido.
