# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 17:25 · **Hito vigente:** camino a H4, 14:30 · **Producto terminado: sáb 18:00** · Tope de redes: 20:30

**URL pública:** https://krylov-tan.vercel.app/ · **a las 16:20 sigue mostrando las cuatro tarjetas de antes del pivote** (rotación, terreno, citas, crédito). P-21 está en el repositorio pero no desplegada.

**Manda D-38 (13:10), sobre D-37:** el método lento de cada motor se corre **al final** (A-36), y cada modelo sortea el tamaño del dataset. Una red se lanza y se valida sin esperarlo. **Ronda 1 terminada en PC 3:** `deformacion` no pasó su sello (falla solo el SBC por unidad). **Ronda 2:** `sismico` entrena en PC 3 desde las 16:14, hasta las 18:15. Falta el veredicto de `cinetica` (PC 2). El detalle pieza por pieza de cada motor está en `estado/MODELOS.md`.

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`. **«Método lento» va al final (D-38): `pendiente` ahí no es atraso hasta A-36.**

| Caso | Motor | Datos | Simulador | Red | Sello | En la app | Método lento | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | listo | listo | pendiente | pendiente | red |
| taludes | deformacion | listo | listo | listo | no pasa | pendiente | pendiente | ejemplo |
| flotacion | cinetica | listo | listo | en curso | pendiente | pendiente | pendiente | ejemplo |
| flota | desgaste | listo | listo | pendiente | pendiente | pendiente | pendiente | ejemplo |
| sismicidad | sismico | listo | listo | en curso | pendiente | pendiente | pendiente | ejemplo |

Verificado en PC 3 a las 14:00, corriendo: los cuatro simuladores existen y sus pruebas pasan (`pytest motor/cinetica motor/desgaste motor/sismico motor/deformacion`); `leyes` responde verde con la red y ya tiene su examen por color (A-22; M-54: de 147 bloques «conviene apartar», 138 estaban sobre el límite). Las cuatro tarjetas nuevas responden `no_disponible` hasta que su red valide, y la web pinta su ejemplo.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🔴 atrasado | La URL pública no cambió desde el pivote: H4 (14:30) no se cumplió. Sin estado nuevo desde las 12:40. Recorte: desplegar ya P-21 y sacar `leyes` real (P-22); `Curva` (P-23) y el chat (P-24) esperan |
| amortizacion (PC 2) | 🟡 sin noticias | Sin estado ni commits desde las 13:57. Falta el veredicto de `cinetica` (16:10), lanzar `desgaste` y responder el pedido de `ventana` |
| seguimiento (PC 3) | 🟡 entrenando | Dos a la vez desde las 16:33, hasta las 18:15: `sismico` (364 datasets por segundo) y `deformacion` retomado (281), por decisión de su persona. El sello de `deformacion` de las 16:10 (no pasa) sigue vigente hasta revalidar |

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
- **Ahora, PC 2 y una persona, por `taludes`:** su red no pasó (solo el SBC por unidad; coberturas en 0,90). Opciones: revisar el criterio, seguir entrenando después de la ronda 2, o adelantar su método lento para salir «precalculada». Hasta entonces la tarjeta sigue de ejemplo.
- **Decidido (17:25, persona de PC 3):** `sismicidad` sigue entrenando, sin método lento; fuera del inicio a las 18:00 y entra si su red pasa antes de las 20:30. **Falta `flota`:** lo decide la persona de PC 2. **17:40, PC 1 y PC 3 (S-31):** qué tarjetas quedan en `casos/INICIO`; hoy solo `leyes` responde con su motor.
