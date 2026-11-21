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
| `Fin` | Va al cierre (lámina 10) |
| `0` | «Cómo funciona»: la arquitectura, fuera del recorrido |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y qué hay detrás de cada lámina |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En la lámina 5, arrastrar gira el terreno |

En la dirección: `#5` abre la lámina 5, `#5.1` su segundo paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final y `?animado` fuerza el movimiento. Con «reducir movimiento» activado en el sistema, el deck abre sin animaciones.

## Las láminas

Son diez, más la de arquitectura. Doce pulsaciones recorren todo.

| # | Lámina | Qué se ve, y para qué está cada cosa | De dónde sale |
|---|---|---|---|
| 1 | El valor, a primera vista | «7 horas y un especialista», tachado; «0,69 segundos» con Krylov. Abajo, una barra a escala: mide las 7 horas y 25 minutos; a esa escala Krylov es menos de un píxel, y por eso es un punto que late cada 0,69 s | M-09 y M-10, del sello del motor espacial (`js/portada.js`) |
| 2 | Entra un archivo, sale la respuesta | Un archivo tras otro entra a la red y sale su mapa, que se suma a una muralla de mapas; dos contadores; al segundo paso, 228 análisis en 0,69 s contra más de 7 horas | Cada mapa es la respuesta real de la red para un banco distinto (`datos.js → rafaga`). 10 ms: `latencia_ms` del sello. 2 minutos: M-25. M-08, M-09, M-10 |
| 3 | Mundos simulados | Terrenos simulados en remolino; contador; la pila | M-01 (7.750.592) |
| 4 | Cinco decisiones | «Una mina decide esto todos los días»: las cinco preguntas, dichas sin palabras de minería, con una figura cada una | Las figuras son ilustraciones |
| 5 | Qué roca conviene procesar | El terreno como superficie topográfica en tres colores; lo que cuesta no saber; al segundo paso, «¿Dónde perforo?» con 40 columnas de luz y los tres mejores lugares | `api.analizar("leyes")` y `api.donde_medir("leyes")` con la red: M-40, M-41, M-43, M-46 |
| 6 | La pared de la mina | La pared, hecha de puntos, partida en sus 36 sectores: cada sector se desplaza y se enciende lo que el radar midió, hora a hora, durante 48 horas. La franja amarilla es el barrido del radar; las etiquetas, los dos sectores que más se movieron | El archivo de demo del caso `taludes` |
| 7 | El cobre en la planta | Las 8 líneas de estanques, con sus burbujas. La espuma de cada estanque brilla según el cobre que flotó ahí; los estanques apagados no se han medido. La columna del final de cada línea es el cobre recuperado; la línea blanca, la meta | El archivo de demo del caso `flotacion` |
| 8 | Los camiones | Los 40 camiones subiendo la rampa del rajo. La columna sobre cada uno es su desgaste, que sube con las horas de operación; la marca roja, la falla. Las etiquetas siguen a los dos más gastados | El archivo de demo del caso `flota` (el rajo es una ilustración) |
| 9 | Los túneles | Los 8 sectores de túneles después de una explosión: cada destello es un temblor del archivo, a su hora y con su tamaño según la magnitud; en rojo, el fuerte. El número de cada sector cuenta los temblores que lleva | El archivo de demo del caso `sismicidad` (el lugar de cada destello dentro de su sector es una ilustración) |
| 10 | Cierre | El mensaje de venta; un contador de los análisis que Krylov habría respondido mientras duró el pitch; la muralla de mapas que se sigue llenando; el QR | El contador es una cuenta: segundos desde la primera pulsación ÷ 10 ms (y ÷ 117 s para el método lento). El QR se dibuja desde `config.js` |
| 0 | Cómo funciona | Bayesian Amortized Inference en dos mitades, con los números del sello | `motor/artefactos/espacial/sello.json`, M-13 |

Las cuatro escenas de las láminas 6 a 9 están en `js/decisiones.js`. Cada una recorre su archivo en el tiempo (el reloj de arriba a la derecha dice por dónde va), se queda unos segundos en el final y vuelve a empezar.

## Lo que hay detrás, y que la pantalla no dice

A pedido, la pantalla no lleva pies ni rótulos («simulado», «ilustración», «medido en…», «hoja de ruta»), ni la lámina de «sabe cuando no sabe», y el deck habla de las cinco decisiones como producto. **En ninguna lámina se afirma que los datos sean de una mina real ni se muestran resultados inventados.** Lo que sigue es lo que quien presenta tiene que saber para responder con la verdad si le preguntan; está también en las notas de cada lámina (tecla `N`).

1. **De las cinco decisiones, hoy responde una.** Al generar estos datos (sáb 21-nov, 13:23) solo `leyes` tenía su motor respondiendo, con la red validada. Los motores de `taludes`, `flotacion`, `flota` y `sismicidad` todavía no respondían: **sus láminas animan el archivo de demo de cada caso; el color dice cuánto se midió (cuánto se movió un sector, cuánto desgaste lleva un camión), no qué conviene hacer.** Cuando un motor responda, se vuelve a correr `generar.py`: cada unidad toma el color de su decisión y la columna de texto muestra cuántas hay de cada una y lo que cuesta no saber. Antes de presentar hay que mirar la tabla «Los cinco casos» de `estado/TABLERO.md`.
2. **Todos los archivos de demo son simulados** (`origen_datos` de cada caso lo dice, y la app lo muestra). El único examen con datos reales es el del motor espacial en el terreno público del río Mosa: 24 de 31 mediciones escondidas dentro del rango (M-13, 77%).
3. **Las 7 horas son una multiplicación:** 228 análisis × 117,1 s (M-10, M-25). Nadie las corrió seguidas. Y se midieron en el terreno real, no en el banco del demo. Son la lámina 1 y la 2.
4. **Los mapas de las láminas 2 y 10 se repiten:** son 32, guardados; el deck los anima, no los calcula. Y el contador del cierre es una cuenta a 10 ms por análisis, no una medición.
5. **Los costos son supuestos** (K-22 a K-24): US$ 1.577.707 y US$ 8.943 dependen de ellos.
6. **En las escenas 6 a 9 el movimiento está exagerado para que se vea** (24 milímetros no se ven en una pared), y la forma de la pared, del rajo y de los túneles es una ilustración: lo que viene del archivo es cuánto, cuándo y en qué unidad.
7. **En la pared y en los túneles, Krylov apoya la decisión de un especialista** (regla 22 de `AGENTS.md`): no se promete seguridad.

Esto se aparta de las reglas 9 y 17 de `AGENTS.md` y de D-37, que piden rotular en pantalla lo simulado y separar lo construido de lo que es lámina. El repositorio es público y la app sí lo rotula: si el jurado mira las dos cosas, las va a ver distintas.

## Las palabras

El deck se escribe para alguien que nunca pisó una mina: «la pared de la mina» y no «talud»; «explosión» y no «tronadura»; «líneas de estanques» y no «celdas»; «partes del terreno» y no «bloques»; «Sector 25» y no «S-25»; «Camión 05» y no «CAEX-05». Los nombres se traducen al dibujar (`nombre()` en `js/decisiones.js`); los archivos de cada caso no se tocan.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`:** la demo real del producto. De ahí salen el QR del cierre, el texto a su lado y lo que abre la tecla `D`.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5».
- **`tiempos`:** los segundos de cada lámina que muestran las notas.

## Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js`, todo con `KRYLOV_MOTOR_ESPACIAL=red`: el caso estrella (`CASO = "leyes"`), el terreno real (`REAL = "terreno"`), los cuatro casos de series (`SERIES`), 32 bancos con la respuesta de la red para las láminas 2 y 10 y los terrenos del simulador. Los rótulos, límites y costos se leen de la API y de los archivos de cada caso. (También escribe el archivo que no alcanza y los casos de práctica, que el deck ya no usa.)

**Hay que volver a correrlo cada vez que un motor nuevo empiece a responder**, y después rehacer el respaldo.

## Respaldo estático

`respaldo/01.jpg` a `11.jpg` (1920×1080, el estado final de cada lámina; la 11 es «Cómo funciona») y `respaldo/krylov-deck.pdf`. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Qué se probó y qué no

- **Probado** (sáb 21-nov, 14:10, MacBook Air M3 con un entrenamiento corriendo en su GPU, Chromium sin ventana, abierto por `file://`): las 11 láminas y sus 13 pasos a 1920×1080 en modo estático, y el recorrido completo con el teclado a 1280×720 en movimiento, sin errores de consola y a 60 cuadros por segundo; las teclas; la pausa; la tecla `0`; la tecla `D` sin internet (abre el aviso y `Esc` vuelve); el modo «reducir movimiento»; el QR del cierre. Y una revisión automática de que ninguna cifra queda partida en dos líneas, en todas las láminas y pasos a 1920×1080.
- **Sin probar:** la tecla `D` con internet en esta versión (no cambió desde la anterior, donde abrió la demo), Safari, el proyector del lugar y un control de presentaciones real.
- **Si el navegador no tiene WebGL**, las láminas con 3D (3 a 9) muestran su imagen de `respaldo/`.

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

- **A `amortizacion` (PC 2):** avisar cuando `deformacion`, `cinetica`, `desgaste` o `sismico` respondan en `api.analizar`, para regenerar `datos.js` y el respaldo.
- **A `seguimiento`:** `GUION.md` y `LAMINAS.md` describen otro pitch (abre con el barco, entra a la app, siete láminas). Hay que dejar uno solo. Y la lámina 1 muestra «7 horas» y «0,69 segundos» (M-09, M-10): conviene que una persona las firme en `CIFRAS.md` como las cifras de apertura.
- **A `producto` (PC 1):** si cambia la dirección del producto, avisar para `config.js`.
- **A una persona del equipo:** confirmar los nombres del cierre; abrir el deck en Safari y con el proyector antes del ensayo.
