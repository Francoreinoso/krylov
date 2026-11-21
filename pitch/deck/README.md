# Krylov · deck de venta

**Krylov, el Artificial Data Scientist de la minería.** El mensaje del deck: los modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide, gracias a Bayesian Amortized Inference.

Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional. El guion está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html`. Después, `F` para pantalla completa.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. En el cierre no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `Fin` | Va al cierre (lámina 13) |
| `0` | «Cómo funciona»: la arquitectura, fuera del recorrido |
| `Q` `A` `L` `M` | Las láminas de preguntas, fuera del recorrido: **Q**uién lo usa, qué **A**rchivo recibe, por qué no un **L**LM, qué pasa en producción (**M**onitoreo). Entre ellas se avanza con las flechas |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y qué hay detrás de cada lámina |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En la lámina 7, arrastrar gira el terreno |

En la dirección: `#7` abre la lámina 7, `#7.1` su segundo paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final y `?animado` fuerza el movimiento. Con «reducir movimiento» activado en el sistema, el deck abre sin animaciones.

## Las láminas

Son trece en el recorrido (catorce pulsaciones), más cinco fuera de él para las preguntas.

| # | Lámina | Qué se ve, y para qué está cada cosa | De dónde sale |
|---|---|---|---|
| 1 | El valor, a primera vista | Dos filas iguales. «En el pasado: 7 horas», con una barra de 228 tramos (un análisis de 2 minutos cada uno). «Hoy, con Krylov: 0,69 segundos», con la misma escala: menos de un píxel, un punto que late cada 0,69 s | M-08, M-09, M-10 y M-25, del sello del motor espacial (`js/portada.js`) |
| 2 | Generative AI para datasets | «No es una red que predice». Dos filas con la misma forma, que se mueven a la vez: un LLM (entra texto, sale texto) y Krylov (entra un dataset, sale la decisión con su incertidumbre). Ninguno se vuelve a entrenar para responder. Abajo, la línea técnica: Simulation-based Inference, p(parámetros \| dataset) | Los datasets y mapas de la fila de Krylov son respuestas reales de la red (`datos.js → rafaga`); el texto del LLM son barras, a propósito (`js/paradigma.js`) |
| 3 | En el pasado vs. hoy | El flujo de trabajo de un data scientist contra el de Bayesian Amortized Inference, como una carrera con un solo reloj (el tiempo de cómputo). Arriba, tres pasos que se repiten con cada dataset. Abajo, tres pasos que se hacen una vez y un cuarto, inferir, que es instantáneo. Los colores son los mismos pasos en las dos filas | 117 s por dataset (M-25), 228 en 7 h 25 min (M-08, M-10), 280 minutos de entrenamiento (M-02), 10 ms por dataset (`latencia_ms`). El contador final es una cuenta (`js/flujo.js`) |
| 4 | Mundos simulados | Terrenos simulados en remolino; el contador | M-01 (7.750.592) |
| 5 | Entra un archivo, sale la respuesta | Un archivo tras otro entra a la red y sale su mapa, que se suma a una muralla de mapas; dos contadores; al segundo paso, 228 análisis en 0,69 s contra más de 7 horas | Cada mapa es la respuesta real de la red para un banco distinto. 10 ms: `latencia_ms`. 2 minutos: M-25. M-08, M-09, M-10 |
| 6 | Cinco decisiones | «Una mina decide esto todos los días»: las cinco preguntas, dichas sin palabras de minería, con una figura cada una. Bajo cada pregunta, **quién la toma** (el geólogo, quien vigila la pared, el jefe de turno…) | Las figuras son ilustraciones. Los roles son a quién se le vendería primero: no hay clientes |
| 7 | Qué roca conviene procesar | El terreno como superficie topográfica en tres colores; lo que cuesta no saber; al segundo paso, «¿Dónde perforo?» con 40 columnas de luz y los tres mejores lugares | `api.analizar("leyes")` y `api.donde_medir("leyes")` con la red: M-40, M-41, M-43, M-46 |
| 8 | La pared de la mina | La pared, hecha de puntos, partida en sus 36 sectores: cada sector se desplaza y se enciende lo que el radar midió, hora a hora; la cámara se acerca a medida que se mueve. La franja amarilla es el barrido del radar. En la columna de texto, la curva de dos sectores de la misma pared: el que más se movió y el que menos | El archivo de demo del caso `taludes` |
| 9 | El cobre en la planta | Las 8 líneas de estanques, con sus burbujas. La espuma de cada estanque brilla según el cobre que flotó ahí y rebalsa a una canaleta que corre hasta el final de la línea; ahí, la columna es el cobre recuperado, y la línea blanca, la meta | El archivo de demo del caso `flotacion` |
| 10 | Los camiones | Los 40 camiones, cada uno hecho de miles de puntos sobre su carrocería (se ven macizos en cualquier pantalla), subiendo y bajando por los cuatro niveles de la rampa, con las ruedas girando. **El color de cada camión es su desgaste**: de verde a rojo; el que pasa el 85% del límite parpadea. Las etiquetas siguen a los más gastados que estén a la vista | El archivo de demo del caso `flota` (la rampa es una ilustración) |
| 11 | Los túneles | Los 8 sectores de túneles después de una explosión: cada destello es un temblor del archivo, a su hora y con su tamaño según la magnitud; en rojo, el fuerte | El archivo de demo del caso `sismicidad` (el lugar de cada destello dentro de su sector es una ilustración) |
| 12 | ¿Y cómo sé que acierta? | **Un número de 0 a 1: 0,90.** A la derecha, el examen que Krylov se toma con el archivo: 68 muestras escondidas, cada una con el rango que dio (la barra) y lo que de verdad había (el punto): 61 adentro, 7 afuera. A la izquierda, la misma pregunta tres veces: con este archivo, en 2.000 casos nuevos y con datos reales | `datos.js → examen_puntos` (el examen de `api.analizar("leyes")`, muestra por muestra) y el sello: `cobertura_90`, `examen_5_particiones` (`js/confianza.js`) |
| 13 | Cierre | El mensaje de venta; un contador de los análisis que Krylov habría respondido mientras duró el pitch; la muralla de mapas que se sigue llenando; el QR | El contador es una cuenta: segundos desde la primera pulsación ÷ 10 ms. El QR se dibuja desde `config.js` |

Fuera del recorrido, para las preguntas (`js/preguntas.js`):

| Tecla | Lámina | Qué responde | De dónde sale |
|---|---|---|---|
| `Q` | ¿Quién lo usa? | Quien decide en el turno, no un data scientist: cinco roles, cada uno con su decisión | Roles, no empresas. No hay clientes ni pilotos |
| `A` | ¿Qué archivo recibe? | Un CSV, tres columnas: las primeras filas reales de dos archivos de demo, con el papel de cada columna | `datos/demo/leyes.csv`, `datos/demo/flota.csv`, `casos/<caso>.yaml` |
| `L` | ¿Y si le subo el archivo a un LLM? | **La prueba, hecha de verdad**: el mismo archivo y el mismo examen a Claude Fable 5.2, con herramientas y 3 minutos, dos veces | `datos/prueba_llm/` (ver su `LEEME.md`) |
| `M` | ¿Y si falla en producción? | Cada respuesta trae su control: el semáforo, el examen del archivo y el sello del motor | La API (`leyes_pocos`), `examen_puntos` y los criterios del sello |
| `0` | Cómo funciona | Bayesian Amortized Inference en dos mitades, con los números del sello | `motor/artefactos/espacial/sello.json`, M-13 |

Las cuatro escenas de las láminas 8 a 11 están en `js/decisiones.js`. Cada una recorre su archivo en el tiempo (el reloj de arriba a la derecha dice por dónde va), se queda unos segundos en el final y vuelve a empezar.

## Lo que hay detrás, y que la pantalla no dice

A pedido, la pantalla no lleva pies ni rótulos («simulado», «ilustración», «medido en…», «hoja de ruta»), ni la lámina de «sabe cuando no sabe», y el deck habla de las cinco decisiones como producto. **En ninguna lámina se afirma que los datos sean de una mina real ni se muestran resultados inventados.** Lo que sigue es lo que quien presenta tiene que saber para responder con la verdad si le preguntan; está también en las notas de cada lámina (tecla `N`).

1. **De las cinco decisiones, hoy responde una.** Al generar estos datos (sáb 21-nov, 13:23) solo `leyes` tenía su motor respondiendo, con la red validada. Los motores de `taludes`, `flotacion`, `flota` y `sismicidad` todavía no respondían: **sus láminas (8 a 11) animan el archivo de demo de cada caso; el color dice cuánto se midió (cuánto se movió un sector, cuánto desgaste lleva un camión), no qué conviene hacer.** Cuando un motor responda, se vuelve a correr `generar.py`: cada unidad toma el color de su decisión y la columna de texto muestra cuántas hay de cada una y lo que cuesta no saber. Antes de presentar hay que mirar la tabla «Los cinco casos» de `estado/TABLERO.md`.
2. **Todos los archivos de demo son simulados** (`origen_datos` de cada caso lo dice, y la app lo muestra). El único examen con datos reales es el del motor espacial en el terreno público del río Mosa: 24 de 31 mediciones escondidas dentro del rango (M-13, 77%).
3. **Las 7 horas son una multiplicación:** 228 análisis × 117,1 s (M-10, M-25). Nadie las corrió seguidas. Y se midieron en el terreno real, no en el banco del demo. Son las láminas 1, 3 y 5, y en las tres se dice lo mismo: 228 análisis, a 2 minutos cada uno.
4. **Los mapas de las láminas 2, 5 y 12 se repiten:** son 32, guardados; el deck los anima, no los calcula. **Y hay dos contadores que son cuentas, no mediciones:** el «casi un millón» de la lámina 3 (las 2 h 45 min que quedan después de entrenar ÷ 10 ms) y el del cierre (segundos del pitch ÷ 10 ms).
4b. **La lámina 2 es una analogía.** Krylov no es un modelo de lenguaje: se parece a un LLM en que se entrena antes, una vez, y después solo se usa. Y responde datasets de la familia con que practicó; fuera de ella, avisa y no responde. En la lámina 3, durante las primeras 4 h 40 min el pasado va ganando: es lo que significa amortizar, y está bien que se vea. El punto de equilibrio (unos 144 datasets) es M-36, todavía pendiente en `CIFRAS.md`: no se dice como cifra.
5. **Los costos son supuestos** (K-22 a K-24): US$ 1.577.707 y US$ 8.943 dependen de ellos.
6. **En las escenas 8 a 11 el movimiento está exagerado para que se vea** (24 milímetros no se ven en una pared), y la forma de la pared, del rajo y de los túneles es una ilustración: lo que viene del archivo es cuánto, cuándo y en qué unidad.
6b. **La prueba con el LLM no dio «el LLM no sirve».** Claude Fable 5.2 acertó parecido a Krylov (61 y 63 de 68 dentro del rango, contra 61). Lo que la prueba sí mostró: 152 y 177 segundos contra 10 ms; dos corridas, dos programas distintos, con diferencias de hasta 459 ppm en un lugar; y ningún sello. «Unas 20 horas» y «15.000 veces» son cuentas. Es una prueba, dos corridas, un archivo simulado, con el computador cargado. **No se dice que un LLM responde mal**: no es lo que se midió, y cualquiera puede repetirlo.
6c. **En «¿cómo sé que acierta?», lo ideal es 0,90 y no 1**: un rango que acierta siempre es demasiado ancho. Y con datos reales hay dos números: 138 de 155 escondiendo de a un quinto (el del sello, en pantalla) y 24 de 31 en la partición que muestra la app (M-13, 0,77).
6d. **En producción no hay historial ni alertas:** el control es por respuesta (semáforo y examen). Un tablero que los siga en el tiempo es hoja de ruta.
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

- **Probado** (sáb 21-nov, 16:30, MacBook Air M3 con un entrenamiento corriendo en su GPU, Chromium sin ventana, abierto por `file://`): las 18 láminas y sus 20 pasos a 1920×1080 en modo estático, y el recorrido completo con el teclado a 1280×720 en movimiento (14 pulsaciones hasta el cierre; la siguiente no pasa a las preguntas), sin errores de consola y a 60 cuadros por segundo; las teclas, incluidas `Q`, `A`, `L`, `M`, `0` y `Fin`; la pausa. Dos revisiones automáticas, en todas las láminas y pasos: que ninguna cifra quede partida en dos líneas y que ningún texto quede encima de otro, ni a mitad de un cambio de paso.
- **Las escenas se miraron además como se ven en una pantalla de alta densidad** (el doble de píxeles): ahí los camiones anteriores, dibujados con contornos, eran un enredo punteado; por eso se rehicieron macizos.
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
