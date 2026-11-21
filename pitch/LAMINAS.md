# Láminas · deck minero (S-27)

> Versión del pivote a minería (D-37, sáb 12:30). El pitch parte en el deck (`pitch/deck/index.html`), entra a la app para las decisiones y vuelve al deck para el cierre. Las palabras de cada momento están en `pitch/GUION.md`; aquí está **qué muestra cada lámina y qué hay que cambiarle al deck que ya existe**. Cada número lleva su id de `pitch/CIFRAS.md`; los corchetes no se muestran hasta medirlos. Sin jerga, ni estadística ni minera (`GLOSARIO.md`); la lámina técnica sí usa los nombres técnicos.
>
> Para distinguir **lo construido de lo que es lámina** (regla 17): lo que no responde en la app lleva en pantalla el rótulo «hoja de ruta» o «precalculado», según corresponda.

## Qué cambia en el deck, en una tabla

El deck de antes del pivote tiene nueve láminas y una de respaldo. **Seis sirven casi tal cual**, porque ya contaban el motor espacial. El trabajo de S-27, en orden de prioridad:

| # | Lámina | Estado | Qué hay que hacer | Min |
|---|---|---|---|---|
| 1 | Apertura: el barco | **Sirve.** | Cambiar el titular final: «Calcular antes. Decidir al instante.» se queda; debajo, «Eso hicimos para una mina.» | 5 |
| 2 | El problema: la carrera | **Sirve.** | Cambiar la frase de entrada: «En una mina las decisiones grandes no esperan. Los modelos que miden el riesgo tardan horas.» Los números (228 análisis, 0,69 s, 7 h 24 min) no cambian: M-08, M-09, M-10 | 10 |
| 3 | Millones de casos simulados | **Sirve.** | Sin cambios de datos (7.750.592 terrenos, M-01; 280 min, M-02). El rótulo sigue diciendo «terrenos simulados» | 0 |
| 4 | El mapa | **Cambiar los datos.** | Regenerar `datos/datos.js` con el caso `leyes` en vez de `terreno` (`pitch/deck/datos/generar.py`: cambiar el nombre del caso). Altura = arsénico estimado; colores = «puede ir a la planta», «conviene apartar», «no sabemos»; puntos = los 340 pozos. Rótulos: «banco simulado» y «costos supuestos». Número: US$ 1.577.707 (M-41) | 20 |
| 5 | ¿Dónde perforo? | **Cambiar los datos y el título.** | Los tres pines del caso `leyes` (M-46: US$ 8.943, 8.376 y 7.967), «480 análisis rehechos» (M-43) y el tiempo solo cuando esté medido limpio (M-44). El mapa rehecho sale de `api.analizar("leyes", mediciones=[…])` | 15 |
| 6 | **Nueva: cinco decisiones** | **Hacer.** Reemplaza a «Sabe cuando no sabe» (la nube era de rotación) | Cinco tarjetas en una fila, cada una con un dibujo simple, su pregunta y su estado real: «responde al instante», «precalculado» u «hoja de ruta». Texto de cada tarjeta, abajo. Si no hay tiempo para animarla: estática | 30 |
| 7 | Cierre | **Sirve.** Era la 9 | La frase con «minas simuladas», el QR y «Lo construimos con Claude Code» | 5 |
| — | Visión (era la 7) y Negocio (era la 8) | **Salen de los 3 minutos.** | La de visión hablaba de minería, clima y plataformas como hoja de ruta: ya no aplica. La de negocio era de plataformas con miles de empresas: ya no aplica. Se borran o quedan fuera del recorrido | 5 |
| 0 | Respaldo técnico (tecla `0`) | **Actualizar.** | La ficha del motor espacial no cambia. La tabla «los otros motores» pasa a ser la de los cuatro motores nuevos con su estado real a las 20:30 | 15 |

Después de cambiar las láminas: rehacer el respaldo en PNG y PDF (`pitch/deck/respaldo/capturar.mjs`) y poner al día `pitch/deck/README.md`.

**Si S-27 no alcanza:** las láminas 1, 2, 3 y 7 con los cambios de texto bastan; los momentos 4 a 6 se hacen completos en la app, que es donde mejor se ven.

## Lámina 6 · Cinco decisiones (texto)

Titular: **«Una mina decide esto todos los días.»** Bajada: «La misma idea: calcular antes, decidir al instante.»

| Tarjeta | Dibujo | Pregunta | Una línea |
|---|---|---|---|
| 1 | Una grilla de bloques en tres colores | ¿Este bloque va a la planta o se aparta? | Y dónde tomar una muestra más |
| 2 | Una pared con un tramo que se curva | ¿Es ruido o el muro va a ceder? | Cuánto falta, con su rango |
| 3 | Burbujas subiendo | ¿Se me está yendo cobre? | Lo dice mirando solo el principio de la línea |
| 4 | Un camión en una subida | ¿Qué camión paro antes de que falle? | Antes de su próxima mantención |
| 5 | Un túnel con ondas | ¿Puede volver a entrar la gente? | En qué sectores conviene esperar |

Debajo de cada tarjeta, su estado, leído de la tabla «Los cinco casos» de `estado/TABLERO.md` el sábado a las 20:30: «responde al instante» (verde), «precalculado» (ámbar) u «hoja de ruta» (gris). **No se escribe a mano algo distinto de lo que diga el tablero.**

## Portada y cierre dentro de la app (tecla `L`, PC 1, P-28)

**Portada.** «Krylov» · «El data scientist artificial de la minería» · *(chico)* Platanus Hack 26 · track Simulaciones.

**Cierre.** «Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo.» · «En un segundo, porque ya practicó con millones de minas simuladas.» · QR a **https://krylov-tan.vercel.app/** con la leyenda «Escanea y mueve los costos tú» · Equipo: [nombres, cuando cada persona confirme que se pueden mostrar] · Pie chico: «Construido con Claude Code».

**Por confirmar antes de decir «millones de minas simuladas»:** hoy lo sostiene M-01 (7.750.592 terrenos del motor espacial). Los motores nuevos suman lo suyo (M-48). Si alguien pregunta «¿minas?»: «terrenos, muros, plantas, flotas y sectores simulados; el número exacto de cada uno está en la lámina técnica».

## Respaldo técnico (tecla `0`; nombres técnicos)

**Krylov: inferencia basada en simulación amortizada, caso por caso.** Por motor: un modelo bayesiano generativo explícito, un simulador vectorizado, una red entrenada solo con simulaciones (NPE con flujos normalizadores condicionales) y un MCMC de referencia (NumPyro, NUTS). En los motores jerárquicos, amortización factorizada: q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D)).

| Motor | Decisión | Modelo en una línea | Parámetros | Entrenamiento | Sello | Responde |
|---|---|---|---|---|---|---|
| `espacial` | Leyes y arsénico | Proceso gaussiano anisotrópico con tendencia opcional y error de medición; red convolucional con cabeza de mapa y cabeza de flujo | 7 | 7.750.592 terrenos, 280 min, MacBook Air M4 (M-01, M-02) | PASA: cobertura del 90% = 0,90; 0,26 desviaciones contra el MCMC (M-28) | Red |
| `deformacion` | Taludes y relaves | Mezcla por sector: fluencia estable o acelerada (velocidad inversa), jerárquica | 7 + 2 por sector | [M-48] | [M-49] | [M-52] |
| `cinetica` | Flotación | Cinética de primer orden con fracción rápida y lenta, jerárquica entre líneas, observada en las primeras celdas | 6 + 2 por línea | [M-48] | [M-49] | [M-52] |
| `desgaste` | Flota | Proceso gamma jerárquico con mediciones ruidosas y covariable de exigencia | 5 + 2 por camión | [M-48] | [M-49] | [M-52] |
| `sismico` | Sismicidad | Hawkes temporal con núcleo exponencial y magnitudes de Gutenberg-Richter, jerárquico entre sectores | 6 + 2 por sector | [M-48] | [M-49] | [M-52] |

- **«¿Dónde perforo?»:** rehace el análisis completo 480 veces (M-43) en [M-44]. En el terreno real: 228 análisis en 0,69 s contra 26.699 s con el MCMC (M-08 a M-10; las 7 horas son 228 × 117 s).
- **Examen con datos reales del motor espacial:** 24 de 31 mediciones escondidas dentro del rango de 90% (M-13: 77%). Con sondajes reales de cobre: [M-47, si se repite la medición].
- **Qué no hace todavía:** tres dimensiones; dominios geológicos; más de 400 muestras por banco; el muro completo; ecuaciones de varias fases; telemetría; ubicación de los sismos; conexión a sensores.

## Respaldo: qué existe hoy y qué es hoja de ruta

| Existe (se ve en la app) | Hoja de ruta (solo lámina) |
|---|---|
| App en línea con las decisiones que respondan, también sin servidor | Conexión a los sistemas de una faena |
| `leyes`: red validada, mapa, «¿Dónde perforo?» y la muestra simulada | Tres dimensiones, dominios geológicos, cobre y arsénico a la vez |
| `taludes` y `flotacion`: red validada si pasó; si no, «precalculado». **Se dice cuál** | El muro completo; ecuaciones de varias fases |
| `flota` y `sismicidad`: red, «precalculado» o fuera. **Se dice cuál** | Telemetría de la flota; ubicación de cada sismo |
| Archivos del demo simulados con verdad escondida, rotulados | Datos de una faena; clientes; pilotos; precios |

Se llena el sábado a las 20:30 con lo que de verdad quedó; lo que no esté, pasa a la columna derecha.

## Respaldo de negocio (solo si preguntan)

- **Por qué minería:** casi una de cada cuatro toneladas de cobre del mundo sale de Chile (I-01); la minería es el 13% del PIB y el 59% de las exportaciones (I-02).
- **Lo que vale decidir mejor:** un punto de recuperación en la planta más grande son unos US$ 170 millones al año (I-14, estimación nuestra); en 2013 un radar avisó siete horas antes del mayor deslizamiento minero registrado y no hubo heridos (I-09).
- **Qué se vendería:** una decisión a la vez, a quien la toma todos los días. Sin precio todavía; no hay clientes ni conversaciones.
- **Lo que todavía no es ventaja:** la técnica es pública. Hoy la ventaja es el equipo y llegar primero. Se dice así.
