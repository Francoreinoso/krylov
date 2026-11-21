---
name: medir-rendimiento
description: Mide en 8 minutos cuánto simula y entrena de verdad un MacBook Air sin ventilador con la red real de un motor de Krylov (espacial, supervivencia, jerarquico o estados), decide procesador contra GPU del Mac, y mide el presupuesto del paso local. Úsala en PC 2 o PC 3 antes de lanzar cada entrenamiento, o si uno va más lento de lo previsto. Recibe el motor_id.
argument-hint: "[espacial | supervivencia | jerarquico | estados]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Medir rendimiento y elegir dispositivo, por motor

Rol: `amortizacion` (PC 2), o la persona de PC 3 en su computador. Duración: 8 minutos, no más. Se mide **motor por motor** y con la red real, no con una de juguete: por eso va después de escribir el simulador y la red y justo antes de lanzar. De aquí sale el presupuesto de cómputo: ninguna cifra de «millones de datasets» ni de horas se compromete antes de medirla.

## Antes

- Enchufado, **tapa abierta**, brillo al mínimo, superficie dura. Modo de bajo consumo apagado.
- Entorno: `uv sync --group entrenar`. Confirma Accelerate con `uv run python -c "import numpy; numpy.show_config()"`.
- **Nada entrenando en este computador.** Un número medido encima de un entrenamiento no sirve.

## Pasos

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`.

1. **Simulador (1 min).** Datasets simulados por segundo, en procesador y en la GPU del Mac, con el n y el tamaño de lote reales.
   `uv run python -m motor.<id>.medir --que simulador`
2. **Entrenamiento en procesador (2 min).** 20 pasos de calentamiento y 200 cronometrados, con dos tamaños de lote.
   `uv run python -m motor.<id>.medir --que entrenar --dispositivo cpu`
3. **Entrenamiento en la GPU del Mac (2 min).** Lo mismo con `--dispositivo mps`, todo en `float32`. Llama a `torch.mps.synchronize()` antes de parar el cronómetro; sin eso el número es falso. Anota cualquier aviso de operaciones que caen al procesador.
4. **Sostenido (2 min).** El ganador sin parar. Compara los últimos 30 s con los primeros 30 s: esa es la caída por temperatura.
5. **Registra** en el estado del computador → Números medidos, con hora y con el motor: datasets por segundo, pasos por segundo, dispositivo, y la estimación de cuántos datasets verá la red en su turno.

## Presupuesto del paso local (una vez por motor de tabla, cuando exista `nucleo/<id>.py`)

Por análisis son 32 muestras × unidades × nodos². Mide con el archivo real del caso:

- **Un análisis: menos de 1 segundo.**
- **La cartera de 1.000 empresas: segundos.**
- Si no alcanza: menos nodos (15 de Gauss-Hermite suelen bastar en una dimensión), vectorizar por grupo y, para la cartera, 8 muestras. Anota con cuántos nodos lo logra.

## Tiempos que van al guion

Los de `donde_medir`, la cartera, el recorrido y el MCMC de referencia se miden **sin ningún entrenamiento corriendo en ese computador** (ventanas de 08:30 a 09:15 y de 12:00 a 12:30 en PC 2).

## Cómo decidir

- **Dispositivo:** la GPU del Mac solo si supera al procesador por más de 1,5 veces y sin avisos de caída. Si no, procesador. Con la red convolucional de `espacial` suele ganar la GPU; con los codificadores de conjuntos no se sabe: se mide.
- **Si el sostenido cae más de 30%:** baja el tamaño de lote o usa el procesador. Un turno a ritmo parejo sirve más que uno que se ahoga.
- **Nube:** solo si a las 09:00 algo va atrasado y una persona abrió la sesión de Kaggle o Colab y vio la cuota (`STACK.md`, 3.3).

## Terminado cuando

Los números del motor están en el estado con hora, el dispositivo está elegido y la estimación de datasets del turno está escrita.
