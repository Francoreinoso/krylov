---
name: validar-motor
description: Valida la red de un motor de series de Krylov (cinetica, deformacion, desgaste o sismico) con los chequeos de WORKPLAN 11.8 que no dependen del MCMC - SBC global y local y cobertura de lo que se decide en simulaciones nuevas, por tramos de tamaño del dataset, examen con la verdad escondida y semáforo - exporta el codificador a ONNX y los dos flujos a flujo.npz y flujo_local.npz, y escribe el sello del motor (sello.json) con números medidos y los campos mcmc en null. La comparación con el MCMC de referencia (NUTS) se corre al final, para los cinco motores, y se agrega al sello (D-38, tarea A-36). Úsala en PC 2 o PC 3 al terminar cada ronda (16:10 y 18:15), antes de activar la red en el producto, y otra vez al final para agregar el método lento. El motor espacial ya tiene su sello y no se reentrena. Recibe el motor_id.
argument-hint: "[cinetica | deformacion | desgaste | sismico]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Validar la red de un motor y escribir su sello

Rol: `amortizacion` (PC 2); en PC 3 la corre su persona para los motores que entrenó ahí. Hay **un sello por motor**: su ficha técnica. Lo que se dice en voz alta es el **examen** (con un archivo simulado se dice «con datos simulados»); lo medido en simulaciones va al pie de la pantalla y a la lámina técnica. Tope: 20 minutos en la ronda 1, porque la ronda 2 se lanza a las 16:30, y 45 en la ronda 2.

**`espacial` ya tiene su sello (PASA) y no se reentrena.** Para `leyes` falta el examen con su verdad escondida (A-22) y, al final, el MCMC de su archivo (A-36).

**El orden (D-38):** primero todo lo que no depende del MCMC (pasos 1 a 7), con eso se escribe el sello y se decide «pasa». El método lento (paso 8) va al final, cuando las cinco redes tienen veredicto. Se adelanta solo para una red que no pasó y cuya tarjeta no tendría con qué responder a las 17:30; cuando pase, se anota y se avisa a la persona del computador.

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`. Detalle de cada chequeo: `WORKPLAN.md`, 11.8 y 11.9.

**Antes:** ningún entrenamiento corriendo en este computador. El MCMC y las mediciones de tiempo nunca corren encima de un entrenamiento. Ronda 1 (`cinetica` en PC 2, `deformacion` en PC 3) a las 16:10; ronda 2 (`desgaste` en PC 2, `sismico` en PC 3) a las 18:15.

## Pasos

1. **Calibración en simulaciones nuevas.** SBC (el rango del valor verdadero entre las muestras del posterior tiene que ser uniforme, parámetro por parámetro) y cobertura del intervalo de 90%, en tres niveles: los parámetros globales η; los locales λ_j de cada unidad (SBC local); y **lo que se decide**, la probabilidad de cada unidad contra su valor exacto con el η y el λ_j verdaderos. Sobre 2.000 datasets simulados nuevos (si no hay tiempo, 500 y se anota).
   `uv run python -m motor.<id>.validar --sbc 2000`
2. **Por tramos de tamaño del dataset**, y el peor va al sello (`peor_grupo`, `cobertura_90_peor_grupo`): pocas, medias y muchas unidades; series cortas y largas. Los tramos salen de los rangos de `config.json` (el grupo `Diseño del dataset` del modelo).
3. **Tamaño fuera de rango.** Un archivo bajo el mínimo del motor da `rojo_datos` con un motivo que nombra lo que hay y lo que el motor conoce; uno sobre el máximo se submuestrea con semilla fija y lleva aviso. `papeles()` publica el mismo rango que `config.json`, y el archivo del demo cae bien adentro.
4. **El método rápido de siempre** del motor (el de su apartado en 11.2 a 11.5: una recta, una sola exponencial, un conteo por hora): su resultado en el mismo examen. Es solo la comparación que muestra qué se pierde sin el modelo completo.
5. **Examen con la verdad escondida:** `datos/demo/<caso>_verdad.csv` trae lo que pasó de verdad con cada unidad. Se compara con lo que la red dijo, por tramos de la probabilidad que se dio.
6. **Semáforo.** Un archivo con muy pocas lecturas tiene que dar `rojo_datos`; uno que cae lejos de las simulaciones en el espacio de resúmenes, `rojo_modelo`. La nube (`nube.npz`) se guarda solo si el motor la tiene; no es requisito.
7. **Exportación.** El codificador a ONNX con relleno y máscara hasta el tamaño máximo del motor, el tamaño real como entrada y dos salidas, s(D) y los s_j: `onnxruntime` da lo mismo que `torch` en 10 datasets (diferencia bajo 0,001). Los flujos a `flujo.npz` y `flujo_local.npz`: **con los mismos pesos y el mismo ruido, `nucleo/flujo.py` en NumPy da la misma muestra que `torch`**, con tolerancia de `float32`. Mide la latencia de un análisis completo (codificador, 32 muestras de η, los locales de cada unidad y «lo que se decide»).
8. **Al final, el método lento (A-36).** Sin nada entrenando y cuando las cinco redes tengan veredicto. NumPyro con NUTS, solo dentro de `motor/`: de 3 a 5 datasets simulados, más el del demo, con 10 minutos de presupuesto por dataset.
   `uv run python -m motor.<id>.mcmc --simulados 3 --caso <caso>`
   Se informa lo que salga, tal cual: el tiempo de cada uno, r̂, y las medias y rangos del posterior de la red contra los del MCMC. **Si NUTS no converge (r̂ sobre 1,05) en su presupuesto**, se anota «el método lento no convergió en 10 minutos» y se sigue. En `deformacion` el posterior es multimodal: 4 cadenas. **No se elige ni se degrada la referencia para que la red se vea mejor.** Si el MCMC resulta rápido, se dice, y `amortizacion.que_se_compara` dice exactamente qué se comparó (un análisis, rehacer cientos de análisis, o rehacerlo con cada dato nuevo). Las muestras del archivo del demo (η y los λ_j) se guardan en `motor/artefactos/<id>/mcmc/<clave>.npz`: son el respaldo de la tarjeta. Con esto se completan los campos `mcmc_*` del sello.
9. **Escribe `motor/artefactos/<id>/sello.json`** (después del paso 7; se completa después del 8) con los campos de `contratos/CONTRATO.md` y el veredicto (`pasa`), como el de `espacial`: `simulaciones_entrenamiento`, `entrenamiento_min`, `casos_validacion`, `cobertura_90`, `cobertura_90_peor_grupo`, `peor_grupo`, `sbc_pasa`, `cobertura_90_metodo_rapido`, `latencia_ms`, `mcmc_datasets_comparados`, `mcmc_s_por_dataset`, `mcmc_diferencia_media`, `amortizacion`, `limitaciones` (lo que el motor todavía no es: `WORKPLAN.md`, 1.2). Lo que no se midió va en `null`; no se estima: los `mcmc_*` y `amortizacion` quedan en `null` hasta el paso 8.
10. **Pide registrar** las cifras que se van a mostrar (skill `registrar-cifra`) y avisa a PC 3: el tablero lee el sello.

## Pasa si

- SBC sin sesgo visible: para los globales, los criterios de D-32; para los locales, el tamaño de la desviación de D-39 (w = √(χ²/n) bajo 0,1 y rango medio a menos de 0,03 de 0,5).
- Cobertura de 90% entre 85% y 95%, para η y para lo que se decide, y sobre 80% en el peor tramo de tamaño.
- Un análisis tarda menos de 1 segundo.

**El examen con la verdad escondida se informa y no decide (D-39):** va en el sello y es lo que se dice en voz alta, pero con 8 o 36 unidades no aprueba ni reprueba una red.

**«Pasa» no espera al MCMC (D-38).** Cuando la comparación exista se agrega al sello; si la diferencia con el MCMC convergido supera 0,3 desviaciones estándar del posterior en las medias de η, se informa y el equipo revisa el veredicto.

Los umbrales se cambian solo con una entrada en `DECISIONES.md`, nunca en silencio.

## Si no pasa

1. Se adelanta el paso 8 para el archivo del demo de ese motor (10 minutos de presupuesto) y se avisa a la persona del computador. Si converge, la tarjeta responde con la implementación `mcmc` (`KRYLOV_MOTOR_<ID>=mcmc`): el posterior del MCMC precalculado, rotulado «precalculado». El guion no dice que responde la red.
2. Si el computador está libre y falta para el tope: seguir entrenando y revalidar con el siguiente punto de guardado. A menudo basta con más datasets.
3. Achicar lo que la red conoce (rangos del prior, de unidades o de lecturas) en `config.json` y en `papeles()`, y decirlo en `limitaciones`. Sirve sobre todo cuando solo falla el peor tramo de tamaño.
4. **A las 20:30 se cierra (tope de redes).** Orden de corte: `desgaste`, `sismico`, `cinetica`, `deformacion`. El mapa de `leyes` y «¿Dónde perforo?» no se cortan. Una tarjeta sin red y sin método lento sale del inicio. Lo decide PC 3 con el equipo en H5 y en el tope de redes.

## Terminado cuando

`sello.json`, `codificador.onnx`, `flujo.npz` y `flujo_local.npz` están subidos, el estado dice «pasa» o «no pasa» con los números (incluido el peor tramo de tamaño), `estado/MODELOS.md` tiene marcadas las piezas de ese motor, y `producto` sabe qué valor poner en `KRYLOV_MOTOR_<ID>`. Las muestras de `mcmc/` y los campos `mcmc_*` se suben al final, con el paso 8.
