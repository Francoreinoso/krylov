# Modelos candidatos: lo que Krylov podría amortizar después, en minería

> Material de apoyo para la lámina 7 del deck («Hoja de ruta») y para la pregunta «¿y después qué?». **Nada de esto está construido ni se va a construir en la hackathon.** Este archivo usa nombres técnicos; en pantalla y en voz alta se usa `GLOSARIO.md`.
>
> Los cinco problemas salen del documento del equipo «Inferencia Bayesiana Amortizada para la Gran Minería Chilena». Aquí se les agrega lo que ese documento no trae: horas estimadas, datos públicos que se podrían usar y el riesgo de cada uno.

La idea que se vende es una sola: un modelo estadístico difícil, de los que hoy exigen un data scientist y horas de cómputo, **se entrena una vez con casos simulados y después responde en un paso**, con su rango, con lo que cuesta no saber y con dónde conviene medir. Eso es un Artificial Data Scientist. Cada modelo de esta lista sería un motor más.

## Con qué vara se estiman las horas

Las horas son **estimaciones nuestras, no medidas**. La unidad es una persona con Claude Code y un MacBook Air, como en esta hackathon. Lo único medido que hay para calibrarlas:

| Medido | Valor | Cifra |
|---|---|---|
| Entrenamiento del motor del terreno, que pasó su sello | 280 minutos, 7.750.592 terrenos simulados, MacBook Air M4 | M-01, M-02 |
| Entrenamiento del motor de rotación, que **no** pasó su sello | 267,5 minutos, 12.739.616 empresas simuladas, MacBook Air M3 | M-21, M-23, M-28 |
| Un análisis del terreno con el método lento (MCMC) | 117 segundos | M-25 |
| Horas de construcción del motor del terreno | No se midieron | M-19, pendiente |

La segunda fila es la que manda: **una noche de entrenamiento no garantiza un motor validado.** Un modelo con 7 parámetros pasó; uno con 32 no. Los cinco modelos de abajo son más grandes que los dos.

## Resumen

| # | Decisión | El modelo, en una línea | Construir | Entrenar | Validar | Total | Qué reúsa |
|---|---|---|---|---|---|---|---|
| 1 | Leyes: ¿planta, lixiviación o botadero? | Campo gaussiano 3D con dominios geológicos | 14 a 18 h | 8 a 12 h | 6 a 8 h | 28 a 38 h | `espacial` casi entero |
| 2 | Camiones: ¿cuál falla primero? | Desgaste latente por equipo y tiempo hasta la falla | 8 a 10 h | 5 a 6 h | 5 h | 18 a 21 h | `supervivencia` |
| 3 | Flotación: ¿cómo ajusto la planta? | Cinética de flotación, con ecuaciones diferenciales | 12 a 16 h | 6 a 8 h | 6 h | 24 a 30 h | Poco |
| 4 | Sismicidad: ¿evacúo el sector? | Proceso de Hawkes jerárquico por sector | 12 a 16 h | 6 a 8 h | 6 a 8 h | 24 a 32 h | `jerarquico` en parte |
| 5 | Taludes y relaves: ¿ruido o falla? | Estado latente en espacio y tiempo, no lineal | 16 a 22 h | 10 a 12 h | 8 a 10 h | 34 a 44 h | `espacial` en parte |

**Por dónde partir:** el 1. Es el mismo tipo de modelo que el motor que ya pasó su sello, y la historia sale directa del demo: del terreno con zinc a los bloques de una mina. Después el 2, que es el más barato, siempre que antes se arregle el motor del que parte. Los dos últimos deciden sobre la seguridad de personas: van al final y con otro estándar de validación.

---

## 1 · Control de leyes: cobre y arsénico

**La decisión.** Con los datos de los pozos de tronadura, ¿este bloque va a planta, a lixiviación o a botadero? ¿En cuáles no se sabe, y conviene muestrear más antes de mover la pala?

**El modelo.** Dos capas: dominios geológicos que no se ven (un campo de Markov oculto) y, dentro de cada dominio, la ley como un proceso gaussiano. Es el modelo del motor `espacial` con una dimensión más, con más de un metal y con dominios.

**Por qué hoy es caro.** El campo de dominios tiene una constante de normalización que no se puede calcular, y la covarianza escala con el cubo del número de muestras. Los rangos se sacan con cientos de simulaciones condicionales, y lo hace un geoestadístico.

**Qué simularía el generador.** Yacimientos: dominios al azar, leyes por dominio, anisotropía con rumbo y manteo, pozos en malla regular con error de laboratorio.

**Datos públicos.** Los servicios geológicos de los estados de Australia publican sondajes con leyes (por ejemplo, el portal SARIG de Australia del Sur). Los conjuntos de libro de texto (Walker Lake, Jura) son reales pero en dos dimensiones. No conocemos datos públicos de pozos de tronadura con arsénico en Chile: **el piloto necesitaría los datos de la faena.**

**El riesgo.** La grilla. A 16 bloques por lado son 4.096 celdas, cuatro veces las de hoy, y sigue siendo gruesa para un banco real. La versión con red sobre grafos que propone el documento del equipo no se parece a nada que hayamos validado.

## 2 · Flota de camiones: vida útil remanente

**La decisión.** En cada cambio de turno, ¿qué camión conviene detener para mantención antes de que falle en la rampa?

**El modelo.** Cada equipo tiene un desgaste que no se ve, que crece a saltos según cómo se usa y que deja huella en la telemetría y en el análisis de aceite; la falla ocurre cuando cruza un nivel. La mayoría de los equipos todavía no falla (censura). Es la familia del motor `supervivencia`.

**Por qué hoy es caro.** Los modelos que juntan desgaste y falla tienen decenas de miles de variables latentes restringidas a ser positivas, y se ajustan con MCMC, flota por flota. Lo que se usa en su lugar son reglas fijas.

**Qué simularía el generador.** Flotas: equipos con edad, horas, carga y pendiente; desgaste con incrementos Gamma; sensores con ruido y con huecos; mantenciones que lo reinician en parte.

**Datos públicos.** No conocemos telemetría pública de camiones mineros. Para probar el método sirven C-MAPSS de la NASA (turbinas hasta la falla; es simulado por la NASA y hay que decirlo) y las estadísticas de discos duros de Backblaze (reales). **El piloto necesitaría los datos de la faena.**

**El riesgo.** Es el más barato y el menos seguro: el motor del que parte **no pasó su sello** tras una noche de entrenamiento (0,43 desviaciones contra el método lento; el límite es 0,3). Primero hay que entender por qué.

## 3 · Flotación: recuperación en la planta

**La decisión.** Cambió el mineral que entra. ¿Cómo ajusto aire, reactivos y nivel de espuma para no perder metal por la cola?

**El modelo.** La cinética de flotación de cada especie mineral, banco por banco, como un sistema de ecuaciones diferenciales cuyas constantes cambian con el mineral; se observa con analizadores en línea y con cámaras de espuma.

**Por qué hoy es caro.** Cada paso del MCMC obliga a resolver ecuaciones diferenciales rígidas y sus derivadas, y la respuesta tiene más de un máximo: dos combinaciones distintas de constantes explican casi igual los datos.

**Qué simularía el generador.** Trayectorias de la planta con mezclas de mineral que cambian, con los sensores y su ruido. Simular es fácil y se puede dejar corriendo antes; por eso el caso calza bien.

**Datos públicos.** En Kaggle hay un conjunto real de una planta de flotación de mineral de hierro, con mediciones cada pocos segundos durante varios meses («Quality Prediction in a Mining Process»). No es cobre y hay que leer su licencia.

**El riesgo.** Que la respuesta honesta sea «con estos sensores no se puede saber» para la mitad de las constantes. Eso también es un resultado, y Krylov lo dice; pero hay que saberlo antes de prometer una recomendación de operación.

## 4 · Sismicidad inducida: estallido de rocas

**La decisión.** Después de una tronadura en una mina subterránea, ¿evacúo esta calle o la mantengo en producción?

**El modelo.** Un proceso de Hawkes por sector: cada sismo sube por un rato la probabilidad de los siguientes. Los parámetros de cada sector se parecen a los de los demás (jerárquico).

**Por qué hoy es caro.** La verosimilitud crece con el cuadrado del número de eventos, y la jerarquía produce la geometría de embudo que frena al MCMC.

**Qué simularía el generador.** Secuencias de sismos por sector con el algoritmo de Ogata: tronaduras, réplicas, magnitudes y ubicaciones.

**Datos públicos.** La plataforma europea de sismicidad inducida (IS-EPOS) publica episodios de minas subterráneas. Queda por revisar qué trae exactamente y con qué licencia.

**El riesgo.** Es una decisión sobre la vida de personas. Krylov no puede ser quien decide evacuar: a lo más puede decir cuánto no se sabe. Y validar un modelo de eventos raros es difícil por definición: hay pocos estallidos con que examinarlo. Va al final, con la mina y con sus geomecánicos.

## 5 · Taludes y tranques de relaves

**La decisión.** El radar muestra que un sector del muro se mueve. ¿Es ruido atmosférico, deformación normal después de una tronadura, o el comienzo de una falla?

**El modelo.** El estado del macizo (resistencia, deformación) evoluciona en el espacio y en el tiempo, de manera no lineal, y se observa con radar y con piezómetros.

**Por qué hoy es caro.** Seguir un estado latente no lineal de miles de nodos rompe los métodos de partículas; se termina usando umbrales fijos de velocidad.

**Qué simularía el generador.** Muros con zonas débiles al azar, lluvia, tronaduras y el ruido propio del radar.

**Datos públicos.** Las imágenes de radar del satélite Sentinel-1 son públicas y se han usado para estudiar tranques después de sus fallas. Sernageomin publica el catastro de depósitos de relaves de Chile. Los radares terrestres de las faenas no son públicos.

**El riesgo.** El más alto de la lista, por las mismas razones del anterior y porque es el modelo más grande. Es el último.

---

## Qué se puede decir de esto en el pitch

- **Sí:** «La hoja de ruta es un modelo para cada decisión crítica de la mina: leyes, sismicidad, camiones, flotación, taludes y relaves.» Con «Hoja de ruta» en pantalla.
- **No:** horas, fechas, nombres de faenas ni de empresas, ni que alguno de estos modelos existe.
- **Tampoco, por ahora, las cifras del documento del equipo.** No tienen fuente registrada en `pitch/CIFRAS.md`:

| Afirmación del documento | Qué falta |
|---|---|
| Geología tiene menos de 2 horas tras recibir los datos de pozos de tronadura | Fuente |
| El arsénico castiga el concentrado sobre 0,5% | Fuente |
| Tras una tronadura hay 15 a 30 minutos para decidir si se evacúa | Fuente |
| Un camión detenido en rampa cuesta US$ 15.000 a 40.000 por hora | Fuente |
| La pulpa está 15 a 25 minutos en los bancos | Fuente |
| Los radares escanean el muro cada 2 a 6 minutos | Fuente |
| Piloto de 8 semanas sobre datos históricos | Es un plan: registrarlo como hipótesis |

  Son las cifras que más venden. Si se van a usar, una persona abre la fuente de cada una y la registra antes; mientras tanto, las láminas dicen lo mismo sin número.
- **Si preguntan «¿eso no existe ya?»:** existen modelos ya amortizados para familias fijas o genéricas (la búsqueda está en `estado/seguimiento.md`, sábado 10:50). No revisamos ninguno de estos cinco casos: se responde «no lo hemos revisado para ese caso».
