# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 13:25 · **Hito vigente:** camino a H4, 14:30 · **Producto terminado: sáb 18:00** · Tope de redes: 20:30

**URL pública:** https://krylov-tan.vercel.app/ (todavía muestra las cuatro tarjetas anteriores; cambia con P-21 y P-22).

**Manda D-38 (13:10), sobre D-37:** el método lento de cada motor se corre **al final** (A-36), y cada modelo sortea el tamaño del dataset. Una red se lanza y se valida sin esperarlo. **Nada está entrenando y nada se lanza hasta que el equipo dé la partida.** El detalle pieza por pieza de cada motor está en `estado/MODELOS.md`.

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`. **«Método lento» va al final (D-38): `pendiente` ahí no es atraso hasta A-36.**

| Caso | Motor | Datos | Simulador | Red | Sello | En la app | Método lento | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | listo | listo | pendiente | pendiente | red |
| taludes | deformacion | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |
| flotacion | cinetica | listo | listo | pendiente | pendiente | pendiente | pendiente | ejemplo |
| flota | desgaste | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |
| sismicidad | sismico | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |

Verificado en PC 3 a las 13:20, corriendo: `pytest nucleo` pasa (34) y `leyes` responde verde con la red (**A-21 terminada**); `pytest motor/comun/prueba_series.py motor/cinetica` pasa (8): el andamio de series existe (**A-23 terminada**) y `cinetica` tiene simulador y red sin entrenar, a falta de su prueba de humo (A-24). Las cuatro tarjetas nuevas responden `no_disponible` y la web pinta su ejemplo.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 sin noticias | P-21 pasó su tope (13:10) y no hay estado nuevo desde las 12:40. Si a las 13:50 no está, lleva el doble: subir lo que haya |
| amortizacion (PC 2) | 🟢 adelantado | A-21 y A-23 terminadas; `cinetica` casi lista. Falta `deformacion` (A-25), que es lo que PC 3 necesita para la ronda 1 |
| seguimiento (PC 3) | 🟢 al día | Plan y tablero al día con D-38; entorno de entrenamiento listo y probado. Espera A-25 y la partida |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-21** (cinco tarjetas mineras, cuatro con su ejemplo rotulado): subirla con lo que haya. Después **P-22**, tope 13:50: `leyes` real con la red y «¿Dónde perforo?» en la URL pública; es lo único que H4 exige de PC 1. Después **P-23** (`Curva`). Nuevo y opcional: `papeles()` trae `rangos` con una frase lista (D-38).
- **PC 2 · amortizacion:** ahora la prueba de humo de `cinetica` (**A-24**) y **A-25** (`deformacion`: simulador con su a priori de tamaño y prueba de humo; subirla apenas pase, PC 3 la lanza). Después **A-22** (examen de `leyes` con la verdad escondida) y **A-26** (lanzar la ronda 1 cuando el equipo dé la partida; tope 14:30). Sin método lento antes.
- **PC 3 · seguimiento:** ahora **S-22** (una persona confirma las decisiones de abajo). **S-24 terminada** (13:45): `datos/demo/subida_<caso>.csv` para los cinco casos; el de `leyes` ya responde verde. Después **S-26** (guion en voz alta) y **S-25** (firmar cifras). Con la partida y A-25 subida: `medir-rendimiento` y lanzar `deformacion` aquí hasta las 16:10.

## Qué cambió respecto del plan

- **D-38 (13:10):** el método lento pasa al final (A-36, desde las 19:00 o antes si un computador queda libre); el sello se escribe sin él. Se adelanta solo para una tarjeta cuya red no pasó. Cada modelo sortea cuántas unidades y lecturas trae el archivo; fuera de ese rango, `rojo_datos`.
- **Lo que D-38 deja sin respaldo:** `flota` y `sismicidad` validan a las 18:15, después del cierre. Sin método lento previo, a las 18:00 no tienen con qué responder (ver «Próxima decisión»).
- **S-27 adelantada:** el deck minero ya está en `pitch/deck/` (13:00). En el tablero en vivo, «Método lento» ahora va última.

## Próxima decisión

- **Ahora, una persona:** dar la partida de la ronda 1 (`cinetica` en PC 2, `deformacion` en PC 3). Y de D-37: la excepción de las 20:30, datos simulados rotulados, quién presenta; la clave de Anthropic para Render.
- **H4 · 14:30:** `leyes` en la URL pública; cinco tarjetas; ronda 1 entrenando o por lanzarse.
- **17:30, una persona, por `flota` y por `sismicidad`:** detener su entrenamiento para adelantar el método lento de su archivo (sale «precalculada» a las 18:00), o dejarla fuera del inicio y sumarla si su red pasa antes de las 20:30. PC 3 lleva la pregunta a las 17:15 con el avance de cada red.
