# Estado · seguimiento (PC 3)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 3 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («S-23 terminada: …»): así lo lee el tablero en vivo.
Persona: clementeferrer · Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y `WORKPLAN.md`. Instrucciones: `PC3_SEGUIMIENTO.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/seguimiento_hasta_el_pivote.md`.

## Hecho

- sáb 12:40 · S-21 terminada: pivote a minería en el repositorio (D-37). Primera parte: `AGENTS.md`, `GLOSARIO.md`, `WORKPLAN.md`, `contratos/CONTRATO.md` con sus ejemplos, los tres `PC*.md`, `casos/`, `datos/`, `pitch/CIFRAS.md` y el tablero. Segunda parte, en el commit siguiente: `pitch/` (guion, láminas, hoja de ruta, borradores de entrega), las doce skills, `SKILLS.md`, `STACK.md`, `motor/README.md`, la descripción del proyecto y el tablero en vivo (repositorio `krylov-panel`). Lo hizo una sesión de Claude Code en el computador de Rodrigo, a pedido suyo. Ver: `git log` y `estado/TABLERO.md`.
- sáb 12:40 · Investigación de respaldo (dos agentes, fuentes abiertas hoy): cifras de minería con enlace (`pitch/CIFRAS.md`, I-01 en adelante; falta la firma de una persona, S-25) y datos abiertos por caso (`pitch/CIFRAS.md`, «Datos de los casos»).
- sáb 13:00 · S-27 adelantada: deck minero en `pitch/deck/` con `leyes` como caso estrella, respaldo estático y `pitch/PITCH_v2.md` (356 palabras). Ver: `git log -- pitch/deck`.
- sáb 13:25 · D-38 revisada contra el resto del plan (los archivos que editó PC 2 calzan). Puestos al día con el método lento al final: `PC3_SEGUIMIENTO.md`, `WORKPLAN.md` 6.4 (S-28, S-30, S-32), la skill `ronda`, `estado/TABLERO.md` (columna «Método lento» al final). El tablero en vivo ya lee la tabla nueva (busca las columnas por nombre), pero sigue dibujando «Método lento» tercera: el cambio de `ETAPAS` está hecho y sin subir (ver Bloqueos).
- sáb 13:25 · Decisión abierta de D-38 anotada al final de `DECISIONES.md`: `flota` y `sismicidad` a las 17:30.
- sáb 13:20 · Verificado corriendo, en este computador: A-21 (`uv run pytest nucleo -q`, 34 pasan; `api.analizar("leyes")` verde con la red) y A-23 (`uv run pytest motor/comun/prueba_series.py motor/cinetica -q`, 8 pasan).
- sáb 13:20 · Entorno de entrenamiento listo: `uv sync --group entrenar` hecho, las 8 pruebas pasan y no hay ningún proceso de entrenamiento (`pgrep -fl "motor.*entrenar"` vacío; `jerarquico` ya no corre).

## En curso

- sáb 13:25 · S-22: una persona da la partida de la ronda 1 y confirma las decisiones de D-37. Sigue: S-24 (archivos `subida_*.csv`), S-25, S-26. Con la partida y A-25 subida: `medir-rendimiento deformacion` y lanzar `deformacion` aquí hasta las 16:10.

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | (ninguno: nada se lanza hasta que el equipo dé la partida; después, `deformacion` en la ronda 1 y `sismico` en la ronda 2) |
| Comando exacto | Pendiente de A-25 y de `medir-rendimiento`: `caffeinate -dims uv run python -m motor.deformacion.entrenar --dispositivo <cpu o mps> --hasta 16:10 --guardar-cada-min 10` |
| Hora de inicio | — |

## Bloqueos

- sáb 13:30 · Tablero en vivo: el `git push` a `Silent-math/krylov-panel` fue denegado para la cuenta de este computador (403). No se forzó. Falta que quien tiene permiso aplique el cambio de una línea en `index.html`: en `ETAPAS`, mover `['lento','Método lento']` al final de la lista (y lo mismo en las líneas 16 y 30 del README).

## Pedidos a otros

- sáb 13:25 · **A PC 2 (A-25):** `deformacion` es lo que este computador espera para la ronda 1: avisar en el estado apenas pase su prueba de humo. (El pedido de A-21 quedó resuelto a las 13:02.)
- sáb 13:25 · **A PC 1:** no hay estado nuevo desde las 12:40. Subir P-21 con lo que haya y anotar la hora; H4 solo exige `leyes` en la URL pública (P-22).
- sáb 13:30 · **A PC 2 (o a quien tenga permiso en `Silent-math/krylov-panel`):** mover «Método lento» al final de `ETAPAS` en `index.html` (detalle en Bloqueos).
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
| Extraños que repiten la idea, prueba 1 (guion minero) | pendiente: de 3 | S-29 | — |
| Extraños que repiten la idea, prueba 2 | pendiente: de 3 | sáb 19:00 | — |
