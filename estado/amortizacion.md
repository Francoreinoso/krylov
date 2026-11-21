# Estado · amortizacion (PC 2)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 2 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («A-23 terminada: …»): así lo lee el tablero en vivo.
Persona: Rodrigo · Dueño de `nucleo/` y `motor/`. Instrucciones: `PC2_AMORTIZACION.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/amortizacion_hasta_el_pivote.md`.

## Hecho

- sáb 12:10 · Antes del pivote, y sigue sirviendo: `motor/comun/` (codificador, flujo, entrenamiento, validación), `nucleo/flujo.py`, `nucleo/decision.py`, `nucleo/tabla.py`, `nucleo/api.py` y el motor `espacial` completo, con su sello (PASA, 09:39). Detalle en `estado/historia/amortizacion_hasta_el_pivote.md`.
- sáb 12:05 · Verificado al preparar el pivote, en este computador y con `estados` entrenando al lado: `KRYLOV_MOTOR_ESPACIAL=red`, `api.analizar("leyes")` responde verde en 0,10 s y `api.donde_medir("leyes")` rehace 480 análisis en 1,0 s. Los tiempos que van al guion se miden de nuevo sin nada entrenando (A-22).

- sáb 13:02 · A-21 terminada: `MOTORES` trae los cinco motores mineros, `casos/INICIO` las cinco tarjetas y `prueba_api` espera ese orden. No había ningún entrenamiento corriendo. Verificado: `uv run pytest nucleo -q` pasa; `api.casos()` da leyes, taludes, flotacion, flota, sismicidad; `api.analizar("leyes")` verde con la red. Una tarjeta sin motor responde `no_disponible`.
- sáb 13:10 · D-38 escrita y el plan al día (encargo directo de la persona de PC 2): el método lento va al final (tarea nueva A-36) y cada modelo lleva un nivel de diseño del dataset. Tocados: `DECISIONES.md`, `WORKPLAN.md` (6.3, 6.5 a 6.8, 11), `PC2_AMORTIZACION.md`, `AGENTS.md`, `SKILLS.md`, skills `entrenar-motor`, `validar-motor`, `ronda`, `actualizar-estado`, y `contratos/CONTRATO.md` (tabla de rangos y `papeles().rangos`).
- sáb 13:10 · `estado/MODELOS.md` creado: los cinco modelos con sus niveles y 13 casillas de estado cada uno. El tablero en vivo lo lee (sección «Los cinco modelos»); el parseo se probó con node contra los archivos reales.
- sáb 13:12 · A-23 terminada: el andamio de series. `motor/comun/series.py` (codificador por unidad con máscara, atención sobre unidades, flujo global y local, pérdida, SBC global, local y de lo que se decide por tramos de tamaño, sello sin MCMC, exportación) y `nucleo/series.py` (leer el archivo largo, revisar tamaño, ONNX + flujos en NumPy, `unidades`, `curva`, `factores`, examen). Verificado con `uv run pytest motor/comun/prueba_series.py -q`: exporta a ONNX con formas fijas, NumPy = torch en los dos flujos (diferencia bajo 1e-4), el relleno no cambia los resúmenes y la pérdida baja.
- sáb 13:12 · A-24, simulador y red de `cinetica` listos, con el a priori de tamaño (2 a 16 líneas, 5 a 12 celdas, 3 al total medidas, 2 a 6 minutos por celda). Verificado con `uv run pytest motor/cinetica -q`: tamaños dentro del rango, un solo preprocesamiento, y el archivo del demo cae entre los percentiles 2 y 98 de lo simulado.

- sáb 13:20 · A-23, ampliación: el andamio acepta un estado discreto por unidad (`CON_CLASE`, para `deformacion`: estable o acelerando), con su cabeza exportada junto al flujo local y muestreada en NumPy. Las mismas pruebas pasan.
- sáb 13:20 · A-24: `api.analizar("flotacion")` probado de punta a punta con una red de ensayo exportada a una carpeta temporal: la respuesta trae las mismas claves que `contratos/ejemplos/analizar_flotacion.json` (unidades con `curva`, factores, examen, semáforo) y un archivo de 1 línea da `rojo_datos` con su motivo. La red de ensayo se borró: no hay artefactos de `cinetica` en el repositorio.
- sáb 13:31 · A-24, prueba de humo de `cinetica`: 305.536 datasets en 3 min (CPU, lote 128); la pérdida media bajó de 6,9 a 4,0; `validar --sbc 200` corre (cobertura de lo que se decide 0,91, ensayo: no es resultado). Comando: `uv run python -m motor.cinetica.entrenar --minutos 3 --nuevo --carpeta motor/checkpoints/cinetica_humo`.
- sáb 13:32 · A-25 terminada: `deformacion` listo para lanzar en PC 3. `nucleo/deformacion.py` (diseño 6 a 80 sectores, 24 a 200 lecturas, hasta 15% faltantes; un solo preprocesamiento: grilla común, resta de la primera lectura y de la mediana entre sectores, escala e; `analizar` con curva y `marca`) y `motor/deformacion/` (simular, entrenar, validar, exportar, pruebas). Estado discreto por sector (`CON_CLASE`); locales (log v, log(u_f − 1), log A). Verificado: `uv run pytest motor/deformacion nucleo -q` pasa (predictivo a priori del demo entre los percentiles 2 y 98, mismo preprocesamiento en simulador y archivo, modo común exacto, `rojo_datos` con 3 sectores o 10 lecturas); exporta con NumPy = torch (diferencia bajo 1e-6) y `analizar("taludes")` da la forma del contrato en 212 ms con la red sin entrenar. Prueba de humo: 129.536 datasets en 3 min (GPU del Mac, lote 128), pérdida de 10,2 a 4,9; `validar --sbc 200` corre (ensayo, no es resultado).
- sáb 13:32 · A-23, arreglo del andamio: con estado discreto, la cobertura local ya no cuenta la columna z.

## En curso

- sáb 13:32 · A-26: ronda 1 lista para lanzar cuando Rodrigo dé la partida. PC 3: `caffeinate -dims uv run python -m motor.deformacion.entrenar --hasta 16:10 --dispositivo mps --lote 128 --guardar-cada-min 10` (medido aquí: 670 a 770 datasets/s en la GPU del Mac, 3,5 GB; en CPU con lote 64, 130/s). PC 2: `cinetica` con `--dispositivo mps --lote 512`. Sigue A-28 (`sismico`) y A-27 (`desgaste`), sin lanzar.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 13:10 · **A PC 3:** por encargo directo de la persona de PC 2 esta sesión editó archivos tuyos: `DECISIONES.md` (D-38), `WORKPLAN.md`, `casos/INICIO` (las cuatro tarjetas descomentadas), las skills y el tablero en vivo (sección nueva que lee `estado/MODELOS.md`). Falta de tu lado: `PC3_SEGUIMIENTO.md` y la columna «Método lento» de `estado/TABLERO.md` todavía suponen el MCMC antes del entrenamiento; con D-38, «Método lento» pendiente no es atraso hasta A-36. Y hay una decisión abierta para las 17:30 al final de `DECISIONES.md` (ronda 2).
- sáb 13:10 · **A PC 1:** el contrato ganó dos cosas opcionales (D-38). `papeles(motor_id)` trae `rangos` (tamaños con que practicó la red y una `frase` lista); un archivo sobre el máximo responde `amarillo` con aviso (submuestra de semilla fija) y bajo el mínimo `rojo_datos` con su motivo. La forma de `analizar` no cambió.
- sáb 13:10 · **A PC 3:** registrar cifras solo cuando haya sello; hoy no hay ninguna nueva.
- sáb 13:32 · **A PC 3 (`WORKPLAN.md` 11.2):** el motor quedó con tres locales continuos (log v_j, log(u_f,j − 1), log A_j) más z_j, no solo (z_j, log(u_f,j − 1)); y el simulador suma un modo común AR(1) que no se infiere (amplitud hasta 0,4 del sector típico): el preprocesamiento lo resta. Agregar esas dos líneas al bloque.
- sáb 13:32 · **A PC 3 (`casos/taludes.yaml`):** `velocidad_fondo` no tiene sentido sin unidades (el motor divide por la escala del archivo) y no sale en «qué pesa». Propuesta: cambiar esa etiqueta por `falta_para_ceder: "Cuánto les falta, en general, a los sectores que se aceleran"`. `ruido` ahora es el error de lectura comparado con el movimiento de fondo.

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | (ninguno; `estados` se detiene con el pivote) |
| Comando exacto | — |
| Hora de inicio | — |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| `leyes`: bloques por color (costos por defecto) | 147 conviene apartar, 568 puede ir a la planta, 309 no sabemos (1.024 bloques) | `api.analizar("leyes")` con la red | 12:05 |
| `leyes`: lo que cuesta no saber | US$ 1.577.707 (supuestos K-22 y K-23) | lo mismo | 12:05 |
| `leyes`: examen | 61 de 68 muestras escondidas dentro del rango de 90% | lo mismo | 12:05 |
| `leyes`: «¿Dónde perforo?» | 480 análisis rehechos; pin A vale US$ 8.943 (neto 7.443), B 8.376, C 7.967 | `api.donde_medir("leyes")` con la red | 12:05 |
| `espacial`: sello | PASA. 7.750.592 terrenos simulados, 280 min, cobertura del 90%: 0,90; 117 s por análisis con el método lento | `motor/artefactos/espacial/sello.json` | 09:39 |
