# Estado · amortizacion (PC 2)

> **Hackathon:** el producto se termina el **sábado a las 18:00**; después solo se itera el demo y el pitch. Lo más simple que se vea bien.

Lo edita solo PC 2 (skill `actualizar-estado`). Líneas cortas, con hora de Santiago.
Persona: Rodrigo · Dueño de `nucleo/` y `motor/`. Instrucciones: `PC2_AMORTIZACION.md`.

## Hecho

- sáb 03:00 · Plan final recibido. Nada construido todavía.
- sáb 03:24 · Arranque de PC 2 (sesión A): clon con dos destinos de push y rol declarado. Primer commit propio; `git ls-remote` de los dos repositorios comparado.
- sáb 03:31 · **A-01 terminada.** `pyproject.toml` con el grupo `entrenar` y `uv.lock`; `motor/comun/` (`codificador.py`, `flujo.py`, `entrenar.py`) y `nucleo/flujo.py`. Ver: `uv sync --group entrenar && uv run pytest motor/comun -q` (15 pruebas pasan, 8 s).
- sáb 03:31 · A-01, las tres comprobaciones, corridas: (1) los pesos de `zuko.flows.NICE` se leen capa por capa (máscara alternada fija + MLP de tres lineales con ReLU; la escala es `e/(1+|e|/|ln 1e-3|)`): **se usa `zuko`**, sin acoplamiento propio. (2) `numpyro` 0.22.0 y `jax` 0.12.1 instalan en Python 3.12.16 y NUTS corre (300+300 pasos de un modelo de juguete en 1,4 s). (3) El pooling de atención con máscara exporta a ONNX con lote y n variables (exportador nuevo, `dynamo=True` con `dynamic_shapes`) y `onnxruntime` coincide con `torch`: **queda el pooling de atención**.

## En curso

- sáb 03:31 · Sesión A: A-02 (preprocesamiento y simulador de terrenos), para las 04:15. Sesión B: A-B1. Meta de la noche: a las 05:15, `espacial` entrenando en PC 2 y `supervivencia` en PC 3.

## Interfaz de lo compartido (sesión A → sesión B y PC 3)

Cambios de interfaz se anotan aquí, con hora.

- sáb 03:31 · `motor.comun.codificador`: `PoolingAtencion(dim, cabezas=4)` y `PoolingPromedio(dim)`, las dos con `forward(h, mascara)` sobre `h` (..., n, dim) y `mascara` (..., n) en `float32` (1 = fila real); aceptan ejes delanteros, así que sirven para filas → grupo → dataset; atributo `dim_salida`; un conjunto vacío da ceros, no NaN. `CodificadorConjunto(dim_fila, dim_oculta=128, dim_resumen=128, pooling="atencion")` con `forward(x, mascara)` → (B, dim_resumen). `exportar_onnx(modulo, ejemplo, ruta, nombres_entrada, ejes_dinamicos, nombres_salida=("resumen",))` y `comparar_con_onnxruntime(modulo, ruta, entradas)` → máxima diferencia absoluta. `ejes_dinamicos` va por nombre de argumento de `forward`: `{"x": {0: "lote", 1: "n"}, "mascara": {0: "lote", 1: "n"}}`; exportar con un ejemplo de lote 2 o más.
- sáb 03:31 · **Ojo al exportar:** el exportador nuevo borra del grafo las sumas con constantes muy chicas (`x + 1e-8` desaparece; con `1e-6` no). Un `+ eps` no protege una división en ONNX: usar `clamp(min=…)` y probar el caso degenerado en `onnxruntime`.
- sáb 03:31 · `motor.comun.flujo.FlujoCondicional(dim_theta, dim_contexto=128, capas=8, ocultas=(128, 128))`: `fijar_escala(theta_del_prior)` una vez antes de entrenar (estandariza θ); `log_prob(theta, contexto)` (la pérdida NPE es `-log_prob(...).mean()`); `muestrear(contexto, m)` → (m, ..., d); `muestrear_con_ruido(contexto, ruido)`; `exportar_npz(ruta, **extra)`. θ entra en espacio sin restricciones; la transformación la hace cada motor.
- sáb 03:31 · `nucleo.flujo`: `cargar(ruta)`, `ruido(semilla, m, dim_theta)`, `muestrear(flujo, contexto, ruido)` → mismas muestras que `torch`. Solo NumPy.
- sáb 03:31 · `motor.comun.entrenar.entrenar(modulo, perdida_de_lote, datasets_por_paso, carpeta, minutos=… | hasta="HH:MM", guardar_cada_min=10, tasa=1e-3, retomar=True, config=…)`: `perdida_de_lote()` simula un lote nuevo y devuelve `(pérdida, dict de partes)`. Escribe `carpeta/ultimo.pt` (atómico; también al recibir Ctrl-C o `kill`) y `carpeta/registro.jsonl`; cuenta `datasets_simulados`; retoma solo si existe `ultimo.pt`. `elegir_dispositivo("cpu"|"mps"|"auto")`, `cargar_punto(ruta, modulo)`.
- sáb 03:31 · Pruebas: los archivos se llaman `prueba_*.py` o `test_*.py`, y `pytest` los busca en `nucleo/` y `motor/`.

## Elecciones de `STACK.md` (A-01)

- Entorno: `uv` 0.13.8 con Python 3.12.16 (lo instaló `uv`). Versiones que resolvió: `torch` 2.15.0 (GPU del Mac disponible), `zuko` 1.6.0, `numpy` 2.5.5, `onnx` 1.23.2, `onnxscript` 0.7.2, `onnxruntime` 1.32.0, `numpyro` 0.22.0, `jax` 0.12.1.
- Framework: PyTorch. Flujo: acoplamiento afín con `zuko.flows.NICE` (8 capas, máscara alternada fija), muestreado en NumPy. Codificador de tablas: DeepSets con pooling de atención. MCMC: NumPyro. Dispositivo: sin decidir, se mide en A-04.
- `numpy.show_config()` no nombra Accelerate en este entorno (BLAS «system», sin más detalle): **no verificado** qué BLAS usa.

## Bloqueos

- (ninguno)

## Pedidos a otros

- (ninguno)

## Entrenamiento en curso

| Qué | Valor |
|---|---|
| Comando exacto | — |
| Hora de inicio | — |
| Dónde quedan los puntos de guardado | — |
| Cómo retomar si se cae | — |

## Números medidos

| Qué | Valor | Cómo se midió | Hora |
|---|---|---|---|
| Simular un conjunto de 150 puntos sueltos, 1 proceso | 0,33 ms | NumPy con Accelerate, M4 16 GB, lote de 64 | sáb 00:24 |
| Simular un conjunto de 300 puntos sueltos, 1 proceso | 1,15 ms | ídem | sáb 00:24 |
| Flujo: máxima diferencia NumPy contra `torch`, mismos pesos y mismo ruido | 9,5e-6 (7 parámetros) y 5,7e-6 (32), con muestras de hasta 26 en valor absoluto | `motor/comun/prueba_flujo.py`, 32 muestras × 5 datasets, pesos perturbados | sáb 03:31 |
| Codificador de conjuntos: máxima diferencia `onnxruntime` contra `torch` | 6,0e-8 (lote 1, n 50), 1,2e-7 (lote 3, n 300), 9,7e-8 (lote 2, n 1.470) | `motor/comun/prueba_codificador.py`, sin entrenar, exportado con n 64 | sáb 03:31 |
| Terrenos simulados por segundo en grilla de 32×32 | sin medir | A-02 | — |
| Pasos de entrenamiento por segundo, CPU | sin medir | `medir-rendimiento` | — |
| Pasos de entrenamiento por segundo, GPU del Mac | sin medir | `medir-rendimiento` | — |
| Caída sostenida por temperatura | sin medir | `medir-rendimiento` | — |
| Dispositivo elegido | sin decidir | `medir-rendimiento` | — |
| Terrenos simulados usados en el entrenamiento | sin medir | A-09 | — |
| Sello de `espacial` | sin medir | `validar-motor` | — |
| «¿Dónde mido?»: análisis rehechos y segundos, con la red | sin medir | A-11 | — |
| «¿Dónde mido?»: los mismos análisis con el MCMC de referencia | sin medir | A-12 | — |
| Cartera: análisis y segundos | sin medir | A-12 | — |
