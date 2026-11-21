# PC 1 · Producto: backend, frontend y despliegue

> **Hackathon:** el producto se termina el **sábado a las 18:00**. Lo más simple que se vea bien, y que la simulación se vea en pantalla.
>
> **Pivote del sábado 12:10 (D-37): Krylov es el data scientist artificial de la minería.** Este archivo reemplaza tu lista anterior. Lo hecho antes sigue sirviendo casi entero.

Eres el agente de Claude Code del **PC 1**. Tu rol es `producto`. El contexto general está en `AGENTS.md`, que ya se cargó.

## Tu misión en una línea

Dejar funcionando, en el computador del escenario y en una URL pública, la app minera que el jurado va a ver: cinco decisiones, un recorrido de once pasos sin esperas, y un QR que abre lo mismo en cualquier teléfono.

## Qué cambia para ti con el pivote, y qué no

**No cambia:** el chat, el calce, la interpretación, el modo estático, los deslizadores (`decision.ts`), el mapa en canvas, «¿Dónde mido?» (P-09), el pie con «precalculado», el diseño. **La forma de las respuestas es la misma:** mapa (`analizar_espacial.json`) o lista (`analizar_tabla.json`).

**Cambia:**

1. **Las tarjetas.** Son cinco, en el orden de `casos/INICIO`: `leyes`, `taludes`, `flotacion`, `flota`, `sismicidad`. Salen la cartera y las tarjetas de rotación, inasistencias y crédito. Ningún texto de minería va escrito en el código: sale de `casos/<nombre>.yaml` y de `casos/textos.yaml`.
2. **`leyes` es el terreno con otro archivo.** Mismo motor (`espacial`), mismo mapa, mismos pines. El botón dice «¿Dónde perforo?» (sale de `rotulos.donde_medir` del caso; la ruta sigue siendo `/api/donde-medir`). Los rótulos de los tres colores también salen del caso.
3. **Un componente nuevo: `Curva`.** En los cuatro casos de lista, cada unidad puede traer `curva` (`contratos/CONTRATO.md`, sección 6): los puntos medidos, la línea de «ahora», un abanico (`bajo`, `medio`, `alto`) con lo que Krylov cree que viene, la línea del límite y los nombres de los ejes. Al elegir una unidad de la lista se dibuja su curva; al abrir la tarjeta, la de la unidad con más duda. En `taludes` puede venir además `marca` («faltan entre 9 y 31 horas»). Si `curva` no viene, la lista se ve igual que antes.
4. **Ejemplos fijos nuevos** para maquetar desde ya: `contratos/ejemplos/casos.json` y `analizar_taludes.json`, `analizar_flotacion.json`, `analizar_flota.json`, `analizar_sismicidad.json`. Sus números son inventados: en pantalla llevan el rótulo «ejemplo» hasta que PC 2 entregue lo real.
5. **Los archivos de los casos de lista son series:** una fila por medición, con `unidad`, `tiempo` y `valor`. `papeles(motor_id)` lo dice; el calce funciona igual.
6. **El archivo que no sirve** (tecla `M`) ahora es `leyes_pocos`: un banco con 12 pozos, que da `rojo_datos` con su motivo. Ya no hay arco rojo → corrección → verde, salvo que PC 2 entregue la nube de un motor.
7. **Rótulo de datos simulados.** Cada caso trae `sintetico: true` y su `origen_datos`: la pantalla lo muestra siempre.

## Lo que es tuyo y lo que no

- **Tuyo:** `servicio/` (backend), `web/` (frontend y `web/public/estatico/`), `estado/producto.md`, y el despliegue.
- **No tocas:** `nucleo/` y `motor/` (PC 2); `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md` (PC 3). Si necesitas un cambio ahí, lo pides en «Pedidos a otros» de tu estado.
- **No importas `torch`** en `servicio/`. No tocas motores: llamas a las funciones de `nucleo/api.py`.
- **Este computador no entrena ni corre el método lento de siempre.**

## Cómo trabajas

1. Antes de cada tarea: `git pull --rebase` y lee `estado/TABLERO.md`. **Si el tablero dice otra cosa que esta lista, manda el tablero.**
2. Haz la tarea contra su criterio de «listo cuando». Si lleva el doble de su duración, córtala o simplifícala y anótalo.
3. Al terminar: skill `actualizar-estado`, con el identificador de la tarea al inicio de la línea («P-22 terminada: …»).
4. Si necesitas algo de PC 2 que todavía no existe, sigue con el ejemplo fijo. Nunca esperes.
5. **Las horas de la tabla son topes, no horas de inicio (D-29).**
6. **Vercel:** el plan gratuito llegó a su límite diario esta mañana. Despliega solo cuando cambie `web/` y agrupa los redespliegues en H4 (14:30), H5 (16:30) y H6 (18:00).

## Tus tareas, en orden

El detalle (entregable y criterio de cada una) está en `WORKPLAN.md`, sección 6.2. El recorrido que tiene que salir está en la sección 4.3. Las vistas, en la 1.3. El formato de cada respuesta, en `contratos/CONTRATO.md`, sección 6.

| Id | Hora | Min | Qué |
|---|---|---|---|
| P-21 | 12:30 | 40 | Inicio minero: cinco tarjetas en el orden de `casos/INICIO`, textos del chat («¿Qué decisión tienes que tomar?»), fuera la cartera y lo antiguo. Las cuatro tarjetas nuevas pintan su ejemplo fijo, rotulado «ejemplo» |
| P-22 | 13:10 | 40 | `leyes` real con la red: mapa, deslizadores, «¿Dónde perforo?» con sus tres pines y tres resultados. `exportar_estatico` de `leyes`. Redespliegue |
| P-23 | 13:50 | 60 | Componente `Curva`, contra `analizar_taludes.json` |
| | 14:30 | | **H4:** `leyes` en la URL pública; cinco tarjetas en el inicio |
| P-24 | 14:50 | 40 | Chat con los cinco modelos: `papeles` de los motores de series, calce por regla y por modelo de lenguaje, interpretación con las plantillas nuevas, un archivo de prueba por caso |
| P-25 | 15:30 | 30 | Conectar `flotacion` y `taludes` reales cuando PC 2 avise. `exportar_estatico` |
| P-26 | 16:00 | 30 | Vista «sabe cuando no sabe»: tecla `M` carga `leyes_pocos` → banda roja con el motivo |
| | 16:30 | | **H5:** dos tarjetas nuevas respondiendo con datos del motor |
| P-27 | 16:40 | 30 | Conectar `flota` y `sismicidad`. **La tarjeta que a las 17:30 no tenga respuesta del motor sale del inicio** |
| P-28 | 17:10 | 30 | Modo demo: teclas `1` a `5`, `D`, `M`, `L`; semilla fija; pantalla completa; portada y cierre con QR. `exportar_estatico` completo. Redespliegue |
| P-29 | 17:40 | 20 | Skill `preparar-demo`. Borrar código muerto (cartera, vistas antiguas). **18:00: producto terminado** |
| P-30 | 18:15 | 20 | Hasta las 20:30, cada vez que PC 2 pase un motor a `red`: regenerar su estático, comprobar el rótulo y redesplegar. Nada más cambia |

Después de las 18:00: solo textos, orden, tamaños y errores (`WORKPLAN.md`, sección 6.6). A las 22:00, el video de respaldo con PC 3.

## Lo que más importa de tu trabajo

- **Primero `leyes`.** Es el demo mínimo y ya responde con la red. Si a las 14:30 no está en la URL pública, deja todo lo demás.
- **El modo estático no es un extra.** La URL del QR tiene que hacer el recorrido completo sin servidor. Mantenlo al día con `exportar_estatico` cada vez que cambie quién responde una tarjeta.
- **La pantalla dice quién responde.** «ejemplo» (número inventado), «precalculado» (método lento) o nada (respondió la red). A las 17:30 no queda ninguna tarjeta en «ejemplo»: o responde el motor, o sale del inicio.
- **La curva es el show de las cuatro tarjetas nuevas.** Un abanico ancho se tiene que leer como duda desde la última fila. Línea del límite gruesa, «ahora» marcado, ejes con palabras.
- **Sin jerga, ni estadística ni minera.** Si un texto de `casos/` usa una palabra que no está en `GLOSARIO.md`, «Minería en simple», pídele el cambio a PC 3.
- **Nada tarda más de 2 segundos.**
- **El código se revisa.** Un cuarto de la nota es «aspecto técnico», con revisión automatizada del repositorio. Sin código muerto de la cartera ni de las tarjetas antiguas, y la prueba de `decision.ts` pasando.

## Qué recibes y qué entregas

- De PC 2: `nucleo/api.py`. `leyes` ya responde. `flotacion` y `taludes` cerca de las 15:40 (primero precalculado). `flota` y `sismicidad` cerca de las 17:10. Cada vez que un motor pasa a `red`, PC 2 avisa en su estado.
- De PC 3: los casos, los datos del demo, los ejemplos fijos, los textos de pantalla y los archivos de prueba para subir.
- Entregas: la URL pública y el demo. Avisa a PC 3 cada vez que redespliegues.

## Arranque en un computador nuevo

Si este computador ya trabajó antes del pivote, no hay nada que instalar: `git pull --rebase` y sigue. Si es un clon nuevo:

```bash
gh auth login && gh auth setup-git
git clone https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git krylov && cd krylov
git remote set-url --add --push origin https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git
git remote set-url --add --push origin https://github.com/Silent-math/krylov.git
cp CLAUDE.local.md.ejemplo CLAUDE.local.md     # dejar ROL: producto y @PC1_PRODUCTO.md
```

`git remote -v` tiene que mostrar una línea `(fetch)` y dos `(push)`. Reglas de siempre: `git pull --rebase` antes de cada `git push`; nunca `--force`; nada de claves en el repositorio; no tocar los cuatro archivos de entrega de la raíz. Lo que hay que instalar está en `STACK.md`, secciones 1 y 2.
