---
name: registrar-cifra
description: Registra en pitch/CIFRAS.md un número que se va a mostrar en pantalla, en una lámina o en el guion, con su tipo (medido, fuente o hipótesis) y su origen. Úsala cada vez que aparezca una cifra nueva que verá el jurado, incluidos los costos de cada caso de uso y los resultados que el guion tiene entre corchetes.
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

## Reglas

- **Lo que se dice en voz alta sobre exactitud sale del examen con datos reales**, no de simulaciones. La exactitud en simulaciones va en la lámina técnica.
- Una comparación de tiempos dice exactamente qué se comparó: «rehacer N análisis con el método lento de siempre tomó M minutos en este computador». Nunca se elige un rival lento a propósito.
- Las cifras de un sponsor (clientes, usuarios, reservas) solo con fuente pública y enlace. Nunca de memoria.
- Los costos de un caso sin fuente van como hipótesis y la app los muestra como supuestos, en deslizadores.
- Un cálculo sobre otras cifras se anota como cálculo y nombra las filas de las que sale.
- La columna «Verificó» vacía significa que todavía no puede ir en una lámina.

## Terminado cuando

La fila existe, está subida, y quien la pidió tiene el id.
