# Respaldo del deck original

Esta carpeta guarda el deck tal como estaba el sábado 21 de noviembre a las 22:40, antes de la última iteración de diseño. Sirve para devolver una lámina a su estado original sin tocar las demás.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `index.html`, `deck.css`, `config.js`, `yacimiento.html`, `js/` | El código original completo. Abre solo: `open pitch/deck/original/index.html`. Usa `../vendor` y `../datos`, que no cambiaron |
| `capturas/NN_P.jpg` | Cómo se veía cada lámina (NN es su posición original, P su paso) |

El mismo estado está en git, con el tag `deck-original`:

```
git show deck-original:pitch/deck/index.html
git diff deck-original -- pitch/deck/js/flujo.js
```

## Dónde vive cada lámina

Cada lámina tiene tres partes: su `<section>` en `index.html`, su bloque de reglas en `deck.css` (cada bloque empieza con un comentario que nombra la lámina) y su escena en `js/`.

| Lámina original | `data-id` | Escena |
|---|---|---|
| 1 · Portada | `valor` | `js/portada.js`, `js/campo.js` |
| 2 · Generative AI para datasets | `paradigma` | `js/paradigma.js` |
| 3 · Antes y hoy | `flujo` | `js/flujo.js` |
| 4 · Terrenos simulados | `mundos` | `js/mundos.js`, `js/campo.js` |
| 5 · Entra un archivo, sale la respuesta | `rafaga` | `js/rafaga.js` |
| 6 · Cinco decisiones | `vision` | `js/vision.js` |
| 7 · La roca | `leyes` | `js/terreno.js`, `js/zoom.js`, `js/intervalos.js` |
| 8 · La pared | `taludes` | `js/decisiones.js`, `js/zoom.js`, `js/intervalos.js` |
| 9 · La planta | `flotacion` | `js/decisiones.js` |
| 10 · Los camiones | `flota` | `js/decisiones.js` |
| 11 · Los túneles | `sismicidad` | `js/decisiones.js` |
| 12 · ¿Cómo sé que acierta? | `confianza` | `js/confianza.js` |
| 13 · Cierre | `cierre` | `js/cierre.js` |
| Q · ¿Quién lo usa? | `quien` | `js/vision.js`, `js/preguntas.js` |
| A · ¿Qué archivo recibe? | `archivo` | `js/preguntas.js` |
| L · ¿Y un LLM? | `llm` | `js/preguntas.js` |
| M · Intervalo de credibilidad | `produccion` | `js/preguntas.js`, `js/intervalos.js` |
| Y · El yacimiento | `yacimiento` | `yacimiento.html`, `js/yacimiento.js` |
| 0 · Cómo funciona | `arquitectura` | `js/arquitectura.js` |

## Cómo devolver una lámina a su original

Para pedírselo a Claude Code: «vuelve las láminas X e Y al estado original de `pitch/deck/original`, y mantén las demás como están».

A mano, para la lámina con `data-id="<id>"`:

1. En `index.html`, reemplazar su `<section … data-id="<id>">` completo por el de `original/index.html`.
2. En `deck.css`, reemplazar el bloque de esa lámina por el de `original/deck.css`.
3. Su escena: si el archivo de `js/` es solo de esa lámina, copiarlo desde `original/js/`. Si es compartido (`decisiones.js`, `zoom.js`, `intervalos.js`, `preguntas.js`, `vision.js`), copiar solo el `K.registrar('<id>', …)` de esa lámina.
4. Abrir el deck y pasar por esa lámina y sus vecinas.

El detalle de qué cambió en cada lámina, y por qué, está en `../CAMBIOS.md`.
