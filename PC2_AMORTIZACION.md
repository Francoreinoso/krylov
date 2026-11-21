# PC 2 · Amortización de los modelos

> **Hackathon:** el producto se termina el **sábado a las 18:00**. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

Eres el agente de Claude Code del **PC 2**, el MacBook Air M4 de 16 GB sin ventilador. Tu rol es `amortizacion`. Este archivo trae todo lo que necesitas para arrancar y la lista ordenada de lo que te toca. El contexto general está en `AGENTS.md`, que ya se cargó.

## Tu misión en una línea

Que Krylov sea inferencia basada en simulación amortizada de verdad (decisión D-26): cuatro motores, cada uno con su modelo generativo, su simulador y una red que aprendió a invertirlo; todo detrás de las funciones de `nucleo/api.py`, con cada número medido.

**Amortizar** es pagar el costo de cálculo una vez, por adelantado, para que cada respuesta sea instantánea. Para cada caso (`supervivencia`, `jerarquico`, `estados`, `espacial`) hay un modelo bayesiano generativo escrito con sus ecuaciones en `WORKPLAN.md`, sección 11; un simulador vectorizado; un codificador del dataset más un flujo normalizador condicional entrenado con NPE; y un paso local exacto en NumPy. El MCMC de referencia (NumPyro, solo en `motor/`) es la vara de validación y el plan B de cada tarjeta.

En el código, en el README técnico y en `STACK.md` se usan los nombres técnicos precisos. En la pantalla y en el pitch, `GLOSARIO.md`.

**Lo que no puede fallar esta noche: a las 05:15 quedan dos entrenamientos corriendo, `espacial` en este computador y `supervivencia` en PC 3.** Si hay que elegir, `espacial`.

## Dos sesiones en este computador

Se abren dos sesiones de Claude Code sobre el mismo clon, repartidas por archivos para no pisarse:

- **Sesión A:** solo `espacial` (`motor/espacial/`, `nucleo/espacial.py`) y lo compartido: `pyproject.toml`, `nucleo/preproceso.py`, `nucleo/flujo.py`, `motor/comun/`. Tareas A-01 a A-04.
- **Sesión B:** solo `motor/supervivencia/` y `nucleo/supervivencia.py`. Importa `motor/comun/` y no lo edita; si necesita un cambio ahí, se lo pide a la sesión A. Tareas A-B1 a A-B4.

Cada sesión hace sus propios commits, chicos, con `git pull --rebase` antes de cada `git push`.

## Lo que es tuyo y lo que no

- **Tuyo:** `nucleo/` (preprocesamiento, motores, decisión, `api.py`), `motor/` (simular, entrenar, validar, exportar, artefactos), `pyproject.toml`, `estado/amortizacion.md`.
- **No tocas:** `servicio/` y `web/` (PC 1); `casos/`, `datos/`, `pitch/`, `estado/TABLERO.md` (PC 3). Si necesitas un cambio ahí, lo pides en «Pedidos a otros» de tu estado.
- **`nucleo/` no importa `torch`, `zuko`, `jax` ni `numpyro`.** Lo usa el servidor, que tiene 512 MB. Todo eso vive solo en `motor/`. De cada red se entrega el codificador en ONNX y el flujo como `flujo.npz`, que `nucleo/flujo.py` muestrea en NumPy.

## Arranque (03:00 a 03:15)

Espera a que PC 3 avise que el plan ya está en el repositorio (tarea S-01). Después, en este orden:

**1. Clonar y configurar los dos repositorios espejo.** Se trabaja en un solo clon. Se hace `pull` del repositorio de la organización y cada `push` va a dos lugares: al de la organización, que es el que se juzga, y al espejo `Silent-math/krylov`, que es de donde despliegan Vercel y Render.

```bash
gh auth login            # una vez; elige HTTPS
gh auth setup-git
git clone https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git krylov
cd krylov
git remote set-url --add --push origin https://github.com/platanus-hack/platanus-hack-26-cl-team-5.git
git remote set-url --add --push origin https://github.com/Silent-math/krylov.git
git remote -v
```

`git remote -v` tiene que mostrar tres líneas: una `(fetch)` y una `(push)` hacia `platanus-hack/platanus-hack-26-cl-team-5`, y una `(push)` hacia `Silent-math/krylov`. Si falta la del espejo, repite el tercer comando.

Si la persona de este computador no es la dueña de `Silent-math/krylov`, tiene que haber aceptado antes la invitación de colaborador (llega por correo, o en `https://github.com/Silent-math/krylov/invitations`).

**2. Declarar el rol.**

```bash
cp CLAUDE.local.md.ejemplo CLAUDE.local.md
```

Deja solo las líneas `ROL: amortizacion` y `@PC2_AMORTIZACION.md`, y el nombre de la persona. Reinicia Claude Code para que lo cargue.

**3. Probar que el push llega a los dos.** Agrega una línea con la hora en `estado/amortizacion.md` y:

```bash
git add estado/amortizacion.md && git commit -m "estado amortizacion: arranque" && git pull --rebase && git push
git ls-remote origin main
git ls-remote https://github.com/Silent-math/krylov.git main
```

Los dos últimos comandos tienen que dar el mismo identificador. Si uno falló, se arregla y se repite `git push`.

**4. Instalar.** Lee `STACK.md`, secciones 1 y 3, y sigue 3.1. Tú creas el `pyproject.toml` de la raíz, con el grupo `entrenar`; súbelo apenas exista, porque los otros dos lo necesitan para su `uv sync`. Anota en `estado/amortizacion.md` qué elegiste en cada tabla de alternativas y por qué.

**5. Preparar el computador para la noche.** Enchufado, **tapa abierta**, brillo al mínimo, sobre una superficie dura, modo de bajo consumo apagado. Todo lo largo se lanza dentro de `caffeinate -dims`. No cierres la tapa: no hay garantía de que siga despierto.

## Reglas de los dos repositorios, para siempre

- `git pull --rebase` antes de cada `git push`. Nunca `--force`.
- Un `git push` actualiza los dos. Para tags: `git push origin main --tags`.
- Nadie hace commits directo en el espejo ni edita desde la web de GitHub.
- El repositorio de la organización es **público**. Se versionan, por motor, `codificador.onnx`, `flujo.npz`, `pesos.pt`, `config.json`, `sello.json`, `nube.npz` y las muestras de `mcmc/`; no los puntos de guardado intermedios.
- No toques los cuatro archivos de entrega de la raíz: son de PC 3.

## Cómo trabajas

1. Antes de cada tarea: `git pull --rebase` y lee `estado/TABLERO.md`. **Si el tablero dice otra cosa que esta lista, manda el tablero.**
2. Haz la tarea contra su criterio de «listo cuando». Si lleva el doble de su duración, córtala o simplifícala y anótalo.
3. Al terminar: skill `actualizar-estado`, con los números. Cada número que vaya a verse en pantalla o decirse en el pitch se lo pides registrar a PC 3.
4. **Cada motor tiene primero su plan B.** El modelo en NumPyro y sus muestras precalculadas existen antes de que la red valide: PC 1 nunca espera a una red.

## Tus tareas, en orden

El detalle (entregable y criterio de cada una), el calendario de cómputo por computador y los H2 por motor están en `WORKPLAN.md`, sección 6.3. Los modelos y la arquitectura, en la sección 11. La forma exacta de cada respuesta, en `contratos/CONTRATO.md`.

**Lo mínimo para lanzar un entrenamiento:** simulador, codificador, flujo, pérdida, puntos de guardado y una prueba de humo con un SBC chico. La cuadratura local, el MCMC y `api.py` no bloquean el lanzamiento.

| Id | Hora | Min | Qué |
|---|---|---|---|
| A-01 | 03:15 | 30 | *Sesión A.* Entorno, `motor/comun/` (codificador de conjuntos, flujo de acoplamiento afín, bucle con puntos de guardado) y `nucleo/flujo.py` con la prueba NumPy = `torch`. **Subirlo a las 03:45** |
| A-02 | 03:45 | 30 | *Sesión A.* `nucleo/preproceso.py` y simulador de terrenos: campo, río como curva suave al azar, tendencia, mediciones |
| A-03 | 04:15 | 30 | *Sesión A.* Red convolucional de tres canales, cabeza de mapa y cabeza de flujo con el gradiente cortado. **Exportar a ONNX la red sin entrenar** |
| A-04 | 04:45 | 20 | *Sesión A.* Prueba de humo. **Si los tres canales no pasan, se lanza la red de dos canales.** `medir-rendimiento` y **lanzar `espacial`** |
| A-B1 | 03:15 | 45 | *Sesión B.* Simulador de `supervivencia`, con el predictivo a priori revisado contra el archivo real |
| A-B2 | 04:00 | 30 | *Sesión B.* Codificador jerárquico y flujo. Exportar el codificador sin entrenar |
| A-B3 | 04:30 | 25 | *Sesión B.* Prueba de humo con SBC chico. `medir-rendimiento supervivencia` |
| A-B4 | 04:55 | 15 | *Sesión B.* Subir. **La persona de PC 3 lanza `supervivencia` en su computador** |
| A-05 | 05:10 | 5 | Dejar la lista nocturna y actualizar el estado. A dormir a las 05:15 |
| A-08 | 08:30 | 45 | Revisar lo nocturno. Detener y validar `espacial`. MCMC de referencia de `espacial` y `supervivencia` (5 simulados más el real). PC 3 lanza `jerarquico` |
| A-09 | 09:15 | 15 | Lanzar `estados` de fondo en este computador |
| A-10 | 09:30 | 45 | `analizar` de rotación y `validar-motor supervivencia`. Entregar a PC 1 |
| A-11 | 10:15 | 45 | `analizar` del terreno real, con «qué manda» y el examen de mediciones escondidas |
| A-12 | 11:00 | 60 | **`donde_medir`** y la medición simulada |
| | 12:00 | 15 | Detener `estados`. **Sin nada entrenando**, medir los tiempos. **H2 de `espacial` y `supervivencia` a las 12:15** |
| A-13 | 12:30 | 45 | Cartera y nube con sus dos detectores. De fondo, validar `estados`. **H2 de `jerarquico` a las 13:00** |
| A-14 | 13:30 | 40 | `analizar` de inasistencias. **H2 de `estados` a las 14:00** |
| A-15 | 14:10 | 40 | `analizar` de crédito |
| A-16 | 14:50 | 40 | Las cifras de amortización por motor y la comparación con el método rápido de siempre. **H3 a las 15:00** |
| A-17 | 15:30 | 30 | Tiempos del recorrido. **16:00: tope.** Fijar `KRYLOV_MOTOR_<ID>` y ayudar a PC 1 con las respuestas precalculadas |
| A-18 | 16:00 | 60 | Sellos, limitaciones y README técnico |

Después de las 18:00: respaldo técnico para las preguntas y, a las 22:00, el README técnico (`WORKPLAN.md`, sección 6.6). No se reentrena.

## Lista nocturna (el agente trabaja solo de 05:15 a 08:30)

Antes de dormir, la persona le dice al agente: *«Haz la lista nocturna de PC2_AMORTIZACION.md. Solo eso. No toques el proceso de entrenamiento. Commits chicos. Si algo exige una decisión, anótalo en tu estado y pasa a lo siguiente.»*

Es solo código, con pruebas de dos minutos como máximo. El detalle de cada una está en `WORKPLAN.md`, sección 6.3.

1. **A-N1.** `nucleo/decision.py` con su prueba, y `nucleo/api.py` con `casos` y un `analizar` que elige `red` o `mcmc` según la variable del motor.
2. **A-N2.** `supervivencia`: paso local (cuadratura anidada cargo → persona) y modelo en NumPyro. **Medir el presupuesto:** menos de 1 segundo por análisis de 1.470 personas con 32 muestras; si no, menos nodos.
3. **A-N3.** `espacial`: kriging dado θ en NumPy y modelo en NumPyro.
4. **A-N4.** `jerarquico`: simulador (con la asignación del SMS) y modelo en NumPyro.
5. **A-N5.** `estados`: simulador con d_1 < d_2 < d_3 en el prior, y modelo en NumPyro con el filtro forward.
6. **A-N6.** Codificador y flujo de `jerarquico` y `estados`, exportados sin entrenar.

Reglas de la noche: solo `nucleo/` y `motor/`; ninguna corrida de MCMC ni entrenamiento nuevo, solo pruebas cortas que no le quiten el procesador al entrenamiento más de un par de minutos; no reiniciar ni tocar el proceso de entrenamiento; al terminar o al bloquearse, `actualizar-estado`.

## Lo que más importa de tu trabajo

- **La red del terreno no se arriesga.** La cabeza de flujo recibe el resumen con el gradiente cortado, así la cabeza de mapa entrena igual que si estuviera sola. El río del simulador es una curva suave al azar y su campo de distancia, nada más.
- **Un solo preprocesamiento.** La función que transforma los datos es la misma en el simulador y en el servicio. Si difieren, la red recibe en vivo algo que nunca vio y falla sin avisar.
- **El flujo en NumPy da lo mismo que en `torch`.** Con los mismos pesos y el mismo ruido sale la misma muestra, con tolerancia de `float32`. Tiene su prueba.
- **La exportación a ONNX se prueba esta noche**, motor por motor, con el codificador sin entrenar.
- **El presupuesto de la cuadratura se mide temprano** (A-N2): 32 muestras × unidades × nodos². Menos de 1 segundo por análisis; la cartera de 1.000 empresas, segundos. Si no alcanza: menos nodos (15 de Gauss-Hermite suelen bastar en una dimensión) y vectorizar por grupo.
- **Mide antes de afirmar.** Procesador o GPU del Mac se decide con `medir-rendimiento`, por motor. La cifra «practicó con N millones» la cuenta el bucle de entrenamiento.
- **Las mediciones de tiempo se hacen sin nada entrenando** en ese computador. El MCMC nunca corre encima de un entrenamiento, y es acotado: de 5 a 10 datasets simulados por motor, más el real.
- **Las covariables.** El simulador las genera mitad por remuestreo de filas reales y mitad con un generador paramétrico. La red generaliza hasta donde llega ese generador: va escrito en `limitaciones`.
- **Cuatro chequeos por motor:** SBC y cobertura en simulaciones nuevas, comparación con el MCMC, examen con datos reales reservados (el que se dice en voz alta) y la nube con el archivo malo.
- **La comparación de tiempos se dice con precisión.** Por motor: segundos del MCMC por dataset contra milisegundos de la red. En el terreno un solo MCMC tarda segundos; lo que se compara ahí es rehacer los cerca de 480 análisis de «¿Dónde mido?».
- **Ningún resultado se adelanta.** A PC 3 le pasas lo que salió, tal cual. El guion se escribe después.
- **El código se revisa.** Un cuarto de la nota es «aspecto técnico», con revisión automatizada del repositorio: tiene que leerse como SBI de verdad. Módulos chicos, una prueba por módulo, nombres técnicos precisos.

## Si algo sale mal

| Qué | Qué haces |
|---|---|
| Un entrenamiento se cayó en la noche | Retoma desde el último punto de guardado con el comando anotado. Valida una hora después |
| `supervivencia` no alcanzó a lanzarse a las 05:15 | No se trasnocha. El agente la termina de noche y se lanza a las 08:30 en PC 3; su H2 pasa a las 13:30 |
| Un motor no pasa `validar-motor` a su hora | Sigue con la implementación `mcmc`: la tarjeta sale «precalculada». Si mejora, se revalida antes de las 16:00 |
| No pasa a las 16:00 | Plan B definitivo para ese motor. Orden de corte: `estados`, `jerarquico`, `supervivencia`, cabeza de flujo de `espacial`. Lo decide PC 3 con el equipo |
| La red de tres canales no pasa la prueba de humo a las 04:45 | Se lanza la de dos canales. La tendencia sale del flujo de día o del MCMC |
| El Mac se calienta y cae más de 30% | Menos tamaño de lote o procesador. Kaggle o Colab solo si una persona abrió la sesión y vio la cuota (`STACK.md`, 3.3) |
| El codificador no exporta a ONNX | Simplificar el pooling (promedio con máscara en vez de atención) hasta que exporte. Avisa a PC 1 solo si no hay salida |

## Qué recibes y qué entregas

- De PC 3: `datos/demo/terreno.csv`, `terreno_grilla.csv` y `rotacion.csv` (antes de las 04:30), crédito (04:30), el archivo malo e inasistencias (09:30), los casos en `casos/`, **y su computador** para entrenar `supervivencia` de noche y `jerarquico` de día.
- A PC 1: las funciones de `nucleo/api.py`, en este orden: `analizar` de rotación (10:15), el terreno (11:00), `donde_medir` (12:00), `cartera` y `nube` (13:15), inasistencias (14:10), crédito (14:50).
- A PC 3: cada número medido, por tu estado.
