---
name: validar-motor
description: Valida la red de un motor de series de Krylov (cinetica, deformacion, desgaste o sismico) con los chequeos de WORKPLAN 11.8 - SBC global y local y cobertura de lo que se decide en simulaciones nuevas, comparación con el MCMC de referencia (NUTS) si converge en 10 minutos por dataset, examen con la verdad escondida y semáforo - exporta el codificador a ONNX y los dos flujos a flujo.npz y flujo_local.npz, y escribe el sello del motor (sello.json) con números medidos. Úsala en PC 2 o PC 3 al terminar cada ronda (16:10 y 18:15) y antes de activar la red en el producto. El motor espacial ya tiene su sello y no se reentrena. Recibe el motor_id.
argument-hint: "[cinetica | deformacion | desgaste | sismico]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Validar la red de un motor y escribir su sello

Rol: `amortizacion` (PC 2); en PC 3 la corre su persona para los motores que entrenó ahí. Hay **un sello por motor**: su ficha técnica. Lo que se dice en voz alta es el **examen** (con un archivo simulado se dice «con datos simulados»); lo medido en simulaciones va al pie de la pantalla y a la lámina técnica. Tope: 20 minutos en la ronda 1, porque la ronda 2 se lanza a las 16:30, y 45 en la ronda 2.

**`espacial` ya tiene su sello (PASA) y no se reentrena.** Para `leyes` solo falta el MCMC de su archivo y el examen con su verdad escondida (A-22).

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`. Detalle de cada chequeo: `WORKPLAN.md`, 11.8 y 11.9.

**Antes:** ningún entrenamiento corriendo en este computador. El MCMC y las mediciones de tiempo nunca corren encima de un entrenamiento. Ronda 1 (`cinetica` en PC 2, `deformacion` en PC 3) a las 16:10; ronda 2 (`desgaste` en PC 2, `sismico` en PC 3) a las 18:15.

## Pasos

1. **Calibración en simulaciones nuevas.** SBC (el rango del valor verdadero entre las muestras del posterior tiene que ser uniforme, parámetro por parámetro) y cobertura del intervalo de 90%, en tres niveles: los parámetros globales η; los locales λ_j de cada unidad (SBC local); y **lo que se decide**, la probabilidad de cada unidad contra su valor exacto con el η y el λ_j verdaderos. Sobre 2.000 datasets simulados nuevos (si no hay tiempo, 500 y se anota).
   `uv run python -m motor.<id>.validar --sbc 2000`
2. **Por grupos**, y se reporta el peor: pocas y muchas unidades; series cortas y largas.
3. **Comparación con el MCMC de referencia** (NumPyro con NUTS, solo dentro de `motor/`): **de 3 a 5 datasets simulados, más el del demo.** Medias y rangos del posterior de la red contra los del MCMC, y **el tiempo de cada uno**: esa es la cifra de amortización. Las muestras del archivo del demo (η y los λ_j) se guardan en `motor/artefactos/<id>/mcmc/<clave>.npz`: son el plan B de la tarjeta.
   `uv run python -m motor.<id>.mcmc --simulados 3 --caso <caso>`
   **Si NUTS no converge (r̂ sobre 1,05) en 10 minutos por dataset**, se anota «el método lento no convergió en 10 minutos», el sello se apoya en el SBC y esa tarjeta no tiene plan B. En `deformacion` el posterior es multimodal: 4 cadenas y se informa r̂.
4. **El método rápido de siempre** del motor (el de su apartado en 11.2 a 11.5: una recta, una sola exponencial, un conteo por hora): su resultado en el mismo examen. Es solo la comparación que muestra qué se pierde sin el modelo completo.
5. **Examen con la verdad escondida:** `datos/demo/<caso>_verdad.csv` trae lo que pasó de verdad con cada unidad. Se compara con lo que la red dijo, por tramos de la probabilidad que se dio.
6. **Semáforo.** Un archivo con muy pocas lecturas tiene que dar `rojo_datos`; uno que cae lejos de las simulaciones en el espacio de resúmenes, `rojo_modelo`. La nube (`nube.npz`) se guarda solo si el motor la tiene; no es requisito.
7. **Exportación.** El codificador a ONNX con formas fijas con relleno y dos salidas, s(D) y los s_j: `onnxruntime` da lo mismo que `torch` en 10 datasets (diferencia bajo 0,001). Los flujos a `flujo.npz` y `flujo_local.npz`: **con los mismos pesos y el mismo ruido, `nucleo/flujo.py` en NumPy da la misma muestra que `torch`**, con tolerancia de `float32`. Mide la latencia de un análisis completo (codificador, 32 muestras de η, los locales de cada unidad y «lo que se decide»).
8. **Escribe `motor/artefactos/<id>/sello.json`** con los campos de `contratos/CONTRATO.md` y el veredicto (`pasa`), como el de `espacial`: `simulaciones_entrenamiento`, `entrenamiento_min`, `casos_validacion`, `cobertura_90`, `cobertura_90_peor_grupo`, `peor_grupo`, `sbc_pasa`, `cobertura_90_metodo_rapido`, `latencia_ms`, `mcmc_datasets_comparados`, `mcmc_s_por_dataset`, `mcmc_diferencia_media`, `amortizacion`, `limitaciones` (lo que el motor todavía no es: `WORKPLAN.md`, 1.2). Lo que no se midió va en `null`; no se estima.
9. **Pide registrar** las cifras que se van a mostrar (skill `registrar-cifra`) y avisa a PC 3: el tablero lee el sello.

## Pasa si

- SBC sin sesgo visible (criterios de D-32).
- Cobertura de 90% entre 85% y 95%, para η y para lo que se decide.
- Diferencia con el MCMC bajo 0,3 desviaciones estándar del posterior en las medias de η, si el MCMC convergió.
- Un análisis tarda menos de 1 segundo.

Los umbrales se cambian solo con una entrada en `DECISIONES.md`, nunca en silencio.

## Si no pasa

1. La tarjeta sigue respondiendo con la implementación `mcmc` (`KRYLOV_MOTOR_<ID>=mcmc`): el posterior del MCMC precalculado, rotulado «precalculado». El guion no dice que responde la red.
2. Si el computador está libre y falta para el tope: seguir entrenando y revalidar con el siguiente punto de guardado. A menudo basta con más datasets.
3. Achicar lo que la red conoce (rangos del prior, de unidades o de lecturas) y decirlo en `limitaciones`.
4. **A las 20:30 se cierra (tope de redes).** Orden de corte: `desgaste`, `sismico`, `cinetica`, `deformacion`. El mapa de `leyes` y «¿Dónde perforo?» no se cortan. Una tarjeta sin red y sin método lento sale del inicio. Lo decide PC 3 con el equipo en H5 y en el tope de redes.

## Terminado cuando

`sello.json`, `codificador.onnx`, `flujo.npz`, `flujo_local.npz` y las muestras de `mcmc/` están subidos, el estado dice «pasa» o «no pasa» con los números, y `producto` sabe qué valor poner en `KRYLOV_MOTOR_<ID>`.
