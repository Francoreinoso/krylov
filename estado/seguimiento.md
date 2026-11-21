# Estado · seguimiento (PC 3)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 3 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («S-23 terminada: …»): así lo lee el tablero en vivo.
Persona: clementeferrer · Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y `WORKPLAN.md`. Instrucciones: `PC3_SEGUIMIENTO.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/seguimiento_hasta_el_pivote.md`.

## Hecho

- sáb 12:40 · S-21 terminada: pivote a minería en el repositorio (D-37). Primera parte: `AGENTS.md`, `GLOSARIO.md`, `WORKPLAN.md`, `contratos/CONTRATO.md` con sus ejemplos, los tres `PC*.md`, `casos/`, `datos/`, `pitch/CIFRAS.md` y el tablero. Segunda parte, en el commit siguiente: `pitch/` (guion, láminas, hoja de ruta, borradores de entrega), las doce skills, `SKILLS.md`, `STACK.md`, `motor/README.md`, la descripción del proyecto y el tablero en vivo (repositorio `krylov-panel`). Lo hizo una sesión de Claude Code en el computador de Rodrigo, a pedido suyo. Ver: `git log` y `estado/TABLERO.md`.
- sáb 12:40 · Investigación de respaldo (dos agentes, fuentes abiertas hoy): cifras de minería con enlace (`pitch/CIFRAS.md`, I-01 en adelante; falta la firma de una persona, S-25) y datos abiertos por caso (`pitch/CIFRAS.md`, «Datos de los casos»).
- sáb 13:00 · S-27 adelantada: deck minero en `pitch/deck/` con `leyes` como caso estrella, respaldo estático y `pitch/PITCH_v2.md` (356 palabras). Ver: `git log -- pitch/deck`.
- sáb 13:25 · D-38 revisada contra el resto del plan (los archivos que editó PC 2 calzan). Puestos al día con el método lento al final: `PC3_SEGUIMIENTO.md`, `WORKPLAN.md` 6.4 (S-28, S-30, S-32), la skill `ronda`, `estado/TABLERO.md` (columna «Método lento» al final). El tablero en vivo ya lee la tabla nueva (busca las columnas por nombre), y el cambio de `ETAPAS` quedó subido a `krylov-panel` (commit `77294d3`) cuando la cuenta de este computador recibió permiso: «Método lento» va última.
- sáb 13:25 · Decisión abierta de D-38 anotada al final de `DECISIONES.md`: `flota` y `sismicidad` a las 17:30.
- sáb 13:20 · Verificado corriendo, en este computador: A-21 (`uv run pytest nucleo -q`, 34 pasan; `api.analizar("leyes")` verde con la red) y A-23 (`uv run pytest motor/comun/prueba_series.py motor/cinetica -q`, 8 pasan).
- sáb 13:20 · Entorno de entrenamiento listo: `uv sync --group entrenar` hecho, las 8 pruebas pasan y no hay ningún proceso de entrenamiento (`pgrep -fl "motor.*entrenar"` vacío; `jerarquico` ya no corre).
- sáb 13:27 · S-24 terminada (la parte que no depende de PC 2): un archivo de prueba por caso para subir en el chat, `datos/demo/subida_<caso>.csv` con su `_verdad.csv`, para `leyes`, `taludes`, `flotacion`, `flota` y `sismicidad`. Simulados con el mismo generador de cada caso, otra semilla (2027), otro tamaño y otros nombres de columnas y unidades (minutos, porcentaje, hierro en ppm); el calce esperado de cada uno está en la cabecera de `datos/preparar/subida.py`. Un comando: `uv run python datos/preparar/subida.py`. Verificado: `api.analizar_archivo("espacial", subida_leyes.csv, {x: este_m, y: norte_m, valor: arsenico_ppm, umbral: 500})` responde verde en 0,09 s; los otros cuatro quedan dentro de los rangos de tamaño de su motor (20 sectores con 66 a 71 lecturas; 5 líneas con 3 a 5 celdas medidas; 24 camiones con 4 a 10 muestras; 5 sectores con 13 a 32 sismos). Pendiente de A-25, A-27 y A-28: mirarlos contra cada simulador.
- sáb 13:27 · S-23, verificado: el archivo real de sondajes con cobre (`datos/demo/leyes_cobre_real.csv`, 91 sondajes, Zenodo 7051975, CC BY 4.0) responde verde con la red por `analizar_archivo` (x, y, valor = `cu_pct`). Con límite 0,5% deja 954 de 1.024 bloques en «no sabemos»: son sondajes de exploración separados por cientos de metros, no un banco. No se agregó a la tarjeta: sirve como archivo real para subir, y como ejemplo de «sabe cuánto no sabe» con datos reales. El archivo real de taludes (`taludes_real.csv`, 52 prismas con 52 a 130 lecturas) cabe en los rangos de `deformacion`; falta probarlo cuando exista el motor.
- sáb 13:30 · S-26, la parte que no exige a una persona: `pitch/GUION.md` al día con D-38 (qué se dice de cada tarjeta nueva cuando el método lento va al final) y M-44 medido aquí sin nada entrenando. Falta leerlo en voz alta con cronómetro (una persona).
- sáb 13:44 · Ronda 1 lanzada en este computador: `deformacion` entrena hasta las 16:10. La partida la dio la persona de este computador (clementeferrer). Antes: `git pull` con A-25, 44 pruebas pasan (`pytest motor/comun/prueba_series.py motor/deformacion nucleo -q`), `validar --sbc 200` corre sobre una red de 1 minuto (ensayo, no es resultado), enchufado y nada más entrenando.
- sáb 14:00 · Pedidos de PC 2 hechos: `casos/taludes.yaml` (etiqueta `falta_para_ceder` en vez de `velocidad_fondo`, y `ruido` con su sentido nuevo); `WORKPLAN.md` 11.2 (tres locales continuos más z_j; modo común AR(1) que no se infiere), 11.4 («hoy» es la última muestra; mantención de 50 a 1.000 horas; segundo local log(X_hoy + 0,01); el camión que falló se sortea entero; 16 sorteos) y 11.5 (se descarta el dataset con un sector sobre 300 sismos; tensores de 16 × 301; α bajo 0,95·b·ln 10); `pitch/CIFRAS.md` M-54 y M-55 (examen de `leyes` por color y por tramos). Verificado: `pytest nucleo motor/cinetica motor/desgaste motor/sismico -q` pasa.
- sáb 14:00 · `ventana: 6` en `casos/sismicidad.yaml`: **no aplicado**. Con esa línea falla `motor/sismico/prueba_sismico.py::test_fuera_del_rango_es_rojo_datos` (sin ella pasan las 5): `analizar_archivo` hereda la `ventana` del caso base, así que un archivo subido de 0,3 horas se trata como si cubriera 6. Ver pedido a PC 2.
- sáb 13:59 · Ritmo de `deformacion` revisado a los 15 minutos: entre 410 y 540 datasets por segundo (partió en 539; caída cerca de 15%, bajo el 30% que obliga a relanzar). Primer punto de guardado a las 13:53: 276.480 datasets, pérdida de 10,2 a 4,3.

## En curso

- sáb 13:44 · `deformacion` entrenando hasta las 16:10; primer punto de guardado a las 13:54. A las 16:10: S-28 (detener, `validar-motor deformacion` sin método lento, exportar y subir).
- sáb 13:25 · S-22: una persona confirma las decisiones de D-37. Sigue: S-26 (guion contra lo que existe; leerlo en voz alta es de una persona) y S-25 (firmas, una persona). Con la partida y A-25 subida: `medir-rendimiento deformacion` y lanzar `deformacion` aquí hasta las 16:10.

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | `deformacion` (ronda 1), en PC 3 |
| Comando exacto | `caffeinate -dims uv run python -m motor.deformacion.entrenar --hasta 16:10 --dispositivo mps --lote 128 --guardar-cada-min 10 --nuevo`, con la salida en `motor/checkpoints/deformacion/entrenar.log` |
| Dónde corre | En el worktree `.claude/worktrees/pc3-seguimiento-tableros-d4cd0b` de este computador, con el Python de `~/Downloads/krylov/.venv` |
| Puntos de guardado | `motor/checkpoints/deformacion/ultimo.pt`, cada 10 minutos (no se versionan) |
| Para retomar si se cae | El mismo comando sin `--nuevo`: retoma solo desde `ultimo.pt` |
| Para detener | `pkill -INT -f "motor.deformacion.entrenar"` (guarda antes de salir) |
| Hora de inicio | sáb 13:44 |

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 13:25 · **A PC 2 (A-25):** `deformacion` es lo que este computador espera para la ronda 1: avisar en el estado apenas pase su prueba de humo. (El pedido de A-21 quedó resuelto a las 13:02.)
- sáb 13:25 · **A PC 1:** no hay estado nuevo desde las 12:40. Subir P-21 con lo que haya y anotar la hora; H4 solo exige `leyes` en la URL pública (P-22).
- sáb 13:27 · **A PC 1 (P-24):** ya están los archivos de prueba para subir, `datos/demo/subida_<caso>.csv`; el calce esperado de cada uno (con su transformación) está en la cabecera de `datos/preparar/subida.py`. Hoy solo `subida_leyes.csv` responde (verde); los otros cuatro dan `no_disponible` hasta que su red valide. Los `subida_rotacion_*` antiguos se borran cuando PC 2 retire sus pruebas (A-32).
- sáb 13:27 · **A PC 2 (A-25, A-27, A-28):** al tener cada simulador, mirar también `subida_<caso>.csv` y `taludes_real.csv` contra el predictivo a priori, y avisar si alguno cae fuera para regenerarlo.
- sáb 14:00 · **A PC 2 (`nucleo/sismico.py` o `nucleo/api.py`):** pediste `ventana: 6` en `casos/sismicidad.yaml`, pero con esa línea `analizar_archivo("sismico", …)` hereda la ventana del caso base y tu prueba `test_fuera_del_rango_es_rojo_datos` falla (`KeyError: 'semaforo'` en el archivo corto). Dos salidas: que el archivo subido no herede `ventana` (y la tome del calce o del último temblor), o cambiar la prueba. Avisa cuál y agrego la línea al caso en el momento. Mientras tanto el demo usa 5,94 horas en vez de 6.
- sáb 13:25 · **A una persona:** dar la partida de la ronda 1, y a las 17:30 la decisión abierta de D-38 (`DECISIONES.md`).
- sáb 12:40 · **A PC 1 (P-21):** hasta A-21, las cuatro tarjetas nuevas se pintan desde `contratos/ejemplos/casos.json` y `analizar_<caso>.json` (números inventados, rotulados «ejemplo»).
- sáb 12:40 · **A una persona:** las cuatro confirmaciones de D-37 y la clave de Anthropic para Render.
- sáb 12:40 · **A PC 2 (A-32):** `pyproject.toml` todavía describe el proyecto con «cuatro motores»; ajustarlo al retirar los antiguos.

## Rondas

- sáb 12:40 · Pivote. Próxima ronda: 13:15.
- sáb 13:25 · Ronda: A-21 y A-23 verificadas; tablero rehecho con D-38. Próxima ronda: 14:00.

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| `deformacion`: datasets simulados por segundo al entrenar, en este Mac (M3) | GPU del Mac, lote 128: 509; lote 256: 639; procesador, lote 64: 91. Se eligió GPU con lote 128 (más pasos por minuto; es lo que recomendó PC 2). A ese ritmo, cerca de 4,4 millones de muros simulados hasta las 16:10 (estimación) | Tres corridas de 1,2 min con `--minutos 1.2 --nuevo` en una carpeta temporal, sin nada más entrenando | 13:42 |
| `leyes`: «¿Dónde perforo?», 480 análisis rehechos (M-44) | 1,3 s (cinco corridas: 1,30 a 1,48) | `api.donde_medir("leyes")` con la red, MacBook Air M3, sin nada entrenando | 13:27 |
| `leyes`: un análisis completo | 0,007 a 0,008 s | `api.analizar("leyes")`, cinco corridas, lo mismo | 13:27 |
| Extraños que repiten la idea, prueba 1 (guion minero) | pendiente: de 3 | S-29 | — |
| Extraños que repiten la idea, prueba 2 | pendiente: de 3 | sáb 19:00 | — |
