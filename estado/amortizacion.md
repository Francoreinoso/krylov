# Estado · amortizacion (PC 2)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 2 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago.
Persona: [nombre] · Dueño de `nucleo/` y `motor/`. Instrucciones: `PC2_AMORTIZACION.md`.

## Hecho

- sáb 03:00 · Plan final recibido. Nada construido todavía.

## En curso

- (vacío) · Primera tarea: A-01, entorno y preprocesamiento espacial. Meta de la noche: entrenamiento de la red espacial corriendo antes de las 05:15.

## Bloqueos

- (ninguno)

## Pedidos a otros

- (ninguno)

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Comando exacto | — |
| Hora de inicio | — |
| Dónde quedan los puntos de guardado | — |
| Cómo retomar si se cae | — |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Simular un conjunto de 150 puntos sueltos, 1 proceso | 0,33 ms | NumPy con Accelerate, M4 16 GB, lote de 64 | sáb 00:24 |
| Simular un conjunto de 300 puntos sueltos, 1 proceso | 1,15 ms | ídem | sáb 00:24 |
| Terrenos simulados por segundo en grilla de 32×32 | sin medir | A-02 | — |
| Pasos de entrenamiento por segundo, CPU | sin medir | `medir-rendimiento` | — |
| Pasos de entrenamiento por segundo, GPU del Mac | sin medir | `medir-rendimiento` | — |
| Caída sostenida por temperatura | sin medir | `medir-rendimiento` | — |
| Dispositivo elegido | sin decidir | `medir-rendimiento` | — |
| Terrenos simulados usados en el entrenamiento | sin medir | A-09 | — |
| Sello de `espacial` | sin medir | `validar-motor` | — |
| «¿Dónde mido?»: análisis rehechos y segundos, con la red | sin medir | A-11 | — |
| «¿Dónde mido?»: los mismos análisis con el método exacto | sin medir | A-11 | — |
| Cartera: análisis y segundos | sin medir | A-12 | — |
