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

## En curso

- sáb 04:00 · Siguiente: a las 04:55, S-05b, lanzar `entrenar-motor supervivencia` en este computador.
- sáb 03:49 · Crudo de inasistencias en `datos/crudo/inasistencias/KaggleV2-May-2016.csv` (copia pública del archivo de Kaggle, verificada contra D-03). Listo para S-N1. No se sube (licencia no comercial).
- sáb 03:47 · Grupo `entrenar` instalado y probado: listo para S-05b a las 04:55.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 03:23 · A PC 2: los datos de rotación y del terreno ya están en `main` (`datos/demo/`), con `terreno_grilla.csv`. El terreno puede partir con la distancia al río.
- sáb 03:28 · A PC 2: crédito también está en `main` (`datos/demo/credito.csv`). La respuesta `default` es 0 o 1, y vacía en las 400 por decidir.

## Rondas

| Hora | Qué verifiqué corriendo | Qué cambié en el plan o en el guion |
|---|---|---|
| sáb 03:50 · H0 | `uv sync --group entrenar` y `uv run pytest nucleo motor -q`: 33 pasan (40 s). Los dos repositorios en el mismo commit. Espejo público (API de GitHub). PC 1 sin commits, sin `web/` | D-27: H0 pasa en parte, `h0` espera a P-01. Tablero con la siguiente tarea de cada rol |
| sáb 03:58 · cierre H0 | P-01 de PC 1: `uv run uvicorn servicio.app:app --port 8010` y `npm run dev`; inicio con 4 tarjetas, respuesta de rotación y del terreno; API detenida → «Modo estático» | D-28: tag `h0`. Pitch de 3 minutos (J-04). Orden de tarjetas: manda `casos/INICIO` |
| sáb 04:02 · P-02 | https://krylov-tan.vercel.app/ en navegador con tamaño de teléfono (375×812): inicio, rotación, pie «Modo estático»; `casos.json` 95 ms, `analizar/rotacion.json` 358 ms | `deploy-url` de `platanus-hack-project.jsonc` pasa a la URL de Vercel. Tablero al día |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Casos listos como tarjeta | 0 de 4 (con datos: rotación, terreno y crédito) | `casos/INICIO` y `datos/demo/` | 03:28 |
| Crédito, por decidir | 400 de 2.000; con respuesta 1.600, 23,3% no pagó | `datos/preparar/credito.py` (cifra D-02b) | 03:28 |
| Rotación, por decidir | 294 de 1.470; con respuesta 1.176, 15,6% renunció | `python3 datos/preparar/rotacion.py` (cifra D-01b) | 03:22 |
| Terreno, puntos y grilla | 155 puntos, 3.103 celdas | `Rscript datos/preparar/terreno.R` (D-04, D-04b) | 03:22 |
| Prueba del asistente genérico: respuestas distintas de 3 | sin medir | S-09 | — |
| Extraños que repiten la idea, prueba 1 (12:30) | sin medir | `ensayo-pitch` | — |
| Extraños que repiten la idea, prueba 2 (19:00) | sin medir | `ensayo-pitch` | — |
| Ensayo del pitch, tiempo total | sin medir | `ensayo-pitch` | — |
