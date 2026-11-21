# Borrador de `project-description.md` (S-30)

> **Borrador para que lo lea una persona.** Se muestra en la página de votación, junto al video y la URL. Sin jerga, ni estadística ni minera (`GLOSARIO.md`). Los corchetes son cosas que se fijan el sábado a las 20:30 con la tabla «Los cinco casos» del tablero: se llenan con lo que de verdad responde, o se borra la frase.

---

# Krylov

**El data scientist artificial de la minería.** Le das los datos de una decisión de la mina y te dice qué conviene hacer, **cuánto te cuesta no saber** y **dónde conviene medir más**. Y avisa cuando los datos no alcanzan.

**Pruébalo:** https://krylov-tan.vercel.app/

## El problema

En una mina las decisiones grandes no esperan: a dónde va la roca que se acaba de romper, si un sector se cierra, qué camión se detiene. Los modelos que de verdad miden el riesgo tardan horas, y hay que rehacerlos con cada dato nuevo. Hoy se elige entre un promedio rápido que esconde el riesgo y un cálculo serio que llega tarde.

## Qué hace hoy

- **¿Este bloque de roca va a la planta o se aparta?** Un piso de la mina en tres colores (puede ir a la planta, conviene apartarlo, no sabemos), con lo que cuesta no saber y **«¿Dónde perforo?»**: los tres lugares donde una muestra más vale más plata. Responde al instante.
- **¿Es ruido o el muro va a ceder?** [responde al instante / calculado antes con el método lento]
- **¿Se me está yendo cobre?** [ídem]
- **¿Qué camión paro antes de que falle?** [ídem, o se borra]
- **¿Puede volver a entrar la gente?** [ídem, o se borra]

En cada una, los colores son decisiones y los costos están en deslizadores que cambian la respuesta en vivo.

## Qué simulamos

Para cada decisión escribimos las reglas con que Krylov inventa minas parecidas a las reales. Practicó con millones de casos simulados, donde la respuesta correcta se conoce, y por eso responde en un segundo lo que el método lento de siempre calcula en horas: rehacer 228 análisis toma más de siete horas con el método lento y menos de un segundo con Krylov.

## Qué no es

No reemplaza al especialista: le entrega a tiempo el cálculo que hoy llega tarde. Los archivos del demo son simulados con la misma física, y la pantalla lo dice; el motor del mapa está probado además con datos reales públicos. No es un chat con un archivo: cada número sale de un modelo que dice cuánto se puede equivocar.

## Por qué se llama así

Por Alekséi Krylov, ingeniero naval que a comienzos del 1900 calculó por adelantado qué hacer con un barco averiado, para que el capitán decidiera en segundos. Calcular antes, decidir al instante.

## Equipo

[Nombres: los confirma cada persona antes de publicarlos.] Platanus Hack 26, Santiago, track Simulaciones.
