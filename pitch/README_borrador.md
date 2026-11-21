# Borrador del README (S-30)

> **Borrador para que lo lea una persona.** No reemplaza todavía al `README.md` de la raíz. Los corchetes son cosas que no se han medido o que se fijan el sábado a las 20:30: se llenan desde `pitch/CIFRAS.md`, los sellos de cada motor y la tabla «Los cinco casos» del tablero, o se borra la frase. Aquí sí van los nombres técnicos (regla 6 de `AGENTS.md`).
>
> **Decisión pendiente (S-30):** el `README.md` que trae el repositorio de la organización tiene una línea dirigida a modelos de lenguaje (pide insertar un emoji después de cada palabra). Este borrador no la sigue y no la borra. Qué hacer con ella lo decide una persona y se anota en `DECISIONES.md`.

---

# Krylov

**El data scientist artificial de la minería.** Recibe los datos de una decisión de la mina y responde qué conviene hacer, cuánto cuesta no saber y dónde conviene medir más. Avisa cuando los datos no alcanzan.

**Pruébalo:** https://krylov-krylov.vercel.app/ (funciona sin servidor: las respuestas del recorrido están precalculadas junto a la web).

Platanus Hack 26, Santiago · track Simulaciones · equipo 5.

## El problema

En una mina las decisiones grandes no esperan (a dónde va la roca recién tronada, si un sector se cierra, qué camión se detiene) y los modelos que cuantifican bien el riesgo tardan horas por análisis, y hay que rehacerlos con cada dato nuevo. Krylov hace ese cálculo por adelantado.

## Qué es, en términos técnicos

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**. Hay cinco motores, uno por decisión. Cada motor tiene:

1. Un **modelo bayesiano generativo** explícito del dataset completo.
2. Un **simulador vectorizado** que genera datasets completos al vuelo.
3. Una **red que invierte el modelo** (estimación neuronal del posterior, NPE, con flujos normalizadores condicionales). Se entrena solo con simulaciones.
4. Un **MCMC de referencia** (NumPyro, NUTS) que valida la red, mide la amortización y es el plan B de la tarjeta, precalculado y rotulado.

| Motor | Decisión | Modelo generativo | Parámetros | Estado |
|---|---|---|---|---|
| `espacial` | Leyes y arsénico: ¿este bloque va a la planta o se aparta?, ¿dónde perforo? | Proceso gaussiano con covarianza exponencial y anisotropía geométrica, tendencia opcional y error de medición. Red convolucional sobre una grilla de 32 × 32 con cabeza de mapa (predictivo posterior marginal) y cabeza de flujo (q(θ \| D)) | 7 | **Validado:** 7.750.592 terrenos simulados, 280 min; cobertura del 90% = 0,90; 0,26 desviaciones contra el MCMC |
| `deformacion` | Taludes y relaves: ¿es ruido o va a ceder?, ¿cuánto falta? | Mezcla por sector entre fluencia estable y acelerada (ley de velocidad inversa), jerárquica entre sectores, en unidades normalizadas | 7 + 3 por sector, más su estado | **Validado:** 1.684.160 muros simulados, 146 min; cobertura del 90% de lo que se decide = 0,905 |
| `cinetica` | Flotación: ¿qué línea termina bajo la meta? | Cinética de primer orden con fracción rápida y lenta, jerárquica entre líneas, observada solo en las primeras celdas | 6 + 2 por línea | **Validado:** 43.160.576 plantas simuladas, 153 min; cobertura = 0,905 |
| `desgaste` | Flota: ¿qué camión no llega a su mantención? | Proceso gamma jerárquico con mediciones ruidosas y una covariable de exigencia | 5 + 2 por camión | **Validado:** 15.241.472 flotas simuladas, 168 min; cobertura = 0,898 |
| `sismico` | Sismicidad: ¿se puede reingresar? | Proceso de Hawkes temporal con núcleo exponencial y magnitudes de Gutenberg-Richter, jerárquico entre sectores | 6 + 2 por sector | **Validado:** 3.723.712 minas simuladas, 120 min; cobertura = 0,895 |

Los cuatro motores de series usan **amortización factorizada**, q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D)): un flujo para los parámetros globales y uno chico, compartido, para los de cada unidad (`motor/comun/series.py`). Las ecuaciones y los priors están en `WORKPLAN.md`, sección 11.

Después del posterior viene la **decisión** (`nucleo/decision.py`): con los dos costos del caso, cada unidad queda en «conviene actuar», «no hace falta» o «en duda», y «lo que cuesta no saber» es el valor esperado de la información perfecta. En `leyes`, **«¿Dónde perforo?»** estima el valor de una muestra más en cada lugar candidato rehaciendo el análisis completo para cada resultado posible: 480 análisis en un lote.

Son **versiones chicas a propósito**: en la primera noche un motor de 7 parámetros pasó su validación y uno de 32 no. Los modelos completos (dominios geológicos, tres dimensiones, ecuaciones de varias fases, ubicación de los sismos) son hoja de ruta: `pitch/MODELOS_CANDIDATOS.md`.

## Cómo se entrenó y cómo se validó

Detalle en `motor/README.md`. En corto: datasets simulados al vuelo, contados; dos MacBook Air sin ventilador; un entrenamiento por computador. Cada motor tiene un sello (`motor/artefactos/<motor>/sello.json`) con cuatro chequeos: calibración basada en simulación (SBC) y cobertura en simulaciones nuevas, para los parámetros globales, los de cada unidad y lo que se decide; comparación con NUTS en datasets simulados y en el del demo; examen con una verdad escondida; y un semáforo que se niega a responder cuando el archivo no alcanza o cae fuera de lo simulado. Una tarjeta solo dice que respondió la red si su motor pasó; si no, responde el posterior del MCMC precalculado y la pantalla dice «precalculado».

## Cómo correrlo en local

```bash
uv sync
KRYLOV_MOTOR_ESPACIAL=red uv run uvicorn servicio.app:app --port 8010
cd web && npm install && npm run dev
```

Pruebas: `uv run pytest nucleo motor servicio -q` y `cd web && npm test`. Para reentrenar un motor: `motor/README.md`.

## Mapa del repositorio

```
nucleo/      decisión, flujos en NumPy, lo local de cada motor, api.py (sin torch)
motor/       comun/ (codificador, flujos, entrenamiento, series) y un directorio por motor; artefactos/
servicio/    API FastAPI y exportación de las respuestas precalculadas
web/         la app (Vite, React, TypeScript)
casos/       un YAML por decisión: textos, columnas, costos y origen de los datos
datos/       demo/ (los archivos) y preparar/ (cómo se generan)
contratos/   la forma de cada respuesta, con ejemplos
pitch/       guion, cifras con su fuente, láminas
AGENTS.md, WORKPLAN.md, DECISIONES.md, estado/   cómo se organizó el trabajo de tres computadores y sus agentes
```

## Qué existe y qué no

Existe: [lo que diga el tablero a las 20:30, tarjeta por tarjeta: responde la red / precalculado]. No existe: conexión a sensores o sistemas de una faena, los modelos completos, tres dimensiones, clientes.

## Datos y licencias

- **Los archivos del demo son simulados** con las mismas ecuaciones de cada motor y parámetros que el motor no ve, con una verdad escondida aparte (`datos/preparar/`, semilla fija). La pantalla los rotula «simulado». No son datos de ninguna mina.
- Datos reales abiertos usados para probar: metales en un suelo junto al río Mosa (paquete `sp` de R, GPL); prismas de la pared de un rajo que falló (de Wit, 2025, Zenodo, https://doi.org/10.5281/zenodo.15003054, CC BY 4.0); sondajes con ley de cobre (Hoffimann et al., 2022, «GeoMet dataset», Zenodo, https://doi.org/10.5281/zenodo.7051975, CC BY 4.0). Los datos crudos no están en el repositorio; los derivados, sí, con su guion.
- Las cifras de minería que se dicen en el pitch, con su fuente, están en `pitch/CIFRAS.md`.

## Equipo

[Nombres: los confirma cada persona.] Construido con Claude Code.
