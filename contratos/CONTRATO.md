# Contrato entre los tres computadores

**Estado: se congela en H0 (sáb 03:45). Después, cambios solo con una entrada en `DECISIONES.md` y aviso a los otros dos roles.**

> Hackathon: proyecto chico, el producto se termina el sábado a las 18:00. Este contrato es lo mínimo para que nadie espere a nadie. No lo amplíes.

Para qué sirve: que `producto` avance desde el minuto cero con ejemplos fijos, sin esperar a `amortizacion`, y que agregar un caso de uso no toque código.

Palabras que se usan en todo el archivo (el resto está en `GLOSARIO.md`):

- **Motor**: un modelo generativo de una familia de datasets, más la red que aprendió a invertirlo con simulaciones (inferencia basada en simulación, amortizada). Hay cuatro, uno por caso (decisión D-26): `supervivencia` (rotación), `jerarquico` (inasistencias), `estados` (crédito) y `espacial` (terreno). Los tres primeros se llaman aquí **motores de tabla**. El modelo de cada uno está en `WORKPLAN.md`, sección 11.
- **Modelo generativo**: las reglas con que Krylov inventa empresas, carteras o terrenos para practicar.
- **Caso**: una pregunta de negocio resuelta con un motor, un archivo de datos y sus costos. Un archivo en `casos/`.
- **Unidad**: aquello sobre lo que se decide (una persona, una cita, un cliente, un bloque de terreno).
- **Actuar**: lo que la empresa haría si la respuesta es «sí» (retener, confirmar la cita, no aprobar, limpiar). Cada caso le pone su nombre.

Los JSON de `contratos/ejemplos/` son datos fijos para maquetar: sus números son inventados y no se muestran en el demo ni en el pitch. Los genera `contratos/ejemplos/generar.py`.

Convenciones: campos en español y `snake_case`; plata en la moneda del caso, sin formato; tiempos en milisegundos; probabilidades entre 0 y 1.

## 1. Datos de entrada (CSV)

Separador coma, punto decimal, primera fila con encabezados.

**Motores de tabla.** Una fila por unidad. Cada caso declara en su YAML qué papel cumple cada columna en el modelo (sección 4). Común a los tres:

- **Qué unidades se deciden:** las filas con la respuesta vacía (`evento` u `objetivo`). `seguimiento` prepara cada archivo dejando vacía la respuesta en un **20% de las filas elegido al azar, con semilla fija y sin mirar la respuesta**, y guarda la verdad de esas filas en `datos/demo/<caso>_verdad.csv` (columnas `id`, `objetivo`). Ese archivo no entra al motor: sirve solo para el examen con datos reales (sección 3).
- Nunca se vacía según la respuesta (por ejemplo «los que siguen en la empresa»): rompe el caso.
- Entre 200 y 2.000 filas por análisis. Con más, se toma una muestra con semilla fija y se anota.
- Opcional: `extra`, columnas que el archivo declara como factor y el modelo no usa. No entran a la red; las revisa el semáforo (sección 6, nube).

| Motor | Columnas que exige | Cómo se muestrea |
|---|---|---|
| `supervivencia` | `tiempo` (años en la empresa), `evento` (renunció o sigue), `grupo`, `efectos`, `suave`, `encuestas` (cuatro ordinales) | Filas al azar |
| `jerarquico` | `objetivo` (sí/no), `paciente`, `grupo`, `suave`, `categoria`, `tratamiento`, `efectos` | **Pacientes completos dentro de barrios elegidos**, nunca filas sueltas |
| `estados` | `objetivo` (sí/no del mes siguiente) y seis meses de `atraso`, `saldo` y `pago`, más `cupo` y `transiciones` | Filas al azar |

**Motor `espacial`.** Columnas `x`, `y`, `valor` y, opcional, `tendencia` (distancia al río en cada punto); en ese caso el caso trae además `grilla`, un CSV con `x`, `y` y esa misma distancia para cada celda del terreno. Entre 30 y 400 filas. El terreno se lleva a una grilla fija de 32×32 celdas (una sola escala para los dos ejes; si dos puntos caen en la misma celda se promedian). Las unidades son las celdas de esa grilla, que en pantalla se llaman bloques.

## 2. Lo que `amortizacion` le entrega a `producto` (`nucleo/api.py`)

Dueño: `amortizacion`. `producto` no toca motores ni redes: llama a estas funciones puras, que devuelven diccionarios listos para convertir a JSON, **con la misma forma que los ejemplos fijos**.

```python
# nucleo/api.py  — solo NumPy, PyYAML y onnxruntime. Nunca importa torch, zuko, jax ni numpyro.
def casos() -> dict: ...
def analizar(caso: str, transformaciones: list[str] = (), costos: dict | None = None,
             mediciones: list[dict] = ()) -> dict: ...
def cartera(caso: str) -> dict: ...
def donde_medir(caso: str, mediciones: list[dict] = ()) -> dict: ...
def nube(caso: str, transformaciones: list[str] = ()) -> dict: ...
def sello(motor_id: str) -> dict: ...
```

- `mediciones` es una lista de `{x, y, valor}` que se agregan a los datos del caso antes de responder. Así se simula «medí aquí y salió esto».
- Todas llevan semilla fija: misma entrada, misma salida.

**Implementaciones de un motor.** Una variable de entorno por motor, sin cambiar código:

| Variable | Valores |
|---|---|
| `KRYLOV_MOTOR_SUPERVIVENCIA` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_JERARQUICO` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_ESTADOS` | `mcmc` (por defecto) o `red` |
| `KRYLOV_MOTOR_ESPACIAL` | `mcmc` (por defecto) o `red` |

- `red`: el codificador (ONNX) resume el dataset, el flujo normalizador condicional entrega 32 muestras del posterior de los parámetros globales (se muestrea en NumPy leyendo `flujo.npz`) y lo local se resuelve exacto en NumPy. En `espacial`, además, la cabeza de mapa entrega media y margen por bloque. Se activa motor por motor cuando pasa `validar-motor`.
- `mcmc`: el posterior del MCMC de referencia (NUTS), **precalculado** en `motor/` y guardado en `motor/artefactos/<motor_id>/mcmc/<clave>.npz`. `nucleo/` solo lee esas muestras y aplica el mismo paso local exacto. Toda respuesta que sale de aquí lleva `implementacion: "mcmc"` y `precalculado: true`, y la pantalla lo rotula. Es el plan B de cada tarjeta, y existe primero.
- Si un motor no tiene ni red validada ni muestras precalculadas para la clave pedida, `analizar` devuelve un error con frase en español y `producto` sigue con el ejemplo fijo.
- Lo que cambia entre `red` y `mcmc` es de dónde salen las 32 muestras. La forma de la respuesta es la misma.

**Un solo preprocesamiento.** `nucleo/preproceso.py` es la única función que transforma datos. La usan el simulador de entrenamiento (`motor/`) y el servicio. Tiene una prueba que pasa el mismo arreglo por los dos caminos y da idéntico.

## 3. Capa de decisión (`nucleo/decision.py` y `web/src/decision.ts`)

Dueño de la definición: `amortizacion`. Hay dos copias de la misma cuenta de diez líneas: Python (la de referencia) y TypeScript (para que los deslizadores de costos respondan sin esperar a la red). Una prueba en cada lado lee `contratos/ejemplos/decision_prueba.json` y exige el mismo resultado. Cada caso de prueba trae `regla`: `tabla` (con `muestras_p`) o `espacial` (con `p`).

Definiciones, que sostienen cada número en pantalla:

- **Costos del caso.** `C_si` = lo que cuesta actuar sobre una unidad que no lo necesitaba (`costos.falso_si`). `C_no` = lo que cuesta no actuar sobre una que sí (`costos.falso_no`).
- **Punto de corte** = `C_si / (C_si + C_no)`. Si la probabilidad de «sí» supera ese valor, conviene actuar.
- **Los tres colores son decisiones, no pronósticos:**
  - `actuar`: conviene actuar, y saber más casi seguro no cambiaría la decisión.
  - `no_actuar`: no conviene actuar, y saber más casi seguro no la cambiaría.
  - `en_duda`: la decisión podría cambiar. **Regla única para todos los motores: hay más de 10% de probabilidad de que la decisión cambie al saber más.**
- **Cómo se calcula «podría cambiar».**
  - Motores de tabla: cada unidad trae `muestras_p`, 32 versiones creíbles de su probabilidad (una por muestra del posterior). `p` es el promedio. La unidad está `en_duda` si más de 10% de las muestras caen al otro lado del punto de corte.
  - `espacial`: cada bloque trae `p`, la probabilidad de superar el umbral del caso. Si se actúa, la probabilidad de equivocarse es `1 − p`; si no se actúa, es `p`. Está `en_duda` si esa probabilidad supera 10%.
- **Lo que cuesta no saber** (en pantalla, el número grande). Es la plata que se ahorraría, en promedio, si la duda se despejara antes de decidir:
  - Motores de tabla: `duda = min(C_si·(1 − p), C_no·p) − promedio sobre muestras de min(C_si·(1 − p_s), C_no·p_s)`. Nunca es negativo y vale casi cero en las unidades que no están en duda.
  - `espacial`: `duda = min(C_si·(1 − p), C_no·p)`. Aquí toda la duda se despeja midiendo el bloque.
  - Total = suma de `duda` sobre las unidades.
- **Qué pesa**: sale del posterior de los parámetros globales, en los cuatro motores. Por factor, la dirección y una etiqueta de `certeza`: `seguro` si al menos 95% de las versiones creíbles coinciden en el signo, `probable` si al menos 80%, `no_se_sabe` en otro caso.
- **Examen con datos reales.** Con las respuestas guardadas en `<caso>_verdad.csv` (motores de tabla) o escondiendo 20% de los puntos medidos (espacial), se compara lo que Krylov dijo con lo que pasó. Sale en el campo `examen`. Es la única exactitud que se dice en voz alta; la medida en simulaciones va en la lámina técnica.

## 4. Caso (`casos/<nombre>.yaml`)

Dueño: `seguimiento`. `casos/INICIO` lista, uno por línea y en orden, los casos que aparecen como tarjetas; el primero abre el demo.

```yaml
nombre: ejemplo_formato
tarjeta:
  titulo: "¿A quién conviene retener?"
  empresa_o_industria: "Caso tipo Buk"
  sponsor: Buk                       # o null. Si no es null, la tarjeta dice «caso tipo Buk · datos públicos de ejemplo»
  oculto: false                      # true: no aparece en el inicio (el archivo malo del demo)
pregunta: "¿A qué personas conviene ofrecerles un plan de retención?"
motor: supervivencia                 # supervivencia | jerarquico | estados | espacial
unidad: { singular: persona, plural: personas }
rotulos:
  actuar: "Conviene retener"
  no_actuar: "No hace falta"
  en_duda: "No sabemos si conviene"
  costo_de_no_saber: "Lo que te cuesta no saber"
columnas:                            # el papel de cada columna en el modelo del motor; ver casos/*.yaml
  id: EmployeeNumber
  evento: Attrition                  # supervivencia. En jerarquico y estados la respuesta se llama `objetivo`
  tiempo: YearsAtCompany
  grupo: JobRole
  efectos: [OverTime, DistanceFromHome, NumCompaniesWorked]
  suave: MonthlyIncome
  encuestas: [EnvironmentSatisfaction, JobSatisfaction, RelationshipSatisfaction, WorkLifeBalance]
  extra: []                          # declaradas como factor y fuera del modelo; las revisa el semáforo
  disponibles: null                  # cuántas columnas traía el archivo original; se llena al bajarlo
  elegidas_por: equipo               # siempre `equipo` (no hay capa de lenguaje, D-26)
# jerarquico: { id, objetivo, paciente, grupo, suave, categoria, tratamiento, efectos, extra }
# estados:    { id, objetivo, atraso: [6 meses], saldo: [6], pago: [6], cupo, transiciones, extra }
# espacial:   { x: x, y: y, valor: zinc, tendencia: dist, umbral: 720, unidad_valor: "mg/kg", transformacion: log }  más `grilla:` en la raíz
costos:
  falso_si: { valor: 1500, min: 200, max: 5000, etiqueta: "Costo de un plan de retención", tipo: hipótesis, cifra: K-01 }
  falso_no: { valor: 6000, min: 1000, max: 20000, etiqueta: "Costo de reemplazar a alguien", tipo: hipótesis, cifra: K-02 }
  medicion: { valor: null, etiqueta: "Costo de una medición", tipo: hipótesis, cifra: X-00 }   # solo espacial
moneda: USD
dataset: datos/demo/ejemplo.csv
verdad: datos/demo/ejemplo_verdad.csv        # opcional: habilita el examen con datos reales
origen_datos: "Datos públicos de ejemplo"    # se ve en pantalla tal cual
sintetico: false                             # si es true, la interfaz muestra «sintético»
cartera: { modo: simulada, n: 1000 }         # opcional. Las empresas salen del simulador del motor
```

Reglas: `cifra` es el id de una fila de `pitch/CIFRAS.md`. `min` y `max` son los extremos del deslizador. El servicio no carga un caso con costos en `null` y lo dice al arrancar; los demás casos siguen funcionando.

## 5. Capa de lenguaje

No hay (decisión D-26): «Sube tus datos» se cortó, porque cada motor responde una familia de archivos y no un CSV cualquiera. `en_palabras` sale de plantillas escritas por `seguimiento`, llenadas con los números del JSON. `columnas.elegidas_por` es siempre `equipo`. En el pitch, Anthropic aparece solo como la herramienta con que se construyó el producto (Claude Code).

## 6. API HTTP y modo estático (backend → frontend)

Base `/api`. Errores: `{"error": "frase en español", "codigo": "..."}` con estado 4xx; nunca una traza.

**Regla del modo estático.** Toda respuesta que el demo necesita existe también como archivo en `web/public/estatico/`, generado por `uv run python -m servicio.exportar_estatico` y subido a git. La web pide primero a la API; si no hay API configurada, no responde en 1,5 segundos o la URL trae `?estatico=1`, lee el archivo. Así la URL pública del QR aguanta a toda la sala sin servidor, y el escenario funciona sin internet.

| Ruta | Para qué | Archivo estático | Ejemplo fijo |
|---|---|---|---|
| `GET /api/casos` | Vista 1 | `casos.json` | `casos.json` |
| `POST /api/analizar` | Vistas 2 y 4 | `analizar/<clave>.json` | `analizar_tabla.json`, `analizar_espacial.json`, `analizar_rojo.json` |
| `POST /api/cartera` | Vista 3 | `cartera/<caso>.json` | `cartera.json` |
| `POST /api/donde-medir` | Vista 2, casos espaciales | `donde-medir/<clave>.json` | `donde_medir.json` |
| `POST /api/nube` | Vista 4 | `nube/<clave>.json` | `nube.json` |
| `GET /api/sello?motor=` | Pie y panel | `sello/<motor>.json` | `sello.json` (espacial), `sello_<motor>.json` (los de tabla, sin medir) |

`<clave>` = nombre del caso, más `__` y cada transformación o medición en orden (`rotacion_malo__quitar_factor-fecha_salida`, `terreno__A-alto`). `exportar_estatico` escribe todas las claves que el recorrido del demo puede pedir: cada caso, el arco rojo → verde, y para el caso espacial las tres mejores candidatas con sus tres resultados posibles.

### `POST /api/analizar`

Petición: `{ "caso": "rotacion", "transformaciones": [], "costos": null, "mediciones": [] }`.

`transformaciones` acepta `"quitar_factor:<nombre>"` (motores de tabla; saca la columna de `extra` o de `efectos`) y `"quitar_tendencia"` (espacial). Así se hace el arco rojo → corrección → verde sin otra ruta.

Respuesta para los motores de tabla (campos; el ejemplo completo está en `ejemplos/analizar_tabla.json`). **Es la misma forma para los tres**: cambia `motor_id` y qué factores aparecen.

```json
{
  "caso": "rotacion", "motor_id": "supervivencia", "implementacion": "red", "precalculado": false,
  "titular": "35 personas están en duda. No saber te cuesta cerca de 18 mil dólares.",
  "costo_de_no_saber": { "valor": 18400, "moneda": "USD" },
  "costos": { "falso_si": { "valor": 1500, "min": 200, "max": 5000, "etiqueta": "Costo de un plan de retención" },
              "falso_no": { "valor": 6000, "min": 1000, "max": 20000, "etiqueta": "Costo de reemplazar a alguien" } },
  "punto_de_corte": 0.2,
  "unidades": [ { "id": "E-014", "etiqueta": "E-014", "p": 0.31, "rango_bajo": 0.18, "rango_alto": 0.47,
                  "muestras_p": [0.22, 0.35, 0.29], "estado": "en_duda", "duda": 212.5 } ],
  "resumen_colores": { "actuar": 18, "no_actuar": 79, "en_duda": 23 },
  "factores": [ { "nombre": "OverTime", "etiqueta": "Horas extra", "direccion": "sube", "efecto": 0.94,
                  "rango_bajo": 0.51, "rango_alto": 1.38, "certeza": "seguro" } ],
  "columnas": { "usadas": ["OverTime"], "disponibles": 35, "elegidas_por": "equipo", "explicacion": "" },
  "semaforo": { "estado": "verde", "motivo": "", "propuesta": null },
  "examen": { "tipo": "datos_reales_reservados", "n": 294, "frase": "", "tramos": [ { "dijimos": 0.1, "paso": 0.09, "n": 120 } ] },
  "sello_resumen": { "frase": "", "medido": false },
  "en_palabras": ["...", "...", "..."],
  "rotulos": { "actuar": "Conviene retener", "no_actuar": "No hace falta", "en_duda": "No sabemos si conviene", "costo_de_no_saber": "Lo que te cuesta no saber" },
  "registro": ["294 personas por decidir", "9 cargos"],
  "tiempo_ms": 310, "sintetico": false, "origen_datos": "Datos públicos de ejemplo"
}
```

- `implementacion` es `red` o `mcmc`. Con `mcmc`, `precalculado` es `true` y la pantalla lo rotula «precalculado».
- `muestras_p` trae 32 valores por unidad, con dos decimales: una por muestra del posterior, pasada por el paso local exacto. Con eso la web recalcula colores, `duda` y el total al mover un deslizador, sin llamar a nadie.
- `examen` va en `null` si el caso no tiene archivo de verdad. `examen.frase` la escribe el servicio con los números de `tramos`, nunca a mano.
- `sello_resumen.medido` es `false` mientras no haya examen ni sello; la interfaz muestra entonces «exactitud en medición» y ningún porcentaje.
- En `factores`, la interfaz muestra la flecha (`direccion`) y la etiqueta de `certeza`, no el número. Pueden aparecer factores que no son columnas (por ejemplo `compromiso`, que el modelo arma con las cuatro encuestas).

En casos `espacial`, `unidades` va en `null`, `factores` trae «qué manda en el terreno» (el río, la continuidad entre vecinos, el error de medición; sale del posterior y ya no es opcional) y la respuesta agrega:

```json
"mapa": { "nx": 32, "ny": 32, "x0": 178605, "y0": 329714, "lado": 121.5,
          "p": [0.02, 0.4, null], "media": [310.0, 690.0, null],
          "puntos": [ { "x": 181072, "y": 333611, "valor": 1022 } ],
          "umbral": 720, "unidad_valor": "mg/kg" }
```

`p` y `media` tienen `nx·ny` valores, fila por fila desde abajo a la izquierda; `null` marca celdas fuera del terreno. La web pinta cada bloque con la misma regla de la sección 3.

Con `semaforo.estado` en `rojo_datos` o `rojo_modelo`: `costo_de_no_saber`, `unidades`, `mapa` y `factores` vienen en `null`. Con `rojo_modelo`, `semaforo.propuesta` trae `{ "transformacion": "quitar_factor:fecha_salida", "texto": "..." }`.

### `POST /api/donde-medir`

Solo casos espaciales. Petición `{ "caso": "terreno", "mediciones": [] }`. Respuesta (`ejemplos/donde_medir.json`):

```json
{
  "caso": "terreno",
  "candidatas": [ { "puesto": 1, "etiqueta": "A", "x": 180100, "y": 331900,
                    "valor_de_medir": 41200, "costo_medicion": 3000, "valor_neto": 38200,
                    "resultados_posibles": { "bajo": 240, "medio": 610, "alto": 1480 } } ],
  "mensaje_parada": null,
  "analisis_rehechos": 480, "tiempo_ms": 900, "implementacion": "red", "precalculado": false
}
```

- `candidatas` trae las tres mejores. `valor_de_medir` es cuánto baja «lo que cuesta no saber», en promedio, si se mide ahí.
- `analisis_rehechos` es el conteo real de análisis completos que hizo falta (lugares candidatos × resultados posibles). Es la cifra que se dice en voz alta.
- Al hacer clic en una candidata, la web ofrece «sale bajo / medio / alto», llama a `analizar` con esa medición y vuelve a llamar a `donde-medir` con la misma lista.
- `mensaje_parada` aparece cuando ninguna medición paga su costo: «Con lo que ya sabes, medir más no se paga».
- Si se sirve precalculado, `precalculado: true` y `tiempo_ms` es el tiempo medido de verdad al generarlo.

### `POST /api/cartera`

Petición `{ "caso": "rotacion" }`. Respuesta (`ejemplos/cartera.json`):

```json
{
  "caso": "rotacion", "n_analisis": 1000, "tiempo_ms": 1840, "precalculado": false,
  "filas": [ { "cliente": "Empresa 017", "n_unidades": 86, "costo_de_no_saber": 4120, "por_unidad": 47.9, "en_duda": 9, "estado": "verde" } ],
  "sintetico": true, "origen_datos": "1.000 empresas simuladas, cada una distinta"
}
```

`filas` viene ordenado por `costo_de_no_saber` descendente. Con `cartera.modo: simulada`, las empresas salen del simulador del motor del caso (el mismo modelo generativo con que se entrenó la red), con parámetros, covariables y tamaños distintos, y la pantalla dice «simuladas». La red las responde en lote. Si el motor está en `mcmc`, la cartera trae solo las empresas que se alcanzaron a precalcular, `n_analisis` dice cuántas y `precalculado` es `true`.

### `POST /api/nube`

Petición `{ "caso": "rotacion_malo", "transformaciones": [] }`. Respuesta (`ejemplos/nube.json`):

```json
{
  "caso": "rotacion_malo", "n_simulaciones": 200000,
  "ejes": { "x": { "nombre": "Qué tan bien adivina la respuesta el mejor factor, solo", "min": 0.5, "max": 1.0 },
            "y": { "nombre": "Proporción de «sí»", "min": 0.0, "max": 1.0 } },
  "puntos": [[0.61, 0.18], [0.72, 0.4]],
  "archivo": { "x": 0.99, "y": 0.16, "dentro": false },
  "detectores": { "ejes_con_nombre": { "dentro": false, "motivo": "La columna «fecha_salida» adivina sola la respuesta." },
                  "resumenes_aprendidos": { "dentro": true, "distancia": 2.1, "limite": 4.6 } }
}
```

**Qué es la nube (D-26).** `puntos` son datasets simulados del **predictivo a priori del modelo generativo del motor**: las mismas simulaciones con que practicó la red. Hay dos detectores, y `rojo_modelo` sale si cualquiera de los dos marca:

1. **Ejes con nombre (lo que se dibuja).** De cada dataset simulado y del archivo se calculan dos resúmenes que se dicen en palabras: qué tan bien adivina la respuesta el mejor factor por sí solo (incluidas las columnas `extra`), y la proporción de «sí». Una columna que delata la respuesta cae afuera por construcción. Es lo único que la web dibuja.
2. **Resúmenes aprendidos (no se dibuja).** La distancia del archivo, en el espacio de resúmenes del codificador, al conjunto de las simulaciones. Atrapa lo que los dos ejes no ven. Va en `detectores.resumenes_aprendidos` y, si marca, el motivo lo dice en una frase.

`archivo.dentro` es `true` solo si los dos detectores dicen dentro. `puntos` es una muestra de hasta 3.000; `n_simulaciones` es el conteo real.

### `GET /api/sello?motor=espacial`

Respuesta (`ejemplos/sello.json`): el contenido de `motor/artefactos/<motor_id>/sello.json` más `frases`, una lista de oraciones sin jerga.

**Un sello por motor.** Campos de `sello.json`: `motor_id`, `implementacion`, `simulaciones_entrenamiento`, `entrenamiento_min`, `casos_validacion` (datasets simulados nuevos del SBC), `cobertura_90`, `cobertura_90_peor_grupo`, `peor_grupo`, `sbc_pasa`, `cobertura_90_metodo_rapido`, `latencia_ms`, `mcmc_datasets_comparados`, `mcmc_s_por_dataset`, `mcmc_diferencia_media` (diferencia de medias entre la red y el MCMC, en desviaciones estándar del posterior), `amortizacion` (`que_se_compara`, `mcmc_s`, `red_s`), `nube_malo_cae_fuera`, `minutos_de_punta_a_punta`, `fecha`, `maquina`, `limitaciones`. Un campo sin medir va en `null` y la interfaz lo omite.

## 7. Artefactos de un motor

`motor/artefactos/<motor_id>/`, uno por motor, versionados en git:

- `codificador.onnx`: lo que usa el servicio. En `espacial` incluye la cabeza de mapa.
- `flujo.npz`: los pesos del flujo normalizador condicional. `nucleo/flujo.py` lo muestrea en NumPy; una prueba exige que, con los mismos pesos y el mismo ruido, dé la misma muestra que `torch` (tolerancia de `float32`).
- `pesos.pt`: lo que usa el entrenamiento.
- `config.json`: el prior, los rangos de n, la arquitectura y la versión de `preproceso`.
- `sello.json`.
- `mcmc/<clave>.npz`: muestras del posterior del MCMC de referencia para cada clave del recorrido. Es el plan B.
- `nube.npz`: los resúmenes (con nombre y aprendidos) de las simulaciones del predictivo a priori.
