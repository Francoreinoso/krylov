# Krylov · Plan de trabajo final

Platanus Hack 26, Santiago, track Simulaciones. Escrito el sábado 21 de noviembre a las 03:00. Reemplaza al plan v3 y responde a la crítica v3 (sección 9).

> **Cambio de fondo, sáb 03:00 (decisión D-26):** Krylov es inferencia basada en simulación amortizada, con cuatro motores, uno por caso. Este archivo ya está al día con ese cambio; la sección 9 se conserva como historia.

> **Esto es una hackathon.** Proyecto chico, tiempo acotado, se vende con un pitch corto. **El producto se termina el sábado a las 18:00.** Desde ahí solo se itera el demo y el pitch. El plan no depende de contactar a nadie. Ante la duda: lo más simple que se vea bien en el demo, y que la simulación se vea en pantalla.

Fechas fijas: producto terminado sábado 18:00 · entrega domingo 08:00 · cierre de repositorios domingo 08:30 · presentaciones generales 09:30 · finales 12:00.

## 0. En una página

**Qué es Krylov.** Un **data scientist artificial**: le das un archivo de datos y una pregunta de negocio, y te dice qué conviene hacer, **cuánto te cuesta no saber** y **dónde conviene averiguar más**. Y avisa cuando los datos no sirven.

**Cómo funciona, en una frase.** Hace el cálculo difícil antes: para cada tipo de pregunta tiene reglas con que inventa empresas (o terrenos), practica con millones de esos casos simulados, donde la respuesta correcta se conoce, y por eso después responde al instante.

**Por qué se llama así.** Por Alekséi Krylov, ingeniero naval que a comienzos del 1900 calculó por adelantado qué hacer con un barco averiado, para que el capitán decidiera en segundos. Calcular antes, decidir al instante.

**Qué se ve en el demo.** Cuatro tarjetas. Se abre la de Buk: quién conviene retener, con deslizadores de costos que cambian la respuesta en vivo. Se le pasa un archivo malo y Krylov muestra, sobre una nube de empresas simuladas, que no se parece a nada que haya visto. Después un terreno real: dónde limpiar, dónde no se sabe, y **«¿Dónde mido?»**, tres pines con plata. Un clic simula la medición y el mapa cambia.

**La frase que el jurado tiene que poder repetir.** *«Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo. En un segundo, porque ya practicó con millones de mundos simulados.»*

**Qué cambió respecto del plan v3**, en cinco líneas:

1. El nombre es Krylov.
2. El momento estrella es «¿Dónde mido?», que antes era opcional.
3. Cada tarjeta tiene su propio motor: un modelo de los que hoy exigen un especialista, y una red que practicó con casos simulados de ese modelo (D-26). Lo que antes era una regresión con el método exacto ya no existe.
4. Los colores son decisiones y el número grande mide de verdad la duda.
5. La URL pública funciona sin servidor, y el plan se cortó a cuatro tarjetas, cada una con su motor.

### 0.1 El objetivo: ganar, con los criterios oficiales

Los criterios están publicados en las bases (antes no los teníamos). Cada decisión de alcance se toma contra ellos.

| Criterio | Peso | Qué dice | Cómo lo cumplimos |
|---|---|---|---|
| **Aspecto técnico** | 25% | Calidad de la ingeniería y de las decisiones de diseño: complejidad, modelación y adecuación. **El jurado puede apoyarse en una revisión automatizada del código** | Inferencia basada en simulación amortizada, caso por caso: cuatro modelos generativos escritos con sus ecuaciones, un simulador y una red por modelo, validada con SBC, contra un MCMC de referencia y contra datos reales; un contrato entre módulos; pruebas por módulo; un README que lo explica con los nombres técnicos |
| **Ambición** | 20% | Qué tan altos fueron los objetivos para las 36 horas | Entrenar en una noche y una mañana, en dos notebooks sin ventilador, redes que reemplazan un cálculo de minutos por empresa; cuatro motores; app desplegada |
| **Ejecución** | 20% | Qué tan pulido, coherente y funcional es el resultado | Recorrido sin esperas; URL pública que no se cae; tarde entera para ensayar |
| **Impacto** | 20% | El valor que entrega a sus usuarios, **la profundidad por sobre el alcance** | Cada pantalla termina en una decisión con plata. Por eso la cartera («miles de clientes») pesa menos que «¿Dónde mido?» |
| **Originalidad** | 15% | Qué tan sorprendente es, si va más allá de la primera solución evidente | No es un chat con un archivo: dice cuánto no sabe y cuánto vale averiguarlo |

Otras tres cosas de las bases que cambian el plan:

- **Solo llegan a la final los equipos con una demostración funcional.**
- Hay 12 equipos en Simulaciones, de 48. Los ganadores de cada categoría reciben premio, así que primero hay que ganarle al track.
- La página de votación de cada proyecto muestra la descripción, el video del pitch en el escenario y la URL pública. Se vota días después: la URL tiene que seguir viva.

No hay criterio que premie el modelo de negocio. Queda en una frase y una lámina de respaldo.

### Conceptos en un minuto

Están completos en `GLOSARIO.md`. Los que más se usan:

| Concepto | Qué significa aquí |
|---|---|
| **Data scientist artificial** | Programa que hace el trabajo de un analista de datos: elige el método, lo aplica, dice qué conviene hacer y cuándo los datos no sirven |
| **Simular** | Inventar datos con reglas conocidas. Krylov practica con casos simulados, donde la respuesta correcta se conoce |
| **Amortizar** | Pagar el costo de cálculo una sola vez, por adelantado, para que cada respuesta sea instantánea |
| **Motor** | Las reglas con que Krylov inventa casos de un tipo de pregunta, más la red que practicó con ellos y por eso responde al instante. Hay cuatro, uno por tarjeta |
| **Caso de uso** | Una pregunta de negocio resuelta con un motor, un archivo de datos y sus costos. Cada tarjeta es un caso |
| **Unidad** | Aquello sobre lo que se decide: una persona, una cita, un cliente, un bloque de terreno |
| **Tres colores** | Son decisiones: «conviene actuar», «no hace falta», «no sabemos si conviene» |
| **Lo que te cuesta no saber** | La plata que se ahorraría si la duda se despejara antes de decidir |
| **¿Dónde mido?** | Los tres lugares donde una medición más vale más plata |
| **Examen** | Lo que pasó cuando Krylov respondió sobre datos reales que no había visto |
| **Modo estático** | Las respuestas del demo guardadas como archivos junto a la web |
| **PC 1, PC 2, PC 3** | Los tres computadores: producto, amortización y seguimiento |
| **Hito (H0 a H3)** | Hora fija en que se mide contra un criterio escrito y se decide seguir o cortar |

## 1. El producto

### 1.1 Qué reemplaza

Hoy, para responder «¿a quién conviene retener?» o «¿dónde mido antes de gastar?», una empresa necesita un data scientist: alguien que elige un modelo, lo programa, lo ajusta y explica el resultado. Tarda días, cuesta un sueldo, y casi nunca dice cuánto se puede equivocar ni cuánto vale salir de la duda. La mayoría de las empresas no tiene uno.

Krylov hace ese trabajo, con los modelos que usaría ese especialista y no con los simples. Con el método de siempre, cada uno de esos modelos tarda minutos por empresa; Krylov ya practicó con millones de casos simulados y responde en milisegundos, para una empresa o para mil.

### 1.2 Los motores

| Motor | Tarjeta | Qué modelo es, en palabras | Por qué el método de siempre es lento | Al sábado 18:00 |
|---|---|---|---|---|
| `espacial` | Terreno | El terreno varía de a poco, más en una dirección que en otra, y cambia con la distancia al río; cada medición trae error | «¿Dónde mido?» exige rehacer el análisis cientos de veces | Red obligatoria. Es el momento estrella |
| `supervivencia` | Rotación (tipo Buk) | Cuánto dura una persona en la empresa, cuando de muchas todavía no se sabe (siguen ahí). Efecto del sueldo que no es una recta, diferencias por cargo y un compromiso de cada persona que no se ve, pero se asoma en sus cuatro encuestas | Una incógnita por persona, más las de cada cargo | Red comprometida. Abre el demo y alimenta la cartera |
| `jerarquico` | Inasistencias (tipo AgendaPro) | Cada paciente tiene su propia tendencia a faltar y cada barrio la suya; la espera pesa de forma no lineal y el efecto del SMS cambia con la espera | Cerca de mil incógnitas en dos niveles | Red como meta; si no, sale precalculado |
| `estados` | Crédito | Cada cliente pasa mes a mes por estados que no se ven (al día, apretado, en problemas); sus atrasos, deudas y pagos de seis meses son la huella | Hay que recorrer la historia de cada cliente en cada paso del cálculo | Red como meta; es la más difícil. Si no, sale precalculado |
| Eventos raros, series de tiempo, segmentación | | | | Lámina de hoja de ruta. No se construyen |

Cada motor tiene además su versión con el método lento de siempre (MCMC), que se calcula una vez y se guarda: es la vara para validar la red y el plan B de la tarjeta. Una tarjeta que sale del plan B se rotula «precalculado» y el guion no dice que responde la red. La regresión simple queda solo como «el método rápido de siempre», para mostrar qué se pierde sin el modelo completo. El detalle técnico está en la sección 11.

### 1.3 Las cuatro vistas

**Vista 1 · Inicio: «¿Qué quieres saber?»**
- Cuatro tarjetas: «Caso tipo Buk · ¿A quién conviene retener?», «Terreno · ¿Dónde limpio y dónde mido?», «Caso tipo AgendaPro · ¿Qué citas conviene confirmar?», «Crédito · ¿A quién le apruebo?».
- Abajo, en chico: «Casos de ejemplo con datos públicos. No son datos de estas empresas.»

**Vista 2 · Respuesta.** Es la pantalla principal. De arriba abajo:
1. **Titular en una frase.** «[N] personas están en duda. No saber te cuesta [plata].»
2. **Lo que te cuesta no saber**, en grande.
3. **Dos deslizadores de costos**, con su pregunta en palabras («¿Cuánto te cuesta reemplazar a alguien?»). Al moverlos cambian los colores, el titular y el número, sin espera. Dicen «supuesto».
4. **Las unidades en tres colores.** En casos de tabla, una lista ordenada con una barra por unidad que muestra su rango y la línea del punto de corte. En casos espaciales, un mapa.
5. **Qué pesa.** Cada factor con una flecha y una etiqueta: «seguro», «probable» o «no se puede saber con estos datos». En el terreno dice qué manda: el río, lo que pasa en los bloques vecinos o el error de cada medición.
6. **El examen.** «Escondimos a [294] personas reales. De las que dijimos [30]% de riesgo, se fue el [N]%.»
7. **Pie:** qué motor usó, de dónde vienen los datos y, si la respuesta salió del plan B, el rótulo «precalculado».

En casos con mapa, además:

8. **Botón «¿Dónde mido?».** Aparecen tres pines, cada uno con lo que vale medir ahí, y una línea: «Para saberlo rehíce [N] análisis completos en [X] segundos». Clic en un pin: «sale bajo / medio / alto». Se elige uno y el mapa, el número grande y los pines cambian.

**Vista 3 · Todos a la vez (Cartera).**
- Un botón: «Analizar a todas mis empresas».
- Un contador que sube: «[1.000] análisis en [N] segundos».
- Una tabla ordenada por lo que les cuesta no saber, con una columna «por persona». Las empresas son simuladas, cada una distinta, y la pantalla lo dice.

**Vista 4 · Sabe cuando no sabe.** Es un estado de la vista 2, no una pantalla aparte.
- Se carga el archivo malo (tecla `M`): el caso de rotación con una columna que delata la respuesta.
- Aparece **la nube**: miles de puntos, cada uno una empresa simulada con la que Krylov practicó, y el archivo como un punto rojo afuera. Texto: «No se parece a nada que haya visto».
- Banda roja con el motivo en una línea y un botón con la corrección propuesta. Se aplica, el punto cae dentro de la nube y la pantalla pasa a verde.

Reglas de pantalla: nada tarda más de dos segundos, ninguna palabra de estadística, todo lo simulado rotulado, toda cifra registrada en `pitch/CIFRAS.md`.

### 1.4 Dónde se ve la simulación

Es el nombre del track y era lo que el plan anterior no mostraba. Ahora aparece cinco veces, y ninguna se corta. Desde D-26, además, es cierta en las cuatro tarjetas: cada una responde con una red que practicó con casos simulados de su propio modelo.

| Dónde | Qué se simula | Qué se dice |
|---|---|---|
| La nube (vista 4) | Empresas inventadas con las reglas del motor: las mismas con que practicó | «Esto es con lo que practicó» |
| «¿Dónde mido?» | Cientos de resultados posibles de una medición que todavía no se hace | «Imaginó [N] resultados y rehízo el análisis para cada uno» |
| El clic en un pin | Una medición | «Mido, sale alto, y el mapa cambia» |
| La cartera (vista 3) | 1.000 empresas inventadas con esas mismas reglas, cada una distinta | «Con el método de siempre, [horas]. Krylov, [segundos]» |
| El cierre | Los casos del entrenamiento | «Anoche practicó con [N] millones de empresas y terrenos simulados» |

### 1.5 Lo que se cortó y los opcionales

Cortado (decisiones D-17 y D-26): el motor de eventos raros; la voz; WhatsApp; la caja de pregunta libre; las tarjetas sintéticas de licitaciones, obras y cargadores; el análisis a mano con cronómetro; y **«Sube tus datos»** con la capa de lenguaje, porque cada motor responde una familia de archivos y no un CSV cualquiera.

**No hay opcionales.** Todo el tiempo de PC 2 va a los cuatro motores. Lo que antes era opcional y ahora es obligatorio: «qué manda en el terreno», que sale del análisis mismo.

## 2. Dónde se usa

### 2.1 Sponsors

La web del evento lista once: Anthropic, Buk, ElevenLabs, Vercel, Render, Kairos, Kapso, CChC, AgendaPro, Copec y Lici. Cognition no aparece y no se menciona. PC 3 lo confirma mirando el lugar (tarea S-10).

Regla: un caso con el nombre de un sponsor es una hipótesis de uso con datos públicos. No es una afirmación sobre cómo trabaja esa empresa.

| Sponsor | Papel | Qué se muestra | ¿Construido? |
|---|---|---|---|
| **Buk** (anfitrión) | Caso | ¿A quién conviene retener? Datos públicos ficticios creados por IBM, 1.470 personas | Sí. Abre el demo |
| **AgendaPro** | Caso | ¿Qué citas conviene confirmar? Datos públicos reales, 110.527 citas médicas | Sí |
| **Anthropic** | Herramienta | Claude Code construyó el producto. No está integrado en la app y no se dice otra cosa | Sí, como herramienta |
| **Vercel** | Infraestructura | La web y las respuestas precalculadas | Sí |
| **Render** | Infraestructura | La API del cálculo en vivo; la URL pública no depende de ella | Sí |
| ElevenLabs, Kapso, Kairos, CChC, Copec, Lici | No se usan | No se nombran como usados. Pueden ir en la lámina de hoja de ruta como industrias | No |

Además, dos tarjetas sin sponsor: **Crédito** (30.000 clientes reales de tarjetas) y **Terreno** (155 mediciones reales de metales en un suelo).

Solo se dice «usamos X» si X está integrado y funcionando a las 18:00. El show ya no pide al jurado que elija una empresa: con cuatro tarjetas se abre Buk directamente. La elección queda para la versión de cinco minutos («elijan otra pregunta»).

### 2.2 A quién se le vende primero

**A plataformas de software que ya atienden a miles de empresas**, como Buk o AgendaPro. Ninguno de sus clientes va a contratar un data scientist; la plataforma integra Krylov y le da uno a cada cliente. Es una sola venta que llega a miles de empresas. Segundo: quienes toman decisiones caras con mediciones caras (suelos, minería, obras), donde «¿Dónde mido?» paga solo.

Esta decisión no depende de respuestas de nadie.

## 3. El negocio, en una lámina

No lo puntúa ningún criterio. Va en una frase del pitch si sobra tiempo y en una lámina de respaldo.

- **Precio (hipótesis sin validar):** US$ 20 al mes por empresa que lo usa, cobrado a la plataforma.
- **La unidad:** cada 1.000 empresas activas son US$ 240.000 al año. Cada plataforma nueva es una sola venta.
- **Sin meta anual.** La del plan anterior suponía dos pilotos y 20% de adopción el primer año, y se veía ingenua.
- **Por qué ahora:** SAP anunció en mayo de 2026 la compra de Prior Labs, que entrena modelos con datos sintéticos para predecir sobre tablas, con el compromiso de invertir «más de 1.000 millones de euros en los próximos cuatro años» (no es el precio de compra).
- **En qué nos diferenciamos:**

| Frente a | Ellos | Nosotros |
|---|---|---|
| Subirle el archivo a un asistente genérico | Escribe un programa nuevo cada vez. Lo medimos nosotros: [resultado de la prueba S-09] | La misma respuesta siempre, con la duda medida en plata y un examen con datos reales |
| Modelos para tablas (Prior Labs y similares) | Predicen una columna | Decimos qué hacer, cuánto cuesta no saber y dónde averiguar más; y tenemos un motor para datos con ubicación |
| Un data scientist | Días por análisis | Un segundo, para todas las empresas a la vez |

Lo que todavía no es ventaja: la tecnología se puede copiar. Hoy la ventaja es el equipo, que investiga exactamente en esto, y llegar primero. Se dice así.

## 4. El show

### 4.1 Formato

- **Presentaciones generales:** domingo 09:30 a 11:30, todos los equipos, repartidos en tres escenarios. Los mejores pasan a la final.
- **Finales:** 12:00 a 14:30.
- **Duración del pitch:** sin publicar. En 2024 fueron tres minutos. Los tramos grabados de otras sedes de 2026 duran cerca de seis minutos con las preguntas. Se confirma con la consulta S-02 y en la charla «Cómo hacer un buen demo» del sábado a las 20:00.
- Por eso el guion existe en tres largos: 90 segundos, tres minutos y cinco minutos.

### 4.2 Los momentos

El texto completo está en `pitch/GUION.md`, que PC 3 pone al día en cada ronda. Aquí, la estructura:

| # | Tiempo | Momento | Pantalla | Criterio que toca |
|---|---|---|---|---|
| 1 | 0:00 a 0:25 | El nombre y el problema | Tarjetas | Originalidad |
| 2 | 0:25 a 1:00 | La respuesta de Buk: colores de decisión, deslizador, lo que cuesta no saber, «no se puede saber», el examen | Vista 2 | Impacto, técnico |
| 3 | 1:00 a 1:25 | Archivo malo: la nube, la corrección, verde | Vista 4 | Técnico, originalidad |
| 4 | 1:25 a 2:25 | Terreno y «¿Dónde mido?»: pines, análisis rehechos, la comparación, el clic | Mapa | Técnico, ambición, impacto |
| 5 | 2:25 a 2:40 | Todos a la vez | Cartera | Impacto |
| 6 | 2:40 a 3:00 | Cierre: cómo funciona, el QR y la frase | Lámina | Ambición, ejecución |

**Versión de 90 segundos:** momentos 1 (dos frases), 2 y 4, y la frase. **Lo primero que se corta es la cartera. El mapa no se corta nunca.**

La comparación del momento 4 tiene tres números y los tres se miden: lo que tarda Krylov, lo que tarda rehacer los mismos análisis con el método lento de siempre, y cuánto acierta el método rápido de siempre cuando dice 90%. La frase dice exactamente qué se comparó.

### 4.3 El recorrido, clic por clic

Esto es lo que PC 1 tiene que dejar funcionando sin tocar el teclado más de lo indicado.

| # | Acción | Qué aparece | Tiempo máximo |
|---|---|---|---|
| 1 | Se abre la app | Vista 1 con cuatro tarjetas | ya abierta |
| 2 | Clic en la tarjeta de Buk | Vista 2 completa | 1 s |
| 3 | Arrastrar el deslizador «reemplazar a alguien» | Colores, titular y número cambian mientras se arrastra | inmediato |
| 4 | Tecla `M` | La nube con el archivo afuera, banda roja y motivo | 1 s |
| 5 | Clic en el botón de corrección | El punto entra a la nube; pasa a verde | 1 s |
| 6 | Tecla `T` | Mapa del terreno en tres colores, con las mediciones | 1 s |
| 7 | Clic en «¿Dónde mido?» | Tres pines con plata y el conteo de análisis | 2 s |
| 8 | Clic en el pin A, luego en «sale alto» | El mapa, el número y los pines cambian | 2 s |
| 9 | Tecla `C` | Cartera: contador y tabla | 3 s con animación |
| 10 | Tecla `L` | Lámina de cierre con la frase y el QR | inmediato |

Las teclas existen para no depender del mouse en un escenario. Todo el recorrido funciona sin internet y también en la URL pública en modo estático.

### 4.4 Palabras

| No se dice | Se dice |
|---|---|
| posterior, distribución | «rango creíble», «lo que de verdad sabemos» |
| valor de la información | «lo que te cuesta no saber», «cuánto vale averiguarlo» |
| inferencia amortizada | «ya practicó con millones de casos simulados» |
| calibración | «dijimos 30% de riesgo y pasó el 28%» |
| fuera de distribución | «no se parece a nada que haya visto» |
| MCMC | «el método lento de siempre» |
| modelo generativo, prior | «las reglas con que Krylov inventa empresas» |
| regresión logística, bayesiano, kriging | no se nombran; si preguntan: «el método rápido de siempre» |
| «se va, seguro», «senior» | «conviene retener». La palabra «senior» sale de todo |
| simular, simulación | se dicen tal cual, y a menudo: es el nombre del track |

### 4.5 Láminas

La portada y el cierre van dentro de la app (tecla `L`), para no cambiar de ventana. Las de respaldo, en un archivo aparte que solo se abre si preguntan.

1. **Portada:** «Krylov» y la frase.
2. **Cierre:** la frase, el equipo, el QR, y una franja con terrenos simulados pasando.
3. **Respaldo técnico:** por motor, el modelo en una línea, cómo se entrenó (casos simulados, minutos, computador), el sello, la comparación con el método lento y con el rápido, el examen con datos reales, y qué no hace todavía. Esta lámina sí usa los nombres técnicos.
4. **Respaldo de negocio:** la unidad, el primer cliente, la tabla de diferencias.
5. **Respaldo: qué existe hoy y qué es hoja de ruta.**

### 4.6 Si algo falla en vivo

| Falla | Qué se hace |
|---|---|
| No hay internet | Nada cambia: el demo corre en el computador que presenta. Se ensaya así |
| La app se cae | Video de respaldo en la pestaña de al lado, narrado en vivo |
| «¿Dónde mido?» tarda más de 2 segundos | Se sirve el resultado precalculado, que está siempre |
| Se acaba el tiempo | Se salta al cierre. Los momentos 3 y 5 son prescindibles; el 4 no |

## 5. Preguntas difíciles

| Pregunta | Respuesta |
|---|---|
| ¿En qué se diferencia de subirle el archivo a un chat? | Lo probamos: el mismo archivo y la misma pregunta, tres veces. [Resultado de S-09.] Krylov da siempre la misma respuesta, mide la duda en plata y rinde un examen con datos reales. Y un chat no te dice dónde medir |
| ¿Quién eligió las columnas y los costos? | Los costos, tú: son los deslizadores, y la respuesta cambia en vivo. Las columnas, nosotros: cada motor pide las que su modelo necesita (el tiempo en la empresa, las encuestas, el cargo), y la pantalla lo dice |
| ¿Dónde está la simulación? | En todo. Cada tarjeta responde con una red que practicó con [N] millones de empresas o terrenos inventados con reglas conocidas. Antes de responder compara tu archivo con esos casos simulados. Y para decir dónde medir, simula cientos de resultados posibles de una medición que todavía no haces |
| ¿De verdad reemplaza a un data scientist? | Reemplaza el análisis de rutina. Para una empresa que no tiene ninguno, es el primero |
| ¿Estos son datos de Buk o de AgendaPro? | No. Son datos públicos, y lo dice la pantalla. Son casos tipo, para mostrar la pregunta |
| ¿Hablaron con clientes? | [Si hubo conversación con alguien de Buk: la frase textual, con permiso.] Si no: «Todavía no, y no lo vamos a inventar. Es lo primero que haríamos el lunes» |
| ¿Qué impide que lo copien? | Hoy, poco: el equipo, que investiga en esto, y llegar primero. La ventaja se construye con cada motor nuevo y con el historial de exámenes |
| ¿Qué existe hoy y qué es lámina? | Existe una app en línea con cuatro casos, cada uno con su modelo, y [N] redes entrenadas entre anoche y hoy [las que hayan pasado; las demás tarjetas dicen «precalculado»]. Series de tiempo y eventos raros son hoja de ruta |
| ¿Suben cualquier archivo? | Todavía no. Cada motor responde un tipo de pregunta con un tipo de archivo. Agregar un tipo nuevo es escribir sus reglas y dejarlo practicando una noche |
| ¿Y si se equivoca? | Por eso el examen: escondemos datos reales y mostramos cuánto acertó. Y cuando el archivo no se parece a nada que conozca, no responde |
| ¿Mis datos salen de la empresa? | No hace falta: los motores son chicos y pueden correr dentro de la empresa. Ningún modelo de lenguaje ve los datos |
| ¿Quién paga y cuánto? | La plataforma que lo integra. Pensamos en US$ 20 al mes por empresa que lo use; es una hipótesis y lo decimos así |

Técnicas, para quien las haga:

| Pregunta | Respuesta |
|---|---|
| ¿Esto es inferencia basada en simulación de verdad? | Sí. Cada caso tiene un modelo generativo explícito (prior, efectos por grupo, latentes por unidad, censura y faltantes), un simulador, y una red entrenada solo con simulaciones para entregar el posterior de los parámetros (NPE con un flujo normalizador condicional sobre un codificador de conjuntos). Lo local se integra exacto. Está en el README y en el código |
| ¿Por qué no usar MCMC y listo? | Lo usamos, como referencia. Tarda [X] minutos por empresa en [el modelo de rotación]; la red, [Y] milisegundos, con las mismas medias y rangos en [N] casos comparados. Para una plataforma con miles de empresas, es la diferencia entre [horas] y [segundos] |
| En el terreno, un MCMC con 155 puntos tarda segundos | Cierto, y lo decimos. Ahí lo caro es «¿Dónde mido?»: rehacer [N] análisis completos toma [M] minutos con el método de siempre y [X] segundos con la red |
| En ese modelo hay atajos para no rehacer cada análisis desde cero | Sí, en el modelo del terreno los hay, y los conocemos. La red no depende de ellos: funciona igual en modelos donde no existen. Lo que medimos y decimos es rehacer cada análisis completo |
| ¿Cómo saben que la red no se equivoca? | Cuatro chequeos por motor: SBC y cobertura en [N] simulaciones nuevas; contra el MCMC en [5 a 10] datasets simulados y en el real; el examen con datos reales reservados; y un archivo mal especificado, que tiene que caer fuera |
| ¿Y los motores que no pasaron? | Esas tarjetas muestran el resultado del MCMC, calculado antes, y dicen «precalculado». No decimos que ahí responde la red |
| ¿De dónde salen las covariables de las empresas simuladas? | Mitad remuestreando filas reales con perturbaciones y mitad de un generador propio. La red generaliza hasta donde llega ese generador, y está escrito en las limitaciones |
| ¿Ese 90% es sobre sus propias simulaciones? | El del sello, sí, y por eso va en la lámina técnica. Lo que decimos en voz alta es el examen con datos reales |
| ¿Qué pasa con datos que no se parecen al entrenamiento? | Dos detectores, y basta que marque uno. El que se dibuja usa dos medidas con nombre; el otro mide la distancia en los resúmenes que aprendió la red. No dependemos solo del segundo, porque una red puede mandar algo que nunca vio a cualquier parte |
| ¿Por qué una grilla en el terreno y no los puntos tal cual? | Porque en la grilla agregar una medición hipotética es trivial y rehacer 480 análisis es una sola pasada. En los otros tres motores la red sí recibe las filas tal cual, en cualquier orden y cantidad |
| ¿Qué no hace todavía? | Archivos fuera de las cuatro familias, empresas con más de 2.000 filas por análisis, terrenos en tres dimensiones, más de 400 mediciones. Está en la lámina técnica |

## 6. Plan hora a hora

P son las tareas de PC 1 (producto), A las de PC 2 (amortización) y S las de PC 3 (seguimiento). Cada tarea tiene un identificador, una duración, un entregable y una forma de saber que está lista. Las duraciones suponen que Claude Code escribe el código y la persona revisa. Las instrucciones de arranque de cada computador están en su archivo `PC*.md`.

Regla de corte: **si una tarea lleva el doble de su duración, se corta o se simplifica, se anota en `estado/` y se sigue.** A las 18:00 el producto está terminado con lo que haya.

**Regla de adelanto (D-29): las horas de este plan son topes, no horas de inicio.** Cada tarea se empieza apenas existen sus insumos, en el orden de la lista de su rol; al terminar una se toma la siguiente sin esperar su hora, y los agentes de noche siguen con las tareas de día cuando terminan su lista nocturna. Si falta un insumo (una red entrenada, muestras del MCMC, un archivo de otro rol), la tarea se construye contra el ejemplo fijo, datos simulados o la red sin entrenar, se anota «pendiente de <insumo>» y se pasa a la siguiente. No se adelanta lo que no depende de la hora: un entrenamiento por computador; el MCMC nunca encima de un entrenamiento; los tiempos del guion se miden sin nada entrenando; un motor responde con `red` solo después de `validar-motor`; lo que exige a una persona. Los hitos y los H2 por motor son plazos máximos y se pueden pasar antes.

**Si el arranque se atrasa** respecto de las 03:00: se corre el bloque de la madrugada, pero nadie se duerme después de las 05:45 y PC 2 no se duerme sin dejar el entrenamiento corriendo. Lo que no alcanzó pasa a la lista nocturna del agente. El despertar y todo lo que viene después no se mueven.

### 6.1 Vista general

| Bloque | PC 1 · producto | PC 2 · amortización | PC 3 · seguimiento |
|---|---|---|---|
| **03:00 a 03:45** Arranque | Clonar, espejo, entorno. P-01 | Clonar, espejo, entorno. A-01 | S-01 a S-03 |
| **H0 · 03:45** | | | |
| **03:45 a 05:15** | P-02 (primer despliegue), P-03 | Dos sesiones: A-02 a A-04 y A-B1 a A-B4. **Dos entrenamientos lanzados** | S-04, S-05. **Lanza `supervivencia` en su computador a las 04:55** |
| **05:15 a 08:30** | Duerme. El agente hace su lista nocturna | Duerme. `espacial` entrena. El agente hace A-N1 a A-N6 | Duerme hasta las 08:15. `supervivencia` entrena |
| **H1 · 08:45** | | | S-06 |
| **08:30 a 12:15** | P-04 a P-08 | A-08 a A-12. `estados` entrena de fondo | S-07 a S-12. `jerarquico` entrena |
| **H2 · 12:15** | | | |
| **12:30 a 15:00** | P-09 a P-11 | A-13 a A-16. H2 de `jerarquico` (13:00) y `estados` (14:00) | S-13 a S-15 |
| **H3 · 15:00** | | | |
| **15:00 a 18:00** | P-13, P-14 | A-17, A-18. Tope de motores: 16:00 | S-16 a S-18 |
| **PRODUCTO TERMINADO · 18:00** | | | |
| **18:00 a 22:00** Iterar demo y pitch | Ajustes de texto y orden | Respaldo técnico, respuestas | Ensayos, extraños, charla |
| **22:00 a 00:00** | Video de respaldo | README técnico | Entrega |
| **Dom 00:00 a 06:00** | Duermen los tres | | |
| **06:30 a 09:30** | Ensayos 06:30 y 07:30. Entrega 08:00 | | |

Comidas del evento, para no planificar encima: desayuno 08:30 a 10:30, almuerzo 13:30 a 15:00, comida 21:00 a 22:30.

### 6.2 PC 1 · producto (backend, frontend y despliegue)

Dueño de `servicio/` y `web/`. Skills: `desplegar`, `preparar-demo`. Herramientas: `STACK.md`, sección 2.

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| P-01 | 03:15 | 30 | Entorno y esqueleto: una API que devuelve los ejemplos fijos de `contratos/ejemplos/`, una web que pinta las tarjetas y una respuesta, y el modo estático leyendo copias de esos ejemplos en `web/public/estatico/` | `servicio/`, `web/` | Con dos comandos se ve una respuesta de ejemplo en el navegador; con `?estatico=1` se ve igual con la API apagada |
| P-02 | 03:45 | 30 | **Primer despliegue** (skill `desplegar`). Se hace hoy, con los tres despiertos, porque necesita al dueño de la cuenta `Silent-math` | URL en `estado/producto.md` | Otra persona abre la URL desde su teléfono y ve las tarjetas |
| P-03 | 04:15 | 45 | Vista 1 y vista 2 para casos de tabla (`analizar_tabla.json`), contra el ejemplo fijo: titular, número grande, lista con barra, rango y línea del punto de corte, «qué pesa», pie | Componentes | Se lee completa en tamaño de proyector |
| | 05:00 | 15 | Dejar al agente la lista nocturna y actualizar el estado | | |
| | 05:15 | | **Duerme hasta las 08:30** | | |
| P-N1 | noche | | *Agente solo.* `web/src/decision.ts` con la regla de `CONTRATO.md`, sección 3, y su prueba contra `decision_prueba.json`. Deslizadores de costos que recalculan colores, titular y número | | La prueba pasa |
| P-N2 | noche | | *Agente solo.* Mapa en canvas con el ejemplo espacial: bloques en tres colores, mediciones como puntos, leyenda | | Se ve con el ejemplo fijo |
| P-N3 | noche | | *Agente solo.* La nube en canvas con `nube.json`: puntos, el archivo en rojo, ejes en palabras | | Se ve con el ejemplo fijo |
| P-04 | 08:30 | 30 | Revisar lo que dejó el agente. Los deslizadores se sienten bien al arrastrar | | Arrastrar no tiene saltos ni esperas |
| P-05 | 09:00 | 30 | Conectar `nucleo.api.analizar` real para rotación. Primera versión de `servicio/exportar_estatico.py`. Redespliegue | Ruta real | La tarjeta de Buk responde con datos reales en local y, precalculada, en la URL |
| P-06 | 09:30 | 50 | Mapa: terminar sobre el ejemplo y conectar el real cuando PC 2 entregue A-10 | Componente | El terreno real se ve como mapa de tres colores |
| P-07 | 10:20 | 50 | Vista 4: tecla `M`, la nube, banda roja con el motivo, botón de corrección, paso a verde | Estado rojo | El archivo malo recorre rojo, corrección, verde |
| P-08 | 11:10 | 40 | Vista 3: botón, contador animado, tabla ordenada con columna «por persona» | Componente | Con la función de PC 2, 1.000 empresas aparecen ordenadas |
| | 11:50 | 20 | Redespliegue, medir el tiempo desde un teléfono, estado | | Listo para H2 |
| P-09 | 12:30 | 75 | **«¿Dónde mido?»:** botón, tres pines con plata, línea de análisis rehechos, clic en un pin, «sale bajo / medio / alto», el mapa y los pines cambian. Animación del cambio | Componente | Los pasos 7 y 8 del recorrido salen en menos de 2 segundos cada uno |
| | 13:45 | 20 | Almuerzo | | |
| P-10 | 14:05 | 25 | Panel del examen y pie. Rótulo «precalculado» cuando la respuesta trae `precalculado: true`. «Qué pesa» también en el mapa | Panel | Lee del JSON; no hay números escritos a mano |
| P-11 | 14:30 | 30 | Modo demo: teclas `M`, `T`, `C`, `L`, semilla fija, pantalla completa. `exportar_estatico` con todas las claves del recorrido. Redespliegue | Atajos | El recorrido de 4.3 sale completo sin internet y en la URL con `?estatico=1` |
| P-12 | | | **Cortada (D-26).** No hay «Sube tus datos». Sus 45 minutos van a recibir inasistencias y crédito (llegan a las 14:10 y 14:50) y a `exportar_estatico` con la implementación final de cada motor (16:00) | | |
| P-13 | 16:00 | 40 | Portada y cierre dentro de la app (tecla `L`) con el QR guardado como imagen y la franja de terrenos simulados. La vista 2 se lee en un teléfono | Láminas | El QR abre la URL y la respuesta se lee sin hacer zoom |
| P-14 | 16:40 | 50 | Pulido para proyector con los textos de PC 3. Borrar código muerto. Último despliegue. Sacar lo que no funcione | Tag `congelado` | El recorrido sale dos veces seguidas en la URL pública |
| | 17:30 | 30 | Skill `preparar-demo` completa | | Los 17 puntos marcados |

**Desde D-26, lo real de PC 2 llega más tarde que las horas de esta tabla:** rotación 10:15, terreno 11:00, `donde_medir` 12:00, cartera y nube 13:15, inasistencias 14:10, crédito 14:50. P-05 a P-09 se construyen contra el ejemplo fijo a su hora y se conectan cuando llega cada función. PC 1 no entrena ni corre el método lento.

Qué recibe: de PC 2, las funciones de `nucleo/api.py`; de PC 3, los casos, los datos y los textos de pantalla. Qué entrega: la URL y el demo.

### 6.3 PC 2 · amortización de los modelos

Dueño de `nucleo/` y `motor/`. Skills: `medir-rendimiento`, `entrenar-motor`, `validar-motor` (por `motor_id`). Herramientas: `STACK.md`, sección 3. Los cuatro modelos y la arquitectura están en la sección 11. **Reescrita por la decisión D-26.**

**Lo que no puede fallar esta noche: a las 05:15 quedan dos entrenamientos corriendo, `espacial` en PC 2 y `supervivencia` en PC 3.** Si hay que elegir, `espacial`: es el momento estrella.

**Dos sesiones de Claude Code en PC 2, repartidas por archivos.** La sesión A toca solo `espacial` y lo compartido (`pyproject.toml`, `nucleo/preproceso.py`, `nucleo/flujo.py`, `motor/comun/`). La sesión B toca solo `motor/supervivencia/` y `nucleo/supervivencia.py`; importa `motor/comun/` y no lo edita. La persona revisa las pruebas de humo de las dos.

**Lo mínimo para lanzar un entrenamiento** es simulador, codificador, flujo, pérdida, puntos de guardado y una prueba de humo con un SBC chico. La cuadratura local, el MCMC y `api.py` no bloquean el lanzamiento: van en la lista nocturna o en la mañana.

**Calendario de cómputo.** Un entrenamiento por computador. PC 1 (Ryzen con 1,3 GiB libres) no entrena ni corre MCMC. Los tiempos y los millones de datasets son estimaciones hasta que `medir-rendimiento` los mida, motor por motor, antes de lanzar.

| Cuándo | PC 2 · MacBook Air M4, 16 GB | PC 3 · MacBook Air M3, 16 GB |
|---|---|---|
| 05:15 a 08:30 | Entrena `espacial` [~3 h, del orden de millones de terrenos; por medir] | Entrena `supervivencia` [~3 h; por medir]. Lo lanza la persona de PC 3, que no se duerme antes |
| 08:30 a 09:15 | **Nada entrenando.** `validar-motor espacial` y MCMC de referencia de `espacial` y `supervivencia` | Desde las 08:30 entrena `jerarquico` (hasta las 11:30) |
| 09:15 a 12:00 | Entrena `estados` de fondo | Sigue `jerarquico`. A las 11:30: `validar-motor jerarquico` y su MCMC |
| 12:00 a 12:30 | **Nada entrenando.** Se miden los tiempos de `donde_medir`, la cartera y el recorrido | Libre: MCMC que falte |
| 12:30 a 13:30 | `validar-motor estados` y su MCMC | Libre para reentrenar el motor que haya fallado |

Reglas del calendario: las mediciones de tiempo se hacen sin ningún entrenamiento corriendo en ese computador. El MCMC nunca corre encima de un entrenamiento. Si a las 08:30 `supervivencia` no sirve, se relanza en PC 3 y tiene prioridad sobre `jerarquico`. Si a las 09:00 algo va atrasado, una persona abre una sesión de Kaggle o Colab y mira la cuota (diez minutos); se cuenta con eso solo si de verdad está disponible (`STACK.md`, 3.3).

**H2 por motor:** `espacial` y `supervivencia`, 12:15. `jerarquico`, 13:00. `estados`, 14:00. **Tope para cualquier motor: 16:00.** El que no pasó a su hora sale con la implementación `mcmc`, rotulado «precalculado» (sección 6.5).

#### Madrugada, sesión A (`espacial` y lo compartido)

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| A-01 | 03:15 | 30 | Entorno (`pyproject.toml` con el grupo `entrenar`: `torch`, `zuko`, `numpyro`, `onnx`). `motor/comun/`: codificador de conjuntos con máscara, flujo de acoplamiento afín condicional, bucle de entrenamiento con puntos de guardado y conteo de datasets. `nucleo/flujo.py`: el mismo flujo en NumPy. **Subirlo a las 03:45: la sesión B lo espera** | `pyproject.toml`, `motor/comun/`, `nucleo/flujo.py` | Prueba: con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra (tolerancia `float32`). El codificador sin entrenar exporta a ONNX con n variable |
| A-02 | 03:45 | 30 | `nucleo/preproceso.py` para terrenos y simulador de 11.5: campo por Fourier, río como curva suave al azar con su campo de distancia, tendencia, mediciones al azar y agrupadas | `motor/espacial/simular.py` | Una prueba compara el campo con el método directo en una grilla chica; el preprocesamiento da idéntico en NumPy y `torch` |
| A-03 | 04:15 | 30 | Red convolucional de tres canales con cabeza de mapa y cabeza de flujo (**gradiente cortado hacia el codificador**). Exportar a ONNX la red sin entrenar | `motor/espacial/red.py`, `exportar.py` | La pérdida de la cabeza de mapa es idéntica con y sin la cabeza de flujo; `onnxruntime` da lo mismo que `torch` |
| A-04 | 04:45 | 20 | Prueba de humo de 3 minutos y SBC chico. **Si los tres canales no pasan, se lanza la red de dos canales.** `medir-rendimiento espacial` y lanzar con `entrenar-motor espacial` | Proceso corriendo en PC 2 | Existe el primer punto de guardado y el estado dice cómo retomar |

#### Madrugada, sesión B (`supervivencia`)

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| A-B1 | 03:15 | 45 | Simulador vectorizado de 11.2, con n y número de cargos variables, covariables por remuestreo y por generador, y δ borrado en 20%. Mirar el predictivo a priori contra `datos/demo/rotacion.csv` (tasa de renuncia, años) y ajustar el prior | `motor/supervivencia/simular.py`, `config.json` | La tasa de renuncia y la mediana de años del archivo real caen dentro de lo simulado. Un dataset simulado con θ conocido tiene las formas correctas |
| A-B2 | 04:00 | 30 | Codificador jerárquico (filas → cargo → dataset) y flujo sobre los 32 parámetros, con lo de `motor/comun/`. Exportar el codificador sin entrenar | `motor/supervivencia/red.py` | Exporta a ONNX con n variable; la pérdida baja en 2 minutos |
| A-B3 | 04:30 | 25 | Prueba de humo: 5 minutos de entrenamiento y SBC chico de 200 datasets (no tiene que pasar; tiene que correr y mejorar). `medir-rendimiento supervivencia` | Números en el estado | Datasets por segundo y pasos por segundo, medidos |
| A-B4 | 04:55 | 15 | Subir. **La persona de PC 3 hace `git pull`, `uv sync --group entrenar` y lanza `entrenar-motor supervivencia`** | Proceso corriendo en PC 3 | Primer punto de guardado en PC 3; `estado/seguimiento.md` dice cómo retomar |
| A-05 | 05:10 | 5 | Dejar al agente la lista nocturna. Actualizar el estado | | |
| | 05:15 | | **Duerme hasta las 08:30.** Tapa abierta, enchufado, en los dos computadores | | |

Si a las 04:55 `supervivencia` no tiene prueba de humo: no se trasnocha. El agente la termina de noche y se lanza a las 08:30 en PC 3; su H2 pasa a las 13:30 y `jerarquico` espera turno o va a Kaggle o Colab.

#### Lista nocturna (agente solo, PC 2). Solo código, con pruebas de dos minutos como máximo

| Id | Tarea | Entregable | Listo cuando |
|---|---|---|---|
| A-N1 | `nucleo/decision.py` con su prueba contra `decision_prueba.json`. `nucleo/api.py`: `casos`, y `analizar` que elige `red` o `mcmc` por la variable del motor | `nucleo/decision.py`, `nucleo/api.py` | La prueba pasa |
| A-N2 | `supervivencia`: paso local (cuadratura anidada cargo → persona, vectorizada por cargo) y modelo en NumPyro. **Medir el presupuesto:** un análisis de 1.470 personas con 32 muestras | `nucleo/supervivencia.py`, `motor/supervivencia/mcmc.py` | Menos de 1 segundo por análisis, o anotado con cuántos nodos lo logra. En un dataset simulado, el paso local con el θ verdadero da probabilidades calibradas |
| A-N3 | `espacial`: kriging dado θ en NumPy, y modelo en NumPyro | `nucleo/espacial.py`, `motor/espacial/mcmc.py` | En una grilla chica coincide con el cálculo directo |
| A-N4 | `jerarquico`: simulador de 11.3 (con la asignación del SMS) y modelo en NumPyro | `motor/jerarquico/simular.py`, `mcmc.py` | Predictivo a priori revisado contra las tasas anotadas en 11.3 |
| A-N5 | `estados`: simulador de 11.4, **con d_1 < d_2 < d_3 en el prior**, y modelo en NumPyro con el filtro forward marginalizado | `motor/estados/simular.py`, `mcmc.py` | El filtro forward coincide con la enumeración directa en un caso chico |
| A-N6 | Codificador y flujo de `jerarquico` y de `estados`, con exportación sin entrenar. **Sin lanzar entrenamientos** | `motor/<id>/red.py` | Exportan a ONNX |

Reglas de la noche: no tocar el proceso de entrenamiento; ninguna corrida de MCMC ni entrenamiento, solo pruebas cortas; commits chicos; si algo exige una decisión, se anota y se pasa a lo siguiente. **El plan de la mañana no depende de que el agente termine A-N4 a A-N6**: lo que falte se hace a las 08:30 y los H2 de esos motores se corren.

#### Sábado de día

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| A-08 | 08:30 | 45 | Revisar lo nocturno. Detener `espacial` y correr `validar-motor espacial` (SBC, cobertura por grupos). MCMC de referencia de `espacial` y `supervivencia`: 5 datasets simulados más el real, con su tiempo. La persona de PC 3 sube el punto de guardado de `supervivencia` y lanza `jerarquico` | `sello.json` de `espacial`; muestras en `artefactos/<id>/mcmc/` | El estado dice «pasa» o «no pasa» con los números. **Con el MCMC guardado, las dos tarjetas ya tienen plan B** |
| A-09 | 09:15 | 15 | Prueba de humo y lanzar `estados` de fondo en PC 2 | Proceso corriendo | Primer punto de guardado |
| A-10 | 09:30 | 45 | `analizar` de rotación: codificador, flujo, paso local, `factores`, examen. `validar-motor supervivencia`. Entregar a PC 1 y pasar a PC 3 lo que salió | Ruta de rotación | La tarjeta de Buk responde en menos de 1 segundo, con la red o con `mcmc` |
| A-11 | 10:15 | 45 | `analizar` del terreno real: mapa, `factores` («qué manda»), examen escondiendo 20% de las mediciones | Ruta espacial | El terreno responde en menos de 1 segundo; el examen tiene números |
| A-12 | 11:00 | 60 | **`donde_medir`** y la medición simulada vía `analizar(mediciones=…)` | `nucleo/api.donde_medir` | Devuelve tres candidatas |
| | 12:00 | 15 | Detener `estados`. **Sin nada entrenando:** medir `donde_medir` (análisis rehechos, segundos con la red, tiempo del MCMC por análisis) y `analizar`. Números para H2 | Tiempos en el estado | Tres candidatas en menos de 2 segundos |
| A-13 | 12:30 | 45 | Cartera: 1.000 empresas del simulador de `supervivencia`, en lote. Nube con sus dos detectores. **Comprobar que `rotacion_malo` cae fuera y, corregido, dentro.** De fondo, `validar-motor estados` y su MCMC | `nucleo/api.cartera`, `nucleo/api.nube` | 1.000 análisis medidos en segundos; el arco rojo → verde sale |
| | 13:15 | 15 | Almuerzo | | |
| A-14 | 13:30 | 40 | `analizar` de inasistencias, con lo que dio `validar-motor jerarquico` a las 13:00 | Ruta de inasistencias | La tarjeta responde, con la red o con `mcmc` |
| A-15 | 14:10 | 40 | `analizar` de crédito, con lo que dio `validar-motor estados` a las 14:00 | Ruta de crédito | La tarjeta responde, con la red o con `mcmc` |
| A-16 | 14:50 | 40 | Las cifras: por motor, segundos del MCMC por dataset contra milisegundos de la red; la cartera en horas contra segundos; el método rápido de siempre (regresión logística simple) contra Krylov en el examen | Números en el estado | PC 3 tiene los pedidos de registro |
| A-17 | 15:30 | 30 | Tiempos de todo el recorrido. **16:00: tope.** Fijar `KRYLOV_MOTOR_<ID>` de cada motor y ayudar a PC 1 con `exportar_estatico` | Variables fijadas | Ningún paso del recorrido supera 2 segundos; cada tarjeta dice la verdad sobre quién responde |
| A-18 | 16:00 | 60 | Sellos finales y `limitaciones`. README técnico con los nombres precisos: modelo generativo, prior, posterior, NPE, flujo normalizador, SBC, MCMC; cómo se entrenó, cómo se validó, cómo reproducirlo | Sellos y texto | Cada corchete del guion que depende de PC 2 tiene su número o se declara sin número |
| | 17:00 | 60 | Colchón y arreglos | | |

Qué recibe: de PC 3, los archivos de datos y los casos, y su computador para dos entrenamientos. Qué entrega: a PC 1, las funciones de `nucleo/api.py`; a PC 3, los números.

**Lo que este calendario no garantiza.** Son cuatro motores en el tiempo en que antes cabía uno. Lo comprometido para las 18:00: los cuatro modelos generativos con su MCMC de referencia, y las redes de `espacial` y `supervivencia` validadas. `jerarquico` es probable y `estados` es el más difícil. Lo que no pase sale con su plan B y el guion lo dice.

### 6.4 PC 3 · seguimiento (monitoreo, guía, ajustes al plan y al pitch)

Dueño de `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md`, `DECISIONES.md` y este archivo. Skills: `ronda`, `punto-de-control`, `agregar-caso`, `registrar-cifra`, `ensayo-pitch`, `preparar-entrega`.

Su trabajo tiene dos partes. Una es la lista de abajo. La otra, que va primero cuando chocan, es la **ronda**: cada 30 a 45 minutos baja los cambios, verifica corriendo lo que los otros dicen haber terminado, escribe en el tablero la siguiente tarea de cada uno, ajusta el plan si algo se atrasó y pone al día el guion con lo que de verdad existe.

| Id | Cuándo | Min | Tarea | Entregable | Listo cuando |
|---|---|---|---|---|---|
| S-01 | 03:00 | 20 | Subir el plan al repositorio y comprobar que el push llega a los dos repositorios. Avisar para que los otros clonen | Commit en ambos | `git ls-remote` da el mismo identificador en los dos |
| S-02 | 03:20 | 5 | Mandar la consulta a la organización (`pitch/MENSAJES.md`) | Mensaje enviado | Enviado por una persona |
| S-03 | 03:25 | 20 | Caso de rotación (skill `agregar-caso`): 20% de las respuestas vacías al azar, con la verdad guardada aparte | `datos/demo/rotacion.csv` y `_verdad.csv` | Las dos clases siguen presentes en lo que queda |
| | 03:45 | 10 | **H0** | Tablero, tag | Hecho |
| S-04 | 03:55 | 20 | Caso del terreno. PC 2 lo necesita a primera hora. **Incluye bajar `meuse.grid`** (mismo paquete `sp`): la distancia al río en cada celda | `datos/demo/terreno.csv`, `terreno_grilla.csv` | 155 filas con `x`, `y`, `zinc`, `dist`; la grilla con `x`, `y`, `dist` |
| S-05 | 04:15 | 20 | Caso de crédito, con los seis meses de atrasos, saldos y pagos | `datos/demo/credito.csv` y `_verdad.csv` | Muestra de 2.000 filas con todas las columnas de `casos/credito.yaml` |
| S-05b | 04:55 | 20 | **Lanzar el entrenamiento de `supervivencia` en este computador:** `git pull`, `uv sync --group entrenar`, skill `entrenar-motor supervivencia`. Tapa abierta, enchufado | Proceso corriendo | Primer punto de guardado; el estado dice cómo retomar |
| | 05:15 | | **Duerme hasta las 08:15.** Deja al agente su lista nocturna | | |
| S-N1 | noche | | *Agente solo.* Script del caso de inasistencias, sin subir el CSV (licencia no comercial). **Muestra por pacientes completos dentro de 30 barrios**, nunca filas sueltas | `datos/preparar/inasistencias.py` | Corre en local; al menos un tercio de los pacientes tiene 2 o más citas |
| S-N2 | noche | | *Agente solo.* Abrir cada fuente de `pitch/CIFRAS.md` y anotar lo que dice la página. Borrador de `project-description.md` y de la estructura del README | Borradores | Una persona los revisa en la mañana |
| S-06 | 08:15 | 30 | Primera ronda del día: qué pasó en la noche en los tres computadores. Verificar corriendo | Tablero | Cada rol tiene su siguiente tarea |
| S-06b | 08:30 | 10 | **Subir el punto de guardado de `supervivencia` y lanzar `jerarquico` en este computador** (hasta las 11:30). A las 11:30, correr `validar-motor jerarquico` y su MCMC aquí mismo, y pasarle el resultado a PC 2 | Proceso corriendo; después, `sello.json` | `jerarquico` tiene veredicto antes de las 13:00 |
| | 08:45 | 15 | **H1** | Tablero, decisión, tag | Hecho |
| S-07 | 09:00 | 20 | Caso de inasistencias: revisar lo nocturno, columna de cliente | Caso completo | La tarjeta responde en local |
| S-08 | 09:20 | 15 | Archivo malo: rotación más una columna `fecha_salida` que solo tiene dato para quienes renunciaron (va en `columnas.extra`) | `datos/demo/rotacion_malo.csv` | PC 2 lo usa en A-13 |
| S-09 | 09:35 | 20 | Prueba del asistente genérico: el mismo archivo y la misma pregunta, tres veces. Anotar lo que pasó, sea cual sea | `pitch/VALIDACION.md`, cifra M-15 | Tabla llena |
| | 09:55 | 10 | Ronda | | |
| S-10 | 10:05 | 25 | Una persona abre las fuentes de las cifras que van al guion (N-01, K-11, J-01, D-01 a D-04) y firma la columna «Verificó». Mirar en el lugar qué sponsors hay | Columna llena | Ninguna cifra del guion queda sin persona |
| S-11 | 10:30 | 55 | Guion v1 en voz alta y cronometrado, con lo que A-08 y A-10 midieron. Textos de pantalla v1 para PC 1: titulares, rótulos, motivos del semáforo, preguntas de los deslizadores | `pitch/GUION.md`, textos | Las tres versiones calzan en su tiempo |
| | 11:25 | 10 | Ronda | | |
| S-12 | 11:35 | 35 | Esqueleto de láminas: texto de portada y cierre para PC 1; respaldo técnico y de negocio | Láminas | Lo construido y lo que es lámina se distinguen a simple vista |
| | 12:15 | 15 | **H2** | Tablero, decisión, tag | Hecho |
| S-13 | 12:30 | 30 | **Prueba 1 con tres extraños**, con el guion v1 y el demo a medias. Si hay alguien de Buk a mano, la pregunta de `MENSAJES.md` | `pitch/VALIDACION.md` | Tablas llenas |
| S-14 | 13:00 | 40 | Ajustes por la prueba: guion v2 y textos de pantalla definitivos. Lo que no se entendió en la pantalla va como pedido a PC 1 | Guion v2 | Entregado a PC 1 |
| | 13:40 | 30 | Almuerzo. Ronda al volver | | |
| S-15 | 14:20 | 40 | Láminas de respaldo completas, con los números que ya existen | Láminas 3 a 5 | Cada número tiene su fila en `CIFRAS.md` |
| | 15:00 | 20 | **H3:** alguien que no sea de PC 1 hace el recorrido de 4.3, dos veces, en la URL pública y sin internet | Tablero, tag | Hecho |
| S-16 | 15:20 | 60 | Entrega, primer borrador (skill `preparar-entrega`): archivo de proyecto, descripción, README. Decidir con el equipo qué hacer con la línea del README dirigida a modelos de lenguaje | Archivos de entrega | Una persona los leyó |
| | 16:20 | 10 | Ronda | | |
| S-17 | 16:30 | 30 | Guion v3 con todas las cifras medidas. Registrar las cifras finales con PC 2 | Guion sin corchetes, o con la frase sin número | Ningún corchete se dice con un número inventado |
| S-18 | 17:00 | 30 | Ensayo en borrador con quien presenta y con el producto real | Lista de arreglos | La lista llega a PC 1 antes de las 17:30 |
| | 17:30 | 30 | Con PC 1: sacar lo que no funcione. **18:00: tag `congelado`** | | |

Qué recibe: de PC 2, los números; de PC 1, la URL. Qué entrega: casos, datos, textos, la siguiente tarea de cada rol en cada ronda, las decisiones de cada hito y el pitch al día.

### 6.5 Hitos

Cada uno lo corre PC 3 con la skill `punto-de-control` y deja un tag en los dos repositorios para poder volver atrás.

**H0 · sábado 03:45 · ¿Podemos trabajar sin esperarnos?**
- Pasa si: los tres hicieron un commit que está en los dos repositorios; el contrato está congelado; la web muestra un ejemplo fijo.
- Si falla: nada más avanza hasta tener repositorio y contrato.
- También se decide aquí: si el espejo se hace público (lo necesita Vercel) y quién presenta.

**Antes de dormir · 05:15.** No es un hito formal, pero tienen que estar tres cosas: dos entrenamientos corriendo con su primer punto de guardado (`espacial` en PC 2, `supervivencia` en PC 3; si solo cabe uno, `espacial`); la URL pública mostrando el esqueleto; los datos de rotación y terreno en el repositorio. Si el despliegue no salió en 30 minutos, se deja para las 08:30 y no se trasnocha por eso.

**H1 · sábado 08:45 · ¿Sobrevivió la noche?**
- Pasa si: hay puntos de guardado de toda la noche en los dos computadores; la URL pública sigue viva; lo que hicieron los agentes está revisado por una persona.
- Si un entrenamiento se cayó: se retoma desde el último punto de guardado. Si `supervivencia` no sirve, se relanza en PC 3 con prioridad sobre `jerarquico`, y su H2 pasa a las 13:30.
- Si el agente no dejó el paso local ni el MCMC de `supervivencia` y `espacial`: PC 2 los hace primero y todo lo suyo se corre media hora.

**H2 · por motor · ¿Responde la red o el plan B?**

| Motor | Hora | Pasa si |
|---|---|---|
| `espacial` | 12:15 | La cabeza de mapa pasa `validar-motor`; el terreno se ve como mapa; `donde_medir` devuelve tres candidatas en menos de 2 segundos |
| `supervivencia` | 12:15 | Pasa `validar-motor`; la tarjeta de Buk responde con datos reales en la URL |
| `jerarquico` | 13:00 | Pasa `validar-motor` |
| `estados` | 14:00 | Pasa `validar-motor` |

- **Si un motor pasa:** `KRYLOV_MOTOR_<ID>=red`.
- **Si no pasa pero mejora:** sigue entrenando o se reentrena en el computador que esté libre, y se revalida. **Tope para todos: 16:00.**
- **Si no pasa:** `KRYLOV_MOTOR_<ID>=mcmc`. La tarjeta muestra el posterior del MCMC precalculado, rotulada «precalculado», en modo estático; los deslizadores siguen funcionando. El guion no dice que ahí responde la red.
- **Orden de corte**, del primero que cae al último, y qué se dice:

| # | Qué cae | Qué se ve | Qué se dice |
|---|---|---|---|
| 1 | Red de `estados` | Crédito, «precalculado» | «Este lo calculamos con el método lento de siempre; tardó [X] minutos. Es lo que Krylov está aprendiendo a hacer al instante» |
| 2 | Red de `jerarquico` | Inasistencias, «precalculado» | Lo mismo |
| 3 | Red de `supervivencia` | Rotación, «precalculado». La cartera muestra las [N] empresas que se alcanzaron a precalcular | No se dice la cifra de 1.000 ni «al instante» sobre rotación. La frase de amortización se dice solo sobre el terreno |
| 4 | Cabeza de flujo de `espacial` | «Qué manda en el terreno» sale del MCMC | No se dice que eso lo respondió la red |
| Nunca | Cabeza de mapa y «¿Dónde mido?» | | Si fallara, vale lo de abajo |

- Si la cabeza de mapa no pasa a las 16:00: el mapa y «¿Dónde mido?» salen precalculados con el método lento; el demo se ve igual, la interacción queda limitada a los pines precalculados y el guion cuenta las redes como lo que se entrenó, sin afirmar que responden.
- Si una tarjeta no tiene ni su MCMC a las 16:00, sale de `casos/INICIO`.
- Si falta la vista 4 o la cartera: van después de «¿Dónde mido?», que tiene prioridad sobre todo.

**H3 · sábado 15:00 · ¿Está el demo completo?**
- Pasa si: alguien que no sea de PC 1 hace el recorrido de la sección 4.3, dos veces seguidas, en la URL pública y con el wifi apagado en local, sin errores.
- Si pasa: las tres horas son para recibir las tarjetas que faltan, pulir y medir.
- Si no pasa: las tres horas son para que el recorrido salga. Las tarjetas que no estén se sacan del inicio.

**PRODUCTO TERMINADO · sábado 18:00.** Tag `congelado`. Lo que no funciona se saca de la pantalla. Desde aquí no entra ninguna función.

**Entrega · domingo 08:00.** Repositorio oficial con descripción, logo, README y URL pública. Tag `entrega`.

### 6.6 Sábado de 18:00 a 22:00: iterar el demo y el pitch

Lo que sí se puede cambiar: textos, orden de las tarjetas, tamaños de letra, valores por defecto de los deslizadores, el guion, las láminas. Lo que no: funciones, vistas, motores, reentrenar.

| Hora | Qué | Quién |
|---|---|---|
| 18:00 | Recorrido completo con cronómetro. Lista de todo lo que se ve mal | Los tres |
| 18:30 | Ensayo 1 con el computador y el cable de la presentación | Presenta quien vaya a presentar |
| 19:00 | Prueba 2 con tres extraños distintos | PC 3 |
| 19:30 | Arreglos de texto y orden según lo anterior | PC 1 y PC 3 |
| 20:00 | Charla de la organización «Cómo hacer un buen demo». Anotar la duración oficial del pitch | PC 3 y quien presenta. PC 1 y PC 2 siguen con arreglos y con el README |
| 20:45 | Ajustar el largo del guion a lo que dijeron | PC 3 |
| 21:00 | Ensayo 2, cronometrado, con las preguntas difíciles. Comer después | Los tres |
| 21:45 | Últimos arreglos. Último despliegue | PC 1 |
| 22:00 | Video de respaldo: la app en pantalla completa, narración encima | PC 1 y PC 3 |
| 22:00 | README técnico: cómo se entrenó, cómo se validó, cómo reproducir | PC 2 |
| 23:00 | Entrega revisada (skill `preparar-entrega`). Lista previa del domingo (skill `preparar-demo`) | PC 3 |
| 00:00 | A dormir los tres | |

Domingo: ensayo 06:30, ensayo 07:30, entrega 08:00, cierre de repositorios 08:30.

### 6.7 Sueño

| | Sábado madrugada | Domingo |
|---|---|---|
| PC 1 | 05:15 a 08:30 | 00:00 a 06:00 |
| PC 2 | 05:15 a 08:30 | 00:00 a 06:00 |
| PC 3 | 05:15 a 08:15 | 00:00 a 06:00 |

Son cerca de tres horas la primera noche. Terminar el producto a las 18:00 es lo que permite seis horas antes de presentar. Mientras las personas duermen, los agentes trabajan una lista corta y cerrada (`AGENTS.md`, «Trabajo sin humano»); el plan de la mañana no depende de que la terminen.

### 6.8 Qué esperamos tener medido a cada hora

| Hora | Número | Quién |
|---|---|---|
| Sáb 05:00 | `espacial` y `supervivencia`: datasets simulados por segundo y pasos de entrenamiento por segundo, en procesador y en la GPU del Mac | PC 2 |
| Sáb 08:30 | Presupuesto del paso local: milisegundos por análisis de rotación con 32 muestras | PC 2 (agente) |
| Sáb 09:15 | `espacial`: SBC y cobertura. MCMC de referencia de `espacial` y `supervivencia`: segundos por dataset | PC 2 |
| Sáb 10:15 | Rotación: personas en cada color, lo que cuesta no saber, qué pesa, examen con datos reales. `supervivencia`: SBC, cobertura, diferencia con el MCMC | PC 2 |
| Sáb 10:00 | Prueba del asistente genérico | PC 3 |
| Sáb 11:00 | Terreno: examen con mediciones escondidas y qué manda | PC 2 |
| Sáb 12:15 | «¿Dónde mido?»: análisis rehechos, segundos con la red, tiempo con el método lento. Medido sin nada entrenando | PC 2 |
| Sáb 13:00 | `jerarquico`: SBC, cobertura, MCMC. Extraños que repiten la idea, prueba 1 | PC 3 |
| Sáb 13:15 | Cartera: análisis y segundos. ¿El archivo malo cae fuera de la nube y, corregido, dentro? Tiempo de una tarjeta en la URL desde un teléfono | PC 2, PC 1 |
| Sáb 14:00 | `estados`: SBC, cobertura, MCMC | PC 2 |
| Sáb 15:30 | Por motor: segundos del MCMC contra milisegundos de la red; la cartera en horas contra segundos; el método rápido de siempre contra Krylov; examen en crédito e inasistencias | PC 2 |
| Sáb 19:30 | Extraños que repiten la idea, prueba 2 | PC 3 |

### 6.9 Riesgos que nos dejan sin demo

| Riesgo | Señal | Qué se hace |
|---|---|---|
| Un entrenamiento se cae o un Mac se duerme | H1 sin puntos de guardado recientes | Tapa abierta y `caffeinate` desde el inicio, en PC 2 y en PC 3. Se retoma del último punto. Decisión en el H2 de ese motor |
| Cuatro motores no caben en el tiempo de uno | H2 de cada motor | Cada motor tiene primero su MCMC precalculado. Orden de corte escrito en 6.5. Comprometido: `espacial` y `supervivencia` |
| `supervivencia` no alcanza a lanzarse a las 05:15 | A-B3 sin prueba de humo a las 04:55 | No se trasnocha: se lanza a las 08:30 y su H2 pasa a las 13:30 |
| La red del terreno empeora por la cabeza nueva | Prueba de A-03 | El gradiente de la cabeza de flujo no llega al codificador. Si los tres canales no pasan la prueba de humo, se lanza la red de dos canales |
| `estados` no pasa SBC | H2 de las 14:00 | Los estados van ordenados en el prior. Si aun así no pasa, sale precalculado |
| El paso local es lento | A-N2, de noche | Menos nodos de cuadratura; en la cartera, menos muestras |
| El archivo malo no cae fuera de la nube | A-13 | No depende de la red: lo detectan los dos ejes con nombre, por construcción |
| Una red no valida | Su H2 | Esa tarjeta sale con el MCMC precalculado, rotulada. El demo se ve igual; el guion cambia una frase por tarjeta |
| Un codificador no exporta a ONNX | A-01, A-03 y A-B2, antes de las 05:00 | Se sabe la primera noche. A ONNX va solo el codificador; el flujo se muestrea en NumPy. Si el pooling de atención no exporta, promedio con máscara |
| El terreno real no calza con el modelo | A-11 | La tendencia con el río ya está en el modelo: «manda el río» sale del análisis. Si el examen con mediciones escondidas falla igual, semáforo rojo y se dice |
| Vercel no despliega los commits de dos de los tres | P-02 | Espejo público (decisión de H0). Si no, solo despliegan los commits del dueño de la cuenta |
| El servidor gratuito no aguanta o duerme | Siempre | No importa: el recorrido completo está en modo estático |
| Un push llega a un repositorio y no al otro | `git ls-remote` distinto | Repetir `git push`. PC 3 lo comprueba en cada hito |
| PC 1 no alcanza las cuatro vistas | H2 | Orden de corte: cartera, panel del examen. Nunca el mapa ni «¿Dónde mido?» |
| El agente nocturno rompe algo | Mañana | Solo toca sus carpetas y hace commits chicos: se revierte el commit. El plan no dependía de eso |
| Una cifra del guion no llega | Ensayo de las 17:00 | La frase se dice sin número. Nunca se inventa |
| Se rompe algo después de las 18:00 | Ensayo | Se vuelve al tag `congelado` |

## 7. Cómo se coordinan los tres computadores

### 7.1 El contrato

Está en `contratos/CONTRATO.md` y se congela en H0. Cuatro piezas:

1. **Funciones de `nucleo/api.py`.** PC 2 las escribe; PC 1 las envuelve en rutas. Devuelven diccionarios con la misma forma que los ejemplos fijos, con los que la web funciona desde el primer minuto.
2. **Decisión.** La regla de los colores y de «lo que cuesta no saber», escrita una vez y probada en Python y en TypeScript con el mismo archivo.
3. **Modo estático.** Toda respuesta del recorrido existe como archivo junto a la web.
4. **Caso.** Un archivo por caso en `casos/`: la tarjeta, la pregunta, el motor, las columnas, los costos con los extremos de sus deslizadores, el archivo de datos y de dónde viene.

### 7.2 Sincronización

- Una sola rama, `main`. Cada uno escribe solo en sus carpetas, así no hay conflictos.
- `git pull --rebase` antes de cada push. Commits chicos y seguidos.
- **Dos repositorios espejo, un solo push.** `origin` hace `pull` del repositorio de la organización y empuja a ese y a `Silent-math/krylov`. Los comandos están en cada `PC*.md`.
- Cada uno mantiene su archivo en `estado/`. PC 3 mantiene `estado/TABLERO.md`, que trae la siguiente tarea de cada rol.
- Bloqueo de más de 20 minutos: se anota, se toma el camino alternativo y se sigue.
- Un tag por hito.

Cada computador declara su rol en un archivo local `CLAUDE.local.md` que no se sube y que importa su `PC*.md`. `CLAUDE.md` importa `AGENTS.md`, `GLOSARIO.md` y el tablero. `SKILLS.md` es el índice para humanos; lo que Claude Code ejecuta está en `.claude/skills/`.

### 7.3 El repositorio es público

Todo lo que se sube lo puede leer un juez, un rival o la revisión automatizada. Se sube el plan completo, porque tres computadores lo necesitan y porque mostrar cómo se decidió suma en «aspecto técnico». No se suben: claves, el CSV de inasistencias (licencia no comercial), nombres de personas sin su permiso, ni comentarios sobre otros equipos.

## 8. Qué existe y qué es lámina

| El sábado a las 18:00 existirá | Será lámina |
|---|---|
| App desplegada con las cuatro vistas, también sin servidor | Series de tiempo, eventos raros, segmentación |
| Cuatro modelos generativos escritos, cada uno con su simulador y su MCMC de referencia | Integración real con una plataforma |
| Motor `espacial`: red entrenada con terrenos simulados, validada, con su sello. «¿Dónde mido?» y la medición simulada | Clientes, pilotos, precios validados |
| Motor `supervivencia`: red entrenada con empresas simuladas, validada, con su sello (o MCMC precalculado y rotulado, si no pasó) | Terrenos en tres dimensiones |
| Motores `jerarquico` y `estados`: red validada si pasó su H2; si no, MCMC precalculado y rotulado. **Se dice cuál de las dos** | Subir un archivo cualquiera |
| Cuatro tarjetas con datos públicos: tres reales y una ficticia, con examen sobre datos reales reservados | Datos de cualquier sponsor |
| Cartera con 1.000 empresas simuladas, rotuladas (o las precalculadas, si `supervivencia` no pasó) | |

## 9. Respuesta a la crítica v3

> Esta sección es historia: se escribió antes de D-26. Donde dice que `regresion` no lleva red, que la red del terreno devuelve solo el mapa o que los parámetros son opcionales, vale D-26 y la sección 11.

La crítica tiene cinco puntos de fondo y veinte errores concretos. Se atienden todos; en tres se hizo algo distinto de lo que propone, y se explica por qué.

### 9.1 Los cinco de fondo

| # | Crítica | Qué se hace | Quién · cuándo |
|---|---|---|---|
| 1 | La simulación no se ve y el caso estrella no necesita la red | Show nuevo (4.2). La simulación aparece cuatro veces (1.4). El momento estrella es «¿Dónde mido?», que sin la red toma minutos. Lo que se corta primero es la cartera | Todos · D-16 |
| 2 | Los colores dicen algo falso («se va, seguro · 22%») | Los colores pasan a ser decisiones: `actuar`, `no_actuar`, `en_duda`. Rótulos nuevos en cada caso. Guion corregido | Contrato sección 3 · hecho |
| 3 | «Plata en duda» no mide la duda | Reemplazada por «lo que te cuesta no saber», con la fórmula que propone la crítica. Vale cero donde no hay duda | Contrato sección 3 · PC 2, A-07 |
| 4 | «Minutos contra segundos» no sale con las mediciones propias | Esa comparación desaparece. La nueva es rehacer cientos de análisis para «¿Dónde mido?», más la exactitud del método rápido. Las tres cifras se miden y la frase dice qué se comparó | PC 2 · A-11, A-14 |
| 5 | La noche de cómputo se gasta en la red equivocada | No hay red de `regresion`. La noche es para la red del terreno, sobre grilla fija con canal de máscara, lanzada antes de dormir. Tapa abierta | PC 2 · A-02 a A-04 |

### 9.2 Los errores concretos

| # | Crítica | Qué se hace | Quién · cuándo |
|---|---|---|---|
| 6 | S-03 deja una sola clase y rompe la tarjeta de Buk | Se vacía un 20% al azar, sin mirar la respuesta, y la verdad se guarda aparte. Escrito en el contrato y en la skill | PC 3 · S-03 |
| 7 | ¿Quién eligió las columnas y los costos? | Costos en deslizadores, en vivo. Columnas propuestas por Claude para un archivo propio, y los casos del demo pasan por la misma propuesta; la pantalla solo dice «Krylov eligió» si es cierto | PC 1 · P-N1, P-12 |
| 8 | La palabra «senior» invita a pinchar | Sale de la frase y de todo el material | Hecho |
| 9 | La cartera son mil empresas iguales | Las mil empresas salen del simulador, con efectos, tasas y tamaños distintos, rotuladas. El caso de citas usa los 81 barrios reales | PC 2 · A-12 |
| 10 | El sello se mide en sus propias simulaciones | En voz alta se dice el examen con datos reales reservados. Lo de simulaciones va en la lámina técnica | PC 2 · A-08, A-10, A-14 |
| 11 | El guion afirma resultados sin medir | Regla 2 de `AGENTS.md`: los resultados van entre corchetes hasta que el motor los da. Dato de la verificación: en ese archivo la distancia sí se asocia, débilmente, con renunciar | PC 3 · cada ronda |
| 12 | La prueba pública de 2024 está vieja | Sale. Entra una prueba propia con un asistente genérico, sin nombrar a nadie como el malo | PC 3 · S-09 |
| 13 | El análisis a mano con cronómetro juega en contra | Cortado | D-17 |
| 14 | El servidor gratuito no aguanta el QR | Modo estático: todo el recorrido precalculado junto a la web. Red servida con `onnxruntime`. Cálculo en vivo solo en el escenario | PC 1 · P-01, P-11 |
| 15 | Revisen la lista de sponsors | Verificado en la web: son once, AgendaPro, Lici y Copec incluidos; Cognition no está. Se confirma en el lugar | PC 3 · S-10 |
| 16 | Faltan datos del formato | Encontrados: criterios con sus pesos, horario, premios generales, exigencia de demo funcional. Falta la duración del pitch: consulta más corta y charla de las 20:00 | PC 3 · S-02 |
| 17 | La prueba con extraños llega tarde | Dos pruebas: 12:30, cuando todavía se puede cambiar el producto, y 19:00 | PC 3 · S-13 |
| 18 | Colores inconsistentes entre motores | Una sola regla para los dos: en duda si hay más de 10% de probabilidad de que la decisión cambie al saber más. Usa el punto de corte de los costos en ambos | Contrato sección 3 |
| 19 | El terreno real puede dar rojo | Se prueba a las 10:00. Si pasa, se cuenta | PC 2 · A-10 |
| 20 | El umbral de 720 mg/kg puede tener fuente | Tiene: es el valor de intervención holandés para suelo estándar. Deja de ser un supuesto | Cifra K-11 |
| 21 | Buk es el anfitrión: pregúntenle a alguien | Sí, pero sin salir a buscar y sin que el plan dependa de eso: una pregunta de cinco minutos si hay alguien a mano en la prueba de las 12:30 | PC 3 · S-13 |
| 22 | La meta de US$ 1,5 millones se ve ingenua | Sale. Queda la unidad | Sección 3 |
| 23 | La voz quita tiempo | Cortada | D-17 |
| 24 | Cortar el motor de eventos raros, la pregunta libre, WhatsApp y tres tarjetas sintéticas | Cortados. Quedan cuatro tarjetas | D-17 |
| 25 | La frase | Se adopta la propuesta, con el nombre nuevo | Sección 0 |

### 9.3 Dónde no se hizo lo que la crítica propone

| Tema | La crítica propone | Lo que se hace | Por qué |
|---|---|---|---|
| Qué devuelve la red | Los cuatro parámetros del terreno con un flujo, y después un cálculo exacto por cada versión | El mapa completo, directo: valor esperado y margen por bloque. Los parámetros quedan como opcional | La propia crítica avisa que ese cálculo por versión es el cuello de botella de «¿Dónde mido?». Con el mapa directo, 500 análisis son una pasada de 500 grillas. Y una red convolucional con una pérdida simple es más segura de entrenar en una noche que un flujo |
| Contactar a Buk | Quince minutos con alguien de Buk | Cinco minutos, solo si está a mano | El equipo decidió antes que el plan no depende de contactar a nadie (D-08). Se respeta, aprovechando la oportunidad si aparece |
| Horario de PC 2 | Regresión exacta a las 02:00, simulador a las 03:00 | Primero el simulador y la red; la regresión exacta la hace el agente de noche | El plan llega a las 03:00. Lo que necesita horas de cómputo va primero; lo que es solo escribir código puede hacerlo un agente mientras la persona duerme |

### 9.4 Lo que la crítica no vio y este plan agrega

- **Los criterios oficiales del jurado.** Un cuarto de la nota es técnico y puede apoyarse en una revisión automatizada del código. El negocio no puntúa. El guion y el README se armaron contra esos cinco criterios.
- **El atajo del método exacto.** En este modelo se puede calcular «¿Dónde mido?» con el método exacto sin rehacer cada análisis desde cero. Un juez que sepa del tema lo va a decir. La respuesta está en la sección 5 y la comparación se enuncia con precisión: «rehacer cada análisis completo».
- **Vercel y los commits de otros autores.** En el plan gratuito no despliega commits de quien no es dueño de la cuenta si el repositorio es privado. El espejo hoy es privado.
- **El repositorio es público** y el archivo de inasistencias tiene licencia no comercial.
- **«PC-1» se confundía con «PC 1».** Los puntos de control ahora son hitos.
- **El Python del sistema es 3.15** y la biblioteca que sirve la red no existe para esa versión. Se fija 3.12.

## 10. Avisos

- **El `README.md` que venía en el repositorio trae una línea dirigida a modelos de lenguaje** (pide insertar un emoji de plátano después de cada palabra). Los agentes no la siguen por su cuenta. Qué hacer con ella lo decide una persona del equipo en S-16.
- **El archivo de inasistencias tiene licencia CC BY-NC-SA 4.0.** No se sube. El caso vive en local y en las respuestas precalculadas, con atribución.
- **El archivo de rotación es ficticio**, creado por IBM. Se rotula «datos públicos de ejemplo, ficticios».
- **Las cifras de Buk no calzan entre sí:** una página dice más de 10.000 clientes y otra más de 6.000 empresas. Se dice «miles».
- **Los costos de cada caso** son supuestos del demo. Definen la plata que se ve. Van en deslizadores y se dicen como supuestos.
- **El umbral del terreno** aplica a suelo estándar; para otros suelos se corrige. Si preguntan, se dice.
- **Los agentes de investigación leyeron las fuentes hoy**, pero antes de que una cifra vaya a una lámina la abre una persona (S-10).

## 11. Anexo técnico

Reescrito por la decisión D-26. Aquí se usan los nombres técnicos precisos; la pantalla y el pitch siguen usando `GLOSARIO.md`.

### 11.1 La tesis

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**. Cada motor tiene cuatro piezas:

1. Un **modelo bayesiano generativo** explícito del dataset completo: prior sobre los parámetros globales θ → efectos por grupo → latentes por unidad → datos observados, incluidas la censura, las respuestas faltantes y cómo se generan las covariables.
2. Un **simulador vectorizado** de ese modelo, que genera datasets completos al vuelo, con n variable dentro del rango del caso.
3. Una **red que invierte el modelo** (estimación neuronal del posterior, NPE): recibe un dataset entero y entrega q(θ | D). Se entrena solo con simulaciones del modelo.
4. **Respuestas en milisegundos** para cualquier dataset nuevo de la misma familia: el archivo del demo o cada una de las 1.000 empresas de la cartera.

Los cuatro modelos son de los que hoy exigen un especialista con MCMC. La regresión logística simple queda solo como «el método rápido de siempre»: la comparación que muestra qué se pierde sin el modelo completo.

Todos los priors de abajo son puntos de partida. Antes de lanzar un entrenamiento se mira el predictivo a priori contra el archivo real (tasas, rangos) y se ajusta; lo que quede va en `config.json`.

### 11.2 `supervivencia` (rotación)

Datos por persona i: efectos x_i (horas extra, distancia, empresas previas; estandarizados), w_i = log del sueldo estandarizado, cargo g(i), cuatro encuestas ordinales y_ij ∈ {1..4}, años en la empresa t_i (entero) y evento δ_i (renunció o sigue).

```
Globales θ (32):
  k ~ LogNormal(0, 0.5)                    forma del riesgo base Weibull
  β0 ~ Normal(-2.5, 1)                     nivel del riesgo
  β ~ Normal(0, 0.5), 3 efectos
  γ: 6 coeficientes de un B-spline cúbico en w; γ_1 ~ Normal(0, 1),
     γ_m − γ_{m−1} ~ Normal(0, τ),  τ ~ HalfNormal(0.5)     (prior de suavidad)
  σ_u ~ HalfNormal(0.5)                    dispersión entre cargos
  λ ~ Normal(0, 0.7)                       cuánto baja el riesgo con el compromiso
  a_j ~ LogNormal(0, 0.5), c_j1 < c_j2 < c_j3 ~ Normal(0, 1.5) ordenados, j = 1..4   (ítems)
  μ_c ~ Normal(log 6, 0.5), s_c ~ HalfNormal(1)             (censura)
Grupo:    u_g ~ Normal(0, σ_u)             un efecto por cargo
Latente:  z_i ~ Normal(0, 1)               compromiso de la persona
Encuestas:  P(y_ij ≤ m) = logistic(c_jm − a_j z_i)          (logit ordenado)
Evento:     T_i ~ Weibull:  S(t) = exp(−exp(η_i) t^k),  η_i = β0 + x_i·β + s(w_i) + u_g(i) − λ z_i
Censura:    C_i ~ LogNormal(μ_c, s_c)      tiempo desde el ingreso hasta la foto
Observado:  t_i = ⌊min(T_i, C_i)⌋,  δ_i = 1[T_i ≤ C_i];  δ_i se borra en el 20% por decidir
```

- **Ajustes que impusieron los datos.** `Department` tiene 3 niveles: el grupo es `JobRole` (9). Hay 44 personas con 0 años: el tiempo se trata por intervalos de un año. El examen esconde δ, y P(δ = 1 | t, …) solo existe si la censura tiene modelo propio; por eso C está en el modelo.
- **Verosimilitud por intervalos** (la usan el paso local y el MCMC; el simulador es exacto): δ = 1: [S_T(t) − S_T(t+1)] · S_C(t+½). δ = 0: S_T(t+½) · [S_C(t) − S_C(t+1)].
- **Lo que se decide:** p_i = P(δ_i = 1 | t_i, x_i, y_i, datos del cargo, θ), para las personas con δ vacío.
- **Rangos del simulador:** n entre 200 y 2.000; de 3 a 12 cargos.
- **Por qué el MCMC es lento:** un latente por persona (hasta 2.000) más los efectos por cargo, con geometría de embudo.

### 11.3 `jerarquico` (inasistencias)

Datos por cita c del paciente i en el barrio b: días de espera, día de la semana, SMS, efectos x_c (edad, beca, hipertensión, diabetes, alcoholismo) y la respuesta (no llegó).

```
Globales θ (22):
  α ~ Normal(-1.5, 1)
  f: B-spline cúbico de 6 coeficientes en log(1 + espera), con prior de suavidad (como en 11.2)
  κ ~ Normal(-1.5, 1)                      salto de «mismo día»
  d: 4 efectos del día de la semana (lunes de base) ~ Normal(0, 0.3)
  ρ0 ~ Normal(0, 0.5), ρ1 ~ Normal(0, 0.3) efecto del SMS y cómo cambia con la espera
  β ~ Normal(0, 0.5), 5 efectos
  σ_v ~ HalfNormal(1), σ_b ~ HalfNormal(0.5)
Grupo:    u_b ~ Normal(0, σ_b)             un efecto por barrio
Latente:  v_i ~ Normal(0, σ_v)             propensión del paciente, común a todas sus citas
Respuesta:  logit P(no llega) = α + f(espera) + κ·1[mismo día] + d_día
                                + (ρ0 + ρ1·log(1 + espera))·SMS + x_c·β + v_i + u_b
```

- **Ajustes que impusieron los datos.** 35% de las citas son del mismo día, con 4,6% de inasistencia: por eso el salto κ. Ninguna cita del mismo día recibe SMS: el simulador **modela la asignación** (SMS solo con 3 o más días de espera, con probabilidad al azar). Solo 39% de los pacientes tiene 2 o más citas: el simulador genera citas por paciente con una geométrica. Los sábados (39 citas) y las esperas negativas (5) se descartan.
- **Muestra:** pacientes completos dentro de barrios elegidos (`casos/inasistencias.yaml`). Nunca filas sueltas.
- **Rangos del simulador:** de 1.000 a 3.000 citas; de 10 a 40 barrios.
- **Por qué el MCMC es lento:** dos niveles de efectos aleatorios, con cerca de mil latentes de paciente poco informados.

### 11.4 `estados` (crédito)

Datos por cliente i: seis meses de atraso (ordinal de 6 niveles: −2, −1, 0, 1, 2, 3 o más), uso del cupo (saldo / cupo, recortado a [−0,2; 1,5]) y pago (cero, o log(pago / cupo)); covariables x_i (cupo, edad, educación); y el impago del mes siguiente.

```
Estados ocultos: 1 al día, 2 apretado, 3 en problemas.
Globales θ (35):
  π ~ Dirichlet(4, 2, 1)                   estado del primer mes
  A_jk ~ Normal(-2, 1) para j ≠ k, A_jj = 0          (6 libres)
  ψ ~ Normal(0, 0.5), 3 covariables
  Transición: P(s_{t+1} = k | s_t = j, x_i) = softmax_k( A_jk + (k − j)·x_i·ψ )
  Atraso:  logit ordenado con posición m_k (m_1 = 0 < m_2 < m_3) y 5 cortes
  Uso:     Normal(μu_k, σu_k), con μu_1 < μu_2 < μu_3 no impuesto
  Pago:    cero con probabilidad q_k; si no, Normal(μp_k, σp)
  Impago:  Bernoulli(d_k) según el estado del mes 7, con  d_1 < d_2 < d_3
Latente:  la cadena s_i1 … s_i7 de cada cliente
```

- **Identificación.** El intercambio de estados se rompe **en el prior**: logit d_1 ~ Normal(−2.5, 1) y los incrementos hacia d_2 y d_3 son positivos (LogNormal). Sin eso, ni NUTS ni el flujo pasan SBC.
- **Lo que se decide:** p_i = Σ_k P(s_i7 = k | historial, θ) · d_k, con el filtro forward.
- **Rangos del simulador:** de 500 a 2.000 clientes.
- **Por qué el MCMC es lento:** la verosimilitud es un filtro forward por cliente dentro de cada paso de NUTS, con 35 parámetros correlacionados.

### 11.5 `espacial` (terreno)

```
Globales θ (7): alcance a, dirección φ, razón de anisotropía r, varianza σ², ruido de medición τ²,
                y la tendencia β0, β1.
Campo:     y(s) = β0 + β1·√dist(s) + w(s),   w ~ proceso gaussiano de media 0 y covarianza
           σ²·exp(−h), con h la distancia anisotrópica (a, φ, r)
Medición:  z_j = y(s_j) + ε_j,  ε_j ~ Normal(0, τ²),  en 30 a 400 lugares, al azar o agrupados
```

- **La distancia al río** es `dist` del archivo, y se necesita en cada bloque: la trae `datos/demo/terreno_grilla.csv` (de `meuse.grid`, tarea S-04).
- **Simulador.** El campo w sale con transformada de Fourier sobre una grilla del doble de tamaño, recortada; una prueba lo compara con el método directo. **El río es simple:** una curva suave al azar que cruza la grilla (un polinomio cúbico por tres o cuatro puntos al azar) y su campo de distancia, normalizado entre 0 y 1. En 20% de los terrenos no hay tendencia (β1 = 0 y canal en cero), para cubrir archivos sin esa columna.
- **Red.** Entra la grilla de 32×32 con tres canales: valor estandarizado, marca de medición y √dist. Una red convolucional con saltos hace de codificador. Dos cabezas:
  - **Cabeza de mapa:** media y margen de y en cada bloque, con verosimilitud gaussiana del valor verdadero. Es el predictivo posterior marginal, amortizado. **Entrena exactamente igual que si estuviera sola.**
  - **Cabeza de flujo:** q(θ | D) con NPE. **Recibe el resumen con el gradiente cortado** (`detach`), así no puede perjudicar a la cabeza de mapa; si hace falta, se entrena aparte de día sobre el codificador congelado.
- **Salvavidas (04:45).** Si la red de tres canales no pasa la prueba de humo, se lanza la de dos canales del plan anterior (sin tendencia), y la tendencia sale del flujo de día o del MCMC.
- **«Qué manda en el terreno»** sale del posterior: qué parte de la variación explican el río, la continuidad entre vecinos y el ruido. Va en `factores`.
- **Preprocesamiento.** Transformación del valor si el caso la pide (logaritmo para el zinc); una sola escala para los dos ejes; promedio de los puntos que caen en el mismo bloque; estandarización con el promedio y la dispersión de lo medido. El umbral pasa por la misma transformación. Es la misma función en el simulador y en el servicio.
- **MCMC de referencia.** NUTS sobre θ con la verosimilitud marginal del proceso gaussiano; el mapa, por kriging dado cada muestra de θ. **Con 155 puntos tarda segundos, no minutos:** la cifra de amortización del terreno no es un análisis, son los cerca de 480 análisis rehechos de «¿Dónde mido?».
- **«¿Dónde mido?».** Candidatos: bloques en duda sin medición, hasta unos 40, repartidos. Para cada uno, unos 12 resultados posibles tomados del rango que la cabeza de mapa da para ese bloque. Son cerca de 480 grillas en un lote. Para cada una se recalcula lo que cuesta no saber; el valor de medir en un lugar es cuánto baja en promedio. Se entregan las tres mejores, descontado el costo de medir.

### 11.6 Arquitectura común (`motor/comun/`)

- **Codificador del dataset.** Invariante al orden de las filas y con n variable: DeepSets con pooling de atención y máscara de relleno. Jerárquico cuando el modelo lo es: filas → grupo (cargo, o paciente → barrio) → dataset. En `estados`, cada fila es el historial aplanado del cliente. Las filas por decidir entran con la respuesta en cero y una marca. En `espacial`, la red convolucional cumple ese papel. Salida: un resumen s(D) de 128 números.
- **Posterior global.** Flujo normalizador condicional con **capas de acoplamiento afines** (8 capas, permutación fija entre capas), sobre θ llevado a espacio sin restricciones (logaritmos, logits, incrementos positivos). Pérdida NPE: −log q(θ | s(D)), promediada sobre simulaciones. Con `zuko` si su flujo de acoplamiento calza; si no, las 60 líneas propias.
- **Exportación.** A ONNX va solo el codificador (ejes dinámicos para n). El flujo se guarda en `flujo.npz` y **se muestrea en NumPy** (`nucleo/flujo.py`): el acoplamiento afín son productos de matrices. Prueba obligatoria, igual a la del preprocesamiento: con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra con tolerancia de `float32`.
- **Lo local, exacto y en NumPy.** Dado cada θ muestreado, el efecto del grupo y el latente de cada unidad son de una dimensión cada uno: se integran con **cuadratura de Gauss-Hermite anidada** (grupo → unidad), vectorizada por grupo. En `estados`, filtro forward. Por eso θ tiene tamaño fijo aunque cambie el número de cargos o de barrios, la red hace solo lo caro y `nucleo/` sigue sin `torch`.
- **Presupuesto de la cuadratura.** Por análisis son 32 muestras × unidades × nodos². Un análisis tiene que tardar menos de 1 segundo y la cartera de 1.000 empresas, segundos. Se mide la primera noche. Si no alcanza: 15 nodos (o menos), y para la cartera 8 muestras.
- **Hacia el contrato.** 32 muestras del posterior → `muestras_p` por unidad y `factores` con su certeza. La forma de `analizar` no cambia.
- **Covariables.** El simulador genera las X con una mezcla, mitad y mitad: (a) remuestreo de filas reales del archivo del caso, con perturbaciones; (b) un generador paramétrico (cópula gaussiana con correlaciones y marginales al azar). **Límite declarado:** la red generaliza a empresas cuyas covariables caen dentro de lo que cubre (b); la cartera sale de (b), y el segundo detector de la nube avisa cuando un archivo cae fuera.

### 11.7 Entrenamiento

- PyTorch en `float32`; procesador o GPU del Mac según `medir-rendimiento`, **por motor**. Datasets simulados al vuelo; se cuenta cada uno. Puntos de guardado cada 10 minutos. Python 3.12 con `uv`.
- **Lo mínimo para lanzar un entrenamiento:** simulador, codificador, flujo, pérdida, puntos de guardado y una prueba de humo con un SBC chico (200 datasets). La cuadratura local, el MCMC y la integración con `api.py` **no bloquean el lanzamiento**.
- Un entrenamiento por computador. Calendario y presupuesto: sección 6.3.

### 11.8 Validación: un sello por motor

1. **Calibración en simulaciones nuevas.** SBC (los rangos del valor verdadero entre las muestras del posterior deben ser uniformes) y cobertura (el intervalo de 90% contiene al valor verdadero cerca del 90% de las veces), también por grupos: n chico y n grande, pocos y muchos grupos.
2. **Comparación con el MCMC de referencia.** NumPyro con NUTS, solo dentro de `motor/`. **De 5 a 10 datasets simulados por motor, más el real.** Tienen que dar las mismas medias y rangos, y se mide el tiempo de cada uno: esa es la cifra de amortización. Corre en un computador que no esté entrenando, nunca encima de un entrenamiento.
3. **Examen con datos reales reservados.** Ya está en el contrato. Es lo que se dice en voz alta.
4. **Modelo mal especificado.** La nube de 11.9: `rotacion_malo` tiene que caer fuera y, corregido, dentro.

Un motor **pasa** si: SBC sin sesgo visible, cobertura de 90% entre 85% y 95% (y sobre 80% en el peor grupo), y diferencia con el MCMC bajo 0,3 desviaciones estándar del posterior en las medias. Los umbrales se pueden ajustar con una entrada en `DECISIONES.md`, nunca en silencio.

### 11.9 La nube

- Las simulaciones son el **predictivo a priori** del modelo del motor, con el n del archivo.
- **Lo que se dibuja: dos ejes con nombre.** De cada dataset simulado y del archivo: qué tan bien adivina la respuesta el mejor factor por sí solo (incluidas las columnas `extra`), y la proporción de «sí». Una columna que delata la respuesta cae en el borde derecho, fuera de todo lo simulado, por construcción.
- **Segundo detector, sin dibujo:** distancia de Mahalanobis del archivo en el espacio de resúmenes s(D), contra el percentil 99 de las simulaciones. Un resumen aprendido no garantiza que un archivo raro caiga fuera (el codificador puede mandar algo que nunca vio a cualquier parte), por eso no es el que sostiene el momento 3.
- `rojo_modelo` si cualquiera de los dos marca. `fecha_salida` no entra al codificador.

### 11.10 Decisión y servicio

- **Decisión.** `contratos/CONTRATO.md`, sección 3.
- **Servicio.** El codificador corre con `onnxruntime`; el flujo y lo local, en NumPy. `nucleo/` y `servicio/` no importan `torch`, `zuko`, `jax` ni `numpyro`.
- **Plan B por motor.** Implementación `mcmc`: el posterior del MCMC precalculado, leído por `nucleo/` y pasado por el mismo paso local. Sale rotulado «precalculado».

## 12. Fuentes

Consultadas el 21 de noviembre de 2026 por agentes de investigación. Antes de usar una cifra en una lámina, una persona abre la fuente y firma en `pitch/CIFRAS.md` (tarea S-10).

El evento
- Programa y sponsors de Santiago. https://hack.platan.us/26-cl
- Bases: criterios, premios, exigencia de demo. https://hack.platan.us/26-cl/bases
- Cómo se ve la página de votación de un proyecto (otra sede). https://hack.platan.us/26-ar/vote
- Proyectos del track Simulaciones en otra sede. https://hack.platan.us/26-co/vote
- Primera edición, pitch de tres minutos. https://www.df.cl/df-mas/punto-de-partida/36-horas-de-programacion-nonstop-asi-fue-la-primera-platanus-hack

El nombre
- Aleksey Krylov. https://en.wikipedia.org/wiki/Aleksey_Krylov · https://ru.wikipedia.org/wiki/Крылов,_Алексей_Николаевич
- Biografía de divulgación, capítulo de las tablas. http://www.plam.ru/hist/akademik_korabelnoi_nauki/p16.php
- MacTutor. https://mathshistory.st-andrews.ac.uk/Biographies/Krylov_Aleksei/

Datos para los casos (hay copias crudas en `datos_crudos/`, fuera del repositorio, en el computador donde se generó este plan)
- Rotación, ficticio de IBM, 1.470 filas, licencia ODbL. https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset
- Crédito, 30.000 clientes, CC BY 4.0. https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- Inasistencias, 110.527 citas, CC BY-NC-SA 4.0. https://www.kaggle.com/datasets/joniarroba/noshowappointments
- Terreno, 155 muestras, paquete `sp` de R, GPL (>= 2). https://rdrr.io/cran/sp/man/meuse.html · copia en CSV: https://raw.githubusercontent.com/filipkral/meuse/master/meuse.txt
- Valor de intervención holandés para zinc, 720 mg/kg. Circular de remediación de suelos 2013, anexo 1 (copia). https://enviroeng.eu/wp-content/uploads/2022/01/LISTA-HOLANDESA-2013.pdf

Herramientas (detalle y versiones en `STACK.md`, sección 5)
- Render, plan gratuito. https://render.com/docs/free · https://render.com/docs/python-version
- Vercel, límites y repositorios. https://vercel.com/docs/limits · https://vercel.com/docs/git · https://vercel.com/docs/deployments/troubleshoot-project-collaboration
- PyTorch en la GPU del Mac y exportación a ONNX. https://docs.pytorch.org/docs/2.15/notes/mps.html · https://docs.pytorch.org/docs/2.15/onnx.html
- Claude Code: instrucciones de proyecto y skills. https://code.claude.com/docs/en/memory.md · https://code.claude.com/docs/en/skills.md

Negocio (solo lámina de respaldo)
- Buk. https://buk.mx/ · https://www.buk.cl/quienes-somos/buk-mejores-softwares-rh
- AgendaPro, 22.000 negocios. https://www.descubre.vc/noticia/agendapro-alcanza-50-millones-de-reservas-y-lanza-marketplace-regional-2026-08-20
- SAP y Prior Labs, anuncio del 4 de mayo de 2026. https://news.sap.com/2026/05/sap-to-acquire-prior-labs-establish-frontier-ai-lab-europe/
- Empresas activas en Chile, INE. https://www.ine.gob.cl/docs/default-source/estadisticas-experimentales-rue/rue-demografia-de-empresas.html
