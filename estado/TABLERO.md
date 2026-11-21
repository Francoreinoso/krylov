# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 10:04 · **Hito vigente:** H1 cerrado (tag `h1`, D-36). Próximo: H2 de terreno y rotación, 12:15 · **Producto terminado: sáb 18:00**

**URL pública:** https://krylov-tan.vercel.app/ (P-02). Responde con 200 a las 09:23.

**Para el H2 de las 12:15, decide Rodrigo (recomendación de PC 3 entre paréntesis):**
1. **Rotación:** el sello de `supervivencia` NO PASA (sesgo en 3 de 32 parámetros; 0,43 contra el MCMC, el límite es 0,3). A las 12:15 sale con el MCMC precalculado, rotulado. (Recomiendo además seguir entrenándola en PC 3 de 11:50 a 15:15 desde su punto de guardado y revalidar antes de las 16:00; y precalcular ahí mismo la cartera con el MCMC a las 11:45, que es su plan B.)
2. **Papeles opcionales en `supervivencia` (D-35):** la red de la noche no tolera una columna ausente. (Recomiendo cortarlos: punto 2 del orden de corte de D-35; queda el esquema fijo.)
3. **Terreno, «qué manda»:** el sello pasa, pero en el archivo real la tendencia difiere del MCMC en 2,17 desviaciones. (Recomiendo `KRYLOV_ESPACIAL_THETA=mcmc`: mapa y «¿Dónde mido?» de la red; «qué manda» del MCMC, rotulado «precalculado», con el pie mixto.)

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟢 avanza | Subió el chat (interfaz) y P-12 (a) a las 10:00: `GET /api/papeles` y el calce de los archivos del demo, también en modo estático |
| amortizacion (PC 2) | 🟢 avanza | `espacial` validado (pasa, 09:39). A-19 hecha (09:41). Sello de `supervivencia`: no pasa (09:54). `estados` entrena desde las 09:55 hasta las 12:00 |
| seguimiento (PC 3) | 🟢 al día | `jerarquico` entrena aquí hasta las 11:30 (422.000 datasets a las 10:02). Verificado en PC 3: el terreno con la red (0,17 s) y la subida con los tres archivos de prueba (verde, verde y «faltan datos») |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-12 (a)**, tope 10:30: el chat con los cuatro archivos y su respuesta dentro, también estático. **Ya puedes poner `KRYLOV_MOTOR_ESPACIAL=red`** y regenerar el estático del terreno (según la decisión 3, con o sin `KRYLOV_ESPACIAL_THETA=mcmc`). Después **P-12 (b)**, tope 14:30: Render, `analizar_archivo` (ya existe en `nucleo/api.py`), `calce` e `interpretar`. Arreglos chicos: en rojo, el pie no dice «Respondió la red»; ejes de la nube más grandes.
- **PC 2 · amortizacion:** `estados` hasta las 12:00 (en PC 2, nada más pesado hasta entonces). Después, su sello. Con Rodrigo: las tres decisiones de arriba. Pedido: recuperación por parámetro en cada `sello.json` (M-35).
- **PC 3 · seguimiento:** 11:30, `jerarquico` termina solo → su sello en PC 3 (`uv run python -m motor.jerarquico.sello`), sin nada más corriendo → si Rodrigo lo aprueba, cartera de `supervivencia` con el MCMC y después seguir entrenando `supervivencia`. H2 de `jerarquico`: 13:00. Con una persona: S-09 y S-10.

## Qué cambió respecto del plan

- **Guion, momento 4:** con las cifras medidas, «228 análisis, menos de un segundo; con el método lento, más de siete horas». Sale «el método rápido acierta [P]%»: en el terreno cubre 89% contra 90% de la red. El examen real del terreno: 24 de 31 dentro del rango (77%), se dice tal cual si preguntan.
- **D-36 (H1), D-35, D-34:** chat, calce por modelo de lenguaje, subida propia, interpretación. Orden de corte a las 16:00 en D-34 y D-35.
- **D-29 a D-33:** las horas son topes; `estados` 33 parámetros, `jerarquico` 20; `etiquetas`; `unidad`; criterios del sello; `supervivencia` se valida en PC 2.

## Próxima decisión

- Rodrigo: las tres de arriba, antes de las 12:15. Una persona: la clave de Anthropic para Render. El equipo: quién presenta.
- H2: `espacial` y `supervivencia` 12:15; `jerarquico` 13:00; `estados` 14:00; tope 16:00.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito: los archivos del demo precargados en el chat. Inasistencias, solo en PC 2 y PC 3 (licencia no comercial).
