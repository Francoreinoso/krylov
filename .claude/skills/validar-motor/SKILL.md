---
name: validar-motor
description: Valida la red de un motor de Krylov (espacial, supervivencia, jerarquico o estados) con cuatro chequeos - SBC y cobertura en simulaciones nuevas, comparación con el MCMC de referencia, examen con datos reales reservados y la nube con el archivo malo - exporta el codificador a ONNX y el flujo a flujo.npz, y escribe el sello del motor (sello.json) con números medidos. Úsala en PC 2 o PC 3 después de cada punto de guardado que se quiera usar y antes de activar la red en el producto. Recibe el motor_id.
argument-hint: "[espacial | supervivencia | jerarquico | estados]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Validar la red de un motor y escribir su sello

Rol: `amortizacion` (PC 2); en PC 3 la corre su persona para los motores que entrenó ahí. Hay **un sello por motor**: su ficha técnica. Lo que se dice en voz alta es el **examen con datos reales**; lo medido en simulaciones va al pie de la pantalla y a la lámina técnica. Tope: 45 minutos por motor.

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`. Detalle de cada chequeo: `WORKPLAN.md`, 11.8 y 11.9.

**Antes:** ningún entrenamiento corriendo en este computador. El MCMC y las mediciones de tiempo nunca corren encima de un entrenamiento.

## Pasos

1. **Calibración en simulaciones nuevas.** SBC (el rango del valor verdadero entre las muestras del posterior tiene que ser uniforme, parámetro por parámetro) y cobertura del intervalo de 90%, sobre 2.000 datasets simulados nuevos (si no hay tiempo, 500 y se anota).
   `uv run python -m motor.<id>.validar --sbc 2000`
   En `espacial`, además, la cobertura por bloque de la cabeza de mapa.
2. **Por grupos**, y se reporta el peor: n chico y n grande; pocos y muchos grupos (cargos, barrios); en `espacial`, pocas mediciones, mucho ruido y alcance tan largo como el terreno.
3. **Comparación con el MCMC de referencia** (NumPyro con NUTS, solo dentro de `motor/`): **de 5 a 10 datasets simulados, más el real.** Medias y rangos del posterior de la red contra los del MCMC, y **el tiempo de cada uno**: esa es la cifra de amortización. Las muestras del dataset real se guardan en `motor/artefactos/<id>/mcmc/<clave>.npz`: son el plan B de la tarjeta.
   `uv run python -m motor.<id>.mcmc --simulados 5 --real`
   En `espacial` un MCMC tarda segundos: lo que se compara ahí es rehacer los cerca de 480 análisis de «¿Dónde mido?».
4. **El método rápido de siempre** (regresión logística simple; en el terreno, kriging con parámetros fijos): su cobertura en las mismas simulaciones y su resultado en el examen. Es solo la comparación que muestra qué se pierde sin el modelo completo.
5. **Examen con datos reales reservados:** las respuestas guardadas en `<caso>_verdad.csv`, por tramos de la probabilidad que se dio. En el terreno, se esconde 20% de las mediciones y se repite con cinco particiones.
6. **Modelo mal especificado (la nube).** Sobre el predictivo a priori del motor, los dos detectores de 11.9: los ejes con nombre y la distancia en los resúmenes aprendidos. Para `supervivencia`: **`rotacion_malo` tiene que caer fuera y, corregido, dentro.** Se guarda `nube.npz`.
7. **Exportación.** El codificador a ONNX: `onnxruntime` da lo mismo que `torch` en 10 datasets (diferencia bajo 0,001), con n variable. El flujo a `flujo.npz`: **con los mismos pesos y el mismo ruido, `nucleo/flujo.py` en NumPy da la misma muestra que `torch`**, con tolerancia de `float32`. Mide la latencia de un análisis completo (codificador, 32 muestras del flujo, paso local) y, en `espacial`, de un lote de 500 grillas.
8. **Escribe `motor/artefactos/<id>/sello.json`** con los campos de `contratos/CONTRATO.md`: `simulaciones_entrenamiento`, `entrenamiento_min`, `casos_validacion`, `cobertura_90`, `cobertura_90_peor_grupo`, `peor_grupo`, `sbc_pasa`, `cobertura_90_metodo_rapido`, `latencia_ms`, `mcmc_datasets_comparados`, `mcmc_s_por_dataset`, `mcmc_diferencia_media`, `amortizacion`, `nube_malo_cae_fuera`, `limitaciones` (incluido hasta dónde llega el generador de covariables). Lo que no se midió va en `null`; no se estima.
9. **Pide registrar** las cifras que se van a mostrar (skill `registrar-cifra`).

## Pasa si

- SBC sin sesgo visible.
- Cobertura de 90% entre 85% y 95%, y sobre 80% en el peor grupo.
- Diferencia con el MCMC bajo 0,3 desviaciones estándar del posterior en las medias.
- Un análisis tarda menos de 1 segundo; en `espacial`, un lote de 500 grillas, menos de 2 segundos.

Los umbrales se cambian solo con una entrada en `DECISIONES.md`, nunca en silencio.

## Si no pasa

1. La tarjeta sigue respondiendo con la implementación `mcmc` (`KRYLOV_MOTOR_<ID>=mcmc`): el posterior del MCMC precalculado, rotulado «precalculado». El guion no dice que responde la red.
2. Si el computador está libre y falta para el tope: seguir entrenando y revalidar con el siguiente punto de guardado. A menudo basta con más datasets.
3. Achicar lo que la red conoce (rangos del prior o de n) y decirlo en `limitaciones`.
4. **A las 16:00 se cierra.** Orden de corte: `estados`, `jerarquico`, `supervivencia`, la cabeza de flujo de `espacial`. La cabeza de mapa y «¿Dónde mido?» no se cortan. Lo decide PC 3 con el equipo en el H2 de cada motor.

## Terminado cuando

`sello.json`, `codificador.onnx`, `flujo.npz` y las muestras de `mcmc/` están subidos, el estado dice «pasa» o «no pasa» con los números, y `producto` sabe qué valor poner en `KRYLOV_MOTOR_<ID>`.
