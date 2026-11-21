# Krylov · deck de venta

> **Pivote a minería (D-37, sáb 12:10): este deck todavía es el de antes del pivote.** Las láminas 1, 2 y 3 sirven con cambios de texto; la 4 y la 5 se regeneran con el caso `leyes`; la 6 se reemplaza por «cinco decisiones»; las de visión y negocio salen. El detalle, lámina por lámina, está en [`../LAMINAS.md`](../LAMINAS.md) (tarea S-27), y el guion en [`../GUION.md`](../GUION.md). Lo que sigue describe el deck tal como está hoy en el repositorio; el PDF y los PNG de `respaldo/` también son de antes del pivote.

Las láminas del pitch de 3 minutos (cifra J-04). Es una página HTML con animaciones que **abre con doble clic y corre sin internet**: no usa ningún servicio externo, las bibliotecas están en `vendor/` y los datos en `datos/datos.js`.

El guion sincronizado, con los segundos de cada lámina, está en [`../PITCH_v2.md`](../PITCH_v2.md).

## Cómo abrirlo

Doble clic en `index.html`. Después, `F` para pantalla completa.

| Tecla | Qué hace |
|---|---|
| `→` `espacio` `Av Pág` `Enter` | Avanza: el paso siguiente de la lámina o, si no quedan, la lámina siguiente. Un control de presentaciones manda estas teclas |
| `←` `Re Pág` | Retrocede |
| `1` a `9` | Va a esa lámina |
| `0` | Respaldo técnico (lámina 10, fuera de los 3 minutos) |
| `N` | Notas de quien presenta: qué se dice y de dónde sale cada número |
| `P` | Pausa todas las animaciones |
| `F` | Pantalla completa |
| mouse | En las láminas 4 y 5, arrastrar gira el terreno. En la 5 se puede hacer clic en otro pin y en «sale bajo / medio / alto» |

En la dirección: `#4` abre la lámina 4, `#4.2` su tercer paso. `?quieto` apaga el movimiento, `?estatico` deja cada lámina en su estado final (así se sacan las imágenes de respaldo) y `?animado` fuerza el movimiento aunque el sistema pida reducirlo. Si el sistema tiene activado «reducir movimiento» (`prefers-reduced-motion`), el deck abre sin animaciones.

## Qué se probó y qué no

- **Probado** (sáb 21-nov, MacBook Air M3 con un entrenamiento corriendo, Chromium sin ventana, abierto por `file://`): las 10 láminas y sus 21 pasos a 1280×720 y a 1920×1080, sin errores de consola y a 60 cuadros por segundo; las teclas de la tabla; la pausa; el modo sin movimiento.
- **Sin probar:** Safari, el proyector del lugar y un control de presentaciones real. Hay que abrirlo una vez en el computador que presenta antes de subir al escenario.
- **Si el navegador no tiene WebGL**, las láminas con 3D (3, 4, 5, 7 y 9) muestran su imagen de `respaldo/`.

## Las láminas y de dónde sale cada dato

Todo número en pantalla tiene su id de `pitch/CIFRAS.md` o sale de un archivo o comando del repositorio. Los mismos ids están en las notas de cada lámina (tecla `N`).

| # | Lámina | Qué se ve | Números y su fuente | Qué es ilustración |
|---|---|---|---|---|
| 1 | Apertura | Un plano naval que se dibuja solo; el casco se rompe; aparece la tabla y el barco se endereza | N-01: «a comienzos del 1900», sin fecha exacta | **Todo el dibujo.** El barco, los compartimentos y los números romanos de la tabla no reproducen un documento histórico. Rótulo «ilustración» |
| 2 | El problema | La carrera: la barra de Krylov tarda de verdad 0,69 s; la del método lento avanza en tiempo real y, al segundo clic, acelerada | M-08 (228 análisis), M-09 (0,69 s), M-10 (26.699 s), M-25 (117 s por análisis). Leídos de `datos.js → sello` | Nada |
| 3 | Mundos simulados | Terrenos simulados que fluyen y se apilan; contador | M-01 (7.750.592), M-02 (280 min) | Los terrenos son reales del simulador (256, semilla 2026), **repetidos**: se ven cientos, no millones. Rótulo «terrenos simulados» |
| 4 | El mapa | El terreno real en 3D: altura = zinc estimado, color = decisión, capa translúcida = rango creíble, puntos blancos = las 155 mediciones | D-04 (155), K-11 (720 mg/kg), K-12 y K-13 (costos, hipótesis). Bloques por color (20, 67, 254) y lo que cuesta no saber (US$ 646.485): `api.analizar("terreno")` con la red | Nada. Rótulos «datos públicos reales» y «costos supuestos» |
| 5 | ¿Dónde mido? | Tres pines caen sobre el mapa; al medir, el mapa se rehace | M-08, M-09, M-10. Valor de medir en A, B y C (US$ 15.629, 11.582, 10.561): `api.donde_medir("terreno")`. Mapa después de medir y US$ 625.447: `api.analizar("terreno", mediciones=[…])`. K-17 (la medición cuesta US$ 3.000, hipótesis) | Nada. **El mapa rehecho es la respuesta de la red, guardada en `datos.js`**: el deck la anima, no la calcula. En la app corre en vivo |
| 6 | Sabe cuando no sabe | La nube de empresas simuladas; el archivo cae afuera, rojo; se quita la columna y cae adentro, verde | M-29 (cae fuera y, corregido, dentro; límite 0,912). Puntos y posiciones: `api.nube("rotacion_malo")` y la misma con `["quitar_factor:fecha_salida"]`. D-05 y D-01 (el archivo) | Nada. Rótulo «empresas simuladas» |
| 7 | Visión | Minería, clima y plataformas | **Ninguno** | **Toda la lámina.** Rótulo grande «hoja de ruta» y tres rótulos «ilustración». Las figuras son puntos generados en el navegador, no datos |
| 8 | Negocio | Una plataforma y sus 1.000 empresas; precio | C-05 (US$ 20 al mes, hipótesis sin validar), C-06 (US$ 240.000 al año por 1.000 empresas, cálculo sobre C-05) | Los 1.000 puntos. Rótulo «hipótesis» |
| 9 | Cierre | La frase, el QR y el equipo | «Millones» se sostiene con M-01 | El fondo son los terrenos simulados de la lámina 3 |
| 10 | Respaldo técnico | La ficha del motor espacial, con nombres técnicos | `motor/artefactos/espacial/sello.json`; M-13 (24 de 31) | Nada. El estado de los otros tres motores está escrito a mano |

### Cómo se regeneran los datos

Desde la raíz del repositorio (tarda unos segundos; se puede correr con un entrenamiento andando):

```bash
uv run python pitch/deck/datos/generar.py
```

Escribe `datos/datos.js` con: el mapa (`api.analizar`), los tres pines (`api.donde_medir`), el mapa rehecho para cada pin y cada resultado (nueve llamadas a `api.analizar` con una medición más), la nube del archivo malo y del corregido (`api.nube`), 256 terrenos del simulador y una copia del sello. Todo con `KRYLOV_MOTOR_ESPACIAL=red`. **Hay que volver a correrlo si cambia la red del terreno, los costos del caso o el sello.**

El rango creíble por bloque (5% a 95%) no viene en la respuesta de la API. El script lo calcula con las mismas funciones de `nucleo/espacial.py` (`leer_terreno`, `canales_de`, `inferir`: media y desviación de la cabeza de mapa) y comprueba que la media coincide con la de la API.

El QR es `qr.svg`, generado en este computador con la biblioteca `qrcode` de Python, sin servicios externos:

```bash
uv run --no-project --with qrcode python -c "import qrcode; q=qrcode.QRCode(border=0); q.add_data('https://krylov-tan.vercel.app/'); q.make(); print(q.get_matrix())"
```

### Respaldo estático

`respaldo/01.png` a `10.png` (1920×1080, el estado final de cada lámina) y `respaldo/krylov-deck.pdf` con las diez. Si el navegador falla en el escenario, se abre el PDF. Para rehacerlos:

```bash
npm install --no-save playwright-core
CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
```

y el PDF, con Pillow, desde `pitch/deck/respaldo/`:

```bash
uv run --no-project --with pillow python -c "from PIL import Image; import glob; i=[Image.open(a).convert('RGB') for a in sorted(glob.glob('[0-9][0-9].png'))]; i[0].save('krylov-deck.pdf', save_all=True, append_images=i[1:], resolution=144.0, quality=88)"
```

## Cuatro cosas que quien presenta tiene que saber

1. **Las 7 horas son una multiplicación.** M-10 (26.699 s) es 228 análisis × 117,1 s, y esos 117,1 s se midieron en 6 terrenos. Nadie corrió las siete horas seguidas. La lámina 2 lo muestra («117 s por análisis × 228 análisis») y la 10 lo dice con todas sus letras. Si preguntan, se responde así.
2. **La nube es de rotación, y esa red no pasó su sello.** La lámina 6 muestra el detector de archivos malos, que sí está medido (M-29). No se dice que la tarjeta de rotación responde «al instante»: hoy responde con el método lento, precalculado.
3. **El examen real del terreno dio 24 de 31 (77%), no 90%** (M-13). No está en las láminas de los 3 minutos; está en la 10 y se dice tal cual si preguntan.
4. **No se muestra «qué manda en el terreno»** (M-30 sigue pendiente y en el archivo real la red difiere del método lento).

## Qué hay que editar a mano

- **Nombres del equipo** (lámina 9): el arreglo `EQUIPO`, al final de `index.html`. Hoy dice «Equipo 5», porque nadie ha confirmado que su nombre se pueda mostrar.
- **Estado de los otros tres motores** (lámina 10): la tabla «Los otros tres motores» de `index.html`. Está al sábado 11:00, según `estado/TABLERO.md` de las 10:14.
- **De Anthropic** la lámina 9 dice solo «Lo construimos con Claude Code». Si la interpretación del chat funciona a las 18:00, se puede agregar «y un modelo de Claude escribe la interpretación».

## Bibliotecas (todas locales, en `vendor/`)

| Archivo | Qué es | Licencia |
|---|---|---|
| `three.min.js` | three.js r149, para el 3D | MIT (`three.LICENSE`) |
| `gsap.min.js` | GSAP 3.15.1, para las líneas de tiempo | Licencia estándar sin costo de GreenSock (gsap.com/standard-license) |
| `archivo-latin-*.woff2` | Archivo Variable, la tipografía de la app, copiada de `web/node_modules/@fontsource-variable/archivo/` | SIL Open Font License 1.1 (`archivo.LICENSE`) |

Los colores de decisión (rojo `#d93f3f`, ámbar achurado `#e0a100`, verde `#1f9d61`) y el acento son los de `web/src/index.css`. El fondo es oscuro, de escenario; el acento va aclarado para leerse sobre negro.

## Pedidos a otros

- **A `seguimiento` (CIFRAS.md):** registrar las cifras del terreno que el deck muestra y hoy no tienen id propio. Salen de `api.analizar("terreno")` y `api.donde_medir("terreno")` con la red, sáb 21-nov 11:08, PC 3:
  - M-12, lo que vale medir en el mejor punto: **US$ 15.629** (pin A; B 11.582 y C 10.561). Hoy dice «pendiente».
  - Lo que cuesta no saber en el terreno, con los costos por defecto: **US$ 646.485**; después de medir en A y que salga alto (1.113 mg/kg): **US$ 625.447**.
  - Bloques por color: **20** hay que limpiar, **67** no sabemos, **254** no hace falta (341 bloques dentro del terreno).
  - Aclarar en M-10 que los 26.699 s son 228 × 117,1 s (medido por análisis), y decidir si el guion dice «toman» o «tomarían».
- **A `producto` (PC 1):** que la tecla `L` de la app abra este deck. Como el deck vive fuera de `web/`, habría que copiar `pitch/deck/` a `web/public/deck/` en el build (pesa 11 MB con el respaldo; 1,3 MB sin él) y enlazar `deck/index.html`. No es necesario para el escenario: ahí se abre el archivo local.
- **A `amortizacion` (PC 2), sin urgencia:** si `api.analizar` entregara el rango por bloque (`mapa.bajo` y `mapa.alto`), el script no dependería de funciones internas de `nucleo/espacial.py`. El contrato está congelado: es solo una nota.
- **A una persona del equipo:** confirmar los nombres que van en el cierre, y abrir el deck en Safari y con el proyector antes del ensayo.
