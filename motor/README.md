# Krylov · README técnico (borrador)

> Borrador de `amortizacion` (PC 2), puesto al día con el pivote a minería (decisión D-37, sáb 21-nov 12:10). La versión final es la tarea A-35. Aquí van los nombres técnicos precisos; la pantalla y el pitch usan `GLOSARIO.md`. **Solo trae resultados de validación de `espacial`**, copiados de `motor/artefactos/espacial/sello.json`. Los cuatro motores de series están **en construcción (sáb 21-nov)**: lo suyo dice «pendiente» y se llena desde `motor/artefactos/<motor>/sello.json`, nunca de memoria.

## 1. Qué es

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**, para cinco decisiones de una mina. Para cada familia de archivos hay un **motor** con cinco piezas:

| Pieza | Qué es | Dónde está |
|---|---|---|
| Modelo generativo | Un modelo bayesiano explícito del dataset completo: **prior** sobre los parámetros globales → parámetros locales de cada unidad → datos observados, con su error de medición | Ecuaciones en `WORKPLAN.md`, sección 11; encabezado de `nucleo/<motor>.py` |
| Simulador | Ese modelo, vectorizado: genera lotes de datasets completos al vuelo, con tamaño variable | `motor/<motor>/simular.py` |
| Red (NPE) | Un codificador resume el dataset entero en s(D) (128 números) y un **flujo normalizador** condicional entrega el **posterior** amortizado. Se entrena solo con simulaciones (estimación neuronal del posterior, **NPE**) | `motor/<motor>/red.py`, `motor/comun/` |
| Lo local | Lo que falta saber de cada unidad dados los parámetros globales. En `espacial` es exacto: kriging dado θ, en forma cerrada. En los motores de series lo entrega un segundo flujo, chico (amortización factorizada) | `nucleo/<motor>.py`, `nucleo/series.py` |
| MCMC de referencia | NUTS (NumPyro) sobre el mismo modelo y el mismo prior. Valida la red, da la cifra de amortización y es el plan B de la tarjeta, precalculado | `motor/<motor>/mcmc.py` |

Amortizar es pagar el costo de la inferencia una vez, al entrenar: después, el posterior de un dataset nuevo de la misma familia es una pasada de la red y un muestreo del flujo.

Después del posterior viene la **decisión** (`nucleo/decision.py`): con los dos costos del caso, cada unidad queda en «conviene actuar», «no hace falta» o «en duda», y «lo que cuesta no saber» es el valor esperado de la información perfecta.

**Qué existe hoy.** `espacial` está entrenado y validado: su sello dice PASA. `deformacion`, `cinetica`, `desgaste` y `sismico` se escriben y entrenan hoy; no tienen sello ni resultados. Los motores de tabla anteriores al pivote (`supervivencia`, `jerarquico` y `estados`) **se están retirando** del repositorio (tarea A-32) y ya no son parte del producto: si todavía aparecen en `motor/` o en `nucleo/`, es código por borrar.

## 2. Los cinco motores

| Motor | Caso | Modelo generativo, en una línea | Globales | Local, por unidad | Lo que se decide | Estado |
|---|---|---|---|---|---|---|
| `espacial` | `leyes` | Proceso gaussiano con covarianza exponencial y anisotropía geométrica, tendencia opcional y error de medición, sobre una grilla de 32 × 32 (11.6) | θ, 7 | El campo en los bloques sin medir: kriging dado θ | P(valor sobre el umbral) por bloque, y dónde vale más una muestra (`donde_medir`) | **Entrenado y validado** |
| `deformacion` | `taludes` | Dos regímenes por sector, z_j ~ Bernoulli(π): estable, d_j(u) = v_j·u, o acelerando, d_j(u) = v_j·u + A_j·log(u_f,j / (u_f,j − u)) (ley de velocidad inversa); lecturas con ruido gaussiano; jerárquico entre sectores (11.2) | η, 7 | (z_j, log(u_f,j − 1)) | P(z_j = 1 y u_f,j ≤ 1 + H/T) | En construcción, sáb 21-nov |
| `cinetica` | `flotacion` | Cinética de primer orden con fracción rápida y lenta: R_b(t) = Rmax_b·[1 − φ·exp(−k_b·t) − (1 − φ)·exp(−k_b·t/8)], observada solo en las primeras m_b celdas, con error gaussiano; jerárquica entre líneas (11.3) | η, 6 | (log k_b, logit Rmax_b) | P(R_b(t_K) < meta) | En construcción, sáb 21-nov |
| `desgaste` | `flota` | Proceso gamma jerárquico: incrementos ΔX ~ Gamma(forma ν_i·Δt/c², escala c²), con log ν_i ~ Normal(μ_ν + β·x_i, σ_ν) y x_i la exigencia de la ruta; mediciones gaussianas ruidosas; falla cuando X_i cruza 1 (11.4) | η, 5 | (log ν_i, log X_i(t_ahora)) | P(X_i(t_ahora + h_i) ≥ 1) | En construcción, sáb 21-nov |
| `sismico` | `sismicidad` | Proceso de Hawkes temporal con núcleo exponencial y magnitudes: λ_s(t) = μ_s + A_s·ω·e^(−ω·t) + Σ κ(m_i)·ω·e^(−ω·(t − t_i)), con κ(m) proporcional a e^(α·(m − m_0)) y magnitudes exponenciales (Gutenberg-Richter); jerárquico entre sectores (11.5) | η, 6 | (log μ_s, log A_s) | P(al menos un sismo de magnitud ≥ M_c en las próximas H horas) | En construcción, sáb 21-nov |

Los priors, los rangos de cada simulador, el MCMC de referencia y el método rápido de cada motor están en `WORKPLAN.md`, sección 11. No se copian aquí.

**Tamaño.** Los cuatro motores nuevos son chicos a propósito: entre 5 y 7 parámetros globales y 2 locales por unidad. Son la versión que se puede validar en una tarde; los modelos completos son hoja de ruta (sección 7).

**Priors.** En `espacial` son normales truncadas (`motor/espacial/simular.py`, `Prior`) y quedaron en `motor/artefactos/espacial/config.json`. En los motores de series, los de la sección 11 son puntos de partida: antes de lanzar cada entrenamiento se mira el **predictivo a priori** contra el archivo del caso (`python -m motor.<motor>.simular --revisar`), se ajusta, y lo que quede va en el `config.json` del motor.

**Lo que se apartó del plan escrito en `espacial`:** la dirección y la razón de anisotropía se parametrizan juntas, e = log r·(cos 2φ, sin 2φ), y el campo se simula por transformada de Fourier sobre un toro de 128. El caso `leyes` no usa la tendencia: 20% de las simulaciones de entrenamiento no la tenían.

## 3. La red

- **`espacial`** (`motor/espacial/red.py`). Una red convolucional con saltos sobre la grilla de 32 × 32 con tres canales (valor estandarizado, marca de medición, √dist). Dos cabezas: la **cabeza de mapa** da media y desviación por bloque (el predictivo posterior marginal, amortizado) y la **cabeza de flujo** da q(θ | D). La de flujo recibe las características con el gradiente cortado, así la de mapa entrena igual que si estuviera sola (`motor/espacial/prueba_red.py` compara los gradientes). `donde_medir` rehace el análisis para cada lugar candidato y cada resultado posible en un solo lote.
- **El andamio de series** (`motor/comun/series.py` y `nucleo/series.py`; **en construcción**, tarea A-23). Una implementación para los cuatro motores nuevos; cada motor aporta su simulador, su lista de parámetros y su función «lo que se decide». La entrada son tensores con relleno y máscara (unidades, lecturas, canales), con tamaños máximos fijos por motor. Un **codificador por unidad** (convoluciones 1D con máscara y pooling; si no exporta o no aprende, una GRU chica) da s_j; la agregación entre unidades (`motor/comun/codificador.py`: DeepSets con pooling de atención y máscara de relleno, que ya existe) da s(D).
- **Amortización factorizada** en los motores de series: p(η, λ_1..J | y) ≈ q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D)). El **flujo global** entrega η; el **flujo local**, de 2 dimensiones y compartido entre unidades, entrega λ_j. Al entrenar se condiciona en el η verdadero; al responder, en cada muestra de η. Así la dimensión de cada flujo es chica y fija aunque cambie el número de unidades.
- **Posterior** (`motor/comun/flujo.py`). Flujo normalizador condicional de acoplamiento afín (`zuko.flows.NICE`, 8 capas, máscara alternada), sobre los parámetros estandarizados en espacio sin restricciones. **Pérdida NPE:** −log q(θ | s(D)), promediada sobre datasets simulados; en los motores de series, −log q(η | s(D)) − promedio_j log q(λ_j | η, s_j, s(D)).
- **Servicio sin `torch`.** A ONNX se exporta solo el codificador: en `espacial`, con la cabeza de mapa y lote variable; en los motores de series, con formas fijas con relleno y dos salidas, s(D) y los s_j. Los flujos se guardan en `flujo.npz` (y `flujo_local.npz`) y se muestrean en NumPy (`nucleo/flujo.py`). Una prueba exige la misma muestra con los mismos pesos y el mismo ruido (`motor/comun/prueba_flujo.py`). `nucleo/` no importa `torch`, `zuko`, `jax` ni `numpyro`, y una prueba lo comprueba.
- **Un solo preprocesamiento por motor**, en `nucleo/`: la misma función prepara los datasets simulados y el archivo del caso (en `espacial`, `canales_terreno`; en `deformacion` resta el modo común entre sectores y normaliza tiempo y desplazamiento, así el motor no depende de las unidades del archivo).

## 4. Cómo se entrena

```bash
uv sync --group entrenar
uv run python -m motor.<motor>.entrenar --minutos 3 --nuevo            # prueba de humo
uv run python -m motor.<motor>.validar --sbc 200                       # SBC chico: tiene que correr, no pasar
caffeinate -dims uv run python -m motor.<motor>.entrenar --dispositivo cpu --hasta HH:MM --guardar-cada-min 10
```

- Los datasets se simulan al vuelo en cada paso: la red nunca ve dos veces el mismo, y el bucle (`motor/comun/entrenar.py`) cuenta cuántos vio. Esa cuenta es la cifra «practicó con N simulaciones».
- Punto de guardado atómico cada 10 minutos (`motor/checkpoints/<motor>/ultimo.pt`: pesos, optimizador, pasos y conteo); el mismo comando retoma. Los puntos de guardado no se versionan.
- Dispositivo por motor, medido con `python -m motor.<motor>.medir`: `espacial` en la GPU del Mac (7,6 veces el procesador). Los motores de series se miden antes de lanzar cada uno.
- Computadores: MacBook Air M4 de 16 GB (`espacial`; después `cinetica` y `desgaste`) y MacBook Air M3 de 16 GB (`deformacion` y `sismico`). Un entrenamiento por computador, en dos rondas de unos 100 minutos (`WORKPLAN.md`, 6.3). **`espacial` no se reentrena.**

| Motor | Datasets simulados | Minutos | Estado |
|---|---|---|---|
| `espacial` | 7.750.592 | 280 | **Entrenado** (MacBook Air M4 de 16 GB) |
| `cinetica` | pendiente | pendiente | En construcción; ronda 1, sáb 14:30 a 16:10 |
| `deformacion` | pendiente | pendiente | En construcción; ronda 1, sáb 14:30 a 16:10 |
| `desgaste` | pendiente | pendiente | En construcción; ronda 2, sáb 16:30 a 18:15 |
| `sismico` | pendiente | pendiente | En construcción; ronda 2, sáb 16:30 a 18:15 |

## 5. Cómo se valida

Un comando por motor, sin nada entrenando en ese computador (`--ensayo` recorre todo en chico, para probar el programa):

```bash
uv run python -m motor.<motor>.sello
```

Escribe `motor/artefactos/<motor>/sello.json` (lo que muestra la app) y `validacion.json` (el detalle), y termina en PASA o NO PASA. Los chequeos son los de `WORKPLAN.md`, 11.8:

1. **Exportación.** `onnxruntime` y los flujos en NumPy contra `torch`.
2. **SBC y cobertura** en datasets simulados nuevos. SBC (calibración basada en simulación): para un dataset con parámetros verdaderos conocidos se sacan L muestras del posterior amortizado y se cuenta cuántas quedan bajo el valor verdadero; si está calibrado, ese rango es uniforme. Se informa por parámetro y por grupos, con la cobertura del intervalo de 90% contada por rangos, que es exacta (`motor/comun/validacion.py`). En los motores de series se hace **global (η) y local (λ_j)**.
3. **Lo que se decide.** En los motores de series: la cobertura del rango de 90% de la probabilidad de cada unidad contra su valor exacto con el η y el λ_j verdaderos. En `espacial`: la cobertura de la cabeza de mapa en los bloques sin medición.
4. **Contra el MCMC de referencia.** NUTS en datasets simulados (de 3 a 5 en los motores de series) y en el archivo del demo: diferencia de medias del posterior en desviaciones estándar, razón de anchos, r̂ y segundos por dataset. Las muestras del archivo quedan en `mcmc/<caso>.npz`: son el plan B. Si NUTS no converge (r̂ sobre 1,05) en 10 minutos por dataset, se anota y el sello se apoya en el SBC. En `espacial` la referencia marginaliza la estandarización de los datos (derivación en `motor/espacial/mcmc.py`).
5. **El método rápido de siempre.** En `espacial`, kriging con parámetros fijos (lo mide `motor/espacial/sello.py`); en los motores de series, la regla simple de cada caso (11.2 a 11.5). Se mide en las mismas simulaciones y en el mismo examen.
6. **Examen.** Con la **verdad escondida** del archivo del demo (`datos/demo/<caso>_verdad.csv`), que el motor nunca ve. En `espacial`, además, con mediciones reales: se esconde 20% de ellas, con cinco particiones.
7. **Semáforo.** Un archivo con muy pocas lecturas da `rojo_datos`; uno que cae lejos de las simulaciones en el espacio de resúmenes s(D), `rojo_modelo`.

**Un motor pasa** si el SBC no muestra sesgo (criterios de D-32), la cobertura de 90% queda entre 85% y 95% para los parámetros globales y para lo que se decide, la diferencia con el MCMC es menor que 0,3 desviaciones estándar en las medias (si el MCMC convergió) y un análisis tarda menos de 1 segundo. Una tarjeta solo dice que respondió la red si su motor pasó; si no, responde el posterior del MCMC precalculado, rotulado.

| Motor | Sello | SBC | Cobertura del 90% | Diferencia con el MCMC | Examen | Latencia |
|---|---|---|---|---|---|---|
| `espacial` | **PASA** | sin sesgo, en 2.000 datasets simulados nuevos | 0,90 (`cobertura_90`); 0,898 en los parámetros; 0,831 en el peor grupo (alcance largo) | 0,263 desviaciones estándar en las medias, sobre 6 datasets; NUTS tardó 117,1 s por dataset | 138 de 155 mediciones escondidas dentro del rango de 90%, en 5 particiones | 10 ms un análisis; 1.423 ms un lote de 500 grillas |
| `deformacion` | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| `cinetica` | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| `desgaste` | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| `sismico` | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |

Del mismo sello de `espacial`: el método rápido tuvo cobertura de 0,89 en las mismas simulaciones; y la cifra de amortización es rehacer los 228 análisis completos de `donde_medir`, que tomó 0,69 s con la red y 26.698,8 s con el MCMC de referencia.

## 6. Cómo reproducirlo

```bash
uv sync --group entrenar
uv run pytest nucleo motor -q                                  # una prueba por módulo
uv run python -m motor.<motor>.simular --revisar               # predictivo a priori contra el archivo del caso
uv run python -m motor.<motor>.exportar --prueba               # la red sin entrenar exporta y coincide con torch
uv run python -m motor.<motor>.entrenar --hasta HH:MM          # sección 4
uv run python -m motor.<motor>.sello                           # sección 5
```

Con los artefactos en `motor/artefactos/<motor>/`, el servicio responde por `nucleo/api.py` (`casos`, `analizar`, `donde_medir`, `nube`, `sello`, `papeles`, `analizar_archivo`) con `KRYLOV_MOTOR_<MOTOR>=red`; con `mcmc` (el valor por defecto) responde el posterior precalculado. Las semillas de todo lo que se muestra son fijas.

Datos: `datos/demo/leyes.csv` es un banco **simulado** (`datos/preparar/leyes.py`, semilla fija), con su verdad escondida en `leyes_verdad.csv`. Los archivos de los otros cuatro casos se generan igual, con `datos/preparar/<caso>.py` y las ecuaciones de la sección 11. `terreno.csv` y `terreno_grilla.csv` son las mediciones reales públicas con que se examinó `espacial`.

## 7. Límites conocidos

- Cada motor responde una familia de archivos, dentro de los rangos de su simulador (en `espacial`, grilla de 32 × 32 con 30 a 400 mediciones; los de los motores de series, en 11.2 a 11.5).
- `espacial`, según las `limitaciones` de su sello: dos dimensiones; una sola tendencia, la raíz de la distancia a un río; covarianza exponencial con anisotropía geométrica; dos mediciones en el mismo bloque se promedian.
- Ningún motor es todavía el modelo completo (`WORKPLAN.md`, 1.2): `espacial` no separa dominios geológicos; `deformacion` no lleva el muro entero con miles de nodos; `cinetica` no resuelve las ecuaciones de varias fases; `desgaste` no cruza telemetría; `sismico` es temporal y no usa la ubicación de cada sismo.
- En `sismico`, «lo que se decide» sale de la intensidad esperada en forma cerrada con una aproximación de Poisson; la tarea A-28 pide una prueba que la compare con simular hacia adelante.
- En `deformacion` el posterior es multimodal (dos regímenes por sector): el MCMC de referencia marginaliza z_j, corre con 4 cadenas e informa r̂.
- `rojo_modelo` se apoya en un resumen aprendido: no garantiza que todo archivo raro caiga fuera.
