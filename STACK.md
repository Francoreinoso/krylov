# Krylov · Stack: qué instalar en cada computador y por qué

> **Hackathon:** el producto se termina el sábado a las 18:00. Este archivo existe para que nadie pierda una hora eligiendo herramientas ni instale algo que después no sirve en el servidor.

## 0. Cómo se usa este archivo

1. Cada computador instala **lo común** (sección 1) y **lo suyo** (secciones 2, 3 o 4).
2. Cada herramienta trae una tabla de alternativas con pros y contras **para este caso de uso**, una recomendación y una **regla para cambiar**. La recomendación es el punto de partida, no una orden: si el agente o la persona ve que la regla para cambiar se cumple, cambia y lo anota.
3. Lo que se elija se anota en `estado/<rol>.md` con una línea de por qué. Si la elección afecta a otro computador (por ejemplo, el formato en que se exporta la red), además va una entrada en `DECISIONES.md`.
4. Las versiones de la sección 5 se verificaron en las páginas oficiales el 21 de noviembre de 2026. Lo que dice «por medir» o «sin verificar» no se da por cierto: se prueba.

El caso de uso, en una línea, para juzgar cada alternativa: **una app web de cuatro vistas que se muestra una vez en un escenario, una URL pública que toda la sala abre a la vez desde el teléfono, y una red convolucional chica que se entrena una noche en un MacBook Air sin ventilador.** No hay usuarios, ni cuentas, ni datos que guardar.

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
| Base | `numpy`, `pyyaml`, `onnxruntime`, `fastapi[standard]`, `anthropic`, `pandas`, `pytest` | Los tres, y el servidor | `uv sync` |
| Grupo `entrenar` | `torch`, `onnx`, `onnxscript` y, solo si se llega al opcional A-16, `zuko` | Solo PC 2 | `uv sync --group entrenar` |

**Regla que no se rompe:** `nucleo/` y `servicio/` no importan `torch`. El servidor gratuito tiene 512 MB de memoria y el paquete de `torch` para Linux pesa más que eso. La red se entrena con `torch` y se sirve con `onnxruntime`, que pesa unos 28 MB.

### 1.3 Los dos repositorios espejo

Cada computador clona el repositorio de la organización y le agrega el espejo como segundo destino de push. Los comandos exactos y su verificación están en el archivo `PC*.md` de cada computador, sección «Arranque».

## 2. PC 1 · producto (backend, frontend y despliegue)

### 2.1 Qué instalar

```bash
# desde la raíz del repositorio
uv sync                                   # backend: FastAPI, NumPy, onnxruntime, anthropic
npm create vite@latest web -- --template react-ts
cd web && npm install
npm install tailwindcss @tailwindcss/vite  # solo si se elige Tailwind (2.3)
npm install -g vercel                      # solo si hace falta desplegar por línea de comandos (2.6)
```

Variables de entorno, en un archivo `.env` que **no** se sube: `ANTHROPIC_API_KEY`, `KRYLOV_MOTOR_ESPACIAL` (`exacto` o `red`). En la web: `VITE_API_URL`.

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
| Sin backend: todo precalculado | La URL pública no se puede caer | «Sube tus datos» y el cálculo en vivo del escenario dejan de existir | **Es el modo estático**, que se construye igual. No reemplaza al backend en el escenario |
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
| Funciones de Python en Vercel | 2 GB y un procesador entero; no se duerme del mismo modo | Otra forma de empaquetar la API; arranque en frío de unos segundos | Plan B si «Sube tus datos» tarda más de 10 segundos en Render ya despierto |
| Túnel desde PC 1 (cloudflared, ngrok) | Toda la potencia del computador | Depende del wifi del lugar y de que el computador no se cierre | Solo para mostrarle algo a alguien en la mesa |

Configuración de Render: lenguaje «Python 3»; comando de construcción `pip install -r requirements.txt`; comando de inicio `uvicorn servicio.app:app --host 0.0.0.0 --port $PORT`; variable `PYTHON_VERSION` con una versión 3.12 completa (por ejemplo `3.12.x`, la que muestre `uv python list`); variables `ANTHROPIC_API_KEY` y `KRYLOV_MOTOR_ESPACIAL`. El `requirements.txt` sale de `uv export --no-dev --no-hashes -o requirements.txt` y no incluye el grupo `entrenar`.

**El escenario: el computador que presenta, en local.** API y web corriendo en ese computador, con todo precargado y probado sin wifi. La URL pública es para la entrega y para el QR.

### 2.7 Cómo corre la red dentro del servicio

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **onnxruntime (Python) con el modelo exportado a ONNX** | 28 MB; arranca en milisegundos; rápido en procesador; el mismo archivo sirve en el escenario y en el servidor | Un paso de exportación en PC 2, que hay que probar temprano | **Recomendado** |
| `torch` en el servicio | Sin exportar nada | No cabe en el servidor gratuito; arranque lento | Solo en el computador del escenario, y solo si la exportación falla |
| Pasada hacia adelante escrita en NumPy | Cero dependencias | Reescribir convoluciones a mano es una fuente de errores silenciosos | Último recurso |
| onnxruntime-web, la red corriendo en el navegador | Cualquier teléfono simularía mediciones sin servidor: buen golpe de efecto | Con Vite no funciona sin ajustes (hay que servir los archivos `.wasm` y fijar la versión exacta); una hora de riesgo en la tarde | Opcional de P-13, solo si H3 pasó limpio. La versión precalculada se ve igual para quien escanea el QR |

### 2.8 Capa de lenguaje (Claude)

Una sola llamada por archivo subido (proponer columnas) y una por respuesta (tres frases). Se usa el SDK oficial `anthropic` de Python con salida estructurada. **Antes de escribir este código, el agente carga la skill `claude-api`**: varios parámetros que eran habituales ya no existen (temperatura, presupuesto de razonamiento, forzar una herramienta), y de memoria se escribe mal.

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **`claude-opus-5-5` con esfuerzo `low`** | Es el modelo que Anthropic recomienda por defecto; mejor criterio para decidir qué columnas sirven y cuáles delatan la respuesta | Más lento y más caro por llamada (irrelevante a esta escala); no se le puede apagar el razonamiento | **Punto de partida** |
| `claude-haiku-5-5` | El más rápido y barato | Menos criterio en archivos raros | Se cambia a este si la llamada medida pasa de 3 segundos |
| Sin modelo: reglas fijas | Funciona sin internet | No «entiende» nada | Es el respaldo que se construye igual |

Ninguna de las dos llamadas está en el camino del escenario: las tarjetas usan frases de plantilla si la capa no responde.

### 2.9 Lo que no se instala

Base de datos, autenticación, colas, Docker, bibliotecas de estado global, pruebas de extremo a extremo. Nada de eso se ve en el demo.

## 3. PC 2 · amortización de los modelos (MacBook Air M4, 16 GB, sin ventilador)

### 3.1 Qué instalar

```bash
uv python install 3.12
uv sync --group entrenar        # torch, onnx, onnxscript + la base (numpy, onnxruntime…)
uv run python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"
uv run python -c "import numpy; numpy.show_config()"    # debe decir Accelerate
```

No hace falta Node. Antes de lanzar nada largo: enchufado, **tapa abierta**, brillo al mínimo, sobre una superficie dura, modo de bajo consumo apagado, y el comando dentro de `caffeinate -dims`. Con la tapa cerrada y sin pantalla externa, `caffeinate` no garantiza que el equipo siga despierto: no hay documentación oficial que lo afirme, y las fuentes que existen se contradicen.

### 3.2 Framework de entrenamiento

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **PyTorch 2.15** | Convoluciones y transformada de Fourier corren en la GPU del Mac; exporta a ONNX con una función; es lo que el equipo y los agentes conocen mejor; el mismo código corre en la nube si hay que salir | La GPU del Mac no admite números de doble precisión: todo en `float32` | **Recomendado** |
| MLX (Apple) | Hecho para estos chips; convoluciones y Fourier disponibles | No exporta a ONNX de forma oficial, así que el servicio no podría usar la red sin reescribirla; menos ejemplos | No, por la exportación |
| JAX | Rápido en procesador, elegante para simuladores | En Mac es solo procesador en la práctica; exportar a ONNX pasa por paquetes de terceros | No |

### 3.3 Procesador o GPU del Mac

No se decide de memoria: se mide con la skill `medir-rendimiento` sobre la red real, dos minutos en cada uno y dos minutos sostenidos.

| Alternativa | Cuándo conviene |
|---|---|
| GPU del Mac (`mps`) | Si rinde más de 1,5 veces lo del procesador en la red real y no aparecen avisos de operaciones que caen al procesador. Con redes convolucionales suele ganar; **por medir** |
| Procesador (`cpu`) | Si la red es muy chica o si `mps` se calienta y cae más de 30% en dos minutos |
| Nube (Kaggle o Colab gratuitos) | Solo si a las 09:00 el entrenamiento nocturno no sirve y hay que rehacerlo rápido. Las cuotas gratuitas no se pudieron confirmar en páginas oficiales: abrir una sesión y mirar antes de contar con ella |

### 3.4 Qué aprende la red, y con qué biblioteca

Hay dos formas de amortizar el motor espacial. Se eligió la primera como obligatoria y la segunda como opcional.

| Alternativa | Qué entrega | Pros | Contras | Veredicto |
|---|---|---|---|---|
| **Red que devuelve el mapa completo** (entra la grilla con las mediciones, sale el valor esperado y su margen en cada bloque) | El mapa de tres colores y «¿Dónde mido?» en una sola pasada por lote | Es una red convolucional común con una función de pérdida simple; entrena estable; rehacer 500 análisis es una pasada de 500 grillas, sin ningún cálculo exacto en el medio | No entrega los parámetros del terreno (alcance, dirección) | **Obligatoria**. PyTorch puro, sin biblioteca extra |
| Red que devuelve los parámetros del terreno (flujo normalizador) y después un cálculo exacto por cada versión | Los cuatro parámetros con su rango, y permite corregir con la fórmula exacta | Es la inferencia amortizada clásica y da una frase más para el show («manda el río») | El cálculo exacto por versión vuelve a ser el cuello de botella en «¿Dónde mido?»; entrenar un flujo es más delicado | **Opcional** (A-16), con `zuko` |

Si se llega al opcional, estas son las bibliotecas posibles:

| Biblioteca | Pros | Contras | Veredicto |
|---|---|---|---|
| **`zuko`** | Flujos normalizadores en PyTorch, liviana, se enchufa a cualquier red propia | Hay que escribir el bucle de entrenamiento | **Recomendada** para el opcional |
| `sbi` | Bucle de entrenamiento y diagnósticos incluidos | Pensada para simuladores lentos y bancos fijos; aquí el simulador es rápido y se entrena al vuelo, y su estructura estorba | No |
| BayesFlow | Flujo de trabajo completo y diagnósticos de calibración | Corre sobre Keras con otro motor por debajo y solo en Python 3.12 o 3.13: un entorno más que cuidar la noche de la hackathon | No |

### 3.5 Cómo se le pasan los datos a la red

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Grilla fija de 32×32 con un canal que marca dónde hay medición** | Red convolucional estándar; agregar una medición hipotética es marcar una celda; cualquier terreno entra igual | Dos puntos en la misma celda se promedian; la resolución es fija | **Recomendado** |
| Puntos sueltos de cantidad variable (redes de conjuntos o de atención) | Sin pérdida de resolución | Es investigación, no hackathon: más difícil de entrenar y de depurar en una noche | No |

### 3.6 Simulador de terrenos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Transformada de Fourier sobre la grilla, en lotes, con `torch`** | Miles de terrenos por segundo; se simula al vuelo durante el entrenamiento, sin guardar nada en disco; la cifra «practicó con N millones de terrenos» sale de aquí | Es aproximado en los bordes (se simula una grilla más grande y se recorta); hay que comprobarlo contra el método directo en una prueba | **Recomendado** |
| Método directo con NumPy (descomposición de la matriz de covarianza) | Exacto; ya está medido en este computador para puntos sueltos | Para 1.024 celdas son decenas de milisegundos por terreno: un millón de terrenos tomaría horas | Solo como referencia para la prueba y para el método exacto |
| Biblioteca de geoestadística (`gstools`) | Simuladores listos | Una dependencia más, pensada para un terreno a la vez, no para lotes | No |

### 3.7 Método exacto (referencia y plan B)

| Motor | Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|---|
| `regresion` | **NumPy: aproximación clásica corregida con muestreo por importancia** | Milisegundos; sin dependencias; se puede aplicar a mil empresas en un lote | Hay que escribir unas 60 líneas con cuidado | **Recomendado** |
| `regresion` | `statsmodels` o `scikit-learn` | Una línea | Entregan un punto y un error aproximado, no las versiones creíbles que necesita «lo que cuesta no saber» | Solo para contrastar resultados en una prueba |
| `regresion` | Stan o PyMC | El método de referencia de los libros | Compilación y segundos por análisis; dependencias pesadas | No |
| `espacial` | **NumPy: muestreo por importancia sobre los cuatro parámetros** | Uno o dos segundos por análisis; es la vara contra la que se valida la red y el plan B del mapa | Lento para rehacer cientos de análisis, que es justo el argumento del show | **Recomendado** |
| `espacial` | Kriging con parámetros fijos | Instantáneo; es «el método rápido de siempre» | Subestima cuánto se puede equivocar cuando hay pocos puntos. Se mide para decirlo, no se usa | Solo como comparación (A-14) |

### 3.8 Formato de entrega de la red

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **ONNX** (`torch.onnx.export`, que hoy usa el exportador nuevo por defecto) | Lo lee `onnxruntime` en el servicio sin `torch` | Necesita `onnx` y `onnxscript`; el tamaño de lote variable se declara con `dynamic_shapes`. **Probar la exportación con la red sin entrenar, en A-03, no a las 9 de la mañana** | **Recomendado** |
| Archivo de pesos de `torch` | Sin exportar | Obliga a tener `torch` en el servicio | Se guarda igual, para seguir entrenando |

El simulador no se exporta: la transformada de Fourier se usa solo al entrenar.

## 4. PC 3 · seguimiento (monitoreo, casos, datos y pitch)

### 4.1 Qué instalar

```bash
uv sync                 # pandas para preparar los CSV, pytest, pyyaml
brew install node       # solo para poder levantar la web en local y verificar corriendo
```

PC 3 no instala `torch`. Necesita poder correr la app en local (`uv run` y `npm run dev`) porque su trabajo es **verificar corriendo, no leyendo**.

### 4.2 Preparación de datos

| Alternativa | Pros | Contras | Veredicto |
|---|---|---|---|
| **Un script de Python por caso, con pandas, en `datos/preparar/`** | Reproducible; deja escrito de dónde salió cada archivo y con qué semilla se vació el 20% | Diez minutos más que hacerlo a mano | **Recomendado** |
| A mano en una planilla | Rápido para mirar | No queda registro; imposible repetir si hay que cambiar algo a las 16:00 | Solo para mirar |

El archivo del terreno viene en un formato del lenguaje R. Para no instalar R, se busca una copia en CSV de los mismos 155 puntos o se lee con el paquete `pyreadr` (`uv run --with pyreadr …`).

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
| zuko | 1.6.0 | Solo para el opcional | PyPI |
| FastAPI / uvicorn | 0.165 / 0.54 | `fastapi[standard]` ya trae uvicorn | fastapi.tiangolo.com |
| Node.js | 26 (LTS) | Vite 8 pide Node 20.19 o superior | nodejs.org |
| Vite / React | 8 / 19 | `npm create vite@latest web -- --template react-ts` | vite.dev |
| Tailwind CSS | 4 | Plugin `@tailwindcss/vite` y una línea `@import "tailwindcss";` | tailwindcss.com |
| Render, plan gratuito | | 0,1 de procesador, 512 MB, se duerme a los 15 minutos, despierta en cerca de un minuto, Python 3.14 por defecto | render.com/docs/free, /docs/python-version |
| Vercel, plan gratuito | | No conecta repositorios de organizaciones; bloquea commits de otros autores en repositorios privados; funciones de Python con 2 GB | vercel.com/docs/limits, /docs/git |

**Sin verificar, hay que probarlo:** que `caffeinate` mantenga despierto el Mac con la tapa cerrada (por eso la tapa queda abierta); las cuotas gratuitas de Kaggle y Colab; que `vercel deploy --prod` evite el bloqueo por autor; que la red exporte a ONNX sin tropiezos (se prueba en A-03).
