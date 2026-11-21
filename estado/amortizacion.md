# Estado · amortizacion (PC 2)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 2 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago.
Persona: Rodrigo · Dueño de `nucleo/` y `motor/`. Instrucciones: `PC2_AMORTIZACION.md`.

## Hecho

- sáb 03:00 · Plan final recibido. Nada construido todavía.
- sáb 03:24 · Arranque de PC 2 (sesión A): clon con dos destinos de push y rol declarado. Primer commit propio; `git ls-remote` de los dos repositorios comparado.
- sáb 03:31 · **A-01 terminada.** `pyproject.toml` con el grupo `entrenar` y `uv.lock`; `motor/comun/` (`codificador.py`, `flujo.py`, `entrenar.py`) y `nucleo/flujo.py`. Ver: `uv sync --group entrenar && uv run pytest motor/comun -q` (15 pruebas pasan, 8 s).
- sáb 03:31 · A-01, las tres comprobaciones, corridas: (1) los pesos de `zuko.flows.NICE` se leen capa por capa (máscara alternada fija + MLP de tres lineales con ReLU; la escala es `e/(1+|e|/|ln 1e-3|)`): **se usa `zuko`**, sin acoplamiento propio. (2) `numpyro` 0.22.0 y `jax` 0.12.1 instalan en Python 3.12.16 y NUTS corre (300+300 pasos de un modelo de juguete en 1,4 s). (3) El pooling de atención con máscara exporta a ONNX con lote y n variables (exportador nuevo, `dynamo=True` con `dynamic_shapes`) y `onnxruntime` coincide con `torch`: **queda el pooling de atención**.
- sáb 03:30 · **A-B1 terminada (sesión B).** `motor/supervivencia/simular.py`: el modelo generativo de 11.2 en NumPy, por lotes, con n (200 a 2.000) y cargos (3 a 12) variables, covariables mitad remuestreo perturbado de `datos/demo/rotacion.csv` y mitad cópula gaussiana, y δ borrado en el 20%. `nucleo/supervivencia.py`: el preprocesamiento único (`preprocesar`), la base B-spline, θ libre ↔ con restricciones y la lectura del CSV según el YAML del caso. Ver: `uv run python -m motor.supervivencia.simular --revisar datos/demo/rotacion.csv`.
- sáb 03:30 · A-B1, prior ajustado con el predictivo a priori y escrito en `motor/artefactos/supervivencia/config.json`: β0 ~ Normal(−3,5; 1) (el plan decía −2,5), μ_c ~ Normal(2,0; 0,4) (decía log 6; 0,5) y s_c ~ HalfNormal(0,7) (decía 1). El resto, como en 11.2.
- sáb 03:32 · **A-B2 terminada.** `motor/supervivencia/red.py` (codificador jerárquico filas → cargo → dataset y `FlujoCondicional` sobre los 32 parámetros), `entrenar.py`, `validar.py` (SBC y cobertura) y `exportar.py`. El codificador sin entrenar exporta a ONNX con n variable y el flujo en NumPy da lo mismo que `torch`. Ver: `uv run pytest motor/supervivencia -q` (9 pruebas) y `uv run python -m motor.supervivencia.exportar --prueba`.
- sáb 03:53 · **A-B3 terminada.** Prueba de humo de 3 minutos, SBC chico de 200 datasets y `uv run python -m motor.supervivencia.medir`. Números abajo. Con la primera red, a los 11 minutos el posterior de β, λ y las cargas de las encuestas no se movía del prior (contracción cerca de 0): se agregó al codificador un atajo de segundo orden (promedio y covarianza de las 11 columnas, directo a rho) y con 3 minutos la contracción de β pasó a 0,80.
- sáb 04:00 · **A-B4, lo de PC 2, terminado.** Todo subido. Lanzamiento ensayado desde un clon limpio del repositorio oficial (sincronizar, entrenar, punto de guardado, retomar, SBC, pruebas) y, en este clon, parada con Ctrl-C («parada pedida» guarda), retomar y `exportar` desde el punto de guardado. Falta que la persona de PC 3 lo lance (sección de abajo).
- sáb 04:00 · Decisiones de la sesión B, para revisar: (1) el simulador está en NumPy y no en `torch` (`STACK.md` 3.6 decía `torch`); (2) el preprocesamiento de `supervivencia` vive en `nucleo/supervivencia.py` y no en `nucleo/preproceso.py`, que es de la sesión A; (3) cada lote de entrenamiento comparte un n, sorteado log-uniforme entre 200 y 2.000; (4) de filas a cargo se agrega con promedio, y con atención de filas a dataset y de cargos a dataset; (5) el atajo de segundo orden es un resumen escrito a mano que se suma al aprendido (`STACK.md` 3.5 descartaba usar solo resúmenes a mano); (6) «riesgo» = probabilidad de que la persona ya haya renunciado: el punto donde se cambia es la constante `RIESGO` de `nucleo/supervivencia.py`, con su comentario. El paso local por cuadratura y el modelo en NumPyro no existen todavía (A-N2).
- sáb 03:36 · **A-02 terminada.** `nucleo/preproceso.py` (`canales_terreno`: la misma función para el simulador en `torch` y el servicio en NumPy) y `motor/espacial/simular.py` (campo por Fourier, río como curva cúbica al azar, tendencia, mediciones). Ver: `uv run pytest motor/espacial/prueba_simular.py -q` (6 pruebas: preprocesamiento idéntico en NumPy y `torch`; covarianza del campo contra el método directo).
- sáb 03:37 · **A-03 terminada.** `motor/espacial/red.py` (codificador convolucional con saltos, cabeza de mapa, cabeza de flujo con el gradiente cortado) y `exportar.py`. Ver: `uv run pytest motor/espacial/prueba_red.py -q` (la pérdida de mapa y su gradiente son idénticos con y sin la cabeza de flujo) y `uv run python -m motor.espacial.exportar --prueba` (red sin entrenar a ONNX, comparada con `onnxruntime`).
- sáb 03:50 · **A-04 terminada: `espacial` entrenando en PC 2**, con la red de **tres canales**. Prueba de humo de 3 min (1.391 pasos, sin valores no numéricos, tres puntos de guardado), SBC chico de 200 terrenos, retomar y detener con señal probados, predictivo a priori mirado contra `datos/demo/terreno.csv`. Primer punto de guardado de la corrida larga a las 04:00. Comando y cómo retomar: tabla «Entrenamiento en curso».
- sáb 04:02 · Código de A-04: `motor/espacial/entrenar.py`, `validar.py` (SBC y cobertura), `medir.py`, `predictivo.py` (prior contra el archivo real) y `piso_kriging.py` (piso de la pérdida de mapa con kriging exacto). Todas las pruebas: `uv run pytest motor nucleo -q --ignore=motor/supervivencia` (24 pasan, 22 s).
- sáb 04:40 · **A-N1 terminada.** `nucleo/decision.py` (los 45 casos de `decision_prueba.json` pasan), `nucleo/casos.py` y `nucleo/api.py` (`casos`, `analizar` que elige `red` o `mcmc` por `KRYLOV_MOTOR_<ID>`, `cartera`, `donde_medir`, `nube`, `sello`). Ver: `uv run pytest nucleo/prueba_decision.py nucleo/prueba_api.py -q` (8 pasan). Pendiente de cada motor: su `analizar`.

## Decisiones de la sesión A que se apartan del texto del plan (para PC 3 y para el README técnico)

- **Toro de 128 y no «el doble de la grilla»** para el campo por Fourier: con 64 el error de covarianza llegaba a 0,11 (y a 0,21 en la esquina del prior); con 128, mediana 0,000, percentil 95 0,0005 y máximo 0,016 sobre 200 sorteos del prior.
- **Dirección y razón de anisotropía juntas:** e = log r · (cos 2φ, sin 2φ), dos números sin restricciones; el alcance a es el medio geométrico (a·√r a lo largo de φ, a/√r en la perpendicular). Siguen siendo 7 parámetros. El MCMC de referencia (A-N3) tiene que usar la misma parametrización y el mismo prior (`motor/espacial/simular.py`, `Prior`).
- **Terrenos sin tendencia (20%):** el canal va en cero y la tendencia no entra al campo, pero β1 se sortea igual del prior (no se fija en 0): sin datos sobre β1 su posterior es el prior, y así el flujo no persigue una masa puntual.
- **θ en las unidades estandarizadas de los datos:** el flujo aprende θ' = (log a, e1, e2, log(σ/esc), log(τ/esc), (β0 − media)/esc, β1/esc), con `media` y `esc` las de `preproceso`. Para volver a las unidades del caso se deshace con esos dos números.
- **Tercer diseño de mediciones:** además de al azar y agrupadas, una franja junto al río (el terreno real ocupa 341 de los 1.024 bloques, pegado al río).
- **Prior de la tendencia ensanchado** (β1 ~ Normal(0, 4) truncada): con desviación 3 la correlación del archivo real entre zinc y √dist (−0,80) caía en el percentil 1,8 de lo simulado; ahora cae en el 4,7.
- **Red más angosta que la primera versión:** anchos (32, 64, 128), 1,96 millones de parámetros, lote 64, tasa 5e-4 en coseno hasta las 08:30. Rinde más terrenos por noche y aliviana «¿Dónde mido?».
- **Se lanzó a las 03:50 y no a las 05:05**, porque todo lo mínimo estaba listo; el comando termina solo a las 08:30.
- **`git pull --rebase --autostash`** en este computador: dos sesiones comparten el clon y `pull --rebase` falla si la otra tiene cambios sin commit. El autostash los guarda y los repone intactos (comprobado con `md5`).

## Reparto de sesiones en PC 2

Un dueño por motor. Antes de tomar un motor sin dueño, anótate aquí y súbelo; nadie edita los archivos de otro.

| Qué | Archivos | Sesión | Desde |
|---|---|---|---|
| Lo compartido y `api.py` | `pyproject.toml`, `motor/comun/`, `nucleo/flujo.py`, `nucleo/preproceso.py`, `nucleo/decision.py`, `nucleo/api.py`, `nucleo/nube.py` | A | sáb 03:24 |
| `espacial` | `motor/espacial/`, `nucleo/espacial.py` | A | sáb 03:24 |
| `supervivencia` | `motor/supervivencia/`, `nucleo/supervivencia.py` | B | sáb 03:24 |
| `jerarquico` | `motor/jerarquico/`, `nucleo/jerarquico.py` | sin dueño | — |
| `estados` | `motor/estados/`, `nucleo/estados.py` | sin dueño | — |

Cada motor expone en su módulo de `nucleo/` una función `analizar(caso, transformaciones, costos)` que devuelve el diccionario de `contratos/CONTRATO.md`; `nucleo/api.py` (sesión A) la llama. `estado/amortizacion.md` lo editan todas las sesiones: cambios chicos, `git pull --rebase --autostash` justo antes, y commit de inmediato.

## En curso

- sáb 04:00 · Sesión B: A-B1 a A-B4 hechas en lo que toca a PC 2. Falta que PC 3 lance `supervivencia` (04:55). No se corre nada pesado de `supervivencia` en PC 2: `espacial` entrena aquí desde las 03:50. Sigue A-N2 (paso local y NumPyro) con la lista nocturna.
- sáb 04:02 · Sesión A: A-01 a A-04 hechas; `espacial` entrena hasta las 08:30. Sigue A-05 (dejar la lista nocturna) cuando la persona lo diga. No verificado todavía: que `supervivencia` esté corriendo en PC 3 (es de la sesión B y de PC 3).

## Lanzar `supervivencia` en PC 3 (sesión B → la persona de PC 3)

Todo lo que hace falta está versionado: no se necesita ningún archivo de PC 2 ni `datos_crudos/`. Ensayado desde un clon limpio en PC 2 (M4); **en el M3 no está verificado**.

1. Preparar: `git pull` y `uv sync --group entrenar`. Enchufado, tapa abierta, nada más entrenando en ese computador.
2. Prueba de humo, 3 minutos y medio en total:
   - `uv run python -m motor.supervivencia.entrenar --minutos 3 --nuevo`
   - `uv run python -m motor.supervivencia.validar --sbc 200`
   - Está bien si termina con `[punto de guardado · fin del presupuesto]`, la `media_movil` de la pérdida baja (en PC 2: de 37 a 11 en 3 minutos) y el SBC imprime su tabla sin error. No tiene que salir calibrado todavía.
3. **Corrida larga, comando exacto**, en una terminal que no se cierre:
   - `caffeinate -dims uv run python -m motor.supervivencia.entrenar --dispositivo cpu --hasta 08:30 --guardar-cada-min 10`
   - Parte desde el punto de guardado de la prueba de humo: es lo esperado, no se pierde nada. Dispositivo `cpu`: en PC 2 el procesador rindió 2,8 veces lo de la GPU del Mac (si se quiere medir en el M3, un minuto: `uv run python -m motor.supervivencia.medir`).
4. **Si se cae, se cierra la terminal o se reinicia el computador: el mismo comando del paso 3.** Retoma solo desde `motor/checkpoints/supervivencia/ultimo.pt` (un solo archivo, se reescribe cada 10 minutos de forma atómica; lleva pesos, optimizador, pasos y el conteo de datasets simulados). La primera línea tiene que decir `[retomar] … paso N`. Nunca agregar `--nuevo` al retomar: borra el avance.
5. Mirar cómo va, sin tocar el proceso: `tail -n 1 motor/checkpoints/supervivencia/registro.jsonl` (paso, datasets, pérdida, pasos por segundo).
6. Detener a las 08:30 si sigue corriendo: Ctrl-C una sola vez; guarda y sale (`[punto de guardado · parada pedida]`).
7. Entregar el punto de guardado (los de `motor/checkpoints/` no se versionan): `uv run python -m motor.supervivencia.exportar` escribe `codificador.onnx`, `codificador.onnx.data`, `flujo.npz` y `pesos.pt` en `motor/artefactos/supervivencia/`; después `git add motor/artefactos/supervivencia && git commit -m "supervivencia: red de la noche" && git pull --rebase && git push`.
8. Anotar en `estado/seguimiento.md`: comando, hora de inicio, carpeta `motor/checkpoints/supervivencia/` y que se retoma con el mismo comando.

## Interfaz de lo compartido (sesión A → sesión B y PC 3)

Cambios de interfaz se anotan aquí, con hora.

- sáb 03:31 · `motor.comun.codificador`: `PoolingAtencion(dim, cabezas=4)` y `PoolingPromedio(dim)`, las dos con `forward(h, mascara)` sobre `h` (..., n, dim) y `mascara` (..., n) en `float32` (1 = fila real); aceptan ejes delanteros, así que sirven para filas → grupo → dataset; atributo `dim_salida`; un conjunto vacío da ceros, no NaN. `CodificadorConjunto(dim_fila, dim_oculta=128, dim_resumen=128, pooling="atencion")` con `forward(x, mascara)` → (B, dim_resumen). `exportar_onnx(modulo, ejemplo, ruta, nombres_entrada, ejes_dinamicos, nombres_salida=("resumen",))` y `comparar_con_onnxruntime(modulo, ruta, entradas)` → máxima diferencia absoluta. `ejes_dinamicos` va por nombre de argumento de `forward`: `{"x": {0: "lote", 1: "n"}, "mascara": {0: "lote", 1: "n"}}`; exportar con un ejemplo de lote 2 o más.
- sáb 03:31 · **Ojo al exportar:** el exportador nuevo borra del grafo las sumas con constantes muy chicas (`x + 1e-8` desaparece; con `1e-6` no). Un `+ eps` no protege una división en ONNX: usar `clamp(min=…)` y probar el caso degenerado en `onnxruntime`.
- sáb 03:31 · `motor.comun.flujo.FlujoCondicional(dim_theta, dim_contexto=128, capas=8, ocultas=(128, 128))`: `fijar_escala(theta_del_prior)` una vez antes de entrenar (estandariza θ); `log_prob(theta, contexto)` (la pérdida NPE es `-log_prob(...).mean()`); `muestrear(contexto, m)` → (m, ..., d); `muestrear_con_ruido(contexto, ruido)`; `exportar_npz(ruta, **extra)`. θ entra en espacio sin restricciones; la transformación la hace cada motor.
- sáb 03:31 · `nucleo.flujo`: `cargar(ruta)`, `ruido(semilla, m, dim_theta)`, `muestrear(flujo, contexto, ruido)` → mismas muestras que `torch`. Solo NumPy.
- sáb 03:31 · `motor.comun.entrenar.entrenar(modulo, perdida_de_lote, datasets_por_paso, carpeta, minutos=… | hasta="HH:MM", guardar_cada_min=10, tasa=1e-3, retomar=True, config=…)`: `perdida_de_lote()` simula un lote nuevo y devuelve `(pérdida, dict de partes)`. Escribe `carpeta/ultimo.pt` (atómico; también al recibir Ctrl-C o `kill`) y `carpeta/registro.jsonl`; cuenta `datasets_simulados`; retoma solo si existe `ultimo.pt`. `elegir_dispositivo("cpu"|"mps"|"auto")`, `cargar_punto(ruta, modulo)`.
- sáb 04:02 · **Cambio en `motor.comun.entrenar.entrenar`:** nuevo argumento opcional `conservar_cada_min=30` (deja además copias numeradas `paso_0012345.pt`). No rompe llamadas existentes.
- sáb 04:02 · `nucleo.preproceso` (terreno): `canales_terreno(suma, cuenta, raiz_dist)` → `((valor, marca, raiz_dist), media, escala)`, con NumPy o con `torch`; `preparar_terreno(x, y, valor, transformacion, grilla)` para datos reales. `VERSION = "espacial-1"`.
- sáb 04:40 · **`nucleo/api.py` → cada motor.** `api.analizar(caso, transformaciones, costos, mediciones)` carga el YAML y llama a `nucleo.<motor_id>.analizar(caso, transformaciones, costos)`: `caso` es **el diccionario del YAML** (no el nombre), `transformaciones` una lista de textos y `costos` números ya resueltos, `{"falso_si": 1500.0, "falso_no": 6000.0}`. Solo `espacial` recibe además `mediciones=`. El motor devuelve lo propio: `unidades` (o `mapa` y `costo_total`), `factores`, `columnas`, `examen`, `semaforo`, `registro`, `implementacion`, y si quiere `en_palabras` o `titular`. `api` agrega `caso`, `motor_id`, `precalculado`, `costos`, `punto_de_corte`, `resumen_colores`, `costo_de_no_saber` (suma de `duda`), `titular`, `rotulos`, `sintetico`, `origen_datos`, `tiempo_ms`. Con semáforo rojo el motor devuelve `unidades`, `mapa` y `factores` en `None`. Para la cartera: `nucleo.<motor_id>.cartera(caso)`; para la nube: `nube(caso, transformaciones)`.
- sáb 04:40 · `nucleo.decision`: `decidir_tabla(muestras_p, c_si, c_no)` con `muestras_p` (unidades, muestras) → `{"p", "estado", "duda"}` por unidad; `decidir_espacial(p, c_si, c_no)`; `resumen_colores(estado)`; `factor(nombre, etiqueta, muestras)` arma una fila de `factores` con su `certeza`. `nucleo.casos`: `cargar_caso(nombre)`, `implementacion(motor_id)`, `ErrorKrylov(frase, codigo)` (lánzala y `api` la convierte en `{"error", "codigo"}`), `RAIZ`, `ARTEFACTOS`.
- sáb 04:40 · **Para PC 1:** las funciones de `nucleo/api.py` nunca lanzan por un caso o un motor que falta: devuelven `{"error": frase, "codigo": ...}`. Hoy `casos()` ya responde de verdad; `analizar` devuelve `no_disponible` hasta que cada motor entregue.
- sáb 03:31 · Pruebas: los archivos se llaman `prueba_*.py` o `test_*.py`, y `pytest` los busca en `nucleo/` y `motor/`.

## Elecciones de `STACK.md` (A-01)

- Entorno: `uv` 0.13.8 con Python 3.12.16 (lo instaló `uv`). Versiones que resolvió: `torch` 2.15.0 (GPU del Mac disponible), `zuko` 1.6.0, `numpy` 2.5.5, `onnx` 1.23.2, `onnxscript` 0.7.2, `onnxruntime` 1.32.0, `numpyro` 0.22.0, `jax` 0.12.1.
- Framework: PyTorch. Flujo: acoplamiento afín con `zuko.flows.NICE` (8 capas, máscara alternada fija), muestreado en NumPy. Codificador de tablas: DeepSets con pooling de atención. MCMC: NumPyro. Dispositivo de `espacial`: **GPU del Mac** (medido en A-04: 7,6 veces el procesador).
- `numpy.show_config()` no nombra Accelerate en este entorno (BLAS «system», sin más detalle): **no verificado** qué BLAS usa.

## Bloqueos

- (ninguno) · sáb 04:07: resuelto lo de la batería; PC 2 está enchufado y cargando (`pmset -g batt`: AC Power).

## Pedidos a otros

- sáb 04:00 · Sesión B → PC 3: lanzar `supervivencia` a las 04:55 con la sección «Lanzar `supervivencia` en PC 3» de este archivo, y a las 08:30 exportar y subir (paso 7).
- sáb 04:00 · Sesión B → sesión A, sin urgencia: `exportar_onnx` deja dos archivos, `codificador.onnx` y `codificador.onnx.data` (los pesos van aparte). El servicio y git necesitan los dos, o se exporta con los pesos dentro. PC 1 tiene que saberlo antes de A-10.
- sáb 04:00 · Sesión B → sesión A, sin urgencia: si se quiere que `nucleo/preproceso.py` sea el único lugar, basta reexportar ahí `nucleo.supervivencia.preprocesar`.

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Motor y computador | `espacial`, en PC 2 (MacBook Air M4). Tres canales, anchos (32, 64, 128), lote 64 |
| Comando exacto | `nohup perl -MPOSIX -e 'setsid(); exec @ARGV' -- caffeinate -dims uv run python -m motor.espacial.entrenar --dispositivo mps --hasta 08:30 --guardar-cada-min 10 >> motor/checkpoints/espacial/salida.log 2>&1 &` (desde la raíz del repositorio; el `perl … setsid` solo lo desprende de la terminal) |
| Hora de inicio | sáb 03:50. Termina solo a las 08:30 y deja el último punto de guardado |
| Cómo se mira | `tail -f motor/checkpoints/espacial/salida.log` (una línea cada 100 pasos) · `pgrep -fl motor.espacial.entrenar` · `pmset -g assertions \| grep caffeinate` |
| Dónde quedan los puntos de guardado | `motor/checkpoints/espacial/ultimo.pt` cada 10 min (escritura atómica) y una copia numerada `paso_*.pt` cada 30 min; bitácora en `registro.jsonl`. Primer punto: 04:00, paso 4.436, 283.904 terrenos |
| Cómo retomar si se cae | **El mismo comando.** Si existe `ultimo.pt`, sigue desde ahí (pesos, optimizador, conteo de terrenos); probado en la prueba de humo. Si `ultimo.pt` estuviera dañado: copiar encima el `paso_*.pt` más reciente. `--nuevo` parte de cero |
| Cómo detenerlo antes | `pkill -INT -f "python -m motor.espacial.entrenar"`: termina el paso, guarda y sale (probado) |
| Validar sin detenerlo | `uv run python -m motor.espacial.validar --sbc 200` y `uv run python -m motor.espacial.piso_kriging` (corren en el procesador, menos de un minuto cada uno) |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Simular un conjunto de 150 puntos sueltos, 1 proceso | 0,33 ms | NumPy con Accelerate, M4 16 GB, lote de 64 | sáb 00:24 |
| Simular un conjunto de 300 puntos sueltos, 1 proceso | 1,15 ms | ídem | sáb 00:24 |
| Flujo: máxima diferencia NumPy contra `torch`, mismos pesos y mismo ruido | 9,5e-6 (7 parámetros) y 5,7e-6 (32), con muestras de hasta 26 en valor absoluto | `motor/comun/prueba_flujo.py`, 32 muestras × 5 datasets, pesos perturbados | sáb 03:31 |
| Codificador de conjuntos: máxima diferencia `onnxruntime` contra `torch` | 6,0e-8 (lote 1, n 50), 1,2e-7 (lote 3, n 300), 9,7e-8 (lote 2, n 1.470) | `motor/comun/prueba_codificador.py`, sin entrenar, exportado con n 64 | sáb 03:31 |
| Terrenos simulados por segundo en grilla de 32×32 (solo el simulador) | 2.138 en procesador, 5.353 con el campo en la GPU del Mac | `uv run python -m motor.espacial.medir --que simulador`, lote 128, toro de 128 | sáb 03:41 |
| Campo por Fourier contra el método directo | Error máximo de covarianza: mediana 0,000, p95 0,0005, máximo 0,016 (200 sorteos del prior, toro 128) | covarianza implícita del espectro contra exp(−h) directa, todos los desfases hasta 31 | sáb 03:35 |
| `espacial` sin entrenar: `onnxruntime` contra `torch` | 3,2e-6 (lote 1), 2,8e-5 (lote 480); flujo NumPy contra `torch` 9,5e-7 | `uv run python -m motor.espacial.exportar --prueba` | sáb 03:37 |
| Pasos de entrenamiento por segundo, CPU | 0,38 (lote 128, anchos 48-96-192) | `motor.espacial.medir --que entrenar --dispositivo cpu`, 30 pasos | sáb 03:41 |
| Pasos de entrenamiento por segundo, GPU del Mac | 2,89 con la misma red y lote (7,6 veces el procesador). Con la red elegida (32-64-128, lote 64): 7,4 de promedio en los primeros 10 min de la corrida real, unos 475 terrenos/s | `medir` y `registro.jsonl` de la corrida. La sesión B usó el computador a ratos: **no verificado** cuánto baja por eso | sáb 04:00 |
| Caída sostenida por temperatura | Sin caída visible en 10 min: entre 6,6 y 8,6 pasos/s por tramos de 800 pasos, sin tendencia a la baja. **No se hizo** la corrida aparte de 2 min; se lee de `registro.jsonl` | `registro.jsonl` de la corrida real | sáb 04:00 |
| Dispositivo elegido | GPU del Mac (`mps`) para `espacial` | 7,6 veces el procesador, sin avisos de operaciones que caigan al procesador | sáb 03:41 |
| Terrenos simulados usados en el entrenamiento | 283.904 a los 10 min. Estimación, no medida: unos 8 millones a las 08:30 si se sostienen 475/s | lo cuenta el bucle en cada punto de guardado | sáb 04:00 |
| Prueba de humo de `espacial` (3 min, tres canales) | 1.391 pasos, 89.024 terrenos; pérdida NPE de 5,23 a 3,62; pérdida de mapa de 1,02 a 0,93; sin pasos saltados | `entrenar --minutos 3` | sáb 03:47 |
| SBC chico a los 10 min de la corrida real (200 terrenos nuevos, 99 muestras) | Cobertura del 90%: 0,88 en promedio sobre los 7 parámetros (de 0,835 a 0,925); 4 de 7 pasan el χ² de uniformidad; `log_tau`, `beta0` y `beta1` con sesgo todavía (z medio de −0,37 a 0,47). Cabeza de mapa en bloques sin medición: cobertura 0,90, RECM 0,71. **No pasa aún, y no tenía que pasar: corre y mejoró** respecto de los 3 min (contracción de `log_alcance` 0,21 → 0,33; `log_tau` 0,27 → 0,53) | `uv run python -m motor.espacial.validar --sbc 200` | sáb 04:01 |
| Pérdida de mapa contra su piso (kriging exacto con θ verdadero, 60 terrenos) | Trivial 1,416 · red a los 10 min 0,872 · piso 0,766: la red cerró el 84% del camino. RECM en bloques sin medir: 1,007 · 0,709 · 0,671 | `uv run python -m motor.espacial.piso_kriging` | sáb 04:01 |
| Predictivo a priori contra el terreno real | 135 bloques medidos (percentil 57 de lo simulado), correlación con √dist −0,805 (percentil 4,7), semivarianza entre vecinos 0,354 (percentil 63), 117 pares de vecinos (percentil 75) | `uv run python -m motor.espacial.predictivo`, 4.000 terrenos simulados | sáb 03:49 |
| Sello de `espacial` | sin medir | `validar-motor` | — |
| «¿Dónde mido?»: análisis rehechos y segundos, con la red | sin medir | A-11 | — |
| «¿Dónde mido?»: los mismos análisis con el MCMC de referencia | sin medir | A-12 | — |
| Cartera: análisis y segundos | sin medir | A-12 | — |
| `supervivencia` · predictivo a priori contra el archivo real (1.470 personas) | Tasa de renuncia real 0,156: percentil 30 de lo simulado (5% a 95%: 0,03 a 0,94). Mediana de años real 5: percentil 51 (1 a 11). Máximo real 40: percentil 67 | `motor.supervivencia.simular --revisar datos/demo/rotacion.csv`, 2.000 datasets simulados | sáb 03:30 |
| `supervivencia` · simulador | 2.639 datasets por segundo (lote 32, n entre 200 y 2.000) | `motor.supervivencia.medir`, M4, 1 proceso, nada entrenando | sáb 03:37 |
| `supervivencia` · pasos de entrenamiento por segundo, CPU | 38,1 (lote 32) = 1.219 datasets/s; 20,3 (lote 64) = 1.300 datasets/s | ídem, 200 pasos tras 20 de calentamiento, 4 hilos. **Medido con la red anterior al atajo de segundo orden; con la red final, sin carga, no verificado** | sáb 03:37 |
| `supervivencia` · pasos de entrenamiento por segundo, GPU del Mac | 13,7 (lote 32) = 437 datasets/s; 9,9 (lote 64) = 631 datasets/s | ídem, con `torch.mps.synchronize()` | sáb 03:37 |
| `supervivencia` · dispositivo elegido | `cpu` (2,8 veces la GPU del Mac con lote 32) | las dos filas anteriores | sáb 03:37 |
| `supervivencia` · caída sostenida por temperatura | Sin caída en 3 minutos: 37,9 pasos/s los primeros 30 s y 39,6 los últimos 30 s. Más de 3 minutos, no verificado | `registro.jsonl` de la prueba de humo, red anterior al atajo | sáb 03:36 |
| `supervivencia` · prueba de humo, red final | Pérdida NPE (media móvil) de 37 a 11 en 3 minutos y a 4,5 a los 6,8 minutos (243.808 datasets). Corrió con `espacial` entrenando al lado: 17 a 25 pasos/s | `motor.supervivencia.entrenar`, lote 32 | sáb 03:58 |
| `supervivencia` · SBC chico, red final a los 6,8 minutos | Cobertura del intervalo de 90%: 0,897 (peor grupo, n sobre 600: 0,893). Contracción media del posterior 0,56 (β 0,82; λ 0,86; cargas de las encuestas 0,78). **Todavía no calibra:** 8 de 32 parámetros con KS sobre el límite de 0,096 | `motor.supervivencia.validar --sbc 200`, 200 muestras por dataset | sáb 03:58 |
| `supervivencia` · SBC chico, red anterior (sin atajo) a los 11 minutos | Cobertura 0,899; contracción media 0,35, y cerca de 0 en β, λ y las cargas de las encuestas | ídem, 679.936 datasets | sáb 03:46 |
| `supervivencia` · exportación | `onnxruntime` contra `torch`: hasta 2,3e-6 (n de 200, 1.470 y 2.000). Flujo en NumPy contra `torch`: 3,8e-6 | `motor.supervivencia.exportar` sobre el punto de guardado de 6,8 minutos | sáb 03:58 |
| `supervivencia` · datasets que verá la red en su turno en PC 3 | Sin medir. A 1.219 por segundo serían unos 15 millones en 3,5 horas; la cifra real la cuenta el punto de guardado | estimación desde la medición en PC 2 | — |
