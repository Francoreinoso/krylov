# Contrato entre los tres computadores

**Estado: vigente desde el pivote a minería (D-37, sáb 12:10). La forma de las respuestas es la misma que se congeló en H0; D-37 agregó un campo opcional (`curva`) y un formato de archivo (series). Otros cambios, solo con una entrada en `DECISIONES.md` y aviso a los otros dos roles.**

> Hackathon: proyecto chico, el producto se termina el sábado a las 18:00. Este contrato es lo mínimo para que nadie espere a nadie. No lo amplíes.

Para qué sirve: que `producto` avance desde el minuto cero con ejemplos fijos, sin esperar a `amortizacion`, y que agregar un caso de uso no toque código.

Palabras que se usan en todo el archivo (el resto está en `GLOSARIO.md`):

- **Motor**: un modelo generativo de una familia de datasets, más la red que aprendió a invertirlo con simulaciones (inferencia basada en simulación, amortizada). Hay cinco, uno por decisión de la mina: `espacial` (leyes y arsénico), `deformacion` (taludes y relaves), `cinetica` (flotación), `desgaste` (flota) y `sismico` (sismicidad). Los cuatro últimos se llaman aquí **motores de series**. El modelo de cada uno está en `WORKPLAN.md`, sección 11.
- **Modelo generativo**: las reglas con que Krylov inventa minas para practicar.
- **Caso**: una decisión de la mina resuelta con un motor, un archivo de datos y sus costos. Un archivo en `casos/`.
- **Unidad**: aquello sobre lo que se decide (un bloque de roca, un sector del muro, una línea de la planta, un camión, un sector de la mina).
- **Actuar**: lo que la mina haría si la respuesta es «sí» (apartar, cerrar, ajustar, adelantar la mantención, mantener cerrado). Cada caso le pone su nombre.

Los JSON de `contratos/ejemplos/` son datos fijos para maquetar: sus números son inventados y no se muestran en el pitch; en pantalla llevan el rótulo «ejemplo». `generar.py` escribe los que definen la forma (`analizar_tabla.json`, `analizar_espacial.json`, `analizar_rojo.json`, `decision_prueba.json`, `donde_medir.json`, `nube.json`, sellos); `generar_mineria.py` escribe `casos.json` y los cuatro `analizar_<caso>.json` con contenido minero.

Convenciones: campos en español y `snake_case`; plata en la moneda del caso, sin formato; tiempos de cómputo en milisegundos; probabilidades entre 0 y 1.

## 1. Datos de entrada (CSV)

Separador coma, punto decimal, primera fila con encabezados.

**Motor `espacial` (caso `leyes`).** Una fila por muestra: columnas `x`, `y`, `valor` y, opcional, `tendencia` (con ella el caso trae además `grilla`, un CSV con `x`, `y` y esa misma tendencia para cada celda). Entre 30 y 400 filas. El banco se lleva a una grilla fija de 32×32 celdas (una sola escala para los dos ejes; si dos muestras caen en la misma celda se promedian). Las unidades son las celdas de esa grilla, que en pantalla se llaman bloques.

**Motores de series.** Una fila por medición, en formato largo. Papeles comunes a los cuatro:

- `unidad`: a quién pertenece la medición (el sector, la línea, el camión).
- `tiempo`: cuándo se midió, en las unidades que declare el caso (`unidad_tiempo`).
- `valor`: lo medido.

| Motor | `tiempo` | `valor` | Además | Rangos que el motor conoce |
|---|---|---|---|---|
| `deformacion` | horas (o días) desde que parte la ventana | desplazamiento acumulado | `horizonte` del caso, en las unidades de `tiempo` | 6 a 80 sectores; 24 a 200 lecturas por sector, con hasta 15% faltantes |
| `cinetica` | minutos en la línea al salir de cada celda | recuperación acumulada, de 0 a 1 | `umbral` (la meta) y `tiempo_final` del caso | 2 a 16 líneas de 5 a 12 celdas; de 3 celdas medidas por línea al total |
| `desgaste` | horas de operación | indicador de desgaste (1,0 = falla) | `covariables` (una columna de exigencia) y `horizonte_por_unidad` (horas hasta la mantención), repetidas en las filas de cada camión | 8 a 120 camiones; 3 a 20 mediciones por camión, a intervalos irregulares |
| `sismico` | horas desde la tronadura | magnitud | `umbral` (magnitud fuerte), `magnitud_minima` y `horizonte` del caso | 2 a 16 sectores; ventana observada de 2 a 24 horas; hasta 300 sismos por sector (un sector sin sismos vale) |
| `espacial` | — | lo medido en cada lugar (`x`, `y`) | `umbral` del caso | 30 a 400 muestras |

**De dónde salen los rangos (D-38).** Cada modelo sortea el tamaño del dataset como un nivel más (`WORKPLAN.md`, sección 11, grupo `Diseño del dataset`). Los rangos de esta tabla son los del `config.json` de cada motor (clave `diseno`), que es la fuente: si una validación los achica, cambian ahí y aquí. `papeles(motor_id)` los publica en `rangos`.

**Qué unidades se deciden:** todas. Ya no se vacía una parte de las respuestas: lo que se decide es algo que todavía no pasa (¿cede en las próximas 12 horas?).

**La verdad escondida.** Cada archivo simulado tiene al lado `datos/demo/<caso>_verdad.csv`, con una fila por unidad y lo que pasó de verdad (la columna la nombra `verdad_columna` del caso). **Ese archivo no entra al motor**: sirve solo para el examen (sección 3). En `leyes` es `leyes_verdad.csv`, con la ley verdadera de cada bloque.

Bajo el mínimo de la tabla, o con series demasiado cortas, la respuesta es `rojo_datos` con un motivo que nombra lo que hay y lo que el motor conoce («hay 3 camiones y practiqué con flotas de 8 a 120»). Sobre el máximo, el motor toma una submuestra con semilla fija (de unidades, o de lecturas dentro de cada unidad) y responde en `amarillo`, con el aviso en `semaforo.motivo`.

## 2. Lo que `amortizacion` le entrega a `producto` (`nucleo/api.py`)

Dueño: `amortizacion`. `producto` no toca motores ni redes: llama a estas funciones puras, que devuelven diccionarios listos para convertir a JSON, **con la misma forma que los ejemplos fijos**.

```python
# nucleo/api.py  — solo NumPy, PyYAML y onnxruntime. Nunca importa torch, zuko, jax ni numpyro.
def casos() -> dict: ...
def analizar(caso: str, transformaciones: list[str] = (), costos: dict | None = None,
             mediciones: list[dict] = ()) -> dict: ...
def donde_medir(caso: str, mediciones: list[dict] = ()) -> dict: ...        # solo `espacial`
def nube(caso: str, transformaciones: list[str] = ()) -> dict: ...          # solo donde el motor la entregue
def sello(motor_id: str) -> dict: ...
def papeles(motor_id: str) -> dict: ...
def analizar_archivo(motor_id: str, tabla: "pandas.DataFrame | bytes", columnas: dict,
                     costos: dict | None = None, mediciones: list[dict] = ()) -> dict: ...
```

`cartera()` se cortó con el pivote (D-37) y se retira en la tarea A-32.

**`papeles(motor_id)`.** Los papeles de columna que recibe la red del motor, con `minimo`, `maximo`, tipo y textos, y el caso base de donde salen rótulos, unidad y costos por omisión (el primer caso de `casos/INICIO` que usa ese motor):

```json
{"motor_id": "desgaste", "caso_base": "flota",
 "papeles": [{"papel": "unidad", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "texto",
              "texto": "Camión", "texto_largo": "El identificador del camión al que pertenece cada muestra"},
             {"papel": "tiempo", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "numero",
              "texto": "Horas de operación", "texto_largo": "Horas de operación del camión al tomar la muestra"},
             {"papel": "valor", "cantidad": 1, "minimo": 1, "maximo": 1, "tipo": "numero",
              "texto": "Desgaste medido", "texto_largo": "El indicador de desgaste de esa muestra; 1,0 es la falla"},
             {"papel": "covariables", "cantidad": 1, "minimo": 0, "maximo": 1, "tipo": "numero",
              "texto": "Exigencia de la ruta", "texto_largo": "Qué tan exigente es la ruta del camión: pendiente y carga"}],
 "rangos": {"unidades": {"minimo": 8, "maximo": 120}, "lecturas_por_unidad": {"minimo": 3, "maximo": 20},
            "frase": "Practiqué con flotas de 8 a 120 camiones, con 3 a 20 muestras por camión."}}
```

Un papel con `minimo: 0` es opcional: la red practicó también sin él.

`rangos` (D-38, campo nuevo y opcional: la web puede ignorarlo) trae los tamaños de dataset con que practicó la red, leídos del `config.json` del motor: los mismos de la tabla «Rangos que el motor conoce» de la sección 1. `frase` está lista para mostrarse. En `sismico` trae además `ventana_horas`; en `espacial`, solo `muestras`.

**`analizar_archivo(...)`.** Misma forma que `analizar()`. Arma un caso en memoria con el caso base del motor, `columnas` en lugar de las del YAML y la tabla subida. `columnas` acepta papel → nombre de columna, o la forma con transformación:

```json
{"unidad": {"columnas": ["equipo"]},
 "tiempo": {"columnas": ["minutos_operados"], "transformacion": {"nombre": "dividir", "por": 60}},
 "valor":  {"columnas": ["fe_ppm"], "transformacion": {"nombre": "dividir", "por": 120}},
 "umbral": 1.0}
```

Los números del caso (`umbral`, `horizonte`, `tiempo_final`, `magnitud_minima`) pueden venir en `columnas`; si no vienen, valen los del caso base. Transformaciones de la lista cerrada, en `nucleo/preproceso.py`: `dividir` (`por`), `anios_desde_fecha` (`hasta`), `dias_entre` (`desde`, otra columna), `si_no_a_binario`, `reescalar_ordinal` (`de`, `a`), `log` y `categoria_a_codigo`. Una transformación fuera de la lista da `rojo_datos` con su motivo. Si el archivo no calza, devuelve `rojo_datos` o `rojo_modelo` con su motivo; nunca lanza un error al usuario.

- `mediciones` es una lista de `{x, y, valor}` que se agregan a los datos del caso antes de responder (solo `espacial`). Así se simula «perforé aquí y salió esto».
- Todas llevan semilla fija: misma entrada, misma salida.

**Implementaciones de un motor.** Una variable de entorno por motor, sin cambiar código:

| Variable | Valores |
|---|---|
| `KRYLOV_MOTOR_ESPACIAL` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_DEFORMACION` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_CINETICA` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_DESGASTE` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_SISMICO` | `mcmc` (por defecto) o `red` |

- `red`: el codificador (ONNX) resume el dataset y los flujos normalizadores condicionales entregan 32 muestras del posterior, muestreadas en NumPy. En `espacial`, además, la cabeza de mapa entrega media y margen por bloque. En los motores de series hay dos flujos: uno para los parámetros globales (`flujo.npz`) y uno chico para los de cada unidad (`flujo_local.npz`). Se activa motor por motor cuando pasa `validar-motor`.
- `mcmc`: el posterior del MCMC de referencia (NUTS), **precalculado** para el archivo del demo y guardado en `motor/artefactos/<motor_id>/mcmc/<clave>.npz` (globales y locales). `nucleo/` solo lee esas muestras y aplica la misma función «lo que se decide». Toda respuesta que sale de aquí lleva `implementacion: "mcmc"` y `precalculado: true`, y la pantalla lo rotula. Es el plan B de cada tarjeta, y existe primero.
- Si un motor no tiene ni red validada ni muestras precalculadas para la clave pedida, `analizar` devuelve un error con frase en español y `producto` sigue con el ejemplo fijo, rotulado «ejemplo».

**Un solo preprocesamiento por motor.** La función que transforma los datos es la misma para el simulador de entrenamiento (`motor/`) y para el servicio. Tiene una prueba que pasa el mismo arreglo por los dos caminos y da idéntico.

## 3. Capa de decisión (`nucleo/decision.py` y `web/src/decision.ts`)

**No cambió con el pivote.** Dueño de la definición: `amortizacion`. Hay dos copias de la misma cuenta de diez líneas: Python (la de referencia) y TypeScript (para que los deslizadores de costos respondan sin esperar a la red). Una prueba en cada lado lee `contratos/ejemplos/decision_prueba.json` y exige el mismo resultado. Cada caso de prueba trae `regla`: `tabla` (con `muestras_p`) o `espacial` (con `p`).

- **Costos del caso.** `C_si` = lo que cuesta actuar sobre una unidad que no lo necesitaba (`costos.falso_si`). `C_no` = lo que cuesta no actuar sobre una que sí (`costos.falso_no`).
- **Punto de corte** = `C_si / (C_si + C_no)`. Si la probabilidad de «sí» supera ese valor, conviene actuar.
- **Los tres colores son decisiones, no pronósticos:**
  - `actuar`: conviene actuar, y saber más casi seguro no cambiaría la decisión.
  - `no_actuar`: no conviene actuar, y saber más casi seguro no la cambiaría.
  - `en_duda`: la decisión podría cambiar. **Regla única para todos los motores: hay más de 10% de probabilidad de que la decisión cambie al saber más.**
- **Cómo se calcula «podría cambiar».**
  - Regla `tabla` (los cuatro motores de series): cada unidad trae `muestras_p`, 32 versiones creíbles de su probabilidad (una por muestra del posterior). `p` es el promedio. La unidad está `en_duda` si más de 10% de las muestras caen al otro lado del punto de corte.
  - Regla `espacial` (`leyes`): cada bloque trae `p`, la probabilidad de superar el límite del caso. Si se actúa, la probabilidad de equivocarse es `1 − p`; si no se actúa, es `p`. Está `en_duda` si esa probabilidad supera 10%.
- **Lo que cuesta no saber** (en pantalla, el número grande):
  - `tabla`: `duda = min(C_si·(1 − p), C_no·p) − promedio sobre muestras de min(C_si·(1 − p_s), C_no·p_s)`. Nunca es negativo y vale casi cero en las unidades que no están en duda.
  - `espacial`: `duda = min(C_si·(1 − p), C_no·p)`. Aquí toda la duda se despeja muestreando el bloque.
  - Total = suma de `duda` sobre las unidades.
- **Qué significa `p` en cada caso:**

  | Caso | `p` de una unidad |
  |---|---|
  | `leyes` | Probabilidad de que el bloque supere el límite de arsénico |
  | `taludes` | Probabilidad de que el sector ceda dentro del horizonte |
  | `flotacion` | Probabilidad de que la línea termine bajo la meta de recuperación |
  | `flota` | Probabilidad de que el camión falle antes de su próxima mantención |
  | `sismicidad` | Probabilidad de al menos un temblor fuerte en el sector dentro del horizonte |

- **Qué pesa**: sale del posterior de los parámetros globales. Por factor, la dirección y una etiqueta de `certeza`: `seguro` si al menos 95% de las versiones creíbles coinciden en el signo, `probable` si al menos 80%, `no_se_sabe` en otro caso.
- **Examen.** Compara lo que Krylov dijo con la verdad escondida. `leyes`: esconde 20% de las muestras y cuenta cuántas caen dentro del rango. Motores de series: con `<caso>_verdad.csv`, por tramos de probabilidad («cuando dijimos cerca de 30% de riesgo, cedió el 28%»). Con datos simulados la frase lo dice. La exactitud con datos reales (el caso `terreno`, y los archivos reales abiertos si calzan) es la única que se dice en voz alta sin ese aviso.

## 4. Caso (`casos/<nombre>.yaml`)

Dueño: `seguimiento`. `casos/INICIO` lista, uno por línea y en orden, los casos que aparecen como tarjetas; el primero abre el demo. Los ejemplos vivos son los cinco archivos de `casos/`; aquí, el formato de un caso de series:

```yaml
nombre: ejemplo_formato
tarjeta:
  titulo: "¿Qué camión paro antes de que falle?"
  empresa_o_industria: "Flota de camiones · mantención"   # el subtítulo de la tarjeta; nunca el nombre de una minera
  sponsor: null                      # siempre null desde D-37
  oculto: false                      # true: no aparece en el inicio (el archivo que no alcanza)
pregunta: "¿A qué camiones conviene adelantarles la mantención?"
motor: desgaste                      # espacial | deformacion | cinetica | desgaste | sismico
unidad: { singular: camión, plural: camiones }
rotulos:
  actuar: "Conviene adelantar la mantención"     # sin número gramatical: se usa en «En 5 camiones, conviene…»
  no_actuar: "Llega a su mantención"
  en_duda: "No sabemos: tomar otra muestra"
  costo_de_no_saber: "Lo que te cuesta no saber"
  donde_medir: "¿Dónde perforo?"     # opcional, solo `espacial`: el texto del botón
columnas:                            # el papel de cada columna en el modelo del motor
  unidad: unidad
  tiempo: tiempo
  valor: valor
  covariables: [exigencia]           # desgaste
  horizonte_por_unidad: horas_a_mantencion    # desgaste
  umbral: 1.0                        # el límite (desgaste, cinetica, sismico, espacial)
  horizonte: 12                      # deformacion, sismico: en las unidades de `tiempo`
  tiempo_final: 28                   # cinetica
  magnitud_minima: -1.0              # sismico
  unidad_tiempo: "horas de operación"
  unidad_valor: "desgaste (1 = falla)"
  eje_tiempo: "Horas de operación"   # los nombres de los ejes de la curva
  eje_valor: "Desgaste"
  extra: []
  elegidas_por: equipo               # `equipo` en los casos del demo; `usuario` en un archivo subido
# espacial: { x: x, y: y, valor: as_ppm, umbral: 500, unidad_valor: "ppm de arsénico", transformacion: log }  (más `tendencia` y `grilla:` si aplica)
etiquetas: { ritmo: "Qué tan rápido se desgasta la flota", exigencia: "Ruta exigente" }   # nombre en pantalla de cada factor
costos:
  falso_si: { valor: 12000, min: 2000, max: 60000, etiqueta: "Costo de adelantar una mantención que no hacía falta", tipo: hipótesis, cifra: K-51 }
  falso_no: { valor: 90000, min: 20000, max: 400000, etiqueta: "Costo de una falla en plena rampa", tipo: hipótesis, cifra: K-52 }
  medicion: { valor: 1500, etiqueta: "Costo de una muestra más", tipo: hipótesis, cifra: K-24 }   # solo espacial
moneda: USD
dataset: datos/demo/flota.csv
verdad: datos/demo/flota_verdad.csv          # opcional: habilita el examen
verdad_columna: falla_antes_de_la_mantencion
origen_datos: "Flota simulada: 40 camiones con sus muestras de aceite. No son datos de ninguna mina."   # se ve en pantalla tal cual
sintetico: true                              # si es true, la interfaz muestra «simulado»
```

Reglas: `cifra` es el id de una fila de `pitch/CIFRAS.md`. `min` y `max` son los extremos del deslizador. El servicio no carga un caso con costos en `null` y lo dice al arrancar; los demás casos siguen funcionando. Los rótulos de los tres colores se escriben sin número gramatical («Conviene cerrar», no «Conviene cerrarlo»), porque las plantillas los usan después de «En N sectores,».

## 5. Capa de lenguaje

**No cambió con el pivote (D-34, D-35).** El modelo de lenguaje hace dos cosas y ninguna más:

- **Propone el calce.** `servicio/` le manda los papeles del motor (`papeles(motor_id)`, con `texto_largo`) y un resumen de cada columna del archivo: nombre, tipo, valores distintos, rango, porcentaje vacío y tres valores de ejemplo. Nunca filas completas. Devuelve, por papel, `columnas`, `transformacion` (de la lista cerrada), `motivo` y `confianza`, más `no_usadas`. El servicio valida que cada columna exista y cada transformación esté en la lista; el usuario ve el calce y lo confirma antes de `analizar_archivo`. Sin clave o sin internet, el calce sale de una regla por tipo de columna (`origen: "regla"`).
- **Interpreta.** `servicio/` lo llama con el JSON de una respuesta (`POST /api/interpretar`) y devuelve un texto corto. No elige el motor, no calcula y no agrega cifras: el servicio revisa que cada número del texto esté en el JSON; si alguno no está, o si no hay clave (`ANTHROPIC_API_KEY`, variable de entorno de Render, nunca en el repositorio) o no hay internet, devuelve la plantilla.

`titular` y `en_palabras` salen siempre de las plantillas de `casos/textos.yaml`, escritas por `seguimiento` y llenadas con los números del JSON: son el respaldo y lo que se ve primero. Para los archivos del demo, el calce y la interpretación se precalculan en `web/public/estatico/` y van rotulados.

## 6. API HTTP y modo estático (backend → frontend)

Base `/api`. Errores: `{"error": "frase en español", "codigo": "..."}` con estado 4xx; nunca una traza.

**Regla del modo estático.** Toda respuesta que el demo necesita existe también como archivo en `web/public/estatico/`, generado por `uv run python -m servicio.exportar_estatico` y subido a git. La web pide primero a la API; si no hay API configurada, no responde en 1,5 segundos o la URL trae `?estatico=1`, lee el archivo. Así la URL pública del QR aguanta a toda la sala sin servidor, y el escenario funciona sin internet.

| Ruta | Para qué | Archivo estático | Ejemplo fijo |
|---|---|---|---|
| `GET /api/casos` | Vista 1 | `casos.json` | `casos.json` |
| `POST /api/analizar` | Vistas 2 y 3 | `analizar/<clave>.json` | `analizar_espacial.json` (forma del mapa), `analizar_tabla.json` (forma de la lista), `analizar_taludes.json`, `analizar_flotacion.json`, `analizar_flota.json`, `analizar_sismicidad.json` (lista con `curva`), `analizar_rojo.json` |
| `POST /api/donde-medir` | Vista 2, `leyes` | `donde-medir/<clave>.json` | `donde_medir.json` |
| `POST /api/nube` | Vista 3, donde exista | `nube/<clave>.json` | `nube.json` |
| `GET /api/sello?motor=` | Pie y panel | `sello/<motor>.json` | `sello.json` |
| `GET /api/papeles/{motor_id}` | Chat | `papeles/<motor_id>.json` | — |
| `POST /api/analizar_archivo` | Chat, archivo propio | — (exige la API; si no responde, el chat lo dice) | misma forma que `analizar` |
| `POST /api/interpretar` | Chat | `interpretar/<clave>.json` para los archivos del demo, rotulado | — |
| `POST /api/calce` | Chat, antes de analizar | `calce/<caso>.json` para los archivos del demo, rotulado | — |

`<clave>` = nombre del caso, más `__` y cada transformación o medición en orden (`leyes__A-alto`). `exportar_estatico` escribe todas las claves que el recorrido del demo puede pedir: cada caso del inicio, `leyes_pocos`, y para `leyes` las tres mejores candidatas con sus tres resultados posibles.

### `POST /api/analizar`

Petición: `{ "caso": "taludes", "transformaciones": [], "costos": null, "mediciones": [] }`.

Respuesta de los casos de lista (los cuatro motores de series; el ejemplo completo está en `ejemplos/analizar_taludes.json`). **Es la misma forma para los cuatro**: cambia `motor_id`, qué factores aparecen y lo que dibuja la curva.

```json
{
  "caso": "taludes", "motor_id": "deformacion", "implementacion": "red", "precalculado": false,
  "titular": "5 sectores están en duda. No saber te cuesta cerca de 169 mil dólares.",
  "costo_de_no_saber": { "valor": 168838, "moneda": "USD" },
  "costos": { "falso_si": { "valor": 120000, "min": 20000, "max": 500000, "etiqueta": "Costo de cerrar un sector que estaba estable (un turno sin producir ahí)" },
              "falso_no": { "valor": 2500000, "min": 500000, "max": 10000000, "etiqueta": "Costo de un derrumbe con el sector abierto (equipos y producción)" } },
  "punto_de_corte": 0.046,
  "unidad": { "singular": "sector", "plural": "sectores" },
  "unidades": [ { "id": "S-14", "etiqueta": "S-14", "p": 0.31, "rango_bajo": 0.08, "rango_alto": 0.62,
                  "muestras_p": [0.22, 0.35, 0.29], "estado": "en_duda", "duda": 21250.0,
                  "curva": { "t": [0.5, 1.0], "y": [0.1, 0.3], "ahora": 48.0,
                             "t_banda": [48.0, 49.0], "bajo": [3.9, 4.0], "medio": [3.9, 4.2], "alto": [3.9, 4.6],
                             "limite": null, "eje_t": "Horas", "eje_y": "Milímetros que se ha movido",
                             "marca": { "texto": "Faltan entre 9 y 31 horas", "bajo": 9.0, "medio": 16.0, "alto": 31.0 } } } ],
  "resumen_colores": { "actuar": 7, "no_actuar": 24, "en_duda": 5 },
  "factores": [ { "nombre": "fraccion_acelerando", "etiqueta": "Cuánta parte del muro se está acelerando", "direccion": "sube",
                  "efecto": 0.21, "rango_bajo": 0.12, "rango_alto": 0.33, "certeza": "seguro" } ],
  "columnas": { "usadas": ["unidad", "tiempo", "valor"], "disponibles": 3, "elegidas_por": "equipo", "explicacion": "" },
  "semaforo": { "estado": "verde", "motivo": "", "propuesta": null },
  "examen": { "tipo": "verdad_escondida", "n": 36, "frase": "", "tramos": [ { "dijimos": 0.05, "paso": 0.04, "n": 24 } ] },
  "sello_resumen": { "frase": "", "medido": false },
  "en_palabras": ["...", "..."],
  "rotulos": { "actuar": "Conviene cerrar", "no_actuar": "Puede seguir abierto", "en_duda": "No sabemos: seguir midiendo", "costo_de_no_saber": "Lo que te cuesta no saber" },
  "registro": ["36 sectores", "3.295 lecturas"],
  "tiempo_ms": 310, "sintetico": true, "origen_datos": "Muro simulado: 36 sectores…"
}
```

- `implementacion` es `red` o `mcmc`. Con `mcmc`, `precalculado` es `true` y la pantalla lo rotula «precalculado».
- `muestras_p` trae 32 valores por unidad, con dos decimales. Con eso la web recalcula colores, `duda` y el total al mover un deslizador, sin llamar a nadie.
- **`curva` (D-37, opcional por unidad).** Lo medido y lo que Krylov cree que viene:
  - `t`, `y`: los puntos medidos, hasta 60 (si hay más, adelgazados de forma regular). En `sismicidad`, `y` es el número acumulado de temblores.
  - `ahora`: dónde termina lo medido.
  - `t_banda`, `bajo`, `medio`, `alto`: el rango de 90% de lo que viene, desde `ahora` hasta el horizonte (o hasta el final de la línea, o hasta la próxima mantención). Entre 8 y 24 puntos.
  - `limite`: el valor de la línea horizontal (`flota`: 1,0; `flotacion`: la meta), o `null`.
  - `eje_t`, `eje_y`: los nombres de los ejes, del caso.
  - `marca`: opcional (`taludes`): cuánto falta, con su rango y un texto listo.
  - Si hay más de 60 unidades, `curva` viene solo en las 24 con más `duda` y en las que están en `actuar`; en el resto es `null`. La web dibuja la lista igual.
- `examen` va en `null` si el caso no tiene archivo de verdad. `examen.tipo` es `verdad_escondida` (series, datos simulados o reales con desenlace conocido) o `puntos_reales_escondidos` (espacial). `examen.frase` la escribe el servicio con los números de `tramos`, nunca a mano.
- `sello_resumen.medido` es `false` mientras no haya examen ni sello; la interfaz muestra entonces «exactitud en medición» y ningún porcentaje.
- En `factores`, la interfaz muestra la flecha (`direccion`) y la etiqueta de `certeza`, no el número.

En `leyes` (motor `espacial`), `unidades` va en `null`, `factores` trae «qué manda aquí» (la continuidad entre bloques vecinos, el error de cada muestra y, si el caso la tiene, la tendencia), `rotulos` puede traer `donde_medir` y la respuesta agrega:

```json
"mapa": { "nx": 32, "ny": 32, "x0": 0.0, "y0": 0.0, "lado": 7.5,
          "p": [0.02, 0.4, null], "media": [310.0, 690.0, null],
          "puntos": [ { "x": 7.2, "y": 7.2, "valor": 528 } ],
          "umbral": 500, "unidad_valor": "ppm de arsénico" }
```

`p` y `media` tienen `nx·ny` valores, fila por fila desde abajo a la izquierda; `null` marca celdas fuera del banco. La web pinta cada bloque con la misma regla de la sección 3.

Con `semaforo.estado` en `rojo_datos` o `rojo_modelo`: `costo_de_no_saber`, `unidades`, `mapa` y `factores` vienen en `null`. Con `rojo_modelo`, `semaforo.propuesta` puede traer `{ "transformacion": "...", "texto": "..." }`; si no hay corrección que proponer, va en `null` y la pantalla muestra solo el motivo.

### `POST /api/donde-medir`

Solo `espacial`. En pantalla es «¿Dónde perforo?». Petición `{ "caso": "leyes", "mediciones": [] }`. Respuesta (`ejemplos/donde_medir.json`):

```json
{
  "caso": "leyes",
  "candidatas": [ { "puesto": 1, "etiqueta": "A", "x": 23, "y": 172,
                    "valor_de_medir": 8943, "costo_medicion": 1500, "valor_neto": 7443,
                    "resultados_posibles": { "bajo": 185, "medio": 367, "alto": 727 } } ],
  "mensaje_parada": null,
  "analisis_rehechos": 480, "tiempo_ms": 990, "implementacion": "red", "precalculado": false
}
```

- `candidatas` trae las tres mejores. `valor_de_medir` es cuánto baja «lo que cuesta no saber», en promedio, si se toma una muestra ahí.
- `analisis_rehechos` es el conteo real de análisis completos que hizo falta (lugares candidatos × resultados posibles). Es la cifra que se dice en voz alta.
- Al hacer clic en una candidata, la web ofrece «sale bajo / medio / alto», llama a `analizar` con esa medición y vuelve a llamar a `donde-medir` con la misma lista.
- `mensaje_parada` aparece cuando ninguna muestra paga su costo: «Con lo que ya sabes, muestrear más no se paga».
- Si se sirve precalculado, `precalculado: true` y `tiempo_ms` es el tiempo medido de verdad al generarlo.

### `POST /api/nube`

Solo para los motores que la entreguen (hoy, ninguno de los cinco la tiene para un caso minero; el semáforo `rojo_modelo` con su motivo funciona igual). Forma: `ejemplos/nube.json`. `puntos` son datasets simulados del predictivo a priori del modelo del motor, con dos ejes con nombre que cada motor define en su `config.json`, y `archivo` es dónde cae el archivo del usuario. El segundo detector (distancia en el espacio de resúmenes del codificador contra su percentil 99) corre en los cinco motores y es el que decide `rojo_modelo`.

### `GET /api/sello?motor=espacial`

Respuesta (`ejemplos/sello.json`): el contenido de `motor/artefactos/<motor_id>/sello.json` más `frases`, una lista de oraciones sin jerga.

**Un sello por motor.** Campos de `sello.json`: `motor_id`, `implementacion`, `pasa`, `criterios`, `simulaciones_entrenamiento`, `entrenamiento_min`, `casos_validacion`, `cobertura_90`, `cobertura_90_parametros`, `cobertura_90_locales` (motores de series), `cobertura_90_peor_grupo`, `peor_grupo`, `sbc_pasa`, `cobertura_90_metodo_rapido`, `latencia_ms`, `mcmc_datasets_comparados`, `mcmc_s_por_dataset`, `mcmc_diferencia_media`, `mcmc_convergio`, `amortizacion` (`que_se_compara`, `mcmc_s`, `red_s`), `fecha`, `maquina`, `limitaciones`. Un campo sin medir va en `null` y la interfaz lo omite. **Los campos `mcmc_*` y `amortizacion` parten en `null`** (D-38): el método lento de cada motor se corre al final y `pasa` se decide sin él; `peor_grupo` y `cobertura_90_peor_grupo` son el peor tramo de tamaño del dataset. El tablero en vivo lee este archivo directamente del repositorio.

### `POST /api/analizar_archivo`, `POST /api/interpretar` y `POST /api/calce`

- `POST /api/analizar_archivo`: multipart con `archivo`, `motor_id`, `columnas` (JSON), `costos` (JSON, opcional). Responde como `POST /api/analizar`.
- `POST /api/interpretar`: el JSON de una respuesta → `{"texto": str, "origen": "modelo" | "plantilla"}`. Los números de la respuesta se muestran antes; el texto llega después y no los bloquea.
- `POST /api/calce`: multipart con `archivo` y `motor_id` → `{"calce": {papel: {"columnas": [...], "transformacion": {...} | null, "motivo": str, "confianza": "alta" | "media" | "baja"}}, "no_usadas": [...], "origen": "modelo" | "regla"}`.

## 7. Artefactos de un motor

`motor/artefactos/<motor_id>/`, uno por motor, versionados en git:

- `codificador.onnx`: lo que usa el servicio. En `espacial` incluye la cabeza de mapa. En los motores de series tiene dos salidas: el resumen del dataset y el de cada unidad.
- `flujo.npz` y, en los motores de series, `flujo_local.npz`: los pesos de los flujos normalizadores condicionales. `nucleo/flujo.py` los muestrea en NumPy; una prueba exige que, con los mismos pesos y el mismo ruido, den la misma muestra que `torch` (tolerancia de `float32`).
- `pesos.pt`: lo que usa el entrenamiento.
- `config.json`: el prior, los rangos, la arquitectura y la versión del preprocesamiento.
- `sello.json`.
- `mcmc/<clave>.npz`: muestras del posterior del MCMC de referencia para cada clave del recorrido. Es el plan B.
