# Krylov · deck de venta

**Krylov, el Artificial Data Scientist de la minería.** El mensaje del deck: los modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide, gracias a Bayesian Amortized Inference.

Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional. El guion está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html`. Después, `F` para pantalla completa.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. En el cierre no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `Fin` | Va al cierre (lámina 11) |
| `0` | «Cómo funciona»: la arquitectura, fuera del recorrido |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y qué hay detrás de cada lámina |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En la lámina 5, arrastrar gira el banco |

En la dirección: `#5` abre la lámina 5, `#5.1` su segundo paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final y `?animado` fuerza el movimiento. Con «reducir movimiento» activado en el sistema, el deck abre sin animaciones.

## Las láminas

| # | Lámina | Qué se ve | De dónde sale |
|---|---|---|---|
| 1 | El problema | Un rajo hecho de puntos; tres preguntas de la mina; «exigen un especialista y horas de cómputo»; Krylov | El rajo es una ilustración (`js/puntos.js`) |
| 2 | Entra un archivo, sale la respuesta | Un banco tras otro entra a la red y sale su mapa, que se suma a una muralla de mapas; dos contadores; al segundo paso, 228 análisis en 0,69 s contra más de 7 horas | Cada mapa es la respuesta real de la red para un banco distinto (`datos.js → rafaga`). 10 ms: `latencia_ms` del sello. 2 minutos: M-25. M-08, M-09, M-10 |
| 3 | Mundos simulados | Terrenos simulados en remolino; contador; la pila | M-01 (7.750.592) |
| 4 | Cinco decisiones | «Una mina decide esto todos los días»: las cinco preguntas, con una figura cada una | Las figuras son ilustraciones |
| 5 | Leyes | El banco como superficie topográfica en tres colores; lo que cuesta no saber; al segundo paso, «¿Dónde perforo?» con 40 columnas de luz y los tres mejores lugares | `api.analizar("leyes")` y `api.donde_medir("leyes")` con la red: M-40, M-41, M-43, M-46 |
| 6 | Taludes | Una cordillera: lo que el radar midió en cada uno de los 36 sectores del muro | El archivo de demo del caso `taludes` |
| 7 | Flotación | Las curvas de las 8 líneas de la planta subiendo hacia la meta | El archivo de demo del caso `flotacion` |
| 8 | Flota | El desgaste de los 40 camiones acercándose a la falla | El archivo de demo del caso `flota` |
| 9 | Sismicidad | Los temblores de 8 sectores después de una tronadura | El archivo de demo del caso `sismicidad` |
| 10 | Sabe cuando no sabe | Los casos con que practicó; un banco con 12 muestras cae afuera; con 340, adentro | `api.analizar("leyes_pocos")` y 3.000 terrenos del simulador |
| 11 | Cierre | El mensaje de venta; el rajo se envuelve en una esfera; QR | El QR se dibuja desde `config.js` |
| 0 | Cómo funciona | Bayesian Amortized Inference en dos mitades, con los números del sello | `motor/artefactos/espacial/sello.json`, M-13 |

## Lo que hay detrás, y que la pantalla ya no dice

En esta versión se sacaron de la pantalla, a pedido, los pies y rótulos («simulado», «ilustración», «medido en…», «hoja de ruta») y la frase «Krylov sabe cuánto no sabe…». El deck habla de las cinco decisiones como producto. **En ninguna lámina se afirma que los datos sean de una mina real ni se muestran resultados inventados**; lo que sigue es lo que quien presenta tiene que saber para responder con la verdad si le preguntan. Está también en las notas de cada lámina (tecla `N`).

1. **De las cinco decisiones, hoy responde una.** Al generar estos datos (sáb 21-nov, 13:20) solo `leyes` tenía su motor respondiendo, con la red validada. Los motores de `taludes`, `flotacion`, `flota` y `sismicidad` todavía no respondían: **sus láminas dibujan el archivo de demo de cada caso, sin colores de decisión ni cifras de respuesta.** Cuando un motor responda, se vuelve a correr `generar.py` y su lámina pinta sola la decisión de cada unidad, cuántas hay de cada color y lo que cuesta no saber. Antes de presentar hay que mirar la tabla «Los cinco casos» de `estado/TABLERO.md`.
2. **Todos los archivos de demo son simulados** (`origen_datos` de cada caso lo dice, y la app lo muestra). El único examen con datos reales es el del motor espacial en el terreno público del río Mosa: 24 de 31 mediciones escondidas dentro del rango (M-13, 77%).
3. **Las 7 horas son una multiplicación:** 228 análisis × 117,1 s (M-10, M-25). Nadie las corrió seguidas. Y se midieron en el terreno real, no en el banco.
4. **Los bancos de la lámina 2 se repiten:** son 32, guardados; el deck los anima, no los calcula.
5. **Los costos son supuestos** (K-22 a K-24): US$ 1.577.707 y US$ 8.943 dependen de ellos.
6. **En taludes y sismicidad, Krylov apoya la decisión de un especialista** (regla 22 de `AGENTS.md`): no se promete seguridad.

Esto se aparta de las reglas 9 y 17 de `AGENTS.md` y de D-37, que piden rotular en pantalla lo simulado y separar lo construido de lo que es lámina. El repositorio es público y la app sí lo rotula: si el jurado mira las dos cosas, las va a ver distintas.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`:** la demo real del producto. De ahí salen el QR del cierre, el texto a su lado y lo que abre la tecla `D`.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5».
- **`tiempos`:** los segundos de cada lámina que muestran las notas.

## Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js`, todo con `KRYLOV_MOTOR_ESPACIAL=red`: el caso estrella (`CASO = "leyes"`), el terreno real (`REAL = "terreno"`), el archivo que no alcanza (`POCOS = "leyes_pocos"`), los cuatro casos de series (`SERIES`), 32 bancos con la respuesta de la red para la lámina 2 y los terrenos del simulador. Los rótulos, límites y costos se leen de la API y de los archivos de cada caso.

**Hay que volver a correrlo cada vez que un motor nuevo empiece a responder**, y después rehacer el respaldo.

## Respaldo estático

`respaldo/01.jpg` a `12.jpg` (1920×1080, el estado final de cada lámina; la 12 es «Cómo funciona») y `respaldo/krylov-deck.pdf`. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Qué se probó y qué no

- **Probado** (sáb 21-nov, MacBook Air M3, Chromium sin ventana, abierto por `file://`): las 12 láminas y sus 19 pasos a 1280×720 y a 1920×1080, sin errores de consola y a 60 cuadros por segundo; las teclas; la pausa; el modo sin movimiento; la tecla `D` con y sin internet; el QR. Y una revisión automática de que ninguna cifra queda partida en dos líneas, en todas las láminas y pasos a 1920×1080.
- **Sin probar:** Safari, el proyector del lugar y un control de presentaciones real.
- **Si el navegador no tiene WebGL**, las láminas con 3D (1, 3, 4, 5 y 11) muestran su imagen de `respaldo/`.

## Bibliotecas y tipografías (todas locales, en `vendor/`)

| Archivo | Qué es | Licencia |
|---|---|---|
| `three.min.js` | three.js r149, para el 3D | MIT (`three.LICENSE`) |
| `gsap.min.js` | GSAP 3.15.1, para las líneas de tiempo | Licencia estándar sin costo de GreenSock (gsap.com/standard-license) |
| `qrcode.js` | qrcode-generator 2.0.4, dibuja el QR en el navegador | MIT (en la cabecera del archivo) |
| `big-shoulders-display-*.woff2` | Titulares y cifras | SIL Open Font License 1.1 |
| `instrument-sans-*.woff2` | Texto | SIL Open Font License 1.1 |
| `jetbrains-mono-*.woff2` | Datos | SIL Open Font License 1.1 |
| `archivo-*.woff2` | La tipografía de la app; el deck ya no la usa | SIL Open Font License 1.1 |

## Pedidos a otros

- **A `amortizacion` (PC 2):** avisar cuando `deformacion`, `cinetica`, `desgaste` o `sismico` respondan en `api.analizar`, para regenerar `datos.js` y el respaldo. Y M-44, el tiempo limpio de los 480 análisis.
- **A `seguimiento`:** `GUION.md` y `LAMINAS.md` describen otro pitch (abre con el barco, entra a la app, siete láminas). Hay que dejar uno solo.
- **A `producto` (PC 1):** si cambia la dirección del producto, avisar para `config.js`.
- **A una persona del equipo:** confirmar los nombres del cierre; abrir el deck en Safari y con el proyector antes del ensayo.
