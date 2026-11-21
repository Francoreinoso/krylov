# Krylov · Stack: qué instalar en cada computador y por qué

> **Hackathon:** el producto se termina el sábado a las 18:00. Este archivo existe para que nadie pierda una hora eligiendo herramientas ni instale algo que después no sirve en el servidor.

## 0. Cómo se usa este archivo

1. Cada computador instala **lo común** (sección 1) y **lo suyo** (secciones 2, 3 o 4).
2. Cada herramienta trae una tabla de alternativas con pros y contras **para este caso de uso**, una recomendación y una **regla para cambiar**. La recomendación es el punto de partida, no una orden: si el agente o la persona ve que la regla para cambiar se cumple, cambia y lo anota.
3. Lo que se elija se anota en `estado/<rol>.md` con una línea de por qué. Si la elección afecta a otro computador (por ejemplo, el formato en que se exporta la red), además va una entrada en `DECISIONES.md`.
4. Las versiones de la sección 5 se verificaron en las páginas oficiales el 21 de noviembre de 2026. Lo que dice «por medir» o «sin verificar» no se da por cierto: se prueba.

El caso de uso, en una línea, para juzgar cada alternativa: **una app web de cuatro vistas que se muestra una vez en un escenario, una URL pública que toda la sala abre a la vez desde el teléfono, y cuatro redes chicas de inferencia basada en simulación (un codificador del dataset más un flujo normalizador condicional por motor) que se entrenan entre una noche y una mañana en dos MacBook Air sin ventilador.** No hay usuarios, ni cuentas, ni datos que guardar.

Desde la decisión D-26, en la sección 3 de este archivo, en el código y en el README técnico se usan los nombres técnicos precisos: modelo generativo, prior, posterior, NPE, flujo normalizador, SBC, MCMC. La pantalla y el pitch siguen usando `GLOSARIO.md`.

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

Variables de entorno, en un archivo `.env` que **no** se sube (y en Render, `ANTHROPIC_API_KEY` desde D-34): una `KRYLOV_MOTOR_<ID>` por motor (`KRYLOV_MOTOR_SUPERVIVENCIA`, `KRYLOV_MOTOR_JERARQUICO`, `KRYLOV_MOTOR_ESTADOS`, `KRYLOV_MOTOR_ESPACIAL`), con valor `mcmc` (por defecto) o `red`; las fija PC 2 cuando cada motor pasa `validar-motor`. En la web: `VITE_API_URL`. Desde D-34, en Render: `ANTHROPIC_API_KEY`, solo para interpretar (2.8).

### 2.2 Framework de la web

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Vite + React + TypeScript** | Es una sola página con estado en memoria: no necesita más. Arranca en segundos, sale como archivos estáticos que Vercel sirve sin configuración, y los agentes lo escriben sin tropiezos. Los tipos atrapan los desajustes con el contrato | Sin rutas ni servidor propios (no hacen falta) | **Recomendado** |
| Next.js 16 | Vercel lo trata de primera; trae rutas y funciones de servidor | Trae complejidad que aquí no se usa (componentes de servidor, caché); más formas de romper el modo estático; compila más lento | Solo si el equipo ya lo domina y quiere las rutas de API en el mismo proyecto |
| SvelteKit | Menos código por pantalla, animaciones incluidas | Menos material de entrenamiento para los agentes; nadie del equipo lo usa a diario | No |
| HTML y JavaScript a mano | Cero dependencias | Con cuatro vistas, deslizadores y un mapa interactivo se vuelve inmanejable en horas | No |

Regla para cambiar: ninguna. Con el tiempo que hay, cambiar de framework después de P-01 es perder la noche.

### 2.3 Estilos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Tailwind CSS 4** | Los agentes producen pantallas ordenadas rápido; en Vite se instala con un plugin y una línea de CSS, sin archivo de configuración | Clases largas en el código | **Recomendado** |
| CSS a mano con variables | Control total, cero dependencias | Más lento de iterar con un agente; fácil terminar con estilos inconsistentes | Válido para la tipografía grande del proyector, mezclado con Tailwind |
| Biblioteca de componentes (shadcn y similares) | Deslizadores y tablas listos | Instalación y configuración que se comen media hora; apariencia genérica | Solo el deslizador, si el nativo del navegador no se ve bien |

### 2.4 Mapa, nube y barras

Lo que hay que dibujar: una grilla de 32×32 bloques de colores con puntos y pines encima; una nube de unos 3.000 puntos; barras horizontales con su rango.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Canvas 2D a mano** (un componente por dibujo) | 1.024 rectángulos y 3.000 puntos se dibujan en un milisegundo; control total de colores y animación; se ve igual en teléfono y proyector; cero dependencias | Hay que escribir la conversión de coordenadas y el clic sobre un pin | **Recomendado** para mapa y nube |
| SVG con React | Clic y estilos gratis; nítido en cualquier tamaño | 1.024 nodos más 3.000 puntos empiezan a pesar al animar | **Recomendado** para las barras y la lista de unidades |
| D3 | Escalas y ejes resueltos | Curva de aprendizaje y choque con React | Solo `d3-scale`, si hace falta |
| Biblioteca de gráficos (Recharts, Plotly) | Un gráfico en diez líneas | No hacen bien una grilla con pines interactivos; Plotly pesa varios megas en un teléfono | No |
| Mapa geográfico (MapLibre, deck.gl, Leaflet) | Fondo de mapa real | El terreno son 155 puntos en coordenadas locales: un mapa de calles no aporta y agrega teselas, claves y fallas sin internet | No |

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

**El escenario: el computador que presenta, en local.** API y web corriendo en ese computador, con todo precargado y probado sin wifi. La URL pública es para la entrega y para el QR.

### 2.7 Cómo corren las redes dentro del servicio

De cada motor llegan dos archivos: `codificador.onnx` y `flujo.npz` (sección 3.8). El servicio no los toca: llama a `nucleo/api.py`.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **onnxruntime (Python) para el codificador, NumPy para el flujo y para lo local** | 28 MB; arranca en milisegundos; rápido en procesador; los mismos archivos sirven en el escenario y en el servidor | Un paso de exportación en PC 2, que hay que probar temprano, y una prueba de que el flujo en NumPy da lo mismo que en `torch` | **Recomendado** |
| `torch` en el servicio | Sin exportar nada | No cabe en el servidor gratuito; arranque lento | Solo en el computador del escenario, y solo si la exportación falla |
| Todo el codificador escrito en NumPy | Cero dependencias | Reescribir convoluciones y atención a mano es una fuente de errores silenciosos | Último recurso |
| onnxruntime-web, la red corriendo en el navegador | Cualquier teléfono simularía mediciones sin servidor | Con Vite no funciona sin ajustes; una hora de riesgo en la tarde | No. Los opcionales se cortaron (D-26); la versión precalculada se ve igual para quien escanea el QR |

### 2.8 Capa de lenguaje (Claude)

> **Vuelve con la decisión D-34 (sáb 07:12), solo para interpretar.** El modelo de lenguaje recibe el JSON de una respuesta y escribe un texto corto (`POST /api/interpretar`). **No propone columnas** (el usuario las asigna con el selector) ni elige el motor, y no agrega cifras: el servicio revisa que cada número del texto esté en el JSON y, si no, o sin clave o sin internet, usa la plantilla de `casos/textos.yaml`. Se instala el SDK `anthropic` **solo en `servicio/`** (nunca en `nucleo/` ni en `web/`); la clave va en `ANTHROPIC_API_KEY`, variable de entorno de Render, y nunca entra al repositorio. Antes (D-26) la capa estaba cortada.

Una sola llamada por respuesta (la interpretación). Para los archivos del demo se precalcula y se guarda en `web/public/estatico/interpretar/`. Se usa el SDK oficial `anthropic` de Python con salida estructurada. **Antes de escribir este código, el agente carga la skill `claude-api`**: varios parámetros que eran habituales ya no existen (temperatura, presupuesto de razonamiento, forzar una herramienta), y de memoria se escribe mal.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **`claude-opus-5-5` con esfuerzo `low`** | Es el modelo que Anthropic recomienda por defecto; mejor criterio para decidir qué columnas sirven y cuáles delatan la respuesta | Más lento y más caro por llamada (irrelevante a esta escala); no se le puede apagar el razonamiento | **Punto de partida** |
| `claude-haiku-5-5` | El más rápido y barato | Menos criterio en archivos raros | Se cambia a este si la llamada medida pasa de 3 segundos |
| Sin modelo: reglas fijas | Funciona sin internet | No «entiende» nada | Es el respaldo que se construye igual |

La llamada no está en el camino del escenario: los números salen primero, la interpretación del demo está precalculada y, si la capa no responde, se usa la plantilla.

### 2.9 Lo que no se instala

Base de datos, autenticación, colas, Docker, bibliotecas de estado global, pruebas de extremo a extremo. Nada de eso se ve en el demo.

## 3. PC 2 · amortización de los modelos (MacBook Air M4, 16 GB, sin ventilador)

Reescrita por la decisión D-26. Los cuatro modelos generativos y la arquitectura están en `WORKPLAN.md`, sección 11; aquí va con qué herramienta se hace cada pieza y por qué.

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
| PC 2 | MacBook Air M4, 16 GB | Entrena `espacial` de noche y `estados` de día. Validaciones y MCMC cuando no hay nada entrenando |
| PC 3 | MacBook Air M3, 16 GB | Entrena `supervivencia` de noche y `jerarquico` de día. Lo lanza su persona; no edita `motor/` |
| PC 1 | Ryzen 3 5300U, 6,6 GiB de memoria (1,3 GiB libres), sin GPU | **No entrena ni corre MCMC.** No instala el grupo `entrenar` |

Procesador o GPU del Mac no se decide de memoria: se mide con la skill `medir-rendimiento`, **motor por motor**, dos minutos en cada uno y dos minutos sostenidos.

| Alternativa | Cuándo conviene |
|---|---|
| GPU del Mac (`mps`) | Si rinde más de 1,5 veces lo del procesador en la red real y no aparecen avisos de operaciones que caen al procesador. Con la red convolucional de `espacial` suele ganar; con los codificadores de conjuntos, que son capas densas chicas sobre muchas filas, **por medir** |
| Procesador (`cpu`) | Si la red es muy chica o si `mps` se calienta y cae más de 30% en dos minutos |
| Nube (Kaggle o Colab gratuitos) | Solo si a las 09:00 algo va atrasado **y una persona abrió la sesión y vio la cuota** (diez minutos). Las cuotas gratuitas no se pudieron confirmar en páginas oficiales: no se cuenta con ella de antemano |

Dos reglas más: las mediciones de tiempo que van al guion se hacen sin ningún entrenamiento corriendo en ese computador, y el MCMC de referencia nunca corre encima de un entrenamiento.

### 3.4 Qué aprende la red, y con qué biblioteca

Cada motor es inferencia basada en simulación amortizada: la red aprende a invertir el modelo generativo. Qué parte del posterior se le pide a la red es la decisión de fondo.

| Alternativa | Qué entrega | Pros | Contras | Veredicto |
|---|---|---|---|---|
| **NPE sobre los parámetros globales θ, y lo local exacto en NumPy** | q(θ \| D) con un flujo normalizador condicional sobre el resumen s(D) del codificador. Dado cada θ muestreado, el efecto de grupo y el latente de cada unidad se integran con cuadratura de Gauss-Hermite anidada (filtro forward en `estados`) | θ tiene tamaño fijo aunque cambie el número de cargos o de barrios; la red hace solo lo caro; el predictivo por unidad es exacto dado θ; `nucleo/` sigue sin `torch` | Hay que escribir el paso local de cada motor y medir su presupuesto (32 muestras × unidades × nodos²) | **Elegida** para `supervivencia`, `jerarquico` y `estados` |
| Una cabeza por unidad (la red entrega directo la probabilidad de cada fila) | `muestras_p` sin paso local | Una sola pasada | No hay posterior de θ, así que no hay «qué pesa» ni SBC sobre parámetros; se parece a una regresión con un emulador al lado, que es justo lo que D-26 reemplaza | No |
| NPE también sobre los efectos de grupo y los latentes | Todo el posterior conjunto | Sin cuadratura | La dimensión crece con n y con el número de grupos; no entrena en horas | No |
| **En `espacial`: cabeza de mapa más cabeza de flujo** | La cabeza de mapa entrega media y margen por bloque (predictivo posterior marginal, amortizado); la de flujo, q(θ \| D) sobre los 7 parámetros del terreno | «¿Dónde mido?» sigue siendo una pasada en lote de ~480 grillas; «qué manda en el terreno» sale del posterior | Dos pérdidas sobre un mismo codificador podrían estorbarse | **Elegida**, con el gradiente cortado: la cabeza de flujo recibe el resumen con `detach`, así la de mapa entrena exactamente igual que si estuviera sola |

Qué flujo:

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Acoplamiento afín** (8 capas, permutación fija entre capas) sobre θ en espacio sin restricciones | Muestrear es una pasada hacia adelante de productos de matrices: se reescribe en NumPy en pocas líneas y no depende de la exportación. Con n de cientos a miles de filas el posterior en ese espacio es casi gaussiano, y alcanza | Menos expresivo por capa que un spline | **Elegido** |
| Flujo de splines (NSF) | Más expresivo | Los splines usan `searchsorted`, que complica la exportación a ONNX y la copia en NumPy | No |
| Flujo autorregresivo (MAF) | Buena densidad con pocas capas | Muestrea en un bucle sobre las dimensiones de θ (32 a 35): lento y mal exportable | No |

Con qué biblioteca:

| Biblioteca | Pros | Contras | Veredicto |
|---|---|---|---|
| **`zuko`** | Flujos normalizadores en PyTorch, liviana, se enchufa a cualquier red propia. `zuko.flows.NICE(features, context, transforms)` es el flujo de acoplamiento y usa transformaciones afines por defecto (leído en su documentación; se confirma corriéndolo en A-01) | Hay que escribir el bucle de entrenamiento, y comprobar que sus pesos se pueden leer capa por capa para la copia en NumPy | **Recomendada** para entrenar |
| Acoplamiento afín propio (unas 60 líneas) | Los pesos quedan con nombres propios y la copia en NumPy es directa | Código propio que probar | **Plan B inmediato** si leer los pesos de `zuko` cuesta más de 20 minutos |
| `sbi` | Bucle de entrenamiento y diagnósticos incluidos | Pensada para simuladores lentos y bancos fijos; aquí el simulador es rápido y se entrena al vuelo, y su estructura estorba | No |
| BayesFlow | Flujo de trabajo completo y diagnósticos de calibración | Corre sobre Keras con otro motor por debajo: un entorno más que cuidar la noche de la hackathon | No |

Pérdida, en todos: NPE, −log q(θ | s(D)), promediada sobre datasets simulados al vuelo.

### 3.5 Cómo se le pasa un dataset a la red (el codificador)

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Codificador de conjuntos: DeepSets con pooling de atención y máscara de relleno**, jerárquico cuando el modelo lo es (filas → grupo → dataset) | Invariante al orden de las filas; admite n variable; es la arquitectura estándar para amortizar sobre datasets enteros. **Ya no es «investigación»: es la arquitectura de los tres motores de tabla** | El pooling de atención puede complicar la exportación a ONNX con n variable: se prueba sin entrenar | **Elegido** para `supervivencia`, `jerarquico` y `estados`. Si no exporta, promedio con máscara en vez de atención |
| Set Transformer con puntos inductores | Más expresivo: las filas se miran entre sí | Más lento por paso y más frágil de exportar; no hace falta con filas condicionalmente independientes dado el grupo | Solo si la calibración por grupos no pasa |
| Estadísticos resumen escritos a mano | Simple y rápido | Hay que adivinar qué es suficiente para 30 parámetros; es lo que la red aprende sola | No (los dos resúmenes con nombre de la nube son otra cosa: `WORKPLAN.md`, 11.9) |
| **Grilla fija de 32×32 con canales** (valor, marca de medición, √dist) y red convolucional | Agregar una medición hipotética es marcar una celda; cualquier terreno entra igual; entrena en una noche | Dos puntos en la misma celda se promedian; la resolución es fija | **Elegido** para `espacial`. Salvavidas: dos canales, sin tendencia, si los tres no pasan la prueba de humo a las 04:45 |

### 3.6 Simuladores

Un simulador vectorizado por motor, en `torch`, que genera datasets completos al vuelo durante el entrenamiento, sin guardar nada en disco. La cifra «practicó con N millones» la cuenta el bucle de entrenamiento.

| Pieza | Alternativa elegida | Por qué, y qué se descartó |
|---|---|---|
| Campo del terreno | **Transformada de Fourier sobre una grilla del doble de tamaño, recortada** | Miles de terrenos por segundo. Es aproximado en los bordes: una prueba lo compara con el método directo (descomposición de la covarianza en NumPy), que es exacto pero toma decenas de milisegundos por terreno. `gstools` simula un terreno a la vez: no |
| Río del terreno | **Una curva suave al azar y su campo de distancia** | Lo más simple que da una tendencia creíble. Nada de redes fluviales |
| Tablas | **Muestreo directo del modelo de 11.2 a 11.4, con n y número de grupos variables y relleno con máscara** | Todos los modelos se muestrean hacia adelante sin iterar |
| Covariables | **Mitad remuestreo perturbado de filas reales, mitad generador paramétrico** (cópula gaussiana con correlaciones y marginales al azar) | Solo con las X del archivo del demo la red no generaliza a las 1.000 empresas de la cartera; solo con el generador puede no cubrir el archivo real. Límite declarado: generaliza hasta donde llega el generador |

Los simuladores no se exportan: se usan solo al entrenar, al validar y para la cartera y la nube (que se precalculan o corren con una copia en NumPy si hace falta en `nucleo/`).

### 3.7 MCMC de referencia (validación y plan B)

Cada motor tiene su modelo escrito una segunda vez, para NUTS. Sirve para dos cosas: es la vara contra la que se valida la red (mismas medias y rangos, y el tiempo de cada uno es la cifra de amortización), y sus muestras precalculadas son la implementación `mcmc`, el plan B de cada tarjeta.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **NumPyro (NUTS) sobre JAX**, solo dentro de `motor/` | Rápido en procesador; los latentes discretos de `estados` se marginalizan con el filtro forward escrito en JAX; cadenas vectorizadas | Dos dependencias más en el grupo `entrenar`; hay que confirmar que instalan (A-01) | **Recomendado** |
| PyMC | Sintaxis más conocida | Compilación más lenta al primer uso; más pesado de instalar | Solo si NumPyro no instala |
| Stan | El de referencia de los libros | Compilar cada modelo en C++ la noche de la hackathon | No |
| Muestreo por importancia en NumPy | Sin dependencias | No escala a 30 parámetros con un latente por unidad | No |

Es acotado: de 5 a 10 datasets simulados por motor, más el real. Corre en un computador que no esté entrenando. En `espacial`, con 155 puntos, tarda segundos: la cifra de amortización ahí son los ~480 análisis rehechos de «¿Dónde mido?».

**El método rápido de siempre** es otra cosa: una regresión logística simple (o kriging con parámetros fijos, en el terreno). No es un motor ni un plan B. Se mide solo para la comparación que muestra qué se pierde sin el modelo completo (A-16).

### 3.8 Formato de entrega de cada red

| Pieza | Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|---|
| Codificador | **ONNX** (`torch.onnx.export`, que hoy usa el exportador nuevo por defecto) | Lo lee `onnxruntime` en el servicio sin `torch` | Necesita `onnx` y `onnxscript`; el número de filas variable se declara con `dynamic_shapes`. **Probar la exportación con la red sin entrenar, motor por motor, la primera noche** | **Recomendado**. En `espacial` incluye la cabeza de mapa |
| Flujo | **`flujo.npz` con los pesos, muestreado en NumPy por `nucleo/flujo.py`** | Sin riesgo de exportación; el acoplamiento afín son productos de matrices | Dos implementaciones del mismo flujo. Prueba obligatoria: con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra, con tolerancia de `float32` | **Recomendado** |
| Flujo | Exportar el flujo entero a ONNX | Un solo archivo | Muestrear dentro del grafo es justo lo que puede no exportar | No |
| Todo | Archivo de pesos de `torch` | Sin exportar | Obliga a tener `torch` en el servicio | Se guarda igual (`pesos.pt`), para seguir entrenando |

Artefactos por motor, en `motor/artefactos/<motor_id>/`: `codificador.onnx`, `flujo.npz`, `pesos.pt`, `config.json`, `sello.json`, `nube.npz` y `mcmc/<clave>.npz` (`contratos/CONTRATO.md`, sección 7).

## 4. PC 3 · seguimiento (monitoreo, casos, datos y pitch)

### 4.1 Qué instalar

```bash
uv sync                 # pandas para preparar los CSV, pytest, pyyaml
uv sync --group entrenar   # D-26: este computador entrena `supervivencia` de noche y `jerarquico` de día
brew install node       # solo para poder levantar la web en local y verificar corriendo
```

PC 3 (MacBook Air M3, 16 GB) instala el grupo `entrenar` solo para **lanzar** entrenamientos y validaciones que escribió PC 2: no edita `motor/`. Mismas precauciones que PC 2 (3.1): enchufado, tapa abierta, `caffeinate -dims`. Además necesita poder correr la app en local (`uv run` y `npm run dev`) porque su trabajo es **verificar corriendo, no leyendo**.

### 4.2 Preparación de datos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Un script de Python por caso, con pandas, en `datos/preparar/`** | Reproducible; deja escrito de dónde salió cada archivo y con qué semilla se vació el 20% | Diez minutos más que hacerlo a mano | **Recomendado** |
| A mano en una planilla | Rápido para mirar | No queda registro; imposible repetir si hay que cambiar algo a las 16:00 | Solo para mirar |

El archivo del terreno viene en un formato del lenguaje R. Para no instalar R, se busca una copia en CSV de los mismos 155 puntos o se lee con el paquete `pyreadr` (`uv run --with pyreadr …`). Lo mismo vale para `meuse.grid` (3.103 celdas con `x`, `y`, `dist`), que desde D-26 hace falta como `datos/demo/terreno_grilla.csv`: la tendencia con la distancia al río se necesita en cada bloque.

### 4.3 Láminas

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Láminas dentro de la misma app** (una vista más, tecla `L`) | No se cambia de ventana en el escenario; el QR y la frase salen con la misma tipografía; no depende de internet | Las escribe PC 1 con el texto de PC 3 | **Recomendado** para portada y cierre |
| Google Slides o Keynote | Rápido de editar por cualquiera | Cambiar de ventana en vivo es donde más demos se traban | Para las láminas de respaldo, que solo se abren si preguntan |

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
| numpyro / jax | sin verificar | MCMC de referencia (NUTS), solo en `motor/`. La versión y que instalen en Python 3.12 en Mac con chip Apple se comprueban en A-01 | por confirmar en A-01 |
| FastAPI / uvicorn | 0.165 / 0.54 | `fastapi[standard]` ya trae uvicorn | fastapi.tiangolo.com |
| Node.js | 26 (LTS) | Vite 8 pide Node 20.19 o superior | nodejs.org |
| Vite / React | 8 / 19 | `npm create vite@latest web -- --template react-ts` | vite.dev |
| Tailwind CSS | 4 | Plugin `@tailwindcss/vite` y una línea `@import "tailwindcss";` | tailwindcss.com |
| Render, plan gratuito | | 0,1 de procesador, 512 MB, se duerme a los 15 minutos, despierta en cerca de un minuto, Python 3.14 por defecto | render.com/docs/free, /docs/python-version |
| Vercel, plan gratuito | | No conecta repositorios de organizaciones; bloquea commits de otros autores en repositorios privados; funciones de Python con 2 GB | vercel.com/docs/limits, /docs/git |

**Sin verificar, hay que probarlo:** que `caffeinate` mantenga despierto el Mac con la tapa cerrada (por eso la tapa queda abierta); las cuotas gratuitas de Kaggle y Colab; que `vercel deploy --prod` evite el bloqueo por autor; que cada codificador exporte a ONNX con n variable (se prueba sin entrenar, motor por motor: A-01, A-03, A-B2, A-N6); que `numpyro` y `jax` instalen en este entorno (A-01); cuántos datasets por segundo simula y entrena cada motor (`medir-rendimiento`).
