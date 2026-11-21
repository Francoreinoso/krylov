# Krylov · Plan de trabajo (pivote a minería)

Platanus Hack 26, Santiago, track Simulaciones. Escrito el sábado 21 de noviembre a las 12:10. **Reemplaza al plan final de las 03:00** (cuatro tarjetas de industrias distintas). La decisión es D-37; la historia del plan anterior está en git (tags `h0` y `h1`) y en `DECISIONES.md`.

> **Esto es una hackathon.** Proyecto chico, tiempo acotado, se vende con un pitch corto. **El producto se termina el sábado a las 18:00.** Desde ahí solo se itera el demo y el pitch. El plan no depende de contactar a nadie. Ante la duda: lo más simple que se vea bien en el demo, y que la simulación se vea en pantalla.

Fechas fijas: producto terminado sábado 18:00 · tope de redes sábado 20:30 · entrega domingo 08:00 · cierre de repositorios domingo 08:30 · presentaciones generales 09:30 · finales 12:00.

## 0. En una página

**Qué es Krylov.** El **data scientist artificial de la minería**. Le das los datos de una decisión de la mina y te dice qué conviene hacer, **cuánto te cuesta no saber** y **dónde conviene medir más**. Y avisa cuando los datos no sirven.

**El problema, en simple.** En una mina, las decisiones grandes no esperan: a dónde va la roca que se acaba de romper, si un sector se evacúa, qué camión se detiene. Los modelos que de verdad miden el riesgo tardan horas en cada vuelta, y hay que rehacerlos con cada dato nuevo. Por eso hoy se elige entre dos males: un promedio rápido que esconde el riesgo, o un cálculo serio que llega cuando la decisión ya se tomó.

**Cómo funciona, en una frase.** Hace el cálculo difícil antes: para cada decisión tiene reglas con que inventa minas, practica con millones de esos casos simulados, donde la respuesta correcta se conoce, y por eso después responde al instante.

**Por qué se llama así.** Por Alekséi Krylov, ingeniero naval que a comienzos del 1900 calculó por adelantado qué hacer con un barco averiado, para que el capitán decidiera en segundos. Calcular antes, decidir al instante.

**Qué se ve en el demo.** Cinco decisiones de una mina. Se abre la primera: un piso del rajo recién tronado, en tres colores (este bloque puede ir a la planta, este conviene apartarlo porque trae demasiado arsénico, en este no sabemos), con el número de lo que cuesta no saber y deslizadores de costos que cambian todo en vivo. Después, **«¿Dónde perforo?»**: tres pines con plata; un clic simula la muestra y el mapa cambia. Después, las otras cuatro, quince segundos cada una: el muro que se mueve, la planta que pierde cobre, el camión que va a fallar, el sector donde la gente espera para volver a entrar. En cada una se ve una curva con su abanico de duda.

**La frase que el jurado tiene que poder repetir.** *«Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo. En un segundo, porque ya practicó con millones de minas simuladas.»*

**Qué cambió respecto del plan de las 03:00**, en cinco líneas:

1. Una sola industria: minería. Cinco decisiones en vez de cuatro tarjetas sin relación.
2. Se parte de lo que ya funciona: el motor espacial validado, ahora con un banco minero. Es el caso estrella.
3. Cuatro motores nuevos y chicos (5 a 7 parámetros) que comparten un andamio y entrenan en dos rondas de 100 minutos.
4. La forma de las respuestas no cambia: mapa o lista en tres colores. Se agrega la curva con su abanico.
5. Se cortaron la cartera y los motores de rotación, inasistencias y crédito.

### 0.1 El objetivo: ganar, con los criterios oficiales

| Criterio | Peso | Qué dice | Cómo lo cumplimos |
|---|---|---|---|
| **Aspecto técnico** | 25% | Calidad de la ingeniería y de las decisiones de diseño. **El jurado puede apoyarse en una revisión automatizada del código** | Inferencia basada en simulación amortizada: cinco modelos generativos escritos con sus ecuaciones, un simulador y una red por modelo, validada con SBC, contra un MCMC de referencia y con una verdad escondida; un andamio común para los modelos jerárquicos; contrato entre módulos; pruebas por módulo; README técnico |
| **Ambición** | 20% | Qué tan altos fueron los objetivos para las 36 horas | Cinco decisiones de la gran minería; redes entrenadas en dos notebooks sin ventilador; un pivote completo a mitad de la hackathon con el producto en línea |
| **Ejecución** | 20% | Qué tan pulido, coherente y funcional es el resultado | Recorrido sin esperas; URL pública que no se cae; cada tarjeta dice la verdad sobre quién responde |
| **Impacto** | 20% | El valor que entrega a sus usuarios, **la profundidad por sobre el alcance** | Una industria, y un caso llevado hasta el final: decidir bloque por bloque, saber cuánto cuesta la duda y dónde perforar para despejarla |
| **Originalidad** | 15% | Qué tan sorprendente es | No es un tablero con promedios ni un chat con un archivo: dice cuánto no sabe y cuánto vale averiguarlo |

Otras tres cosas de las bases: **solo llegan a la final los equipos con una demostración funcional**; hay 12 equipos en Simulaciones, de 48; y la página de votación muestra la descripción, el video del pitch y la URL pública, que tiene que seguir viva días después. No hay criterio que premie el modelo de negocio: queda en una frase y una lámina de respaldo.

### Conceptos en un minuto

Están completos en `GLOSARIO.md`, que además trae «Minería en simple». Los que más se usan:

| Concepto | Qué significa aquí |
|---|---|
| **Data scientist artificial** | Programa que hace el trabajo de un analista de datos: elige el método, lo aplica, dice qué conviene hacer y cuándo los datos no sirven |
| **Simular** | Inventar datos con reglas conocidas. Krylov practica con casos simulados, donde la respuesta correcta se conoce |
| **Amortizar** | Pagar el costo de cálculo una sola vez, por adelantado, para que cada respuesta sea instantánea |
| **Motor** | Las reglas con que Krylov inventa casos de una decisión, más la red que practicó con ellos. Hay cinco |
| **Caso** | Una decisión de la mina resuelta con un motor, un archivo de datos y sus costos. Cada tarjeta es un caso |
| **Unidad** | Aquello sobre lo que se decide: un bloque, un sector del muro, una línea de la planta, un camión |
| **Tres colores** | Son decisiones: «conviene actuar», «no hace falta», «no sabemos si conviene» |
| **Lo que te cuesta no saber** | La plata que se ahorraría si la duda se despejara antes de decidir |
| **¿Dónde perforo?** | Los tres lugares donde una muestra más vale más plata |
| **Curva** | Lo medido en una unidad y el abanico de lo que Krylov cree que viene |
| **Examen** | Lo que pasó cuando Krylov respondió sobre datos cuya respuesta estaba escondida |
| **Hito (H4 a H6)** | Hora fija en que se mide contra un criterio escrito y se decide seguir o cortar |

## 1. El producto

### 1.1 Qué reemplaza

Hoy cada una de estas decisiones la toma un especialista (un geólogo, un geomecánico, un jefe de mantención, un metalurgista) con lo que alcanza a calcular en el tiempo que tiene: un promedio, una regla fija, su experiencia. El modelo que mediría bien el riesgo existe, pero necesita a un experto en estadística y horas de cómputo, y la decisión no espera.

Krylov no reemplaza al especialista: le entrega, en el tiempo que sí tiene, lo que ese modelo diría. Con el método de siempre cada análisis tarda minutos u horas; Krylov ya practicó con millones de casos simulados y responde en milisegundos, cada vez que llega un dato nuevo.

### 1.2 Las cinco decisiones y sus motores

| # | Caso | La decisión, en simple | Qué modelo es, en palabras | Por qué el método de siempre es lento | Al sábado 18:00 |
|---|---|---|---|---|---|
| 1 | `leyes` | Después de cada tronadura: ¿este bloque va a la planta o se aparta por arsénico? ¿Dónde tomo una muestra más? | La roca vecina se parece, más en una dirección que en otra, y cada muestra trae error | «¿Dónde perforo?» exige rehacer el análisis cientos de veces | **Red validada. No se corta.** Motor `espacial` |
| 2 | `taludes` | El radar dice que el muro se mueve: ¿es ruido o va a ceder? ¿Cuánto falta? | Cada sector se mueve a su ritmo; algunos se aceleran, y la forma de esa aceleración dice cuánto falta | Hay que probar, sector por sector, las dos historias posibles y todas las fechas de falla | Red o precalculado. Motor `deformacion`, ronda 1 |
| 3 | `flotacion` | ¿Se me está yendo cobre al relave? ¿Qué línea ajusto? | El cobre flota rápido al principio y cada vez más lento; cada línea tiene su ritmo y su tope | Con pocas celdas medidas, muchas curvas distintas calzan igual de bien | Red o precalculado. Motor `cinetica`, ronda 1 |
| 4 | `flota` | ¿Qué camión paro antes de que falle en la rampa? | Cada camión acumula un desgaste que no se ve, a saltos y sin retroceder; lo que se mide es una huella con error | Una incógnita por cada tramo de cada camión | Red, precalculado o fuera. Motor `desgaste`, ronda 2 |
| 5 | `sismicidad` | Tras una tronadura bajo tierra: ¿puede volver a entrar la gente? | Cada sismo sube por un rato la probabilidad del siguiente; los grandes, más | Cada sismo nuevo obliga a recalcular toda la historia | Red, precalculado o fuera. Motor `sismico`, ronda 2 |

Cada motor tiene su versión con el método lento de siempre (MCMC), que se calcula una vez para el archivo del demo y se guarda: es la vara para validar la red y el plan B de la tarjeta. Una tarjeta que sale del plan B se rotula «precalculado» y el guion no dice que responde la red. El detalle técnico está en la sección 11.

**Lo que cada motor nuevo NO es todavía** (y se dice): el modelo completo del documento técnico del equipo. `deformacion` no lleva el muro entero con miles de nodos; `cinetica` no resuelve las ecuaciones de varias fases; `desgaste` no cruza telemetría; `sismico` no usa la ubicación de cada sismo; `espacial` no separa dominios geológicos ni trabaja en tres dimensiones. Son la versión que cabe en una tarde, hecha para que la idea se vea funcionando.

### 1.3 Las tres vistas

**Vista 1 · Inicio: chat «¿Qué decisión tienes que tomar?»**
- Cinco tarjetas, en el orden de `casos/INICIO`, cada una con su pregunta en palabras y una línea que explica el reloj («hay que decidir antes de que la pala cargue el bloque»).
- Se adjunta un archivo: el del demo viene precargado; también se puede subir uno propio. Un modelo de lenguaje propone qué columna va en cada papel y el usuario lo confirma.
- Abajo, en chico: «Datos simulados con la misma física. No son datos de ninguna mina.»

**Vista 2 · Respuesta.** Es la pantalla principal. De arriba abajo:
1. **Titular en una frase.** «[N] bloques están en duda. No saber te cuesta [plata].»
2. **Lo que te cuesta no saber**, en grande.
3. **Dos deslizadores de costos**, con su pregunta en palabras. Al moverlos cambian los colores, el titular y el número, sin espera. Dicen «supuesto».
4. **Las unidades en tres colores.** En `leyes`, un mapa del banco. En los otros cuatro, una lista ordenada con una barra por unidad que muestra su rango y la línea del punto de corte.
5. **La curva** (casos de lista). Al elegir una unidad: los puntos medidos, la línea de «ahora», el abanico de lo que viene y la línea del límite. En `taludes`, además, una marca con «cuánto falta» y su rango.
6. **Qué pesa**, con sus etiquetas.
7. **El examen.** «Escondimos [68] muestras y [61] cayeron dentro del rango que dimos.» En datos simulados dice «con datos simulados».
8. **Pie:** qué motor respondió, de dónde vienen los datos y, si la respuesta salió del plan B, el rótulo «precalculado».

En `leyes`, además:

9. **Botón «¿Dónde perforo?».** Aparecen tres pines, cada uno con lo que vale muestrear ahí, y una línea: «Para saberlo rehíce [N] análisis completos en [X] segundos». Clic en un pin: «sale bajo / medio / alto». Se elige uno y el mapa, el número grande y los pines cambian.

**Vista 3 · Sabe cuando no sabe.** Es un estado de la vista 2. Se carga un archivo que no sirve (tecla `M`): un banco con muy pocos pozos, o una serie demasiado corta. Banda roja con el motivo en una línea: «No respondo todavía: con estos datos no alcanza». Donde el motor tenga nube, se dibuja con el archivo afuera.

Reglas de pantalla: nada tarda más de dos segundos, ninguna palabra de estadística ni de minería sin explicar, todo lo simulado rotulado, toda cifra registrada en `pitch/CIFRAS.md`.

### 1.4 Dónde se ve la simulación

Es el nombre del track. Aparece cinco veces y ninguna se corta.

| Dónde | Qué se simula | Qué se dice |
|---|---|---|
| «¿Dónde perforo?» | Cientos de resultados posibles de una muestra que todavía no se toma | «Imaginó [N] resultados y rehízo el análisis para cada uno» |
| El clic en un pin | Una muestra | «Perforo, sale alto, y el mapa cambia» |
| El abanico de cada curva | Los futuros posibles de un muro, de un camión o de una línea | «Cada línea del abanico es un futuro que calza con lo medido» |
| El rótulo de los datos | El banco, la flota y el muro del demo | «Los inventamos con reglas físicas y escondimos la respuesta: Krylov no la vio» |
| El cierre | Los casos del entrenamiento | «Practicó con [N] millones de minas simuladas» |

### 1.5 Lo que se cortó y la hoja de ruta

Cortado en D-37: la cartera; las tarjetas de rotación, inasistencias y crédito con sus motores; los casos con nombre de sponsor. Sigue cortado lo de D-17: voz, WhatsApp, caja de pregunta libre.

Hoja de ruta, siempre rotulada: los modelos completos del documento técnico; la conexión directa a los sistemas de una faena (laboratorio, radar, despacho de camiones, red sísmica); tres dimensiones; más decisiones (tronadura, molienda, agua).

## 2. Para quién

### 2.1 A quién se le habla

**No sabemos quién va a evaluar.** Puede ser un fundador de software, un inversionista o alguien de un sponsor. Casi seguro no es minero y no estudió estadística. El pitch y la pantalla se escriben para esa persona: cada decisión se cuenta con algo que cualquiera imagina (un camión detenido en una subida, un muro que se mueve, gente esperando para volver a entrar) y cada palabra del rubro se explica la primera vez. Si hay un minero en la sala, tiene que poder decir «así es».

### 2.2 Sponsors

Ya no hay casos con nombre de sponsor. Se dice que usamos Anthropic (un modelo de Claude propone el calce y escribe la interpretación; el producto se construyó con Claude Code), Vercel (la web) y Render (la API), y solo lo que funcione a las 18:00.

### 2.3 Quién lo usaría

El área de una faena que toma una de estas decisiones todos los días: geología de corto plazo (leyes), geomecánica (taludes, sismicidad), mantención (flota), planta (flotación). No hay clientes ni conversaciones, y no se dice que las haya.

## 3. El negocio, en una lámina

No lo puntúa ningún criterio. Va en una frase si sobra tiempo y en una lámina de respaldo.

- **Por qué minería:** es la industria más grande de Chile y sus decisiones diarias mueven mucha plata; las cifras, con su fuente, están en `pitch/CIFRAS.md`, sección «La minería».
- **Qué se vende:** una decisión a la vez. Cada motor es un producto para un área de la faena.
- **Precio:** sin hipótesis todavía. Si preguntan: «No lo sabemos. Lo primero sería probar un motor con datos históricos de un área».
- **Lo que todavía no es ventaja:** la técnica es pública y se puede copiar. Hoy la ventaja es el equipo, que investiga exactamente en esto, y llegar primero. Se dice así.

## 4. El show

### 4.1 Formato

- **Presentaciones generales:** domingo 09:30 a 11:30. **Finales:** 12:00 a 14:30.
- **Duración del pitch:** 3 minutos (J-04, respuesta de la organización). Se confirma en la charla «Cómo hacer un buen demo» del sábado a las 20:00.
- El guion existe en dos largos: 3 minutos y 90 segundos. Texto completo en `pitch/GUION.md`; el del deck, en `pitch/PITCH_v2.md`.

### 4.2 Los momentos

| # | Tiempo | Momento | Pantalla | Criterio que toca |
|---|---|---|---|---|
| 1 | 0:00 a 0:20 | El nombre: Krylov y el barco. «Calcular antes, decidir al instante» | Deck, lámina 1 | Originalidad |
| 2 | 0:20 a 0:45 | El problema: en una mina las decisiones no esperan y los modelos serios tardan horas. La carrera: los mismos análisis, menos de un segundo contra horas | Deck, lámina 2 | Técnico, ambición |
| 3 | 0:45 a 1:00 | Cómo: practicó con millones de casos simulados, una noche, en un MacBook | Deck, lámina 3 | Técnico |
| 4 | 1:00 a 1:25 | **Decisión 1, el banco:** tres colores, lo que cuesta no saber, deslizador | App o deck, mapa | Impacto |
| 5 | 1:25 a 1:45 | **«¿Dónde perforo?»:** pines, análisis rehechos, el clic | App o deck, mapa | Técnico, impacto |
| 6 | 1:45 a 2:40 | **Las otras cuatro decisiones**, unos 14 segundos cada una, con su curva: el muro, la planta, el camión, el reingreso | App, cuatro tarjetas | Ambición, impacto |
| 7 | 2:40 a 3:00 | Cierre: no reemplaza al especialista, le da el cálculo a tiempo. La frase y el QR | Deck, cierre | Ejecución |

**Versión de 90 segundos:** momentos 1 (dos frases), 2, 4 y 5, una frase que nombra las otras cuatro, y el cierre. **Lo primero que se corta es el momento 6, tarjeta por tarjeta** (primero `flota`, después `sismicidad`). **El mapa y «¿Dónde perforo?» no se cortan nunca.**

De cada tarjeta del momento 6 se dice la verdad: «esta ya responde al instante» o «esta la calculamos con el método lento y la estamos entrenando». Las variantes están escritas en `pitch/GUION.md`.

### 4.3 El recorrido, clic por clic

Esto es lo que PC 1 tiene que dejar funcionando sin tocar el teclado más de lo indicado.

| # | Acción | Qué aparece | Tiempo máximo |
|---|---|---|---|
| 1 | Se abre la app | Chat con las cinco decisiones y sus archivos del demo precargados | ya abierta |
| 2 | Tecla `1` (o clic en «Leyes y arsénico») | Mapa del banco en tres colores, número grande, deslizadores | 1 s |
| 3 | Arrastrar el deslizador «mandar a la planta un bloque con demasiado arsénico» | Colores, titular y número cambian mientras se arrastra | inmediato |
| 4 | Tecla `D` (o clic en «¿Dónde perforo?») | Tres pines con plata y el conteo de análisis rehechos | 2 s |
| 5 | Clic en el pin A, luego en uno de los tres resultados | El mapa, el número y los pines cambian | 2 s |
| 6 | Tecla `2` | Taludes: lista de sectores en tres colores; el sector más urgente abierto con su curva, el abanico y «cuánto falta» | 1 s |
| 7 | Tecla `3` | Flotación: líneas en tres colores; la curva de la línea en duda | 1 s |
| 8 | Tecla `4` | Flota: camiones en tres colores; la curva del camión que conviene parar | 1 s |
| 9 | Tecla `5` | Sismicidad: sectores en tres colores; la curva del sector en duda | 1 s |
| 10 | Tecla `M` | Un archivo que no alcanza: banda roja con el motivo | 1 s |
| 11 | Tecla `L` | Lámina de cierre con la frase y el QR | inmediato |

Las teclas existen para no depender del mouse en un escenario. Todo el recorrido funciona sin internet y también en la URL pública en modo estático. Una tarjeta que no tenga respuesta real a las 17:30 sale del inicio y su tecla no hace nada.

### 4.4 Palabras

| No se dice | Se dice |
|---|---|
| posterior, distribución | «rango creíble», «lo que de verdad sabemos» |
| valor de la información | «lo que te cuesta no saber», «cuánto vale averiguarlo» |
| inferencia amortizada | «ya practicó con millones de minas simuladas» |
| calibración | «cuando dimos un rango, la respuesta cayó adentro 9 de cada 10 veces» |
| MCMC | «el método lento de siempre» |
| modelo generativo, prior | «las reglas con que Krylov inventa minas» |
| *ore control*, *blasthole* | «decidir a dónde va cada bloque», «pozo de tronadura» |
| *rockburst*, *panel caving* | «estallido de roca», «minería subterránea» |
| CAEX, RUL | «camión», «cuánto le queda» |
| *rougher*, cinética | «línea de flotación», «qué tan rápido flota el cobre» |
| GB-InSAR, fluencia terciaria | «radar», «el muro se mueve cada vez más rápido» |
| «evita accidentes», «predice el derrumbe» | «ayuda a decidir a tiempo», «dice cuánto falta, con su rango» |
| simular, simulación | se dicen tal cual, y a menudo: es el nombre del track |

### 4.5 Láminas

El pitch parte en el deck (`pitch/deck/`) y entra a la app para las decisiones. Detalle lámina por lámina en `pitch/LAMINAS.md`. En corto: 1 el barco; 2 la carrera; 3 minas simuladas; 4 el banco; 5 «¿Dónde perforo?»; 6 cinco decisiones; 7 cierre con QR; y de respaldo: técnica, qué existe hoy, negocio.

### 4.6 Si algo falla en vivo

| Falla | Qué se hace |
|---|---|
| No hay internet | Nada cambia: el demo corre en el computador que presenta. Se ensaya así |
| La app se cae | Video de respaldo en la pestaña de al lado, narrado en vivo |
| «¿Dónde perforo?» tarda más de 2 segundos | Se sirve el resultado precalculado, que está siempre |
| Una tarjeta del momento 6 no carga | Se salta a la siguiente; ninguna depende de otra |
| Se acaba el tiempo | Se salta al cierre. El momento 6 es prescindible; el 4 y el 5 no |

## 5. Preguntas difíciles

| Pregunta | Respuesta |
|---|---|
| ¿Son datos reales de una mina? | No, y la pantalla lo dice. No hay datos públicos de faenas para estas decisiones, así que inventamos cada archivo con las mismas reglas físicas, con una respuesta escondida que Krylov no ve. El motor del mapa está probado además con datos reales públicos de metales en un suelo: escondimos 31 mediciones y 24 cayeron dentro del rango que dio |
| ¿Hablaron con alguna minera? | «Todavía no, y no lo vamos a inventar. Es lo primero que haríamos el lunes» |
| ¿Esto reemplaza al geólogo o al geomecánico? | No. Le entrega, en el tiempo que tiene para decidir, lo que el modelo completo diría. La decisión sigue siendo suya |
| ¿Qué existe hoy y qué es lámina? | Existe una app en línea con [N] decisiones. En [las que hayan pasado] responde una red entrenada hoy; en [las demás] la respuesta se calculó con el método lento y la pantalla dice «precalculado». Los modelos completos y la conexión a sensores son hoja de ruta |
| ¿En qué se diferencia de un tablero o de subirle el archivo a un chat? | Un tablero muestra lo que pasó. Un chat escribe un programa distinto cada vez y no sabe cuánto se equivoca. Krylov da la decisión, la duda medida en plata y dónde medir para despejarla; y el modelo de lenguaje solo cuenta el resultado: no pone ningún número |
| ¿Dónde está la simulación? | En todo. Cada motor practicó con millones de casos inventados con reglas conocidas. Para decir dónde perforar, simula cientos de resultados de una muestra que todavía no existe. Y cada abanico es un conjunto de futuros simulados que calzan con lo medido |
| ¿Por qué cinco decisiones y no una bien hecha? | Hay una bien hecha: la del banco, validada y con «¿Dónde perforo?». Las otras cuatro muestran que la misma idea sirve en toda la mina; de cada una decimos en qué estado está |
| ¿Y si se equivoca en algo de seguridad? | Por eso da un rango y no un número, por eso dice «no sabemos» cuando no alcanza, y por eso la decisión es de una persona. No prometemos evitar accidentes |
| ¿Esto ya existe? | La técnica es investigación activa (inferencia amortizada). En minería se usan modelos de este tipo fuera de línea, en horas. No conocemos un producto que los entregue al instante para estas decisiones; no revisamos todo el mercado y no nombramos a nadie |
| ¿Qué impide que lo copien? | Hoy, poco: el equipo, que investiga en esto, y llegar primero |
| ¿Suben cualquier archivo? | Cualquiera con la forma de una de las cinco decisiones: eliges cuál, y Krylov propone qué columna es qué. Si no calza, no responde y dice qué falta |
| ¿Mis datos salen de la faena? | No hace falta: los motores son chicos y pueden correr adentro. Al modelo de lenguaje van los nombres de las columnas con un resumen y los números de la respuesta; nunca filas. Se puede apagar |

Técnicas, para quien las haga:

| Pregunta | Respuesta |
|---|---|
| ¿Esto es inferencia basada en simulación de verdad? | Sí. Cada decisión tiene un modelo generativo explícito, un simulador, y una red entrenada solo con simulaciones para entregar el posterior (NPE con flujos normalizadores condicionales). En los modelos jerárquicos, amortización factorizada: un flujo para los parámetros globales y otro, chico, para los de cada unidad. Está en el README y en el código |
| ¿Por qué no usar MCMC y listo? | Lo usamos, como referencia. En el banco, rehacer los análisis de «¿Dónde perforo?» toma [horas] con el método lento y [segundos] con la red. Y estas decisiones se repiten con cada dato nuevo |
| En el modelo espacial hay atajos para no rehacer cada análisis | Sí, y los conocemos. La red no depende de ellos: funciona igual en modelos donde no existen. Lo que medimos y decimos es rehacer cada análisis completo |
| ¿Cómo saben que la red no se equivoca? | Cuatro chequeos por motor: SBC y cobertura en simulaciones nuevas (global y por unidad); contra el MCMC en datasets simulados y en el del demo; la verdad escondida del archivo; y el semáforo cuando el archivo cae fuera de lo simulado |
| ¿Y los motores que no pasaron? | Esas tarjetas muestran el resultado del MCMC, calculado antes, y dicen «precalculado». No decimos que ahí responde la red |
| Sus modelos son más simples que los que se usan en la industria | Sí, a propósito. Anoche un modelo de 7 parámetros pasó su validación y uno de 32 no. Hicimos cuatro motores chicos que se pueden validar en una tarde; los completos son hoja de ruta |
| El modelo de sismos no usa la ubicación | Correcto: es temporal, por sector. La versión con ubicación es hoja de ruta |
| ¿Por qué no un modelo amortizado ya entrenado? | Los buscamos (sáb 10:50): existen para familias fijas o genéricas y ninguno cubre estos modelos |
| ¿Qué no hace todavía? | Tres dimensiones, dominios geológicos, más de 400 muestras por banco, ubicación de los sismos, telemetría de los camiones, conexión a sensores. Está en la lámina técnica |

## 6. Plan hora a hora

P son las tareas de PC 1 (producto), A las de PC 2 (amortización) y S las de PC 3 (seguimiento). **La numeración parte en 21** para no chocar con lo hecho antes del pivote. Cada tarea tiene un identificador, una hora tope, una duración, un entregable y una forma de saber que está lista. Las duraciones suponen que Claude Code escribe el código y la persona revisa.

Regla de corte: **si una tarea lleva el doble de su duración, se corta o se simplifica, se anota en `estado/` y se sigue.** A las 18:00 el producto está terminado con lo que haya.

**Regla de adelanto (D-29): las horas de este plan son topes, no horas de inicio.** Cada tarea se empieza apenas existen sus insumos, en el orden de la lista de su rol. Si falta un insumo, se construye contra el ejemplo fijo, datos simulados o la red sin entrenar, se anota «pendiente de <insumo>» y se pasa a la siguiente. No se adelanta lo que no depende de la hora: un entrenamiento por computador; el MCMC nunca encima de un entrenamiento; los tiempos del guion se miden sin nada entrenando; un motor responde con `red` solo después de `validar-motor`; lo que exige a una persona.

### 6.1 Vista general

| Bloque | PC 1 · producto | PC 2 · amortización | PC 3 · seguimiento |
|---|---|---|---|
| **12:10 a 12:30** Pivote | Lee D-37 y `PC1_PRODUCTO.md` | A-21: detiene `estados` | S-21, S-22: avisa, detiene `jerarquico` |
| **12:30 a 14:30** | P-21 a P-23: inicio minero, `leyes` real, la curva | A-22 a A-25: `leyes`, el andamio de series, `cinetica`, `deformacion` | S-23 a S-26: datos, cifras con fuente, guion v1 |
| **H4 · 14:30** | | A-26: **lanza la ronda 1** | Lanza `deformacion` aquí |
| **14:30 a 16:30** | P-24 a P-26: chat, dos tarjetas reales, rojo | A-27 a A-30: `desgaste`, `sismico`, `analizar` de la ronda 1, validar | S-27, S-28: deck minero, validar `deformacion` |
| **H5 · 16:30** | | A-31: **lanza la ronda 2** | Lanza `sismico` aquí |
| **16:30 a 18:00** | P-27 a P-29: últimas tarjetas, modo demo | A-32, A-33: retirar motores antiguos, cifras | S-29 a S-31: extraños, entrega, congelar |
| **H6 · 18:00** PRODUCTO TERMINADO | | | |
| **18:00 a 20:30** | P-30: re-exportar si un motor pasa a `red` | A-34, A-35: validar la ronda 2, README técnico | S-32, ensayos, extraños, charla |
| **Tope de redes · 20:30** | | | |
| **20:30 a 00:00** | Video de respaldo | README técnico | Entrega |
| **Dom 00:00 a 06:00** | Duermen los tres | | |
| **06:30 a 09:30** | Ensayos 06:30 y 07:30. Entrega 08:00 | | |

Comidas del evento, para no planificar encima: almuerzo 13:30 a 15:00, comida 21:00 a 22:30.

### 6.2 PC 1 · producto (backend, frontend y despliegue)

Dueño de `servicio/` y `web/`. Skills: `desplegar`, `preparar-demo`. La forma de las respuestas no cambió: lo nuevo es el inicio, los textos, un componente (`Curva`) y sacar lo que ya no va.

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| P-21 | 12:30 | 40 | Inicio minero: las cinco tarjetas en el orden de `casos/INICIO`, textos del chat («¿Qué decisión tienes que tomar?»), fuera la cartera y las tarjetas antiguas. Las cuatro tarjetas nuevas pintan su ejemplo fijo (`contratos/ejemplos/analizar_<caso>.json`) con el rótulo «ejemplo» hasta que llegue lo real. `servicio/fijos.py` y `exportar_estatico` con los casos nuevos | Inicio | Las cinco tarjetas se ven en local y en modo estático; ninguna palabra de rotación, crédito o citas queda en pantalla |
| P-22 | 13:10 | 40 | `leyes` real con la red (`KRYLOV_MOTOR_ESPACIAL=red`): mapa, deslizadores, «¿Dónde perforo?» con los rótulos del caso, los tres pines y sus tres resultados. `exportar_estatico` para `leyes`. Redespliegue | Tarjeta 1 | Los pasos 2 a 5 del recorrido salen en la URL pública, cada uno en menos de 2 s |
| P-23 | 13:50 | 60 | Componente `Curva`: al elegir una unidad de la lista, puntos medidos, línea de «ahora», abanico (`bajo`, `medio`, `alto`), línea del límite y los nombres de los ejes. Contra `analizar_taludes.json` | `web/src/Curva.tsx` | Se lee en tamaño de proyector; sin `curva` en el JSON, la lista se ve igual que antes |
| P-24 | 14:50 | 40 | Chat con los cinco modelos: `papeles` de los motores de series (`unidad`, `tiempo`, `valor`), calce por regla y por modelo de lenguaje, interpretación con las plantillas nuevas. Un archivo de prueba por caso para subir (`datos/demo/subida_*.csv`, los deja PC 3) | Chat | Subir el archivo de prueba de `leyes` responde verde en menos de 2 s, o el chat dice que la API no responde |
| P-25 | 15:30 | 30 | Conectar `flotacion` y `taludes` reales cuando PC 2 avise (primero precalculado; red al validar). `exportar_estatico` | Tarjetas 2 y 3 | Los pasos 6 y 7 del recorrido salen con datos del motor y el rótulo correcto |
| P-26 | 16:00 | 30 | Vista 3: tecla `M` carga `leyes_pocos` (un banco con 12 pozos) → banda roja con el motivo; segunda variante con una serie corta si alcanza | Estado rojo | El paso 10 del recorrido sale en local y en estático |
| P-27 | 16:40 | 30 | Conectar `flota` y `sismicidad` (precalculado, o red si ya pasó). **La tarjeta que a las 17:30 no tenga respuesta del motor sale del inicio** | Tarjetas 4 y 5 | Cada tarjeta visible responde con datos del motor |
| P-28 | 17:10 | 30 | Modo demo: teclas `1` a `5`, `D`, `M`, `L`; semilla fija; pantalla completa; portada y cierre con el QR. `exportar_estatico` completo. Redespliegue | Atajos | El recorrido de 4.3 sale completo sin internet y en la URL con `?estatico=1` |
| P-29 | 17:40 | 20 | Skill `preparar-demo`. Borrar código muerto (cartera, vistas antiguas). **18:00: producto terminado** | Tag `congelado` | El recorrido sale dos veces seguidas en la URL pública |
| P-30 | 18:15 | 20 | Hasta las 20:30, cada vez que PC 2 pase un motor a `red`: regenerar su estático, comprobar el rótulo y redesplegar. Nada más cambia | Estático al día | La tarjeta dice quién responde de verdad |

Qué recibe: de PC 2, las funciones de `nucleo/api.py` (`leyes` ya responde; `flotacion` y `taludes` cerca de las 15:40; `flota` y `sismicidad` cerca de las 17:10); de PC 3, los casos, los datos, los ejemplos fijos y los textos. Qué entrega: la URL y el demo.

### 6.3 PC 2 · amortización de los modelos

Dueño de `nucleo/` y `motor/`. Skills: `medir-rendimiento`, `entrenar-motor`, `validar-motor`. Los cinco modelos y el andamio están en la sección 11.

**Dos sesiones de Claude Code en PC 2, repartidas por archivos.** La sesión A escribe el andamio (`motor/comun/series.py`, `nucleo/series.py`) y después `deformacion` y `sismico`. La sesión B hace `leyes`, `cinetica` y `desgaste`; importa el andamio y no lo edita.

**Calendario de cómputo.** Un entrenamiento por computador. PC 1 no entrena ni corre MCMC.

| Cuándo | PC 2 · MacBook Air M4, 16 GB | PC 3 · MacBook Air M3, 16 GB |
|---|---|---|
| 12:10 | Se detiene `estados` | Se detiene `jerarquico` |
| 12:30 a 14:30 | Nada largo: pruebas de humo y MCMC cortos de los archivos del demo | Libre: MCMC de `leyes` si PC 2 lo pide |
| 14:30 a 16:10 | **Ronda 1:** entrena `cinetica` | **Ronda 1:** entrena `deformacion` |
| 16:10 a 16:30 | **Nada entrenando.** `validar-motor cinetica`; MCMC de los archivos de la ronda 2 | **Nada entrenando.** `validar-motor deformacion` |
| 16:30 a 18:15 | **Ronda 2:** entrena `desgaste` | **Ronda 2:** entrena `sismico` |
| 18:15 a 19:00 | **Nada entrenando.** `validar-motor desgaste`; tiempos del recorrido | **Nada entrenando.** `validar-motor sismico` |
| 19:00 a 20:30 | Libre para seguir entrenando el motor que esté más cerca de pasar | Igual |

Si un motor de la ronda 1 no está listo para lanzarse a las 14:30, se lanza cuando esté y su validación se corre igual a las 16:10 con lo que alcanzó. **Tope de redes: 20:30.**

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| A-21 | 12:15 | 15 | *La persona.* Detener `estados` (Ctrl-C guarda) y no relanzar nada antiguo. `MOTORES` de `nucleo/casos.py` suma `deformacion`, `cinetica`, `desgaste` y `sismico`; `prueba_api` espera el `INICIO` nuevo | Estado | Las pruebas de `nucleo/` pasan con el `INICIO` nuevo |
| A-22 | 12:30 | 30 | *Sesión B.* `leyes` con `espacial`: confirmar `analizar` y `donde_medir` con la red; examen contra `datos/demo/leyes_verdad.csv` (de los bloques en cada color, cuántos estaban de verdad sobre el límite); MCMC de referencia del archivo (`mcmc/leyes.npz`) con su tiempo; textos del caso sin «limpiar» (`casos/textos.yaml` ya es genérico) | Sello de `leyes` en el estado | Verde con la red; el plan B existe; el tiempo del método lento por análisis está medido |
| A-23 | 12:30 | 60 | *Sesión A.* **El andamio de series** (11.6): `motor/comun/series.py` (codificador por unidad con máscara, agregación, flujo global, flujo local, pérdida, SBC global y local, exportación a ONNX con dos salidas y dos `flujo*.npz`) y `nucleo/series.py` (leer el archivo largo, muestrear en NumPy, armar `unidades`, `curva` y el examen con lo de `nucleo/tabla.py`). **Subirlo apenas pase su prueba: la sesión B lo espera** | Andamio | Con un simulador de juguete: exporta, NumPy = `torch`, y la pérdida baja en 2 minutos |
| A-24 | 13:00 | 60 | *Sesión B.* `cinetica` (11.3): `nucleo/cinetica.py`, `motor/cinetica/` (simular, mcmc, red, entrenar, validar, exportar, sello). Predictivo a priori contra `datos/demo/flotacion.csv`. Prueba de humo con SBC chico | Motor listo para lanzar | El archivo del demo cae dentro de lo simulado; el SBC chico corre |
| A-25 | 13:30 | 60 | *Sesión A.* `deformacion` (11.2): lo mismo, con la corrección del modo común en el preprocesamiento. Subir: **lo lanza la persona de PC 3** | Motor listo para lanzar | Igual que A-24, contra `datos/demo/taludes.csv` |
| A-26 | 14:30 | 10 | `medir-rendimiento cinetica` y **lanzar la ronda 1** en PC 2 hasta las 16:10. Antes, el MCMC del archivo del demo de `cinetica` y `deformacion` si cada uno corre en menos de 10 minutos | Proceso corriendo | Primer punto de guardado; el estado dice cómo retomar |
| A-27 | 14:40 | 50 | *Sesión B.* `desgaste` (11.4), sin lanzar | Motor listo | Igual que A-24, contra `datos/demo/flota.csv` |
| A-28 | 14:40 | 60 | *Sesión A.* `sismico` (11.5), sin lanzar: simulador por ramificación y lo que se decide en forma cerrada | Motor listo | Igual, contra `datos/demo/sismicidad.csv`; la forma cerrada coincide con simular hacia adelante |
| A-29 | 15:40 | 30 | `analizar` de `flotacion` y `taludes` con `mcmc` y con la red sin entrenar: `unidades`, `muestras_p`, `curva`, `factores`, examen con la verdad escondida. Entregar a PC 1 | Dos rutas | Las dos tarjetas responden con la forma del contrato |
| A-30 | 16:10 | 20 | **Sin nada entrenando.** Detener la ronda 1. `validar-motor cinetica` aquí; en PC 3, `validar-motor deformacion`. MCMC de los archivos del demo de `desgaste` y `sismico` | Dos sellos | Cada uno dice PASA o NO PASA con sus números |
| A-31 | 16:30 | 10 | **Lanzar la ronda 2:** `desgaste` en PC 2; PC 3 lanza `sismico`. Hasta las 18:15 | Procesos corriendo | Primer punto de guardado en los dos |
| A-32 | 16:40 | 50 | Retirar `supervivencia`, `jerarquico` y `estados` (código, artefactos, pruebas, `cartera`) y pedir a PC 3 que borre sus casos. `analizar` de `flota` y `sismicidad` con `mcmc` | Repositorio limpio | `uv run pytest nucleo motor -q` pasa; `grep -ri rotacion nucleo motor` no encuentra nada |
| A-33 | 17:30 | 30 | Cifras por motor para PC 3. Fijar `KRYLOV_MOTOR_<ID>` de cada tarjeta para las 18:00. Ayudar a PC 1 con `exportar_estatico` | Variables fijadas | Cada tarjeta dice la verdad sobre quién responde |
| A-34 | 18:15 | 45 | **Sin nada entrenando.** `validar-motor desgaste` aquí y `sismico` en PC 3. Tiempos del recorrido. El motor que pase antes de las 20:30 pasa a `red` y se avisa a PC 1 | Sellos | Veredicto de los cuatro motores nuevos en el estado |
| A-35 | 19:00 | 60 | Sellos finales, `limitaciones` y README técnico (`motor/README.md`) con los cinco motores y sus nombres precisos | Texto | Cada corchete del guion que depende de PC 2 tiene su número o se declara sin número |

Qué recibe: de PC 3, los archivos del demo y los casos, y su computador para dos entrenamientos. Qué entrega: a PC 1, las funciones de `nucleo/api.py`; a PC 3, los números.

**Lo que este calendario no garantiza.** Son cuatro motores nuevos en una tarde. Comprometido para las 18:00: `leyes` con su red, y `flotacion` y `taludes` respondiendo con red o con el método lento. `flota` y `sismicidad` son meta: si a las 17:30 no tienen ni su método lento, salen del inicio y quedan en el pitch como hoja de ruta.

### 6.4 PC 3 · seguimiento (monitoreo, guía, ajustes al plan y al pitch)

Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y este archivo. Skills: `ronda`, `punto-de-control`, `agregar-caso`, `registrar-cifra`, `ensayo-pitch`, `preparar-entrega`.

Su trabajo tiene dos partes. Una es la lista de abajo. La otra, que va primero cuando chocan, es la **ronda**: cada 30 a 45 minutos baja los cambios, verifica corriendo lo que los otros dicen haber terminado, pone al día la tabla «Los cinco casos» del tablero, escribe la siguiente tarea de cada uno y ajusta el guion con lo que de verdad existe.

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| S-21 | 12:10 | 30 | Pivote en el repositorio: D-37, este plan, contrato, casos, datos del demo, ejemplos fijos, pitch y tablero | Commit en ambos repositorios | `git ls-remote` da el mismo identificador en los dos |
| S-22 | 12:15 | 15 | *Una persona.* Avisar a PC 1 y PC 2 («hagan pull y lean D-37»). Detener `jerarquico` en este computador. Confirmar las cuatro decisiones abiertas de D-37 | Decisiones anotadas | El tablero dice quién confirmó qué |
| S-23 | 12:30 | 30 | `leyes`: verificar en local que responde verde con la red. Buscar 20 minutos un archivo real de pozos con arsénico o cobre con licencia abierta; si aparece, cambiar `dataset` y `origen_datos` | Caso verificado | La tarjeta responde; el origen de los datos es cierto |
| S-24 | 13:00 | 30 | Con PC 2: los cuatro archivos simulados del demo (`datos/preparar/`) calzan con el simulador de cada motor (predictivo a priori). Si PC 2 cambió un prior, regenerar con la misma semilla. Dejar un archivo de prueba por caso para subir (`subida_*.csv`) | Datos al día | PC 2 confirma en su estado que cada archivo cae dentro de lo simulado |
| S-25 | 13:30 | 30 | *Una persona.* Abrir cada fuente de las cifras de minería (`pitch/CIFRAS.md`, I-01 en adelante) y firmar. Lo que no se pueda abrir sale del guion | Columna «Verificó» | Ninguna cifra del guion queda sin persona |
| S-26 | 14:00 | 30 | Guion minero v1 en voz alta y cronometrado. Textos de pantalla de las cinco tarjetas a PC 1 | `pitch/GUION.md` | Cabe en 3 minutos; ninguna palabra minera sin explicar |
| S-27 | 14:40 | 80 | Deck minero, lámina por lámina según `pitch/LAMINAS.md`: datos de `leyes` regenerados (`pitch/deck/datos/generar.py`), lámina nueva «cinco decisiones», textos, respaldo en PNG y PDF | `pitch/deck/` | Las láminas corren sin internet; cada número tiene su id |
| S-28 | 16:10 | 20 | Detener `deformacion` aquí y correr `validar-motor deformacion`. A las 16:30, lanzar `sismico` (ronda 2) | Sello y proceso | Veredicto en el estado; primer punto de guardado de `sismico` |
| S-29 | 16:40 | 30 | *Una persona.* Prueba con tres extraños que no sepan de minería: ¿repiten la idea?, ¿qué palabra no entendieron? | `pitch/VALIDACION.md` | Tabla llena; cada palabra que no se entendió sale del guion |
| S-30 | 17:10 | 30 | Entrega, primer borrador (skill `preparar-entrega`): README, descripción y archivo de proyecto, con lo que de verdad responde | Archivos de entrega | Una persona los leyó |
| S-31 | 17:40 | 20 | Con PC 1: sacar lo que no funcione. **18:00: tag `congelado`** | Tag | El recorrido sale dos veces |
| S-32 | 18:15 | 20 | Detener `sismico` aquí y correr `validar-motor sismico` | Sello | Veredicto en el estado antes de las 19:00 |

Qué recibe: de PC 2, los números; de PC 1, la URL. Qué entrega: casos, datos, textos, la siguiente tarea de cada rol en cada ronda, las decisiones de cada hito y el pitch al día.

### 6.5 Hitos

Cada uno lo corre PC 3 con la skill `punto-de-control` y deja un tag en los dos repositorios.

**H4 · sábado 14:30 · ¿Arrancó el pivote?**
- Pasa si: `leyes` responde con la red en la URL pública, con «¿Dónde perforo?»; el inicio muestra las cinco tarjetas (cuatro con su ejemplo fijo, rotulado); la ronda 1 está entrenando en los dos computadores o lista para lanzarse en los próximos 15 minutos.
- Si falla lo primero: PC 1 deja todo y saca `leyes`. Es el demo mínimo.
- Si la ronda 1 no está lista: se lanza cuando esté y valida a las 16:10 con lo que alcanzó. Si a las 15:15 un motor de la ronda 1 no tiene prueba de humo, sale con el método lento y su computador pasa a la ronda 2.

**H5 · sábado 16:30 · ¿Responden las primeras tarjetas nuevas?**
- Pasa si: `flotacion` y `taludes` responden en la app con datos del motor (red o precalculado, rotulado); la ronda 2 está entrenando; el guion minero cabe en 3 minutos.
- **Por motor, red o plan B:** si pasó `validar-motor`, `KRYLOV_MOTOR_<ID>=red`. Si no pasó pero mejora, puede seguir entrenando después de la ronda 2 en el computador que quede libre. Si no pasó, `mcmc` y «precalculado».
- Si una tarjeta de la ronda 1 no tiene ni su método lento: sale del inicio a las 17:30.

**H6 · sábado 18:00 · PRODUCTO TERMINADO.** Tag `congelado`. Alguien que no sea de PC 1 hace el recorrido de 4.3 dos veces seguidas, en la URL pública y con el wifi apagado en local. Lo que no funciona se saca de la pantalla. Desde aquí no entra ninguna función.

**Tope de redes · sábado 20:30.** Última hora para pasar un motor a `red`. Después, quién responde cada tarjeta no cambia y el guion se cierra con eso.

**Orden de corte**, del primero que cae al último, y qué se dice:

| # | Qué cae | Qué se ve | Qué se dice |
|---|---|---|---|
| 1 | `desgaste` | Flota «precalculada», o fuera del inicio | «Esta la calculamos con el método lento; tardó [X]. Es lo que Krylov está aprendiendo a hacer al instante». Si está fuera: se nombra como hoja de ruta |
| 2 | `sismico` | Sismicidad «precalculada», o fuera | Lo mismo |
| 3 | `cinetica` | Flotación «precalculada» | Lo mismo |
| 4 | `deformacion` | Taludes «precalculado» | Lo mismo |
| Nunca | El mapa de `leyes` y «¿Dónde perforo?» | | Es el demo mínimo y está validado |

**Entrega · domingo 08:00.** Repositorio oficial con descripción, logo, README y URL pública. Tag `entrega`.

### 6.6 Sábado de 18:00 a 00:00 y domingo

Lo que sí se puede cambiar después de las 18:00: textos, orden de las tarjetas, tamaños de letra, valores por defecto de los deslizadores, el guion, las láminas y, hasta las 20:30, quién responde una tarjeta. Lo que no: funciones, vistas, motores nuevos.

| Hora | Qué | Quién |
|---|---|---|
| 18:00 | Recorrido completo con cronómetro. Lista de todo lo que se ve mal | Los tres |
| 18:15 | Validar la ronda 2 | PC 2 y PC 3 |
| 18:30 | Ensayo 1 con el computador y el cable de la presentación | Quien presenta |
| 19:00 | Prueba 2 con tres extraños distintos | PC 3 |
| 19:30 | Arreglos de texto y orden | PC 1 y PC 3 |
| 20:00 | Charla de la organización «Cómo hacer un buen demo». Anotar la duración oficial del pitch | PC 3 y quien presenta |
| 20:30 | **Tope de redes.** Guion v3 con quién responde cada tarjeta | PC 2 y PC 3 |
| 21:00 | Ensayo 2, cronometrado, con las preguntas difíciles. Comer después | Los tres |
| 21:45 | Últimos arreglos. Último despliegue | PC 1 |
| 22:00 | Video de respaldo: la app en pantalla completa, narración encima | PC 1 y PC 3 |
| 22:00 | README técnico: cómo se entrenó, cómo se validó, cómo reproducir | PC 2 |
| 23:00 | Entrega revisada (skill `preparar-entrega`). Lista previa del domingo (skill `preparar-demo`) | PC 3 |
| 00:00 | A dormir los tres | |

Domingo: ensayo 06:30, ensayo 07:30, entrega 08:00, cierre de repositorios 08:30. Quien presenta duerme al menos seis horas.

### 6.7 Qué esperamos tener medido a cada hora

| Hora | Número | Quién |
|---|---|---|
| Sáb 13:00 | `leyes`: bloques en cada color, lo que cuesta no saber, examen, análisis rehechos y lo que vale el mejor pin. El método lento por análisis en ese archivo | PC 2 |
| Sáb 14:30 | Ronda 1: datasets simulados por segundo de `cinetica` y `deformacion` | PC 2, PC 3 |
| Sáb 16:30 | Ronda 1: simulaciones, minutos, SBC, cobertura, diferencia con el método lento, milisegundos por análisis | PC 2, PC 3 |
| Sáb 17:00 | Extraños que repiten la idea, prueba 1 | PC 3 |
| Sáb 17:30 | Por tarjeta: unidades en cada color, lo que cuesta no saber, examen con la verdad escondida | PC 2 |
| Sáb 19:00 | Ronda 2: lo mismo que la ronda 1. Tiempos del recorrido sin nada entrenando | PC 2, PC 3 |
| Sáb 19:30 | Extraños que repiten la idea, prueba 2 | PC 3 |
| Sáb 20:30 | Qué tarjetas responden con su red y cuáles salieron precalculadas | PC 2 |

### 6.8 Riesgos que nos dejan sin demo

| Riesgo | Señal | Qué se hace |
|---|---|---|
| El pivote deja la app a medias | H4 | `leyes` es lo primero que se conecta y ya responde con la red. Las tarjetas nuevas parten con su ejemplo fijo rotulado. El tag `h1` tiene la app anterior si hubiera que volver |
| Cuatro motores no caben en una tarde | H5 y H6 | Motores chicos, un andamio común, cada uno con su método lento primero. Orden de corte escrito. Comprometido: `leyes`, y dos tarjetas más con red o precalculado |
| El andamio de series se atrasa | A-23 sin subir a las 13:45 | Los motores de la ronda 1 se lanzan con el flujo global solamente y lo propio de cada unidad se resuelve con el método lento para el archivo del demo |
| Un motor no pasa su sello | 16:10 y 18:15 | Tarjeta «precalculada». Si mejora, sigue entrenando hasta las 20:30 |
| El método lento tampoco converge en un motor | A-26, A-30 | Esa tarjeta sale del inicio y queda como hoja de ruta. Se dice |
| Un entrenamiento se cae o un Mac se duerme | Sin puntos de guardado recientes | Tapa abierta y `caffeinate`. Se retoma del último punto |
| El archivo del demo cae fuera de lo simulado | A-24, A-25, A-27, A-28 | Los archivos se generan con las mismas ecuaciones de la sección 11; si PC 2 cambia un prior, PC 3 regenera (S-24) |
| La revisión del código encuentra motores de recursos humanos | Entrega | A-32 los retira. Si no alcanza el sábado, se hace el domingo antes de las 08:00, con las pruebas pasando |
| Vercel llega a su límite de despliegues | P-22 | Solo se despliega cuando cambia `web/`; se agrupan los redespliegues en H4, H5 y H6 |
| El jurado no entiende una palabra minera | S-29 | La prueba con extraños la saca. `GLOSARIO.md`, «Minería en simple» |
| Una cifra del guion no llega | Ensayo | La frase se dice sin número. Nunca se inventa |
| Se rompe algo después de las 18:00 | Ensayo | Se vuelve al tag `congelado` |

## 7. Cómo se coordinan los tres computadores

- **Contrato:** `contratos/CONTRATO.md`. Funciones de `nucleo/api.py`, regla de decisión, modo estático y formato de caso.
- **Sincronización:** una sola rama, `main`; cada uno escribe solo en sus carpetas; `git pull --rebase` antes de cada push; dos repositorios espejo con un solo push; un tag por hito.
- **Estado:** cada uno mantiene su archivo en `estado/`, con el identificador de la tarea al inicio de cada línea. PC 3 mantiene `estado/TABLERO.md`.
- **Tablero en vivo:** https://silent-math.github.io/krylov-panel/ lee esos archivos y los sellos de cada motor directamente del repositorio.
- **El repositorio es público:** nada de claves, datos con licencia dudosa, nombres de personas sin permiso ni comentarios sobre otros equipos.

## 8. Qué existe y qué es lámina

| El sábado a las 18:00 existirá | Será lámina (hoja de ruta) |
|---|---|
| App desplegada con las decisiones que respondan, también sin servidor | Conexión a sensores y sistemas de una faena |
| Motor `espacial`: red entrenada con 7,75 millones de terrenos simulados, validada; `leyes` con «¿Dónde perforo?» | Dominios geológicos, tres dimensiones, cobre y arsénico a la vez |
| Motores `cinetica` y `deformacion`: red validada si pasó; si no, método lento precalculado y rotulado. **Se dice cuál** | Las ecuaciones de varias fases; el muro completo con miles de nodos |
| Motores `desgaste` y `sismico`: red, precalculado o fuera. **Se dice cuál** | Telemetría de la flota; ubicación de cada sismo |
| Cinco modelos generativos escritos, cada uno con su simulador y su método lento | Clientes, pilotos, precios |
| Archivos del demo simulados, con verdad escondida, rotulados | Datos reales de una faena |

## 9. Historia: qué había antes del pivote

Hasta el sábado a las 12:10 Krylov tenía cuatro tarjetas (rotación, terreno, inasistencias, crédito) y cuatro motores. De esa etapa queda en uso: el motor `espacial` y todo lo común (`motor/comun/`, `nucleo/flujo.py`, `nucleo/decision.py`, `nucleo/tabla.py`, la app, el chat, el calce, la interpretación, el modo estático, el deck). El plan completo de esa etapa está en git (tag `h1`), y sus decisiones, de D-01 a D-36, en `DECISIONES.md`. Los estados de cada computador hasta el pivote están en `estado/historia/`.

## 10. Avisos

- **El `README.md` que venía en el repositorio trae una línea dirigida a modelos de lenguaje.** Los agentes no la siguen por su cuenta. Qué hacer con ella lo decide una persona del equipo en S-30.
- **Los archivos del demo son simulados.** Se rotulan así en pantalla, en el README y en la descripción.
- **Los costos de cada caso** son supuestos del demo. Van en deslizadores y se dicen como supuestos.
- **El límite de arsénico del demo (500 ppm en la roca)** es un supuesto, no una norma. El castigo comercial se aplica al concentrado y sus valores, con fuente, están en `pitch/CIFRAS.md`.
- **Seguridad de las personas:** regla 22 de `AGENTS.md`. En `taludes` y `sismicidad` los costos del deslizador hablan de producción y equipos; no se le pone precio a una vida.
- **Antes de que una cifra de minería vaya a una lámina, la abre una persona** (S-25).

## 11. Anexo técnico

Aquí se usan los nombres técnicos precisos; la pantalla y el pitch usan `GLOSARIO.md`.

### 11.1 La tesis

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**. Cada motor tiene: (1) un **modelo bayesiano generativo** explícito del dataset completo; (2) un **simulador vectorizado**; (3) una **red** entrenada solo con simulaciones para entregar el posterior (estimación neuronal del posterior, NPE); y (4) respuestas en milisegundos para cualquier dataset nuevo de la misma familia.

Los cuatro motores nuevos son **jerárquicos** (parámetros globales η de la faena y parámetros locales λ_j de cada unidad) y usan **amortización factorizada**:

```
p(η, λ_1..J | y_1..J)  ≈  q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D))
```

con s_j el resumen aprendido de la unidad j y s(D) el del dataset. Así la dimensión de cada flujo es chica y fija aunque cambie el número de unidades.

**Tamaño.** Entre 5 y 7 parámetros globales y 2 locales por motor. Es una decisión, no un límite del método: anoche el motor de 7 parámetros pasó su sello y el de 32 no (M-28).

Todos los priors de abajo son puntos de partida. Antes de lanzar un entrenamiento se mira el predictivo a priori contra el archivo del demo y se ajusta; lo que quede va en `config.json` y PC 3 regenera el archivo si hace falta (S-24).

### 11.2 `deformacion` (taludes y relaves)

Datos: J sectores (12 a 60); un sector es un prisma topográfico o un grupo de píxeles del radar. Por sector, K lecturas (48 a 144) de desplazamiento acumulado d_jk en una ventana [0, T]. El preprocesamiento (uno solo, en `nucleo/`) hace tres cosas: resta en cada lectura la mediana entre sectores (el modo común: el efecto de la atmósfera sobre el radar, que mueve a todos a la vez); pasa el tiempo a u = t/T; y divide el desplazamiento por la escala del archivo, e = la mediana entre sectores del movimiento total en la ventana. **Así el motor no depende de las unidades:** sirve igual para un radar que mide cada 4 minutos y para prismas que se leen cada 4 horas.

```
En unidades normalizadas (u ∈ [0, 1], desplazamiento / e):
Globales η (7):
  π ~ Beta(1.5, 6)                               fracción de sectores que se están acelerando
  μ_v ~ Normal(0, 0.6),  σ_v ~ HalfNormal(0.7)          velocidad de fondo, en log (1 = el sector típico)
  μ_f ~ Normal(log 0.3, 0.8),  σ_f ~ HalfNormal(0.6)    cuánto falta para la falla, en ventanas, en log
  μ_A ~ Normal(log 1.5, 0.6)                            escala de la aceleración, en log
  σ_e ~ LogNormal(log 0.05, 0.7)                        ruido de cada lectura
Por sector:
  z_j ~ Bernoulli(π)                              1 = acelerando
  log v_j ~ Normal(μ_v, σ_v)
  si z_j = 1:  log(u_f,j − 1) ~ Normal(μ_f, σ_f),   log A_j ~ Normal(μ_A, 0.5)
Trayectoria:
  estable:      d_j(u) = v_j·u
  acelerando:   d_j(u) = v_j·u + A_j·log( u_f,j / (u_f,j − u) )       (velocidad A/(u_f − u): ley de velocidad inversa, Fukuzono 1985, Voight 1988)
Lectura:        y_jk = d_j(u_k) + ε_jk,   ε_jk ~ Normal(0, σ_e)
```

- **Local λ_j:** (z_j, log(u_f,j − 1)). Una cabeza da P(z_j = 1 | η, s_j) y el flujo local da el tiempo que falta, condicionado a z_j = 1.
- **Lo que se decide:** p_j = P(z_j = 1 y u_f,j ≤ 1 + H/T | datos), con H el horizonte del caso (`columnas.horizonte`, en las unidades de tiempo del archivo).
- **Curva:** las lecturas, y el abanico de d_j de T a T + H con las muestras de (η, λ_j), de vuelta en las unidades del archivo. `marca`: la mediana y el rango de 90% de lo que falta para la falla.
- **Rangos del simulador:** J de 12 a 60; K de 48 a 144, con lecturas faltantes al azar (hasta 15%).
- **MCMC de referencia:** NUTS con z_j marginalizado (mezcla de las dos trayectorias por sector). Es multimodal: se corre con 4 cadenas y se informa r̂.
- **Método rápido de siempre:** una recta sobre la velocidad inversa de las últimas lecturas, sector por sector, sin rango.
- **Datos reales (S-24):** los prismas del rajo de Zenodo 15003054 (CC BY 4.0). Las series reales no son hipérbolas limpias (hay prismas que se aceleran y después frenan): si el archivo real cae fuera de lo simulado, el semáforo lo dice y el demo usa el archivo simulado, rotulado.

### 11.3 `cinetica` (flotación)

Datos: B líneas (4 a 12). Cada línea tiene K celdas (6 a 10) y la recuperación acumulada de cobre R_bk ∈ (0, 1) medida a la salida de las **primeras m_b celdas** (m_b entre 3 y K), a tiempos de residencia acumulados t_k en minutos. Se decide sobre la recuperación al final de la línea, t_K, que todavía no se ve.

```
Globales η (6):
  μ_k ~ Normal(log 0.25, 0.6),  σ_k ~ HalfNormal(0.5)       velocidad de flotación, 1/min, en log
  μ_R ~ Normal(logit 0.90, 0.6), σ_R ~ HalfNormal(0.6)      recuperación máxima alcanzable, en logit
  φ ~ Beta(4, 2)                                             fracción del cobre que flota rápido
  σ_y ~ LogNormal(log 0.015, 0.5)                            error de cada medición
  (fijo: la fracción lenta flota 8 veces más lento)
Por línea:   log k_b ~ Normal(μ_k, σ_k),   logit Rmax_b ~ Normal(μ_R, σ_R)
Curva:       R_b(t) = Rmax_b · [ 1 − φ·exp(−k_b·t) − (1 − φ)·exp(−k_b·t / 8) ]
Medición:    y_bk = R_b(t_k) + ε,   ε ~ Normal(0, σ_y),   para k ≤ m_b
```

- **Local λ_b:** (log k_b, logit Rmax_b). Con pocas celdas medidas, k y Rmax se confunden: el posterior local es alargado o bimodal, y por eso va un flujo y no una gaussiana.
- **Lo que se decide:** p_b = P(R_b(t_K) < meta | datos), con la meta del caso (`columnas.umbral`).
- **Curva:** las mediciones, y el abanico de R_b(t) hasta t_K.
- **MCMC de referencia:** NUTS sobre η y los 2B locales. Rápido por dataset; la cifra de amortización es rehacerlo con cada lectura nueva en todas las líneas.
- **Método rápido de siempre:** ajustar una sola exponencial a cada línea por separado, sin rango.

### 11.4 `desgaste` (flota de camiones)

Datos: M camiones (15 a 60). Por camión, J_i mediciones (4 a 12) de un indicador de desgaste y_ij (por ejemplo, hierro en el aceite), normalizado para que la falla sea 1,0, a horas de operación t_ij (en miles de horas); una covariable x_i de exigencia de su ruta, estandarizada; y h_i, las horas que faltan para su próxima mantención programada.

```
Globales η (5):
  μ_ν ~ Normal(log 0.5, 0.5),  σ_ν ~ HalfNormal(0.5)      ritmo de desgaste por mil horas, en log
  β ~ Normal(0.3, 0.3)                                      cuánto acelera el desgaste una ruta exigente
  c ~ LogNormal(log 0.3, 0.4)                               qué tan a saltos avanza el desgaste
  σ_ε ~ LogNormal(log 0.04, 0.5)                            error de cada medición
Por camión:   log ν_i ~ Normal(μ_ν + β·x_i, σ_ν)
Desgaste:     X_i(0) = 0;  incrementos independientes  ΔX ~ Gamma(forma = ν_i·Δt / c², escala = c²)
              (proceso gamma: en promedio avanza ν_i·Δt, a saltos, y nunca retrocede)
Medición:     y_ij = X_i(t_ij) + ε,   ε ~ Normal(0, σ_ε)
Falla:        cuando X_i cruza 1
```

- **Los camiones del archivo siguen en servicio:** el simulador descarta la trayectoria que ya cruzó el límite (X_i(t_ahora) < 0,92) y sortea otra. La red y el MCMC tienen que condicionar en lo mismo.
- **Local λ_i:** (log ν_i, log X_i(t_ahora)).
- **Lo que se decide:** p_i = P(X_i(t_ahora + h_i) ≥ 1 | datos). Dado (η, λ_i), el incremento hasta la mantención es Gamma(ν_i·h_i / c², c²): se estima con 64 sorteos de NumPy por muestra.
- **Curva:** las mediciones, y el abanico de X_i(t) hasta la próxima mantención, con la línea de falla en 1.
- **MCMC de referencia:** NUTS con los incrementos latentes de cada tramo (cientos de variables positivas, sin conjugación con la medición gaussiana). Lento: esa es la historia.
- **Método rápido de siempre:** una recta por camión, extrapolada, sin rango.

### 11.5 `sismico` (sismicidad inducida)

Datos: S sectores (4 a 12). Por sector, los sismos registrados en las T horas siguientes a la tronadura (hasta 300): hora t_i y magnitud m_i ≥ m_0, la mínima que la red sísmica registra completa.

```
Globales η (6):
  μ_μ ~ Normal(log 0.5, 0.7),  σ_μ ~ HalfNormal(0.6)      tasa de fondo por hora, en log
  n ~ Beta(3, 4)                                            cuántos sismos nuevos gatilla, en promedio, cada sismo (menor que 1)
  α ~ LogNormal(log 1.0, 0.3)                               cuánto más gatilla un sismo grande
  ω ~ LogNormal(log 1.5, 0.5)                               qué tan rápido se apaga el efecto, 1/h
  b ~ LogNormal(log 1.0, 0.15)                              cuántos sismos chicos hay por cada grande (Gutenberg-Richter)
Por sector:   log μ_s ~ Normal(μ_μ, σ_μ);   log A_s ~ Normal(log 8, 0.6)    (sismos que gatilla directamente la tronadura)
Intensidad:   λ_s(t) = μ_s + A_s·ω·e^(−ω·t) + Σ_{t_i < t} κ(m_i)·ω·e^(−ω·(t − t_i)),
              κ(m) = n·e^(α·(m − m_0)) / E[e^(α·(m − m_0))]          (proceso de Hawkes con núcleo exponencial)
Magnitudes:   m_i − m_0 ~ Exponencial(b·ln 10),  con α < b·ln 10
```

- **Simulador:** por ramificación (inmigrantes de fondo, hijos de la tronadura, hijos de cada sismo), vectorizado por generaciones. Se trunca en 300 sismos por sector.
- **Local λ_s:** (log μ_s, log A_s).
- **Lo que se decide:** p_s = P(al menos un sismo de magnitud ≥ M_c en las próximas H horas | historia). Con núcleo exponencial la intensidad esperada tiene forma cerrada: E[λ(T + u)] = μ/(1 − n) + (λ(T) − μ/(1 − n))·e^(−ω(1 − n)u). Se integra en [0, H], se multiplica por 10^(−b·(M_c − m_0)) y p_s = 1 − exp(−N). Es una aproximación de Poisson y va escrita en `limitaciones`; una prueba la compara con simular hacia adelante.
- **Curva:** el número acumulado de sismos y el abanico del acumulado esperado en las próximas H horas.
- **Codificador:** cada sismo entra con (t/T, log del tiempo desde el anterior, m − m_0); la serie se ordena por tiempo.
- **MCMC de referencia:** NUTS con la verosimilitud recursiva del núcleo exponencial. Hay que rehacerlo con cada sismo nuevo: esa es la cifra de amortización.
- **Método rápido de siempre:** contar sismos por hora y esperar a que baje de un número fijo.

### 11.6 `espacial` (leyes y arsénico) y lo común

**`espacial` no cambia.** Proceso gaussiano con covarianza exponencial y anisotropía geométrica, tendencia opcional y error de medición; 7 parámetros; red convolucional sobre una grilla de 32 × 32 con cabeza de mapa y cabeza de flujo; kriging dado θ como paso local; «¿Dónde perforo?» rehace el análisis para cada lugar candidato y cada resultado posible en un solo lote. Sello: PASA (sáb 09:39). El caso `leyes` no usa la tendencia (20% de las simulaciones de entrenamiento no la tenían). Detalle en `motor/README.md`.

**El andamio de series (`motor/comun/series.py`, `nucleo/series.py`).** Una implementación para los cuatro motores nuevos; cada motor aporta su simulador, su lista de parámetros y su función «lo que se decide».

- **Entrada.** Tensores con relleno y máscara: (unidades, lecturas, canales). Canales: tiempo normalizado, valor estandarizado, diferencia con la lectura anterior y las covariables de la unidad. Tamaños máximos fijos por motor, para que ONNX no necesite ejes dinámicos.
- **Codificador por unidad.** Convoluciones 1D con máscara y pooling (promedio y máximo) → s_j de 64. Si no exporta o no aprende, una GRU chica.
- **Agregación.** DeepSets con atención sobre las unidades (`motor/comun/codificador.py`, ya existe) → s(D) de 128.
- **Flujo global.** `FlujoCondicional` de `motor/comun/flujo.py` (acoplamiento afín, 8 capas) sobre η en espacio sin restricciones, condicionado en s(D).
- **Flujo local.** El mismo flujo, de 2 dimensiones, compartido entre unidades y condicionado en [η, s_j, s(D)]. Al entrenar se condiciona en el η verdadero; al responder, en cada muestra de η.
- **Pérdida.** −log q(η | s(D)) − promedio_j log q(λ_j | η, s_j, s(D)).
- **Exportación.** El codificador a ONNX con dos salidas (s(D) y los s_j); `flujo.npz` y `flujo_local.npz`, muestreados en NumPy por `nucleo/flujo.py`. La prueba de siempre: NumPy y `torch` dan la misma muestra.
- **Hacia el contrato.** 32 muestras de η; por cada una, una muestra de λ_j por unidad; con eso, `muestras_p` por unidad (la función del motor), la `curva` y los `factores` (el signo y la certeza de los parámetros globales que tienen nombre en `etiquetas`).

### 11.7 Entrenamiento

- PyTorch en `float32`; procesador o GPU del Mac según `medir-rendimiento`, por motor. Datasets simulados al vuelo; se cuenta cada uno. Puntos de guardado cada 10 minutos. Python 3.12 con `uv`.
- **Lo mínimo para lanzar:** simulador, red del andamio, pérdida, puntos de guardado y una prueba de humo con un SBC chico (200 datasets).
- Dos rondas de 100 a 105 minutos, un entrenamiento por computador. Calendario: sección 6.3.

### 11.8 Validación: un sello por motor

1. **Calibración en simulaciones nuevas.** SBC y cobertura del 90% para η, y también para los λ_j (SBC local) y para lo que se decide (p_j contra el valor exacto con el η y el λ_j verdaderos).
2. **Comparación con el MCMC de referencia.** NumPyro con NUTS, solo dentro de `motor/`. De 3 a 5 datasets simulados más el del demo, con su tiempo: esa es la cifra de amortización. Nunca encima de un entrenamiento. Si NUTS no converge (r̂ sobre 1,05) en 10 minutos por dataset, se anota «el método lento no convergió en 10 minutos» y el sello se apoya en el SBC; esa tarjeta no tiene plan B.
3. **Examen con la verdad escondida.** Cada archivo del demo trae aparte lo que pasó de verdad con cada unidad.
4. **Semáforo.** Un archivo con muy pocas lecturas da `rojo_datos`; uno que cae lejos de las simulaciones en el espacio de resúmenes, `rojo_modelo`.

Un motor **pasa** si: SBC sin sesgo visible (criterios de D-32), cobertura de 90% entre 85% y 95% para η y para lo que se decide (y sobre 80% en el peor grupo, como en el sello de `espacial`), diferencia con el MCMC bajo 0,3 desviaciones estándar en las medias de η (si el MCMC convergió), y un análisis en menos de 1 segundo.

### 11.9 Decisión y servicio

- **Decisión.** `contratos/CONTRATO.md`, sección 3. La regla de lista (`muestras_p`) vale para los cuatro motores nuevos; la espacial, para `leyes`.
- **Servicio.** El codificador corre con `onnxruntime`; los flujos y lo local, en NumPy. `nucleo/` y `servicio/` no importan `torch`, `zuko`, `jax` ni `numpyro`.
- **Plan B por motor.** Implementación `mcmc`: las muestras del MCMC precalculado para el archivo del demo (η y los λ_j), pasadas por la misma función «lo que se decide». Sale rotulado «precalculado».

## 12. Fuentes

Las cifras de minería, con su enlace y quién las verificó, están en `pitch/CIFRAS.md`, sección «La minería». Antes de usar una en una lámina, una persona abre la fuente y firma (S-25).

El evento
- Programa y sponsors de Santiago. https://hack.platan.us/26-cl
- Bases: criterios, premios, exigencia de demo. https://hack.platan.us/26-cl/bases

El nombre
- Aleksey Krylov. https://en.wikipedia.org/wiki/Aleksey_Krylov · https://mathshistory.st-andrews.ac.uk/Biographies/Krylov_Aleksei/
- Biografía de divulgación, capítulo de las tablas. http://www.plam.ru/hist/akademik_korabelnoi_nauki/p16.php

El documento técnico del equipo
- «Inferencia Bayesiana Amortizada para la Gran Minería Chilena» (borrador interno, 21-nov-2026): los cinco problemas, sus modelos completos y por qué el MCMC no escala en cada uno. Este plan implementa la versión chica de cada modelo.

Los métodos
- Velocidad inversa para anticipar la falla de un talud: Fukuzono (1985); Voight (1988, 1989).
- Sismicidad que se gatilla a sí misma: Hawkes (1971); Ogata (1988).
- Proceso gamma para desgaste: van Noortwijk (2009), «A survey of the application of gamma processes in maintenance».
- Cinética de flotación con fracción rápida y lenta: Kelsall (1961).
- Inferencia amortizada: Radev et al., BayesFlow; Cranmer, Brehmer y Louppe (2020), «The frontier of simulation-based inference».

Datos reales abiertos
- Terreno (examen del motor espacial), 155 muestras, paquete `sp` de R. https://rdrr.io/cran/sp/man/meuse.html
- Prismas de la pared de un rajo que falló, CC BY 4.0: de Wit, T. (2025), Zenodo. https://doi.org/10.5281/zenodo.15003054
- Sondajes con ley de cobre, CC BY 4.0: Hoffimann et al. (2022), «GeoMet dataset», Zenodo. https://doi.org/10.5281/zenodo.7051975

Herramientas: detalle y versiones en `STACK.md`, sección 5.
