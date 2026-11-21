# Modelos candidatos: qué podría amortizar Krylov después

> Material de apoyo para la lámina 7 del deck («hoja de ruta») y para la pregunta «¿y después qué?». **Nada de esto está construido ni se va a construir en la hackathon.** Este archivo usa nombres técnicos; en pantalla y en voz alta se usa `GLOSARIO.md`.

La idea que se vende es una sola: un modelo estadístico difícil, de los que hoy exigen un especialista y minutos u horas de cómputo por análisis, **se entrena una vez con casos simulados y después responde en un paso**, con su rango, con lo que cuesta no saber y con dónde conviene medir. Cada modelo de esta lista es un motor más: un modelo generativo, su simulador, una red y su método lento de referencia.

## Con qué vara se estiman las horas

Las horas de abajo son **estimaciones nuestras, no medidas**. La unidad es una persona con Claude Code y un MacBook Air, como en esta hackathon. Lo único medido que tenemos para calibrarlas:

| Medido | Valor | Cifra |
|---|---|---|
| Entrenamiento del motor del terreno, que pasó su sello | 280 minutos, 7.750.592 terrenos simulados, MacBook Air M4 | M-01, M-02 |
| Entrenamiento del motor de rotación, que **no** pasó su sello | 267,5 minutos, 12.739.616 empresas simuladas, MacBook Air M3 | M-21, M-23, M-28 |
| Un análisis del terreno con el método lento (MCMC) | 117 segundos | M-25 |
| Horas de construcción del motor del terreno | No se midieron | M-19, pendiente |

La segunda fila es la que manda: **una noche de entrenamiento no garantiza un motor validado.** Un modelo con 7 parámetros pasó; uno con 32 no. Por eso cada estimación trae aparte las horas de validar, y por eso el riesgo de cada candidato importa más que su total.

Sobre los datos públicos: son los conjuntos que conocemos para cada problema. **Nadie los abrió hoy.** Antes de nombrar uno en una lámina hay que abrirlo, leer su licencia y registrarlo en `pitch/CIFRAS.md`.

## Resumen

| # | Modelo | La pregunta | Construir | Entrenar | Validar | Total | Reúsa |
|---|---|---|---|---|---|---|---|
| 1 | Geoestadística minera en 3D | ¿Dónde perforo el próximo sondaje? | 12 a 16 h | 8 a 10 h | 4 a 6 h | 24 a 32 h | `espacial` casi entero |
| 2 | Confiabilidad de equipos | ¿Qué equipo paro antes de que falle? | 6 a 8 h | 4 a 5 h | 4 h | 14 a 17 h | `supervivencia` |
| 3 | Efecto causal en plataformas | ¿Qué acción funcionó de verdad, y en qué empresas? | 10 a 12 h | 6 a 8 h | 6 h | 22 a 26 h | `jerarquico` en parte |
| 4 | Demanda con quiebres de stock | ¿Cuánto pido de cada producto? | 8 a 10 h | 5 a 6 h | 4 a 5 h | 17 a 21 h | `jerarquico` en parte |
| 5 | Campos del clima en espacio y tiempo | ¿Qué trae El Niño para mi cuenca? | 14 a 18 h | 10 a 12 h | 8 h | 32 a 38 h | `espacial` en parte |
| 6 | Valores extremos | ¿Cuál es la crecida de cien años aquí? | 10 a 12 h | 6 a 8 h | 6 h | 22 a 26 h | Poco |

Si hubiera que elegir dos: **el 1**, porque es el mismo tipo de modelo que el motor que ya pasó su sello y la historia sale directa del demo (del terreno con zinc a la mina), y **el 3**, porque responde la pregunta del primer cliente (plataformas con miles de empresas). Antes que cualquiera de los seis va terminar de validar los cuatro motores de hoy.

---

## 1 · Geoestadística minera en 3D

**La pregunta de negocio.** Con los sondajes que ya tengo, ¿qué bloques son mineral, cuáles no, en cuáles no se sabe, y dónde perforo el próximo sondaje para que valga lo que cuesta?

**El modelo.** Un proceso gaussiano en tres dimensiones con anisotropía (la ley del mineral se parece más a lo largo de la veta que a través de ella), tendencia y ley lognormal. Es el modelo del motor `espacial` con una dimensión más y con mediciones a lo largo de rectas (los sondajes) en vez de puntos sueltos.

**Por qué hoy es caro.** El variograma se ajusta a mano y lo hace un geoestadístico. Para tener rangos, y no solo un valor por bloque, se simulan cientos de versiones del yacimiento. Y «¿dónde perforo?» exige rehacer todo el análisis por cada sondaje candidato y por cada resultado posible: es la misma cuenta que nuestros 228 análisis del terreno (0,69 s contra más de 7 horas, M-08 a M-10), en un problema más grande.

**Qué simularía el generador.** Yacimientos: campos gaussianos en 3D por transformada de Fourier (el simulador de hoy ya lo hace en 2D), con rumbo, manteo y razón de anisotropía al azar; leyes lognormales; sondajes como rectas inclinadas con una muestra cada pocos metros; error de laboratorio; campañas de perforación agrupadas, como son las reales.

**Datos públicos que existen.** Los servicios geológicos de los estados de Australia publican sondajes con leyes entregados por las empresas (por ejemplo, el portal SARIG de Australia del Sur). Los conjuntos clásicos de libro de texto (Walker Lake; Jura) son reales pero en dos dimensiones: sirven para probar, no para mostrar. Queda por revisar si hay algo equivalente en Chile.

**Horas honestas.** Construir, 12 a 16: simulador 3D (3), red con convoluciones en una grilla de 16 o 24 bloques por lado (4), método lento de referencia en 3D (3), «¿dónde perforo?» (2), caso con datos reales (2 a 4). Entrenar, 8 a 10: una noche; cada yacimiento simulado cuesta varias veces lo que un terreno. Validar, 4 a 6: el método lento en 3D va a tardar varios minutos por caso.

**El riesgo.** La grilla. Con 16 bloques por lado son 4.096 celdas, cuatro veces las de hoy, y la resolución sigue siendo gruesa para una mina. Si la red no escala a grillas más finas, el motor sirve para exploración temprana y no para planificación.

## 2 · Confiabilidad de equipos

**La pregunta de negocio.** De mi flota de camiones, bombas o turbinas, ¿qué equipo conviene detener para mantención antes de que falle, y en cuáles no sé?

**El modelo.** Tiempo hasta la falla con censura (la mayoría de los equipos todavía no falla) más un desgaste que no se ve y que deja huella en los sensores. Es la familia del motor `supervivencia`: ahí lo que no se ve es el compromiso de una persona y la huella son las encuestas.

**Por qué hoy es caro.** Los modelos que juntan desgaste y falla se ajustan con MCMC, flota por flota, y los arma un ingeniero de confiabilidad. Lo que se usa cuando no hay uno son reglas fijas («mantención cada tantas horas»), que no dicen cuánto se pueden equivocar.

**Qué simularía el generador.** Flotas: equipos con edad, horas de uso y condiciones de trabajo; un desgaste latente por equipo; sensores con ruido y con huecos; mantenciones que reinician en parte el desgaste; fallas de más de un tipo.

**Datos públicos que existen.** C-MAPSS de la NASA (degradación de turbinas hasta la falla; es simulado por la NASA y hay que decirlo), las estadísticas de discos duros que publica Backblaze (reales) y los ensayos de rodamientos hasta la falla del repositorio de pronóstico de la NASA.

**Horas honestas.** Construir, 6 a 8: se reúsan el simulador y la red de `supervivencia`. Entrenar, 4 a 5. Validar, 4.

**El riesgo.** Es el más barato de la lista y a la vez el menos seguro: el motor del que parte **no pasó su sello** tras una noche de entrenamiento (0,43 desviaciones contra el método lento; el límite es 0,3). Primero hay que arreglar ese, y entender por qué falló, antes de prometer este.

## 3 · Efecto causal en plataformas

**La pregunta de negocio.** Activé recordatorios, o un beneficio, o un cambio de precio en una parte de mis empresas cliente. ¿De verdad cambió el resultado? ¿En cuáles sí y en cuáles no? ¿Conviene extenderlo?

**El modelo.** Diferencias en diferencias con adopción escalonada, bayesiano y jerárquico: cada empresa tiene su propio efecto, y las que tienen pocos datos toman prestado del resto.

**Por qué hoy es caro.** Lo hace un economista, pregunta por pregunta. El método rápido de siempre (una regresión con efectos fijos de empresa y de mes) está documentado que se equivoca cuando las empresas adoptan en fechas distintas y el efecto cambia con el tiempo (Goodman-Bacon, 2021; Callaway y Sant'Anna, 2021). El modelo completo, con miles de empresas, es MCMC de horas.

**Qué simularía el generador.** Paneles de empresas por mes: una tendencia común, sacudidas, adopción en fechas distintas, efectos que crecen o se apagan y, sobre todo, **adopción que no es al azar** (las empresas que activan algo son distintas de las que no). Ahí la respuesta correcta se conoce, que es justo lo que falta en los datos reales.

**Datos públicos que existen.** Los estudios clásicos tienen sus datos publicados: el salario mínimo de Card y Krueger, la Proposición 99 de California (el ejemplo del control sintético) y el programa de empleo de LaLonde. Los desafíos de datos de la conferencia ACIC publican conjuntos mitad reales y mitad simulados, donde el efecto verdadero se conoce.

**Horas honestas.** Construir, 10 a 12: generador de paneles (3), red sobre paneles (3), método lento de referencia (2), caso con datos (2 a 4). Entrenar, 6 a 8. Validar, 6: es lo difícil, porque en datos reales no hay respuesta escondida que destapar; el examen tendría que ser con los conjuntos mitad simulados.

**El riesgo.** Vender causalidad de más. El modelo supone que, sin la acción, las empresas habrían seguido tendencias parecidas. Krylov tendría que decir cuándo los datos contradicen ese supuesto (para eso sirve la nube) y negarse a responder, igual que hoy con un archivo malo. Si no lo hace, es peor que no tenerlo.

## 4 · Demanda con quiebres de stock

**La pregunta de negocio.** ¿Cuánto pido de cada producto para cada local? ¿Cuánto me cuesta pedir de más y cuánto quedarme corto?

**El modelo.** Conteos jerárquicos por producto y por local con censura: cuando el producto se acaba, lo vendido es menos que lo que la gente quería comprar, y ese dato faltante no es al azar.

**Por qué hoy es caro.** Los métodos rápidos (promedios móviles y parientes) tratan la venta como si fuera la demanda y por eso piden de menos justo en lo que más se agota. El modelo que corrige eso necesita MCMC por producto, y un negocio chico tiene miles de productos.

**Qué simularía el generador.** Locales por producto por semana: estacionalidad, promociones, productos que casi no se venden, días sin stock y clientes que, si no hay, se llevan otro.

**Datos públicos que existen.** Las competencias de pronóstico M5 (ventas de Walmart) y Corporación Favorita (supermercados de Ecuador), las dos en Kaggle, y el conjunto Online Retail de UCI. Las de Kaggle tienen licencia de competencia: hay que leerla antes de mostrar nada.

**Horas honestas.** Construir, 8 a 10. Entrenar, 5 a 6. Validar, 4 a 5.

**El riesgo.** Es el que mejor calza con lo que Krylov ya muestra (dos costos, tres colores, lo que cuesta no saber) y el que menos se luce: no tiene mapa. Vende bien en una reunión y mal en un escenario.

## 5 · Campos del clima en espacio y tiempo

**La pregunta de negocio.** Para una empresa agrícola, de energía o de seguros: ¿cuánta lluvia y qué temperatura vienen en mi zona los próximos meses, con qué rango, y cómo cambia eso si se confirma El Niño?

**El modelo.** Un campo gaussiano en espacio y tiempo: pocos patrones espaciales que evolucionan con una dinámica lineal con ruido, ajustado a temperatura del mar y a lluvia.

**Por qué hoy es caro.** Los pronósticos oficiales salen de conjuntos de modelos físicos corridos en supercomputadores. La alternativa estadística, un modelo jerárquico en espacio y tiempo, es de las más pesadas que hay: MCMC de horas o días por ajuste.

**Qué simularía el generador.** Décadas de campos mensuales con patrones al azar, estaciones con huecos y series de largo distinto.

**Datos públicos que existen.** La temperatura del mar reconstruida por la NOAA (ERSST) y su índice de El Niño (ONI), HadISST del servicio meteorológico británico, el reanálisis ERA5 de Copernicus y la lluvia de CHIRPS. En Chile, las estaciones de la DGA y de la Dirección Meteorológica, que el centro CR2 reúne.

**Horas honestas.** Construir, 14 a 18. Entrenar, 10 a 12. Validar, 8: hay que predecir años pasados sin mirarlos y comparar con lo que ocurrió.

**El riesgo.** Es el más caro y el más vistoso. Y es el único donde ya existe un pronóstico oficial, gratis y hecho con mucha más física que la nuestra. Lo que Krylov podría agregar es la decisión (cuánto cuesta no saber, para ese negocio), no un pronóstico mejor. Hay que decirlo así.

## 6 · Valores extremos

**La pregunta de negocio.** ¿Cuál es la crecida, la lluvia o el siniestro que se espera una vez cada cien años en este lugar? ¿Cuánto me cuesta diseñar para menos?

**El modelo.** Valores extremos con dependencia espacial. Su verosimilitud no se puede calcular con muchas estaciones, y por eso es un caso de libro para la inferencia basada en simulación: simular es fácil, calcular no.

**Por qué hoy es caro.** Se usan aproximaciones lentas que escalan mal con el número de estaciones, o se analiza cada estación por separado y se pierde lo que una le enseña a la otra.

**Qué simularía el generador.** Máximos anuales por estación, con parámetros que cambian suavemente en el mapa y con tormentas que golpean varias estaciones a la vez.

**Datos públicos que existen.** Los registros diarios de estaciones de la NOAA (GHCN-Daily), los caudales del servicio geológico de Estados Unidos y, en Chile, los caudales y la lluvia de la DGA.

**Horas honestas.** Construir, 10 a 12. Entrenar, 6 a 8. Validar, 6.

**El riesgo.** Los extremos se validan mal por definición: hay pocos. Y la decisión D-17 ya cortó un motor de eventos raros de esta hackathon por tiempo. Va al final de la fila.

---

## Qué se puede decir de esto en el pitch

- **Sí:** «La hoja de ruta es amortizar más modelos de este tipo. El primero sería el del terreno en tres dimensiones, para minería.» Con el rótulo «hoja de ruta» en pantalla.
- **No:** horas, fechas, nombres de empresas mineras, ni que alguno de estos existe. No hay ninguna cifra de esta página en `pitch/CIFRAS.md`.
- **Si preguntan «¿eso no existe ya?»:** existen modelos ya amortizados para familias fijas o genéricas (la búsqueda está en `estado/seguimiento.md`, sábado 10:50). Ninguno reemplaza a uno de nuestros motores, y no revisamos ninguno de los seis candidatos de esta lista: se responde «no lo hemos revisado para ese caso».
