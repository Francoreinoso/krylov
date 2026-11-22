# Última iteración de diseño del deck: qué cambió y por qué

Sábado 21 de noviembre, entre las 22:40 y la medianoche. El deck anterior está completo en [`original/`](original/RESPALDO.md) (abre solo) y en el tag de git `deck-original`. Para devolver una lámina a como estaba: «vuelve las láminas X e Y al estado original de `pitch/deck/original`, y mantén las demás como están».

El recorrido pasó de 13 a 14 láminas: el yacimiento entró como lámina 12. Fuera del recorrido quedan cuatro: Q, L, 0 y W. Las láminas A y M se borraron.

## Lo que cambió en todo el deck

| Qué | Por qué |
|---|---|
| Las láminas 7 a 11 perdieron la columna izquierda («Krylov entrega…», el gráfico de barras, la cuenta de colores y «vale despejar esa duda») | Enredaba, y las cifras de plata salían de costos supuestos |
| En su lugar, un punto viaja por la escena y una tarjeta muestra la respuesta de la red ahí: decisión, estimación, intervalo y distribución, que cambian al viajar (`js/foco.js`) | Es la respuesta de Krylov a la vista: distinta en cada lugar, con su duda |
| La operación se llama «la minera», no «la mina» | Pedido del equipo |
| La tipografía de texto pasó de Instrument Sans a Archivo (ya venía en `vendor/`, con licencia abierta) | El detector de Impeccable marca Instrument Sans como sobreusada; Archivo es más industrial y acompaña mejor a Big Shoulders |
| Se quitaron los rótulos en mayúsculas monoespaciadas sobre los títulos («TEXTO → TEXTO», «DATASET → DECISIÓN…») | Son la marca más reconocible de una interfaz generada |
| La barra de avance se anima con `transform`, no con `width`; se borraron 108 reglas de estilo y dos archivos de código sin uso | Fluidez y un repositorio que se lee limpio |
| Al viajar de una unidad a otra, la curva se desplaza y cambia de ancho (se mezclan los cuantiles de las dos respuestas, no sus dibujos) | Mezclar los dibujos mostraba, a mitad de camino, una curva de dos lomos que no era la respuesta de ninguna |
| La lámina que sale se va en 0,14 s y la que entra espera a que se haya ido; las escenas se funden antes de llegar a la marca y a la cuenta de abajo; las etiquetas flotantes llevan placa oscura | Arreglos de la revisión de movimiento de Impeccable: nada queda encima de otra cosa |
| Dos escenas se rehicieron desde cero (9 y 11), una lámina se rehízo (3) y hay una nueva (W) | Detalle abajo |

## Lámina por lámina

### 1 · Portada
- **Cambio:** el suelo sigue hasta los bordes de la lámina y se pierde en una bruma; ya no hay un rajo flotando sobre negro. Texto nuevo.
- **Por qué:** pedido directo. Con el suelo continuo, la primera imagen es un lugar y no un objeto recortado.
- **Texto antes:** «En una mina, las decisiones no esperan. Krylov las responde al instante, con los modelos que hoy exigen horas de cálculo y un especialista.»
- **Texto ahora:** «Responde en milisegundos lo que a un especialista le toma horas de cálculo, y dice cuánto se puede equivocar.»
- **Archivos:** `js/portada.js`, bloque `#l-valor` de `deck.css`.

### 2 · Generative AI para datasets
- **Cambio:** título y párrafo reescritos; «Un LLM» pasa a «LLM»; fuera «TEXTO → TEXTO» y «DATASET → DECISIÓN, CON SU INCERTIDUMBRE»; las dos frases bajo las filas ahora son paralelas.
- **Por qué:** el párrafo anterior era ambiguo («por eso responde cualquier dataset»), y el título usaba la fórmula «no es X, es Y».
- **Título antes:** «No es una red que predice. Es Generative AI para datasets.» **Ahora:** «Krylov es Generative AI para datasets.»
- **Párrafo antes:** «Un LLM se pre-entrenó con texto: por eso responde cualquier pregunta, sin volver a entrenar. Krylov se pre-entrenó con millones de datasets simulados de minería: por eso responde cualquier dataset.»
- **Párrafo ahora:** «Un LLM leyó tanto texto que hoy responde lo que le preguntes. Krylov practicó con millones de datasets simulados y hoy responde el tuyo: qué conviene hacer y cuánta duda queda.»
- **Línea técnica antes:** «Simulation-based Inference. Un modelo bayesiano simula los datasets posibles, y la red aprende qué hay detrás de cada uno.» **Ahora:** «Simulation-based Inference. Un modelo bayesiano inventa los datasets y la red aprende a leer lo que hay detrás de cada uno.»
- **Bajo las filas, antes:** «Nadie lo entrena para hacerle una pregunta.» / «Ninguna mina entrena un modelo para su dataset.» **Ahora:** «Le preguntas y responde. Nadie lo entrenó para tu pregunta.» / «Le subes un dataset y responde. Nadie lo entrenó para tu dataset.»
- **Archivos:** `js/paradigma.js`, sección `l-paradigma`.

### 3 · Antes y hoy
- **Cambio:** animación nueva. Dos carriles. En «Antes», cada dataset de una fila pasa por tres cajas y recién entonces sale su mapa. Al avanzar, el carril de «Antes» se detiene y sus cajas se van (quedan los huecos, punteados): «Elegir modelo» y «Entrenar» caen al carril de «Hoy» y quedan bajo un corchete que dice «una sola vez» (con «Simular datasets» entre ambas), «Inferir» se encoge hasta ser la red y, antes de un segundo y medio, los datasets ya la cruzan de corrido mientras la grilla de respuestas se llena.
- **Por qué:** el mensaje se entendía pero no impresionaba. Ahora el cambio de paradigma se ve como un movimiento: entrenar sale del ciclo.
- **Texto:** el título se mantiene («Antes, un modelo por dataset. Hoy, una red para todos.»). «En el pasado» pasa a «Antes»; «Elegir el modelo» a «Elegir modelo»; «Entrenar con ese dataset» a «Entrenar»; «↻ con cada dataset» a «todo de nuevo, con cada dataset»; «Inferir: un paso» pasa a ser la red, con «la red, ya entrenada»; «datasets respondidos» a «respondidos».
- **Archivos:** `js/flujo.js` (reescrito).

### 4 · Simulaciones
- **Cambio:** el número ya no es el de un solo modelo. Es la suma de los cinco con sello, 71.560.512, con su desglose debajo (7,8 M bancos de roca, 1,7 M paredes, 43,2 M plantas, 15,2 M flotas de camiones, 3,7 M túneles). El contador sube desde cero y frena. Los terrenos del remolino son más, más chicos y más nítidos, y ninguno cruza gigante por delante del texto.
- **Por qué:** 7.750.592 era solo el primer problema y no quedaba claro. La suma dice «muchas», el desglose dice de qué, y la línea de abajo dice «rápidas».
- **Texto antes:** «Antes de ver un solo dataset real, Krylov se pre-entrenó con / 7.750.592 / terrenos simulados / En cada uno, la respuesta correcta se conoce.»
- **Texto ahora:** «Antes de ver un solo dato real, Krylov practicó con / 71.560.512 / simulaciones / [desglose] / Cinco modelos, pre-entrenados en dos notebooks en menos de 15 horas.»
- **Cifras:** M-66 (suma de M-01 y M-48; 867 minutos).
- **Archivos:** `js/mundos.js`, `js/campo.js`, bloque `#l-mundos`.

### 5 · Entra un archivo, sale la respuesta
- **Cambio:** solo el cuerpo corto. La animación no se tocó.
- **Texto antes:** «La red ya está pre-entrenada: responder es un solo paso.» **Ahora:** «Lo caro se calculó antes. Con tu archivo, Krylov solo responde.»

### 6 · Seis decisiones
- **Cambio:** son seis (entra el yacimiento). Las preguntas se dicen como las diría quien decide. La primera figura es nueva (un piso del rajo en tres colores); la del cuerpo de mineral pasó al yacimiento, que es lo que dibuja.
- **Por qué:** se buscaba impacto. Preguntas cortas, en primera persona y con reloj.
- **Título antes:** «Una mina decide esto todos los días.» **Ahora:** «Una minera se pregunta esto todos los días.»
- **Bajada antes:** «Cinco decisiones, cinco modelos de especialista. Un solo Artificial Data Scientist.» **Ahora:** «Seis preguntas, seis modelos de especialista y un solo Artificial Data Scientist.»
- **Preguntas antes:** «¿Qué roca conviene procesar?», «¿La pared de la mina va a ceder?», «¿Se está perdiendo cobre en la planta?», «¿Qué camión paro antes de que falle?», «¿Puede la gente volver a entrar al túnel?»
- **Preguntas ahora:** «¿Proceso esta roca o la aparto?», «¿La pared aguanta el turno?», «¿Cuánto cobre se está perdiendo?», «¿Qué camión paro hoy?», «¿Ya puede volver a entrar la gente?», «¿Dónde está el mineral?»
- **Archivos:** `js/vision.js`, sección `l-vision`.

### 7 · ¿Qué roca conviene procesar, y cuál apartar?
- **Cambio, paso 1:** fuera toda la columna izquierda. Un punto recorre el terreno entre seis paradas (dos de cada color) y la tarjeta muestra, cuadro a cuadro, lo que la red respondió para el bloque que tiene debajo. Cuando aparece el punto, las muestras y la malla bajan de brillo para que no se pierda. Un clic en el terreno manda el punto ahí.
- **Cambio, paso 2 («¿Dónde perforo?»):** fuera los dólares. Ahora dice cuántos lugares se probaron (40), cuántos análisis se rehicieron (480) y en cuánto (1,3 segundos), y compara los tres mejores entre sí con barras: A = 100, B = 94, C = 89. El conteo en pantalla dura los mismos 1,3 segundos que se midieron.
- **Por qué:** los US$ 9 mil, 8 mil y 8 mil salían de costos supuestos (K-22 a K-24). El valor relativo dice lo mismo sin inventar plata, y los 480 análisis en 1,3 segundos son medidos (M-43, M-44).
- **Texto antes (paso 1):** «Krylov entrega, para cada parte del terreno, cuánto arsénico hay, con su intervalo de credibilidad», el gráfico, «147 Conviene apartar / 309 No sabemos / 568 Puede ir a la planta» y «Más de US$ 1 millón vale despejar esa duda». **Ahora:** la tarjeta: «En este punto del terreno / [decisión] / [ppm de arsénico] / entre … y …» y la curva contra «Máximo que acepta la planta».
- **Texto antes (paso 2):** «Una muestra más cuesta US$ 1.500. Krylov rehízo el análisis completo 480 veces y dice dónde vale más: A US$ 9 mil, B US$ 8 mil, C US$ 8 mil.» **Ahora:** «Krylov probó 40 lugares y rehízo el análisis completo 480 veces, en 1,3 segundos. Estos son los tres donde una muestra más despeja más duda: A 100, B 94, C 89. Lo que aporta una muestra en cada lugar, con A = 100.»
- **Archivos:** `js/terreno.js`, `js/foco.js`, sección `l-leyes`.

### 8 · La pared se mueve. ¿Es ruido, o va a ceder?
- **Cambio:** fuera la columna izquierda. El foco viaja por cinco sectores. En uno que conviene cerrar, la cámara se acerca, el radar se apaga y ese tramo de la pared cede: los escalones se cortan, la masa baja y los fragmentos se abren al pie, con el rótulo «Proyección: así cede si sigue acelerando» unido al tramo. En el que más se movió sin acelerarse, la tarjeta muestra lo que midió el radar y dice «puede seguir abierto».
- **Por qué:** los colores decían qué sector estaba en riesgo, pero nada se veía ceder. Ahora «ceder» ocurre en pantalla, dicho como proyección (regla 22: sin exagerar).
- **Texto antes:** «Krylov entrega, para cada sector que se acelera, cuántas horas le faltan…», el gráfico, «5 Conviene cerrar / 2 No sabemos / 29 Puede seguir abierto», «Decenas de miles de dólares vale despejar esa duda» y la tarjeta «Sector 10: conviene cerrar. Faltan 4,9 horas, entre 2,4 y 7,4».
- **Texto ahora:** la tarjeta: «Sector 10 / Conviene cerrar / 4,9 h / le quedan antes de ceder / entre 2,4 y 7,4 horas», con «Próximas 12 horas» en la línea; y en el sector 25: «Puede seguir abierto / 24 mm / se movió, pero a ritmo parejo: no se está acelerando / Lo que midió el radar en 48 horas».
- **Archivos:** `K.registrar('taludes', …)` en `js/decisiones.js`.

### 9 · ¿Se está perdiendo cobre en la planta?
- **Cambio:** escena rehecha desde cero. La planta se mira desde donde termina la pulpa: lo recuperado sube por una columna hasta su estimación, contra la meta de 84%; lo que no flotó cae al relave, más denso donde se pierde más, con una cifra que sigue al foco («15,3% se va al relave»).
- **Por qué:** la escena anterior mostraba estanques con espuma, y la pérdida, que es la pregunta, no se veía.
- **Texto antes:** «Krylov entrega, para cada línea, el cobre que va a recuperar al final…», el gráfico, «2 Conviene ajustar / 3 No sabemos / 3 Va bien», «Miles de dólares vale despejar esa duda». **Ahora:** la tarjeta («Línea 6 / No sabemos: esperar otra medición / 84,7% / del cobre va a recuperar / entre 82,8 y 87,0%»), «Meta: 84%», «Relave: lo que sobra» y «… se va al relave».
- **Ojo:** la columna y la densidad de la caída usan el eje recortado de la tarjeta (75% a 93%): las diferencias entre líneas se ven más grandes que en un eje de 0 a 100. El porcentaje escrito es el real.
- **Archivos:** `js/flotacion.js` (nuevo).

### 10 · ¿Qué camión paro antes de que falle?
- **Cambio:** fuera la columna izquierda y fuera las etiquetas «Camión 23 cerca de fallar», que eran las que pisaban la tarjeta del Camión 22. Ahora la tarjeta va a la izquierda, donde la escena no llega, y el foco salta entre los camiones que están a la vista, cambiando de color de decisión cuando puede. El camión que se mira se enciende y los demás bajan. El eje del riesgo va en raíz, para que un camión de 3% y uno de 67% se lean en el mismo gráfico.
- **Por qué:** el solape que nadie había visto, y la misma idea de las otras láminas.
- **Texto antes:** «Krylov entrega, para cada camión, el riesgo de que falle antes de su mantención…», el gráfico, «8 Conviene adelantar la mantención / 1 No sabemos / 31 Llega a su mantención», «Cientos de dólares vale despejar esa duda». **Ahora:** la tarjeta («Camión 23 / Conviene adelantar la mantención / 67,0% / de riesgo de fallar antes de su mantención / entre 47,5 y 83,5%») con «Sobre 11,8%, conviene parar» en la línea.
- **Archivos:** `K.registrar('flota', …)` en `js/decisiones.js`.

### 11 · Tras la explosión, ¿puede volver a entrar la gente?
- **Cambio:** escena rehecha desde cero. Un bloque de roca abierto a la altura de los túneles. A la hora cero, la explosión manda un frente de onda por la roca, con polvo y roca que cae en el frente del túnel. Después, cada temblor del archivo sacude su sector a su hora; el fuerte bota roca del techo. La cámara acompaña al foco.
- **Por qué:** la anterior parecía fuegos artificiales: chispas en todas direcciones sobre alambres en el vacío.
- **Texto antes:** «Krylov entrega, por sector, el riesgo de un temblor fuerte en las próximas 6 horas…», el gráfico, «0 Conviene mantener cerrado / 4 No sabemos / 4 Se puede reingresar», «Decenas de miles de dólares vale despejar esa duda». **Ahora:** la tarjeta («Sector 3 / No sabemos: esperar y seguir midiendo / 7,5% / de riesgo de temblor fuerte en 6 horas / entre 3,4 y 12,3%») con «Sobre 9,1%, sigue cerrado», y el reloj «1 h 53 min / después de la explosión».
- **Archivos:** `js/sismicidad.js` (nuevo).

### 12 · ¿Dónde está el mineral? (antes, tecla Y)
- **Cambio:** entra al recorrido, entre los túneles y «¿cómo sé que acierta?». Ajustes de ritmo: la cámara llega antes, los pisos se encienden en 2 segundos y la bajada por la perforación dura 7 segundos en vez de 10. Textos retocados. No se cambió la escena.
- **Por qué:** pedido directo: sumarla a las láminas normales sin cambios grandes.
- **Texto antes:** «Una mina a rajo abierto, simulada. En la zona marcada se perforó y se sacaron 604 muestras de roca.» **Ahora:** «Un rajo abierto, simulado. En la zona marcada se perforó y salieron 604 muestras de roca.»
- **Antes:** «Krylov dibuja el mineral que hay debajo, piso por piso: cada curva de cobre es su borde a una profundidad.» **Ahora:** «En ese tiempo Krylov dibuja el mineral que hay debajo, piso por piso. Cada curva de cobre es su borde a esa profundidad.»
- **Antes:** «Las curvas doradas encierran roca que puede ser mineral, pero todavía no se sabe. Bajando por la próxima perforación, esto espera Krylov a cada profundidad:» **Ahora:** «Las curvas doradas encierran roca que podría ser mineral: ahí todavía no se sabe. Esto espera encontrar Krylov al bajar por la próxima perforación:»
- **Antes:** «Eso tarda el método de siempre en este mismo archivo. Krylov toma la misma decisión en 92,1% de los bloques…» **Ahora:** «Eso tarda el método de siempre con este mismo archivo. Krylov llega a la misma decisión en 92,1% de los bloques…»
- **Aviso antes:** «Sexto modelo, entrenado después del cierre. Yacimiento simulado. Todavía no está en la app.» **Ahora:** «Yacimiento simulado. Este modelo todavía no está en la app.»
- **Ojo:** el sello de este motor dice «no pasa» (dos de sus 15 parámetros). Se cuenta su mapa. Está en las notas.
- **Archivos:** `yacimiento.html`, sección `l-yacimiento`.

### 13 · ¿Y cómo sé que acierta? (antes, 12)
- **Cambio:** otra medida. Antes: decisiones acertadas contra un archivo de demo (0,98, 1,00, 1,00, 0,92, 1,00). Ahora: la validación de cada sello, que ya estaba calculada: en 2.000 casos nuevos, qué fracción de las veces la respuesta real cayó dentro del rango de 90%. Los seis puntos caen sobre la línea de 90% (90,0, 90,5, 90,5, 89,8, 89,5 y 90,1). Abajo, el examen con datos reales públicos: 138 de 155.
- **Por qué:** tres modelos en 100% sobre 4, 5 y 34 casos se veían inventados aunque fueran ciertos. Un 90% que cae en 90% es más creíble y es lo que hay que pedirle a un modelo que dice cuánto duda. No se recalculó nada.
- **Texto antes:** «Acierto de cada modelo: de las decisiones que tomó, cuántas acertó.» **Ahora:** «Cuando Krylov da un rango de 90%, la respuesta real cae adentro 9 de cada 10 veces. Lo medimos en 2.000 casos nuevos por modelo, que la red nunca había visto.» y «Y con datos reales públicos: de 155 mediciones que le escondimos, 138 cayeron dentro de su rango.»
- **Cifras:** M-68, M-63 y M-67.
- **Archivos:** `js/confianza.js`, sección `l-confianza`.

### 14 · Cierre (antes, 13)
- **Cambio:** título y cuerpo reescritos; fuera «cualquier industria».
- **Título antes:** «Modelos que exigían un especialista y horas de cómputo. Ahora, en un segundo y para quien decide.» **Ahora:** «Decidir con el mejor modelo ya no toma horas. Toma lo que demora subir un archivo.»
- **Cuerpo antes:** «Krylov es el Artificial Data Scientist de la minería, y de cualquier industria que decida con datos. Su motor: Bayesian Amortized Inference.» **Ahora:** «Krylov es el Artificial Data Scientist de la minería: seis decisiones respondidas hoy, con Bayesian Amortized Inference por dentro.»
- **Contador antes:** «Mientras duró este pitch, Krylov habría respondido … análisis completos. El método de siempre: 0.» **Ahora:** «Mientras hablábamos, Krylov habría respondido … análisis completos. El método de siempre, 0.»

### Q · ¿Quién lo usa?
- **Cambio:** cargos formales y la sexta columna (el yacimiento).
- **Título antes:** «¿Quién lo usa? Quien decide en el turno.» **Ahora:** «¿Quién lo usa? Quien toma la decisión en terreno.»
- **Antes:** «El geólogo de la mina», «Quien vigila la pared», «El jefe de turno de la planta», «Quien planifica la mantención», «El jefe de turno bajo tierra».
- **Ahora:** «Geólogo de producción · Qué roca va a la planta y cuál se aparta», «Ingeniero geotécnico · Si se cierra un sector de la pared», «Jefe de planta · Qué línea conviene ajustar», «Planificador de mantención · Qué camión se detiene primero», «Jefe de turno subterráneo · Cuándo se reingresa a un sector», «Geólogo de exploración · Dónde está el mineral y dónde perforar».

### L · ¿Y un LLM?
- Sin cambios de contenido (pedido: se queda tal cual). Solo hereda la tipografía nueva.

### 0 · Cómo funciona
- **Cambio:** ahora tiene tres pasos. Primero se ve solo lo que se hace una vez; al avanzar se enciende lo que pasa con cada dataset; y el tercer paso es la ficha de los seis modelos: qué modelo es, con cuántas simulaciones practicó, en cuántos minutos y cuánto tarda cada respuesta. Con otra flecha se pasa al mapa.
- **Por qué:** pedido: más pasos dentro de la lámina, para quien pregunta por dentro.
- **Cifras:** M-01, M-02, M-48, M-63, M-64, M-68.

### W · Quién investiga esto (nueva)
- **Qué es:** un mapamundi de puntos, sin proveedor de mapas ni internet, con los 30 grupos de investigación de 15 países que el review *Neural Methods for Amortized Inference* (Zammit-Mangion, Sainsbury-Dale y Huser, 2025) cita como centrales. Recorrido automático: el mundo, Chile, Norteamérica, Europa occidental, Alemania y Austria, los países nórdicos y los autores del review. Arrastrar gira el mapa; pasar por una luz dice qué aportó ese grupo.
- **Por qué:** mostrar que es investigación seria y reciente, y que la industria recién empieza a usarla.
- **Texto:** «Ciencia de la última década. La industria recién empieza.» y «Detrás de amortized inference hay 30 grupos de investigación de 15 países. De los 23 trabajos que los ponen en este mapa, 19 son de 2016 en adelante.»
- **Ojo:** se pidió «la ciencia es de esta década», pero hay trabajos de 2012 a 2018 en la lista: quedó «de la última década». «La industria recién empieza» es una lectura nuestra, no una medición. La lista no es exhaustiva; la fuente de cada grupo está en `datos/generar_laboratorios.py`. Hay un grupo chileno: la Universidad Técnica Federico Santa María (Cranmer, Pavez y Louppe, 2015).
- **Cifras:** M-69.

### A · ¿Qué archivo recibe? y M · Intervalo de credibilidad
- Se borraron. Están en `original/`.

## Lo que queda pendiente

- **El guion** (`pitch/PITCH_v2.md`, `pitch/GUION.md`, `pitch/LAMINAS.md`) es anterior a esta iteración. Las notas de cada lámina (tecla N) sí están al día. Los tiempos de `config.js` son una propuesta para tres minutos: falta cronometrarlos.
- **Sin probar:** el proyector, Safari y la tecla D.
