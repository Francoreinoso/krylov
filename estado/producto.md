# Estado · producto (PC 1)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 1 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago.
Persona: Francoreinoso · Dueño de `servicio/` y `web/`. Instrucciones: `PC1_PRODUCTO.md`.

## Hecho

- sáb 03:00 · Plan final recibido. Nada construido todavía.
- sáb 03:55 · Arranque: clon con push a los dos repositorios, rol declarado. Espejo `Silent-math/krylov` público (verificado 03:47).
- sáb 03:53 · Instalado según STACK 2.1: `uv sync` (base, sin `entrenar`), Vite + React + TS, Tailwind 4. Node 24.21 en vez de 26: Vite corre igual y no actualizo con la memoria justa.
- sáb 03:53 · **P-01** en `main`: API con las 7 rutas del contrato sobre los ejemplos fijos (`servicio/fijos.py`, una sola tabla para la API y el modo estático), `exportar_estatico` escribe 15 archivos en `web/public/estatico/`, y la web pinta el inicio (4 tarjetas) y la respuesta (titular, número grande, tres colores, unidades, banda roja, rótulo «precalculado»). Pie: «API» o «modo estático». Verificación: `curl -XPOST localhost:8010/api/analizar -d '{"caso":"credito"}'` y `npm run build` sin errores; `/?estatico=1` lee solo archivos.

- sáb 03:59 · **P-02**: web en Vercel desde `Silent-math/krylov` (importó el dueño del espejo). Página, JS y `/estatico/*.json` responden 200 en 0,3 a 0,7 s medidos con curl desde PC 1. El paquete es el mismo de la compilación local. Probada desde un teléfono a las 04:01: abre casi al instante, con `?estatico=1` y sin él.
- sáb 04:37 · **P-03** en `main` y desplegado: el inicio muestra las preguntas en el orden de `casos/INICIO`. La respuesta trae titular, número grande, tres colores (la duda achurada), lista de mayor a menor riesgo con su rango creíble y una sola línea del punto de corte, «qué pesa» con la certeza en palabras y un pie que dice quién respondió. Fuente Archivo instalada en local (`@fontsource-variable/archivo`) para funcionar sin internet. `?caso=rotacion` abre la respuesta directo. Verificado con capturas a 1280×720 y 390 px: se lee completa en el proyector y en el teléfono. El examen queda para P-10.
- sáb 05:04 · **P-N1** en `main`: `web/src/decision.ts` (copia de `nucleo/decision.py`) y `web/pruebas/decision.test.ts`. Ver: `cd web && npm run prueba` (45 de 45 pasan, con `node --test`, sin dependencias nuevas). Deslizadores de costos que recalculan colores, número grande y titular en el navegador.
- sáb 05:04 · **P-N2** (mapa del terreno en canvas: bloques en tres colores, la duda achurada, mediciones como puntos) y **P-N3** (nube en canvas: simulaciones, ejes con nombre, archivo en rojo) en `main`. Se ven con `?caso=terreno` y `?caso=rotacion_malo`.
- sáb 05:04 · **Rediseño acordado con la persona de PC 1**: tema oscuro; colores de decisión rojo, verde y ámbar achurado (como dice el guion); la respuesta cabe en una sola pantalla de 1280×720, en tres columnas (número, colores y deslizadores / lista, mapa o nube / qué pesa y examen); cada persona dibujada como sus 32 versiones creíbles con una sola línea del punto de corte; inicio con la frase de Krylov. Verificado con capturas a 1280×720 y 390 px. Desplegado.

## En curso

- sáb 05:04 · Sigue (adelantado, D-29): P-07 (tecla `M` y botón de corrección), P-09 («¿Dónde mido?» con los pines sobre el mapa), P-08, P-05 (usar `nucleo.api` cuando cada motor responda; si no, el ejemplo fijo).

## Bloqueos

- (ninguno)

## Pedidos a otros

- sáb 05:04 · **A PC 2:** que `analizar` traiga `unidad: {singular, plural}` del YAML. Es un campo nuevo que no rompe nada, pero el contrato está congelado: lo decides tú, con su entrada en DECISIONES. Mientras tanto la web saca el nombre de la unidad del titular («49 personas están…») para rehacerlo al mover los deslizadores.
- sáb 05:04 · **A PC 3, aviso:** la web pasó a tema oscuro y los colores ahora son rojo, verde y ámbar, como dice el guion del momento 4. Si las láminas usan colores de la app, conviene que calcen.

## Direcciones

| Qué | Valor |
|---|---|
| URL pública de la web (Vercel) | https://krylov-tan.vercel.app/ (sáb 03:59) |
| URL pública de la API (Render) | sin desplegar |
| Comando para correr todo en local | `uv run uvicorn servicio.app:app --port 8010 --reload` y `cd web && npm run dev` (en este PC el 8000 está ocupado; la web en dev apunta a `localhost:8010`) |
| Herramientas elegidas de `STACK.md` y por qué | Vite+React+TS: una página con estado en memoria, sale estática. Tailwind 4: pantallas ordenadas rápido, sin configuración. Canvas para mapa y nube, SVG para barras y lista: rendimiento y control. FastAPI: envuelve `nucleo/api.py` en pocas líneas. Web en Vercel y API en Render (pendiente): sponsors, y el modo estático cubre la URL pública. onnxruntime: no aplica en este PC, lo usa `nucleo/` |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Tiempo de una tarjeta, en local | sin medir | — | — |
| Tiempo de una tarjeta, URL pública en modo estático, desde un teléfono | casi instantáneo (a ojo; curl desde PC 1: 0,3 a 0,7 s por archivo) | teléfono, con y sin `?estatico=1`, y curl | 03:59 |
| Tiempo de «¿Dónde mido?» en el computador del escenario | sin medir | — | — |
| Recorrido completo sin internet | sin probar | `preparar-demo` | — |
