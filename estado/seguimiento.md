# Estado · seguimiento (PC 3)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 3 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («S-23 terminada: …»): así lo lee el tablero en vivo.
Persona: [nombre] · Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y `WORKPLAN.md`. Instrucciones: `PC3_SEGUIMIENTO.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/seguimiento_hasta_el_pivote.md`.

## Hecho

- sáb 12:40 · S-21 terminada: pivote a minería en el repositorio (D-37). Primera parte: `AGENTS.md`, `GLOSARIO.md`, `WORKPLAN.md`, `contratos/CONTRATO.md` con sus ejemplos, los tres `PC*.md`, `casos/`, `datos/`, `pitch/CIFRAS.md` y el tablero. Segunda parte, en el commit que sigue: guion, láminas, skills, `STACK.md`, archivos de entrega y el tablero en vivo. Lo hizo una sesión de Claude Code en el computador de Rodrigo, a pedido suyo. Ver: `git log` y `estado/TABLERO.md`.
- sáb 12:40 · Investigación de respaldo (dos agentes, fuentes abiertas hoy): cifras de minería con enlace (`pitch/CIFRAS.md`, I-01 en adelante; falta la firma de una persona, S-25) y datos abiertos por caso (`pitch/CIFRAS.md`, «Datos de los casos»).

## En curso

- sáb 12:40 · S-22: una persona avisa a PC 1 y PC 2, detiene `jerarquico` y confirma las cuatro decisiones de D-37. Sigue: S-23 y S-24 (datos reales abiertos).

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor | (ninguno; `jerarquico` se detiene con el pivote: `pkill -INT -f "motor.jerarquico.entrenar"`) |
| Comando exacto | — |
| Hora de inicio | — |

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 12:40 · **A PC 2 (A-21):** `MOTORES` en `nucleo/casos.py` todavía no conoce `deformacion`, `cinetica`, `desgaste` ni `sismico`: por eso `casos/INICIO` lista solo `leyes` y deja las otras cuatro comentadas. Al registrarlos, descomentar esas líneas y ajustar `nucleo/prueba_api.py`.
- sáb 12:40 · **A PC 1 (P-21):** hasta A-21, las cuatro tarjetas nuevas se pintan desde `contratos/ejemplos/casos.json` y `analizar_<caso>.json` (números inventados, rotulados «ejemplo»).
- sáb 12:40 · **A una persona:** las cuatro confirmaciones de D-37 y la clave de Anthropic para Render.

## Rondas

- sáb 12:40 · Pivote. Próxima ronda: 13:15.

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Extraños que repiten la idea, prueba 1 (guion minero) | pendiente: de 3 | S-29 | — |
| Extraños que repiten la idea, prueba 2 | pendiente: de 3 | sáb 19:00 | — |
