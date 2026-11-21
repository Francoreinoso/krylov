---
name: agregar-caso
description: Prepara un caso de uso de Krylov (una tarjeta del inicio) sin tocar código - baja o arma el CSV, deja vacío al azar el 20% de las respuestas guardando la verdad aparte, comprueba que cada columna cumple su papel en el modelo del motor, completa el YAML y registra sus cifras. Úsala en PC 3 para rotación, terreno, crédito, inasistencias y el archivo malo. Tope de 25 minutos por caso.
argument-hint: "[nombre del caso]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Preparar un caso de uso

Rol: `seguimiento`; `producto` verifica que se ve. Un **caso de uso** es una pregunta de negocio resuelta con un motor, un archivo de datos y sus costos. Los cinco YAML ya vienen escritos en `casos/`, con las columnas **por papel en el modelo generativo del motor** (`WORKPLAN.md`, sección 11; decisión D-26): lo que falta es el archivo de datos y comprobar que las columnas calzan. **Tope: 25 minutos por caso.**

## Pasos

1. **Baja el archivo** desde la fuente de `WORKPLAN.md`, sección 12, a `datos/crudo/` (no se sube). Mira la licencia: el repositorio es público. Si no permite redistribuir, el CSV procesado se agrega a `.gitignore`, el caso funciona solo en local y en las respuestas precalculadas, y se anota en el estado.
2. **Escribe `datos/preparar/<caso>.py`** (pandas, semilla fija) que deja `datos/demo/<caso>.csv`:
   - **Conserva todas las columnas que el YAML nombra**, con su papel: en rotación, `tiempo`, `evento`, `grupo`, `efectos`, `suave` y las cuatro `encuestas`; en crédito, los seis meses de `atraso`, `saldo` y `pago`, más `cupo` y `transiciones`. Si falta una, el motor no puede responder.
   - **Deja vacía la respuesta (`evento` u `objetivo`) en un 20% de las filas elegido al azar, sin mirar la respuesta**, y guarda esas respuestas en `datos/demo/<caso>_verdad.csv` (`id`, `objetivo`). Nunca vacíes según la respuesta: el caso se rompe.
   - **Rotación y crédito:** si el archivo tiene más de 2.000 filas, toma una muestra de 2.000 filas al azar con la misma semilla.
   - **Inasistencias: nunca filas sueltas.** Se eligen 30 barrios con semilla fija y, dentro de ellos, **pacientes completos** (todas sus citas) hasta unas 2.000 citas, cuidando que al menos un tercio de los pacientes tenga 2 o más. El script calcula `dias_de_espera` y `dia_semana`, y descarta las esperas negativas y los sábados. Muestrear filas rompe la estructura de paciente y de barrio que el modelo necesita.
   - **Terreno:** columnas `x`, `y`, `valor` y `dist` (la distancia al río). Además hay que bajar `meuse.grid`, del mismo paquete, y dejarlo como `datos/demo/terreno_grilla.csv` (`x`, `y`, `dist` por celda): la tendencia se necesita en cada bloque, no solo en los 155 puntos. Si no está a las 04:30, avisa a PC 2: el motor arranca sin tendencia.
   - **Archivo malo:** rotación más la columna `fecha_salida`, declarada en `extra`. No entra a la red: la detecta la nube.
3. **Completa el YAML:** verifica cada nombre de columna contra el archivo real (se revisaron contra los CSV crudos el 21-nov, pero se vuelve a comprobar), llena `columnas.disponibles` con la cantidad de columnas del archivo original, revisa `origen_datos`.
4. **Costos.** Cada uno necesita valor, mínimo y máximo del deslizador, etiqueta y un id de `pitch/CIFRAS.md`. Son supuestos: se dicen como supuestos.
5. **Míralo en la app** cuando el motor responda: los tres colores aparecen (no todo de un color), el semáforo no está en rojo, y el examen muestra números.

No hay capa de lenguaje que proponga columnas (se cortó con D-26): `elegidas_por` queda en `equipo`.

## Si los colores no dicen nada

- Todo de un color: mira dónde queda el punto de corte respecto de la tasa real de «sí». Mueve los costos por defecto a valores que puedas defender en voz alta y registra el cambio. No los ajustes para que el número se vea más grande.
- Todo en duda: pocos datos. Prueba con más filas, dentro del rango de n que el motor conoce (`WORKPLAN.md`, sección 11).

## Si lleva el nombre de un sponsor

En pantalla dice «caso tipo Buk · datos públicos de ejemplo». Es una hipótesis de uso: no se afirma cómo trabaja esa empresa ni que los datos son suyos. Si en el lugar se confirma que la empresa no auspicia, `tarjeta.sponsor` pasa a `null`.

## Terminado cuando

El CSV, la verdad y el script están subidos (o anotados como no publicables), el YAML calza con el archivo y las cifras tienen fila en `pitch/CIFRAS.md`.
