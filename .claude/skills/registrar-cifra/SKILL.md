---
name: registrar-cifra
description: Registra en pitch/CIFRAS.md un número que se va a mostrar en pantalla, en una lámina o en el guion, con su tipo (medido, fuente o hipótesis) y su origen. Úsala cada vez que aparezca una cifra nueva que verá el jurado, incluidos los costos de cada caso de uso, las cifras de minería con fuente (ids I-xx, que firma una persona) y los resultados que el guion tiene entre corchetes.
argument-hint: "[qué cifra]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Registrar una cifra

Rol: cualquiera propone; `seguimiento` escribe en `pitch/CIFRAS.md`. Regla del proyecto: **un número sin fila ahí no se muestra.**

## Pasos

1. Clasifica:
   - `medido`: lo medimos nosotros. Anota máquina, hora y el comando que lo reproduce.
   - `fuente`: tiene enlace. Alguien abrió la página y vio el número.
   - `hipótesis`: supuesto nuestro. En pantalla y en voz alta se dice que lo es.
2. Si eres `seguimiento`, agrega la fila: id, cifra, valor, tipo, origen, quién verificó. Si no, pídelo en «Pedidos a otros» de tu estado con esos datos.
3. Usa el id en el caso (`casos/<nombre>.yaml`) o reemplaza el corchete en `pitch/GUION.md`.

## Las cifras de minería (`I-xx`)

Son los datos del rubro que el pitch usa para decir por qué importa cada decisión: cuánto dura un cierre, cuánto cuesta un camión detenido, cuánto castiga el arsénico. Van en la sección «La minería», con ids `I-01` en adelante, tipo `fuente` y su enlace.

- **Una persona abre cada fuente y firma la columna «Verificó»** (tarea S-25). Que la haya leído un agente sirve para trabajar, no para una lámina. Lo que no se pueda abrir sale del guion.
- **Los números del documento técnico del equipo no se usan si no tienen fila.** Varios no resistieron la revisión de fuentes; la lista de los que no se usan está en D-37 y en el tablero.
- Los nombres propios (una minera, una faena, un accidente) aparecen solo aquí, en cifras con fuente, nunca en una tarjeta. Un accidente se cita en una frase sobria o no se cita (reglas 10 y 22).

## Reglas

- **Lo que se dice en voz alta sobre exactitud sale del examen**, no de la calibración en simulaciones, que va en la lámina técnica. Si el examen se hizo con la verdad escondida de un archivo simulado, se dice «con datos simulados»; «con datos reales» solo donde los hubo.
- Una comparación de tiempos dice exactamente qué se comparó: «rehacer N análisis con el método lento de siempre tomó M minutos en este computador». Nunca se elige un rival lento a propósito.
- Los costos de un caso sin fuente van como hipótesis y la app los muestra como supuestos, en deslizadores.
- Un cálculo sobre otras cifras se anota como cálculo y nombra las filas de las que sale.
- La columna «Verificó» vacía significa que todavía no puede ir en una lámina.

## Terminado cuando

La fila existe, está subida, y quien la pidió tiene el id.
