# Estado · seguimiento (PC 3)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 3 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago.
Persona: [nombre] · Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y `WORKPLAN.md`. Instrucciones: `PC3_SEGUIMIENTO.md`.

## Hecho

- sáb 03:00 · Plan final generado.
- sáb 03:20 · S-01 (lo hizo el computador del plan, commit 1b740ac). PC 3 clonado en `~/Downloads/krylov`, push a los dos repositorios comprobado: los dos en 28837dd. Verificar: `git ls-remote origin main; git ls-remote https://github.com/Silent-math/krylov.git main`.
- sáb 03:22 · S-03, rotación: `datos/demo/rotacion.csv` (1.470 filas, las 35 columnas, 294 respuestas vacías al azar con semilla 2026) y `rotacion_verdad.csv` (294 filas, `id`, `objetivo`). Las dos clases quedan presentes. Comando: `python3 datos/preparar/rotacion.py` (el crudo se baja con el `curl` del encabezado del script). Columnas del YAML verificadas contra el archivo.
- sáb 03:22 · S-04, terreno: `datos/demo/terreno.csv` (155 filas, `x`, `y`, `zinc`, `dist`; 33 sobre 720 mg/kg) y `terreno_grilla.csv` (3.103 celdas, `x`, `y`, `dist`). Comando: `Rscript datos/preparar/terreno.R` (R con `sp` 2.1.4, sin descargas). Los 155 puntos caen dentro de la grilla; su `dist` coincide con la de la celda más cercana (diferencia máxima 0,033).
- sáb 03:23 · `uv` 0.13.9 instalado (para `uv sync --group entrenar` a las 04:55).
- sáb 03:55 · S-02: la organización respondió (`pitch/VALIDACION.md`): pitch de 3 minutos, computador propio con audio y video. Cifra J-04 actualizada.
- sáb 04:00 · **H0 cerrado**, tag `h0` en los dos repositorios (D-28). P-01 verificado corriendo: API local en el puerto 8010, web en 5173, inicio y respuestas fijas; con la API detenida, modo estático.
- sáb 03:28 · S-05, crédito (adelantado): `datos/demo/credito.csv` (muestra de 2.000 de 30.000, las 25 columnas con los seis meses de `PAY_*`, `BILL_AMT*` y `PAY_AMT*`, 400 respuestas vacías al azar) y `credito_verdad.csv` (400 filas). Las dos clases quedan presentes. Comando: `uv run --no-project --with pandas --with xlrd python datos/preparar/credito.py` (el crudo se baja con los comandos del encabezado del script).

- sáb 04:45 · **S-N1, inasistencias** (adelantado, D-29): `datos/preparar/inasistencias.py` deja `datos/demo/inasistencias.csv` (1.980 citas, 1.147 pacientes, 30 barrios con 66 citas cada uno, 38% de pacientes con 2 o más citas, 396 por decidir) e `inasistencias_verdad.csv`. Los dos en `.gitignore` (licencia no comercial). Sale idéntico en dos corridas (md5). Columnas verificadas contra `casos/inasistencias.yaml` (parte de S-07; falta ver la tarjeta respondiendo, cuando exista `jerarquico`).
- sáb 04:45 · **S-08, archivo malo**: `datos/preparar/rotacion_malo.py` deja `datos/demo/rotacion_malo.csv` (1.470 filas, 36 columnas): `fecha_salida` tiene fecha solo para las 237 que renunciaron, incluidas 54 de las 294 por decidir. Comando: `python3 datos/preparar/rotacion_malo.py`.
- sáb 04:46 · **S-N3**: borradores `pitch/README_borrador.md` (técnico, con los nombres precisos) y `pitch/descripcion_borrador.md`. No tocan el `README.md` de la organización. Los lee una persona en la mañana.
- sáb 04:49 · **S-N2**: lo que dice hoy cada fuente, en `pitch/CIFRAS.md`, sección «Revisión de fuentes». Sin firmar «Verificó». Para una persona: C-02 (el 96% no está en el INE: es 91,8%), P-01 (hoy solo se verifica «+6.000») y N-01 (fechas solo en la biografía; la Marina no adoptó las tablas entonces). Ninguna de las tres está hoy en el guion.
- sáb 04:51 · **S-11, textos de pantalla v1** (adelantado): `casos/textos.yaml`, las plantillas del contrato (sección 5) para titulares, `en_palabras`, motivos del semáforo, examen, sello, «¿Dónde mido?», nube, cartera y deslizadores. Falta la parte de S-11 que exige a una persona: el guion v1 en voz alta y cronometrado.
- sáb 05:03 · **S-12, esqueleto de láminas** (adelantado): `pitch/LAMINAS.md` con el texto de portada y cierre para PC 1 (P-13) y las tres de respaldo (técnica, negocio, qué existe y qué es hoja de ruta). Cada número con su id de `CIFRAS.md`; lo no medido, entre corchetes.
- sáb 05:03 · Ronda: P-N1 de PC 1 verificado (`npm run prueba`: 45 pasan). PC 2: `uv run pytest nucleo/prueba_decision.py nucleo/prueba_api.py nucleo/prueba_nube.py nucleo/prueba_espacial.py -q`: 15 pasan; `api.casos()` sigue el orden de `casos/INICIO`; `api.analizar("terreno")` responde `no_disponible` (esperado hasta la red validada). `supervivencia`: 2,8 millones de datasets, punto de guardado 04:55.
- sáb 05:14 · Ronda: el rediseño de PC 1 (tema oscuro, mapa P-N2, nube P-N3, deslizadores) revisado a 1280×720 en modo estático con `?caso=rotacion`, `?caso=terreno` y `?caso=rotacion_malo`: se ven bien. Dos pedidos a PC 1 (abajo). PC 2 dejó `estados` listo para entrenar en PC 2 cuando quede libre. `supervivencia`: 3,3 millones de datasets, punto de guardado 05:05.
- sáb 05:14 · `etiquetas` (nombre en pantalla de cada columna) en los cinco YAML de `casos/`, a pedido de PC 2; `nucleo/estados.py` ya las lee. D-30 registra eso y el cambio de `estados` a 33 parámetros (atraso en 5 niveles), también en `WORKPLAN.md` 11.4, `pitch/LAMINAS.md` y el borrador del README.
- sáb 05:23 · Ronda: `jerarquico` de PC 2 corre en PC 3 con el archivo real (que solo está aquí). Predictivo a priori contra `datos/demo/inasistencias.csv`: los 7 resúmenes caen entre los percentiles 30 y 64 de 1.000 carteras simuladas (ver Números medidos); 14 s a baja prioridad. Pruebas: `uv run pytest nucleo/prueba_jerarquico.py motor/jerarquico/prueba_jerarquico.py -q`: 6 pasan. `supervivencia`: 3,8 millones de datasets, punto de guardado 05:15.
- sáb 05:23 · Parte de S-11 sin persona: tiempo estimado del guion de 3 minutos contando palabras (150 por minuto): 176 s de habla, sin clics: no cabe. El momento 2 se pasa (49 s contra 35). Recorte propuesto escrito en `pitch/GUION.md`; lo decide quien presenta en el primer ensayo.
- sáb 05:36 · Ronda: SBC intermedio de `supervivencia` sobre el punto de guardado de los 83 minutos (`uv run python -m motor.supervivencia.validar --sbc 200`, 4 s): cobertura 0,904, peor grupo 0,898, contracción 0,74, 15 de 32 con KS sobre el límite. No pasa todavía: sigue hasta las 08:30 (D-31). Pérdida media por tramo de 10 min: −8,8 (40-50) → −10,3 (80-90). `jerarquico` de PC 2: 20 parámetros, anotado en `WORKPLAN.md` 11.3.
- sáb 05:51 · Ronda: `nucleo/textos.py` de PC 2 ya llena las plantillas de `casos/textos.yaml`. Arreglé las dos que salían mal (pedido de PC 2 de las 05:50): el examen pasa a «Cuando dijimos cerca de 30% de riesgo, se fue el 28%» (sin artículo, sirve para personas, clientes y citas, como en `GLOSARIO.md`); se agregan variantes en singular (`hay_actuar_una`, `hay_en_duda_una`); en el terreno, «no hace falta limpiar» deja de tener frase para que quepa «qué manda». Rótulo del terreno mixto (mapa de la red, «qué manda» del MCMC): `precalculado.pie_espacial_mixto`. `uv run pytest nucleo -q`: 23 pasan y 1 falla, la línea 99 de `nucleo/prueba_api.py`, que compara con el texto viejo del examen (pedido a PC 2). `supervivencia`: 5,1 millones de datasets, punto de guardado 05:45.
- sáb 06:05 · Ronda: `uv run pytest nucleo -q`: 24 pasan (PC 2 cambió su prueba de textos para comprobar números, no redacción). `jerarquico` exporta en el M3: `uv run python -m motor.jerarquico.exportar --prueba` da ONNX contra `torch` hasta 1,4e-6 y flujo NumPy contra `torch` 4,8e-7 (7 s). S-09 dejado listo para una persona: archivo, pregunta exacta y criterio de «respuestas distintas» fijados en `pitch/VALIDACION.md` antes de ver resultados. `supervivencia`: 5,8 millones de datasets, punto de guardado 05:55, pérdida media −12,4. PC 1 sin commits desde las 05:04.
- sáb 04:05 · S-05b, prueba de humo de `supervivencia` en el M3 (adelantada, a pedido de la persona): 3 minutos, 142.400 datasets, pérdida (media móvil) de 37 a 8,9, punto de guardado escrito. SBC de 200: cobertura del 90% en 0,906, contracción media 0,53, 8 de 32 parámetros con KS sobre el límite (todavía no calibra; es lo esperado a los 3 minutos).

## En curso

- sáb 04:05 · **S-05b: `supervivencia` entrena en este computador hasta las 08:30** (adelantada desde las 04:55). Ver la tabla «Entrenamiento en curso».
- sáb 05:03 · Siguiente: S-N4 (rondas de lectura a las 06:15, 07:15 y 08:15, programadas en esta sesión). Lo que queda de mi lista antes de las 08:15 exige a una persona (S-09, S-10, guion en voz alta) o números de los motores (S-15).

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | `supervivencia`, en PC 3 (MacBook Air M3, 16 GB), enchufado |
| Comando exacto | `cd ~/Downloads/krylov && nohup caffeinate -dims uv run python -m motor.supervivencia.entrenar --dispositivo cpu --hasta 08:30 --guardar-cada-min 10 > motor/checkpoints/supervivencia/corrida.log 2>&1 < /dev/null &` (desacoplado: sigue aunque se cierre Claude Code o la terminal) |
| Hora de inicio | sáb 04:05, retomando desde el paso 4.450 de la prueba de humo |
| Puntos de guardado | `motor/checkpoints/supervivencia/ultimo.pt`, cada 10 minutos; avance en `registro.jsonl`; salida en `corrida.log` |
| Mirar cómo va | `tail -n 1 motor/checkpoints/supervivencia/registro.jsonl` |
| Si se cae | El mismo comando. La primera línea de `corrida.log` tiene que decir `[retomar] … paso N`. Nunca `--nuevo` |
| Detener antes de las 08:30 | `pkill -INT -f "motor.supervivencia.entrenar"` (guarda y sale). A las 08:30 se detiene solo |
| Siguiente entrenamiento (S-06b, 08:30) | `jerarquico`, hasta las 11:30: `git pull`, comprobar que `supervivencia` terminó (`pgrep -f motor.supervivencia.entrenar` no devuelve nada), y `nohup caffeinate -dims uv run python -m motor.jerarquico.entrenar --dispositivo cpu --hasta 11:30 --guardar-cada-min 10 > motor/checkpoints/jerarquico/corrida.log 2>&1 < /dev/null &` (crear antes `motor/checkpoints/jerarquico/`). Exportación probada en el M3 a las 06:05 |
| Después (S-06b, 08:30) | **Primero `git pull`** (desde las 05:11 `exportar_onnx` deja un solo `codificador.onnx`, con los pesos dentro). Después `uv run python -m motor.supervivencia.exportar` y subir `motor/artefactos/supervivencia/` (pasos 7 y 8 de `estado/amortizacion.md`) |

## Lista nocturna de PC 3 (el agente solo, 05:15 a 08:15)

Regla: solo esto, solo en `casos/`, `datos/`, `pitch/` y `estado/`, commits chicos, sin desplegar, sin enviar nada a nadie. **`supervivencia` entrena en este computador: no se toca el proceso y no se lanza nada que le quite el procesador más de un par de minutos** (nada de MCMC, entrenamientos ni compilaciones). Si algo exige una decisión, se anota aquí y se pasa a lo siguiente.

1. **S-N1 · inasistencias.** `datos/preparar/inasistencias.py` sobre `datos/crudo/inasistencias/KaggleV2-May-2016.csv`: calcula `dias_de_espera` y `dia_semana`, descarta edades y esperas negativas y los sábados, elige 30 barrios con semilla fija y, dentro de ellos, pacientes completos hasta unas 2.000 citas, con al menos un tercio de los pacientes con dos o más citas. Deja vacía al azar el 20% de las respuestas y guarda la verdad aparte. **El CSV no se sube** (ya está en `.gitignore`); el script sí. Comprobar las columnas contra `casos/inasistencias.yaml`.
2. **S-N2 · fuentes de las cifras.** Abrir cada enlace de `pitch/CIFRAS.md` (lista en `WORKPLAN.md`, sección 12) y anotar en una columna aparte lo que dice la página hoy. No se firma «Verificó»: eso lo hace una persona en S-10.
3. **S-N3 · entrega en borrador.** Borrador de `project-description.md` y de la estructura del README, sin cifras que no estén en `pitch/CIFRAS.md`. **No tocar la línea del README dirigida a modelos de lenguaje:** queda como decisión pendiente para S-16.
4. **S-N4 · ronda de lectura cada hora** (06:15, 07:15, 08:15): `git pull --rebase`, leer los estados de PC 1 y PC 2 y la última línea de `motor/checkpoints/supervivencia/registro.jsonl`. Si alguien dejó un bloqueo, o el entrenamiento dejó de escribir puntos de guardado, destacarlo arriba en el tablero para las 08:15.
5. **Después, por D-29, las tareas de día que no exigen a una persona ni procesador pesado, en orden:** S-07 (revisar el caso de inasistencias contra su YAML) y S-08 (archivo malo: `datos/demo/rotacion_malo.csv`, rotación más `fecha_salida` solo para quienes renunciaron, declarada en `columnas.extra` de `casos/rotacion_malo.yaml`). S-09 y S-10 exigen a una persona: no se hacen de noche.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 03:23 · A PC 2: los datos de rotación y del terreno ya están en `main` (`datos/demo/`), con `terreno_grilla.csv`. El terreno puede partir con la distancia al río.
- sáb 03:28 · A PC 2: crédito también está en `main` (`datos/demo/credito.csv`). La respuesta `default` es 0 o 1, y vacía en las 400 por decidir.
- sáb 04:47 · A PC 2: `datos/demo/rotacion_malo.csv` está en `main`. `fecha_salida` es texto (AAAA-MM-DD) o vacío: lo que delata la respuesta es si está o no, así que el eje «mejor factor por sí solo» de la nube tiene que tratar el vacío como un valor.
- sáb 04:47 · A PC 2: inasistencias no está en el repositorio (licencia no comercial). Si lo necesitas en PC 2 para el predictivo a priori de `jerarquico`, el encabezado de `datos/preparar/inasistencias.py` trae el `curl` y el SHA-256; sale idéntico. En PC 3 ya está, para entrenar y validar `jerarquico` aquí.
- sáb 05:14 · A PC 1: en el estado rojo (`?caso=rotacion_malo`) el pie dice «Respondió la red que practicó con casos simulados», pero ahí Krylov no responde: en rojo, ese pie no va.
- sáb 05:14 · A PC 1: los rótulos de los ejes de la nube son muy chicos para el proyector (ejes con nombre, momento 3 del guion). Más grandes, y horizontales si caben.
- sáb 05:14 · A PC 2: hecho tu pedido de las 05:11: `etiquetas` está en `casos/credito.yaml` y en los otros cuatro casos.
- sáb 05:23 · A PC 2: corrí tu `motor.jerarquico.simular --revisar` aquí, con el archivo real: calza (percentiles 30 a 64; detalle en Números medidos). Si cambias el prior, avísame y lo vuelvo a correr: son 14 segundos.
- sáb 05:36 · A PC 2, sesión B: SBC intermedio de `supervivencia` a los 83 min: cobertura 0,904, contracción 0,74, pero KS sobre el límite en log_k, beta0, lambda, log_a_2, log_a_3, mu_c y nueve cortes de las encuestas (`motor/checkpoints/supervivencia/sbc.json` en PC 3). Para tu prueba de los nodos de la cuadratura del cargo: el archivo real está en el repositorio.
- sáb 05:51 · A PC 2: `casos/textos.yaml` corregido. Cambia una línea de tu prueba: `nucleo/prueba_api.py:99` tiene que esperar «Cuando dijimos cerca de 30% de riesgo, se fue el 28%.». Para las variantes en singular: si `n_actuar == 1` usa `en_palabras.hay_actuar_una` (y `espacial.hay_actuar_una`), lo mismo con `hay_en_duda_una`, pasando `unidad_singular`. `espacial.hay_no_actuar` ya no existe: tu código lo descarta solo.
- sáb 05:51 · A PC 2, el rótulo que me pediste: con `KRYLOV_ESPACIAL_THETA=mcmc`, la tarjeta del terreno no se rotula entera «precalculado»; «qué manda en el terreno» lleva «precalculado» y el pie dice `precalculado.pie_espacial_mixto` de `casos/textos.yaml`. Nunca se dice que «qué manda» lo respondió la red (orden de corte n.º 4).
- sáb 04:51 · A PC 2: las plantillas de texto están en `casos/textos.yaml` (contrato, sección 5: las escribe `seguimiento`). `nucleo/api.py` arma hoy el titular con un f-string; que lea la plantilla de ahí. El titular de verde dice lo mismo que el tuyo.
- sáb 04:36 · A PC 2 (respuesta a tu pedido de las 04:00): `supervivencia` corre en PC 3 desde las 04:05 y termina sola a las 08:30. A las 08:30 PC 3 exporta y sube (paso 7).

## Rondas

| Hora | Qué verifiqué corriendo | Qué cambié en el plan o en el guion |
|---|---|---|
| sáb 03:50 · H0 | `uv sync --group entrenar` y `uv run pytest nucleo motor -q`: 33 pasan (40 s). Los dos repositorios en el mismo commit. Espejo público (API de GitHub). PC 1 sin commits, sin `web/` | D-27: H0 pasa en parte, `h0` espera a P-01. Tablero con la siguiente tarea de cada rol |
| sáb 03:58 · cierre H0 | P-01 de PC 1: `uv run uvicorn servicio.app:app --port 8010` y `npm run dev`; inicio con 4 tarjetas, respuesta de rotación y del terreno; API detenida → «Modo estático» | D-28: tag `h0`. Pitch de 3 minutos (J-04). Orden de tarjetas: manda `casos/INICIO` |
| sáb 04:02 · P-02 | https://krylov-tan.vercel.app/ en navegador con tamaño de teléfono (375×812): inicio, rotación, pie «Modo estático»; `casos.json` 95 ms, `analizar/rotacion.json` 358 ms | `deploy-url` de `platanus-hack-project.jsonc` pasa a la URL de Vercel. Tablero al día |
| sáb 04:36 | `supervivencia` en PC 3: paso 49.470, 1,58 millones de datasets, punto de guardado a las 04:35:33, sin errores en `corrida.log`, `caffeinate` activo, enchufado. PC 1: P-03 sin commit desde las 03:59 (vence 05:00). PC 2: lista nocturna todavía sin escribir (A-05 es a las 05:10) | Guion: versión de 3 minutos como principal; «294 personas reales» → «la respuesta de 294 personas del archivo» (el archivo es ficticio). Tablero: aviso de `codificador.onnx.data` copiado a PC 1. Lista nocturna de PC 3 escrita |
| sáb 04:38 · P-03 | `npm ci` (dependencia nueva de fuente) y `npm run dev`, `/?estatico=1`: tarjetas en el orden de `casos/INICIO`; rotación con lista de más a menos riesgo, punto de corte 20%, «qué pesa» con etiquetas y pie. `supervivencia`: 1,74 millones de datasets | Tablero: P-03 hecho, aviso de `npm ci`, la tarea siguiente y la que viene después. D-29 cambió dos veces (04:35 los tres, 04:36 solo PC 2, 04:38 los tres): queda para los tres; la lista nocturna de PC 3 sigue con S-07 y S-08 |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Casos listos como tarjeta | 0 de 4 (con datos: rotación, terreno y crédito) | `casos/INICIO` y `datos/demo/` | 03:28 |
| Crédito, por decidir | 400 de 2.000; con respuesta 1.600, 23,3% no pagó | `datos/preparar/credito.py` (cifra D-02b) | 03:28 |
| Rotación, por decidir | 294 de 1.470; con respuesta 1.176, 15,6% renunció | `python3 datos/preparar/rotacion.py` (cifra D-01b) | 03:22 |
| Terreno, puntos y grilla | 155 puntos, 3.103 celdas | `Rscript datos/preparar/terreno.R` (D-04, D-04b) | 03:22 |
| `supervivencia` en el M3: pasos de entrenamiento por segundo, CPU, lote 32 | 22 a 28 (unos 800 datasets por segundo); nada más entrenando | `registro.jsonl` de la prueba de humo | 04:05 |
| `supervivencia` en el M3: SBC chico a los 3 minutos | cobertura del 90% en 0,906; contracción media 0,53; 8 de 32 con KS sobre el límite | `uv run python -m motor.supervivencia.validar --sbc 200` | 04:05 |
| `jerarquico`: predictivo a priori contra el archivo real (1.980 citas) | No llega 0,210 → percentil 45 (simulado 0,05 a 0,54); mismo día 0,048 → 30; otro día 0,292 → 51; con SMS 0,266 → 47; citas del mismo día 0,333 → 54; con SMS 0,324 → 54; citas por paciente 1,73 → 64 | `uv run python -m motor.jerarquico.simular --revisar` (1.000 carteras simuladas) | 05:23 |
| `supervivencia`: SBC intermedio a los 83 min (3,9 millones de datasets) | Cobertura del 90%: 0,904 (peor grupo 0,898); contracción media 0,74; 15 de 32 con KS sobre el límite | `uv run python -m motor.supervivencia.validar --sbc 200` | 05:36 |
| Prueba del asistente genérico: respuestas distintas de 3 | sin medir | S-09 | — |
| Extraños que repiten la idea, prueba 1 (12:30) | sin medir | `ensayo-pitch` | — |
| Extraños que repiten la idea, prueba 2 (19:00) | sin medir | `ensayo-pitch` | — |
| Ensayo del pitch, tiempo total | sin medir | `ensayo-pitch` | — |
