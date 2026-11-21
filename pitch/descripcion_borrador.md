# Borrador de `project-description.md` (S-N3)

> **Borrador para que lo lea una persona.** Se muestra en la página de votación, junto al video y la URL. Sin jerga (`GLOSARIO.md`). Los corchetes son cifras sin medir: se llenan desde `pitch/CIFRAS.md` o se borra la frase. Cambios respecto del archivo actual de la raíz: dice qué hace hoy, qué se simuló y qué no existe; saca «lo que hoy le toma minutos a un especialista», que todavía no está medido (M-25).

---

# Krylov

**Un data scientist artificial.** Le das un archivo de datos y una pregunta de negocio, y te dice qué conviene hacer, **cuánto te cuesta no saber** y **dónde conviene averiguar más**. Y avisa cuando los datos no sirven.

**Pruébalo:** https://krylov-tan.vercel.app/

## Qué hace hoy

Cuatro preguntas, cada una con datos públicos:

- **¿A quién conviene retener?** Una empresa de 1.470 personas (datos de ejemplo de IBM).
- **¿Dónde limpio y dónde mido?** Un terreno real con 155 mediciones de zinc junto a un río. Krylov marca qué limpiar, dónde no se sabe y los tres lugares donde una medición más vale más plata.
- **¿Qué citas conviene confirmar?** Citas médicas reales de Brasil.
- **¿A quién le apruebo el crédito?** Clientes de tarjetas de crédito reales de Taiwán.

En cada una, las respuestas son decisiones en tres colores (conviene actuar, no hace falta, no sabemos si conviene), con los costos en deslizadores que cambian la respuesta en vivo.

## Qué simulamos

Para cada pregunta escribimos las reglas con que Krylov inventa empresas, carteras o terrenos parecidos a los reales, incluidas las cosas que no se ven en los datos. Krylov practicó con [N] millones de casos simulados, donde la respuesta correcta se conoce, y por eso responde en [milisegundos] lo que el método lento de siempre calcula en [minutos]. Lo comprobamos de tres formas: en casos simulados nuevos, contra el método lento, y escondiendo respuestas reales que Krylov no vio: [resultado del examen].

## Qué no es

No es un chat con un archivo: dentro de la app no hay ningún modelo de lenguaje. Cada número sale de un modelo que dice cuánto se puede equivocar. Los casos con nombre de empresa son hipótesis de uso con datos públicos.

## Por qué se llama así

Por Alekséi Krylov, ingeniero naval que a comienzos del 1900 calculó por adelantado qué hacer con un barco averiado, para que el capitán decidiera en segundos. Calcular antes, decidir al instante.

## Equipo

[Nombres: los confirma cada persona antes de publicarlos.] Platanus Hack 26, Santiago, track Simulaciones.
