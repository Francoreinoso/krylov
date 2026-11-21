# Krylov · deck de venta (versión minería)

Las láminas del pitch de 3 minutos (cifra J-04): **Krylov, un Artificial Data Scientist para la minería.** Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional.

El guion sincronizado, con los segundos de cada lámina, está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html`. Después, `F` para pantalla completa.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. Un control de presentaciones manda estas teclas. En la lámina 9 no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `0` | «Cómo funciona»: la arquitectura, fuera de los 3 minutos |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y de dónde sale cada número |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En las láminas 4 y 5, arrastrar gira el terreno. En la 5 se puede elegir otra letra en el mapa y «Bajo», «Medio» o «Alto» en la regla |

En la dirección: `#4` abre la lámina 4, `#4.2` su tercer paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final (así se saca el respaldo) y `?animado` fuerza el movimiento aunque el sistema pida reducirlo. Con «reducir movimiento» activado en el sistema (`prefers-reduced-motion`), el deck abre sin animaciones.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`: la demo real del producto.** De ahí salen el QR del cierre (se dibuja solo, sin servicios externos), el texto bajo el QR y lo que abre la tecla `D`. **Hoy apunta a la app publicada, que todavía no es la versión minera.** Cuando el producto final esté desplegado se cambia esa dirección y nada más.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5», porque nadie ha confirmado que su nombre se pueda mostrar.
- **`tiempos`:** los segundos de cada lámina que muestran las notas.

## Qué cambió en esta versión (sáb 21-nov, 12:40)

Rediseño completo según la revisión del equipo:

- **El relato parte del problema, no del nombre.** Lámina 1: en una mina las decisiones no esperan; los modelos que las responden tardan horas y exigen un data scientist; Krylov es un Artificial Data Scientist para la minería. El término aparece en las láminas 1, 3, 8 y 9. La historia del ingeniero naval quedó en una frase de la lámina 3.
- **Lámina 2 es una demostración:** el mismo encargo en dos pantallas, con el mapa que respondió la red apareciendo a los 0,69 s. La tecla `D` abre la demo real.
- **El mapa es una superficie topográfica**, con curvas de nivel, y ya no bloques. «¿Dónde mido?» se rehízo entera alrededor de la plata.
- **La nube** tiene las dos zonas escritas («Todo lo que practicó», «Nunca practicó») y un texto por paso.
- **Hoja de ruta con los cinco problemas** del documento «Inferencia Bayesiana Amortizada para la Gran Minería Chilena».
- **Negocio sin Buk ni AgendaPro:** se parte por la minería; después, cualquier industria.
- **El respaldo técnico ahora es una infografía de arquitectura** (tecla `0`), tomando como referencia el diagrama de inferencia bayesiana amortizada que mandó el equipo.
- **Dirección de arte nueva:** tipografías Big Shoulders Display, Instrument Sans y JetBrains Mono; paleta de cobre, óxido de cobre y oro sobre basalto; sin degradados en el texto, sin píldoras, sin tarjetas.

**Sobre los rótulos.** Salieron las píldoras («Datos públicos reales», «Costos supuestos», «Ilustración»). La información no salió: quedó dentro de las frases («Un terreno real», «terrenos simulados», «Hoja de ruta:», «con los costos que tú pones») y en una línea chica al pie donde hace falta («Imagen: ilustración», «Nada de esta lámina existe todavía», «Plan del equipo · sin clientes todavía»). La regla 9 de `AGENTS.md` sigue pidiendo que lo simulado y lo ilustrativo se diga.

## Qué se probó y qué no

- **Probado** (sáb 21-nov, MacBook Air M3, Chromium sin ventana, abierto por `file://`): las 10 láminas y sus 21 pasos a 1280×720 y a 1920×1080, sin errores de consola y a 60 cuadros por segundo; las teclas de la tabla; la pausa; el modo sin movimiento; la tecla `D` con y sin internet; el QR dibujado desde `config.js`.
- **Sin probar:** Safari, el proyector del lugar y un control de presentaciones real.
- **Si el navegador no tiene WebGL**, las láminas con 3D (1, 3, 4, 5, 7, 8 y 9) muestran su imagen de `respaldo/`.

## Las láminas y de dónde sale cada dato

Todo número en pantalla tiene su id de `pitch/CIFRAS.md` o sale de un archivo o comando del repositorio. Los mismos ids están en las notas (tecla `N`).

| # | Lámina | Qué se ve | Números y su fuente | Qué es ilustración |
|---|---|---|---|---|
| 1 | El problema | Un rajo hecho de puntos que aparece con un barrido; el problema en tres frases; el nombre | Ninguno. «Tardan horas» se sostiene con M-10 | **El rajo.** Lo genera `js/puntos.js`; no es una mina real. Al pie: «Imagen: ilustración» |
| 2 | Demo | Dos pantallas con el mismo encargo: la de Krylov termina en 0,69 s reales y muestra su mapa; la otra avanza en tiempo real y, al segundo clic, acelerada | M-08 (228), M-09 (0,69 s), M-10 (26.699 s), M-25 (117 s por análisis). El mapa: `api.analizar("terreno")` | Nada |
| 3 | Mundos simulados | Terrenos simulados en remolino; contador; la pila que queda | M-01 (7.750.592). N-01 («a comienzos del 1900») | Los terrenos son reales del simulador (256, semilla 2026), **repetidos** |
| 4 | El mapa | El terreno real como superficie: altura = metal estimado, color = decisión, línea blanca = 720 mg/kg, malla = tope del rango creíble, puntos = las 155 mediciones | D-04 (155), K-11 (720 mg/kg), K-12 y K-13 (costos). Áreas por decisión (20, 67, 254 bloques) y US$ 646.485: `api.analizar("terreno")` con la red | Nada. **La superficie se dibuja interpolando** entre los 341 bloques del motor |
| 5 | ¿Dónde mido? | 19 columnas de luz, una por lugar candidato, tan altas como lo que vale medir ahí; las tres mejores con letra; al medir, baja un taladro y el mapa se rehace | K-17 (US$ 3.000). M-08, M-09. A, B y C (US$ 15.629, 11.582, 10.561): `api.donde_medir("terreno")`. Los otros 16 lugares: `generar.py` repite ese cálculo y comprueba que los tres mejores coinciden. US$ 21.038: la diferencia entre 646.485 y el mapa rehecho (625.447) | Nada. **El mapa rehecho es la respuesta de la red, guardada**: el deck la anima, no la calcula |
| 6 | Sabe cuando no sabe | Los casos con que practicó; un archivo cae lejos, en rojo; se quita la columna y cae adentro | M-29 (límite 0,912). `api.nube("rotacion_malo")` y la misma con `["quitar_factor:fecha_salida"]` | Nada. **El ejemplo no es minero** (es el archivo público de rotación, D-01 y D-05): la lámina habla de «casos» y de «un archivo» |
| 7 | Hoja de ruta | Cinco decisiones de la mina, con una figura cada una | **Ninguno** | **Toda la lámina.** El título dice «Hoja de ruta» y el pie «Nada de esta lámina existe todavía · imágenes: ilustración» |
| 8 | Negocio | El rajo se envuelve en una esfera: de la minería a cualquier industria | Ninguno | Los puntos. Al pie: «Plan del equipo · sin clientes todavía» |
| 9 | Cierre | La frase, el QR y el equipo | «Millones» se sostiene con M-01 | El fondo |
| 0 | Cómo funciona | La arquitectura en dos mitades: lo que se hace una vez y lo que pasa con cada archivo | `motor/artefactos/espacial/sello.json`; M-13 (24 de 31) | Nada |

### Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js` con: el mapa (`api.analizar`), los tres mejores lugares (`api.donde_medir`) y los 19 candidatos con su valor, el mapa rehecho para cada letra y cada resultado (nueve llamadas a `api.analizar` con una medición más), la nube del archivo malo y del corregido (`api.nube`), 256 terrenos del simulador y una copia del sello. Todo con `KRYLOV_MOTOR_ESPACIAL=red`.

**Cuando el proyecto termine de pasar a casos mineros**, basta volver a correrlo: los rótulos de las decisiones, la unidad, el umbral y los costos de las láminas 4 y 5 se leen de la respuesta de la API, no están escritos en el HTML. Lo que sí está escrito a mano y habría que cambiar: el título de la lámina 4 («Un terreno real. 155 muestras de zinc.»), su bajada («junto al río Mosa») y la etiqueta «Río Mosa» de `js/terreno.js`; y `generar.py` nombra los casos `terreno` y `rotacion_malo`.

Dos cálculos usan funciones internas de `nucleo/espacial.py`, porque la API no los entrega: el rango creíble por bloque (5% a 95%) y el valor de medir en los 16 lugares que no son los tres mejores. En los dos casos el script comprueba que su resultado coincide con el de la API donde se puede comparar.

### Respaldo estático

`respaldo/01.jpg` a `10.jpg` (1920×1080, el estado final de cada lámina) y `respaldo/krylov-deck.pdf` con las diez. Si el navegador falla en el escenario, se abre el PDF. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Seis cosas que quien presenta tiene que saber

1. **El terreno del demo no es una mina.** Son 155 muestras reales de zinc en un suelo contaminado, junto al río Mosa. Es el mismo tipo de modelo con que se estiman leyes, y así se dice; no se dice que sea un yacimiento. Por eso la lámina 4 habla de «metal» y de «limpiar».
2. **Las 7 horas son una multiplicación.** M-10 (26.699 s) es 228 análisis × 117,1 s, medidos en 6 terrenos. Nadie corrió las siete horas seguidas. La lámina 2 lo dice al pie.
3. **Las cifras del documento de minería no están en las láminas.** Costo por hora de un camión detenido, minutos para decidir tras una tronadura, porcentaje de arsénico, duración del piloto, nombres de faenas: nada tiene fuente registrada en `CIFRAS.md`. Las cinco preguntas de la lámina 7 sí salen de ese documento, sin números.
4. **La nube es del caso de rotación, cuya red no pasó su sello.** La lámina muestra el detector de archivos malos, que sí está medido (M-29). No se dice «al instante» de ese caso.
5. **El examen real del terreno dio 24 de 31 (77%), no 90%** (M-13). Está en la lámina `0` y se dice tal cual si preguntan.
6. **«La industria que más pesa en Chile» va sin cifra.** Si alguien quiere una, hay que registrarla con su fuente.

## Bibliotecas y tipografías (todas locales, en `vendor/`)

| Archivo | Qué es | Licencia |
|---|---|---|
| `three.min.js` | three.js r149, para el 3D | MIT (`three.LICENSE`) |
| `gsap.min.js` | GSAP 3.15.1, para las líneas de tiempo | Licencia estándar sin costo de GreenSock (gsap.com/standard-license) |
| `qrcode.js` | qrcode-generator 2.0.4, dibuja el QR en el navegador | MIT (en la cabecera del archivo) |
| `big-shoulders-display-*.woff2` | Titulares y cifras | SIL Open Font License 1.1 (`big-shoulders-display.LICENSE`) |
| `instrument-sans-*.woff2` | Texto | SIL Open Font License 1.1 (`instrument-sans.LICENSE`) |
| `jetbrains-mono-*.woff2` | Datos y pies | SIL Open Font License 1.1 (`jetbrains-mono.LICENSE`) |
| `archivo-*.woff2` | La tipografía de la app; el deck ya no la usa | SIL Open Font License 1.1 (`archivo.LICENSE`) |

**Colores.** El deck ya no usa los de la app. Decisiones: rojo cobre `#e4603c` (actuar), oro achurado `#eec25a` (no sabemos) y turquesa de óxido de cobre `#2aa596` (no hace falta). Si la app cambia su paleta con el pivote, conviene igualarlas en uno de los dos lados.

## Pedidos a otros

- **A `seguimiento` (CIFRAS.md):** siguen sin id las cifras del terreno que el deck muestra. Salen de `api.analizar("terreno")` y `api.donde_medir("terreno")` con la red, sáb 21-nov 12:20, PC 3:
  - M-12, lo que vale medir en el mejor punto: **US$ 15.629** (A; B 11.582 y C 10.561). Hoy dice «pendiente».
  - Lo que cuesta no saber en el terreno: **US$ 646.485**; después de medir en A y que salga alto (1.113 mg/kg): **US$ 625.447**; la diferencia que se muestra, **US$ 21.038**.
  - Bloques por decisión: **20**, **67** y **254**.
  - Aclarar en M-10 que los 26.699 s son 228 × 117,1 s.
  - Si el pitch va a usar las cifras del documento de minería, registrarlas con su enlace antes.
- **A quien lleve el pivote a minería:** avisar cuando cambien los casos, para regenerar `datos.js` y revisar los tres textos escritos a mano de la lámina 4. Y un archivo malo minero para la lámina 6.
- **A `producto` (PC 1):** la dirección del producto final para `config.js`. Hoy la tecla `D` y el QR abren la app publicada.
- **A una persona del equipo:** confirmar los nombres del cierre, y abrir el deck en Safari y con el proyector antes del ensayo.
