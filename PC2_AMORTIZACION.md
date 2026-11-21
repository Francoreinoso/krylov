# PC 2 · Amortización de los modelos

> **Hackathon:** el producto se termina el **sábado a las 18:00**. Lo más simple que se vea bien, y que la simulación se vea en pantalla.
>
> **Pivote del sábado 12:10 (D-37): Krylov es el data scientist artificial de la minería.** Este archivo reemplaza tu lista anterior. **Lo primero: detener `estados`.** Ya no se usa.

Eres el agente de Claude Code del **PC 2**, el MacBook Air M4 de 16 GB sin ventilador. Tu rol es `amortizacion`. El contexto general está en `AGENTS.md`, que ya se cargó.

## Tu misión en una línea

Que las cinco decisiones de la mina respondan con inferencia basada en simulación amortizada de verdad: `leyes` con el motor `espacial` que ya pasó su sello, y cuatro motores nuevos y chicos (`deformacion`, `cinetica`, `desgaste`, `sismico`) que comparten un andamio, sortean el tamaño del dataset como un nivel más del modelo y entrenan en dos rondas. El método lento de los cinco se corre al final (D-38).

**Amortizar** es pagar el costo de cálculo una vez, por adelantado, para que cada respuesta sea instantánea. Los modelos, con sus ecuaciones, están en `WORKPLAN.md`, sección 11. En el código, en el README técnico y en `STACK.md` se usan los nombres técnicos precisos. En la pantalla y en el pitch, `GLOSARIO.md`.

## La lección de anoche, que ordena todo lo de hoy

El motor de 7 parámetros pasó su sello después de una noche; el de 32 no. Por eso:

- **Motores chicos:** 5 a 7 parámetros globales y 2 locales por unidad. No agregues parámetros «para que sea más realista».
- **Un andamio, cuatro simuladores.** El codificador, los dos flujos, la pérdida, el SBC y la exportación se escriben una vez (`motor/comun/series.py`, `nucleo/series.py`). Cada motor aporta su simulador, su lista de parámetros y su función «lo que se decide».
- **El método lento va al final (D-38).** Es lo que más cómputo gasta, y primero interesa ver qué da la red. Orden por motor: modelo con su diseño del dataset → simulador y predictivo a priori → red → prueba de humo → entrenar → validar sin MCMC (SBC global y local, cobertura de lo que se decide, examen, por tramos de tamaño) → exportar → `analizar` → app. El MCMC (NUTS en NumPyro) de los cinco motores es la tarea A-36. Se adelanta solo si una red no pasa su sello y su tarjeta no tendría con qué responder a las 17:30: anótalo en el estado y avísale a la persona de este computador.
- **Cada modelo sortea el tamaño del dataset (D-38).** Cuántas unidades, cuántas lecturas por unidad (distintas entre unidades), tiempos irregulares y lecturas faltantes: es el grupo `Diseño del dataset` de cada bloque de `WORKPLAN.md`, sección 11, y va en el simulador desde el primer día y en el `config.json`. Una red que practicó con un solo tamaño no sirve para el archivo de un usuario.
- **`espacial` no se toca ni se reentrena.** `leyes` es el mismo motor con otro archivo y ya responde verde.

## Dos sesiones en este computador

- **Sesión A:** el andamio (`motor/comun/series.py`, `nucleo/series.py`) y después `deformacion` y `sismico`. Tareas A-23, A-25, A-28.
- **Sesión B:** `leyes`, `cinetica` y `desgaste`. Importa el andamio y no lo edita; si necesita un cambio ahí, se lo pide a la sesión A. Tareas A-22, A-24, A-27.

Cada sesión hace sus propios commits, chicos, con `git pull --rebase` antes de cada `git push`.

## Lo que es tuyo y lo que no

- **Tuyo:** `nucleo/`, `motor/`, `pyproject.toml`, `estado/amortizacion.md`.
- **No tocas:** `servicio/` y `web/` (PC 1); `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md` (PC 3). Si un prior tuyo deja el archivo del demo fuera de lo simulado, pídele a PC 3 que lo regenere (`datos/preparar/<caso>.py`, misma semilla) o ajusta el prior; no edites el CSV.
- **`nucleo/` no importa `torch`, `zuko`, `jax` ni `numpyro`.** De cada red se entrega el codificador en ONNX y los flujos como `.npz`, que `nucleo/flujo.py` muestrea en NumPy.

## Cómo trabajas

1. Antes de cada tarea: `git pull --rebase` y lee `estado/TABLERO.md`. **Si el tablero dice otra cosa que esta lista, manda el tablero.**
2. Haz la tarea contra su criterio de «listo cuando». Si lleva el doble de su duración, córtala o simplifícala y anótalo.
3. Al terminar: skill `actualizar-estado`, con el identificador de la tarea al inicio de la línea («A-23 terminada: …») y los números. Cada número que vaya a verse en pantalla o decirse en el pitch se lo pides registrar a PC 3.
4. **Las horas de la tabla son topes, no horas de inicio (D-29).** Lo que espera a una red entrenada se construye contra la red sin entrenar y datos simulados.

## Tus tareas, en orden

El detalle (entregable y criterio de cada una) y el calendario de cómputo están en `WORKPLAN.md`, sección 6.3. Los modelos y el andamio, en la sección 11. La forma exacta de cada respuesta, en `contratos/CONTRATO.md`.

| Id | Hora | Min | Qué |
|---|---|---|---|
| A-21 | 12:15 | 15 | *La persona.* Detener `estados` (Ctrl-C guarda). `MOTORES` de `nucleo/casos.py` suma `deformacion`, `cinetica`, `desgaste`, `sismico`; `prueba_api` espera el `INICIO` nuevo; avisar a PC 3 para que descomente las cuatro tarjetas en `casos/INICIO` |
| A-22 | 12:30 | 30 | *Sesión B.* `leyes`: confirmar `analizar` y `donde_medir` con la red; examen contra `leyes_verdad.csv`; `rotulos.donde_medir` del caso en la respuesta. Su método lento pasa a A-36 |
| A-23 | 12:30 | 60 | *Sesión A.* **El andamio de series** (`WORKPLAN.md`, 11.6), con tamaños variables: relleno, máscara y el tamaño como entrada. Subirlo apenas pase su prueba: la sesión B lo espera |
| A-24 | 13:00 | 60 | *Sesión B.* `cinetica` (11.3) con su diseño del dataset, listo para lanzar. Predictivo a priori contra `datos/demo/flotacion.csv` |
| A-25 | 13:30 | 60 | *Sesión A.* `deformacion` (11.2), listo para lanzar. Contra `datos/demo/taludes.csv`. **Lo lanza la persona de PC 3** |
| A-26 | 14:30 | 10 | **Lanzar la ronda 1:** `cinetica` aquí, hasta las 16:10. Sin MCMC antes. **H4** |
| A-27 | 14:40 | 50 | *Sesión B.* `desgaste` (11.4), sin lanzar |
| A-28 | 14:40 | 60 | *Sesión A.* `sismico` (11.5), sin lanzar |
| A-29 | 15:40 | 30 | `analizar` de `flotacion` y `taludes` con la red sin entrenar (la forma, no los números): `unidades`, `muestras_p`, `curva`, `factores`, examen, y `rojo_datos` fuera de los rangos de tamaño. Entregar a PC 1 |
| A-30 | 16:10 | 20 | **Sin nada entrenando.** Detener la ronda 1. `validar-motor cinetica` aquí; PC 3 valida `deformacion`. Sin MCMC (`mcmc_*` en `null`); solo si una red no pasa, se adelanta el de su archivo del demo |
| A-31 | 16:30 | 10 | **Lanzar la ronda 2:** `desgaste` aquí; PC 3 lanza `sismico`. Hasta las 18:15. **H5** |
| A-32 | 16:40 | 50 | Retirar `supervivencia`, `jerarquico`, `estados` y `cartera` del repositorio (código, artefactos, pruebas). `analizar` de `flota` y `sismicidad` con la red sin entrenar |
| A-33 | 17:30 | 30 | Cifras por motor para PC 3. Fijar `KRYLOV_MOTOR_<ID>` de cada tarjeta para las 18:00. Ayudar a PC 1 con `exportar_estatico` |
| A-34 | 18:15 | 45 | **Sin nada entrenando.** `validar-motor desgaste` aquí y `sismico` en PC 3. Tiempos del recorrido. El que pase antes de las 20:30 pasa a `red` |
| A-35 | 19:00 | 60 | Sellos (todavía sin MCMC), `limitaciones` y README técnico (`motor/README.md`) con los cinco motores y sus rangos de tamaño |
| A-36 | 20:00 | 90 | **Al final y sin nada entrenando: el método lento de los cinco motores.** Archivo del demo y de 3 a 5 datasets simulados por motor, 10 minutos de presupuesto por dataset. Tiempo, r̂ y diferencia con la red, tal cual salgan. Completa `mcmc_*` y `amortizacion` de cada sello. Empieza antes si el computador queda sin entrenar |

**Tope de redes: 20:30.** Después no cambia quién responde cada tarjeta. A las 22:00, el README técnico final. No se reentrena después de las 20:30.

## Lo que más importa de tu trabajo

- **El andamio decide el día.** Si A-23 no está subido a las 13:45, la ronda 1 se lanza solo con el flujo global y lo local del archivo del demo sale del método lento (`WORKPLAN.md`, 6.8). Dilo en tu estado a esa hora, no después.
- **Tamaños variables, con un máximo fijo por motor.** El simulador sortea el tamaño de cada dataset; los tensores llevan relleno y máscara hasta el máximo, para que ONNX exporte sin ejes dinámicos. El tamaño entra además como dato explícito al codificador (el pooling normalizado no lo ve), y cada lote puede compartir un tamaño para no gastar relleno. Si las convoluciones con máscara no exportan o no aprenden en la prueba de humo, una GRU chica.
- **Fuera del rango, se dice.** Un archivo bajo el mínimo del motor da `rojo_datos` con su motivo («hay 3 camiones y practiqué con flotas de 8 a 120»); sobre el máximo, submuestra con semilla fija y aviso. `papeles()` publica el mismo rango que el `config.json`, y el archivo del demo queda bien adentro.
- **Un solo preprocesamiento por motor**, en `nucleo/`: la misma función prepara los datasets simulados y el archivo real. En `deformacion` incluye la resta del modo común y la normalización por la escala del archivo.
- **Los flujos en NumPy dan lo mismo que en `torch`.** La prueba de siempre, para el flujo global y para el local.
- **Mide antes de afirmar.** Procesador o GPU del Mac se decide con `medir-rendimiento`, por motor. La cifra «practicó con N» la cuenta el bucle de entrenamiento.
- **Las mediciones de tiempo se hacen sin nada entrenando.** El MCMC nunca corre encima de un entrenamiento.
- **Cuatro chequeos por motor** (`WORKPLAN.md`, 11.8): SBC y cobertura (global, local y de lo que se decide) por tramos de tamaño, con el peor tramo en el sello; examen con la verdad escondida; semáforo; y, al final, la comparación con el MCMC. El sello se escribe sin esperar al MCMC.
- **Si el método lento no converge en 10 minutos por dataset, se anota y se sigue.**
- **El método lento se informa tal cual:** tiempo, r̂ y diferencia con la red. No se elige ni se degrada una referencia para que la red se vea mejor; si resulta rápido en un modelo chico, se dice, y la comparación que se cuente dice exactamente qué se comparó.
- **Ningún resultado se adelanta.** A PC 3 le pasas lo que salió, tal cual. El guion se escribe después.
- **El código se revisa.** Un cuarto de la nota es «aspecto técnico», con revisión automatizada del repositorio: tiene que leerse como SBI de verdad y como un producto minero. Por eso A-32 retira los motores antiguos. Módulos chicos, una prueba por módulo, nombres técnicos precisos.

## Si algo sale mal

| Qué | Qué haces |
|---|---|
| Un motor de la ronda 1 no tiene prueba de humo a las 14:30 | Se lanza cuando esté; valida igual a las 16:10. Si a las 15:15 no hay prueba de humo, se adelanta su método lento y ese computador queda para la ronda 2 |
| Un motor no pasa `validar-motor` | Se adelanta el método lento de su archivo del demo (10 minutos de presupuesto, sin nada entrenando): la tarjeta sale «precalculada». Avisa a la persona de este computador. Si la red mejora, puede seguir entrenando después de la ronda 2 y revalidar antes de las 20:30 |
| El método lento adelantado tampoco converge | Esa tarjeta sale del inicio. Avisa a PC 3 y a PC 1 |
| El peor tramo de tamaño no pasa pero el resto sí | Se achica el rango que el motor declara (`config.json`, `papeles()`), se dice en `limitaciones`, y fuera de ese rango responde `rojo_datos` |
| El SBC local no pasa pero el global sí | La tarjeta responde con el η de la red y los locales del método lento para el archivo del demo; rotulada «precalculado» |
| El Mac se calienta y cae más de 30% | Menos tamaño de lote o procesador |
| El codificador no exporta a ONNX | Promedio con máscara en vez de atención; GRU en vez de convoluciones. Avisa a PC 1 solo si no hay salida |
| El archivo del demo cae fuera de lo simulado | Ajusta el prior o pide a PC 3 regenerar el archivo. No se fuerza |

## Qué recibes y qué entregas

- De PC 3: los archivos del demo (`datos/demo/`: `leyes.csv`, `taludes.csv`, `flotacion.csv`, `flota.csv`, `sismicidad.csv`, cada uno con su `_verdad.csv`), los casos en `casos/`, **y su computador** para entrenar `deformacion` y `sismico`.
- A PC 1: las funciones de `nucleo/api.py`. `leyes` ya; `flotacion` y `taludes` cerca de las 15:40; `flota` y `sismicidad` cerca de las 17:10.
- A PC 3: cada número medido, por tu estado.

## Arranque en un computador nuevo

Este computador ya trabajó antes del pivote: `git pull --rebase` y sigue. Para lanzar algo largo: enchufado, **tapa abierta**, brillo al mínimo, superficie dura, modo de bajo consumo apagado, todo dentro de `caffeinate -dims`. Reglas de siempre: `git pull --rebase` antes de cada `git push`; nunca `--force`; se versionan, por motor, `codificador.onnx`, `flujo.npz`, `flujo_local.npz`, `pesos.pt`, `config.json`, `sello.json` y, cuando existan, las muestras de `mcmc/`; no los puntos de guardado intermedios.
