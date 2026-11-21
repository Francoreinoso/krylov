---
name: agregar-caso
description: Prepara un caso de uso de Krylov (una tarjeta del inicio) sin tocar código - baja o arma el CSV, deja vacío al azar el 20% de las respuestas guardando la verdad aparte, completa el YAML y registra sus cifras. Úsala en PC 3 para rotación, terreno, crédito, inasistencias y el archivo malo. Tope de 25 minutos por caso.
argument-hint: "[nombre del caso]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Preparar un caso de uso

Rol: `seguimiento`; `producto` verifica que se ve. Un **caso de uso** es una pregunta de negocio resuelta con un motor, un archivo de datos y sus costos. Los cinco YAML ya vienen escritos en `casos/`: lo que falta es el archivo de datos y comprobar que las columnas calzan. **Tope: 25 minutos por caso.**

## Pasos

1. **Baja el archivo** desde la fuente de `WORKPLAN.md`, sección 12, a `datos/crudo/` (no se sube). Mira la licencia: el repositorio es público. Si no permite redistribuir, el CSV procesado se agrega a `.gitignore`, el caso funciona solo en local y en las respuestas precalculadas, y se anota en el estado.
2. **Escribe `datos/preparar/<caso>.py`** (pandas, semilla fija) que deja `datos/demo/<caso>.csv`:
   - Para `regresion`: el identificador, el objetivo y las columnas del YAML. **Deja vacío el objetivo en un 20% de las filas elegido al azar, sin mirar la respuesta**, y guarda esas respuestas en `datos/demo/<caso>_verdad.csv` (`id`, `objetivo`). Nunca vacíes según la respuesta: queda una sola clase y el caso se rompe.
   - Si el archivo tiene más de 2.000 filas, toma una muestra de 2.000 con la misma semilla.
   - Para `espacial`: columnas `x`, `y`, `valor`.
3. **Completa el YAML:** verifica cada nombre de columna contra el archivo real (están escritos de memoria), llena `columnas.disponibles` con la cantidad de columnas del archivo original, revisa `origen_datos`.
4. **Costos.** Cada uno necesita valor, mínimo y máximo del deslizador, etiqueta y un id de `pitch/CIFRAS.md`. Son supuestos: se dicen como supuestos.
5. **Míralo en la app** cuando el motor responda: los tres colores aparecen (no todo de un color), el semáforo no está en rojo, y el examen muestra números.
6. **Cuando exista `/api/proponer`** (tarea P-12): pasa el archivo completo y la pregunta. Si la propuesta de columnas es razonable, reemplaza `factores` y pon `elegidas_por: krylov`. Si no, deja `equipo`: la pantalla no dirá que Krylov las eligió.

## Si los colores no dicen nada

- Todo de un color: mira dónde queda el punto de corte respecto de la tasa real de «sí». Mueve los costos por defecto a valores que puedas defender en voz alta y registra el cambio. No los ajustes para que el número se vea más grande.
- Todo en duda: pocos datos. Prueba con más filas.

## Si lleva el nombre de un sponsor

En pantalla dice «caso tipo Buk · datos públicos de ejemplo». Es una hipótesis de uso: no se afirma cómo trabaja esa empresa ni que los datos son suyos. Si en el lugar se confirma que la empresa no auspicia, `tarjeta.sponsor` pasa a `null`.

## Terminado cuando

El CSV, la verdad y el script están subidos (o anotados como no publicables), el YAML calza con el archivo y las cifras tienen fila en `pitch/CIFRAS.md`.
