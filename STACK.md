# Krylov · Stack: qué instalar en cada computador y por qué

> **Hackathon:** el producto se termina el sábado a las 18:00. Este archivo existe para que nadie pierda una hora eligiendo herramientas ni instale algo que después no sirve en el servidor.

## 0. Cómo se usa este archivo

1. Cada computador instala **lo común** (sección 1) y **lo suyo** (secciones 2, 3 o 4).
2. Cada herramienta trae una tabla de alternativas con pros y contras **para este caso de uso**, una recomendación y una **regla para cambiar**. La recomendación es el punto de partida, no una orden: si el agente o la persona ve que la regla para cambiar se cumple, cambia y lo anota.
3. Lo que se elija se anota en `estado/<rol>.md` con una línea de por qué. Si la elección afecta a otro computador (por ejemplo, el formato en que se exporta la red), además va una entrada en `DECISIONES.md`.
4. Las versiones de la sección 5 se verificaron en las páginas oficiales el 21 de noviembre de 2026. Lo que dice «por medir» o «sin verificar» no se da por cierto: se prueba.

El caso de uso, en una línea, para juzgar cada alternativa: **una app web de tres vistas chicas que se muestra una vez en un escenario, una URL pública que toda la sala abre a la vez desde el teléfono, y cinco redes chicas de inferencia basada en simulación (un codificador del dataset más flujos normalizadores condicionales por motor): una ya entrenada en una noche y cuatro que se entrenan en dos rondas de unos 100 minutos, en dos MacBook Air sin ventilador.** No hay usuarios, ni cuentas, ni datos que guardar.

**Pivote a minería (D-37, sáb 12:10).** Las herramientas no cambiaron: cambiaron los motores. Son cinco: `espacial` (ya entrenado y validado) y cuatro **motores de series** (`deformacion`, `cinetica`, `desgaste`, `sismico`) que comparten un andamio. Los motores de tabla `supervivencia`, `jerarquico` y `estados` se retiran (tarea A-32); donde este archivo los nombra, es para explicar una elección que venía de ellos.

Desde la decisión D-26, en la sección 3 de este archivo, en el código y en el README técnico se usan los nombres técnicos precisos: modelo generativo, prior, posterior, NPE, flujo normalizador, SBC, MCMC, proceso de Hawkes, proceso gamma. La pantalla y el pitch siguen usando `GLOSARIO.md`.

## 1. Común a los tres computadores

### 1.1 Qué instalar

| Herramienta | Para qué | Comando (macOS) | Cómo se verifica |
|---|---|---|---|
| Git | Control de versiones | `xcode-select --install` | `git --version` |
| GitHub CLI | Autenticarse una vez para poder empujar a los dos repositorios | `brew install gh` y luego `gh auth login` | `gh auth status` |
| Claude Code | El agente de cada computador | ya instalado en los tres | `claude --version` |
| uv | Entornos de Python y dependencias | `brew install uv` (o `curl -LsSf https://astral.sh/uv/install.sh \| sh`) | `uv --version` |
| Python 3.12 | El intérprete del proyecto | `uv python install 3.12` | `uv run python --version` dentro del repo |
| Node.js 26 (LTS) | Construir la web. PC 2 no lo necesita | `brew install node` | `node --version` |

**Por qué Python 3.12 y no el del sistema.** El Python del sistema en estos computadores es 3.15, y `onnxruntime` no publica paquetes para 3.15. La versión 3.12 es la única que sirve a la vez para `torch`, `onnxruntime` y `numpy`, y es además la que usa Vercel por defecto. Render usa 3.14 por defecto, así que ahí se fija a mano (sección 2.6).

**Por qué uv y no pip, conda o poetry.**

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **uv** | Instala Python y dependencias en segundos; un archivo de bloqueo que deja los tres computadores idénticos; `uv run` evita activar entornos | Render no lo usa de forma nativa: hay que exportar un `requirements.txt` | **Recomendado** |
| pip + venv | Viene con Python; Render lo usa tal cual | Lento, sin archivo de bloqueo, hay que instalar Python 3.12 aparte | Solo dentro de Render |
| conda / mamba | Trae bibliotecas numéricas compiladas | Pesado, lento de resolver, innecesario aquí | No |
| poetry | Maduro | Más lento y más ceremonia que uv para el mismo resultado | No |

### 1.2 Un solo entorno de Python, con un grupo aparte para entrenar

En la raíz del repositorio hay un `pyproject.toml` con dos conjuntos de dependencias. Lo crea PC 2 en su primera tarea y los otros dos hacen `uv sync`.

| Conjunto | Paquetes | Quién lo instala | Comando |
|---|---|---|---|
| Base | `numpy`, `pyyaml`, `onnxruntime`, `fastapi[standard]`, `pandas`, `pytest` | Los tres, y el servidor | `uv sync` |
| Grupo `entrenar` | `torch`, `zuko`, `onnx`, `onnxscript`, y el MCMC de referencia: `numpyro` con `jax` | PC 2 y PC 3 (que presta su computador para entrenar) | `uv sync --group entrenar` |

**Regla que no se rompe:** `nucleo/` y `servicio/` no importan `torch`, `zuko`, `jax` ni `numpyro`. El servidor gratuito tiene 512 MB de memoria y el paquete de `torch` para Linux pesa más que eso. Cada red se entrena con `torch`; el codificador se sirve con `onnxruntime`, que pesa unos 28 MB, y el flujo se muestrea en NumPy (sección 3.8). PC 1 no instala el grupo `entrenar`: tiene 1,3 GiB libres.

### 1.3 Los dos repositorios espejo

Cada computador clona el repositorio de la organización y le agrega el espejo como segundo destino de push. Los comandos exactos y su verificación están en el archivo `PC*.md` de cada computador, sección «Arranque».

## 2. PC 1 · producto (backend, frontend y despliegue)

### 2.1 Qué instalar

```bash
# desde la raíz del repositorio
uv sync                                   # backend: FastAPI, NumPy, onnxruntime
npm create vite@latest web -- --template react-ts
cd web && npm install
npm install tailwindcss @tailwindcss/vite  # solo si se elige Tailwind (2.3)
npm install -g vercel                      # solo si hace falta desplegar por línea de comandos (2.6)
```

Variables de entorno, en un archivo `.env` que **no** se sube (y en Render, `ANTHROPIC_API_KEY` desde D-34): una `KRYLOV_MOTOR_<ID>` por motor (`KRYLOV_MOTOR_ESPACIAL`, `KRYLOV_MOTOR_DEFORMACION`, `KRYLOV_MOTOR_CINETICA`, `KRYLOV_MOTOR_DESGASTE`, `KRYLOV_MOTOR_SISMICO`), con valor `mcmc` (por defecto) o `red`; las fija PC 2 cuando cada motor pasa `validar-motor`. En la web: `VITE_API_URL`. Desde D-34 y D-35, en Render: `ANTHROPIC_API_KEY`, para proponer el calce de columnas y para interpretar (2.8).

### 2.2 Framework de la web

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Vite + React + TypeScript** | Es una sola página con estado en memoria: no necesita más. Arranca en segundos, sale como archivos estáticos que Vercel sirve sin configuración, y los agentes lo escriben sin tropiezos. Los tipos atrapan los desajustes con el contrato | Sin rutas ni servidor propios (no hacen falta) | **Recomendado** |
| Next.js 16 | Vercel lo trata de primera; trae rutas y funciones de servidor | Trae complejidad que aquí no se usa (componentes de servidor, caché); más formas de romper el modo estático; compila más lento | Solo si el equipo ya lo domina y quiere las rutas de API en el mismo proyecto |
| SvelteKit | Menos código por pantalla, animaciones incluidas | Menos material de entrenamiento para los agentes; nadie del equipo lo usa a diario | No |
| HTML y JavaScript a mano | Cero dependencias | Con tres vistas, deslizadores, un mapa interactivo y curvas se vuelve inmanejable en horas | No |

Regla para cambiar: ninguna. La app ya está en línea con este framework; cambiarlo a esta altura es perder el demo.

### 2.3 Estilos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Tailwind CSS 4** | Los agentes producen pantallas ordenadas rápido; en Vite se instala con un plugin y una línea de CSS, sin archivo de configuración | Clases largas en el código | **Recomendado** |
| CSS a mano con variables | Control total, cero dependencias | Más lento de iterar con un agente; fácil terminar con estilos inconsistentes | Válido para la tipografía grande del proyector, mezclado con Tailwind |
| Biblioteca de componentes (shadcn y similares) | Deslizadores y tablas listos | Instalación y configuración que se comen media hora; apariencia genérica | Solo el deslizador, si el nativo del navegador no se ve bien |

### 2.4 Mapa, nube, barras y curva

Lo que hay que dibujar: una grilla de 32×32 bloques de colores con puntos y pines encima; una nube de unos 3.000 puntos, donde el motor la tenga; barras horizontales con su rango; y, desde D-37, la curva de una unidad (puntos medidos, abanico y línea del límite).

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Canvas 2D a mano** (un componente por dibujo) | 1.024 rectángulos y 3.000 puntos se dibujan en un milisegundo; control total de colores y animación; se ve igual en teléfono y proyector; cero dependencias | Hay que escribir la conversión de coordenadas y el clic sobre un pin | **Recomendado** para mapa y nube |
| SVG con React | Clic y estilos gratis; nítido en cualquier tamaño | 1.024 nodos más 3.000 puntos empiezan a pesar al animar | **Recomendado** para las barras y la lista de unidades. Punto de partida también para la curva (`web/src/Curva.tsx`, P-23), que tiene pocos nodos |
| D3 | Escalas y ejes resueltos | Curva de aprendizaje y choque con React | Solo `d3-scale`, si hace falta |
| Biblioteca de gráficos (Recharts, Plotly) | Un gráfico en diez líneas | No hacen bien una grilla con pines interactivos; Plotly pesa varios megas en un teléfono | No |
| Mapa geográfico (MapLibre, deck.gl, Leaflet) | Fondo de mapa real | El banco son 340 pozos en coordenadas locales: un mapa de calles no aporta y agrega teselas, claves y fallas sin internet | No |

### 2.5 Backend

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **FastAPI + uvicorn** | Envuelve las funciones de `nucleo/api.py` en veinte líneas; valida entradas; recibe archivos; corre igual en el computador del escenario y en el servidor | Un proceso más que mantener despierto | **Recomendado** |
| Flask | Más simple todavía | Sin validación ni tipos; ningún ahorro real | No |
| Sin backend: todo precalculado | La URL pública no se puede caer | El cálculo en vivo del escenario deja de existir | **Es el modo estático**, que se construye igual. No reemplaza al backend en el escenario |
| Funciones de Python en Vercel | Un solo proveedor; más memoria y procesador que el servidor gratuito de Render | Arranque en frío en cada función; otra forma de empaquetar | Plan B del despliegue de la API (2.6) |

### 2.6 Dónde se despliega

Hay tres piezas: la web con las respuestas precalculadas, la API, y el computador del escenario.

**La web y las respuestas precalculadas: Vercel.** Es sponsor, sirve archivos estáticos desde una red de distribución, y no se cae con toda la sala conectada. Se conecta al repositorio espejo con «Root Directory» en `web/`.

**Trampa confirmada en la documentación de Vercel.** En el plan gratuito, Vercel no despliega un repositorio **privado** cuando el autor del commit no es el dueño de la cuenta de Vercel. Con tres personas empujando, dos de cada tres commits quedarían sin desplegar. Tampoco puede conectarse a repositorios de una organización, que es la razón de que exista el espejo. Salidas, en orden:

| Salida | Pros | Contras |
|---|---|---|
| **Hacer público el espejo `Silent-math/krylov`** | Es lo que la documentación dice que funciona. El repositorio oficial ya es público, así que no se expone nada nuevo | Lo decide y lo hace el dueño de la cuenta |
| Que solo el dueño de la cuenta haga los commits que se despliegan | No cambia la visibilidad | Frágil: basta un commit de otro para bloquear el despliegue |
| Desplegar con `vercel deploy --prod` desde PC 1 | No depende de la integración con GitHub | Sin verificar: hay reportes de que el bloqueo también aplica |

**La API: Render o Vercel.**

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Render, plan gratuito** | Es sponsor; corre FastAPI tal cual, como proceso; se conecta al espejo | 0,1 de procesador y 512 MB; se duerme tras 15 minutos sin tráfico y tarda cerca de un minuto en despertar; por defecto usa Python 3.14 | **Recomendado**, porque nada del recorrido que se juzga depende de la API: lo cubre el modo estático |
| Funciones de Python en Vercel | 2 GB y un procesador entero; no se duerme del mismo modo | Otra forma de empaquetar la API; arranque en frío de unos segundos | Plan B si la API tarda más de 10 segundos en Render ya despierto |
| Túnel desde PC 1 (cloudflared, ngrok) | Toda la potencia del computador | Depende del wifi del lugar y de que el computador no se cierre | Solo para mostrarle algo a alguien en la mesa |

Configuración de Render: lenguaje «Python 3»; comando de construcción `pip install -r requirements.txt`; comando de inicio `uvicorn servicio.app:app --host 0.0.0.0 --port $PORT`; variable `PYTHON_VERSION` con una versión 3.12 completa (por ejemplo `3.12.x`, la que muestre `uv python list`); y las variables `KRYLOV_MOTOR_<ID>` de cada motor. El `requirements.txt` sale de `uv export --no-dev --no-hashes -o requirements.txt` y no incluye el grupo `entrenar`.

**Límite diario de despliegues.** El plan gratuito de Vercel llegó a su límite el sábado a las 10:10. Desde entonces solo se despliega cuando cambia `web/`, y los redespliegues se agrupan en los hitos H4, H5 y H6 (`WORKPLAN.md`, 6.8).

**El escenario: el computador que presenta, en local.** API y web corriendo en ese computador, con todo precargado y probado sin wifi. La URL pública es para la entrega y para el QR.

### 2.7 Cómo corren las redes dentro del servicio

De cada motor llegan `codificador.onnx` y `flujo.npz`; de los motores de series, además, `flujo_local.npz` (sección 3.8). El servicio no los toca: llama a `nucleo/api.py`.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **onnxruntime (Python) para el codificador, NumPy para el flujo y para lo local** | 28 MB; arranca en milisegundos; rápido en procesador; los mismos archivos sirven en el escenario y en el servidor | Un paso de exportación en PC 2, que hay que probar temprano, y una prueba de que el flujo en NumPy da lo mismo que en `torch` | **Recomendado** |
| `torch` en el servicio | Sin exportar nada | No cabe en el servidor gratuito; arranque lento | Solo en el computador del escenario, y solo si la exportación falla |
| Todo el codificador escrito en NumPy | Cero dependencias | Reescribir convoluciones y atención a mano es una fuente de errores silenciosos | Último recurso |
| onnxruntime-web, la red corriendo en el navegador | Cualquier teléfono simularía mediciones sin servidor | Con Vite no funciona sin ajustes; una hora de riesgo en la tarde | No. Los opcionales se cortaron (D-26); la versión precalculada se ve igual para quien escanea el QR |

### 2.8 Capa de lenguaje (Claude)

> **Vuelve con las decisiones D-34 y D-35, para dos cosas y nada más.** El modelo de lenguaje **propone el calce**: recibe los papeles del motor y un resumen de cada columna, nunca filas, y el usuario ve la propuesta y la confirma. Y **escribe la interpretación**: recibe el JSON de una respuesta y devuelve un texto corto (`POST /api/interpretar`). No elige el motor ni agrega cifras: el servicio revisa que cada número del texto esté en el JSON y, si no, o sin clave o sin internet, usa la plantilla de `casos/textos.yaml` y el calce por regla. Se instala el SDK `anthropic` **solo en `servicio/`** (nunca en `nucleo/` ni en `web/`); la clave va en `ANTHROPIC_API_KEY`, variable de entorno de Render, y nunca entra al repositorio. Antes (D-26) la capa estaba cortada.

Dos llamadas como máximo por archivo: el calce y la interpretación. Para los archivos del demo las dos se precalculan y se guardan en `web/public/estatico/`. Se usa el SDK oficial `anthropic` de Python con salida estructurada. **Antes de escribir este código, el agente carga la skill `claude-api`**: varios parámetros que eran habituales ya no existen (temperatura, presupuesto de razonamiento, forzar una herramienta), y de memoria se escribe mal.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **`claude-opus-5-5` con esfuerzo `low`** | Es el modelo que Anthropic recomienda por defecto; mejor criterio para decidir qué columnas sirven y cuáles delatan la respuesta | Más lento y más caro por llamada (irrelevante a esta escala); no se le puede apagar el razonamiento | **Punto de partida** |
| `claude-haiku-5-5` | El más rápido y barato | Menos criterio en archivos raros | Se cambia a este si la llamada medida pasa de 3 segundos |
| Sin modelo: reglas fijas | Funciona sin internet | No «entiende» nada | Es el respaldo que se construye igual |

La llamada no está en el camino del escenario: los números salen primero, la interpretación del demo está precalculada y, si la capa no responde, se usa la plantilla.

### 2.9 Lo que no se instala

Base de datos, autenticación, colas, Docker, bibliotecas de estado global, pruebas de extremo a extremo. Nada de eso se ve en el demo.

## 3. PC 2 · amortización de los modelos (MacBook Air M4, 16 GB, sin ventilador)

Reescrita por la decisión D-26 y puesta al día con D-37. Los cinco modelos generativos y el andamio de los motores de series están en `WORKPLAN.md`, sección 11; aquí va con qué herramienta se hace cada pieza y por qué.

### 3.1 Qué instalar

```bash
uv python install 3.12
uv sync --group entrenar        # torch, zuko, onnx, onnxscript, numpyro, jax + la base (numpy, onnxruntime…)
uv run python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"
uv run python -c "import zuko, numpyro, jax; print(zuko.__version__, numpyro.__version__, jax.__version__)"
uv run python -c "import numpy; numpy.show_config()"    # debe decir Accelerate
```

No hace falta Node. Antes de lanzar nada largo: enchufado, **tapa abierta**, brillo al mínimo, sobre una superficie dura, modo de bajo consumo apagado, y el comando dentro de `caffeinate -dims`. Con la tapa cerrada y sin pantalla externa, `caffeinate` no garantiza que el equipo siga despierto: no hay documentación oficial que lo afirme, y las fuentes que existen se contradicen. PC 3 instala lo mismo y toma las mismas precauciones cuando entrena.

### 3.2 Framework de entrenamiento

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **PyTorch 2.15** | Convoluciones y transformada de Fourier corren en la GPU del Mac; exporta a ONNX con una función; `zuko` corre encima; es lo que el equipo y los agentes conocen mejor; el mismo código corre en la nube si hay que salir | La GPU del Mac no admite números de doble precisión: todo en `float32` | **Recomendado** para los simuladores y las redes |
| MLX (Apple) | Hecho para estos chips | No exporta a ONNX de forma oficial, así que el servicio no podría usar el codificador sin reescribirlo; menos ejemplos | No, por la exportación |
| JAX | Rápido en procesador, elegante para simuladores | En Mac es solo procesador en la práctica; exportar a ONNX pasa por paquetes de terceros | No para las redes. Sí por debajo de NumPyro, para el MCMC de referencia (3.7) |

### 3.3 Dónde corre cada entrenamiento, y en qué dispositivo

**Un entrenamiento por computador.** Un portátil sin ventilador no sostiene dos a la vez. El calendario, con sus horas, está en `WORKPLAN.md`, sección 6.3.

| Computador | Qué es | Qué corre |
|---|---|---|
| PC 2 | MacBook Air M4, 16 GB | Entrenó `espacial` (sáb 03:50 a 08:30; no se reentrena). Entrena `cinetica` en la ronda 1 y `desgaste` en la ronda 2. Validaciones y MCMC cuando no hay nada entrenando |
| PC 3 | MacBook Air M3, 16 GB | Entrena `deformacion` en la ronda 1 y `sismico` en la ronda 2. Lo lanza su persona; no edita `motor/` |
| PC 1 | Ryzen 3 5300U, 6,6 GiB de memoria (1,3 GiB libres), sin GPU | **No entrena ni corre MCMC.** No instala el grupo `entrenar` |

Procesador o GPU del Mac no se decide de memoria: se mide con la skill `medir-rendimiento`, **motor por motor**, dos minutos en cada uno y dos minutos sostenidos.

| Alternativa | Cuándo conviene |
|---|---|
| GPU del Mac (`mps`) | Si rinde más de 1,5 veces lo del procesador en la red real y no aparecen avisos de operaciones que caen al procesador. Con la red convolucional de `espacial` ganó (7,6 veces el procesador, medido); con los codificadores de series, que son redes chicas sobre muchas unidades, **por medir** |
| Procesador (`cpu`) | Si la red es muy chica o si `mps` se calienta y cae más de 30% en dos minutos |
| Nube (Kaggle o Colab gratuitos) | Solo si una ronda va atrasada **y una persona abrió la sesión y vio la cuota** (diez minutos). Las cuotas gratuitas no se pudieron confirmar en páginas oficiales: no se cuenta con ella de antemano |

Dos reglas más: las mediciones de tiempo que van al guion se hacen sin ningún entrenamiento corriendo en ese computador, y el MCMC de referencia nunca corre encima de un entrenamiento.

### 3.4 Qué aprende la red, y con qué biblioteca

Cada motor es inferencia basada en simulación amortizada: la red aprende a invertir el modelo generativo. Qué parte del posterior se le pide a la red es la decisión de fondo.

| Alternativa | Qué entrega | Pros | Contras | Veredicto |
|---|---|---|---|---|
| **Amortización factorizada: NPE sobre los parámetros globales η y un flujo local chico por unidad** | q(η \| s(D)) · Π_j q(λ_j \| η, s_j, s(D)): un flujo sobre el resumen del dataset y otro, de 2 dimensiones y compartido entre unidades, sobre el resumen de cada unidad | La dimensión de cada flujo es chica y fija aunque cambie el número de unidades; un flujo cubre posteriores locales alargados o bimodales, que una gaussiana no; `nucleo/` sigue sin `torch` | Dos flujos que exportar y que probar; el SBC se hace global y local | **Elegida** para los cuatro motores de series (D-37) |
| NPE sobre los parámetros globales θ, y lo local exacto en NumPy | q(θ \| D) con un flujo normalizador condicional sobre el resumen s(D). Dado cada θ muestreado, lo local se integra en forma cerrada o con cuadratura | θ tiene tamaño fijo; la red hace solo lo caro; lo local es exacto dado θ | Hay que escribir el paso local de cada motor y medir su presupuesto; exige que lo local tenga forma cerrada o pocas dimensiones | Es lo que hace `espacial` (kriging dado θ). Fue la elegida para los tres motores de tabla que se retiran |
| Una cabeza por unidad (la red entrega directo la probabilidad de cada unidad) | `muestras_p` sin paso local | Una sola pasada | No hay posterior de los parámetros, así que no hay «qué pesa» ni SBC sobre parámetros; se parece a una regresión con un emulador al lado, que es justo lo que D-26 reemplaza | No |
| Un solo flujo sobre los globales y los locales de todas las unidades | Todo el posterior conjunto | Sin factorizar | La dimensión crece con el número de unidades; no entrena en una ronda | No |
| **En `espacial`: cabeza de mapa más cabeza de flujo** | La cabeza de mapa entrega media y margen por bloque (predictivo posterior marginal, amortizado); la de flujo, q(θ \| D) sobre los 7 parámetros del modelo | «¿Dónde perforo?» (`donde_medir`) sigue siendo una pasada en lote de ~480 grillas; «qué pesa» sale del posterior | Dos pérdidas sobre un mismo codificador podrían estorbarse | **Elegida**, con el gradiente cortado: la cabeza de flujo recibe el resumen con `detach`, así la de mapa entrena exactamente igual que si estuviera sola |

Qué flujo:

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Acoplamiento afín** (8 capas, permutación fija entre capas) sobre los parámetros en espacio sin restricciones | Muestrear es una pasada hacia adelante de productos de matrices: se reescribe en NumPy en pocas líneas y no depende de la exportación. El mismo `FlujoCondicional` de `motor/comun/flujo.py` sirve de flujo global y de flujo local | Menos expresivo por capa que un spline | **Elegido**, para el flujo de `espacial` y para los dos flujos de cada motor de series |
| Flujo de splines (NSF) | Más expresivo | Los splines usan `searchsorted`, que complica la exportación a ONNX y la copia en NumPy | No |
| Flujo autorregresivo (MAF) | Buena densidad con pocas capas | Muestrea en un bucle sobre las dimensiones de los parámetros: más lento y mal exportable | No |

Con qué biblioteca:

| Biblioteca | Pros | Contras | Veredicto |
|---|---|---|---|
| **`zuko`** | Flujos normalizadores en PyTorch, liviana, se enchufa a cualquier red propia. `zuko.flows.NICE(features, context, transforms)` es el flujo de acoplamiento y usa transformaciones afines por defecto (es el que usa `motor/comun/flujo.py`) | Hay que escribir el bucle de entrenamiento, y comprobar que sus pesos se pueden leer capa por capa para la copia en NumPy | **Recomendada** para entrenar |
| Acoplamiento afín propio (unas 60 líneas) | Los pesos quedan con nombres propios y la copia en NumPy es directa | Código propio que probar | **Plan B inmediato** si leer los pesos de `zuko` cuesta más de 20 minutos |
| `sbi` | Bucle de entrenamiento y diagnósticos incluidos | Pensada para simuladores lentos y bancos fijos; aquí el simulador es rápido y se entrena al vuelo, y su estructura estorba | No |
| BayesFlow | Flujo de trabajo completo y diagnósticos de calibración | Corre sobre Keras con otro motor por debajo: un entorno más que cuidar la noche de la hackathon | No |

Pérdida, en todos: NPE, −log q(θ | s(D)), promediada sobre datasets simulados al vuelo. En los motores de series se suma el término local: −log q(η | s(D)) − promedio_j log q(λ_j | η, s_j, s(D)). Al entrenar, el flujo local se condiciona en el η verdadero; al responder, en cada muestra de η.

### 3.5 Cómo se le pasa un dataset a la red (el codificador)

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Codificador por unidad: convoluciones 1D con máscara y pooling (promedio y máximo)** sobre la serie de cada unidad | Lee tensores con relleno y máscara (unidades, lecturas, canales: tiempo normalizado, valor estandarizado, diferencia con la lectura anterior y covariables de la unidad) y entrega un resumen s_j por unidad. Con tamaños máximos fijos por motor, ONNX no necesita ejes dinámicos | Hay que probar, sin entrenar, que exporta y que la pérdida baja | **Elegido** para los cuatro motores de series (`motor/comun/series.py`). Si no exporta o no aprende, una GRU chica |
| **Codificador de conjuntos: DeepSets con pooling de atención y máscara de relleno** (`motor/comun/codificador.py`, ya existe) | Invariante al orden; admite un número variable de elementos; es la arquitectura estándar para amortizar sobre datasets enteros. En los motores de series agrega los s_j de las unidades en el resumen del dataset, s(D) | El pooling de atención puede complicar la exportación a ONNX: se prueba sin entrenar | **Elegido** para agregar las unidades en los motores de series. Si no exporta, promedio con máscara en vez de atención |
| Set Transformer con puntos inductores | Más expresivo: las unidades se miran entre sí | Más lento por paso y más frágil de exportar; no hace falta con unidades condicionalmente independientes dados los parámetros globales | Solo si la calibración por grupos no pasa |
| Estadísticos resumen escritos a mano | Simple y rápido | Hay que adivinar qué es suficiente para cada modelo; es lo que la red aprende sola | No |
| **Grilla fija de 32×32 con canales** (valor, marca de medición, √dist) y red convolucional | Agregar una medición hipotética es marcar una celda; cualquier terreno o banco entra igual; entrenó en una noche | Dos puntos en la misma celda se promedian; la resolución es fija | **Elegido** para `espacial`, que ya está entrenado con los tres canales |

### 3.6 Simuladores

Un simulador vectorizado por motor, en `torch`, que genera datasets completos al vuelo durante el entrenamiento, sin guardar nada en disco. La cifra «practicó con N millones» la cuenta el bucle de entrenamiento.

| Pieza | Alternativa elegida | Por qué, y qué se descartó |
|---|---|---|
| Campo del terreno | **Transformada de Fourier sobre una grilla del doble de tamaño, recortada** | Miles de terrenos por segundo. Es aproximado en los bordes: una prueba lo compara con el método directo (descomposición de la covarianza en NumPy), que es exacto pero toma decenas de milisegundos por terreno. `gstools` simula un terreno a la vez: no |
| Río del terreno | **Una curva suave al azar y su campo de distancia** | Lo más simple que da una tendencia creíble. Nada de redes fluviales. El caso `leyes` no usa la tendencia: 20% de las simulaciones de entrenamiento no la tenían |
| Series de `deformacion`, `cinetica` y `desgaste` | **Muestreo directo de los modelos de 11.2 a 11.4, con número de unidades y de lecturas variables, lecturas faltantes y relleno con máscara** | Los tres se muestrean hacia adelante sin iterar: trayectorias en forma cerrada e incrementos gamma independientes |
| Sismos de `sismico` | **Simulación por ramificación, vectorizada por generaciones** (inmigrantes de fondo, hijos de la tronadura, hijos de cada sismo), truncada en 300 sismos por sector | Evita simular evento por evento en un bucle. La tarea A-28 pide una prueba que compare la forma cerrada de «lo que se decide» con simular hacia adelante |

El generador de covariables de los motores de tabla se retira con ellos (A-32). Los simuladores no se exportan: se usan solo al entrenar, al validar y, donde exista, para la nube. Los archivos del demo se generan aparte, con las mismas ecuaciones y semilla fija, en `datos/preparar/` (sección 4.2).

### 3.7 MCMC de referencia (validación y plan B)

Cada motor tiene su modelo escrito una segunda vez, para NUTS. **NumPyro con NUTS sigue siendo el método de referencia de los cinco motores después del pivote.** Sirve para dos cosas: es la vara contra la que se valida la red (mismas medias y rangos, y el tiempo de cada uno es la cifra de amortización), y sus muestras precalculadas son la implementación `mcmc`, el plan B de cada tarjeta.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **NumPyro (NUTS) sobre JAX**, solo dentro de `motor/` | Rápido en procesador; los latentes discretos se marginalizan a mano en JAX (en `deformacion`, la mezcla de las dos trayectorias por sector); cadenas vectorizadas | Dos dependencias más en el grupo `entrenar` (ya instaladas: el MCMC de `espacial` corrió con ellas) | **Recomendado** |
| PyMC | Sintaxis más conocida | Compilación más lenta al primer uso; más pesado de instalar | Solo si NumPyro deja de servir |
| Stan | El de referencia de los libros | Compilar cada modelo en C++ en plena hackathon | No |
| Muestreo por importancia en NumPy | Sin dependencias | No escala con parámetros locales por unidad | No |

Es acotado: de 3 a 5 datasets simulados por motor, más el del demo. Corre en un computador que no esté entrenando. Si NUTS no converge (r̂ sobre 1,05) en 10 minutos por dataset, se anota, el sello se apoya en el SBC y esa tarjeta no tiene plan B (`WORKPLAN.md`, 11.8). Qué muestrea NUTS en cada motor nuevo está en 11.2 a 11.5. En `espacial` un análisis con el MCMC tardó 117 s en promedio (sello): la cifra de amortización ahí es rehacer todos los análisis de «¿Dónde perforo?».

**El método rápido de siempre** es otra cosa: la regla simple que se usa cuando no hay tiempo (kriging con parámetros fijos en `espacial`; en los motores de series, una recta, una sola exponencial o un conteo por hora, según 11.2 a 11.5). No es un motor ni un plan B. Se mide solo para la comparación que muestra qué se pierde sin el modelo completo.

### 3.8 Formato de entrega de cada red

| Pieza | Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|---|
| Codificador | **ONNX** (`torch.onnx.export`, que hoy usa el exportador nuevo por defecto) | Lo lee `onnxruntime` en el servicio sin `torch` | Necesita `onnx` y `onnxscript`; un eje variable se declara con `dynamic_shapes`. **Probar la exportación con la red sin entrenar, motor por motor, antes de lanzar su ronda** | **Recomendado**. En `espacial` incluye la cabeza de mapa y el lote es variable. En los motores de series se exporta con formas fijas con relleno y máscara (tamaños máximos por motor) y **dos salidas**: s(D) y los s_j |
| Flujo | **`flujo.npz` con los pesos, muestreado en NumPy por `nucleo/flujo.py`**; en los motores de series, dos archivos: `flujo.npz` (global) y `flujo_local.npz` | Sin riesgo de exportación; el acoplamiento afín son productos de matrices | Dos implementaciones del mismo flujo. Prueba obligatoria: con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra, con tolerancia de `float32` | **Recomendado** |
| Flujo | Exportar el flujo entero a ONNX | Un solo archivo | Muestrear dentro del grafo es justo lo que puede no exportar | No |
| Todo | Archivo de pesos de `torch` | Sin exportar | Obliga a tener `torch` en el servicio | Se guarda igual (`pesos.pt`), para seguir entrenando |

Artefactos por motor, en `motor/artefactos/<motor_id>/`: `codificador.onnx`, `flujo.npz` (y `flujo_local.npz` en los motores de series), `pesos.pt`, `config.json`, `sello.json`, `mcmc/<clave>.npz` y, donde exista, `nube.npz` (`contratos/CONTRATO.md`, sección 7).

## 4. PC 3 · seguimiento (monitoreo, casos, datos y pitch)

### 4.1 Qué instalar

```bash
uv sync                 # pandas para preparar los CSV, pytest, pyyaml
uv sync --group entrenar   # D-37: este computador entrena `deformacion` en la ronda 1 y `sismico` en la ronda 2
brew install node       # solo para poder levantar la web en local y verificar corriendo
```

PC 3 (MacBook Air M3, 16 GB) instala el grupo `entrenar` solo para **lanzar** entrenamientos y validaciones que escribió PC 2: no edita `motor/`. Mismas precauciones que PC 2 (3.1): enchufado, tapa abierta, `caffeinate -dims`. Además necesita poder correr la app en local (`uv run` y `npm run dev`) porque su trabajo es **verificar corriendo, no leyendo**.

### 4.2 Preparación de datos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Un script de Python por caso, con NumPy o pandas, en `datos/preparar/`** | Reproducible; deja escrito de dónde salió cada archivo y con qué semilla se generó, y guarda aparte la verdad escondida | Diez minutos más que hacerlo a mano | **Recomendado** |
| A mano en una planilla | Rápido para mirar | No queda registro; imposible repetir si hay que cambiar algo a las 16:00 | Solo para mirar |

Desde D-37 los archivos del demo son **simulados con las mismas ecuaciones del motor** (`WORKPLAN.md`, sección 11), con semilla fija, una verdad escondida que el motor no ve y el rótulo «simulado»; el modelo a seguir es `datos/preparar/leyes.py`. Donde exista un archivo real con licencia abierta que calce con su motor, se usa y se dice. El suelo real con que se examinó `espacial` (155 puntos y su grilla, ya en `datos/demo/`) queda fuera del inicio: es el examen con datos reales de ese motor.

### 4.3 Láminas

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Láminas dentro de la misma app** (una vista más, tecla `L`) | No se cambia de ventana en el escenario; el QR y la frase salen con la misma tipografía; no depende de internet | Las escribe PC 1 con el texto de PC 3 | **Recomendado** para portada y cierre |
| Google Slides o Keynote | Rápido de editar por cualquiera | Cambiar de ventana en vivo es donde más demos se traban | Para las láminas de respaldo, que solo se abren si preguntan |

Además existe el deck de `pitch/deck/`: una página HTML que abre con doble clic y corre sin internet. El pitch parte ahí y entra a la app para las decisiones (`WORKPLAN.md`, 4.5); la tecla `L` de la app sigue siendo el cierre con el QR.

### 4.4 Video de respaldo y otros

| Qué | Con qué | Por qué |
|---|---|---|
| Grabar la pantalla | QuickTime, que ya viene instalado | No hay nada que configurar. `ffmpeg` sirve para recortar y bajar de peso |
| Código QR | Un generador que entregue un archivo de imagen, guardado dentro de `web/public/` | Tiene que funcionar sin internet en el escenario |
| Cronómetro | El del teléfono | Los ensayos se cronometran por momento |
| Seguimiento continuo | El comando `/loop 30m /ronda` de Claude Code | Corre la skill `ronda` cada media hora sin que nadie se acuerde |

## 5. Versiones verificadas el 21 de noviembre de 2026

| Herramienta | Versión | Dato que importa | Fuente |
|---|---|---|---|
| uv | 0.13.x | `uv python install 3.12` está documentado | docs.astral.sh/uv |
| Python | 3.12 | Único que sirve para todo el stack a la vez | PyPI de cada paquete |
| NumPy | 2.5.x | Requiere Python 3.12 o superior | PyPI |
| PyTorch | 2.15.0 | Paquetes para Mac con chip Apple; la GPU del Mac no admite doble precisión; convoluciones y Fourier tienen implementación propia en la GPU del Mac (leído en el código fuente, no ejecutado) | PyPI, docs.pytorch.org |
| onnxruntime | 1.32.0 | Python 3.11 a 3.14; unos 28 MB en Linux | PyPI |
| onnx / onnxscript | 1.23.x / 0.7.x | Los usa el exportador | PyPI |
| zuko | 1.6.0 | `zuko.flows.NICE` es el flujo de acoplamiento; usa transformaciones afines por defecto (leído en la documentación el 21-nov, no ejecutado) | PyPI, zuko.readthedocs.io |
| numpyro / jax | 0.22.0 / 0.12.1 (las de `uv.lock`) | MCMC de referencia (NUTS) de los cinco motores, solo en `motor/`. Instalan y corren en Python 3.12 en Mac con chip Apple: el MCMC de `espacial` se corrió con ellas | `uv.lock`; `motor/artefactos/espacial/sello.json` |
| FastAPI / uvicorn | 0.165 / 0.54 | `fastapi[standard]` ya trae uvicorn | fastapi.tiangolo.com |
| Node.js | 26 (LTS) | Vite 8 pide Node 20.19 o superior | nodejs.org |
| Vite / React | 8 / 19 | `npm create vite@latest web -- --template react-ts` | vite.dev |
| Tailwind CSS | 4 | Plugin `@tailwindcss/vite` y una línea `@import "tailwindcss";` | tailwindcss.com |
| Render, plan gratuito | | 0,1 de procesador, 512 MB, se duerme a los 15 minutos, despierta en cerca de un minuto, Python 3.14 por defecto | render.com/docs/free, /docs/python-version |
| Vercel, plan gratuito | | No conecta repositorios de organizaciones; bloquea commits de otros autores en repositorios privados; funciones de Python con 2 GB | vercel.com/docs/limits, /docs/git |

**Sin verificar, hay que probarlo:** que `caffeinate` mantenga despierto el Mac con la tapa cerrada (por eso la tapa queda abierta); las cuotas gratuitas de Kaggle y Colab; que `vercel deploy --prod` evite el bloqueo por autor; que el codificador por unidad de los motores de series exporte a ONNX con formas fijas y dos salidas (se prueba sin entrenar: en el andamio, A-23, y motor por motor, A-24, A-25, A-27 y A-28); que NUTS converja en 10 minutos por dataset en cada motor nuevo; cuántos datasets por segundo simula y entrena cada motor (`medir-rendimiento`).
