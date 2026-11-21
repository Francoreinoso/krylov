---
name: validar-motor
description: Mide si la red del motor espacial de Krylov acierta cuando dice que acierta, la compara con el método exacto y con el método rápido de siempre, la exporta a ONNX y escribe su sello (sello.json) con números medidos. Úsala en PC 2 después de cada punto de guardado que se quiera usar y antes de activar la red en el producto.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Validar la red y escribir su sello

Rol: `amortizacion` (PC 2). El **sello** es la ficha técnica de un motor. Lo que se dice en voz alta es el **examen con datos reales**; lo medido en simulaciones va al pie de la pantalla y a la lámina técnica. Tope: 30 minutos.

Los comandos son orientativos: ajústalos al código real.

## Pasos

1. **Exactitud en 5.000 terrenos simulados nuevos** (si no hay tiempo, 2.000 y se anota): con qué frecuencia el rango de 90% que da la red contiene el valor verdadero del bloque.
   `uv run python -m motor.validar --n 5000`
2. **Por grupos difíciles**, y se reporta el peor: pocas mediciones (menos de 60), mucho ruido de medición, continuidad tan larga como el terreno.
3. **Contra el método exacto** en 20 terrenos simulados: el mapa de la red y el del método exacto tienen que parecerse (diferencia media de la probabilidad por bloque bajo 0,05). Anota cuántos segundos tarda el exacto por análisis.
4. **Contra el método rápido de siempre** (el que fija los parámetros del terreno en vez de admitir que no los conoce): mide su exactitud en los mismos 5.000 terrenos. Es la cifra «dice 90% y acierta N%».
5. **Examen con datos reales:** en el terreno del demo, esconde 20% de las mediciones, predícelas con el resto y cuenta cuántas caen dentro del rango. Repite con cinco particiones.
6. **Exporta a ONNX** y comprueba que `onnxruntime` da lo mismo que `torch` en 10 terrenos (diferencia bajo 0,001). Mide la latencia de una pasada y de un lote de 500.
7. **Escribe `motor/artefactos/espacial/sello.json`** con los campos de `contratos/CONTRATO.md`. Lo que no se midió va en `null`; no se estima.
8. **Pide registrar** las cifras que se van a mostrar (skill `registrar-cifra`).

## Pasa si

- Exactitud global entre 87% y 93% cuando dice 90%.
- Peor grupo sobre 82%.
- Se parece al método exacto (paso 3).
- Un lote de 500 terrenos tarda menos de 2 segundos con `onnxruntime` en el computador del escenario.

## Si no pasa

1. Seguir entrenando: a menudo basta con más terrenos. Revalidar con el siguiente punto de guardado.
2. Achicar lo que la red conoce (por ejemplo, sin terrenos de continuidad muy larga) y decirlo en `limitaciones`.
3. Quedarse con el método exacto para el mapa y precalcular «¿Dónde mido?». El demo se ve igual en la URL pública; en el escenario la interacción queda limitada a los pines precalculados y el guion dice «precalculado». Se decide en H2.

## Terminado cuando

`sello.json` y `modelo.onnx` están subidos, el estado dice «pasa» o «no pasa» con los números, y `producto` sabe qué valor poner en `KRYLOV_MOTOR_ESPACIAL`.
