# Estado · amortizacion (PC 2)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 2 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («A-23 terminada: …»): así lo lee el tablero en vivo.
Persona: Rodrigo · Dueño de `nucleo/` y `motor/`. Instrucciones: `PC2_AMORTIZACION.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/amortizacion_hasta_el_pivote.md`.

## Hecho

- sáb 12:10 · Antes del pivote, y sigue sirviendo: `motor/comun/` (codificador, flujo, entrenamiento, validación), `nucleo/flujo.py`, `nucleo/decision.py`, `nucleo/tabla.py`, `nucleo/api.py` y el motor `espacial` completo, con su sello (PASA, 09:39). Detalle en `estado/historia/amortizacion_hasta_el_pivote.md`.
- sáb 12:05 · Verificado al preparar el pivote, en este computador y con `estados` entrenando al lado: `KRYLOV_MOTOR_ESPACIAL=red`, `api.analizar("leyes")` responde verde en 0,10 s y `api.donde_medir("leyes")` rehace 480 análisis en 1,0 s. Los tiempos que van al guion se miden de nuevo sin nada entrenando (A-22).

## En curso

- sáb 12:40 · A-21: detener `estados` y registrar los motores nuevos. Sigue: A-22 (sesión B) y A-23 (sesión A).

## Bloqueos

- (ninguno)

## Pedidos a otros

- (ninguno)

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
