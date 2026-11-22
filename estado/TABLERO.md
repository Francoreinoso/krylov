# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 50 líneas. El tablero en vivo (https://silent-math.github.io/krylov-panel/) lee este archivo.

**Actualizado:** sáb 21-nov 23:50 · **Producto terminado (H6): tag `congelado` (18:32)** · Entrega: dom 08:00

**URL pública:** https://krylov-krylov.vercel.app/ · responde, con las cinco tarjetas por su red (comprobado 23:48). API: https://krylov-api.onrender.com (se duerme a los 15 minutos).

**Las cinco tarjetas tienen su red validada.** El método lento (A-36) ya corrió en PC 3 para los cinco motores: `espacial` en su sello; los cuatro de series como propuesta en `estado/a36_metodo_lento/` (convergen `cinetica` y `sismico` siempre, `deformacion` 2 de 5, `desgaste` solo el demo). **Ninguno de esos cuatro está en un sello: lo decide PC 2.**

## Los cinco casos

Valores de cada celda: `listo`, `en curso`, `pendiente`, `no pasa`, `cortado`. «Responde» dice quién contesta hoy esa tarjeta: `red`, `precalculado`, `ejemplo` (número inventado para maquetar) o `nada`. **«Método lento» va al final (D-38): `pendiente` ahí no es atraso hasta A-36.**

| Caso | Motor | Datos | Simulador | Red | Sello | En la app | Método lento | Responde |
|---|---|---|---|---|---|---|---|---|
| leyes | espacial | listo | listo | listo | listo | listo | listo | red |
| taludes | deformacion | listo | listo | listo | listo | listo | en curso | red |
| flotacion | cinetica | listo | listo | listo | listo | listo | en curso | red |
| flota | desgaste | listo | listo | listo | listo | en curso | en curso | red |
| sismicidad | sismico | listo | listo | listo | listo | listo | en curso | red |

Verificado en PC 3 a las 20:06, corriendo `api.analizar` con cada red: `leyes` (147, 568 y 309 bloques), `taludes` (5, 29 y 2), `flotacion` (2, 3 y 3), `sismicidad` (0, 4 y 4) y `flota` (8, 31 y 1 camiones) responden verde. `flota` todavía no está en el estático ni en la URL pública.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 | URL nueva funcionando con cuatro tarjetas (P-28, P-30). Falta `flota` con `KRYLOV_MOTOR_DESGASTE=red`, exportar y redesplegar |
| amortizacion (PC 2) | 🟢 | `desgaste` PASA (19:35): cinco de cinco. Quedan A-35 (README técnico) y revisar el método lento que PC 3 escribió |
| seguimiento (PC 3) | 🟢 | A-36 corrido para los cinco (propuesta para PC 2). Sexto motor `yacimiento` (D-40, fuera del producto): sello no pasa por los parámetros; el mapa está calibrado y coincide con el método lento (M-63 a M-65) |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora exportar el estático con las cinco redes (`flota` incluida) y redesplegar; después cerrar **P-29** y preparar el demo (`preparar-demo`).
- **PC 2 · amortizacion:** **A-35** (README técnico). Decidir qué entra a los sellos de `estado/a36_metodo_lento/` (ojo: `deformacion` 0,38 y `desgaste` 0,39 quedan sobre 0,3, con referencias que no siempre convergen). Enlazar `pitch/deck/yacimiento.html` en el deck.
- **PC 3 · seguimiento:** S-30: borradores de la entrega listos (`pitch/README_borrador.md`, `pitch/descripcion_borrador.md`). Falta que una persona los lea para aplicarlos; el tag `entrega` va el domingo antes de las 08:00.

## Qué cambió respecto del plan

- **D-38 (13:10):** el método lento pasa al final (A-36, desde las 19:00 o antes si un computador queda libre); el sello se escribe sin él. Se adelanta solo para una tarjeta cuya red no pasó. Cada modelo sortea cuántas unidades y lecturas trae el archivo; fuera de ese rango, `rojo_datos`.
- **D-40 (20:20):** un sexto motor, `yacimiento` (3D desde sondajes), en su carpeta y fuera de la app, del contrato y del recorrido. No toca nada de lo congelado. Se cuenta solo con su sello, y solo si pasa.
- **S-27 adelantada:** el deck minero ya está en `pitch/deck/` (13:00). En el tablero en vivo, «Método lento» ahora va última.

## Próxima decisión

- **Una persona (PC 2 o quien decida):** si el método lento que escribió PC 3 entra a `motor/` y a los sellos. Si la diferencia con una red sale sobre 0,3, el sello de esa red dejaría de decir «pasa»: se decide con los números a la vista, no antes.
- **Una persona, antes del domingo 08:00:** leer los dos borradores de la entrega y decir si se aplican; y qué hacer con la línea del `README.md` original dirigida a modelos de lenguaje (los agentes no la siguen por su cuenta). Además: quién presenta.
- **Decidido:** las cinco tarjetas quedan en `casos/INICIO` con su red; ninguna sale precalculada.
