# Krylov · README técnico (borrador)

> Borrador de la tarea A-18, escrito por `amortizacion` (PC 2) el sábado 21-nov a las 06:30. Aquí van los nombres técnicos precisos; la pantalla y el pitch usan `GLOSARIO.md`. **No trae resultados de validación:** a esta hora ninguna red está validada. Cada cifra de este archivo está medida y anotada en `estado/amortizacion.md` («Números medidos»); lo que falta dice «pendiente» y se llena desde `motor/artefactos/<motor>/sello.json`.

## 1. Qué es

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**. Para cada familia de archivos hay un **motor** con cinco piezas:

| Pieza | Qué es | Dónde está |
|---|---|---|
| Modelo generativo | Un modelo bayesiano explícito del dataset completo: **prior** sobre los parámetros globales θ → efectos por grupo → latentes por unidad → datos observados, incluidas la censura y las respuestas que faltan | Encabezado de `nucleo/<motor>.py`; ecuaciones en `WORKPLAN.md`, sección 11 |
| Simulador | Ese modelo, vectorizado: genera lotes de datasets completos al vuelo, con tamaño variable | `motor/<motor>/simular.py` |
| Red (NPE) | Un codificador resume el dataset entero en s(D) (128 números) y un **flujo normalizador** condicional entrega el **posterior** amortizado q(θ \| s(D)). Se entrena solo con simulaciones (estimación neuronal del posterior, **NPE**) | `motor/<motor>/red.py`, `motor/comun/` |
| Paso local exacto | Dado cada θ muestreado, lo que falta saber de una unidad es de baja dimensión y se integra de forma exacta en NumPy: cuadratura, filtro forward o kriging | `nucleo/<motor>.py` |
| MCMC de referencia | NUTS (NumPyro) sobre el mismo modelo y el mismo prior. Valida la red, da la cifra de amortización y es el plan B de la tarjeta, precalculado | `motor/<motor>/mcmc.py` |

Amortizar es pagar el costo de la inferencia una vez, al entrenar: después, el posterior de un dataset nuevo de la misma familia es una pasada de la red y un muestreo del flujo.

Después del posterior viene la **decisión** (`nucleo/decision.py`): con los dos costos del caso, cada unidad queda en «conviene actuar», «no hace falta» o «en duda», y «lo que cuesta no saber» es el valor esperado de la información perfecta sobre θ.

## 2. Los cuatro motores

| Motor | Caso | Modelo generativo | θ | Latentes que se integran | Paso local |
|---|---|---|---|---|---|
| `supervivencia` | Rotación | Tiempo hasta la renuncia Weibull con censura por intervalos de un año y modelo propio de la censura; B-spline cúbico del log del sueldo con prior de suavidad; efecto aleatorio por cargo; compromiso latente por persona que genera cuatro encuestas ordinales (logit ordenado) | 32 | Efecto del cargo y compromiso de cada persona | Cuadratura anidada cargo → persona (**en construcción**, tarea A-N2) |
| `jerarquico` | Inasistencias | Regresión logística jerárquica: propensión latente por paciente y efecto por barrio; B-spline de log(1 + espera) con un salto en «mismo día»; el efecto del SMS cambia con la espera; se modela la asignación del SMS | 20 | Efecto del barrio y propensión del paciente | Cuadratura de Gauss-Hermite anidada, adaptativa en el nivel del barrio |
| `estados` | Crédito | Cadena de Markov oculta de tres estados por cliente; seis meses de emisiones (atraso en logit ordenado de 5 niveles, uso del cupo normal, pago con masa en cero); transiciones que dependen de cupo, edad y educación; impago según el estado del mes siguiente | 33 | La cadena de estados de cada cliente | Filtro forward |
| `espacial` | Terreno | Proceso gaussiano con covarianza exponencial y anisotropía geométrica, tendencia en √(distancia al río) y error de medición | 7 | El campo en los bloques sin medir | Kriging dado θ (gaussiano, en forma cerrada) |

**Priors.** En `jerarquico` y `estados` el prior es una normal independiente por parámetro en el espacio sin restricciones (logaritmos, logits, incrementos positivos), definida una sola vez en `simular.py` (`PRIOR`, `MEDIAS`, `DESVS`) y leída desde ahí por el MCMC. En `estados` el intercambio de etiquetas entre estados se rompe en el prior: la posición del atraso y la probabilidad de impago van ordenadas por construcción (incrementos positivos). En `espacial` son normales truncadas (`motor/espacial/simular.py`, `Prior`). En `supervivencia`, `motor/artefactos/supervivencia/config.json`. Cada prior se ajustó mirando el **predictivo a priori** contra el archivo real (`python -m motor.<motor>.simular --revisar`): los resúmenes del archivo tienen que caer dentro de lo simulado.

**Covariables.** El simulador las genera mitad por remuestreo perturbado de filas del archivo del caso y mitad con un generador paramétrico. La red generaliza hasta donde llega ese generador; va en `limitaciones` de cada sello.

**Lo que se apartó del plan escrito** (con su motivo en `estado/amortizacion.md`): `jerarquico` tiene 20 parámetros y no 22 (el primer coeficiente del spline va fijo: con el intercepto quedaba una dirección sin identificar); `estados` tiene 33 y no 35 (el archivo no registra el código de atraso 1 en cinco de los seis meses, así que 1 y 2 van juntos); en `espacial` la dirección y la razón de anisotropía se parametrizan juntas, e = log r·(cos 2φ, sin 2φ), y el campo se simula por transformada de Fourier sobre un toro de 128.

## 3. La red

- **Codificador del dataset** (`motor/comun/codificador.py`). DeepSets con pooling de atención y máscara de relleno: invariante al orden de las filas y con n variable. Sigue la jerarquía del modelo: filas → cargo → dataset en `supervivencia`; cita → paciente → barrio → dataset en `jerarquico`; en `estados` cada fila es el historial aplanado de un cliente. Las filas por decidir entran con la respuesta en cero y una marca. Los tres codificadores de tabla suman un atajo de segundo orden (promedio y covarianza de las columnas) y el tamaño del conjunto, que el pooling normalizado no ve.
- **`espacial`** (`motor/espacial/red.py`). Una red convolucional con saltos sobre la grilla de 32 × 32 con tres canales (valor estandarizado, marca de medición, √dist). Dos cabezas: la **cabeza de mapa** da media y desviación por bloque (el predictivo posterior marginal, amortizado) y la **cabeza de flujo** da q(θ | D). La de flujo recibe las características con el gradiente cortado, así la de mapa entrena igual que si estuviera sola (`motor/espacial/prueba_red.py` compara los gradientes).
- **Posterior** (`motor/comun/flujo.py`). Flujo normalizador condicional de acoplamiento afín (`zuko.flows.NICE`, 8 capas, máscara alternada), sobre θ estandarizado en espacio sin restricciones. **Pérdida NPE:** −log q(θ | s(D)), promediada sobre datasets simulados.
- **Servicio sin `torch`.** A ONNX se exporta solo el codificador (ejes dinámicos para n); el flujo se guarda en `flujo.npz` y se muestrea en NumPy (`nucleo/flujo.py`). Una prueba exige la misma muestra con los mismos pesos y el mismo ruido: la diferencia máxima medida fue 9,5e-6 (`motor/comun/prueba_flujo.py`). `nucleo/` no importa `torch`, `zuko`, `jax` ni `numpyro`, y una prueba lo comprueba.
- **Un solo preprocesamiento por motor**, en `nucleo/`: la misma función prepara los datasets simulados y el archivo real (`armar_filas`, `matriz_de_diseno`, `canales_terreno`, `preprocesar`).

## 4. Cómo se entrena

```bash
uv sync --group entrenar
uv run python -m motor.<motor>.entrenar --minutos 3 --nuevo            # prueba de humo
uv run python -m motor.<motor>.validar --sbc 200                       # SBC chico: tiene que correr, no pasar
caffeinate -dims uv run python -m motor.<motor>.entrenar --dispositivo cpu --hasta HH:MM --guardar-cada-min 10
```

- Los datasets se simulan al vuelo en cada paso: la red nunca ve dos veces el mismo, y el bucle (`motor/comun/entrenar.py`) cuenta cuántos vio. Esa cuenta es la cifra «practicó con N simulaciones».
- Punto de guardado atómico cada 10 minutos (`motor/checkpoints/<motor>/ultimo.pt`: pesos, optimizador, pasos y conteo); el mismo comando retoma. Los puntos de guardado no se versionan.
- Dispositivo por motor, medido con `python -m motor.<motor>.medir`: `espacial` en la GPU del Mac (7,6 veces el procesador); `supervivencia` en el procesador (2,8 veces la GPU). `jerarquico` y `estados`: procesador, sin comparar todavía.
- Computadores: MacBook Air M4 de 16 GB (`espacial`, después `estados`) y MacBook Air M3 de 16 GB (`supervivencia`, después `jerarquico`). Un entrenamiento por computador.

| Motor | Datasets simulados | Minutos | Estado |
|---|---|---|---|
| `espacial` | pendiente (lo cuenta el último punto de guardado) | pendiente | entrenando desde el sáb 03:50 |
| `supervivencia` | pendiente | pendiente | entrenando en PC 3 desde el sáb 04:05 |
| `jerarquico` | pendiente | pendiente | listo para lanzar |
| `estados` | pendiente | pendiente | listo para lanzar |

## 5. Cómo se valida

Un comando por motor, sin nada entrenando en ese computador (`--ensayo` recorre todo en chico, para probar el programa):

```bash
uv run python -m motor.<motor>.sello        # espacial, estados, jerarquico (supervivencia: pendiente)
```

Escribe `motor/artefactos/<motor>/sello.json` (lo que muestra la app) y `validacion.json` (el detalle), y termina en PASA o NO PASA. Los chequeos:

1. **Exportación.** `onnxruntime` y el flujo en NumPy contra `torch`, con tamaños distintos de los del ejemplo de exportación.
2. **SBC y cobertura** en datasets simulados nuevos. SBC (calibración basada en simulación): para un dataset con θ verdadero se sacan L muestras de q(θ | D) y se cuenta cuántas quedan bajo el valor verdadero; si q está calibrado, ese rango es uniforme. Se informa por parámetro (χ² de uniformidad, rango medio, contracción respecto del prior) y la cobertura del intervalo de 90%, en total y por grupos (datasets chicos y grandes, pocos y muchos grupos). La cobertura se cuenta por rangos, que es exacta (`motor/comun/validacion.py`).
3. **Lo que se decide.** En los motores de tabla: la cobertura del rango de 90% de la probabilidad de cada unidad por decidir, contra la que da el paso local exacto con el θ verdadero. En `espacial`: la cobertura de la cabeza de mapa en los bloques sin medición.
4. **Contra el MCMC de referencia.** NUTS en 5 datasets simulados y en el archivo real: diferencia de medias del posterior en desviaciones estándar del posterior del MCMC, razón de anchos, r̂ y segundos por dataset. Las muestras del archivo real quedan en `mcmc/<caso>.npz`: son el plan B. En `espacial` la referencia marginaliza la estandarización de los datos (derivación en `motor/espacial/mcmc.py`).
5. **El método rápido de siempre** (`motor/comun/rapido.py`): regresión logística simple con las mismas columnas por fila que ve el codificador, sin estructura; en `espacial`, kriging con parámetros fijos. Se mide su cobertura en las mismas simulaciones y su resultado en el mismo examen.
6. **Examen con datos reales reservados.** En cada archivo se dejó vacía la respuesta del 20% de las filas; se compara lo dicho con lo que pasó, por tramos de probabilidad. En el terreno se esconde 20% de las mediciones, con cinco particiones.
7. **Modelo mal especificado: la nube** (`nucleo/nube.py`, `motor/<motor>/nube.py`). El predictivo a priori del modelo, al tamaño del archivo, con dos detectores: dos ejes con nombre (el AUC del mejor factor por sí solo y la proporción de «sí») y la distancia de Mahalanobis en el espacio de resúmenes s(D) contra su percentil 99.

**Un motor pasa** si el SBC no muestra sesgo, la cobertura de 90% queda entre 85% y 95% (y sobre 80% en el peor grupo), la diferencia con el MCMC es menor que 0,3 desviaciones estándar en las medias y un análisis tarda menos de 1 segundo. Una tarjeta solo dice que respondió la red si su motor pasó; si no, responde el posterior del MCMC precalculado, rotulado.

| Motor | SBC | Cobertura del 90% | Diferencia con el MCMC | Examen real | Responde |
|---|---|---|---|---|---|
| `espacial` | pendiente | pendiente | pendiente | pendiente | pendiente |
| `supervivencia` | pendiente | pendiente | pendiente | pendiente | pendiente |
| `jerarquico` | pendiente | pendiente | pendiente | pendiente | pendiente |
| `estados` | pendiente | pendiente | pendiente | pendiente | pendiente |

Medido hasta ahora, del método rápido solo (sáb 06:15): en el examen real de crédito, AUC 0,762 sobre 400 clientes reservados; en el de inasistencias, AUC 0,737 sobre 396 citas. La comparación con Krylov está pendiente de las redes.

## 6. Cómo reproducirlo

```bash
uv sync --group entrenar
uv run pytest nucleo motor -q                                  # una prueba por módulo
uv run python -m motor.<motor>.simular --revisar               # predictivo a priori contra el archivo del caso
uv run python -m motor.<motor>.exportar --prueba               # la red sin entrenar exporta y coincide con torch
uv run python -m motor.<motor>.entrenar --hasta HH:MM          # sección 4
uv run python -m motor.<motor>.sello                           # sección 5
```

Con los artefactos en `motor/artefactos/<motor>/`, el servicio responde por `nucleo/api.py` (`analizar`, `cartera`, `donde_medir`, `nube`, `sello`) con `KRYLOV_MOTOR_<MOTOR>=red`; con `mcmc` (el valor por defecto) responde el posterior precalculado. Las semillas de todo lo que se muestra son fijas.

Datos: `datos/demo/` trae rotación, crédito y terreno. El archivo de inasistencias no se versiona por su licencia (CC BY-NC-SA); `datos/preparar/inasistencias.py` lo genera idéntico. Sin él, `jerarquico` entrena solo con el generador paramétrico y su sello no corre.

## 7. Límites conocidos

- Cada motor responde una familia de archivos, dentro de los rangos de su simulador (por ejemplo, de 500 a 2.000 clientes en `estados`; de 1.000 a 3.000 citas en 10 a 40 barrios en `jerarquico`; grilla de 32 × 32 con 30 a 400 mediciones en `espacial`).
- En `estados` el uso del cupo se modela como normal por estado; el real tiene ceros y un grupo pegado al cupo.
- En `jerarquico` el SMS no es un experimento: se asigna solo con 3 o más días de espera, y el modelo lo sabe.
- El segundo detector de la nube usa un resumen aprendido: no garantiza que un archivo raro caiga fuera. El que sostiene el caso del archivo malo es el de los ejes con nombre.
- El paso local de `supervivencia` y su MCMC están en construcción a la hora de este borrador.
