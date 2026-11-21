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

## En curso

- sáb 03:59 · Sigue P-03: vista 1 y vista 2 de los casos con lista contra `analizar_tabla.json`.

## Bloqueos

- (ninguno)

## Pedidos a otros

- (ninguno)

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
