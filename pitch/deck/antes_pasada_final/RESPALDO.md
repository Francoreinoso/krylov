# Respaldo del deck antes de la pasada final

Esta carpeta guarda el deck tal como estaba el domingo 22 de noviembre a las 00:30, antes de la pasada final de textos (láminas 2, 7, 12, L y W). Sirve para devolver una lámina a ese estado sin tocar las demás.

Hay dos respaldos, y conviene no confundirlos:

| Carpeta | Tag de git | Qué guarda |
|---|---|---|
| `antes_pasada_final/` (esta) | `deck-antes-pasada-final` | El deck del sábado a la medianoche, con la última iteración de diseño ya hecha |
| `original/` | `deck-original` | El deck del sábado a las 22:40, anterior a esa iteración de diseño |

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `index.html`, `deck.css`, `laboratorios.css`, `config.js`, `yacimiento.html`, `js/` | El código completo de ese momento. Abre solo: `open pitch/deck/antes_pasada_final/index.html`. Usa `../vendor` y `../datos/datos.js`, que no cambiaron |
| `datos/laboratorios.js`, `datos/generar_laboratorios.py` | Los 30 grupos que mostraba el mapa de la lámina W antes de filtrarlo |
| `capturas/01.jpg` a `18.jpg` | Cómo se veía cada lámina (01 a 14, el recorrido; 15 a 18, las preguntas Q, L, 0 y W) |

El mismo estado está en git:

```
git show deck-antes-pasada-final:pitch/deck/yacimiento.html
git diff deck-antes-pasada-final -- pitch/deck/index.html
```

## Dónde vive cada lámina que cambió

| Lámina | `data-id` | Qué archivos la forman |
|---|---|---|
| 2 · Generative AI para datasets | `paradigma` | Su `<section>` en `index.html` |
| 7 · La roca y «¿Dónde perforo?» | `leyes` | Su `<section>` en `index.html`; la frase bajo las barras, en `js/terreno.js` (buscar `class="p nota"`) |
| 12 · ¿Dónde está el mineral? | `yacimiento` | `yacimiento.html` completo, y su `<section>` en `index.html` (solo las notas) |
| L · ¿Y un LLM? | `llm` | Su `<section>` en `index.html`; la línea del pie, en `js/preguntas.js` (buscar `llm-prueba`) |
| W · Quién investiga esto | `laboratorios` | `datos/laboratorios.js`, `datos/generar_laboratorios.py`, `js/laboratorios.js` |

## Cómo devolver una lámina

Para pedírselo a Claude Code:

> Vuelve las láminas 7 y 12 al estado de `pitch/deck/antes_pasada_final`, y mantén las demás como están.

O conservando una parte de lo nuevo:

> Vuelve la lámina 12 al estado de `pitch/deck/antes_pasada_final`, pero mantén la transición nueva entre el primer paso y el segundo.

A mano, para la lámina con `data-id="<id>"`:

1. En `index.html`, reemplazar su `<section … data-id="<id>">` completo por el de esta carpeta.
2. Copiar desde aquí los archivos de la tabla de arriba. Al copiar `yacimiento.html` o `index.html`, las rutas `../vendor/` y `../datos/` vuelven a ser `vendor/` y `datos/`.
3. Si el archivo de `js/` es compartido (`terreno.js`, `preguntas.js`), copiar solo el trozo de esa lámina.
4. Abrir el deck y pasar por esa lámina y sus vecinas.

Qué cambió en cada lámina, y por qué, está en `../CAMBIOS.md`, sección «Pasada final».
