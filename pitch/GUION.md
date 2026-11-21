# Krylov · Guion del pitch (minería)

> Guion único desde el pivote (D-37, sáb 12:10): sirve para el deck y para la app. Lo mantiene PC 3 (`seguimiento`) y lo pone al día en cada ronda. **Los corchetes son resultados que todavía no se miden.** Cuando una cifra queda registrada en `CIFRAS.md`, el corchete se reemplaza por el número. Si a la hora del ensayo un corchete sigue ahí, la frase se dice sin número. Nunca se inventa.
>
> **Para quién se habla:** no sabemos quién evalúa. Alguien de tecnología que nunca pisó una mina ni estudió estadística tiene que poder repetir la idea. Cada palabra minera se explica la primera vez, en cinco palabras o menos.

## La frase

**«Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo. En un segundo, porque ya practicó con millones de minas simuladas.»**

Versión para el campo de una línea de la entrega: *«El data scientist artificial de la minería: te dice qué conviene hacer, cuánto te cuesta no saber y dónde conviene medir más.»*

## La idea, en tres frases (por si solo hay diez segundos)

1. En una mina las decisiones grandes no esperan, y los modelos que de verdad miden el riesgo tardan horas.
2. Krylov hace ese cálculo antes: practica con millones de minas simuladas, donde la respuesta correcta se conoce.
3. Por eso, cuando llega el dato real, responde en un segundo: qué conviene hacer, cuánto no sabe y dónde medir para saber más.

## Por qué se llama Krylov

Alekséi Krylov fue un ingeniero naval y matemático ruso. A comienzos del 1900 calculó por adelantado, barco por barco, qué le pasaba a la nave si se inundaba cada compartimento, y lo dejó en tablas. Con esa tabla, el capitán de un barco con el casco roto no tenía que calcular nada en medio del desastre: miraba y decidía rápido qué compartimento inundar para enderezar el barco. Sus tablas se usaron en marinas de todo el mundo (cifra N-01).

Es la misma idea del producto: **hacer el cálculo difícil antes, para que la decisión sea inmediata.** Y calza con la minería: ahí también se decide con el reloj encima.

Lo que no se dice: el nombre del barco, fechas exactas ni anécdotas de guerra. Si alguien pregunta por el «subespacio de Krylov» de álgebra: es del mismo Krylov, de 1931. Una frase y se sigue.

## Cómo se cuenta cada decisión

Siempre igual, y nunca con el nombre del modelo: **una escena que cualquiera imagina, el reloj, y lo que cuesta equivocarse.**

| Caso | La escena | El reloj | Lo que cuesta equivocarse | Qué muestra Krylov |
|---|---|---|---|---|
| `leyes` | Un piso de la mina recién roto con explosivos. Hay que decidir, trozo por trozo, si esa roca va a la planta | Antes de que la pala la cargue (I-07) | Si entra roca con demasiado arsénico, el cobre que se vende sale castigado o lo rechazan (I-04, I-05) | El mapa en tres colores, lo que cuesta no saber y **dónde perforar** |
| `taludes` | La pared de la mina se mueve unos milímetros. Un radar la mide cada pocos minutos (I-10) | Minutos | Cerrar un sector sin motivo cuesta un turno; no cerrarlo a tiempo, mucho más | Qué sectores cerrar y **cuánto falta**, con su rango |
| `flotacion` | La planta separa el cobre con burbujas. El mineral cambia sin avisar | Media hora: lo que tarda en pasar por la línea (I-15) | El cobre que no se rescata se va al barro que sobra. Un punto de recuperación vale millones al año (I-14) | Qué líneas van a terminar perdiendo cobre, mirando solo el principio |
| `flota` | Un camión del porte de una casa falla en plena subida | Cada turno | Miles de dólares por hora detenido (I-18), más la reparación de emergencia | Qué camiones no llegan a su próxima mantención |
| `sismicidad` | Bajo tierra, después de una explosión la roca sigue crujiendo. La gente espera afuera | Horas (I-20) | Esperar de más es producción perdida; entrar antes de tiempo es un riesgo que nadie quiere correr | En qué sectores conviene seguir esperando |

## Qué puntúa el jurado y dónde lo mostramos

Criterios oficiales de las bases (cifra J-01).

| Criterio | Peso | Momento del pitch que lo muestra |
|---|---|---|
| Aspecto técnico | 25% | La carrera («228 análisis: más de siete horas contra menos de un segundo»); «rehízo 480 análisis completos»; el examen; la lámina técnica en las preguntas |
| Ambición | 20% | Cinco decisiones de la gran minería; redes entrenadas en dos notebooks; el pivote completo con el producto en línea |
| Ejecución | 20% | Todo es en vivo y sin esperas; el QR abre la app funcionando; cada tarjeta dice quién responde |
| Impacto | 20% | Plata en cada pantalla: lo que cuesta no saber, lo que vale perforar aquí. Una industria, y un caso llevado hasta el final |
| Originalidad | 15% | No es un tablero ni un chat con un archivo: dice cuánto no sabe y dónde medir para saber más |

Consecuencia: el negocio ocupa, a lo más, una frase. No hay criterio que lo premie.

## Versión de tres minutos

**Es la versión principal** (3 minutos en generales y finales, cifra J-04). **Tiempo estimado, no cronometrado:** contado en palabras, a 150 por minuto, son unas 365 palabras, cerca de 2:25 de habla; con los clics, 2:50. El cronómetro de verdad es el primer ensayo (S-26).

`[→]` es una pulsación en el deck; lo que va entre paréntesis es lo que hace la pantalla.

**Momento 1 · El nombre (0:00 a 0:20).** Deck, lámina 1: el barco.

> «A comienzos del 1900, un ingeniero naval, Alekséi Krylov, hizo algo raro: calculó por adelantado qué hacer si el barco se rompía.» `[→]` *(el casco se rompe)* «Con el casco roto no hay tiempo para calcular.» `[→]` *(aparece la tabla; el barco se endereza)* «Pero el cálculo ya estaba hecho, en una tabla: mirar y decidir. Eso mismo hicimos para una mina.»

**Momento 2 · El problema y la carrera (0:20 a 0:45).** Deck, lámina 2.

> «En una mina las decisiones grandes no esperan: a dónde va la roca recién rota, si un sector se cierra, qué camión se detiene. Y los modelos que de verdad miden el riesgo tardan horas.» `[→]` *(parten dos barras)* «El mismo trabajo, 228 análisis. Con el método lento de siempre: más de siete horas. Con Krylov: menos de un segundo.»

**Momento 3 · Cómo (0:45 a 1:00).** Deck, lámina 3.

> «¿Cómo? Antes de ver un solo dato real, practicó con más de siete millones de terrenos simulados, donde la respuesta correcta se conoce. Una noche, en un MacBook Air. El cálculo difícil se paga una vez.»

**Momento 4 · Primera decisión: el banco (1:00 a 1:25).** App, tecla `1` (o deck, lámina 4).

> «Primera decisión. Un piso de la mina, recién roto con explosivos. En cada hoyo se midió cuánto arsénico trae la roca: si entra demasiado a la planta, el cobre se vende castigado. Krylov responde el piso entero, trozo por trozo. Verde: puede ir a la planta. Rojo: conviene apartarlo. Ámbar: no sabemos.» *(mueve un deslizador; los colores cambian)* «Y este número es lo que te cuesta no saber.»

**Momento 5 · ¿Dónde perforo? (1:25 a 1:45).** App, tecla `D`.

> «Entonces, la pregunta que vale plata: si puedo tomar una muestra más, ¿dónde perforo? Para contestar, Krylov imaginó cientos de resultados y rehízo el análisis completo 480 veces, en [X] segundos. Una muestra aquí vale cerca de nueve mil dólares.» *(clic en el pin A y en un resultado)* «Perforo, sale [alto], y el mapa cambia.»

**Momento 6 · Cuatro decisiones más (1:45 a 2:40).** App, teclas `2` a `5`. Unos 13 segundos cada una; en cada tarjeta se abre sola la curva de la unidad con más duda.

> «La misma idea, en cuatro decisiones más.»
>
> `2` «La pared de la mina se mueve; un radar la mide cada pocos minutos. ¿Es ruido o va a ceder? Krylov dice qué sectores cerrar, y cuánto falta. Este abanico es lo que no sabe.»
>
> `3` «La planta separa el cobre con burbujas. Mirando solo el principio de cada línea, dice cuáles van a terminar perdiendo cobre.»
>
> `4` «Cuarenta camiones. Dice cuáles no llegan a su próxima mantención, antes de que fallen en plena subida.»
>
> `5` «Y bajo tierra, después de una explosión la roca sigue crujiendo. Dice en qué sectores conviene esperar antes de que vuelva a entrar la gente.»
>
> *(la verdad sobre quién responde, una sola frase; se elige a las 20:30)* «[Las cuatro responden al instante.]» (si la flota pasa su sello) o «[Estas tres ya responden al instante; los camiones son lo que sigue.]» (lo cierto a las 18:35) o, si alguna salió precalculada, «[esta la calculamos con el método lento de siempre.]» Se dice solo lo que diga el tablero.

**Momento 7 · Cierre (2:40 a 3:00).** Deck, lámina de cierre (tecla `L` en la app).

> «No reemplaza al geólogo ni a quien cuida el muro: les entrega a tiempo el cálculo que hoy llega tarde. Lo construimos con Claude Code y está en línea: escaneen y muevan los costos ustedes. Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo.»

### De dónde sale cada número que se dice

| Se dice | Cifra | Cuidado |
|---|---|---|
| «A comienzos del 1900» | N-01 | Sin fecha exacta, sin nombre de barco |
| «228 análisis», «más de siete horas», «menos de un segundo» | M-08, M-10, M-09 | Se midieron en el terreno real (caso `terreno`), no en el banco. Las siete horas son 228 × 117 s: nadie las corrió seguidas. Si preguntan, se dice así |
| «más de siete millones de terrenos simulados» | M-01 | Son terrenos, no «minas»: la palabra exacta en ese momento es «terrenos» |
| «una noche, en un MacBook Air» | M-02 | 280 minutos |
| «480 veces» | M-43 | |
| «en [X] segundos» | M-44 | Medido sin nada entrenando en PC 3 (MacBook Air M3, sáb 13:27): 1,3 s, cinco corridas entre 1,30 y 1,48. Hasta que se mida en el computador que presenta, se dice «en poco más de un segundo». No se dice «menos de un segundo» para los 480 análisis |
| «cerca de nueve mil dólares» | M-46 | Con los costos por defecto, que son supuestos (K-22 a K-24) |
| «sale [alto]» | — | Se elige en el ensayo el resultado que mejor se ve; con «alto» la duda total subió un poco en la prueba de las 12:05. Probar «bajo» |
| «cuarenta camiones» | D-13 | Flota simulada |
| «cada pocos minutos» | I-10 | |

Lo que **no** se dice en voz alta: ningún nombre de mina ni de empresa; «evita accidentes»; el accidente de El Teniente (I-21); cifras del documento técnico que no están en `CIFRAS.md`; «al instante» sobre una tarjeta que salió precalculada.

## Si una tarjeta salió precalculada o no está (se decide a las 20:30)

De cada tarjeta nueva se dice una de tres cosas, según lo que diga la tabla «Los cinco casos» del tablero.

**Con D-38 (13:10) el método lento va al final**, así que «precalculada» ya no es el punto de partida de ninguna tarjeta: solo queda así la que no pasó su sello y cuyo método lento se adelantó y convergió. Lo esperable a las 18:00 es que `flotacion` y `taludes` respondan con su red, y que `flota` y `sismicidad` (que validan a las 18:15) estén fuera del inicio o precalculadas, según lo que una persona decida a las 17:30; pueden sumarse con su red hasta las 20:30.

| La tarjeta | En pantalla | Se dice |
|---|---|---|
| Responde su red | Sin rótulo | La frase del momento 6, tal cual |
| Salió precalculada | Rótulo «precalculado» | La frase de la decisión, y al final del momento 6: «esta la calculamos con el método lento de siempre; tardó [X]. Es lo que Krylov está aprendiendo a hacer al instante» |
| No está en la app | No aparece | Sale del momento 6. En el cierre: «la misma idea sirve para [la flota, los temblores bajo tierra]: es lo que sigue» |

- **Si las cuatro nuevas salieron precalculadas:** el momento 6 se acorta a dos tarjetas (las que se vean mejor) y la frase final es: «En el piso de la mina, Krylov ya responde al instante. Estas las calculamos con el método lento mientras sus redes terminan de entrenar.»
- **Si ninguna nueva está:** el momento 6 se reemplaza por 20 segundos de la lámina «cinco decisiones», rotulada «hoja de ruta», y el tiempo que sobra va al momento 5 (un segundo clic: otro pin, otro resultado).
- **Nunca se corta** el banco ni «¿Dónde perforo?».

## Versión de 90 segundos

Momento 1 (dos frases: «Krylov calculó por adelantado qué hacer si el barco se rompía. Eso hicimos para una mina»), momento 2 completo, momento 4, momento 5, una frase («la misma idea ya corre para el muro que se mueve, la planta, los camiones y los temblores bajo tierra») y la frase de cierre.

## Preguntas que van a hacer

Las respuestas completas están en `WORKPLAN.md`, sección 5. Las cinco que hay que tener en la punta de la lengua:

- **«¿Son datos reales?»** «No, y la pantalla lo dice: los inventamos con las mismas reglas físicas y escondimos la respuesta. El motor del mapa está probado además con datos reales públicos: escondimos 31 mediciones y 24 cayeron dentro del rango que dio.» (M-13: es 77%, no 90%; se dice tal cual.)
- **«¿Hablaron con alguna minera?»** «Todavía no, y no lo vamos a inventar.»
- **«¿Reemplaza al especialista?»** «No. Le entrega a tiempo lo que el modelo completo diría. La decisión sigue siendo suya.»
- **«¿Qué existe hoy?»** Lo que diga el tablero a las 20:30, tarjeta por tarjeta.
- **«¿No es un chat con un archivo?»** «El chat es la puerta. Cada número sale de un motor que practicó con millones de casos simulados; el modelo de lenguaje solo cuenta el resultado.»

## Si algo falla en vivo

| Falla | Qué se hace |
|---|---|
| No hay internet | Nada cambia: el deck y la app corren en el computador que presenta |
| La app se cae | Los momentos 4 y 5 se hacen en el deck (láminas 4 y 5); el 6, con la lámina «cinco decisiones» |
| «¿Dónde perforo?» tarda más de 2 segundos | Se sirve el resultado precalculado, que está siempre |
| Una tarjeta del momento 6 no carga | Se salta a la siguiente tecla |
| Se acaba el tiempo | Se salta al cierre desde donde se esté. El momento 6 es prescindible; el 4 y el 5 no |

## Corchetes pendientes

| Corchete | Cifra | Quién y cuándo |
|---|---|---|
| Segundos de «¿Dónde perforo?» en el banco, sin nada entrenando | M-44 | Medido en PC 3: 1,3 s. Falta en el computador que presenta (PC 2, A-22, o el ensayo) |
| Qué resultado se elige en el pin A | — | Ensayo, S-26 |
| Quién responde cada tarjeta nueva | M-52 | A las 18:35, con su red: el muro, la planta y los temblores (más el banco). Falta la flota: su red valida después de las 18:15. Se cierra a las 20:30 |
| Cuánto tardó el método lento en una tarjeta precalculada | M-50 | PC 2, sellos |
| Extraños que repiten la idea | M-53 | PC 3, S-29 y 19:00 |
