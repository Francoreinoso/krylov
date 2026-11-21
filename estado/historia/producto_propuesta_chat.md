# Propuesta de PC 1: Krylov como chat sobre las redes amortizadas

**Escrita por PC 1 (producto), sáb 07:01. Es un borrador.** No cambia nada mientras PC 3 no la registre en `DECISIONES.md`. AGENTS.md, GLOSARIO, WORKPLAN, CONTRATO y el TABLERO son de PC 3 (regla 14), así que aquí va el texto listo para pegar.

---

## 1. Entrada para `DECISIONES.md`

Lleva el siguiente número libre. Al escribir esto la última era D-33, así que sería D-34.

**D-34 · sáb 21-nov HH:MM · Krylov responde en un chat: el usuario elige el modelo, sube un archivo, la red amortizada lo resuelve y un modelo de lenguaje cuenta el resultado en palabras.** Reemplaza lo que D-26 corta sobre «Sube tus datos», la capa de lenguaje y Anthropic.

- **Qué cambia.**
  - El inicio es un chat.
  - El usuario elige uno de los cuatro modelos según lo que quiere preguntar: `supervivencia` (¿cuánto dura y quién se va?), `jerarquico` (¿quién falta?, con tendencia propia por persona y por grupo), `estados` (¿quién cae en problemas?, mes a mes) y `espacial` (¿qué manda en el terreno y dónde mido?).
  - Adjunta un archivo: uno de los cuatro del demo o uno propio.
  - Asigna cada columna a su papel en el modelo, con un selector que la app rellena según el tipo de columna.
  - La red del motor responde en milisegundos con la misma forma que `analizar`. La respuesta (titular, número grande, tres colores, deslizadores, qué pesa, examen, semáforo) se pinta dentro del chat.
  - Un modelo de lenguaje escribe la interpretación de ese JSON.
- **Por qué.** El valor de amortizar está en que **cualquier archivo de la misma familia** se responde al instante, no solo el del demo. Con un solo archivo por motor, eso no se veía en pantalla. Las redes que entrenan desde la madrugada ya son el motor de modelado del data scientist artificial; el chat solo lo deja a la vista.
- **El motor no depende del caso, pero sí del esquema.** Cada red se entrenó con papeles fijos. `supervivencia`: id, evento, tiempo, grupo, exactamente 3 efectos, 1 efecto suave y 4 encuestas ordinales de 1 a 4 (`nucleo/supervivencia.py`, `N_EFECTOS`, `N_ENCUESTAS`). Los papeles de los otros tres motores los confirma PC 2. Un archivo con otro número de columnas por papel nunca lo vio la red al practicar: el semáforo responde `rojo_modelo` y dice qué falta. **Los entrenamientos en curso no cambian.**
- **El modelo de lenguaje solo interpreta.**
  - No elige el motor, no calcula y no inventa cifras.
  - Recibe el JSON de la respuesta y devuelve un texto corto.
  - El servicio revisa que cada número del texto esté en el JSON. Si alguno no está, o si no hay clave o no hay internet, se muestra la plantilla de `casos/textos.yaml`.
  - La clave vive en una variable de entorno de Render y nunca entra al repositorio.
- **Dónde viven las redes.**
  - `validar-motor` las exporta a `motor/artefactos/<motor_id>/` (`codificador.onnx` y `.onnx.data`, `flujo.npz`, `config.json`, `sello.json`, `nube.npz`), y esa carpeta se versiona.
  - `nucleo/` las carga con `onnxruntime` y NumPy, sin `torch`.
  - La API de Render se construye desde el espejo y trae esos archivos. Un archivo subido va a `POST /api/analizar_archivo` en Render.
  - Vercel solo sirve la web y las respuestas precalculadas de los archivos del demo.
  - Ninguna red corre en el navegador.
- **Modo estático.** Los cuatro archivos del demo tienen su respuesta y su interpretación precalculadas en `web/public/estatico/`, y la interpretación va rotulada. El QR y el escenario hacen el recorrido completo sin servidor. La subida de un archivo propio funciona solo cuando la API responde; si no responde, el chat lo dice.
- **Contrato** (cambio con aviso a los tres roles; detalle en la sección 4):
  - `nucleo/api.py` suma `papeles(motor_id)` y `analizar_archivo(motor_id, tabla, columnas, costos)`.
  - `servicio/` suma `POST /api/analizar_archivo` y `POST /api/interpretar`.
  - Lo que ya existe no cambia de forma.
- **Qué no cambia:** los cuatro motores y sus modelos generativos, los entrenamientos y sus horas, el MCMC como referencia y plan B (rotulado «precalculado»), los tres colores como decisiones, los deslizadores en el navegador (`decision.ts`), el semáforo, la nube, «¿Dónde mido?», la cartera, la regla de cifras registradas y el cierre a las 18:00.
- **Riesgos.**
  - Render gratis tiene 0,1 de procesador y 512 MB, y se duerme. Se mide la red con un archivo de 2.000 filas en Render; si pasa de 2 s, el plan B es Funciones de Python en Vercel (`STACK.md`, 2.6).
  - GitHub no acepta archivos de más de 100 MB. PC 2 confirma el tamaño de `codificador.onnx.data`.
  - El modelo de lenguaje tarda unos segundos: los números salen primero y el texto llega después, sin bloquear.
  - Los archivos subidos caen fuera de lo que la red conoce mucho más que los del demo, así que los dos detectores de la nube tienen que correr también sobre ellos.
- **Orden de corte**, si a las 16:00 no está: primero la interpretación del modelo de lenguaje (queda la plantilla), después la subida de un archivo propio (quedan los cuatro del demo dentro del chat). El chat con los archivos del demo no se corta.
- **Lo que se gana, dicho:** el jurado ve que la misma red responde un archivo que no es el del demo, y Anthropic pasa a estar integrado de verdad, si funciona a las 18:00.

· Propuesta de PC 1, decisión del equipo.

---

## 2. Cambios a `AGENTS.md`

### «Qué es», párrafo «Cómo funciona», al final

Agregar:

> En pantalla, Krylov es un **chat**. El usuario elige el modelo según lo que quiere preguntar, adjunta un archivo (uno de los del demo o uno propio) y asigna cada columna a su papel en el modelo. La red de ese motor responde en milisegundos, y un modelo de lenguaje cuenta el resultado en palabras. Los números salen siempre del motor (D-34).

Y en el punto 4 de las cuatro piezas, cambiar «para cualquier archivo de la misma familia: el del demo o cada una de las 1.000 empresas de la cartera» por:

> para cualquier archivo con el mismo esquema: el del demo, uno que suba el usuario o cada una de las 1.000 empresas de la cartera.

### «Qué se construye»

Reemplazar el punto 1 por:

> 1. **Inicio · chat «¿Qué quieres saber?»** Se elige uno de los cuatro modelos (con su pregunta en palabras), se adjunta un archivo (los cuatro del demo están precargados; también se puede subir uno propio) y se asigna cada columna a su papel. La app sugiere la asignación según el tipo de columna y el usuario la confirma.

En el punto 2 («Respuesta»), agregar al principio:

> Se pinta dentro del chat. Debajo de los números va **la interpretación**: un texto corto escrito por un modelo de lenguaje a partir del JSON del motor, o la plantilla si no hay conexión.

### «Qué NO se construye»

Reemplazar el primer punto por:

> - Un modelo de lenguaje que elija el motor, calcule o ponga números. Tampoco pregunta libre que se traduzca sola a un motor: el usuario elige el modelo.
> - Calce automático de columnas por su nombre: las columnas se asignan a sus papeles con el selector.

Quitar «un chat» del punto «Cuentas de usuario, base de datos, panel de administración, un chat, una quinta vista». Queda: «Cuentas de usuario, base de datos, panel de administración, una quinta vista».

### «Contratos»

Agregar al punto `amortizacion` → `producto`:

> Desde D-34, además: `papeles(motor_id)` (los papeles de columna que recibe cada red, con cantidad y tipo) y `analizar_archivo(motor_id, tabla, columnas, costos)`, que responde un archivo subido con la misma forma que `analizar`.

Agregar un punto:

> - **Interpretación.** `servicio/` llama al modelo de lenguaje con el JSON de la respuesta (`POST /api/interpretar`). La clave va en una variable de entorno de Render. Para los archivos del demo, la interpretación se precalcula en `web/public/estatico/`.

### «Sponsors», fila Anthropic

Reemplazar por:

> | Integrado en la app y herramienta con que se construyó | Anthropic | Un modelo de Claude escribe la interpretación de cada respuesta (D-34). Solo se dice si funciona a las 18:00; si no, vuelve a ser solo la herramienta con que se construyó. Claude Code construyó el producto |

### Reglas

- **Regla 7**, agregar al final: «Los números de una respuesta aparecen en menos de 2 segundos. La interpretación del modelo de lenguaje llega después y no los bloquea.»
- **Regla 8**, agregar: «Incluida la interpretación de los archivos del demo, precalculada y rotulada. Subir un archivo propio exige la API; si no responde, el chat lo dice.»
- **Regla 11**, reemplazar por:
  > 11. **El modelo de lenguaje solo interpreta.** Todo número sale de un motor. El modelo de lenguaje recibe el JSON del motor y escribe un texto corto: no elige el motor, no calcula y no agrega cifras. El servicio revisa que cada número del texto esté en el JSON; si no está, o si no hay clave o internet, se muestra la plantilla de `casos/textos.yaml`. *Es la respuesta a «¿no es un chat con un CSV?»: el chat es la puerta, y la respuesta la da una red que practicó con millones de casos simulados.*

---

## 3. Cambios a `GLOSARIO.md`

En «Lo que se ve en pantalla», agregar:

- **Chat.** La puerta de entrada de Krylov. Se elige el modelo, se adjunta un archivo y se asignan las columnas. La respuesta aparece dentro de la conversación.
- **Papel de una columna.** Lo que una columna significa para el modelo: el tiempo, el evento, el grupo, un factor, una encuesta. Cada modelo pide sus papeles, en una cantidad fija.
- **Interpretación.** El texto corto que acompaña a una respuesta. Lo escribe un modelo de lenguaje leyendo los números del motor y no agrega números propios. Sin conexión, se usa la plantilla.

En la tabla de jerga, agregar la fila:

| Inferencia amortizada sobre un archivo subido | «La red que practicó responde tu archivo al instante» |

---

## 4. Contrato (`contratos/CONTRATO.md`): lo que se agrega

```python
# nucleo/api.py (PC 2)
def papeles(motor_id: str) -> dict:
    """Papeles de columna que recibe la red del motor."""
    # {"motor_id": "supervivencia", "papeles": [
    #    {"papel": "tiempo", "cantidad": 1, "tipo": "entero", "texto": "Años en la empresa"},
    #    {"papel": "efectos", "cantidad": 3, "tipo": "numero", "texto": "Factores"}, ...],
    #  "caso_base": "rotacion"}       # de dónde salen rótulos, unidad y costos por omisión

def analizar_archivo(motor_id: str, tabla: "pandas.DataFrame | bytes", columnas: dict,
                     costos: dict | None = None, mediciones: list[dict] = ()) -> dict:
    """Misma forma que analizar(). Arma un caso en memoria con el caso base del motor,
    `columnas` en lugar de las del YAML y la tabla subida, y llama al analizar del motor."""
```

```
# servicio/ (PC 1)
GET  /api/papeles/{motor_id}
POST /api/analizar_archivo     multipart: archivo, motor_id, columnas (JSON), costos (JSON)
POST /api/interpretar          JSON de una respuesta → {"texto": str, "origen": "modelo" | "plantilla"}
```

`analizar_archivo` devuelve `semaforo.estado = "rojo_datos"` o `"rojo_modelo"` con su motivo cuando el archivo no calza (faltan papeles, cantidades distintas o valores fuera de rango). Nunca lanza un error al usuario.

---

## 5. Otros archivos que PC 3 pone al día

- `WORKPLAN.md`: P-12 revive como «Chat, subida y asignación de papeles», más una tarea de PC 2 para `papeles` y `analizar_archivo`.
- `PC1_PRODUCTO.md`: la sección «Qué cambió con D-26» y la fila P-12.
- `STACK.md`: el SDK de Anthropic en `servicio/` y la variable `ANTHROPIC_API_KEY` en Render.
- `pitch/GUION.md`: la respuesta a «¿no es un chat con un CSV?» y, si se quiere, un momento del demo donde se sube un archivo que no es el del demo.
- `estado/TABLERO.md`: la tarea nueva de PC 2 y la de PC 1.
- `pitch/CIFRAS.md`: el tiempo de `analizar_archivo` en Render, cuando se mida.
