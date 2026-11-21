# PC 1 · Producto: backend, frontend y despliegue

> **Hackathon:** el producto se termina el **sábado a las 18:00**. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

Eres el agente de Claude Code del **PC 1**. Tu rol es `producto`. Este archivo trae todo lo que necesitas para arrancar y la lista ordenada de lo que te toca. El contexto general está en `AGENTS.md`, que ya se cargó.

## Tu misión en una línea

Dejar funcionando, en el computador del escenario y en una URL pública, la app que el jurado va a ver: cuatro vistas, un recorrido de diez pasos sin esperas, y un QR que abre lo mismo en cualquier teléfono.

## Lo que es tuyo y lo que no

- **Tuyo:** `servicio/` (backend), `web/` (frontend y `web/public/estatico/`), `estado/producto.md`, y el despliegue.
- **No tocas:** `nucleo/` y `motor/` (PC 2); `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md` (PC 3). Si necesitas un cambio ahí, lo pides en «Pedidos a otros» de tu estado.
- **No importas `torch`** en `servicio/`. No tocas motores: llamas a las funciones de `nucleo/api.py`.
- **Este computador no entrena ni corre el método lento de siempre.** Tiene 6,6 GiB de memoria y casi toda en uso; los entrenamientos van en PC 2 y PC 3.

## Arranque (03:00 a 03:15)

Espera a que PC 3 avise que el plan ya está en el repositorio (tarea S-01). Después, en este orden:

**1. Clonar y configurar los dos repositorios espejo.** Se trabaja en un solo clon. Se hace `pull` del repositorio de la organización y cada `push` va a dos lugares: al de la organización, que es el que se juzga, y al espejo `Silent-math/krylov`, que es de donde despliegan Vercel y Render (no pueden conectarse al de la organización).

```bash
gh auth login            # una vez; elige HTTPS
gh auth setup-git
git clone https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git krylov
cd krylov
git remote set-url --add --push origin https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git
git remote set-url --add --push origin https://github.com/Silent-math/krylov.git
git remote -v
```

`git remote -v` tiene que mostrar tres líneas: una `(fetch)` y una `(push)` hacia `platanus-hack/platanus-hack-26-cl-team-5`, y una `(push)` hacia `Silent-math/krylov`. Si falta la del espejo, repite el tercer comando.

Si la persona de este computador no es la dueña de `Silent-math/krylov`, tiene que haber aceptado antes la invitación de colaborador (llega por correo, o en `https://github.com/Silent-math/krylov/invitations`).

**2. Declarar el rol.**

```bash
cp CLAUDE.local.md.ejemplo CLAUDE.local.md
```

Deja solo las líneas `ROL: producto` y `@PC1_PRODUCTO.md`, y el nombre de la persona. Reinicia Claude Code para que lo cargue.

**3. Probar que el push llega a los dos.** Agrega una línea con la hora en `estado/producto.md` y:

```bash
git add estado/producto.md && git commit -m "estado producto: arranque" && git pull --rebase && git push
git ls-remote origin main
git ls-remote https://github.com/Silent-math/krylov.git main
```

Los dos últimos comandos tienen que dar el mismo identificador. Si uno falló (por ejemplo, la invitación sin aceptar), se arregla y se repite `git push`.

**4. Instalar.** Lee `STACK.md`, secciones 1 y 2, y sigue 2.1. Anota en `estado/producto.md` qué elegiste en cada tabla de alternativas y por qué, en una línea cada una.

## Reglas de los dos repositorios, para siempre

- `git pull --rebase` antes de cada `git push`. Nunca `--force`.
- Un `git push` actualiza los dos. Para tags: `git push origin main --tags`.
- Nadie hace commits directo en el espejo ni edita desde la web de GitHub: los dos tienen que tener exactamente la misma historia.
- El repositorio de la organización es **público**. Nada de claves (van en `.env`, que no se sube) ni datos con licencia dudosa.
- No toques los cuatro archivos de entrega de la raíz (`README.md`, `platanus-hack-project.jsonc`, `project-description.md`, `project-logo.png`): son de PC 3.

## Cómo trabajas

1. Antes de cada tarea: `git pull --rebase` y lee `estado/TABLERO.md`. **Si el tablero dice otra cosa que esta lista, manda el tablero**: PC 3 lo ajusta en cada ronda según cómo va el día.
2. Haz la tarea contra su criterio de «listo cuando». Si lleva el doble de su duración, córtala o simplifícala y anótalo.
3. Al terminar: skill `actualizar-estado`. Eso es lo que PC 3 lee.
4. Si necesitas algo de PC 2 que todavía no existe, sigue con el ejemplo fijo de `contratos/ejemplos/`. Nunca esperes.
5. **Las horas de la tabla son topes, no horas de inicio (D-29).** Empieza cada tarea apenas existan sus insumos y toma la siguiente al terminar. Si la tarea que nombra el tablero ya está hecha, sigue con la próxima de esta lista.

## Qué cambió con la decisión D-26 (léelo antes de P-01)

Ahora hay cuatro motores, uno por tarjeta: `supervivencia` (rotación), `jerarquico` (inasistencias), `estados` (crédito) y `espacial` (terreno). Para ti cambia poco, porque la forma de las respuestas es la misma:

- El ejemplo fijo de las tres tarjetas con lista se llama `analizar_tabla.json`. Sirve igual para rotación, inasistencias y crédito: cambia `motor_id` y qué factores aparecen.
- `decision_prueba.json` trae en cada caso `regla`: `tabla` (con `muestras_p`) o `espacial` (con `p`).
- **El terreno ahora trae `factores`** («qué manda en el terreno»). El panel «qué pesa» se muestra también junto al mapa.
- **Toda respuesta trae `implementacion` (`red` o `mcmc`) y `precalculado`.** Cuando `precalculado` es `true`, la tarjeta y el pie llevan el rótulo «precalculado». No es un error: es el plan B de esa tarjeta, y la pantalla tiene que decir la verdad sobre quién responde.
- **Hay un sello por motor:** `sello.json` (terreno) y `sello_<motor>.json`. Un campo en `null` no se muestra.
- **La nube** trae además `detectores`. Se dibuja solo con los dos ejes con nombre y el punto del archivo; si `detectores` trae un motivo, va en la banda roja.
- ~~**«Sube tus datos» se cortó**, con su ruta, la capa de lenguaje y la clave de Anthropic en la app.~~ **Revertido por D-34 (sáb 07:12):** el inicio es un chat; se elige el modelo, se adjunta un archivo (el del demo o uno propio) y se asigna cada columna a su papel; un modelo de lenguaje escribe la interpretación desde el JSON y nunca pone números (regla 11 nueva). Tarea P-12. El pie nunca dice «Krylov eligió N columnas»: las columnas las asigna el usuario.
- **La cartera puede llegar precalculada y con menos de 1.000 empresas.** El contador muestra `n_analisis`, sea el que sea, y el rótulo «precalculado» si corresponde.

## Tus tareas, en orden

El detalle (entregable y criterio de cada una) está en `WORKPLAN.md`, sección 6.2. El recorrido que tiene que salir está en la sección 4.3. Las vistas, en la 1.3. El formato de cada respuesta, en `contratos/CONTRATO.md`, sección 6.

| Id | Hora | Min | Qué |
|---|---|---|---|
| P-01 | 03:15 | 30 | Esqueleto: API que devuelve los ejemplos fijos, web que los pinta, y modo estático leyendo copias en `web/public/estatico/` |
| P-02 | 03:45 | 30 | **Primer despliegue** con la skill `desplegar`. Necesita al dueño de la cuenta `Silent-math`, así que se hace hoy, con todos despiertos |
| P-03 | 04:15 | 45 | Vista 1 (tarjetas, sin botón de subir archivo) y vista 2 para los casos con lista, contra `analizar_tabla.json`. Rótulo «precalculado» cuando la respuesta lo trae |
| | 05:00 | 15 | Dejar la lista nocturna y actualizar el estado. A dormir a las 05:15 |
| P-04 | 08:30 | 30 | Revisar lo nocturno. Deslizadores que se sienten bien |
| P-05 | 09:00 | 30 | Primera versión de `exportar_estatico`, con los ejemplos fijos. Redespliegue. `analizar` real de rotación se conecta cuando PC 2 avise (cerca de las 10:15) |
| P-06 | 09:30 | 50 | Mapa del terreno con su panel «qué manda»; conectar el real cuando PC 2 avise (cerca de las 11:00) |
| P-07 | 10:20 | 50 | Vista 4: tecla `M`, la nube con sus dos ejes con nombre, rojo, corrección, verde. Con el ejemplo fijo; la real llega a las 13:15 |
| P-08 | 11:10 | 40 | Vista 3: cartera con contador y tabla, con el ejemplo fijo; la real llega a las 13:15 |
| | 11:50 | 20 | Redespliegue y medición desde un teléfono. **H2 a las 12:15** |
| P-09 | 12:30 | 75 | **«¿Dónde mido?»**: pines, análisis rehechos, clic, resultado, el mapa cambia. Es lo más importante del día |
| P-10 | 14:05 | 25 | Panel del examen y pie. Conectar inasistencias (14:10) y crédito (14:50) cuando PC 2 avise |
| P-11 | 14:30 | 30 | Modo demo: teclas `M`, `T`, `C`, `L`, semilla fija, pantalla completa. `exportar_estatico` completo. Redespliegue. **H3 a las 15:00** |
| P-12 | 07:30 | 120 | **Revive con D-34.** (a) Tope 10:30: chat con los cuatro archivos del demo, selector de papeles (`GET /api/papeles`) y la respuesta dentro del chat, también en modo estático. (b) Tope 14:30: API en Render, `POST /api/analizar_archivo` y `POST /api/interpretar` (SDK `anthropic` solo en `servicio/`, clave en Render, revisión de números, plantilla si falla); interpretaciones del demo precalculadas y rotuladas. Orden de corte a las 16:00: primero la interpretación, después la subida propia |
| P-13 | 16:00 | 40 | Portada y cierre dentro de la app (tecla `L`), con QR. Vista en teléfono |
| P-14 | 16:40 | 50 | Pulido para proyector, borrar código muerto, último despliegue |
| | 17:30 | 30 | Skill `preparar-demo`. **18:00: producto terminado** |

Después de las 18:00: solo textos, orden, tamaños y errores (`WORKPLAN.md`, sección 6.6). A las 22:00, el video de respaldo con PC 3.

## Lista nocturna (el agente trabaja solo de 05:15 a 08:30)

Antes de dormir, la persona le dice al agente: *«Haz la lista nocturna de PC1_PRODUCTO.md y, cuando la termines, sigue adelantando las tareas de día en orden, contra los ejemplos fijos (D-29). Commits chicos. Si algo exige una decisión, anótalo en tu estado y pasa a lo siguiente.»*

1. **P-N1.** `web/src/decision.ts`: la regla de `contratos/CONTRATO.md`, sección 3, con una prueba que lee `contratos/ejemplos/decision_prueba.json` y exige el mismo resultado. Deslizadores de costos en la vista 2 que recalculan colores, titular y número grande con las `muestras_p` de cada unidad, sin llamar a la API.
2. **P-N2.** El mapa en canvas con `analizar_espacial.json`: bloques en tres colores según la misma regla, mediciones como puntos, leyenda en palabras.
3. **P-N3.** La nube en canvas con `nube.json`: los puntos, el archivo en rojo, los ejes rotulados en palabras.

Reglas de la noche: solo `web/` y `servicio/`; no desplegar; no instalar nada que no esté en `STACK.md`; al terminar o al bloquearse, `actualizar-estado`.

## Lo que más importa de tu trabajo

- **El modo estático no es un extra.** La URL pública del QR tiene que hacer el recorrido completo sin servidor: el plan gratuito de Render tiene una décima de procesador y se duerme. La web pide a la API y, si no responde en 1,5 segundos, lee el archivo de `web/public/estatico/`. Constrúyelo en P-01 y mantenlo al día con `exportar_estatico`.
- **Los deslizadores responden en el navegador**, no en el servidor. Por eso existe `decision.ts`.
- **El mapa y «¿Dónde mido?» van antes que todo lo demás.** Si te atrasas, el orden de corte es: cartera, panel del examen.
- **La pantalla dice quién responde.** A las 16:00 PC 2 fija, tarjeta por tarjeta, si responde la red o sale precalculada. `exportar_estatico` se corre de nuevo después de esa hora.
- **Nada tarda más de 2 segundos.** Lo que tarde más se sirve precalculado.
- **El código se revisa.** Un cuarto de la nota es «aspecto técnico», con revisión automatizada del repositorio. Componentes con nombres claros, sin código muerto, y la prueba de `decision.ts` pasando.

## Qué recibes y qué entregas

- De PC 2: `nucleo/api.py`. Primero `analizar` para rotación (10:15), después el terreno (11:00), `donde_medir` (12:00), `cartera` y `nube` (13:15), inasistencias (14:10) y crédito (14:50). Hasta que llegue cada una, sigues con su ejemplo fijo.
- De PC 3: los casos y sus datos, y los textos de pantalla (v1 a las 11:30, definitivos a las 13:40).
- Entregas: la URL pública y el demo. Avisa a PC 3 cada vez que redespliegues.
