# Krylov · el guion del deck

> El guion para presentar `pitch/deck/index.html` de principio a fin. Las mismas frases están en las notas de cada lámina (tecla `N`).
>
> **Tiempo estimado, no cronometrado:** contado en palabras, a 150 por minuto. El cronómetro de verdad es el primer ensayo.
>
> **No es el mismo pitch de `pitch/GUION.md`**, que abre con el barco, entra a la app para las decisiones y tiene siete momentos. Este es el del deck de venta, tal como quedó después de la revisión del sábado a las 17:20. Hay que dejar uno solo.

## Lo que se vende

**Modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide.** Krylov es el Artificial Data Scientist de la minería.

**Y la idea que cambia el marco: no es una red que predice, es Generative AI para datasets.** Un LLM aprendió cómo se escribe y por eso responde cualquier texto sin volver a entrenar. Krylov aprendió cómo se generan los datos de una mina (un modelo bayesiano simula millones de datasets posibles, y una red aprende qué hay detrás de cada uno) y por eso responde cualquier dataset de esa familia. Eso es Simulation-based Inference, o Bayesian Amortized Inference. La mina ya no necesita a un data scientist que entrene un modelo para un dataset en particular.

El guion empuja esa idea en seis golpes:

1. **El valor, antes que nada** (lámina 1): en el pasado, siete horas; hoy, menos de un segundo.
2. **El cambio de paradigma** (láminas 2 y 3): Generative AI para datasets; en el pasado un modelo por dataset, hoy una red para todos.
3. **La prueba** (láminas 4 y 5): con qué practicó, y cómo se ve responder.
4. **El tamaño** (láminas 6 a 11): una mina toma cinco decisiones así todos los días, y cada una se ve.
5. **La confianza** (lámina 12): un número de 0 a 1, y el rango a la vista.
6. **El recuerdo** (lámina 13): el mensaje, el contador y el QR.

Y después del pitch, **las preguntas de quien dirige una empresa**, cada una con su lámina y su tecla (más abajo).

## La cuenta

- **367 palabras = 147 segundos de habla.**
- **14 pulsaciones** de `→` recorren las trece láminas. A 1,5 segundos por pulsación son 21 segundos.
- Habla más pulsaciones: **2:48. Quedan 12 segundos libres** en un pitch de 3 minutos. Es muy poco: lo primero que sale está en «Si falta tiempo».

| # | Lámina | Desde | Hasta | Palabras | Qué tiene que verse antes de seguir |
|---|---|---|---|---|---|
| 1 | Portada | 0:00 | 0:13 | 32 | El nombre, la frase y el camión |
| 2 | Generative AI para datasets | 0:13 | 0:32 | 44 | El LLM respondiendo «Platanus Hack 26»; Krylov respondiendo un dataset |
| 3 | En el pasado vs. hoy | 0:32 | 0:49 | 36 | Primero el pasado, dando vueltas; después «Hoy», y el contador que se dispara |
| 4 | Mundos simulados | 0:49 | 0:56 | 14 | El contador en 7.750.592 |
| 5 | Entra un archivo, sale la respuesta | 0:56 | 1:03 | 13 | La muralla llenándose de mapas |
| 6 | Cinco decisiones | 1:03 | 1:12 | 18 | Las cinco preguntas |
| 7 | Qué roca conviene procesar | 1:12 | 1:36 | 52 | Los intervalos contra el límite; después, la A con sus US$ 8.943 |
| 8 | La pared de la mina | 1:36 | 1:53 | 39 | Las horas que faltan, con su intervalo; los sectores en rojo |
| 9 | El cobre en la planta | 1:53 | 2:04 | 25 | Lo que va a recuperar cada línea, contra la meta |
| 10 | Los camiones | 2:04 | 2:14 | 21 | Los camiones pasando; uno en rojo, parpadeando |
| 11 | Los túneles | 2:14 | 2:26 | 25 | La explosión; los temblores, cada vez menos |
| 12 | Cómo sé que acierta | 2:26 | 2:38 | 27 | El 0,98 con sus cuadrados; el 0,90 con sus intervalos |
| 13 | Cierre | 2:38 | 2:48 | 21 | El contador corriendo; el QR |

## El guion

`[→]` es una pulsación. Entre paréntesis, lo que hace la pantalla.

### 1 · Portada (0:00 a 0:13)

*(ya está en pantalla al empezar: el nombre, «El Artificial Data Scientist de la minería», una frase, y un camión minero hecho de puntos)*

> «En una mina, las decisiones no esperan. Krylov es el Artificial Data Scientist de la minería: las responde al instante, con los modelos que hoy exigen horas de cálculo y un especialista.»

### 2 · Generative AI para datasets (0:13 a 0:32)

`[→]` *(arriba, a un LLM se le escribe «¿Cuál es la mejor hackathon del año 2026?» y responde «Platanus Hack 26. Por lejos.»; abajo, a Krylov le entra un dataset y sale el mapa de decisiones)*

> «Y no es una red que predice. Es Generative AI para datasets. A un LLM le preguntas cuál es la mejor hackathon del año y responde, sin que nadie lo entrene para eso. Krylov hace lo mismo con datos: subes tu dataset y responde.»

La pregunta y la respuesta del LLM están escritas a mano: es un guiño a la sala. Conviene dejar que se termine de escribir antes de seguir (unos 3 segundos).

### 3 · En el pasado vs. hoy (0:32 a 0:49)

`[→]` *(solo «En el pasado»: tres pasos que se encienden en orden y vuelven a empezar con cada dataset)*

> «En el pasado, cada dataset era empezar de cero: elegir el modelo, entrenarlo, inferir. Dos minutos cada uno.»

`[→]` *(aparece «Hoy»: tres pasos que se hacen una sola vez; después, «Inferir» late y el contador se dispara)*

> «Hoy la red se pre-entrena una sola vez, con datasets simulados. Después, cada respuesta son diez milisegundos.»

Para un jurado técnico: «Es Simulation-based Inference.» Si preguntan cuánto cuesta ese «una sola vez»: 4 horas 40 minutos, y lo hace Krylov, no la mina.

### 4 · Mundos simulados (0:49 a 0:56)

`[→]` *(remolino de terrenos simulados; el contador sube hasta 7.750.592)*

> «Más de siete millones de terrenos simulados, antes de ver un solo dataset real.»

### 5 · Entra un archivo, sale la respuesta (0:56 a 1:03)

`[→]` *(un archivo tras otro entra a la red y sale su mapa; la muralla se llena; el contador sube)*

> «Y así responde. Entra un archivo, sale la respuesta. Y otro, y otro.»

### 6 · Cinco decisiones (1:06 a 1:15)

`[→]`

> «Una mina decide esto todos los días. Cinco decisiones, cinco modelos de especialista, un solo Artificial Data Scientist.»

### 7 · Qué roca conviene procesar (1:12 a 1:36)

`[→]` *(el terreno en tres colores; a la izquierda, una barra por cada parte del terreno: su intervalo de credibilidad, contra el límite)*

> «¿Qué roca conviene procesar? Krylov entrega, para cada parte del terreno, cuánto arsénico hay, con su intervalo de credibilidad. De ahí sale la decisión, y lo que vale despejar la duda: un millón y medio de dólares.»

`[→]` *(un barrido enciende 40 columnas de luz; quedan A, B y C)*

> «Y dice dónde perforar: una muestra más en A vale cerca de nueve mil dólares.»

### 8 · La pared de la mina (1:36 a 1:53)

`[→]` *(la pared, con cada sector en el color de su decisión; a la izquierda, las horas que le faltan a cada sector que se acelera, con su intervalo)*

> «La pared de la mina se mueve. Krylov entrega cuántas horas le faltan a cada sector, con su intervalo: a este, entre dos y siete. Y el que más se movió no es ninguno de los que conviene cerrar.»

### 9 · El cobre en la planta (1:53 a 2:04)

`[→]` *(los estanques se encienden; a la izquierda, lo que va a recuperar cada línea, con su intervalo, contra la meta)*

> «¿Se está perdiendo cobre en la planta? Mirando los primeros estanques, entrega cuánto va a recuperar cada línea, con su intervalo: dos conviene ajustarlas ya.»

### 10 · Los camiones (2:04 a 2:14)

`[→]` *(los camiones pasan por los cuatro niveles de la rampa; cada uno va cambiando de verde a rojo con su desgaste)*

> «¿Qué camión paro? Con el aceite de toda la flota, entrega el desgaste con que llega cada uno a su mantención.»

### 11 · Los túneles (2:14 a 2:26)

`[→]` *(la explosión; después, los temblores en cada sector, cada vez menos)*

> «Después de una explosión bajo tierra, la roca sigue crujiendo. Krylov entrega cuántos temblores fuertes vienen en cada sector, para decidir cuándo volver a entrar.»

### 12 · Cómo sé que acierta (2:26 a 2:38)

`[→]` *(arriba, un cuadrado por decisión: casi todos verdes; abajo, una barra por valor escondido y el punto de lo que había)*

> «¿Y cómo sabemos que acierta? Cuando decidió, acertó en el noventa y ocho por ciento. Y nueve de cada diez valores reales cayeron dentro de su intervalo.»

### 13 · Cierre (2:38 a 2:48)

`[→]` *(el contador corre; la muralla de mapas se sigue llenando; el QR)*

> «Modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide. Eso es Krylov. Pruébenlo.»

## Las preguntas de quien dirige una empresa

Cada una tiene su lámina, fuera del recorrido. Se abre con su tecla desde cualquier parte; `Fin` vuelve al cierre.

| Pregunta | Tecla | La respuesta, en una frase | Lo que no hay que decir |
|---|---|---|---|
| **¿Quién lo usa?** | `Q` | «Quien toma la decisión en el turno: el geólogo, quien vigila la pared, el jefe de turno. No un data scientist.» | Que hay clientes o pilotos: no los hay |
| **¿Qué archivo recibe?** | `A` | «El que pide el modelo de cada decisión. El de la pared agrupa lecturas por sector; el de los camiones, muestras de aceite por camión.» | Que sirve cualquier archivo, o que se conecta a sensores |
| **¿Y si le subo el archivo a un LLM?** | `L` | «Un LLM no trae el modelo adentro: tendría que escribirlo y correrlo con cada dataset. Minutos, contra milisegundos. Lo probamos.» | **Que el LLM responde mal** (en la prueba acertó parecido) **o que corrió MCMC** (no alcanzó: usó atajos) |
| **¿Cómo garantizan que la inferencia es buena?** | lámina 12 | «Con dos números. Cuando decide, acierta 98 de cada 100. Y 9 de cada 10 valores reales caen dentro de su intervalo.» | «98%» a secas: es cuando decidió, y con un terreno simulado |
| **¿Cómo se monitorea en producción?** | `M` | «Cada predicción viene con su intervalo de credibilidad. Angosto, está seguro; ancho, duda, y lo dice antes de que alguien decida.» | **Que el intervalo es de 95%: es de 90%.** Ni que hay un tablero de monitoreo o alertas |
| **¿Cómo funciona por dentro?** | `0` | El diagrama: lo que se hace una vez, y lo que pasa con cada dataset | |

**Sobre la prueba con el LLM, sin adornos.** Se le entregó a Claude Fable 5.2 (con herramientas: podía escribir y correr código) el mismo archivo y el mismo examen que se toma Krylov, con 3 minutos, dos veces. Resultado: 61 y 63 de 68 muestras dentro del rango, contra 61 de Krylov. **No respondió mal.** Tardó 152 y 177 segundos contra 10 milisegundos; las dos veces escribió un programa distinto (sus estimaciones difieren hasta 459 ppm en un lugar), y una de las dos terminó con su método de respaldo. A ese ritmo, «¿Dónde perforo?» (480 análisis) tomaría unas 20 horas en vez de 1,3 segundos: eso es una cuenta. Es una sola prueba, con un archivo simulado y el computador cargado; está completa en `pitch/deck/datos/prueba_llm/`. El argumento de venta no es «el LLM no sirve»: es **al instante, igual cada vez y con sello**.

## Lo que es cierto hoy, para decirlo bien

El deck habla de las cinco decisiones como producto, y el guion también. **Lo que se diga en voz alta tiene que ser cierto en el momento de presentar.** Antes de subir al escenario se mira la tabla «Los cinco casos» de `estado/TABLERO.md`.

| Lámina | Qué había al escribir esto (sáb 21-nov, 18:05) | Qué se dice |
|---|---|---|
| 7 · Qué roca procesar | Responde la red validada. Terreno simulado | Tal cual |
| 8 · La pared | **Responde la red validada** (pasó su sello a las 17:36, con el criterio de D-39; a las 16:10, con el anterior, no pasaba). Pared simulada | Tal cual. Si preguntan por la validación: «pasó hoy; todavía falta compararla con el método lento» |
| 9 · El cobre | **Responde la red validada** (pasó su sello a las 17:09). Planta simulada | Tal cual |
| 10 · Los camiones | El motor no tiene red. La lámina dice qué entrega Krylov, sin gráfico ni cifras | «Entrega el desgaste…» describe el producto; si preguntan, «esa red todavía no está» |
| 11 · Los túneles | La red está entrenando. Igual que los camiones | Igual; entra si pasa antes de las 20:30 |

Cuando un motor empieza a responder, se vuelve a correr `pitch/deck/datos/generar.py` y su lámina pinta cada unidad con el color de su decisión, con sus cuentas; ahí la frase en presente es cierta.

**Si preguntan, se responde con la verdad:**

- **«¿Por qué 0,90 y no 1?»** «Porque prometemos un rango de 90%. Si acertara siempre, el rango sería demasiado ancho y no serviría para decidir.»
- **«¿Y con datos reales?»** «138 de 155 mediciones escondidas dentro del rango, escondiendo de a un quinto. En la partición que muestra la app, 24 de 31.» (0,89 y 0,77: los dos son ciertos.)
- **«¿Entonces es un LLM?»** «No. Se parece en una cosa: se entrena antes, una vez, y después solo se usa. Lo que aprendió no es lenguaje: es el modelo estadístico de cada decisión, simulando millones de datasets.» (En la app sí hay un modelo de lenguaje, pero solo propone qué columna es cuál y redacta el texto; ningún número sale de él.)
- **«¿Responde cualquier dataset?»** «Cualquiera de la familia con que practicó: la misma decisión, dentro de los tamaños que simuló. Si el archivo no se parece a nada que haya visto, lo dice y no responde.»
- **«¿Y entrenar no cuesta?»** «Sí: 4 horas 40 minutos, una vez, y lo hacemos nosotros. En la lámina 3 se ve: durante ese rato el método de siempre va ganando. Después de eso, cada dataset cuesta 10 milisegundos.»
- **«¿Esos datos son de una mina?»** «No: son archivos de demostración, simulados con la misma física. Con datos reales públicos, el motor del terreno dejó 24 de 31 mediciones escondidas dentro del rango que dio.» (M-13: 77%, no 90%.)
- **«¿Las cinco funcionan hoy?»** Lo que diga el tablero. «La de la roca está validada; las otras cuatro son motores más chicos que [están entrenando / ya responden].»
- **«¿Por qué 90% y no 95%?»** «Porque es el intervalo con que validamos la red: de cada diez, nueve aciertan. Se puede entregar el de 95%; hay que volver a validarlo.»
- **La pared y los túneles:** «Krylov apoya la decisión de un especialista; no la reemplaza.»

## De dónde sale cada número que se dice

| Se dice | Cifra |
|---|---|
| «siete horas» y «menos de un segundo» (lámina 5) | M-10: 26.699 s = 228 × 117,1 s; M-09: 0,69 s |
| «228 análisis» | M-08 |
| «más de siete millones de terrenos simulados» | M-01: 7.750.592 |
| «cerca de nueve mil dólares» | M-46: US$ 8.943, con el costo supuesto K-24 |

En pantalla, además:

- **Lámina 3:** 2 minutos por dataset (M-25) y 10 milisegundos por dataset (`latencia_ms` del sello). Los dos contadores cuentan lo que la animación muestra: no son cifras.
- **Lámina 5:** 10 milisegundos y 2 minutos por análisis; 228 análisis en 0,69 s.
- **Lámina 7:** 147, 309 y 568 partes del terreno, de 1.024 (M-40), US$ 1.577.707 (M-41), US$ 1.500 (K-24), 480 análisis (M-43).
- **Lámina 7:** además, los intervalos de credibilidad de 90% de 13 partes del terreno (sin cifras escritas: son barras).
- **Lámina 8:** 5, 2 y 29 sectores; US$ 78.574 (costos supuestos K-31 y K-32); las horas que faltan para seis sectores, con su intervalo (por ejemplo, «2,4 a 7,4 h»). Respuesta de la red de `deformacion`, con sello (17:36).
- **Lámina 9:** 2, 3 y 3 líneas; US$ 8.809; la recuperación final de cada línea con su intervalo (por ejemplo, «78 a 82%»), contra la meta de 84% (K-41). Respuesta de la red de `cinetica`, con sello.
- **Las cifras de las láminas 8 y 9 no tienen fila en `CIFRAS.md`** (M-51 las tenía pendientes; los motores ya corrieron): hay que registrarlas.
- **Láminas 10 y 11:** la magnitud del temblor más fuerte del archivo (1,2).
- **Lámina 12:** 0,98 (700 de 715 decisiones correctas, y 309 «no sabemos»: M-54, terreno simulado); 0,90 (61 de 68 valores escondidos dentro de su intervalo de 90%); 500 ppm (K-21).
- **Lámina 13:** el contador, que es una cuenta (segundos del pitch ÷ 10 ms).
- **Láminas de preguntas:** las filas de `datos/demo/leyes.csv` y `flota.csv`; entre 30 y 400 muestras; y la prueba con el LLM (61, 61 y 63 de 68; 10 ms, 152 s y 177 s; 459 ppm; 1,3 s de M-44; «unas 20 horas» y «15.000 veces», que son cuentas).

## Si falta tiempo

Quedan 12 segundos de margen. Si el ensayo se pasa, sale en este orden:

1. **La lámina 4** (mundos simulados), 7 segundos: la lámina 3 ya lo dijo.
2. **Las láminas 8 a 11 cuyo motor no responda**, 9 segundos cada una.
3. **El segundo paso de la lámina 7** («¿Dónde perforo?»), 7 segundos.

La lámina 12 no se saca: es la que responde «¿y cómo sé que acierta?» antes de que lo pregunten.

## Si sobra tiempo o si preguntan

Sobran 12 segundos: no sobra nada. Si en el ensayo queda holgura, conviene gastarla en la lámina 3, dejando que el contador de «Hoy» corra un par de segundos.

- **Tecla `D`: la demo real**, encima de las láminas. Necesita internet.
- **Teclas `Q`, `A`, `L`, `M`:** las láminas de preguntas (arriba).
- **Tecla `0`: cómo funciona.** Bayesian Amortized Inference en dos mitades, con los números del sello del motor.
- **Lámina 7:** arrastrar con el mouse gira el terreno.

## Si algo falla

| Falla | Qué se hace |
|---|---|
| El navegador no abre el deck o se ve mal | `pitch/deck/respaldo/krylov-deck.pdf`: las dieciocho láminas en su estado final |
| Una animación se traba | `P` la pausa; `→` sigue |
| No hay internet | Nada cambia, salvo la tecla `D` |
