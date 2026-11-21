# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 09:25 (H1) · **Hito vigente:** H1 cerrado (tag `h1`, D-36). Próximo: H2 de terreno y rotación, 12:15 · **Producto terminado: sáb 18:00**

**URL pública:** https://krylov-tan.vercel.app/ (P-02). Responde con 200 a las 09:23 (página y respuestas precalculadas, 0,47 a 0,74 s).

**⚠️ Para Rodrigo (D-36): PC 2 está detenido desde las 08:30 esperándote.** A-08 (sello de `espacial`), el sello de `supervivencia` (D-33) y lanzar `estados` son el camino crítico del H2 de las 12:15. Si A-08 no parte a las 10:00, el H2 de `estados` corre al tope de las 16:00. **⚠️ PC 1:** sin código desde las 05:03; si P-12 (a) no está en `main` a las 10:30, se cortan el calce y la interpretación (D-34, D-35).

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 sin código desde las 05:03 | P-01 a P-03 y P-N1 a P-N3 verificados. Después, diseño de D-34 y D-35. Ahora P-12 |
| amortizacion (PC 2) | 🔴 esperando a Rodrigo | `espacial` terminó a las 08:30 (7,75 millones de terrenos). `supervivencia` lista para su sello. D-34 y D-35 en `estados`, `jerarquico` y `espacial` |
| seguimiento (PC 3) | 🟢 al día | `supervivencia` exportada y subida (12,74 millones de datasets, 13b3e42). `jerarquico` (D-35) entrena aquí desde las 08:52 hasta las 11:30 |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-12 (a)**, tope 10:30: chat con los cuatro archivos del demo, calce de columnas y respuesta dentro del chat, también en modo estático. Después **P-12 (b)**, tope 14:30: API en Render (no existe todavía), `analizar_archivo`, `calce` e `interpretar` (clave de Anthropic en Render, la pone una persona). **Empuja lo que tengas.** Arreglos chicos: en rojo, el pie no dice «Respondió la red»; ejes de la nube más grandes. Archivos de prueba para la subida: `datos/demo/subida_rotacion_{ventas,investigacion,rrhh}.csv`.
- **PC 2 · amortizacion:** con Rodrigo, ahora **A-08** (`uv run python -m motor.espacial.sello`), después el sello de `supervivencia` (la red ya está en `main`) y lanzar `estados`; nunca dos a la vez. Sesión B: **A-19** (D-34 y D-35), tope 10:30. Pedido: recuperación por parámetro en cada `sello.json` (M-35).
- **PC 3 · seguimiento:** `jerarquico` hasta las 11:30 (no se toca). Ahora S-07 (inasistencias, cuando haya red) y, con una persona, S-09 y S-10. 11:30: detener `jerarquico`; su sello, en un computador sin nada entrenando. H2 de `jerarquico`: 13:00.

## Qué cambió respecto del plan

- **D-36 (H1):** pasa; alertas por PC 2 detenido y PC 1 sin código.
- **D-35 (07:40):** el modelo de lenguaje propone el calce de columnas (sin filas) y el usuario lo confirma; papeles opcionales en `jerarquico` y `estados`.
- **D-34 (07:12):** chat, subida propia y modelo de lenguaje que interpreta. **Orden de corte a las 16:00:** primero el calce y la interpretación, después la subida propia; el chat con los archivos del demo no se corta.
- **D-29 a D-33:** las horas son topes; `estados` 33 parámetros, `jerarquico` 20; `etiquetas`; `unidad`; criterios del sello; `supervivencia` se valida en PC 2.
- Guion: 3 minutos (J-04) y no cabía (176 s de habla). Si se muestra la subida en el escenario, sale la cartera.

## Próxima decisión

- Una persona: la clave de Anthropic para Render. Al validar: ¿la nube va al semáforo? (D-32, D-33). El equipo: quién presenta.
- H2: `espacial` y `supervivencia` 12:15; `jerarquico` 13:00; `estados` 14:00; tope 16:00.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito: los archivos del demo precargados en el chat. Inasistencias, solo en PC 2 y PC 3 (licencia no comercial).
