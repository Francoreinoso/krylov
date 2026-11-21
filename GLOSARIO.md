# Glosario de Krylov

Las palabras del proyecto, en una o dos líneas cada una. Se usan igual en todos los archivos, en la pantalla y en el pitch. Si un término no está aquí, no se usa sin explicarlo. Este glosario manda en la pantalla y en el pitch; en el código, en `STACK.md`, en el anexo técnico y en el README técnico se usan los nombres técnicos precisos (última tabla).

**No sabemos quién evalúa.** Toda frase tiene que entenderla alguien de tecnología que nunca pisó una mina ni estudió estadística. Por eso hay dos listas de palabras que se explican siempre: las del producto y las de la minería.

## El producto

- **Krylov.** El nombre del producto y de la empresa. Viene de Alekséi Krylov, ingeniero naval que calculó por adelantado qué hacer con un barco averiado para que el capitán decidiera en segundos. El relato, con su fuente, está en `pitch/GUION.md`.
- **Data scientist artificial.** Programa que hace el trabajo de un analista de datos: elige el método, lo aplica, dice qué conviene hacer, cuánto se puede equivocar y cuándo los datos no sirven. Krylov lo es para las decisiones de una mina.
- **Decisión operacional.** Una decisión que la mina toma muchas veces al día o a la semana, contra el reloj: a dónde va un bloque de roca, si se evacúa un sector, qué camión se detiene. Krylov resuelve cinco.
- **Modelo avanzado.** Modelo que, además de predecir, dice cuánto se puede equivocar. Hoy exige un especialista y horas de cálculo.
- **Simular.** Inventar datos con reglas conocidas. Krylov practica con millones de casos simulados, donde la respuesta correcta se conoce, antes de ver datos reales.
- **Modelo generativo.** Las reglas con que Krylov inventa minas para practicar: cómo varía la ley de la roca, cómo se desgasta un camión, cómo se mueve un muro antes de ceder, incluido el error de cada medición. Cada motor tiene las suyas. En pantalla se dice «las reglas».
- **El método lento de siempre.** La forma en que un especialista resuelve hoy estos modelos: correcta, y de minutos u horas por análisis. Krylov la usa para comprobar sus redes y como respaldo. En el código se llama MCMC.
- **El método rápido de siempre.** Lo que se usa en faena cuando no hay tiempo: un promedio, una regla fija, una recta. Es la comparación: muestra qué se pierde sin el modelo completo.
- **Precalculado.** Rótulo de una respuesta que no salió de la red sino del método lento, calculado antes. Una tarjeta rotulada así no se presenta como respuesta al instante.
- **Amortizar.** Pagar el costo de cálculo una sola vez, por adelantado, entrenando una red con casos simulados, para que después cada respuesta sea instantánea.
- **Motor.** Un modelo avanzado con sus reglas para inventar casos y una red que practicó con ellos, listo para responder al instante. Hay cinco, uno por decisión:
  - `espacial` (leyes y arsénico): datos con ubicación; qué bloques superan un límite y dónde conviene muestrear.
  - `deformacion` (taludes y relaves): cuánto se mueve cada sector de un muro y si se está acelerando.
  - `cinetica` (flotación): qué tan rápido y cuánto cobre se recupera en cada línea de la planta.
  - `desgaste` (flota): cuánto desgaste lleva cada camión, que no se ve pero deja huella en lo que se mide.
  - `sismico` (sismicidad): cada sismo chico sube por un rato la probabilidad del siguiente.
- **Red.** El programa que aprendió, mirando solo casos simulados, a dar para un archivo entero la misma respuesta que el método lento de siempre, en milisegundos.
- **Ronda de entrenamiento.** El rato (unos 100 minutos) en que una red practica en uno de los dos MacBook. Hay dos rondas después del pivote.

## Minería en simple

Cada palabra de esta lista se explica **la primera vez que aparece** en pantalla, en una lámina o en el pitch, con la frase de la derecha o una más corta. Después se puede usar sola.

| Palabra | Cómo se explica |
|---|---|
| **Rajo abierto** | Una mina a cielo abierto: un cráter enorme que se excava por pisos |
| **Banco** | Un piso del rajo. Se saca de a un trozo cada vez |
| **Tronadura** | La explosión controlada que rompe la roca para poder cargarla |
| **Pozo de tronadura** | Cada hoyo donde va el explosivo. De cada uno se saca una muestra de roca |
| **Bloque** | Un trozo del banco del tamaño de una casa. Se decide de a un bloque |
| **Ley** | Cuánto cobre trae la roca. Una ley de 0,6% son 6 kilos de cobre por tonelada |
| **Arsénico** | Un elemento tóxico que viene mezclado con el cobre en algunos yacimientos. Si el producto trae mucho, vale menos o no se puede vender |
| **Planta** | Donde la roca se muele y se separa el cobre |
| **Botadero** | Donde se deja la roca que no vale la pena procesar |
| **Concentrado** | El polvo rico en cobre que sale de la planta. Es lo que la mina vende |
| **Castigo** | El descuento que aplica el comprador cuando el concentrado trae impurezas, como el arsénico |
| **Flotación** | La etapa de la planta que separa el cobre con burbujas: el cobre se pega a las burbujas y sube; el resto se hunde |
| **Línea** (o banco de celdas) | Una fila de estanques de flotación por donde va pasando la pulpa. No confundir con el banco del rajo: en pantalla se dice «línea» |
| **Recuperación** | Qué parte del cobre que entró a la planta se logró rescatar. Lo que no, se va al relave |
| **Relave** | El barro que sobra después de sacar el cobre |
| **Tranque de relaves** | El embalse donde se guarda ese barro, contenido por un muro |
| **Talud** | La pared inclinada del rajo |
| **Radar de taludes** | Un radar que mide, cada pocos minutos, cuántos milímetros se movió cada parte de la pared |
| **CAEX** | El camión minero gigante: carga unas 300 toneladas. En pantalla se dice «camión» |
| **Rampa** | El camino por donde los camiones suben la roca desde el fondo del rajo |
| **Mantención programada** | La detención planificada de un equipo para revisarlo. Lo caro es la falla que no estaba planificada |
| **Minería subterránea** | La mina que se explota por túneles, bajo tierra |
| **Sismo inducido** | Un temblor chico que provoca la propia excavación al cambiar las presiones de la roca |
| **Estallido de roca** | Cuando la roca, bajo presión, revienta de golpe dentro del túnel |
| **Sector** | Una zona de la mina (un grupo de túneles, un tramo del muro) que se abre o se cierra como una sola cosa |
| **Reingreso** | Volver a dejar entrar a la gente a un sector después de una tronadura o de un sismo |

No se dice en pantalla ni en el pitch: *ore control*, *blasthole*, *rockburst*, *panel caving*, *rougher*, *RUL*, *GB-InSAR*, *pórfido*. Si alguien del rubro pregunta, se le responde con su palabra.

## Lo que se ve en pantalla

- **Caso de uso** (o «caso»). Una decisión de la mina resuelta con un motor, un archivo de datos y sus costos. Vive en `casos/<nombre>.yaml`. Cada tarjeta del inicio es un caso.
- **Unidad.** Aquello sobre lo que se decide: un bloque de roca, un sector del muro, una línea de la planta, un camión, un sector de la mina.
- **Actuar.** Lo que la mina haría si la respuesta es «sí»: apartar el bloque, cerrar el sector, ajustar la línea, adelantar la mantención, no reingresar. Cada caso le pone su nombre.
- **Costos del caso.** Dos números que pone el usuario con deslizadores: cuánto cuesta actuar cuando no hacía falta y cuánto cuesta no actuar cuando sí hacía falta. Son supuestos del demo y se dicen como supuestos.
- **Punto de corte.** El nivel de riesgo desde el cual conviene actuar. Sale de los dos costos. Si actuar es barato y no actuar es caro, el punto de corte es bajo.
- **Tres colores.** Son decisiones, no pronósticos: «conviene actuar», «no hace falta» y «no sabemos si conviene». Una unidad está en el tercero cuando hay más de 10% de probabilidad de que la decisión cambie al saber más.
- **Lo que te cuesta no saber.** El número grande de la pantalla. Es la plata que se ahorraría, en promedio, si la duda se despejara antes de decidir. Vale cero cuando no hay duda.
- **¿Dónde perforo?** En el caso de leyes: los tres lugares donde una muestra más vale más plata. Para calcularlo, Krylov imagina cientos de resultados posibles y rehace el análisis completo para cada uno. (En el contrato y en el código se llama `donde_medir`; antes del pivote en pantalla decía «¿Dónde mido?».)
- **Curva.** En los casos de lista, el dibujo de una unidad: los puntos medidos y un **abanico** con lo que Krylov cree que viene, más la línea del límite. Un abanico ancho es mucha duda.
- **Límite.** El valor que no se quiere cruzar: el arsénico que la planta acepta, el desgaste con que un camión falla, la recuperación mínima.
- **Horizonte.** Hasta cuándo mira la respuesta: las próximas horas, el resto del turno, hasta la próxima mantención.
- **Qué pesa.** Los factores que mueven la respuesta, cada uno con una etiqueta: seguro, probable, o no se puede saber con estos datos.
- **Examen.** Lo que pasó cuando Krylov respondió sobre datos cuya respuesta estaba escondida: «escondimos 68 muestras y 61 cayeron dentro del rango que dimos». Con datos reales es la exactitud que se dice en voz alta; con datos simulados se dice «con datos simulados».
- **Verdad escondida.** En un archivo simulado, la respuesta correcta que se guardó aparte y que el motor nunca ve. Sirve para el examen.
- **Sello.** La ficha técnica de un motor: con cuántas simulaciones practicó, cuánto acierta en casos simulados nuevos, cuánto se parece al método lento y cuánto tarda cada uno. Va en el pie de la pantalla y en la lámina técnica.
- **Nube.** El dibujo de las simulaciones con que Krylov practicó, con el archivo del usuario encima. Si el archivo cae fuera, Krylov no responde. Se muestra en los motores donde existe.
- **Semáforo.** Verde: responde. Amarillo: responde con un aviso. Rojo: no responde y dice por qué, porque faltan datos o porque el archivo no se parece a nada que conozca.
- **Modo estático.** Las respuestas del demo guardadas como archivos junto a la web. Así la URL pública responde aunque no haya servidor.
- **Chat.** La puerta de entrada de Krylov. Se elige la decisión, se adjunta un archivo y se confirma el calce de las columnas. La respuesta aparece dentro de la conversación.
- **Papel de una columna.** Lo que una columna significa para el modelo: la unidad (qué camión), el tiempo, el valor medido, la ubicación. Cada modelo pide sus papeles.
- **Calce.** Qué columna del archivo va en cada papel del modelo, y con qué transformación (por ejemplo, minutos a horas). Lo propone un modelo de lenguaje leyendo los nombres y un resumen de las columnas, nunca las filas; el usuario lo ve y lo confirma.
- **Interpretación.** El texto corto que acompaña a una respuesta. Lo escribe un modelo de lenguaje leyendo los números del motor y no agrega números propios. Sin conexión, se usa la plantilla.

## El negocio

- **Primer cliente.** A quién se le vendería primero: el área de una faena que toma una de estas decisiones todos los días (geología de corto plazo, geomecánica, mantención, planta). No hay clientes ni pilotos, y no se dice que los haya.
- **Hoja de ruta.** Lo que no está construido. Va siempre rotulado así: los modelos completos del documento técnico, la conexión a sensores, más decisiones.

## El trabajo

- **PC 1, PC 2, PC 3.** Los tres computadores: producto, amortización y seguimiento. Sus instrucciones están en `PC1_PRODUCTO.md`, `PC2_AMORTIZACION.md` y `PC3_SEGUIMIENTO.md`.
- **Pivote.** El cambio del sábado a las 12:10 (decisión D-37): de cuatro tarjetas de industrias distintas a cinco decisiones de una mina.
- **Hito (H4 a H6).** Hora fija en que se mide contra un criterio escrito y se decide seguir o cortar. H0 y H1 son de antes del pivote.
- **Tope de redes.** Sábado 20:30: la última hora en que una red puede reemplazar al «precalculado» de su tarjeta.
- **Ronda.** La revisión que hace PC 3 cada 30 a 45 minutos: baja los cambios, mira qué terminó cada uno, lo verifica, escribe la siguiente tarea de cada rol en el tablero y ajusta el guion. (No confundir con la ronda de entrenamiento.)
- **Producto terminado.** Sábado a las 18:00. Desde ahí no entra nada nuevo: solo se itera el demo y el pitch.
- **Contrato.** El acuerdo sobre qué datos se pasan los tres computadores. Está en `contratos/CONTRATO.md`.
- **Repositorios espejo.** El oficial de la organización y el personal `Silent-math/krylov`, que reciben exactamente los mismos commits con un solo `git push`.
- **Cifra registrada.** Número con fila en `pitch/CIFRAS.md`, clasificado como medido, con fuente o hipótesis. Lo que no está ahí no se muestra.

## Qué se dice en vez de la jerga

| Término técnico | En pantalla y en el pitch |
|---|---|
| Posterior, intervalo de credibilidad | «Rango creíble», «lo que de verdad sabemos» |
| Valor de la información | «Lo que te cuesta no saber», «cuánto vale averiguarlo» |
| Diseño de experimentos | «¿Dónde perforo?», «dónde conviene medir» |
| Calibración, cobertura | «Cuando dimos un rango, la respuesta cayó adentro 9 de cada 10 veces» |
| Fuera de distribución, fuera del prior | «No se parece a nada que haya visto» |
| Inferencia amortizada | «Ya practicó con millones de minas simuladas» |
| Modelo bayesiano | «Un modelo que dice cuánto se puede equivocar» |
| Modelo generativo, prior | «Las reglas con que Krylov inventa minas» |
| Modelo jerárquico | «Lo que aprende de un camión le sirve para los demás» |
| Latente | «Algo que no se ve en los datos pero deja huella» (el desgaste de un camión) |
| Proceso gaussiano, kriging | «La roca vecina se parece» |
| Proceso de Hawkes | «Cada sismo sube por un rato la probabilidad del siguiente» |
| Proceso gamma | «El desgaste avanza a saltos y nunca retrocede» |
| Cinética de primer orden | «El cobre flota rápido al principio y cada vez más lento» |
| Fluencia terciaria, velocidad inversa | «El muro se mueve cada vez más rápido», «cuánto falta» |
| NPE, flujo normalizador, codificador | No se nombran. «La red que practicó» |
| SBC | No se nombra. «Lo comprobamos en casos simulados nuevos» |
| Umbral de decisión | «Punto de corte» |
| MCMC | «El método lento de siempre» |
| Kriging con parámetros fijos, promedio móvil, regla fija | No se nombran. «El método rápido de siempre» |
| Simulación, simular | Se dicen tal cual: es el nombre del track |
