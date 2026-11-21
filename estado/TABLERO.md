# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 18:31 · **Producto terminado (H6): tag `congelado` puesto a las 18:40** · Tope de redes: 20:30

**URL pública:** https://krylov-tan.vercel.app/ · **sigue con las tarjetas de antes del pivote: Vercel limitó los despliegues por 24 horas (17:58).** El código y el estático están en `main`. Lo decide una persona: otra cuenta o proyecto de Vercel. Sin eso, el QR lleva a la app antigua.

**Cuatro de cinco tarjetas tienen su red validada** (`leyes`, `taludes`, `flotacion`, `sismicidad`); falta `flota`. D-38: el método lento va al final (A-36). D-39: el SBC por unidad se decide por el tamaño de la desviación. Detalle por motor: `estado/MODELOS.md`.

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`. **«Método lento» va al final (D-38): `pendiente` ahí no es atraso hasta A-36.**

| Caso | Motor | Datos | Simulador | Red | Sello | En la app | Método lento | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | listo | listo | listo | pendiente | red |
| taludes | deformacion | listo | listo | listo | listo | listo | pendiente | red |
| flotacion | cinetica | listo | listo | listo | listo | listo | pendiente | red |
| flota | desgaste | listo | listo | en curso | pendiente | pendiente | pendiente | ejemplo |
| sismicidad | sismico | listo | listo | listo | listo | en curso | pendiente | red |

Verificado en PC 3 a las 18:30, corriendo: `pytest nucleo motor servicio`, 98 pasan; con sus variables en `red`, `leyes` (147, 568 y 309 bloques), `taludes` (5, 29 y 2 sectores), `flotacion` (2, 3 y 3 líneas) y `sismicidad` (0, 4 y 4 sectores) responden verde. «En la app» es en local y en el estático de `main`, no en la URL pública.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🔴 sin URL | P-21 a P-28 hechas y en `main`, pero Vercel no despliega por 24 horas. Falta `sismicidad` con su red (P-30) y cerrar P-29 |
| amortizacion (PC 2) | 🟡 | `cinetica` PASA. Falta el veredicto de `desgaste` (validaba a las 18:15) y después A-35 y A-36 |
| seguimiento (PC 3) | 🟢 | `deformacion` y `sismico` PASAN; nada entrenando. Cifras de los sellos registradas (M-48 a M-52) |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-30**: exportar el estático con las cuatro redes (`sismicidad` incluida, y la frase del sello corregida) y cerrar **P-29**. El despliegue espera a que una persona resuelva Vercel.
- **PC 2 · amortizacion:** ahora **A-34** (veredicto de `desgaste`) y avisar a PC 1 si pasa. Después **A-35** (README técnico) y **A-36** (método lento de `espacial`, `cinetica` y `desgaste`, sin nada entrenando).
- **PC 3 · seguimiento:** H6 corrido y tag `congelado` puesto (18:40). Ahora ensayo con una persona (18:30), prueba con extraños (19:00, una persona) y **A-36** aquí para `deformacion` y `sismico` cuando PC 2 suba su `mcmc.py`.

## Qué cambió respecto del plan

- **D-38 (13:10):** el método lento pasa al final (A-36, desde las 19:00 o antes si un computador queda libre); el sello se escribe sin él. Se adelanta solo para una tarjeta cuya red no pasó. Cada modelo sortea cuántas unidades y lecturas trae el archivo; fuera de ese rango, `rojo_datos`.
- **Lo que D-38 deja sin respaldo:** `flota` y `sismicidad` validan a las 18:15, después del cierre. Sin método lento previo, a las 18:00 no tienen con qué responder (ver «Próxima decisión»).
- **S-27 adelantada:** el deck minero ya está en `pitch/deck/` (13:00). En el tablero en vivo, «Método lento» ahora va última.

## Próxima decisión

- **Ahora, una persona,** de D-37: la excepción de las 20:30, datos simulados rotulados, quién presenta; la clave de Anthropic para Render.
- **Ahora, una persona:** Vercel (otra cuenta o proyecto), o el QR del pitch lleva a la app antigua. Y `flota`: entra al inicio solo si `desgaste` pasa antes de las 20:30.
- **Decidido (17:25, persona de PC 3):** `sismicidad` sigue entrenando, sin método lento; fuera del inicio a las 18:00 y entra si su red pasa antes de las 20:30. **Falta `flota`:** lo decide la persona de PC 2. **17:40, PC 1 y PC 3 (S-31):** qué tarjetas quedan en `casos/INICIO`; hoy solo `leyes` responde con su motor.
