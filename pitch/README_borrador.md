# Borrador del README (S-30)

> **Borrador para que lo lea una persona.** No reemplaza todavía al `README.md` de la raíz. Puesto al día el sábado a las 23:45 con los cinco sellos, el tablero y `pitch/CIFRAS.md`: ya no tiene corchetes. Aquí sí van los nombres técnicos (regla 6 de `AGENTS.md`). Para aplicarlo, después de leerlo: copiar desde la línea `# Krylov` hasta el final sobre `README.md`.
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
4. Un **MCMC de referencia** (NumPyro, NUTS): la segunda vara para la red y la medida de la amortización. Se corrió al final, cuando las redes ya tenían su veredicto.

| Motor | Decisión | Modelo generativo | Parámetros | Estado |
|---|---|---|---|---|
| `espacial` | Leyes y arsénico: ¿este bloque va a la planta o se aparta?, ¿dónde perforo? | Proceso gaussiano con covarianza exponencial y anisotropía geométrica, tendencia opcional y error de medición. Red convolucional sobre una grilla de 32 × 32 con cabeza de mapa (predictivo posterior marginal) y cabeza de flujo (q(θ \| D)) | 7 | **Sello pasa.** 7.750.592 terrenos simulados, 280 min; cobertura del 90% = 0,90; 0,26 desviaciones contra el MCMC |
| `deformacion` | Taludes y relaves: ¿es ruido o va a ceder?, ¿cuánto falta? | Mezcla por sector entre fluencia estable y acelerada (ley de velocidad inversa), jerárquica entre sectores, en unidades normalizadas | 7 + 3 por sector, más su estado | **Sello pasa.** 1.684.160 muros simulados, 146 min; cobertura del 90% de lo que se decide = 0,905 |
| `cinetica` | Flotación: ¿qué línea termina bajo la meta? | Cinética de primer orden con fracción rápida y lenta, jerárquica entre líneas, observada solo en las primeras celdas | 6 + 2 por línea | **Sello pasa.** 43.160.576 plantas simuladas, 153 min; cobertura = 0,905 |
| `desgaste` | Flota: ¿qué camión no llega a su mantención? | Proceso gamma jerárquico con mediciones ruidosas y una covariable de exigencia | 5 + 2 por camión | **Sello pasa.** 15.241.472 flotas simuladas, 168 min; cobertura = 0,898 |
| `sismico` | Sismicidad: ¿se puede reingresar? | Proceso de Hawkes temporal con núcleo exponencial y magnitudes de Gutenberg-Richter, jerárquico entre sectores | 6 + 2 por sector | **Sello pasa.** 3.723.712 minas simuladas, 120 min; cobertura = 0,895 |

Los cuatro motores de series usan **amortización factorizada**, q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D)): un flujo para los parámetros globales y uno chico, compartido, para los de cada unidad (`motor/comun/series.py`). Las ecuaciones y los priors están en `WORKPLAN.md`, sección 11.

Después del posterior viene la **decisión** (`nucleo/decision.py`): con los dos costos del caso, cada unidad queda en «conviene actuar», «no hace falta» o «en duda», y «lo que cuesta no saber» es el valor esperado de la información perfecta. En `leyes`, **«¿Dónde perforo?»** estima el valor de una muestra más en cada lugar candidato rehaciendo el análisis completo para cada resultado posible: 480 análisis en un lote.

Son **versiones chicas a propósito**: en la primera noche un motor de 7 parámetros pasó su validación y uno de 32 no. Los modelos completos (dominios geológicos, tres dimensiones, ecuaciones de varias fases, ubicación de los sismos) son hoja de ruta: `pitch/MODELOS_CANDIDATOS.md`.

## Cómo se entrenó y cómo se validó

Detalle en `motor/README.md`. En corto: datasets simulados al vuelo, contados; dos MacBook Air sin ventilador; un entrenamiento por computador. Cada motor tiene un sello (`motor/artefactos/<motor>/sello.json`) con: calibración basada en simulación (SBC) y cobertura en 2.000 simulaciones nuevas, para los parámetros globales, los de cada unidad y lo que se decide, por tramos de tamaño del archivo; examen con una verdad escondida; latencia; y un semáforo que se niega a responder cuando el archivo no alcanza o cae fuera de lo simulado. Una tarjeta solo dice que respondió la red si su motor pasó su sello. Las cinco pasaron: ninguna salió precalculada.

**La comparación con el MCMC de referencia, tal como salió:**

| Motor | Segundos por dataset (NUTS) | Convergió (r̂ ≤ 1,05) | Diferencia de medias con la red, en desviaciones del MCMC | Dónde está |
|---|---|---|---|---|
| `espacial` | 117 | 6 datasets comparados (el sello no guarda su r̂) | 0,26 | En su sello |
| `cinetica` | 13,7 | 5 de 5 | 0,14 | `estado/a36_metodo_lento/` |
| `sismico` | 28,0 | 5 de 5 | 0,17 | `estado/a36_metodo_lento/` |
| `deformacion` | 63,0 | 2 de 5 | 0,38 | `estado/a36_metodo_lento/` |
| `desgaste` | 255 (solo el archivo del demo) | 1 de 5: los cuatro simulados no terminaron en 10 minutos | 0,39 en los globales; 0,07 en lo de cada camión | `estado/a36_metodo_lento/` |

Para los cuatro motores de series el MCMC se escribió y corrió al final y **no está en sus sellos**: es una propuesta por revisar. En `deformacion` y `desgaste` la referencia no convergió en todos los datasets, así que esos dos números no alcanzan para juzgar a sus redes. En modelos chicos como estos el MCMC resulta rápido (segundos a minutos por dataset); la ganancia grande de amortizar está en lo que exige rehacer el análisis muchas veces: en `espacial`, 228 análisis completos tomaron 26.699 s con el MCMC y 0,69 s con la red.

## Cómo correrlo en local

```bash
uv sync
KRYLOV_MOTOR_ESPACIAL=red KRYLOV_MOTOR_DEFORMACION=red KRYLOV_MOTOR_CINETICA=red KRYLOV_MOTOR_DESGASTE=red KRYLOV_MOTOR_SISMICO=red uv run uvicorn servicio.app:app --port 8010
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
pitch/       guion, cifras con su fuente, láminas y el deck (pitch/deck/)
yacimiento/  un sexto motor experimental, en 3D, fuera de la app (ver abajo)
AGENTS.md, WORKPLAN.md, DECISIONES.md, estado/   cómo se organizó el trabajo de tres computadores y sus agentes
```

## Qué existe y qué no

**Existe:** las cinco tarjetas responden con su red, en la app y en la URL pública (`leyes`, `taludes`, `flotacion`, `flota`, `sismicidad`); «¿Dónde perforo?» en `leyes`; subir un archivo propio y asignar sus columnas (necesita la API; el calce y el texto los propone un modelo de lenguaje, que no calcula ni pone números); el modo estático, que responde el recorrido sin servidor.

**No existe:** conexión a sensores o sistemas de una faena, los modelos completos del documento técnico, clientes ni pilotos.

**Experimental, fuera de la app (`yacimiento/`):** un sexto motor entrenado después del cierre del producto. Un yacimiento en 3D leído desde sondajes: 16.384 bloques, proceso gaussiano anisotrópico con ocho covariables, 15 parámetros; U-Net 3D con cabeza de mapa y cabeza de flujo; 126.696 yacimientos simulados. **Su sello no pasa:** el mapa por bloque está calibrado (0,901 de cobertura del 90% en 2.000 yacimientos nuevos) y coincide con el MCMC de referencia en el yacimiento del demo (misma decisión en 92% de los bloques; 913 s contra unos 20 ms), pero la cabeza de parámetros falla el SBC y no aprendió los alcances del campo. Solo se muestra su mapa, en una lámina del deck.

## Datos y licencias

- **Los archivos del demo son simulados** con las mismas ecuaciones de cada motor y parámetros que el motor no ve, con una verdad escondida aparte (`datos/preparar/`, semilla fija). La pantalla los rotula «simulado». No son datos de ninguna mina.
- Datos reales abiertos usados para probar: metales en un suelo junto al río Mosa (paquete `sp` de R, GPL); prismas de la pared de un rajo que falló (de Wit, 2025, Zenodo, https://doi.org/10.5281/zenodo.15003054, CC BY 4.0); sondajes con ley de cobre (Hoffimann et al., 2022, «GeoMet dataset», Zenodo, https://doi.org/10.5281/zenodo.7051975, CC BY 4.0). Los datos crudos no están en el repositorio; los derivados, sí, con su guion.
- Las cifras de minería que se dicen en el pitch, con su fuente, están en `pitch/CIFRAS.md`.

## Equipo

Clemente Ferrer, Franco Reinoso y Rodrigo Pizarro Alegría. Construido con Claude Code.
