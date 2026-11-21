# Krylov · deck de venta (versión minería)

Las láminas del pitch de 3 minutos (cifra J-04): **Krylov, un Artificial Data Scientist para la minería.** Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: las bibliotecas están en `vendor/` y los datos en `datos/datos.js`. Lo único que usa red es la demo en vivo (tecla `D`), que es opcional.

Esta versión junta dos cosas: **el pivote a minería (D-37, `pitch/LAMINAS.md`, tarea S-27)** y **la revisión del deck que hizo el equipo el sábado a las 12:10**. Donde las dos no dicen lo mismo, está anotado en «Diferencias con `LAMINAS.md`», más abajo. El guion del deck está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html`. Después, `F` para pantalla completa.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. Un control de presentaciones manda estas teclas. En la lámina 9 no sigue de largo |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `0` | «Cómo funciona»: la arquitectura, fuera de los 3 minutos |
| `D` | Abre la demo en vivo encima de las láminas (necesita internet). `D` o `Esc` la cierran |
| `N` | Notas de quien presenta: qué se dice y de dónde sale cada número |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En las láminas 4 y 5, arrastrar gira el banco. En la 5 se puede elegir otra letra en el mapa y «Bajo», «Medio» o «Alto» en la regla |

En la dirección: `#4` abre la lámina 4, `#4.2` su tercer paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final (así se saca el respaldo) y `?animado` fuerza el movimiento aunque el sistema pida reducirlo. Con «reducir movimiento» activado en el sistema (`prefers-reduced-motion`), el deck abre sin animaciones.

## Lo que se cambia a mano: `config.js`

- **`demo.url` y `demo.texto`: la demo real del producto.** De ahí salen el QR del cierre (se dibuja solo, sin servicios externos), el texto bajo el QR y lo que abre la tecla `D`. Cuando cambie la dirección del producto final, se cambia ahí y nada más.
- **`casos`: quién responde hoy cada una de las cinco decisiones** (lámina 7): `responde`, `precalculado` o `ruta`. Tiene que decir lo mismo que la tabla «Los cinco casos» de `estado/TABLERO.md`. **Se revisa a las 20:30.** Hoy: `leyes` responde; las otras cuatro, hoja de ruta.
- **`equipo`:** los nombres para el cierre. Hoy dice «Equipo 5», porque nadie ha confirmado que su nombre se pueda mostrar.
- **`tiempos`:** los segundos de cada lámina que muestran las notas.

## Las láminas y de dónde sale cada dato

Todo número en pantalla tiene su id de `pitch/CIFRAS.md` o sale de un archivo o comando del repositorio. Los mismos ids están en las notas (tecla `N`).

| # | Lámina | Qué se ve | Números y su fuente | Qué es simulado o ilustración |
|---|---|---|---|---|
| 1 | El problema | Un rajo hecho de puntos que aparece con un barrido; el problema en tres frases; el nombre | Ninguno. «Tardan horas» se sostiene con M-10 | **El rajo es una ilustración** (`js/puntos.js`). Al pie: «Imagen: ilustración» |
| 2 | Demo | Dos pantallas con el mismo encargo: la de Krylov termina en 0,69 s reales y muestra su mapa; la otra avanza en tiempo real y, al segundo clic, acelerada | M-08 (228 análisis), M-09 (0,69 s), M-10 (26.699 s), M-25 (117 s por análisis). El mapa es el del terreno real (`api.analizar("terreno")`), porque ese es el encargo que se midió | Nada |
| 3 | Mundos simulados | Terrenos simulados en remolino; contador; la pila que queda | M-01 (7.750.592). N-01 («a comienzos del 1900») | Los terrenos son reales del simulador (256, semilla 2026), **repetidos** |
| 4 | El banco | El caso `leyes` como superficie: altura = arsénico estimado, color = decisión, línea blanca = 500 ppm, malla = tope del rango creíble, puntos = las 340 muestras | M-40 (147, 309 y 568 bloques), M-41 (US$ 1.577.707), K-21 (500 ppm), K-22 y K-23 (costos) | **El banco es simulado.** Lo dicen el título y la bajada, que es el `origen_datos` del caso. La superficie se dibuja interpolando entre los 1.024 bloques |
| 5 | ¿Dónde perforo? | 40 columnas de luz, una por lugar candidato, tan altas como lo que vale una muestra ahí; las tres mejores con letra; al perforar, baja un taladro y el mapa se rehace | K-24 (US$ 1.500), M-43 (480 análisis), M-46 (US$ 8.943, 8.376 y 7.966). El mapa rehecho: `api.analizar("leyes", mediciones=[…])` | El mismo banco simulado. **El mapa rehecho es la respuesta de la red, guardada**: el deck la anima, no la calcula |
| 6 | Sabe cuando no sabe | Los terrenos con que practicó, según cuántas muestras tenían; un banco con 12 muestras cae afuera, en rojo; con sus 340, adentro | El motivo en pantalla es el de `api.analizar("leyes_pocos")`. Límites 30 y 400: los del simulador y de `nucleo/espacial.py` | 3.000 terrenos del simulador (semilla 2026). Solo el eje horizontal significa algo; el pie lo dice |
| 7 | Cinco decisiones | Las cinco preguntas de D-37 con una figura cada una y su estado real | Ninguno | **Las cinco figuras.** El estado sale de `config.js` |
| 8 | Negocio | El rajo se envuelve en una esfera: de la minería a cualquier industria | Ninguno | Los puntos. Al pie: «Plan del equipo · sin clientes todavía» |
| 9 | Cierre | La frase con «minas simuladas», el QR y el equipo | «Millones» se sostiene con M-01 | El fondo |
| 0 | Cómo funciona | La arquitectura en dos mitades: lo que se hace una vez y lo que pasa con cada archivo | `motor/artefactos/espacial/sello.json`; M-13 (24 de 31, con datos reales) | Nada |

### Cómo se regeneran los datos

Desde la raíz del repositorio (unos segundos):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js`, todo con `KRYLOV_MOTOR_ESPACIAL=red`. Al principio del archivo están los tres casos que usa: `CASO = "leyes"` (láminas 4 y 5), `REAL = "terreno"` (lámina 2 y examen) y `POCOS = "leyes_pocos"` (lámina 6). **Los rótulos, la unidad, el límite, los costos y el origen de los datos se leen de la respuesta de la API**: si el caso cambia (por ejemplo, si S-23 trae pozos reales), basta volver a correrlo. Lo único escrito a mano es el título de la lámina 4 («Un banco de la mina, simulado.»).

Dos cálculos usan funciones internas de `nucleo/espacial.py`, porque la API no los entrega: el tope del rango creíble por bloque y el valor de una muestra en los 37 lugares que no son los tres mejores. En los dos el script comprueba que su resultado coincide con el de la API donde se puede comparar.

### Respaldo estático

`respaldo/01.jpg` a `10.jpg` (1920×1080, el estado final de cada lámina) y `respaldo/krylov-deck.pdf` con las diez. Si el navegador falla en el escenario, se abre el PDF. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].jpg'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Qué se probó y qué no

- **Probado** (sáb 21-nov, MacBook Air M3, Chromium sin ventana, abierto por `file://`): las 10 láminas y sus 21 pasos a 1280×720 y a 1920×1080, sin errores de consola y a 60 cuadros por segundo; las teclas de la tabla; la pausa; el modo sin movimiento; la tecla `D` con y sin internet; el QR dibujado desde `config.js`.
- **Sin probar:** Safari, el proyector del lugar y un control de presentaciones real.
- **Si el navegador no tiene WebGL**, las láminas con 3D (1, 3, 4, 5, 7, 8 y 9) muestran su imagen de `respaldo/`.

## Diferencias con `LAMINAS.md` (D-37)

`LAMINAS.md` describe siete láminas y un pitch que entra a la app en los momentos 4 a 6. Este deck tiene nueve y se puede presentar entero sin salir de él. Lo que no coincide, y por qué:

| `LAMINAS.md` | Este deck | Por qué |
|---|---|---|
| Lámina 1: el barco | El problema en una mina; el barco quedó en una frase de la lámina 3 | La revisión del deck: la apertura solo explicaba el nombre y no era show |
| Lámina 2: frase del problema y carrera de barras | El problema pasó a la lámina 1; la 2 es una demostración con dos pantallas | La revisión: «demostrar cosas, poder acceder a una demo» |
| Lámina 6: cinco decisiones, en vez de la nube | Están las dos: «sabe cuando no sabe» con el caso `leyes_pocos` (lámina 6) y las cinco decisiones (lámina 7) | La nube de rotación se retiró; esta usa el motor espacial y el archivo que no alcanza |
| Visión y negocio salen | La visión es la lámina 7 (las cinco decisiones); el negocio se mantiene (lámina 8) | La revisión pidió mantener el negocio, sin Buk ni AgendaPro. Se puede saltar con la tecla `9` |
| Respaldo técnico: una tabla de motores | Una infografía de arquitectura con los números del sello del motor espacial | La revisión pidió reemplazar la tabla. Los cuatro motores nuevos no están en ella |
| Colores de la app (rojo, ámbar, verde) | Rojo cobre `#e4603c`, ámbar oro `#eec25a`, verde malaquita `#1fa87a` | La revisión pidió otra paleta. Se siguen diciendo «rojo», «ámbar» y «verde» |
| Rótulos «banco simulado» y «costos supuestos» | Sin píldoras: lo dicen el título, la bajada y una línea al pie | La revisión pidió sacar las píldoras. La información sigue en pantalla (regla 9) |

**Quien decide el pitch tiene que elegir** entre presentar el deck completo o saltar a la app en los momentos 4 a 6 como dice `GUION.md`. El deck sirve para las dos cosas: en el segundo caso se usan las láminas 1 a 3 y la 9.

## Seis cosas que quien presenta tiene que saber

1. **El banco es simulado; el examen con datos reales es otro caso.** `leyes` es un banco de tronadura simulado. El mismo motor, con el terreno público del río Mosa, dejó 24 de 31 mediciones escondidas dentro de su rango (M-13, 77%, no 90%). Está en la lámina `0` y se dice tal cual si preguntan.
2. **Las 7 horas son una multiplicación.** M-10 (26.699 s) es 228 análisis × 117,1 s, medidos en 6 terrenos. Nadie corrió las siete horas seguidas. La lámina 2 lo dice al pie. Y son del terreno real, no del banco.
3. **El tiempo de «¿Dónde perforo?» no está en pantalla.** M-44 no se ha medido limpio. En este computador los 480 análisis tardaron 1,3 s.
4. **Si la muestra sale alta, lo que cuesta no saber sube.** Con el resultado «Alto» en A pasa de 1.577.707 a 1.581.939. Por eso la lámina 5 muestra por defecto el resultado del medio (baja US$ 10.263) y dice cuánto baja en promedio (US$ 8.943, que es lo que vale la muestra). Si se elige «Alto» en la regla, la lámina dice «sube».
5. **Las cifras de minería (I-01 a I-22) no están en las láminas.** Ninguna tiene todavía la firma de una persona (S-25). «La industria que más pesa en Chile» va sin número.
6. **En seguridad no se promete** (regla 22). La lámina 7 lo dice al pie: Krylov apoya la decisión de un especialista; no la reemplaza.

## Bibliotecas y tipografías (todas locales, en `vendor/`)

| Archivo | Qué es | Licencia |
|---|---|---|
| `three.min.js` | three.js r149, para el 3D | MIT (`three.LICENSE`) |
| `gsap.min.js` | GSAP 3.15.1, para las líneas de tiempo | Licencia estándar sin costo de GreenSock (gsap.com/standard-license) |
| `qrcode.js` | qrcode-generator 2.0.4, dibuja el QR en el navegador | MIT (en la cabecera del archivo) |
| `big-shoulders-display-*.woff2` | Titulares y cifras | SIL Open Font License 1.1 (`big-shoulders-display.LICENSE`) |
| `instrument-sans-*.woff2` | Texto | SIL Open Font License 1.1 (`instrument-sans.LICENSE`) |
| `jetbrains-mono-*.woff2` | Datos y pies | SIL Open Font License 1.1 (`jetbrains-mono.LICENSE`) |
| `archivo-*.woff2` | La tipografía de la app; el deck ya no la usa | SIL Open Font License 1.1 (`archivo.LICENSE`) |

## Pedidos a otros

- **A `seguimiento`:**
  - M-46 dice C = US$ 7.967 (medido en PC 2); en PC 3 el mismo comando da 7.966. Es redondeo entre computadores; el deck muestra lo que da el comando donde se generó.
  - Registrar lo que muestra la lámina 5 después de perforar: con el resultado del medio en A (375 ppm), lo que cuesta no saber pasa de US$ 1.577.707 a 1.567.444.
  - `GUION.md` abre con el barco (momento 1); el deck ya no. Hay que elegir uno de los dos y dejar un solo guion.
  - Cuando una persona firme I-02 (13,1% del PIB, 59% de las exportaciones), se puede poner la cifra en la lámina 8.
- **A `amortizacion` (PC 2):** M-44, el tiempo limpio de los 480 análisis, para ponerlo en la lámina 5.
- **A `producto` (PC 1):** si cambia la dirección del producto, avisar para `config.js`.
- **A una persona del equipo:** confirmar los nombres del cierre; revisar `config.js → casos` a las 20:30; abrir el deck en Safari y con el proyector antes del ensayo.
