# Krylov · deck de venta

**Krylov, el Artificial Data Scientist de la minería.** El mensaje del deck: decidir con el mejor modelo ya no toma horas ni un especialista; toma lo que demora subir un archivo, gracias a Bayesian Amortized Inference.

Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional. El guion (dos minutos de relato y uno de demo) está en [`../PITCH_FINAL.md`](../PITCH_FINAL.md).

## Cómo abrirlo

Doble clic en `index.html` **desde el Finder**, o `open pitch/deck/index.html` en la terminal: se abre en el navegador. Después, `F` para pantalla completa.

**No sirve abrirlo desde una vista previa que solo carga el HTML** (por ejemplo, haciendo clic en el archivo dentro de la app de Claude): ahí no llegan ni el código ni los estilos, y la página lo avisa arriba. Para verlo dentro de un panel así hay que servir la carpeta: `python3 -m http.server 8765 --directory pitch/deck` y abrir `http://localhost:8765/`.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. En el cierre no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `Fin` | Va al cierre (lámina 14) |
| `Q` `L` `0` `W` | Las láminas de preguntas, fuera del recorrido: **Q**uién lo usa, por qué no un **L**LM, cómo funciona (**0**, tres pasos) y quién investiga esto en el mundo (**W**). Entre ellas se avanza con las flechas |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y qué hay detrás de cada lámina |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En la lámina 7, arrastrar gira el terreno y un clic sobre él manda el foco a ese punto. En la 12, arrastrar gira el rajo. En la W, arrastrar gira el mapa y pasar por una luz dice qué aportó ese grupo |

En la dirección: `#7` abre la lámina 7, `#7.1` su segundo paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final y `?animado` fuerza el movimiento. Con «reducir movimiento» activado en el sistema, el deck abre sin animaciones.

## Las láminas

Catorce en el recorrido (18 pulsaciones hasta el cierre), más cuatro fuera de él. Qué cambió en cada lámina y por qué está en [`CAMBIOS.md`](CAMBIOS.md). Hay dos respaldos para devolver una lámina a como estaba: [`antes_pasada_final/`](antes_pasada_final/RESPALDO.md) (el deck del sábado a la medianoche) y [`original/`](original/RESPALDO.md) (el del sábado a las 22:40).

| # | Lámina | Qué se ve, y para qué está cada cosa | De dónde sale |
|---|---|---|---|
| 1 | Portada | El nombre, qué es y una frase. Un rajo abierto como maqueta topográfica, con el suelo que sigue hasta los bordes; una onda de luz sale del fondo y enciende las curvas de nivel | Una ilustración hecha con una fórmula (`js/portada.js`): no es ninguna minera ni representa datos |
| 2 | Generative AI para datasets | Un LLM (entra una pregunta, sale la respuesta) y Krylov (entra un dataset, sale la decisión). Ninguno se vuelve a entrenar para responder | Los datasets y mapas de la fila de Krylov son respuestas reales de la red. La pregunta y la respuesta del LLM son un guiño a la sala, escrito a mano |
| 3 | Antes y hoy | Dos carriles, **sin tiempos**. «Antes»: cada dataset pasa por elegir, entrenar e inferir. Al avanzar, las cajas bajan: elegir, simular y pre-entrenar quedan «una sola vez», «inferir» se encoge hasta ser la red, y los datasets la cruzan de corrido | Los contadores cuentan lo que la animación muestra: no son una medición (`js/flujo.js`) |
| 4 | Simulaciones | El remolino de terrenos y la suma de las simulaciones de los cinco modelos con sello, con su desglose y el tiempo total de pre-entrenamiento | M-01, M-48 y M-66 (`js/mundos.js` suma lo que trae `datos.js`) |
| 5 | Entra un archivo, sale la respuesta | Un archivo tras otro entra a la red y sale su mapa; dos contadores | 10 ms: `latencia_ms` del sello. 117 segundos: el método lento por análisis en ese mismo modelo (M-25) |
| 6 | Seis decisiones | «Una minera se pregunta esto todos los días»: las seis preguntas, con una figura cada una | Las figuras son ilustraciones |
| 7 | Qué roca conviene procesar | El terreno en tres colores. **Un punto lo recorre** y, a la izquierda, la tarjeta muestra lo que la red respondió para el lugar que tiene debajo: la decisión, el arsénico estimado, su intervalo de 90% y la distribución entera contra el máximo que acepta la planta (`js/foco.js`). Segundo paso, «¿Dónde perforo?»: Krylov ensaya el pozo en 40 lugares, con 12 resultados posibles en cada uno, rehace el mapa las 480 veces y muestra los tres lugares donde perforar deja menos terreno en duda | La red del motor `espacial`. M-40, M-43, M-44, M-46 (el valor ya no se muestra en dólares) |
| 8 | La pared | La pared en el color de la decisión de cada sector. El foco viaja de sector en sector; en uno que conviene cerrar, la cámara se acerca y **ese tramo cede, rotulado como proyección**. En uno que se movió sin acelerarse, la tarjeta muestra lo que midió el radar | La red del motor `deformacion` (sello a las 17:36) |
| 9 | El cobre en la planta | Las ocho líneas vistas desde donde termina la pulpa: lo recuperado sube por una columna hasta su estimación, contra la meta; **lo que no flotó cae al relave**, más denso donde se pierde más | La red del motor `cinetica` (`js/flotacion.js`) |
| 10 | Los camiones | Los camiones en la rampa, en el color de su decisión. El foco salta entre los que están a la vista y su tarjeta muestra el riesgo de cada uno | La red del motor `desgaste` |
| 11 | Los túneles | Un bloque de roca abierto a la altura de los túneles: la explosión manda una onda por la roca y después cada temblor del archivo sacude su sector a su hora | La red del motor `sismico` (`js/sismicidad.js`). Dónde cae cada temblor dentro del sector es ilustración |
| 12 | ¿Dónde está el mineral? | El sexto modelo, en cuatro pasos: el rajo con la zona perforada; el mineral debajo, piso por piso; una perforación que se recorre hacia abajo, con la tarjeta de las otras decisiones (cobre estimado, rango de 90% y decisión, que pasa de «Mineral» a «Estéril» y a «No se sabe»); y el examen (94 de cada 100 donde se pronunció, «no se sabe» en dos de cada tres bloques). Es `yacimiento.html` dentro de un marco | La red del motor `yacimiento` sobre un yacimiento simulado (M-63, M-64). **No está en la app y su sello no pasa: se cuenta el mapa. La pantalla ya no lo rotula: está en las notas** |
| 13 | ¿Y cómo sé que acierta? | Por modelo, en 2.000 casos nuevos: qué fracción de las veces la respuesta real cayó dentro del rango de 90%. Los seis puntos caen sobre la línea de 90%. Abajo, el examen con datos reales públicos | `cobertura_90` de cada sello; M-63 para el yacimiento; M-67 |
| 14 | Cierre | El mensaje de venta; un contador de los análisis que Krylov habría respondido mientras duró el pitch; el QR | El contador es una cuenta: segundos desde la primera pulsación ÷ 10 ms |

Fuera del recorrido:

| Tecla | Lámina | Qué responde | De dónde sale |
|---|---|---|---|
| `Q` | ¿Quién lo usa? | Quien toma la decisión en terreno: las seis figuras, cada una con el cargo que toma esa decisión | Cargos, no empresas. No hay clientes ni pilotos |
| `L` | ¿Y un LLM? | «Correría el modelo caro cada vez». Una cadena de MCMC arma la respuesta de a una muestra; Krylov la entrega entera | Los dos tiempos salen de la prueba de `datos/prueba_llm/` y del sello. Las nubes son una ilustración. El detalle de la prueba ya no está en pantalla: está en las notas |
| `0` | Cómo funciona | Tres pasos: lo que se hace una sola vez; lo que pasa con cada dataset; y la ficha de los seis modelos (qué modelo es, simulaciones, minutos, milisegundos) | `js/arquitectura.js`; M-01, M-02, M-48, M-63, M-64, M-68 |
| `W` | Quién investiga esto | Un mapamundi de puntos con 31 grupos de 18 países que publican amortized Bayesian inference, en un recorrido automático por regiones. Cada grupo está por un trabajo de 2020 en adelante que lo dice en su título o en su resumen | `datos/laboratorios.js`, que escribe `datos/generar_laboratorios.py` con la frase literal y la fuente de cada grupo; M-69 |

**Una lámina de decisión entra al recorrido solo si el motor de su caso ya responde**, igual que el inicio de la app. Lo decide `js/nucleo.js` al abrir, mirando `datos.js`. La excepción es la lámina 12: está en el recorrido a pedido del equipo, con su aviso en pantalla («Este modelo todavía no está en la app»).

**Las seis láminas de decisión tienen la misma columna: la pregunta y la tarjeta del foco.** Un punto viaja por la escena y la tarjeta muestra la respuesta de la red para la unidad que se está mirando: la decisión en su color, la estimación, su intervalo de 90% y la distribución entera contra el límite con que se decide. Al viajar, la curva y las cifras pasan de una unidad a la otra. Todo sale de `datos.js` (`js/foco.js`); ya no hay gráfico de barras ni cuenta de colores ni cifras de plata en esas láminas.

## Cómo decide Krylov que no sabe

Es la pregunta que el deck provoca en casi todas sus láminas, así que conviene tener la respuesta a mano.

La red no entrega un número: para cada bloque, sector, línea o camión entrega todos los valores que calzan con los datos y qué tan probable es cada uno (la curva de cada tarjeta). Cada decisión tiene un límite. Con las dos cosas se calcula la probabilidad de equivocarse con la decisión que se tomaría, y **si esa probabilidad pasa de 10%, la respuesta es «no sabemos»**. Es una regla fija del producto (`UMBRAL_DE_DUDA` en `nucleo/decision.py`; `contratos/CONTRATO.md`, sección 3) y es la misma en las seis láminas de decisión, incluida la tarjeta de la 12. La red no la aprende.

Lo que la red sí aprende es el ancho de cada rango, y eso es lo que examina la lámina 13. El rango sale ancho con pocos datos cerca, con mediciones ruidosas o cuando el valor está pegado al límite.

En la app hay un segundo «no sé» que el deck no muestra: el semáforo rojo, cuando el archivo trae muy pocos datos, más de los que la red practicó, o viene en otra escala. Es lo que muestra la demo con el archivo de 12 muestras (`../PITCH_FINAL.md`).

## Lo que hay detrás, y que la pantalla no dice

A pedido, la pantalla no lleva pies ni rótulos («simulado», «ilustración», «medido en…», «hoja de ruta»), ni la lámina de «sabe cuando no sabe», y el deck habla de las cinco decisiones como producto. **En ninguna lámina se afirma que los datos sean de una mina real ni se muestran resultados inventados.** Lo que sigue es lo que quien presenta tiene que saber para responder con la verdad si le preguntan; está también en las notas de cada lámina (tecla `N`).

1. **Las cinco decisiones muestran la respuesta de su red, las cinco con sello:** `leyes` (motor `espacial`), `flotacion` (`cinetica`, 17:09), `taludes` (`deformacion`, 17:36, con el criterio de D-39), `sismicidad` (`sismico`, 18:15) y `flota` (`desgaste`, 19:35). Ninguna de las cuatro nuevas está comparada todavía con el método lento. **La lámina de los camiones volvió al recorrido sin frase en el guion ni tiempo en `config.js`:** quien presenta decide si la dice. `generar.py` usa la red de un motor apenas existe su `codificador.onnx` y guarda `sello_pasa` en `datos.js`.
1b. **En la pared, un dato que se puede decir:** en ese archivo simulado, los 5 sectores que la red manda cerrar son los 5 que cedían según la verdad escondida, y el que más se movió (Sector 25, 24 mm) no cede. Es un archivo y es simulado.
2. **Todos los archivos de demo son simulados** (`origen_datos` de cada caso lo dice, y la app lo muestra). El único examen con datos reales es el del motor espacial en el terreno público del río Mosa: 24 de 31 mediciones escondidas dentro del rango (M-13, 77%).
2b. **Los «datos reales públicos» de la lámina 13 son el conjunto `meuse`:** 155 muestras de suelo con metales pesados (se usa el zinc), tomadas junto al río Mosa, cerca de Stein, en los Países Bajos (Rikken y Van Rijn, 1993; Burrough y McDonnell, 1998). Viene con el paquete `sp` de R, con licencia GPL; en el repositorio es `datos/demo/terreno.csv` (D-04). **No es de una mina:** es un terreno contaminado, el mismo tipo de problema que la roca. El examen escondió las mediciones de a un quinto, cinco veces: 138 de 155 dentro del rango de 90% (M-67).
2c. **La lámina 12 ya no dice en pantalla que el yacimiento es simulado ni que el modelo no está en la app.** Las dos cosas siguen siendo ciertas. «La respuesta correcta de este yacimiento» existe porque es simulado. Tampoco muestra tiempos: 18 a 22 ms con la red y 913 segundos con el método lento, con la misma decisión en 92% de los bloques (M-64, M-65).
3. **Las 7 horas son una multiplicación:** 228 análisis × 117,1 s (M-10, M-25). Nadie las corrió seguidas. Y se midieron en el terreno real, no en el banco del demo. Son las láminas 3 y 5, y en las dos se dice lo mismo: 228 análisis, a 2 minutos cada uno.
4. **Los mapas de las láminas 2, 3, 5 y 14 se repiten:** son 32, guardados; el deck los anima, no los calcula. **Y hay contadores que no son mediciones:** los dos de la lámina 3 cuentan lo que la animación muestra (una vuelta, un dataset), y el del cierre es una cuenta (segundos del pitch ÷ 10 ms).
4b. **La lámina 2 es una analogía.** Krylov no es un modelo de lenguaje: se parece a un LLM en que se entrena antes, una vez, y después solo se usa. Y responde datasets de la familia con que practicó; fuera de ella, avisa y no responde. En la lámina 3, «una sola vez» fueron 4 h 40 min de pre-entrenamiento (M-02): no está en pantalla, y hay que saberlo. El punto de equilibrio (unos 144 datasets) es M-36, todavía pendiente en `CIFRAS.md`: no se dice como cifra.
5. **Los costos y los límites son supuestos del demo, y por eso la plata salió de la pantalla.** El motor da US$ 1.577.707, 78.574, 8.809 y 40.664 de «lo que cuesta no saber», y US$ 8.943, 8.376 y 7.966 para los tres lugares de «¿Dónde perforo?»: todos dependen de los costos K-22 en adelante, que son supuestos. En la lámina 7 los tres lugares se comparan entre sí (100, 94 y 89, con A = 100); si preguntan por la plata, se dice con el supuesto por delante. El máximo de arsénico (500 ppm, K-21: «supuesto, no una norma») va sin número; la meta de la planta (84%, K-41) y las 12 horas de la pared (el horizonte del caso) sí se dicen, porque sin ellas no se leen los intervalos.
5b. **Los «117 segundos» de la lámina 5 no son inventados:** es lo que tardó el método lento (MCMC) por análisis en el modelo del terreno, medido en 6 terrenos (`mcmc_s_por_dataset` del sello, M-25). La lámina 3 ya no lleva tiempos.
6. **En las escenas 8 a 11 el movimiento está exagerado para que se vea** (24 milímetros no se ven en una pared), y la forma de la pared, del rajo y de los túneles es una ilustración: lo que viene del archivo es cuánto, cuándo y en qué unidad.
6b. **La lámina del LLM dice «correría el modelo caro», y eso es lo que cuesta dar la posteriori completa; en la prueba, el LLM ni siquiera llegó a correrlo:** con 3 minutos tuvo que conformarse con atajos. Las dos nubes de esa lámina son una ilustración (la de la izquierda es una cadena de Metropolis de verdad, corrida en el navegador, sobre una posteriori inventada para el dibujo). **La prueba con el LLM no dio «el LLM no sirve».** Claude Fable 5.2 acertó parecido a Krylov (61 y 63 de 68 dentro del rango, contra 61). Lo que la prueba sí mostró: 152 y 177 segundos contra 10 ms; dos corridas, dos programas distintos, con diferencias de hasta 459 ppm en un lugar; y ningún sello. «Unas 20 horas» y «15.000 veces» son cuentas. Es una prueba, dos corridas, un archivo simulado, con el computador cargado. **No se dice que un LLM responde mal**: no es lo que se midió, y cualquiera puede repetirlo.
6c. **Los intervalos son de 90%, no de 95%.** El motor entrega los cuantiles 5% y 95% de la posteriori y es con 90% que se validó (0,90 de acierto en 2.000 casos). Pasar a 95% exige recalcular y volver a validar; mientras tanto, el deck dice 90%. Y en la medida de los intervalos **lo ideal es 0,90 y no 1**: un rango que acierta siempre es demasiado ancho. Y con datos reales hay dos números: 138 de 155 escondiendo de a un quinto (el del sello, en pantalla) y 24 de 31 en la partición que muestra la app (M-13, 0,77).
6d. **La lámina 13 ya no muestra la accuracy de las decisiones** (tres modelos en 1,00 sobre muy pocos casos se veían inventados): muestra la cobertura del rango de 90% en los 2.000 casos de cada sello. **Si preguntan por la accuracy, es la de las decisiones y excluye las «no sabemos»:** la roca, 700 de 715 (M-54); la pared, 34 de 34; la planta, 5 de 5; los camiones, 36 de 39; los túneles, 4 de 4 (M-56). **La pared, la planta y los túneles son muy pocos casos, de un solo archivo simulado:** un 1,00 sobre 5 decisiones no es una garantía. La validación robusta está en cada sello (2.000 casos nuevos por red). Si se dice «acierta», se dice «cuando decidió, en estos archivos».
6e. **La lámina 8 proyecta cómo cede un sector, y lo rotula «Proyección».** Es una ilustración de lo que significa «le quedan 4,9 horas»: la forma del derrumbe no sale del modelo. **El viaje del foco entre unidades mezcla dos curvas para la transición:** lo que se lee cuando el punto se detiene es la respuesta de la red para esa unidad. En la lámina 7 no hay mezcla: en cada cuadro se dibuja el bloque que el punto tiene debajo.
6f. **En producción no hay historial ni alertas:** el control es por respuesta (semáforo y examen). Un tablero que los siga en el tiempo es hoja de ruta.
7. **En la pared y en los túneles, Krylov apoya la decisión de un especialista** (regla 22 de `AGENTS.md`): no se promete seguridad.

Esto se aparta de las reglas 9 y 17 de `AGENTS.md` y de D-37, que piden rotular en pantalla lo simulado y separar lo construido de lo que es lámina. El repositorio es público y la app sí lo rotula: si el jurado mira las dos cosas, las va a ver distintas.

## Las palabras

El deck se escribe para alguien que nunca pisó una faena. La operación se llama «la minera» (no «la mina»), y lo físico, por su nombre: «el rajo», «la pared», «los túneles». «La pared» y no «talud»; «explosión» y no «tronadura»; «líneas de estanques» y no «celdas»; «partes del terreno» y no «bloques»; «Sector 25» y no «S-25»; «Camión 05» y no «CAEX-05». Los nombres se traducen al dibujar (`nombre()` en `js/decisiones.js`); los archivos de cada caso no se tocan.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`:** la demo real del producto. De ahí salen el QR del cierre, el texto a su lado y lo que abre la tecla `D`.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5».
- **`tiempos`:** los segundos de cada lámina que muestran las notas. Son los del guion final (`../PITCH_FINAL.md`), contados a 150 palabras por minuto: falta cronometrarlos en un ensayo.
- **`cifras`:** las tres que no salen de `datos.js`: los segundos de «¿Dónde perforo?» (M-44) y la ficha y la cobertura del yacimiento (M-63, M-64), porque su archivo de datos solo se carga en su lámina.

## La entrada por pasos

Lo que aparece por pasos (`data-paso`) entra con un fundido de 0,4 segundos; solo los títulos suben 12 px. Los retardos entre pasos (`--d` en el HTML) conservan su orden y se acortan en la misma proporción, con un tope de 1,2 segundos. Todo sale de siete tokens de `:root` en `deck.css`. Para volver a la entrada anterior (subir 26 px, desenfocada) basta cambiarlos: `--dur-entrada: .7s`, `--sube-titulo: 26px`, `--sube-cuerpo: 26px`, `--desenfoque-entrada: 6px`, `--escala-retardo: 1` y `--tope-retardo: 9s` (la curva, `--curva-entrada`, es la misma de antes; la posición usaba 0,9 segundos y con los tokens queda en 0,7).

## Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Con `--series` rehace solo los cuatro casos de lista (y la posteriori de cada unidad, que dibujan las tarjetas) y deja el resto de `datos.js` como estaba: no usa `torch` ni vuelve a medir tiempos.

Escribe `datos/datos.js`, todo con `KRYLOV_MOTOR_ESPACIAL=red`: el caso estrella (`CASO = "leyes"`), el terreno real (`REAL = "terreno"`), los cuatro casos de series (`SERIES`), 32 bancos con la respuesta de la red para las láminas 2, 5 y 13, los terrenos del simulador, el examen del archivo muestra por muestra (`examen_puntos`), las primeras filas de dos archivos de demo (`archivos`) y, si existe, el resultado de la prueba con el LLM (`prueba_llm`). Los rótulos, límites y costos se leen de la API y de los archivos de cada caso. (También escribe el archivo que no alcanza y los casos de práctica, que el deck ya no usa.)

**Hay que volver a correrlo cada vez que un motor nuevo empiece a responder**, y después rehacer el respaldo.

## Respaldo estático

`respaldo/01.jpg` a `18.jpg` (1920×1080, el estado final de cada lámina, en el orden en que quedan al abrir: 01 a 14 el recorrido, 15 a 18 las preguntas Q, L, 0 y W; rehechas el domingo 22-nov a las 02:40, abriendo el deck por `file://`). Si el navegador no tiene WebGL, cada lámina con 3D muestra la imagen de su posición: **si cambia qué motores responden, hay que rehacer el respaldo**, porque el orden cambia y `respaldo/krylov-deck.pdf`. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Qué se probó y qué no

- **Probado el domingo 22-nov entre las 00:45 y las 02:45, en la pasada final** (Chrome 156 manejado con `playwright-core`, 1280×720 y 1920×1080; el Playwright MCP estaba tomado por otra sesión): las láminas que cambiaron (2, 7, 12, L y W) y todos sus pasos, y el recorrido completo, sin errores de consola. En la lámina 12, las seis transiciones entre pasos se midieron cuadro a cuadro: 16,7 ms de mediana y de percentil 95, sin cuadros perdidos. Esa lámina pasó además por el revisor de movimiento de Impeccable en tiras de cuadros: confirmó que el tirón del primer paso desapareció y dio cinco ajustes, los cinco aplicados. El mapa de la lámina W se miró en sus siete paradas. **Sin probar en esta pasada:** el proyector, Safari y la tecla `D`.

- **Probado el sábado 21-nov entre las 22:45 y la medianoche, en la última iteración de diseño** (Playwright MCP con Chrome, 1280×720 y 1920×1080, con `?animado` y con `?quieto`): las 18 láminas y todos sus pasos, sin errores ni avisos de consola y a 60 cuadros por segundo según el contador del deck; el detector de Impeccable sin hallazgos sobre `index.html`, `deck.css`, `laboratorios.css` y `yacimiento.html`; y ninguna regla de estilo sin uso. Las animaciones de las láminas 1, 3, 4, 7 a 12 y W se revisaron en tiras de cuadros con el revisor de movimiento de Impeccable, en dos rondas: 15 arreglos en la primera (13 resueltos y 2 parciales en su veredicto) y 5 retoques después, comprobados en capturas propias. Con `?quieto`, dos capturas separadas por 1,2 segundos salen idénticas en las láminas 8 y 10. **Sin probar en esta iteración:** el proyector, Safari, la tecla `D` y el respaldo sin WebGL.

- **Probado** (sáb 21-nov, 18:15, MacBook Air M3 con dos entrenamientos corriendo, Chromium sin ventana y el panel de navegador de la app de Claude): las 18 láminas y sus 20 pasos a 1920×1080 en modo estático, y el recorrido completo con el teclado (14 pulsaciones hasta el cierre), sin errores de consola y a 60 cuadros por segundo; las teclas, incluidas `Q`, `A`, `L`, `M`, `0` y `Fin`; la pausa. Dos revisiones automáticas, en todas las láminas y pasos: que ninguna cifra quede partida en dos líneas y que ningún texto quede encima de otro ni se salga del cuadro.
- **Probado también en un navegador con ventana** (el panel de la app de Claude, pantalla de alta densidad, con dos entrenamientos corriendo): 60 cuadros por segundo. **Ahí apareció un error que las capturas sin ventana no mostraban:** las cuatro escenas de las láminas 8 a 11 no se pintaban, porque sus puntos sumaban luz sin opacidad (un color que no es válido, y que ese navegador descarta). Se corrigió (`js/decisiones.js`: la opacidad de cada punto es la de su canal más fuerte) y se comprobó en ese mismo panel.
- **Las escenas se miraron además como se ven en una pantalla de alta densidad** (el doble de píxeles): ahí los camiones anteriores, dibujados con contornos, eran un enredo punteado, y las líneas de un píxel de los estanques y los túneles casi no se veían. Por eso los camiones se rehicieron macizos y todos los contornos se dibujan ahora con puntos seguidos (`cordon` en `js/decisiones.js`).
- **La revisión de textos superpuestos se corre además con las letras más separadas**, para simular un navegador que corta las líneas en otro lugar (así apareció el solape de la lámina 7 que no se veía en las capturas), y revisa que ningún texto se salga del cuadro. Las columnas de texto ahora fluyen: lo que viene después nunca queda debajo.
- **Lo que la revisión automática no mira:** el texto dibujado dentro de un lienzo (las barras de las láminas 1 y 3, las filas de la 2, la curva de la 8, el gráfico de la 12). Eso se revisó a ojo, en capturas.
- **Probado otra vez el sábado 21-nov entre las 20:40 y las 21:05, después de aplicar la auditoría del deck** (Chrome 156 con `playwright-core`, con ventana para el recorrido y sin ventana para las capturas): el recorrido completo con el teclado (14 pulsaciones hasta el cierre), las teclas `P`, `C`, `Q`, `A`, `L`, `M`, `0`, `N` y `Fin`, y un clic en el terreno de la lámina 7, a 60 cuadros por segundo; las 18 láminas y sus 20 pasos a 1920 y a 1280, con «reducir movimiento» y en modo estático. Ningún texto queda fuera del cuadro, ninguna tarjeta queda encima de una etiqueta ni de la columna, y con la pausa o con «reducir movimiento» nada sigue cambiando. El único error de consola que apareció (una vez cada tanto, en la lámina 2, por el reloj del primer cuadro) quedó corregido en `js/nucleo.js`: 144 cargas seguidas sin errores. La tecla `C` ya no abre nada, porque los camiones están en el recorrido.
- **Sin probar:** la tecla `D`, Safari, el proyector del lugar, un control de presentaciones real, y el deck en una pantalla de verdad con el entrenamiento corriendo (las capturas dan 60 cuadros por segundo, pero sin ventana).
- **Si el navegador no tiene WebGL**, las láminas con 3D muestran su imagen de `respaldo/`.

## Bibliotecas y tipografías (todas locales, en `vendor/`)

| Archivo | Qué es | Licencia |
|---|---|---|
| `three.min.js` | three.js r149, para el 3D | MIT (`three.LICENSE`) |
| `gsap.min.js` | GSAP 3.15.1, para las líneas de tiempo | Licencia estándar sin costo de GreenSock (gsap.com/standard-license) |
| `qrcode.js` | qrcode-generator 2.0.4, dibuja el QR en el navegador | MIT (en la cabecera del archivo) |
| `big-shoulders-display-*.woff2` | Titulares y cifras | SIL Open Font License 1.1 |
| `instrument-sans-*.woff2` | Texto | SIL Open Font License 1.1 |
| `jetbrains-mono-*.woff2` | Datos | SIL Open Font License 1.1 |
| `archivo-*.woff2` | La tipografía de la app; el deck ya no la usa | SIL Open Font License 1.1 |

## Pedidos a otros

- **A `amortizacion` (PC 2):** avisar cuando `deformacion`, `cinetica`, `desgaste` o `sismico` respondan en `api.analizar`, para regenerar `datos.js` y el respaldo.
- **A `seguimiento`:** el guion vigente es `PITCH_FINAL.md`. `GUION.md`, `LAMINAS.md` y `PITCH_v2.md` describen decks anteriores: conviene borrarlos o rotularlos. Las cifras del deck que no tenían fila en `CIFRAS.md` se registraron el sábado a las 20:35, y conviene que una persona las firme: los 10 milisegundos (M-26), la prueba con el LLM (M-15), el acierto de cada modelo (M-56), los intervalos de la lámina de la tecla M y su «7 de 8» (M-57) y las cinco tarjetas de las láminas 7 a 11 (M-58 a M-62). Los gráficos de intervalos de las láminas 8 a 11 ya no escriben sus valores.
- **A `producto` (PC 1):** si cambia la dirección del producto, avisar para `config.js`.
- **A una persona del equipo:** confirmar los nombres del cierre; abrir el deck en Safari y con el proyector antes del ensayo.
