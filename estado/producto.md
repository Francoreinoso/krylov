# Estado · producto (PC 1)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 1 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago. **El identificador de la tarea va al inicio de la línea** («P-21 terminada: …»): así lo lee el tablero en vivo.
Persona: Francoreinoso · Dueño de `servicio/` y `web/`. Instrucciones: `PC1_PRODUCTO.md`.

Archivo nuevo desde el pivote a minería (D-37, sáb 12:10). Lo anterior está en `estado/historia/producto_hasta_el_pivote.md`.

## Hecho

- sáb 12:10 · Antes del pivote, y sigue sirviendo: app en línea con chat, calce, interpretación, modo estático, deslizadores, mapa en canvas y «¿Dónde mido?» sobre el `donde_medir` real (P-09, en curso a las 11:33). Detalle en `estado/historia/producto_hasta_el_pivote.md`.
- sáb 16:40 · P-21 terminada: cinco tarjetas mineras en el orden de `casos/INICIO`, las cuatro nuevas con su ejemplo fijo rotulado «Ejemplo» (commit `cc97fdc`). En el repositorio, sin desplegar.
- sáb 16:40 · P-22 terminada: `leyes` con la red. Cada pin simula una sola muestra sobre el análisis original (A → B → C en cualquier orden, también sin servidor); el botón dice «¿Dónde perforo?» desde antes de la primera respuesta (sin texto fijo); «¿Dónde perforo?» se sirve precalculado (`precalculado: true`, rotulado) y se pide a la par del análisis; «Responde la red» solo si el sello del motor pasa (`servicio/respuestas.py`, `_con_sello`); pie sin doble punto («Datos simulados.»); el deslizador vuelve al costo del caso (imán de medio paso); `GET /api/textos` y `estatico/textos.json`. Arranque: `KRYLOV_MOTOR_ESPACIAL=red uv run uvicorn servicio.app:app --port 8010` y `cd web && npm run dev` (`?estatico` para el modo sin servidor). Verificación: `cd web && npm run build && npm run prueba && cd .. && uv run pytest servicio -q` (6 pasan, dos nuevas en `servicio/prueba_sello.py`). Sin navegador en esta sesión: el recorrido en pantalla (P-22-23, tabla 2.8) queda para la persona. `web/` lista para desplegar cuando la persona decida.
- sáb 16:40 · P-22, nota: con los costos del caso el cliente ya usa los conteos y el número del servidor (`useDecision.ts`, `sinCambios`): 147 / 568 / 309 y US$ 1.577.707. Los colores del mapa sí se recalculan en el navegador con 32 versiones.

## En curso

- sáb 16:40 · P-23: componente `Curva` (legible en proyector, abanico con color propio, marca de taludes, curva en pantalla completa). Tope 17:40.

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 16:40 · P-22, a PC 2: `sello_resumen.frase` llega vacía en `analizar`; por eso el pie no muestra la frase del sello.
- sáb 16:40 · P-22, a PC 3: la plantilla de `sismicidad` dice «En 1 sectores» (concordancia).
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
