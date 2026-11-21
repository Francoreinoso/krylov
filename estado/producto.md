# Estado · producto (PC 1)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 1 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («P-21 terminada: …»): así lo lee el tablero en vivo.
Persona: Francoreinoso · Dueño de `servicio/` y `web/`. Instrucciones: `PC1_PRODUCTO.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/producto_hasta_el_pivote.md`.

## Hecho

- sáb 12:10 · Antes del pivote, y sigue sirviendo: app en línea con chat, calce, interpretación, modo estático, deslizadores, mapa en canvas y «¿Dónde mido?» sobre el `donde_medir` real (P-09, en curso a las 11:33). Detalle en `estado/historia/producto_hasta_el_pivote.md`.
- sáb 16:40 · P-21 terminada: cinco tarjetas mineras en el orden de `casos/INICIO`, las cuatro nuevas con su ejemplo fijo rotulado «Ejemplo» (commit `cc97fdc`). En el repositorio, sin desplegar.
- sáb 16:40 · P-22 terminada: `leyes` con la red. Cada pin simula una sola muestra sobre el análisis original (A → B → C en cualquier orden, también sin servidor); el botón dice «¿Dónde perforo?» desde antes de la primera respuesta (sin texto fijo); «¿Dónde perforo?» se sirve precalculado (`precalculado: true`, rotulado) y se pide a la par del análisis; «Responde la red» solo si el sello del motor pasa (`servicio/respuestas.py`, `_con_sello`); pie sin doble punto («Datos simulados.»); el deslizador vuelve al costo del caso (imán de medio paso); `GET /api/textos` y `estatico/textos.json`. Arranque: `KRYLOV_MOTOR_ESPACIAL=red uv run uvicorn servicio.app:app --port 8010` y `cd web && npm run dev` (`?estatico` para el modo sin servidor). Verificación: `cd web && npm run build && npm run prueba && cd .. && uv run pytest servicio -q` (6 pasan, dos nuevas en `servicio/prueba_sello.py`). Sin navegador en esta sesión: el recorrido en pantalla (P-22-23, tabla 2.8) queda para la persona. `web/` lista para desplegar cuando la persona decida.
- sáb 16:48 · P-23 terminada: `Curva` legible desde la última fila (textos de 17 a 18, 3 a 5 marcas por eje, puntos de radio 4, «ahora» punteado con su rótulo, límite de 4 px, nombres de los ejes dentro del dibujo); abanico en azul propio (`--abanico: #6fa8ff`, no se confunde con los tres colores ni con el cobre) con su leyenda de `casos/textos.yaml`; en taludes, «Faltan entre 6 y 16 horas» grande junto al nombre y una franja en el gráfico; sismicidad en escalones (prop `escalones`, decidida por `motor_id`); guardia en `marcas()`; los rótulos salen de `GET /api/textos` (`estatico/textos.json`), sin respaldo escrito en el código; la curva también en pantalla completa (`useUnidadElegida`, `CurvaDeUnidad`); la unidad elegida siempre está en la lista corta del chat (CAEX-30 en `flota`). Verificación: la de P-22 más `grep -n "AHORA\|LÍMITE\|Límite\|Ahora" web/src/Curva.tsx` vacío. Visto en capturas de Firefox sin ventana (el componente con los datos del estático, no el recorrido con clics): S-18, S-04 con marca y franja, L-7, CAEX-30, CAEX-37, Sector 5, y la pantalla completa de taludes, flota y sismicidad. `curva: null` probado en memoria (dos unidades sin curva: 6 filas clicables de 8; ninguna: sin curva y sin hueco). El recorrido con clics (tabla 3.9, tecla `V`, zoom al 50%) queda para la persona.
- sáb 16:40 · P-22, nota: con los costos del caso el cliente ya usa los conteos y el número del servidor (`useDecision.ts`, `sinCambios`): 147 / 568 / 309 y US$ 1.577.707. Los colores del mapa sí se recalculan en el navegador con 32 versiones.

## En curso

- sáb 16:48 · Sin tarea en curso: P-22 y P-23 subidas. Espera que la persona decida el despliegue y la siguiente tarea (P-24).

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 16:40 · P-22, a PC 2: `sello_resumen.frase` llega vacía en `analizar`; por eso el pie no muestra la frase del sello.
- sáb 16:40 · P-22, a PC 3: la plantilla de `sismicidad` dice «En 1 sectores» (concordancia).
- sáb 16:48 · P-23, a PC 3: en `flotacion` la recuperación llega como fracción («0,84»); ¿se muestra así o en porcentaje? La web no la convierte por su cuenta.
- sáb 16:48 · P-23, a PC 2 y PC 3: en los ejemplos fijos de `taludes` y `flota` el abanico no nace en el último punto medido (son números inventados; se dibuja tal cual). Que las respuestas reales sí lo hagan.
- sáb 16:48 · P-23, nota: en `flota`, los camiones con poco desgaste (CAEX-37, CAEX-13) quedan abajo del gráfico porque el límite (1,0) siempre está a la vista; el eje vertical parte en 0 cuando todos los valores son positivos, y nada más.
- sáb 16:40 · P-22, recorte anotado: cada pin simula su resultado medio; elegir bajo, medio o alto por pin (`WORKPLAN.md`, «tres resultados») no entra.
- sáb 16:40 · P-22, para P-24/P-29: textos de minería que todavía están escritos en `web/src`: `Mapa.tsx` («Cada punto es una muestra de un pozo…», «Mapa del banco…», «Ya perforaste en…»), `RespuestaEnChat.tsx` («Perforas en…», «Una muestra aquí vale», «Perforar en», «Límite», «Una muestra más cuesta»), `Chat.tsx` («Perforar en», «Una mina decide esto todos los días», «minas simuladas»), `Lateral.tsx` («Decisiones de la mina»), `preguntas.ts` (`MOTOR_EN_PALABRAS`), `Deslizadores.tsx` («Supuestos del demo…»).

## Direcciones

| Qué | Valor |
|---|---|
| URL pública de la web (Vercel) | https://krylov-tan.vercel.app/ |
| URL pública de la API (Render) | sin desplegar |
| Comando para correr todo en local | `uv run uvicorn servicio.app:app --port 8010 --reload` y `cd web && npm run dev` |
| Vercel | El plan gratuito llegó a su límite diario el sábado a las 10:10. Solo se despliega cuando cambia `web/`; agrupar los redespliegues en H4, H5 y H6 |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Tiempo de la tarjeta de `leyes` en la URL pública, desde un teléfono | sin medir | — | — |
| Tiempo de «¿Dónde perforo?» en el computador del escenario | sin medir | — | — |
| Cálculo de «¿Dónde perforo?» de `leyes` (480 análisis rehechos), al exportar | 2.869 ms (antes 3.358 ms) | `exportar_estatico` en PC 1, `tiempo_ms` | sáb 16:40 |
| Lectura del precalculado de «¿Dónde perforo?» | 4 a 6 ms | `curl` al servidor de desarrollo, tres veces | sáb 16:40 |
| `analizar` de `leyes` por la API local | 246 ms | `curl` a `/api/analizar` en PC 1 | sáb 16:40 |
