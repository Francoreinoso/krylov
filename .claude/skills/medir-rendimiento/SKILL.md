---
name: medir-rendimiento
description: Mide en 8 minutos cuánto simula y entrena de verdad un MacBook Air sin ventilador con la red real de un motor de series de Krylov (cinetica, deformacion, desgaste o sismico), decide procesador contra GPU del Mac, y mide el presupuesto de un análisis. Úsala en PC 2 o PC 3 antes de lanzar cada entrenamiento de las dos rondas, o si uno va más lento de lo previsto. El motor espacial ya se midió y no se repite. Recibe el motor_id.
argument-hint: "[cinetica | deformacion | desgaste | sismico]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Medir rendimiento y elegir dispositivo, por motor

Rol: `amortizacion` (PC 2), o la persona de PC 3 en su computador. Duración: 8 minutos, no más. Se mide **motor por motor** y con la red real (la del andamio de series, `motor/comun/series.py`), no con una de juguete: por eso va después de escribir el simulador y la red y justo antes de lanzar su ronda. De aquí sale el presupuesto de cómputo: ninguna cifra de «millones de datasets» ni de minutos se compromete antes de medirla. `espacial` ya se midió y entrenó: no se repite.

## Antes

- Enchufado, **tapa abierta**, brillo al mínimo, superficie dura. Modo de bajo consumo apagado.
- Entorno: `uv sync --group entrenar`. Confirma Accelerate con `uv run python -c "import numpy; numpy.show_config()"`.
- **Nada entrenando en este computador.** Un número medido encima de un entrenamiento no sirve.

## Pasos

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`.

1. **Simulador (1 min).** Datasets simulados por segundo, en procesador y en la GPU del Mac, con los tamaños máximos (unidades y lecturas) y el tamaño de lote reales.
   `uv run python -m motor.<id>.medir --que simulador`
2. **Entrenamiento en procesador (2 min).** 20 pasos de calentamiento y 200 cronometrados, con dos tamaños de lote.
   `uv run python -m motor.<id>.medir --que entrenar --dispositivo cpu`
3. **Entrenamiento en la GPU del Mac (2 min).** Lo mismo con `--dispositivo mps`, todo en `float32`. Llama a `torch.mps.synchronize()` antes de parar el cronómetro; sin eso el número es falso. Anota cualquier aviso de operaciones que caen al procesador.
4. **Sostenido (2 min).** El ganador sin parar. Compara los últimos 30 s con los primeros 30 s: esa es la caída por temperatura.
5. **Registra** en el estado del computador → Números medidos, con hora y con el motor: datasets por segundo, pasos por segundo, dispositivo, y la estimación de cuántos datasets verá la red en su ronda (unos 100 minutos).

## Presupuesto de un análisis (una vez por motor, cuando exista `nucleo/<id>.py`)

Por análisis son 32 muestras de los parámetros globales y, por cada una, una muestra de los locales de cada unidad, más la función «lo que se decide» del motor (`WORKPLAN.md`, 11.6). Mide con el archivo del demo:

- **Un análisis: menos de 1 segundo.**
- Si no alcanza: vectorizar por unidad y, si todavía falta, menos sorteos dentro de «lo que se decide». Anota con cuánto lo logra.

## Tiempos que van al guion

Los de `donde_medir`, el recorrido y el MCMC de referencia se miden **sin ningún entrenamiento corriendo en ese computador**: antes de las 14:30, de 16:10 a 16:30 y de 18:15 a 19:00 (`WORKPLAN.md`, 6.3).

## Cómo decidir

- **Dispositivo:** la GPU del Mac solo si supera al procesador por más de 1,5 veces y sin avisos de caída. Si no, procesador. Con la red convolucional de `espacial` ganó la GPU; con los codificadores de series, que son redes chicas sobre muchas unidades, no se sabe: se mide.
- **Si el sostenido cae más de 30%:** baja el tamaño de lote o usa el procesador. Una ronda a ritmo parejo sirve más que una que se ahoga.
- **Cómputo fuera de los dos Mac (Kaggle o Colab):** solo si una ronda va atrasada y una persona abrió la sesión y vio la cuota (`STACK.md`, 3.3).

## Terminado cuando

Los números del motor están en el estado con hora, el dispositivo está elegido y la estimación de datasets de la ronda está escrita.
