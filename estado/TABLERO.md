# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 18:18 · **Hito vigente:** camino a H4, 14:30 · **Producto terminado: sáb 18:00** · Tope de redes: 20:30

**URL pública:** https://krylov-tan.vercel.app/ · **a las 16:20 sigue mostrando las cuatro tarjetas de antes del pivote** (rotación, terreno, citas, crédito). P-21 está en el repositorio pero no desplegada.

**D-38:** el método lento va al final (A-36). **D-39 (17:10):** el SBC por unidad se decide por el tamaño de la desviación; con eso **`cinetica` y `deformacion` pasan su sello.** Ronda 2: `sismico` entrena en PC 3 hasta las 18:15 y `desgaste` en PC 2. Detalle por motor: `estado/MODELOS.md`.

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`. **«Método lento» va al final (D-38): `pendiente` ahí no es atraso hasta A-36.**

| Caso | Motor | Datos | Simulador | Red | Sello | En la app | Método lento | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | listo | listo | pendiente | pendiente | red |
| taludes | deformacion | listo | listo | listo | listo | en curso | pendiente | red |
| flotacion | cinetica | listo | listo | listo | listo | listo | pendiente | red |
| flota | desgaste | listo | listo | en curso | pendiente | pendiente | pendiente | ejemplo |
| sismicidad | sismico | listo | listo | listo | listo | pendiente | pendiente | red |

Verificado en PC 3 a las 14:00, corriendo: los cuatro simuladores existen y sus pruebas pasan (`pytest motor/cinetica motor/desgaste motor/sismico motor/deformacion`); `leyes` responde verde con la red y ya tiene su examen por color (A-22; M-54: de 147 bloques «conviene apartar», 138 estaban sobre el límite). Las cuatro tarjetas nuevas responden `no_disponible` hasta que su red valide, y la web pinta su ejemplo.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 al cierre | P-21 a P-26 hechas entre 16:40 y 17:32; `flotacion` responde con su red. Falta activar `taludes` con la red y el despliegue |
| amortizacion (PC 2) | 🟢 | `cinetica` PASA (43,2 millones de plantas). `desgaste` entrenando. D-39 escrita |
| seguimiento (PC 3) | 🟢 | `sismico` PASA (18:15; 3.723.712 datasets) y `deformacion` PASA (17:36). Nada entrenando. Batería del Mac en 8% |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-21** (cinco tarjetas mineras, cuatro con su ejemplo rotulado): subirla con lo que haya. Después **P-22**, tope 13:50: `leyes` real con la red y «¿Dónde perforo?» en la URL pública; es lo único que H4 exige de PC 1. Después **P-23** (`Curva`). Nuevo y opcional: `papeles()` trae `rangos` con una frase lista (D-38).
- **PC 2 · amortizacion:** `cinetica` entrena hasta las 16:10. Ahora las pruebas de humo de `desgaste` (A-27) y, si se puede sin estorbar al entrenamiento, nada más pesado. A las 16:10 **A-30** (validar `cinetica` sin método lento) y **A-31** (lanzar `desgaste`). Pendiente de PC 2: `ventana` en `sismicidad` (ver pedidos de PC 3).
- **PC 3 · seguimiento:** ahora **S-22** (una persona confirma las decisiones de abajo). **S-24 terminada** (13:27): `datos/demo/subida_<caso>.csv` para los cinco casos; el de `leyes` ya responde verde. Después **S-26** (guion en voz alta) y **S-25** (firmar cifras). A las 16:10, **S-28**: detener `deformacion`, validar sin método lento, exportar y subir.

## Qué cambió respecto del plan

- **D-38 (13:10):** el método lento pasa al final (A-36, desde las 19:00 o antes si un computador queda libre); el sello se escribe sin él. Se adelanta solo para una tarjeta cuya red no pasó. Cada modelo sortea cuántas unidades y lecturas trae el archivo; fuera de ese rango, `rojo_datos`.
- **Lo que D-38 deja sin respaldo:** `flota` y `sismicidad` validan a las 18:15, después del cierre. Sin método lento previo, a las 18:00 no tienen con qué responder (ver «Próxima decisión»).
- **S-27 adelantada:** el deck minero ya está en `pitch/deck/` (13:00). En el tablero en vivo, «Método lento» ahora va última.

## Próxima decisión

- **Ahora, una persona,** de D-37: la excepción de las 20:30, datos simulados rotulados, quién presenta; la clave de Anthropic para Render.
- **Ahora, PC 1:** `KRYLOV_MOTOR_DEFORMACION=red`, volver a exportar `taludes` y desplegar. A las 18:00, tres tarjetas con su red: `leyes`, `flotacion` y `taludes`.
- **Decidido (17:25, persona de PC 3):** `sismicidad` sigue entrenando, sin método lento; fuera del inicio a las 18:00 y entra si su red pasa antes de las 20:30. **Falta `flota`:** lo decide la persona de PC 2. **17:40, PC 1 y PC 3 (S-31):** qué tarjetas quedan en `casos/INICIO`; hoy solo `leyes` responde con su motor.
