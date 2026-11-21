# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 12:40 · **Hito vigente:** pivote a minería (D-37). Próximo: H4, 14:30 · **Producto terminado: sáb 18:00** · Tope de redes: 20:30

**URL pública:** https://krylov-tan.vercel.app/ (todavía muestra las cuatro tarjetas anteriores; cambia con P-21 y P-22).

**PIVOTE (D-37): Krylov es el data scientist artificial de la minería. Lo primero que hace cada computador:** `git pull`, leer D-37 en `DECISIONES.md` y su `PC*.md`. **Se detienen los entrenamientos de `estados` (PC 2) y `jerarquico` (PC 3): ya no se usan.** Las tareas nuevas parten en 21; lo anterior está en `estado/historia/`.

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`.

| Caso | Motor | Datos | Simulador | Método lento | Red | Sello | En la app | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | pendiente | listo | listo | pendiente | red |
| taludes | deformacion | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |
| flotacion | cinetica | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |
| flota | desgaste | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |
| sismicidad | sismico | listo | pendiente | pendiente | pendiente | pendiente | pendiente | ejemplo |

`leyes` ya responde con la red validada (verificado en PC 2, sáb 12:05: verde; 147 bloques «conviene apartar», 568 «puede ir a la planta», 309 «no sabemos»; 61 de 68 muestras escondidas dentro del rango; «¿Dónde perforo?» rehace 480 análisis en cerca de 1 s, con otro entrenamiento corriendo). Falta su método lento para el archivo nuevo (A-22) y verla en la app (P-22).

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 pivote | P-09 («¿Dónde mido?») sirve tal cual para `leyes`. Ahora P-21 |
| amortizacion (PC 2) | 🟡 pivote | Detener `estados`. Ahora A-21, A-22 (sesión B) y A-23 (sesión A) |
| seguimiento (PC 3) | 🟡 pivote | Detener `jerarquico`. Ahora S-22 |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-21**, tope 13:10: inicio con las cinco tarjetas mineras (cuatro contra su ejemplo fijo, rotulado «ejemplo»), fuera la cartera y lo antiguo. Después **P-22**, tope 13:50: `leyes` real con la red y «¿Dónde perforo?» en la URL pública. Después **P-23**: el componente `Curva`.
- **PC 2 · amortizacion:** ahora **A-21** (la persona detiene `estados`; `MOTORES` y `prueba_api` con el `INICIO` nuevo). Sesión B: **A-22** (`leyes`: método lento del archivo y examen con la verdad escondida), después **A-24** (`cinetica`). Sesión A: **A-23** (el andamio de series; subirlo apenas pase su prueba), después **A-25** (`deformacion`). **Ronda 1 lanzada a las 14:30.**
- **PC 3 · seguimiento:** ahora **S-22** (una persona avisa, detiene `jerarquico` y confirma las cuatro decisiones de D-37). Después **S-23** y **S-24** (datos reales abiertos de taludes y de cobre, si calzan) y **S-25** (firmar las cifras de minería).

## Qué cambió respecto del plan

- **D-37 (12:10):** cinco decisiones de una mina; se parte del motor `espacial`. Cuatro motores nuevos y chicos con un andamio común; dos rondas de entrenamiento (14:30 y 16:30); tope de redes 20:30. Se cortan la cartera y rotación, inasistencias y crédito.
- **Cifras del documento técnico que no se usan:** «menos de 2 horas» (leyes), «15 a 30 minutos» (reingreso), «US$ 15.000 a 40.000 por hora» (camión). Las que sí, con su fuente, en `pitch/CIFRAS.md`, sección «La minería».
- **El contrato no cambió de forma.** Se agregó `curva` (opcional, por unidad) y el archivo largo de los motores de series (`unidad`, `tiempo`, `valor`).

## Próxima decisión

- **Una persona del equipo, cuanto antes:** confirmar de D-37 (1) la excepción de las 20:30, (2) el orden de las rondas, (3) datos simulados rotulados, (4) quién presenta. Y la clave de Anthropic para Render.
- **H4 · 14:30:** `leyes` en la URL pública; cinco tarjetas; ronda 1 entrenando.
