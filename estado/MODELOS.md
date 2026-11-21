# Los cinco modelos · cómo opera cada uno y qué falta

Una sección por motor. La mantiene quien construye el motor (skill `actualizar-estado`): al terminar una pieza marca su casilla y reescribe «Falta ahora». El tablero en vivo (https://silent-math.github.io/krylov-panel/) dibuja este archivo junto con el bloque de ecuaciones de cada motor en `WORKPLAN.md`, sección 11; las ecuaciones se escriben solo allá.

**Formato (lo lee el tablero; no cambiar la forma):** el título es `` ## `motor` · caso `caso` ``. Después, un párrafo que empieza con `**Cómo opera, en simple.**`; una tabla `### Niveles` con las columnas `Nivel | Símbolo | Qué es | A priori`; una lista `### Estado` con las trece casillas `- [x]` o `- [ ]`, siempre en el mismo orden y con el mismo nombre (lo que va después de los dos puntos es una nota libre: un número medido, qué falta); y una línea `**Falta ahora:**`. Una casilla se marca solo cuando la pieza corrió y se verificó.

## `espacial` · caso `leyes`

**Cómo opera, en simple.** La roca vecina se parece: si un pozo trae mucho arsénico, los bloques de al lado probablemente también. Krylov inventó millones de bancos (los pisos del rajo) con reglas distintas de cuánto se parece la roca vecina y en qué dirección, y practicó adivinando esas reglas a partir de las muestras. Con el archivo de una tronadura dibuja el mapa de arsénico, bloque por bloque, con su rango. Con eso dice qué bloques conviene apartar, cuáles pueden ir a la planta y en cuáles no se sabe; y dónde una muestra más vale más plata.

### Niveles

| Nivel | Símbolo | Qué es | A priori |
|---|---|---|---|
| Tamaño del dataset | n | Cuántos bloques del banco traen muestra, y cómo están repartidos (al azar, agrupados o en una franja) | log-uniforme de 30 a 400, sobre una grilla de 32 × 32 bloques |
| Parámetros de la faena | a | Hasta qué distancia la roca vecina se parece (alcance), en bloques | log a ~ Normal(log 4,5; 0,55) |
| Parámetros de la faena | e₁, e₂ | En qué dirección se parece más, y cuánto más (anisotropía) | Normal(0; 0,5) cada uno |
| Parámetros de la faena | σ | Cuánto varía la ley dentro del banco | log σ ~ Normal(0; 0,4), en unidades estandarizadas |
| Parámetros de la faena | τ | Error de cada muestra | log τ ~ Normal(log 0,35; 0,7) |
| Parámetros de la faena | β₀, β₁ | Nivel general y tendencia del banco (el caso `leyes` no usa la tendencia) | Normal(0; 1) y Normal(0; 4); 20% de los bancos simulados sin tendencia |
| Parámetros de cada unidad | y(s) | La ley verdadera de cada bloque, que no se ve | Proceso gaussiano con covarianza exponencial; dado lo anterior se calcula exacto (kriging) |
| Lo que se mide | z_j | La ley medida en la muestra de cada pozo (en `leyes`, el logaritmo del arsénico en ppm) | z_j = y(s_j) + error Normal(0; τ) |
| Lo que se decide | p_bloque | Probabilidad de que el bloque supere el límite de arsénico | Sale de lo anterior; el límite lo pone el caso (500 ppm) |

### Estado

- [x] Ecuaciones escritas: `WORKPLAN.md` 11.6 y `motor/espacial/simular.py`
- [x] A priori de tamaño: entre 30 y 400 muestras, tres formas de repartirlas
- [x] Simulador
- [ ] Predictivo a priori contra el archivo del demo: se miró contra `terreno.csv`; falta mirarlo contra `leyes.csv`
- [x] Red
- [x] Prueba de humo
- [x] Entrenamiento: 7.750.592 terrenos simulados en 280 min
- [x] SBC global: pasa; cobertura del 90% de los parámetros, 0,898
- [x] SBC por unidad: aquí es la cobertura del mapa, bloque por bloque, 0,90
- [x] Cobertura de lo que se decide, por tamaño: con menos y con más de 100 muestras; peor grupo 0,831 (alcance largo)
- [x] Examen con la verdad escondida: 61 de 68 muestras escondidas de `leyes` dentro del rango
- [ ] Exportación y app: exportada y responde por `nucleo/api.py`; falta verla en la app (P-22)
- [x] Método lento: 117 s por análisis en 6 terrenos simulados; falta el del archivo `leyes` (A-22)

**Falta ahora:** verla en la app (P-22) y el método lento del archivo `leyes` con su tiempo (A-22).

## `deformacion` · caso `taludes`

**Cómo opera, en simple.** Un radar mide cuántos milímetros se mueve cada sector del muro. Casi todos los sectores se mueven lento y parejo; unos pocos se mueven cada vez más rápido, y esos son los que pueden ceder. Krylov practicó con muros inventados donde se sabía qué sectores se estaban acelerando y cuánto les faltaba. Con las lecturas de un muro dice, sector por sector, qué tan probable es que ceda dentro del plazo que importa, y cuánto falta, con su rango.

### Niveles

| Nivel | Símbolo | Qué es | A priori |
|---|---|---|---|
| Tamaño del dataset | J | Cuántos sectores trae el archivo | log-uniforme de 6 a 80 |
| Tamaño del dataset | K_j | Cuántas lecturas tiene cada sector (distinto en cada uno, con lecturas faltantes) | de 24 a 200; hasta 15% faltantes al azar |
| Parámetros de la faena | π | Qué parte de los sectores se está acelerando | Beta(1,5; 6) |
| Parámetros de la faena | μ_v, σ_v | Velocidad de fondo del muro y cuánto cambia entre sectores | Normal(0; 0,6) y HalfNormal(0,7), en log |
| Parámetros de la faena | μ_f, σ_f | Cuánto falta para que ceda un sector que se acelera, y cuánto cambia entre sectores | Normal(log 0,3; 0,8) y HalfNormal(0,6), en log |
| Parámetros de la faena | μ_A | Qué tan fuerte es la aceleración | Normal(log 1,5; 0,6) |
| Parámetros de la faena | σ_e | Error de cada lectura | LogNormal(log 0,05; 0,7) |
| Parámetros de cada unidad | z_j | Si el sector se está acelerando (sí o no) | Bernoulli(π) |
| Parámetros de cada unidad | v_j | Velocidad de fondo del sector | log v_j ~ Normal(μ_v; σ_v) |
| Parámetros de cada unidad | u_f,j | Cuándo cedería el sector, si se está acelerando | log(u_f,j − 1) ~ Normal(μ_f; σ_f) |
| Parámetros de cada unidad | A_j | Qué tan fuerte se acelera el sector | log A_j ~ Normal(μ_A; 0,5) |
| Lo que se mide | y_jk | Desplazamiento acumulado del sector en cada lectura | Trayectoria del sector + error Normal(0; σ_e) |
| Lo que se decide | p_j | Probabilidad de que el sector ceda dentro del horizonte | Sale de lo anterior; el horizonte lo pone el caso |

### Estado

- [x] Ecuaciones escritas: `WORKPLAN.md` 11.2
- [x] A priori de tamaño: 6 a 80 sectores, 24 a 200 lecturas, hasta 15% faltantes por sector (`nucleo/deformacion.py`, `DISENO`)
- [x] Simulador: `motor/deformacion/simular.py`; pasa por el mismo preprocesamiento que el archivo (modo común, escala e)
- [x] Predictivo a priori contra el archivo del demo: dentro de los percentiles 2 y 98 (`motor/deformacion/prueba_deformacion.py`)
- [x] Red: el andamio de series con estado discreto por sector, sin entrenar; exporta y responde `analizar("taludes")` con la forma del contrato
- [x] Prueba de humo: 129.536 datasets en 3 min (GPU del Mac, lote 128); la pérdida bajó de 10,2 a 4,9; el SBC de 200 corre
- [ ] Entrenamiento: en curso en PC 3 desde las 13:44, hasta las 16:10 (GPU del Mac, lote 128; cerca de 510 datasets por segundo)
- [ ] SBC global
- [ ] SBC por unidad
- [ ] Cobertura de lo que se decide, por tamaño
- [ ] Examen con la verdad escondida
- [ ] Exportación y app
- [ ] Método lento

**Falta ahora:** que termine su entrenamiento en PC 3 (16:10) y validarlo ahí, sin método lento (S-28).

## `cinetica` · caso `flotacion`

**Cómo opera, en simple.** En cada línea de la planta el cobre flota rápido al principio y cada vez más lento. Krylov practicó con plantas inventadas donde se sabía cómo terminaba cada línea. Con lo medido en las primeras celdas dice cuánto cobre va a recuperar la línea al final, con su rango. Lo que aprende de una línea le sirve para las demás, y con eso dice qué líneas conviene ajustar ahora y en cuáles conviene esperar otra medición.

### Niveles

| Nivel | Símbolo | Qué es | A priori |
|---|---|---|---|
| Tamaño del dataset | B | Cuántas líneas trae el archivo | de 2 a 16 |
| Tamaño del dataset | K, m_b | Cuántas celdas tiene una línea y en cuántas de las primeras ya se midió (distinto en cada línea) | K de 5 a 12; m_b de 3 a K |
| Tamaño del dataset | Δ | Minutos que la pulpa pasa en cada celda (cada línea varía hasta 15%) | log-uniforme de 2 a 6 |
| Parámetros de la faena | μ_k, σ_k | Qué tan rápido flota el cobre en esta planta y cuánto cambia entre líneas | Normal(log 0,25; 0,6) y HalfNormal(0,5), en log |
| Parámetros de la faena | μ_R, σ_R | Cuánto cobre se puede recuperar como máximo y cuánto cambia entre líneas | Normal(logit 0,90; 0,6) y HalfNormal(0,6), en logit |
| Parámetros de la faena | φ | Qué parte del cobre flota rápido | Beta(4; 2) |
| Parámetros de la faena | σ_y | Error de cada medición | LogNormal(log 0,015; 0,5) |
| Parámetros de cada unidad | k_b | Velocidad de flotación de la línea | log k_b ~ Normal(μ_k; σ_k) |
| Parámetros de cada unidad | Rmax_b | Tope de recuperación de la línea | logit Rmax_b ~ Normal(μ_R; σ_R) |
| Lo que se mide | y_bk | Parte del cobre ya recuperada a la salida de cada celda medida | Curva de la línea + error Normal(0; σ_y) |
| Lo que se decide | p_b | Probabilidad de que la línea termine bajo la meta de recuperación | Sale de lo anterior; la meta la pone el caso |

### Estado

- [x] Ecuaciones escritas: `WORKPLAN.md` 11.3
- [x] A priori de tamaño: 2 a 16 líneas, 5 a 12 celdas, 3 al total medidas (`nucleo/cinetica.py`, `DISENO`)
- [x] Simulador: `motor/cinetica/simular.py`
- [x] Predictivo a priori contra el archivo del demo: dentro de los percentiles 2 y 98 (`motor/cinetica/prueba_cinetica.py`)
- [x] Red: el andamio de series, sin entrenar
- [x] Prueba de humo: 305.536 datasets en 3 min (CPU, lote 128); la pérdida media bajó de 6,9 a 4,0; el SBC de 200 corre
- [ ] Entrenamiento
- [ ] SBC global
- [ ] SBC por unidad
- [ ] Cobertura de lo que se decide, por tamaño
- [ ] Examen con la verdad escondida
- [ ] Exportación y app
- [ ] Método lento

**Falta ahora:** lanzar su entrenamiento en la ronda 1 (A-26) cuando el equipo dé la partida.

## `desgaste` · caso `flota`

**Cómo opera, en simple.** El desgaste de un camión no se ve, pero deja huella en lo que se mide (por ejemplo, el hierro en el aceite). Avanza a saltos y nunca retrocede, y más rápido en las rutas exigentes. Krylov practicó con flotas inventadas donde se sabía cuándo fallaba cada camión. Con las muestras de una flota dice qué tan probable es que cada camión falle antes de su próxima mantención programada, y cuál conviene parar antes.

### Niveles

| Nivel | Símbolo | Qué es | A priori |
|---|---|---|---|
| Tamaño del dataset | M | Cuántos camiones trae el archivo | log-uniforme de 8 a 120 |
| Tamaño del dataset | J_i | Cuántas muestras tiene cada camión (distinto en cada uno, a intervalos irregulares) | de 3 a 20 |
| Parámetros de la faena | μ_ν, σ_ν | Ritmo de desgaste de la flota y cuánto cambia entre camiones | Normal(log 0,5; 0,5) y HalfNormal(0,5), en log |
| Parámetros de la faena | β | Cuánto acelera el desgaste una ruta exigente | Normal(0,3; 0,3) |
| Parámetros de la faena | c | Qué tan a saltos avanza el desgaste | LogNormal(log 0,3; 0,4) |
| Parámetros de la faena | σ_ε | Error de cada medición | LogNormal(log 0,04; 0,5) |
| Parámetros de cada unidad | ν_i | Ritmo de desgaste del camión | log ν_i ~ Normal(μ_ν + β·x_i; σ_ν) |
| Parámetros de cada unidad | X_i(t) | Desgaste que lleva el camión hoy, que no se ve | Proceso gamma: avanza ν_i por cada mil horas, a saltos |
| Lo que se mide | y_ij | El indicador de desgaste en cada muestra (la falla es 1,0) | X_i(t_ij) + error Normal(0; σ_ε) |
| Lo que se decide | p_i | Probabilidad de que el camión falle antes de su próxima mantención | Sale de lo anterior; las horas que faltan vienen en el archivo |

### Estado

- [x] Ecuaciones escritas: `WORKPLAN.md` 11.4
- [ ] A priori de tamaño
- [ ] Simulador
- [ ] Predictivo a priori contra el archivo del demo
- [ ] Red
- [ ] Prueba de humo
- [ ] Entrenamiento
- [ ] SBC global
- [ ] SBC por unidad
- [ ] Cobertura de lo que se decide, por tamaño
- [ ] Examen con la verdad escondida
- [ ] Exportación y app
- [ ] Método lento

**Falta ahora:** su simulador con el a priori de tamaño, sobre el andamio que ya existe (A-27, ronda 2).

## `sismico` · caso `sismicidad`

**Cómo opera, en simple.** Después de una tronadura la roca sigue crujiendo, y cada temblor sube por un rato la probabilidad del siguiente. Krylov practicó con minas inventadas donde se sabía qué pasó después en cada sector. Con los temblores registrados hasta ahora dice, sector por sector, qué tan probable es un temblor fuerte en las próximas horas. Apoya la decisión del especialista sobre el reingreso; no la reemplaza.

### Niveles

| Nivel | Símbolo | Qué es | A priori |
|---|---|---|---|
| Tamaño del dataset | S | Cuántos sectores trae el archivo | de 2 a 16 |
| Tamaño del dataset | T | Cuántas horas se llevan observadas desde la tronadura | log-uniforme de 2 a 24 h |
| Tamaño del dataset | N_s | Cuántos temblores registró cada sector | Los genera el proceso; tope de 300 por sector |
| Parámetros de la faena | μ_μ, σ_μ | Cuánto tiembla la mina sin tronadura y cuánto cambia entre sectores | Normal(log 0,5; 0,7) y HalfNormal(0,6), en log |
| Parámetros de la faena | n | Cuántos temblores nuevos gatilla, en promedio, cada temblor | Beta(3; 4) |
| Parámetros de la faena | α | Cuánto más gatilla un temblor grande | LogNormal(log 1,0; 0,3) |
| Parámetros de la faena | ω | Qué tan rápido se calma la roca | LogNormal(log 1,5; 0,5) |
| Parámetros de la faena | b | Cuántos temblores chicos hay por cada grande | LogNormal(log 1,0; 0,15) |
| Parámetros de cada unidad | μ_s | Cuánto tiembla el sector por sí solo | log μ_s ~ Normal(μ_μ; σ_μ) |
| Parámetros de cada unidad | A_s | Cuántos temblores gatilló directamente la tronadura en el sector | log A_s ~ Normal(log 8; 0,6) |
| Lo que se mide | t_i, m_i | La hora y la magnitud de cada temblor registrado | Proceso de Hawkes; magnitudes con Gutenberg-Richter |
| Lo que se decide | p_s | Probabilidad de al menos un temblor fuerte en las próximas horas | Sale de lo anterior; la magnitud y el plazo los pone el caso |

### Estado

- [x] Ecuaciones escritas: `WORKPLAN.md` 11.5
- [ ] A priori de tamaño
- [ ] Simulador
- [ ] Predictivo a priori contra el archivo del demo
- [ ] Red
- [ ] Prueba de humo
- [ ] Entrenamiento
- [ ] SBC global
- [ ] SBC por unidad
- [ ] Cobertura de lo que se decide, por tamaño
- [ ] Examen con la verdad escondida
- [ ] Exportación y app
- [ ] Método lento

**Falta ahora:** su simulador con el a priori de tamaño, sobre el andamio que ya existe (A-28, ronda 2).
