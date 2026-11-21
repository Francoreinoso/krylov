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

- sáb 04:05 · S-05b, prueba de humo de `supervivencia` en el M3 (adelantada, a pedido de la persona): 3 minutos, 142.400 datasets, pérdida (media móvil) de 37 a 8,9, punto de guardado escrito. SBC de 200: cobertura del 90% en 0,906, contracción media 0,53, 8 de 32 parámetros con KS sobre el límite (todavía no calibra; es lo esperado a los 3 minutos).

## En curso

- sáb 04:05 · **S-05b: `supervivencia` entrena en este computador hasta las 08:30** (adelantada desde las 04:55). Ver la tabla «Entrenamiento en curso».
- sáb 03:49 · Crudo de inasistencias en `datos/crudo/inasistencias/KaggleV2-May-2016.csv` (copia pública del archivo de Kaggle, verificada contra D-03). Listo para S-N1. No se sube (licencia no comercial).

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
| Después (S-06b, 08:30) | `uv run python -m motor.supervivencia.exportar` y subir `motor/artefactos/supervivencia/` (pasos 7 y 8 de `estado/amortizacion.md`) |

## Lista nocturna de PC 3 (el agente solo, 05:15 a 08:15)

Regla: solo esto, solo en `casos/`, `datos/`, `pitch/` y `estado/`, commits chicos, sin desplegar, sin enviar nada a nadie. **`supervivencia` entrena en este computador: no se toca el proceso y no se lanza nada que le quite el procesador más de un par de minutos** (nada de MCMC, entrenamientos ni compilaciones). Si algo exige una decisión, se anota aquí y se pasa a lo siguiente.

1. **S-N1 · inasistencias.** `datos/preparar/inasistencias.py` sobre `datos/crudo/inasistencias/KaggleV2-May-2016.csv`: calcula `dias_de_espera` y `dia_semana`, descarta edades y esperas negativas y los sábados, elige 30 barrios con semilla fija y, dentro de ellos, pacientes completos hasta unas 2.000 citas, con al menos un tercio de los pacientes con dos o más citas. Deja vacía al azar el 20% de las respuestas y guarda la verdad aparte. **El CSV no se sube** (ya está en `.gitignore`); el script sí. Comprobar las columnas contra `casos/inasistencias.yaml`.
2. **S-N2 · fuentes de las cifras.** Abrir cada enlace de `pitch/CIFRAS.md` (lista en `WORKPLAN.md`, sección 12) y anotar en una columna aparte lo que dice la página hoy. No se firma «Verificó»: eso lo hace una persona en S-10.
3. **S-N3 · entrega en borrador.** Borrador de `project-description.md` y de la estructura del README, sin cifras que no estén en `pitch/CIFRAS.md`. **No tocar la línea del README dirigida a modelos de lenguaje:** queda como decisión pendiente para S-16.
4. **S-N4 · ronda de lectura cada hora** (06:15, 07:15, 08:15): `git pull --rebase`, leer los estados de PC 1 y PC 2 y la última línea de `motor/checkpoints/supervivencia/registro.jsonl`. Si alguien dejó un bloqueo, o el entrenamiento dejó de escribir puntos de guardado, destacarlo arriba en el tablero para las 08:15.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 03:23 · A PC 2: los datos de rotación y del terreno ya están en `main` (`datos/demo/`), con `terreno_grilla.csv`. El terreno puede partir con la distancia al río.
- sáb 03:28 · A PC 2: crédito también está en `main` (`datos/demo/credito.csv`). La respuesta `default` es 0 o 1, y vacía en las 400 por decidir.
- sáb 04:36 · A PC 2 (respuesta a tu pedido de las 04:00): `supervivencia` corre en PC 3 desde las 04:05 y termina sola a las 08:30. A las 08:30 PC 3 exporta y sube (paso 7).

## Rondas

| Hora | Qué verifiqué corriendo | Qué cambié en el plan o en el guion |
|---|---|---|
| sáb 03:50 · H0 | `uv sync --group entrenar` y `uv run pytest nucleo motor -q`: 33 pasan (40 s). Los dos repositorios en el mismo commit. Espejo público (API de GitHub). PC 1 sin commits, sin `web/` | D-27: H0 pasa en parte, `h0` espera a P-01. Tablero con la siguiente tarea de cada rol |
| sáb 03:58 · cierre H0 | P-01 de PC 1: `uv run uvicorn servicio.app:app --port 8010` y `npm run dev`; inicio con 4 tarjetas, respuesta de rotación y del terreno; API detenida → «Modo estático» | D-28: tag `h0`. Pitch de 3 minutos (J-04). Orden de tarjetas: manda `casos/INICIO` |
| sáb 04:02 · P-02 | https://krylov-tan.vercel.app/ en navegador con tamaño de teléfono (375×812): inicio, rotación, pie «Modo estático»; `casos.json` 95 ms, `analizar/rotacion.json` 358 ms | `deploy-url` de `platanus-hack-project.jsonc` pasa a la URL de Vercel. Tablero al día |
| sáb 04:36 | `supervivencia` en PC 3: paso 49.470, 1,58 millones de datasets, punto de guardado a las 04:35:33, sin errores en `corrida.log`, `caffeinate` activo, enchufado. PC 1: P-03 sin commit desde las 03:59 (vence 05:00). PC 2: lista nocturna todavía sin escribir (A-05 es a las 05:10) | Guion: versión de 3 minutos como principal; «294 personas reales» → «la respuesta de 294 personas del archivo» (el archivo es ficticio). Tablero: aviso de `codificador.onnx.data` copiado a PC 1. Lista nocturna de PC 3 escrita |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Casos listos como tarjeta | 0 de 4 (con datos: rotación, terreno y crédito) | `casos/INICIO` y `datos/demo/` | 03:28 |
| Crédito, por decidir | 400 de 2.000; con respuesta 1.600, 23,3% no pagó | `datos/preparar/credito.py` (cifra D-02b) | 03:28 |
| Rotación, por decidir | 294 de 1.470; con respuesta 1.176, 15,6% renunció | `python3 datos/preparar/rotacion.py` (cifra D-01b) | 03:22 |
| Terreno, puntos y grilla | 155 puntos, 3.103 celdas | `Rscript datos/preparar/terreno.R` (D-04, D-04b) | 03:22 |
| `supervivencia` en el M3: pasos de entrenamiento por segundo, CPU, lote 32 | 22 a 28 (unos 800 datasets por segundo); nada más entrenando | `registro.jsonl` de la prueba de humo | 04:05 |
| `supervivencia` en el M3: SBC chico a los 3 minutos | cobertura del 90% en 0,906; contracción media 0,53; 8 de 32 con KS sobre el límite | `uv run python -m motor.supervivencia.validar --sbc 200` | 04:05 |
| Prueba del asistente genérico: respuestas distintas de 3 | sin medir | S-09 | — |
| Extraños que repiten la idea, prueba 1 (12:30) | sin medir | `ensayo-pitch` | — |
| Extraños que repiten la idea, prueba 2 (19:00) | sin medir | `ensayo-pitch` | — |
| Ensayo del pitch, tiempo total | sin medir | `ensayo-pitch` | — |
