# Krylov · deck de venta

**Krylov, el Artificial Data Scientist de la minería.** El mensaje del deck: los modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide, gracias a Bayesian Amortized Inference.

Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional. El guion está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html` **desde el Finder**, o `open pitch/deck/index.html` en la terminal: se abre en el navegador. Después, `F` para pantalla completa.

**No sirve abrirlo desde una vista previa que solo carga el HTML** (por ejemplo, haciendo clic en el archivo dentro de la app de Claude): ahí no llegan ni el código ni los estilos, y la página lo avisa arriba. Para verlo dentro de un panel así hay que servir la carpeta: `python3 -m http.server 8765 --directory pitch/deck` y abrir `http://localhost:8765/`.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. En el cierre no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `Fin` | Va al cierre (lámina 13) |
| `0` | Cómo funciona | Bayesian Amortized Inference en dos mitades: solo el diagrama, sin fórmulas ni cifras | `js/arquitectura.js` |
| `Q` `A` `L` `M` | Las láminas de preguntas, fuera del recorrido: **Q**uién lo usa, qué **A**rchivo recibe, por qué no un **L**LM, qué pasa en producción (**M**onitoreo). Entre ellas se avanza con las flechas |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y qué hay detrás de cada lámina |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En la lámina 7, arrastrar gira el terreno |

En la dirección: `#7` abre la lámina 7, `#7.1` su segundo paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final y `?animado` fuerza el movimiento. Con «reducir movimiento» activado en el sistema, el deck abre sin animaciones.

## Las láminas

Son trece en el recorrido (catorce pulsaciones), más cinco fuera de él para las preguntas.

**Las láminas 7 a 11 tienen la misma columna de texto: lo que Krylov entrega.** Primero el gráfico de intervalos de credibilidad (una barra por unidad: `js/intervalos.js`), después cuántas unidades hay en cada color, y el valor. El gráfico y los números aparecen solos cuando el motor del caso responde (`llenar()` en `js/decisiones.js`).

| # | Lámina | Qué se ve, y para qué está cada cosa | De dónde sale |
|---|---|---|---|
| 1 | Portada | El nombre, qué es y una frase. A la derecha, un camión minero hecho de decenas de miles de puntos, avanzando, mientras una franja de luz lo recorre | El camión es una ilustración (`js/portada.js`, con el modelo de `js/decisiones.js`) |
| 2 | Generative AI para datasets | «No es una red que predice». Dos filas con la misma forma, que se mueven a la vez: un LLM (entra una pregunta, sale la respuesta) y Krylov (entra un dataset, sale la decisión con su incertidumbre). Ninguno se vuelve a entrenar para responder | Los datasets y mapas de la fila de Krylov son respuestas reales de la red (`datos.js → rafaga`). **La pregunta y la respuesta del LLM («¿Cuál es la mejor hackathon del año 2026?», «Platanus Hack 26. Por lejos.») son un guiño a la sala, escrito a mano** (`js/paradigma.js`) |
| 3 | En el pasado vs. hoy | El flujo de trabajo, en **dos pasos** para mirar una cosa a la vez. Primero «En el pasado»: elegir el modelo, entrenar con ese dataset, inferir; y de nuevo con cada dataset. Al avanzar, «Hoy»: elegir el modelo, simular datasets, pre-entrenar la red, una sola vez; después, inferir es un forward pass | 2 minutos por dataset (M-25) y 10 milisegundos (`latencia_ms`). Los contadores cuentan lo que la animación muestra, no son una medición (`js/flujo.js`) |
| 4 | Mundos simulados | Terrenos simulados en remolino; el contador | M-01 (7.750.592) |
| 5 | Entra un archivo, sale la respuesta | Un archivo tras otro entra a la red y sale su mapa, que se suma a una muralla de mapas; dos contadores | Cada mapa es la respuesta real de la red para un banco distinto. 10 ms: `latencia_ms`. 2 minutos: M-25 |
| 6 | Cinco decisiones | «Una mina decide esto todos los días»: las cinco preguntas, dichas sin palabras de minería, con una figura cada una | Las figuras son ilustraciones. Quién toma cada decisión está en la lámina de la tecla `Q` |
| 7 | Qué roca conviene procesar | El terreno en tres colores y, a la izquierda, **lo que Krylov entrega**: para 13 partes del terreno, cuánto arsénico hay con su intervalo de credibilidad de 90%, contra el límite; debajo, cuántas partes hay de cada color y lo que vale despejar la duda (US$ 1.577.707). Al segundo paso, «¿Dónde perforo?» | `api.analizar("leyes")` y `api.donde_medir("leyes")` con la red; los intervalos son los cuantiles 5% y 95% de su posteriori (`datos.js → terreno.bajo, alto`) |
| 8 | La pared de la mina | La pared pintada con la decisión de cada sector. A la izquierda, para los sectores que se aceleran, cuántas horas faltan, con su intervalo de credibilidad; debajo, 5 / 2 / 29 y el valor (US$ 78.574). Arriba a la derecha, la curva de un sector: lo medido y el abanico de lo que puede venir | La respuesta de la red del motor `deformacion`, **que no pasó su sello todavía** (ver más abajo) |
| 9 | El cobre en la planta | Las líneas de estanques, con sus columnas en el color de su decisión. A la izquierda, el cobre que va a recuperar cada línea, con su intervalo de credibilidad, contra la meta; debajo, 2 / 3 / 3 y el valor (US$ 8.809) | La respuesta de la red del motor `cinetica`, **que pasó su sello** el sábado a las 17:09 |
| 10 | Los camiones | Los camiones, cada uno hecho de miles de puntos, subiendo y bajando por la rampa; su color es su desgaste. A la izquierda, qué entrega Krylov, **sin gráfico ni cifras** | El archivo de demo del caso `flota`. Su motor todavía no tiene red |
| 11 | Los túneles | Los túneles después de una explosión: cada destello es un temblor del archivo. A la izquierda, qué entrega Krylov, sin gráfico ni cifras | El archivo de demo del caso `sismicidad`. Su red está entrenando |
| 12 | ¿Y cómo sé que acierta? | **Dos medidas de accuracy, de 0 a 1.** Las decisiones: 0,98 (decidió en 715 partes del terreno y acertó en 700; un cuadrado por decisión). Los intervalos: 0,90 (61 de 68 valores escondidos dentro de su intervalo; una barra por valor) | `datos.js → terreno.examen_bloques` (M-54) y `examen_puntos` (`js/confianza.js`) |
| 13 | Cierre | El mensaje de venta; un contador de los análisis que Krylov habría respondido mientras duró el pitch; la muralla de mapas que se sigue llenando; el QR | El contador es una cuenta: segundos desde la primera pulsación ÷ 10 ms. El QR se dibuja desde `config.js` |

Fuera del recorrido, para las preguntas (`js/preguntas.js`):

| Tecla | Lámina | Qué responde | De dónde sale |
|---|---|---|---|
| `Q` | ¿Quién lo usa? | Quien decide en el turno: las cinco figuras 3D de la lámina 6, cada una con la persona que toma esa decisión | Roles, no empresas. No hay clientes ni pilotos |
| `A` | ¿Qué archivo recibe? | El que pide el modelo de cada decisión: para cada una, cómo agrupa (un dibujo de sus niveles), cuántas unidades y filas trae su archivo, qué es una fila y sus columnas | `casos/<caso>.yaml` (`datos.js → modelos`) |
| `L` | ¿Y un LLM? | «Tendría que correr el modelo caro, cada vez». En 3D: a la izquierda, una cadena de MCMC arma la respuesta de a una muestra; a la derecha, Krylov la entrega entera. 2 a 3 minutos contra 10 milisegundos | La prueba de `datos/prueba_llm/` y el sello. Las nubes son una ilustración |
| `M` | Cada predicción viene con su intervalo de credibilidad | Las ocho líneas de la planta: la estimación, su intervalo de 90% y lo que de verdad pasó (7 de 8 adentro) | La red de `cinetica` y la verdad escondida del archivo |
| `0` | Cómo funciona | Bayesian Amortized Inference en dos mitades, con los números del sello | `motor/artefactos/espacial/sello.json`, M-13 |

Las cuatro escenas de las láminas 8 a 11 están en `js/decisiones.js`. Cada una recorre su archivo en el tiempo (el reloj de arriba a la derecha dice por dónde va), se queda unos segundos en el final y vuelve a empezar.

## Lo que hay detrás, y que la pantalla no dice

A pedido, la pantalla no lleva pies ni rótulos («simulado», «ilustración», «medido en…», «hoja de ruta»), ni la lámina de «sabe cuando no sabe», y el deck habla de las cinco decisiones como producto. **En ninguna lámina se afirma que los datos sean de una mina real ni se muestran resultados inventados.** Lo que sigue es lo que quien presenta tiene que saber para responder con la verdad si le preguntan; está también en las notas de cada lámina (tecla `N`).

1. **De las cinco decisiones, hoy muestran respuesta tres.** `leyes` y `flotacion`, con sus redes validadas (la de la planta, `cinetica`, pasó su sello el sábado a las 17:09). Y `taludes`, con la red del motor `deformacion`, que entrenó pero **todavía no pasó su sello**: cumple 5 de 6 criterios; el que falla es la calibración sector por sector, y no está comparada con el método lento. `generar.py` usa la red de un motor apenas existe su `codificador.onnx`, haya pasado o no, y guarda `sello_pasa` en `datos.js`. **Para la pared, esto se aparta de la regla 5 de `AGENTS.md`**: en la app, esa tarjeta todavía no se presenta como respuesta de la red. Si el equipo no quiere mostrarla, basta borrar esa condición en `serie()` y volver a generar. Las otras dos (`flota`, `sismicidad`) no tienen red todavía: sus láminas animan el archivo de demo y dicen qué entrega Krylov, sin gráfico ni cifras.
1b. **En la pared, un dato que se puede decir:** en ese archivo simulado, los 5 sectores que la red manda cerrar son los 5 que cedían según la verdad escondida, y el que más se movió (Sector 25, 24 mm) no cede. Es un archivo y es simulado.
2. **Todos los archivos de demo son simulados** (`origen_datos` de cada caso lo dice, y la app lo muestra). El único examen con datos reales es el del motor espacial en el terreno público del río Mosa: 24 de 31 mediciones escondidas dentro del rango (M-13, 77%).
3. **Las 7 horas son una multiplicación:** 228 análisis × 117,1 s (M-10, M-25). Nadie las corrió seguidas. Y se midieron en el terreno real, no en el banco del demo. Son las láminas 3 y 5, y en las dos se dice lo mismo: 228 análisis, a 2 minutos cada uno.
4. **Los mapas de las láminas 2, 5 y 12 se repiten:** son 32, guardados; el deck los anima, no los calcula. **Y hay contadores que no son mediciones:** los dos de la lámina 3 cuentan lo que la animación muestra (una vuelta, un dataset), y el del cierre es una cuenta (segundos del pitch ÷ 10 ms).
4b. **La lámina 2 es una analogía.** Krylov no es un modelo de lenguaje: se parece a un LLM en que se entrena antes, una vez, y después solo se usa. Y responde datasets de la familia con que practicó; fuera de ella, avisa y no responde. En la lámina 3, «una sola vez» fueron 4 h 40 min de pre-entrenamiento (M-02): no está en pantalla, y hay que saberlo. El punto de equilibrio (unos 144 datasets) es M-36, todavía pendiente en `CIFRAS.md`: no se dice como cifra.
5. **Los costos son supuestos** (K-22 a K-24): US$ 1.577.707 y US$ 8.943 dependen de ellos.
6. **En las escenas 8 a 11 el movimiento está exagerado para que se vea** (24 milímetros no se ven en una pared), y la forma de la pared, del rajo y de los túneles es una ilustración: lo que viene del archivo es cuánto, cuándo y en qué unidad.
6b. **La lámina del LLM dice «tendría que correr el modelo caro», y eso es lo que cuesta dar la posteriori completa; en la prueba, el LLM ni siquiera llegó a correrlo:** con 3 minutos tuvo que conformarse con atajos. Las dos nubes de esa lámina son una ilustración (la de la izquierda es una cadena de Metropolis de verdad, corrida en el navegador, sobre una posteriori inventada para el dibujo). **La prueba con el LLM no dio «el LLM no sirve».** Claude Fable 5.2 acertó parecido a Krylov (61 y 63 de 68 dentro del rango, contra 61). Lo que la prueba sí mostró: 152 y 177 segundos contra 10 ms; dos corridas, dos programas distintos, con diferencias de hasta 459 ppm en un lugar; y ningún sello. «Unas 20 horas» y «15.000 veces» son cuentas. Es una prueba, dos corridas, un archivo simulado, con el computador cargado. **No se dice que un LLM responde mal**: no es lo que se midió, y cualquiera puede repetirlo.
6c. **Los intervalos son de 90%, no de 95%.** El motor entrega los cuantiles 5% y 95% de la posteriori y es con 90% que se validó (0,90 de acierto en 2.000 casos). Pasar a 95% exige recalcular y volver a validar; mientras tanto, el deck dice 90%. Y en la medida de los intervalos **lo ideal es 0,90 y no 1**: un rango que acierta siempre es demasiado ancho. Y con datos reales hay dos números: 138 de 155 escondiendo de a un quinto (el del sello, en pantalla) y 24 de 31 en la partición que muestra la app (M-13, 0,77).
6d. **La accuracy de las decisiones (0,98) excluye las «no sabemos»**: de 1.024 partes del terreno, decidió en 715 y acertó en 700; en 309 dijo que no sabía. Es contra la verdad escondida de un terreno simulado (M-54). Si se dice «98%», se dice «cuando decidió».
6e. **En producción no hay historial ni alertas:** el control es por respuesta (semáforo y examen). Un tablero que los siga en el tiempo es hoja de ruta.
7. **En la pared y en los túneles, Krylov apoya la decisión de un especialista** (regla 22 de `AGENTS.md`): no se promete seguridad.

Esto se aparta de las reglas 9 y 17 de `AGENTS.md` y de D-37, que piden rotular en pantalla lo simulado y separar lo construido de lo que es lámina. El repositorio es público y la app sí lo rotula: si el jurado mira las dos cosas, las va a ver distintas.

## Las palabras

El deck se escribe para alguien que nunca pisó una mina: «la pared de la mina» y no «talud»; «explosión» y no «tronadura»; «líneas de estanques» y no «celdas»; «partes del terreno» y no «bloques»; «Sector 25» y no «S-25»; «Camión 05» y no «CAEX-05». Los nombres se traducen al dibujar (`nombre()` en `js/decisiones.js`); los archivos de cada caso no se tocan.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`:** la demo real del producto. De ahí salen el QR del cierre, el texto a su lado y lo que abre la tecla `D`.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5».
- **`tiempos`:** los segundos de cada lámina que muestran las notas.

## Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js`, todo con `KRYLOV_MOTOR_ESPACIAL=red`: el caso estrella (`CASO = "leyes"`), el terreno real (`REAL = "terreno"`), los cuatro casos de series (`SERIES`), 32 bancos con la respuesta de la red para las láminas 2, 5 y 13, los terrenos del simulador, el examen del archivo muestra por muestra (`examen_puntos`), las primeras filas de dos archivos de demo (`archivos`) y, si existe, el resultado de la prueba con el LLM (`prueba_llm`). Los rótulos, límites y costos se leen de la API y de los archivos de cada caso. (También escribe el archivo que no alcanza y los casos de práctica, que el deck ya no usa.)

**Hay que volver a correrlo cada vez que un motor nuevo empiece a responder**, y después rehacer el respaldo.

## Respaldo estático

`respaldo/01.jpg` a `18.jpg` (1920×1080, el estado final de cada lámina; de la 14 a la 18 son las de preguntas) y `respaldo/krylov-deck.pdf`. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Qué se probó y qué no

- **Probado** (sáb 21-nov, 18:15, MacBook Air M3 con dos entrenamientos corriendo, Chromium sin ventana y el panel de navegador de la app de Claude): las 18 láminas y sus 20 pasos a 1920×1080 en modo estático, y el recorrido completo con el teclado (14 pulsaciones hasta el cierre), sin errores de consola y a 60 cuadros por segundo; las teclas, incluidas `Q`, `A`, `L`, `M`, `0` y `Fin`; la pausa. Dos revisiones automáticas, en todas las láminas y pasos: que ninguna cifra quede partida en dos líneas y que ningún texto quede encima de otro ni se salga del cuadro.
- **Probado también en un navegador con ventana** (el panel de la app de Claude, pantalla de alta densidad, con dos entrenamientos corriendo): 60 cuadros por segundo. **Ahí apareció un error que las capturas sin ventana no mostraban:** las cuatro escenas de las láminas 8 a 11 no se pintaban, porque sus puntos sumaban luz sin opacidad (un color que no es válido, y que ese navegador descarta). Se corrigió (`js/decisiones.js`: la opacidad de cada punto es la de su canal más fuerte) y se comprobó en ese mismo panel.
- **Las escenas se miraron además como se ven en una pantalla de alta densidad** (el doble de píxeles): ahí los camiones anteriores, dibujados con contornos, eran un enredo punteado, y las líneas de un píxel de los estanques y los túneles casi no se veían. Por eso los camiones se rehicieron macizos y todos los contornos se dibujan ahora con puntos seguidos (`cordon` en `js/decisiones.js`).
- **La revisión de textos superpuestos se corre además con las letras más separadas**, para simular un navegador que corta las líneas en otro lugar (así apareció el solape de la lámina 7 que no se veía en las capturas), y revisa que ningún texto se salga del cuadro. Las columnas de texto ahora fluyen: lo que viene después nunca queda debajo.
- **Lo que la revisión automática no mira:** el texto dibujado dentro de un lienzo (las barras de las láminas 1 y 3, las filas de la 2, la curva de la 8, el gráfico de la 12). Eso se revisó a ojo, en capturas.
- **Sin probar:** la tecla `D` y «reducir movimiento» en esta versión (no cambiaron), Safari, el proyector del lugar, un control de presentaciones real, y el deck en una pantalla de verdad con el entrenamiento corriendo (las capturas dan 60 cuadros por segundo, pero sin ventana).
- **Si el navegador no tiene WebGL**, las láminas con 3D (4 y 6 a 11) muestran su imagen de `respaldo/`.

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
- **A `seguimiento`:** `GUION.md` y `LAMINAS.md` describen otro pitch (abre con el barco, entra a la app, siete láminas). Hay que dejar uno solo. Y hay cifras nuevas en pantalla que conviene que una persona firme en `CIFRAS.md` (además de la prueba con el LLM y el 138 de 155 del sello, que hoy no tienen fila): «7 horas» y «0,69 segundos» como apertura (M-09, M-10), «4 h 40 min» de entrenamiento (M-02) y, sobre todo, el «casi un millón» de la lámina 3, que es una cuenta. M-36 (el punto de equilibrio) sigue pendiente.
- **A `producto` (PC 1):** si cambia la dirección del producto, avisar para `config.js`.
- **A una persona del equipo:** confirmar los nombres del cierre; abrir el deck en Safari y con el proyector antes del ensayo.
