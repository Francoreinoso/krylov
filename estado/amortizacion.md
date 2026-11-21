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
- sáb 13:50 · A-27, `desgaste` listo salvo su prueba de humo: `nucleo/desgaste.py` (diseño 8 a 120 camiones, 3 a 20 muestras; preprocesamiento único; `analizar` con curva hasta la mantención y línea de falla) y `motor/desgaste/` (simular, entrenar, validar, exportar, pruebas). Verificado con `uv run pytest motor/desgaste -q` (6 pasan: tamaños, camiones en servicio, mismo preprocesamiento, la probabilidad de falla contra simular hacia adelante, predictivo a priori del demo, `rojo_datos` con 3 camiones); exporta con NumPy = torch (bajo 1e-6); `analizar("flota")` con la red sin entrenar da la forma del contrato en 281 ms; en 120 pasos de procesador la pérdida baja de 5,7 a 2,7. La prueba de humo de 3 minutos no se corrió: `cinetica` está entrenando aquí.
- sáb 13:55 · A-28, `sismico` listo salvo su prueba de humo: `nucleo/sismico.py` (diseño 2 a 16 sectores, ventana de 2 a 24 h, hasta 300 sismos; preprocesamiento único con la tronadura como primera lectura de cada sector; forma cerrada de lo que se decide; `analizar` con la curva del acumulado) y `motor/sismico/` (simulador por ramificación, entrenar, validar, exportar, pruebas). Verificado con `uv run pytest motor/sismico -q` (5 pasan: tamaños y sectores sin sismos, mismo preprocesamiento, forma cerrada contra 20.000 simulaciones hacia adelante, predictivo a priori del demo, `rojo_datos`); exporta con NumPy = torch (bajo 1e-6); `analizar("sismicidad")` con la red sin entrenar da la forma del contrato en 117 ms; en 100 pasos de procesador la pérdida baja de 6,4 a 5,3. Sin prueba de humo de 3 minutos todavía.
- sáb 13:55 · A-29, la forma: con la red sin entrenar exportada a una carpeta temporal, `analizar` de `taludes`, `flotacion`, `flota` y `sismicidad` devuelve las mismas claves que su ejemplo de `contratos/ejemplos/` (unidades con `curva`, factores, examen, semáforo). No hay artefactos de estos motores en el repositorio: hasta que una red pase su sello, las tarjetas responden `no_disponible`. `uv run pytest nucleo motor/comun/prueba_series.py motor/cinetica motor/deformacion motor/desgaste motor/sismico -q`: 59 pasan.

## En curso

- sáb 13:32 · A-26: ronda 1 lista para lanzar cuando Rodrigo dé la partida. PC 3: `caffeinate -dims uv run python -m motor.deformacion.entrenar --hasta 16:10 --dispositivo mps --lote 128 --guardar-cada-min 10` (medido aquí: 670 a 770 datasets/s en la GPU del Mac, 3,5 GB; en CPU con lote 64, 130/s). PC 2: `cinetica` con `--dispositivo mps --lote 512`. Sigue A-28 (`sismico`) y A-27 (`desgaste`), sin lanzar.
- sáb 13:39 · A-26: ronda 1 lanzada en PC 2 con la partida de Rodrigo. `cinetica` en la GPU del Mac, lote 512, cerca de 8.700 datasets por segundo en el primer minuto. Se detiene sola a las 16:10.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 13:10 · **A PC 3:** por encargo directo de la persona de PC 2 esta sesión editó archivos tuyos: `DECISIONES.md` (D-38), `WORKPLAN.md`, `casos/INICIO` (las cuatro tarjetas descomentadas), las skills y el tablero en vivo (sección nueva que lee `estado/MODELOS.md`). Falta de tu lado: `PC3_SEGUIMIENTO.md` y la columna «Método lento» de `estado/TABLERO.md` todavía suponen el MCMC antes del entrenamiento; con D-38, «Método lento» pendiente no es atraso hasta A-36. Y hay una decisión abierta para las 17:30 al final de `DECISIONES.md` (ronda 2).
- sáb 13:10 · **A PC 1:** el contrato ganó dos cosas opcionales (D-38). `papeles(motor_id)` trae `rangos` (tamaños con que practicó la red y una `frase` lista); un archivo sobre el máximo responde `amarillo` con aviso (submuestra de semilla fija) y bajo el mínimo `rojo_datos` con su motivo. La forma de `analizar` no cambió.
- sáb 13:10 · **A PC 3:** registrar cifras solo cuando haya sello; hoy no hay ninguna nueva.
- sáb 13:32 · **A PC 3 (`WORKPLAN.md` 11.2):** el motor quedó con tres locales continuos (log v_j, log(u_f,j − 1), log A_j) más z_j, no solo (z_j, log(u_f,j − 1)); y el simulador suma un modo común AR(1) que no se infiere (amplitud hasta 0,4 del sector típico): el preprocesamiento lo resta. Agregar esas dos líneas al bloque.
- sáb 13:32 · **A PC 3 (`casos/taludes.yaml`):** `velocidad_fondo` no tiene sentido sin unidades (el motor divide por la escala del archivo) y no sale en «qué pesa». Propuesta: cambiar esa etiqueta por `falta_para_ceder: "Cuánto les falta, en general, a los sectores que se aceleran"`. `ruido` ahora es el error de lectura comparado con el movimiento de fondo.
- sáb 13:50 · **A PC 3 (`WORKPLAN.md` 11.4):** en `desgaste` quedó: «hoy» es la última muestra del camión; lo que falta para la mantención va de 50 a 1.000 horas (el demo trae 750 y el plan decía hasta 500); el segundo local es log(X_hoy + 0,01), no log X_hoy; el camión que ya falló se sortea entero de nuevo (ruta, horas, ritmo y trayectoria); y p_i usa 16 sorteos por muestra, no 64 (son 512 por cada versión de la flota).
- sáb 13:55 · **A PC 3 (`casos/sismicidad.yaml`):** agregar `ventana: 6` en `columnas` (horas observadas desde la tronadura). Sin eso el motor usa la hora del último temblor del archivo (5,94) como ventana.
- sáb 13:55 · **A PC 3 (`WORKPLAN.md` 11.5):** en `sismico` quedó: un dataset con algún sector sobre 300 sismos se descarta y se sortea otro (1,3% con 8 sectores), no se trunca; la tronadura entra como primera lectura de cada sector (tensores de 16 × 301); α se restringe a menos de 0,95·b·ln 10.
- sáb 13:55 · **A PC 3, para la ventana de las 16:10:** la prueba de humo de `sismico` antes de lanzarlo: `uv run python -m motor.sismico.entrenar --minutos 3 --nuevo --dispositivo mps --lote 64 --carpeta motor/checkpoints/sismico_humo` y `uv run python -m motor.sismico.validar --sbc 200 --punto motor/checkpoints/sismico_humo/ultimo.pt`.
- sáb 13:55 · **A PC 1:** las cuatro respuestas de lista ya tienen su forma real (A-29). Diferencias con los ejemplos: en `taludes`, `marca` viene solo en los sectores que probablemente se aceleran; en `sismicidad`, la curva es el acumulado de temblores y `limite` va en `null`; en `flota`, `limite` es 1.

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | `cinetica` (ronda 1, PC 2) |
| Comando exacto | `caffeinate -dims uv run python -m motor.cinetica.entrenar --nuevo --hasta 16:10 --dispositivo mps --lote 512 --guardar-cada-min 10` |
| Hora de inicio | sáb 13:38 |
| Puntos de guardado | `motor/checkpoints/cinetica/ultimo.pt`; registro en `motor/checkpoints/cinetica/salida.log` |
| Para retomar | el mismo comando sin `--nuevo` |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| `leyes`: bloques por color (costos por defecto) | 147 conviene apartar, 568 puede ir a la planta, 309 no sabemos (1.024 bloques) | `api.analizar("leyes")` con la red | 12:05 |
| `leyes`: lo que cuesta no saber | US$ 1.577.707 (supuestos K-22 y K-23) | lo mismo | 12:05 |
| `leyes`: examen | 61 de 68 muestras escondidas dentro del rango de 90% | lo mismo | 12:05 |
| `leyes`: «¿Dónde perforo?» | 480 análisis rehechos; pin A vale US$ 8.943 (neto 7.443), B 8.376, C 7.967 | `api.donde_medir("leyes")` con la red | 12:05 |
| `espacial`: sello | PASA. 7.750.592 terrenos simulados, 280 min, cobertura del 90%: 0,90; 117 s por análisis con el método lento | `motor/artefactos/espacial/sello.json` | 09:39 |
