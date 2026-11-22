# Última iteración de la app: qué cambió y por qué

Domingo 22 de noviembre, desde las 00:00 (decisión D-42 en `DECISIONES.md`). La app anterior está completa en el tag de git
`web-original` (el mismo commit que `d4940e1`) y sus capturas en [`original/capturas/`](original/capturas/). Para devolver
una vista: «vuelve las vistas X e Y al estado original con `git checkout web-original -- <archivos>`, y mantén las demás».
Ojo: varias vistas comparten `src/App.tsx`, que se rehízo entero; devolver una sola vista exige devolver `App.tsx` y
rehacer a mano el enganche de las demás.

**Lo que manda:** el deck y la app son la misma cosa. Cuando alguien sube un archivo, sus filas entran a la red como en la
lámina 5 («Entra un archivo, sale la respuesta») y la respuesta aparece en la misma escena de la lámina de esa decisión
(el terreno, la pared, la planta, los camiones, los túneles), con el mismo punto que viaja y la misma tarjeta con la
distribución, pero con los datos del archivo.

## Cómo está hecho

| Qué | Por qué |
|---|---|
| La app corre los módulos del deck **sin tocarlos** (`pitch/deck/js/*.js`, `deck.css`, `index.html` y `vendor/`): `vite.config.ts` los sirve en desarrollo y los copia a `dist/deck/` al compilar. No hay copias en el repositorio | Una sola escena para el deck y la app: si cambia una lámina, cambia la respuesta |
| `escena.html` + `src/escena/marco.ts`: una lámina del deck dentro de un marco. Recibe los datos de la respuesta (`window.KRYLOV_DATOS`), arma la sección de esa lámina con el mismo HTML del deck y carga sus módulos en el mismo orden | El deck arma cada escena una sola vez: un marco por respuesta deja que cada archivo tenga la suya |
| `src/escena/datos.ts`: de una respuesta de la API a los datos que lee el deck, con la misma forma que escribe `pitch/deck/datos/generar.py` | Aquí no se calcula ningún intervalo: todo sale del motor |
| `src/escena/LaminaDeck.tsx` y `protocolo.ts`: el marco en React y sus mensajes (el paso de la lámina, perforar, pausa, las teclas) | Las teclas del escenario son de la app aunque el foco esté en la escena |
| Sin WebGL, en una pantalla angosta o con la API anterior (sin los campos de D-42), la respuesta se muestra con los componentes de antes (`Respaldo.tsx`: mapa, lista y curva) | La URL del QR la abre toda la sala; Render se redespliega a mano |

## Vista por vista

### 1 · Portada del inicio
- **Cambio:** el cerro de partículas (`Particulas.tsx`) se reemplazó por la lámina 1 del deck, el rajo en relieve con el suelo hasta los bordes, corriendo en vivo. Su texto es el del deck. Encima, abajo a la izquierda, la caja para subir el archivo, con el archivo de ejemplo a un clic. Dentro de la app, el bloque de texto de la portada sube un poco (`escena.html`) para dejarle lugar a la caja.
- **Por qué:** la acción principal estaba escondida detrás de un «+» en una caja de chat. Ahora es lo primero que se ve, y el archivo de ejemplo no exige elegir nada antes.
- **Texto antes:** «Krylov / Un data scientist artificial para la minería. / Modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide.» y la caja «Elige una decisión o escribe qué quieres saber».
- **Texto ahora:** el de la lámina 1: «Krylov / El Artificial Data Scientist de la minería / Responde en milisegundos lo que a un especialista le toma horas de cálculo, y dice cuánto se puede equivocar.» Y la caja: «Sube el archivo de tu decisión / Un CSV, como sale de tu planilla. Arrástralo aquí o elígelo. / Elegir archivo · Probar con un archivo de ejemplo / El de ejemplo es un banco de roca simulado: no son datos de ninguna minera.»
- **Archivos:** `src/Inicio.tsx`, `src/Subir.tsx`, `escena.html`. Borrados: `Particulas.tsx`, `Compositor.tsx`.
- **Devolver:** `git checkout web-original -- web/src/Chat.tsx web/src/Particulas.tsx web/src/Compositor.tsx` y montar `Chat` en `App.tsx`.

### 2 · Las decisiones
- **Cambio:** la lámina 6 del deck, en vivo (las seis figuras que se mueven y las seis preguntas). Cada columna se puede tocar y abre esa decisión. Debajo, en las mismas columnas, quién la toma en la minera y qué archivo se sube (de `casos/<caso>.yaml`, `tarjeta.quien` y `tarjeta.archivo`).
- **Por qué:** las figuras eran dibujos quietos y las bajadas («La roca vecina se parece») no le decían nada a quien decide.
- **Texto antes:** «Una mina decide esto todos los días.» y las preguntas «¿Este bloque va a la planta o se aparta?», «¿Es ruido o el muro va a ceder?», «¿Se me está yendo cobre al relave?», «¿Puede volver a entrar la gente?», con bajadas «La roca vecina se parece», «El muro se mueve cada vez más rápido», «El cobre flota rápido al principio y cada vez más lento», «Cada sismo sube por un rato la probabilidad del siguiente» y «Responde la red».
- **Texto ahora:** «Una minera se pregunta esto todos los días.», «Seis preguntas, seis modelos de especialista y un solo Artificial Data Scientist.» y las seis preguntas del deck, palabra por palabra. Bajo cada una, el cargo («Geólogo de producción», «Ingeniero geotécnico», «Jefe de planta», «Planificador de mantención», «Jefe de turno subterráneo»), el archivo y «Responder con un archivo».
- **Archivos:** `src/Inicio.tsx`, `casos/*.yaml`. Borrados: `Decisiones.tsx`, `FiguraMina.tsx`, `Ilustracion.tsx`, `preguntas.ts`.
- **Devolver:** `git checkout web-original -- web/src/Decisiones.tsx web/src/FiguraMina.tsx web/src/Ilustracion.tsx web/src/preguntas.ts casos/`.

### 3 · Soltar el archivo
- **Cambio:** el navegador lee las filas del archivo (`csv.ts`: punto y coma, coma decimal, BOM y latin-1) y cada fila cae como un punto en una tarjeta, como en la lámina 5. Cuando llegan las columnas, los puntos se ordenan: donde están las muestras si el archivo trae ubicación, o una serie por unidad si trae tiempo (`orden.ts`, `Coreografia.tsx`). Un archivo que se suelta sin decisión pregunta «¿Qué decisión es?» (no la adivina ningún modelo).
- **Por qué:** soltar el archivo no movía nada: una ficha naranja con «CSV · 1.375 filas · 3 columnas».
- **Texto antes:** «Suelta tu CSV / Queda adjunto a tu próxima pregunta».
- **Texto ahora:** «Suéltalo aquí / Después eliges qué decisión es.» (o la pregunta de la decisión elegida).
- **Archivos:** `src/csv.ts`, `src/orden.ts`, `src/Coreografia.tsx`, `src/Viaje.tsx`, `src/Subir.tsx`. Borrado: `TarjetaArchivo.tsx`.

### 4 · El calce de columnas
- **Cambio:** dice quién propuso y qué leyó: el equipo (los archivos de ejemplo), la regla por nombre y tipo, o un modelo de lenguaje con su proveedor (hoy Groq, D-41), «que leyó el nombre, un resumen y tres valores de ejemplo de cada columna; nunca filas completas». La transformación se escribe como se entiende: «minutos ÷ 60, de minutos a horas». Los selectores son de la app. Mientras llega la propuesta, las columnas del archivo esperan arriba y después bajan a su papel. Sigue siendo obligatorio confirmar (D-35).
- **Por qué:** «Columnas propuestas por un modelo de prueba» y «en dividir» se veían rotos frente a un jurado.
- **Texto antes:** «Leí las columnas de X. Esta es mi propuesta de qué columna cumple cada papel del modelo («el muro se mueve cada vez más rápido»): revísala antes de analizar.» · «Columnas propuestas por un modelo de prueba» · «en dividir» · «(ninguna)» · «No se usan 2 columnas: …».
- **Texto ahora:** «¿Qué columna es qué?» · «Las propuso un modelo de lenguaje (Groq), que leyó el nombre, un resumen y tres valores de ejemplo de cada columna; nunca filas completas.» (o «Krylov las eligió por el nombre y el tipo de cada columna.», o «Las columnas de este archivo ya las eligió el equipo.») · «minutos ÷ 60, de minutos a horas» · «Ninguna» · «Krylov no usa las columnas …» · el botón dice qué falta si falta algo.
- **Archivos:** `src/Calce.tsx`, `src/asignacion.ts`. Borrado: `CalceEnChat.tsx`.
- **Devolver:** `git checkout web-original -- web/src/CalceEnChat.tsx`.

### 5 · La espera
- **Cambio:** los puntos del archivo viajan por el carril y entran al núcleo, que gira mientras dure la espera real, sin barra de avance inventada. Cuando llega la respuesta, el núcleo se abre y aparece la escena. Un cronómetro de verdad cuenta el tiempo de Krylov (sin lo que la persona tarda en revisar las columnas) y la respuesta separa lo que tardó la red (`tiempo_ms` del motor), leer las columnas y el viaje al servidor. Si pasan 4 segundos, dice que el servidor gratuito está despertando. Con un servidor rápido, la entrada dura al menos 0,9 s para que se vea; el cronómetro dice el tiempo real.
- **Por qué:** 5,4 segundos de una línea gris «Calculando con el modelo…» eran el peor momento de la app.
- **Texto antes:** «Calculando con el modelo…».
- **Texto ahora:** «Krylov está respondiendo / 0,8 s / La red responde en milisegundos. El resto es el viaje de tu archivo hasta el servidor y de vuelta.» · «El servidor gratuito se duerme cuando nadie lo usa. Está despertando: la primera vez tarda hasta 25 segundos.» · en la respuesta: «Krylov respondió en 0,8 s · La red, 0,04 s. Leer tus columnas, 3,1 s. El viaje hasta el servidor y de vuelta, 0,7 s.»; con los datos guardados del demo: «Respuesta guardada · 0,06 s · Es lo que tardó la red cuando se calculó esta respuesta del demo.»
- **Archivos:** `src/Viaje.tsx`, `src/reloj.ts`, `src/Coreografia.tsx`, `src/App.tsx`.

### 6 · La respuesta de la roca
- **Cambio:** la lámina 7 del deck con los datos de la respuesta: el terreno en relieve, el punto que lo recorre y la tarjeta con la decisión, las ppm de arsénico, el rango de 90% y la distribución contra el máximo que acepta la planta. Un clic en el terreno manda el punto ahí; arrastrar lo gira. La escena y su barra caben enteras en 1440×900 y 1920×1080, sin bajar. La plata salió de arriba: los costos son supuestos y están plegados más abajo («Supuestos de costo»), con lo que valdría despejar la duda dicho como una cuenta sobre costos inventados.
- **Por qué:** era una grilla plana en tres colores, con «No saber te cuesta cerca de 1,6 millones de dólares» y US$ 1.577.707 como lo más grande.
- **Texto antes:** «309 bloques están en duda. No saber te cuesta cerca de 1,6 millones de dólares.» · «Lo que te cuesta no saber / US$ 1.577.707 / Con los costos que tú pones» · «Supuestos del demo · muévelos y la respuesta cambia» · «Responde la red · En 0,04 s» · «Texto de plantilla · precalculado».
- **Texto ahora:** la tarjeta del deck («En este punto del terreno / Conviene apartar / 2.036 ppm de arsénico / entre 1.329 y 3.306 / Máximo que acepta la planta»), la barra («Krylov respondió en … · Respondió la red, que practicó con casos simulados · Banco de roca simulado: 340 pozos con arsénico y cobre. No son datos de ninguna minera.») y, plegado: «Supuestos de costo / Para decidir, Krylov compara dos costos. Son supuestos del demo, no precios de una minera: muévelos y la decisión de cada bloque cambia con ellos. / Con estos supuestos, despejar la duda valdría unos US$ … Es una cuenta sobre costos inventados: por eso no está arriba.» La interpretación dice quién la escribió: «Texto de plantilla, armado con los números de Krylov» o «Lo escribió un modelo de lenguaje (Groq) con los números de Krylov, y cada número se revisó contra la respuesta».
- **Archivos:** `src/Resultado.tsx`, `src/escena/*`, `src/Interpretacion.tsx`. Borrados: `RespuestaEnChat.tsx`, `Respuesta.tsx`, `NumeroGrande.tsx`.
- **Devolver:** `git checkout web-original -- web/src/RespuestaEnChat.tsx web/src/Respuesta.tsx web/src/NumeroGrande.tsx web/src/Chat.tsx`.

### 7 · «¿Dónde perforo?»
- **Cambio:** el paso 2 de la lámina 7: 40 lugares probados, 480 análisis rehechos y los tres mejores comparados entre sí con barras (A = 100), sin dólares. Los segundos son los de esta respuesta si salió del servidor, y si es la guardada del demo, los 1,3 s medidos (M-44): la misma cifra que dice el deck. «Perforar en A, B o C» hace bajar el taladro en la escena, el terreno se rehace desde ahí y el punto se va a ese bloque. Tecla `D` o el botón de la barra.
- **Por qué:** «Una muestra aquí vale US$ 8.943» salía de costos supuestos (K-22 a K-24), y «precalculado» contradecía al deck.
- **Texto antes:** «Una muestra más cuesta US$ 1.500. ¿Dónde perforo? / Para elegirlos, Krylov rehízo el análisis completo 480 veces · precalculado / A · Una muestra aquí vale US$ 8.943 · Cuesta US$ 1.500 · Perforar en A» y, después, «Bajó US$ 10.263 con una sola muestra.»
- **Texto ahora:** el del deck: «¿Dónde perforo? / Krylov probó 40 lugares y rehízo el análisis completo 480 veces, en 1,3 segundos. Estos son los tres donde una muestra más despeja más duda: / A 100 · B 94 · C 89 / Lo que aporta una muestra en cada lugar, con A = 100.» Y en la app: «Perforaste en A: la muestra dio 375 ppm de arsénico, lo más probable ahí. El terreno se rehízo con ella y ahora quedan 307 bloques en duda (antes, 309).»
- **Archivos:** `src/Resultado.tsx`, `src/escena/marco.ts`.

### 8 · La pared, la planta, los camiones y los túneles
- **Cambio:** cada una es la escena de su lámina (8, 9, 10 y 11), con su foco y su tarjeta, y con los datos del archivo. Sirven para otra cantidad de unidades (el archivo de prueba de la pared trae 20 sectores; el del demo, 36). En la pared, lo que cede se rotula «Proyección», como en el deck (regla 22). Las unidades se nombran en simple en los archivos del demo («Sector 25», «Camión 05»); en uno propio, con el nombre que trae.
- **Por qué:** eran un titular con dólares, tres conteos, dos deslizadores y, más abajo, una lista y una curva.
- **Texto antes (pared):** «2 sectores están en duda. No saber te cuesta cerca de 79 mil dólares.», «Conviene cerrar 5 / No sabemos: seguir midiendo 2 / Puede seguir abierto 29», «US$ 78.574», la lista «S-10 100% · S-28 97% …». Lo mismo en las otras tres, con sus cifras.
- **Texto ahora:** la tarjeta de cada lámina del deck («Sector 10 / Conviene cerrar / 4,9 h / le quedan antes de ceder / entre 2,4 y 7,4 horas / Próximas 12 horas», «Línea 3 / Conviene ajustar / 80,7% / del cobre va a recuperar», «Camión 27 / Llega a su mantención / 0,4% de riesgo de fallar antes de su mantención / Sobre 11,8%, conviene parar», «Sector 6 / Se puede reingresar / 6,4% de riesgo de temblor fuerte en 6 horas / Sobre 9,1%, sigue cerrado»).
- **Ojo:** dos ejes vienen fijos en el código del deck y no se tocaron: la pared dibuja las horas que faltan hasta 36 h, y la planta, la recuperación entre 75% y 93%. Un archivo con otra escala se dibuja recortado en la tarjeta; las cifras escritas son las reales.
- **Archivos:** `src/escena/datos.ts`, `src/Resultado.tsx`, `src/Respaldo.tsx`, `src/textos.ts`.

### 9 · Cuando Krylov no responde
- **Cambio:** la escena también lo cuenta: los puntos van hacia el núcleo, se quedan amontonados en la puerta y se apagan; el núcleo no se enciende. El motivo, en una línea grande, con qué hacer. Tecla `M`.
- **Por qué:** era una banda roja.
- **Texto antes:** «No respondo todavía: con estos datos no alcanza. / KRYLOV NO RESPONDE CON ESTE ARCHIVO / Hay 12 mediciones y hacen falta al menos 30.»
- **Texto ahora:** «Krylov no respondió / Hay 12 muestras y hacen falta al menos 30: sube un archivo con más pozos. / Subir otro archivo · Probar con el de ejemplo».

### 10 · El cierre (tecla L)
- **Cambio:** el mismo título y el mismo cuerpo de la lámina 14 del deck, con el QR a esta app.
- **Texto antes:** «Krylov / Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo. / En un segundo, porque ya practicó con millones de minas simuladas.»
- **Texto ahora:** «Decidir con el mejor modelo ya no toma horas. Toma lo que demora subir un archivo. / Krylov es el Artificial Data Scientist de la minería: seis decisiones respondidas hoy, con Bayesian Amortized Inference por dentro. / Pruébalo · krylov-krylov.vercel.app».
- **Archivos:** `src/Cierre.tsx`.
- **Devolver:** `git checkout web-original -- web/src/Cierre.tsx web/src/Particulas.tsx`.

### En toda la app
- **Tipografía:** Archivo, como el deck (`pitch/deck/deck.css`), en vez de Instrument Sans. Las tipografías se sirven desde `/deck/vendor`: se borró `public/fuentes/`.
- **Sin rótulos en mayúsculas monoespaciadas** (la clase `.dato`) ni texto con degradado (`.brillo`). La información se queda (quién respondió y qué es simulado, reglas 5 y 9); la forma cambia.
- **«La minera», no «la mina»**, y lo físico por su nombre: el rajo, la pared, la planta, los túneles; «explosión» en vez de «tronadura».
- **Sin chat:** la app es una sola historia (inicio → archivo → columnas → respuesta), una idea por pantalla. Ya no hay caja de pregunta libre que prometía más de lo que hacía ni barra lateral de conversaciones.
- **Teclas:** `1` a `5` (cada decisión con los datos del demo), `6` (el yacimiento), `M`, `L`, `F`, `D` (en la roca), `Esc` (volver al inicio).
- **Código muerto borrado:** `VistaClasica.tsx`, la ruta `/clasico` de `vercel.json`, `Chat.tsx`, `Lateral.tsx`, `SelectorModelo.tsx`, `Pie.tsx`, `Nube.tsx` y lo que solo usaban ellos.
- **Devolver todo:** `git checkout web-original -- web/ casos/` (y `servicio/ nucleo/ contratos/` para el backend).

## Backend (D-42)

| Qué | Por qué | Archivos |
|---|---|---|
| Una sola función de la posteriori (`nucleo/series.py: posteriori`), usada por la API y por `pitch/deck/datos/generar.py`; campos nuevos y opcionales: `mapa.bajo`/`mapa.alto`, `unidades[].posteriori`, `unidades[].serie`, `escena`, `donde_medir.lugares`, `propuesto_por` y, en las tarjetas, `quien` y `archivo` | La tarjeta del deck dibuja 64 cuantiles y el rango de cada bloque, y eso solo lo calculaba el deck | `nucleo/`, `contratos/CONTRATO.md` y sus ejemplos, `pitch/deck/datos/generar.py` |
| La web nueva funciona contra la API vieja: sin esos campos muestra el respaldo | Render se redespliega a mano | `src/escena/datos.ts` (`hayEscena`) |
| El estático lleva los campos nuevos, y los cinco archivos de prueba tienen su calce y su respuesta guardados (`estatico/prueba/`) | La URL pública funciona sin servidor, también con «Probar con un archivo de ejemplo» | `servicio/exportar_estatico.py`, `public/estatico/` |
| Un archivo de un extraño (Excel en español, BOM, latin-1, columnas de más, vacío, 6 MB, escala equivocada) responde siempre con una frase que dice qué pasó y qué hacer; nunca un 500 sin explicación | Lo va a subir un jurado | `nucleo/api.py`, `nucleo/tabla.py`, `servicio/app.py`, `servicio/prueba_subidas.py` |
| Código muerto: `/api/cartera`, `tiene_cartera`, `sponsor`; los comentarios que decían que Groq era solo de prueba | Revisión del código | `servicio/`, `nucleo/api.py` |
| Memoria: un análisis a la vez y sin la arena de onnxruntime. Pico con seis a la vez: 514 MB antes, 318 MB ahora (270 MB con `MALLOC_ARENA_MAX=2`) | Render gratis tiene 512 MB y se cayó dos veces | `servicio/app.py` |

## Segundo bloque (domingo, 01:30 a 01:45)

### 11 · El yacimiento, la sexta decisión
- **Cambio:** entra como sexta columna del inicio y con la tecla `6`. Es el recorrido de `pitch/deck/yacimiento.html`, sin tocarlo, dentro de un marco, con sus cuatro pasos (botones Anterior y Siguiente, o las flechas). La barra de abajo dice lo que es. En un teléfono se muestra la ficha sin el recorrido.
- **Por qué:** el deck dice seis decisiones y la app tenía cinco. Su red no corre en el servicio y su sello no pasa, así que no recibe archivos y no dice «respondió la red» (regla 5).
- **Texto ahora** (de `casos/textos.yaml`, sección `yacimiento`): «¿Dónde está el mineral? / Geólogo de exploración / Las muestras de las perforaciones: dónde se perforó, a qué profundidad y cuánto cobre trae la roca. / Ver el recorrido» · «Yacimiento simulado y respuesta calculada antes. Esta decisión todavía no recibe archivos.» · «De este modelo se cuenta solo su mapa: en yacimientos simulados nuevos, el cobre de verdad cayó dentro del rango que dio Krylov en 9 de cada 10 bloques. El resto de su comprobación todavía no pasa.» (M-63) · «El recorrido en tres dimensiones se ve en una pantalla más ancha.»
- **Archivos:** `src/Yacimiento.tsx`, `src/App.tsx`, `src/Inicio.tsx`, `src/Encabezado.tsx`, `vite.config.ts`, `casos/textos.yaml`, `servicio/respuestas.py`.
- **Devolver:** borrar `src/Yacimiento.tsx`, la sección `yacimiento` de `casos/textos.yaml` y sus usos en `App.tsx` e `Inicio.tsx`.

### 12 · El puente con el deck (tecla D del deck)
- **Cambio:** en la lámina de una decisión (7 a 12), la tecla `D` del deck abre la app en esa misma decisión (`?decision=<caso>`), con el archivo de ejemplo a un clic. En las demás láminas abre el inicio, como antes. El deck sigue abriendo con doble clic y sin internet: es una línea en `K.demo`.
- **Archivos:** `pitch/deck/js/nucleo.js` (lo único del deck que se tocó), `src/App.tsx`.
- **Devolver:** `git checkout web-original -- pitch/deck/js/nucleo.js`.

### 13 · El teléfono (390 × 844)
- **Revisado en Chrome:** inicio, columnas, espera, las respuestas de la roca y la pared, «Krylov no respondió», el cierre y el yacimiento. Nada se sale de la pantalla ni queda tapado.
- **Cambio:** el mapa de la roca ahora trae la leyenda de sus tres colores, con los rótulos del caso (antes eran tres colores sin explicar).
- **Archivos:** `src/Mapa.tsx`, `src/Respaldo.tsx`.

### Arreglos del segundo bloque
| Qué | Por qué | Archivos |
|---|---|---|
| En «¿Dónde perforo?», la barra de abajo muestra solo lo necesario para perforar | A 1440 × 900 la barra se partía en tres líneas y los botones A, B y C quedaban bajo el pliegue | `src/Resultado.tsx` |
| El título de la portada baja y se achica un poco | La «K» y la «l» de «Krylov» quedaban cortadas contra el encabezado | `escena.html` |
| Las fichas de cada pregunta suben hacia las preguntas, y el enlace dice «Subir su archivo» | Había un vacío entre la pregunta y quién la decide, y «Responder con un archivo» se partía en dos líneas | `src/Inicio.tsx` |
| La interpretación ya no habla de plata: el modelo de lenguaje no lee los costos, y un texto que los nombre sale como plantilla | Los costos son supuestos del demo; con Groq el texto volvía a decir «US$ 78.574» | `servicio/interpretar.py`, `servicio/prueba_interpretar.py` |
| Vercel también despliega cuando cambia solo `pitch/deck` | La app usa los módulos del deck: un cambio ahí cambia la app | `vercel.json` |
| Fuera `sponsor: null` de los casos y del contrato | Código muerto | `casos/*.yaml`, `contratos/CONTRATO.md` |

### Textos del segundo bloque (antes → ahora)
| Dónde | Antes | Ahora |
|---|---|---|
| Fichas del inicio | «Responder con un archivo» | «Subir su archivo» |
| Plantilla, hay que actuar | «En 5 sectores, conviene cerrar, y saber más no cambiaría la decisión.» | «En 5 sectores conviene cerrar, y saber más no cambiaría la decisión.» |
| Plantilla, qué pesa | «Lo que más pesa es error de cada lectura del radar…» | «Lo que más pesa: error de cada lectura del radar…» |
| Plantilla de la roca | «Aquí manda lo que pasa en los bloques vecinos.» | «Aquí manda: lo que pasa en los bloques vecinos.» |
| Mapa del teléfono | (sin leyenda) | «Conviene apartar · No sabemos: conviene muestrear · Puede ir a la planta» |

Para regenerar las respuestas guardadas con texto de plantilla (sin llamar a ningún modelo de lenguaje):
`ANTHROPIC_API_KEY= GROQ_API_KEY= KRYLOV_MOTOR_ESPACIAL=red KRYLOV_MOTOR_CINETICA=red KRYLOV_MOTOR_DEFORMACION=red KRYLOV_MOTOR_SISMICO=red KRYLOV_MOTOR_DESGASTE=red uv run python -m servicio.exportar_estatico`

## Tercer bloque (domingo, 01:45 a 01:55): accesibilidad y voz de los textos

Revisión WCAG 2.1 AA con la skill `accessibility-review`, medida en Chrome a 390 × 844 y a 1440 × 900 en siete vistas
(inicio, columnas, roca, pared, «no respondió», cierre y yacimiento).

| Qué se midió | Resultado |
|---|---|
| Contraste de todo el texto (4,5:1; 3:1 en texto grande) | Pasa en las siete vistas |
| Nombre accesible de botones, enlaces, selectores y deslizadores | Todos tienen |
| Foco visible con teclado | Sí: contorno de 2 px en oro o tinta |
| Idioma de la página | `es` |
| Título principal (`h1`) | Faltaba en columnas, «no respondió», las respuestas con escena y el yacimiento: agregado |
| Alto para el dedo en el teléfono (44 px) | Los enlaces de las fichas medían 26 px y ahora 47; la marca y «Supuestos de costo», 44. Las filas de la lista de unidades siguen en 30 px (pasan el mínimo de 24 de WCAG 2.2, no el de 44) |

| Qué cambió | Por qué | Archivos |
|---|---|---|
| Un motivo largo de «Krylov no respondió» se escribe en tamaño de texto, no de titular | El aviso de la escala equivocada son tres frases y llenaba la pantalla | `src/Viaje.tsx` |
| Los avisos y errores hablan todos en tercera persona («Krylov no pudo…») | Había «No pude», «No encontré», «No respondo» y «Krylov no pudo» mezclados | `src/App.tsx`, `src/api.ts`, `casos/textos.yaml` |
| Fuera la línea «Supuestos del demo · muévelos y la respuesta cambia» | Repetía el párrafo de arriba y usaba la clase de los rótulos antiguos | `src/Deslizadores.tsx`, `src/ListaUnidades.tsx` |

### Textos del tercer bloque (antes → ahora)
| Dónde | Antes | Ahora |
|---|---|---|
| Aviso al cargar | «No pude cargar las decisiones. Recarga la página.» | «Krylov no pudo cargar las decisiones. Recarga la página.» |
| Aviso del demo | «No pude abrir los datos del demo: API 500» | «Krylov no pudo abrir los datos del demo: el servidor respondió 500. Recarga la página.» |
| Aviso del ejemplo | «No encontré el archivo de ejemplo: no encontré subida_leyes.csv» | «Krylov no encontró el archivo de ejemplo: falta subida_leyes.csv. Recarga la página.» |
| Plantilla en rojo | «No respondo todavía: con estos datos no alcanza.» | «Krylov no responde todavía: con estos datos no alcanza.» |
| Plantilla en rojo | «No respondo todavía: este archivo no se parece a nada que haya visto.» | «Krylov no responde todavía: este archivo no se parece a nada que haya visto.» |
| Plantilla en amarillo | «Respondo, con un aviso: el archivo se parece a lo que practiqué, pero está cerca del borde.» | «Krylov responde, con un aviso: el archivo se parece a lo que practicó, pero está cerca del borde.» |
| Motivo en rojo | «Este archivo no se parece a nada de lo que practiqué. Prefiero no responder antes que responder mal. …» | «Este archivo no se parece a nada de lo que Krylov practicó, y prefiere no responder antes que responder mal. …» |
| Propuesta | «Propongo sacar la columna «X» y responder con las demás.» | «Krylov propone sacar la columna «X» y responder con las demás.» |
| Supuestos de costo | «Supuestos del demo · muévelos y la respuesta cambia» | (se quitó: lo dice el párrafo de arriba) |

**Queda en primera persona:** los motivos que escriben los motores en `nucleo/` («… y practiqué con bancos de hasta 600»). Son de PC 2 y están fuera de este encargo.

## Cuarto bloque (domingo, 02:05 a 02:15): la respuesta nunca queda en negro

- **Falla:** al subir `subida_sismicidad.csv` (5 sectores) la respuesta quedaba en negro. La escena de los túneles del deck (`pitch/deck/js/sismicidad.js`) está hecha para los 8 sectores del demo: con menos, un punto de la roca queda sin sector cercano y el módulo se cae al armarse («Cannot read properties of undefined (reading 'tinte')»). La API respondía bien.
- **Cambio:** si la escena avisa que falló, o no avisa que está lista en 12 segundos, la respuesta se muestra con el respaldo (la lista de unidades y la curva de la que se mira). No se tocó el deck.
- **Queda:** con un archivo de menos de 8 sectores, los túneles se ven con el respaldo y no con la escena. Arreglarlo de verdad es una línea en `pitch/deck/js/sismicidad.js` (función `cercaDe`), que este encargo no permite tocar: lo decide una persona.
- **Archivos:** `src/Resultado.tsx`, `src/escena/LaminaDeck.tsx`.

## Lo que queda pendiente

- **Sin probar:** Safari, el proyector y un teléfono de verdad.
- **Sin medir:** los cuadros por segundo de las escenas en un notebook y en un teléfono.
- **Sin hacer:** `design-critique` y `ux-copy` con sus skills (la crítica de diseño y el repaso de textos se hicieron a mano, mirando cada vista en Chrome); el repaso con Impeccable y Humanizer quedó fuera por decisión del equipo.
- **Texto flojo que sale del motor:** el examen de la pared dice «Cuando dijimos cerca de 0% de riesgo, cedió el 0%»: elige el primer tramo. Es de `nucleo/`.

## Tercer bloque (domingo, 03:00)

### 14 · El mouse manda en las cinco escenas
- **Cambio:** con el mouse sobre el modelo, la cámara deja de mecerse y la tarjeta es la de lo que se apunta (el bloque, el sector de la pared, la línea, el camión, el sector de los túneles). Arrastrar gira el modelo; con Mayús o el botón derecho, lo desplaza (en la roca solo gira). Con los camiones, el tiempo de la escena se detiene mientras se apunta a uno. Cuando el mouse sale, la vista vuelve a la suya y el recorrido automático sigue desde ahí.
- **En la pared** se puede apuntar a los 36 sectores. Los que el deck no visita muestran la decisión del motor y lo que midió el radar («24 mm · se movió en total»), con la tarjeta sin curva del deck.
- **Por qué:** quien mira un modelo pregunta por el lugar que apunta; el punto que viajaba solo se leía como azar.
- **Archivos:** `src/escena/mouse.ts`, `src/escena/marco.ts`. El deck no se tocó: allá el recorrido sigue solo.
- **No entra:** el yacimiento (tecla `6`), que es una página del deck con su giro por dentro.
- **Devolver:** borrar `src/escena/mouse.ts` y la llamada a `conMouse` en `marco.ts`.
