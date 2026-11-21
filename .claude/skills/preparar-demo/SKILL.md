---
name: preparar-demo
description: Revisa que el demo de Krylov está listo para mostrarse - el recorrido de las cinco decisiones de la mina con sus teclas, URL pública en modo estático, modo sin internet, video de respaldo y el computador que presenta. Úsala en PC 1 antes de cada ensayo, de grabar el video y de subir al escenario, y en cada vuelta de la fase de iteración del sábado de 18:00 a 22:00.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Preparar el demo

Rol: `producto` (PC 1); verifica `seguimiento`. Quince minutos.

## Fase de iteración (sáb 18:00 a 22:00)

El producto ya está terminado. El ciclo es: **ensayo → una mejora → ensayo**. En cada vuelta se elige UNA cosa de la lista que dejó el ensayo.

Se puede cambiar: textos, orden de las tarjetas, colores, tamaños, velocidad de las animaciones, valores por defecto de los deslizadores, errores. Y, hasta las 20:30, quién responde una tarjeta: si PC 2 pasa un motor a `red`, se regenera su estático, se comprueba el rótulo y se redespliega (P-30).
No se puede: funciones nuevas, vistas nuevas, motores nuevos, cambios al contrato.

## Lista

**El recorrido** (`WORKPLAN.md`, sección 4.3)
1. Se abre el chat con las decisiones que siguen en el inicio y sus archivos del demo precargados. Cada tarjeta dice de dónde vienen sus datos.
2. Tecla `1`: `leyes`. El mapa del banco en tres colores, el número grande y los deslizadores, en menos de 1 segundo, tres veces seguidas y con los mismos números (semilla fija).
3. Arrastrar el deslizador «mandar a la planta un bloque con demasiado arsénico» cambia colores, titular y «lo que te cuesta no saber» sin espera.
4. Tecla `D`: «¿Dónde perforo?». Tres pines con plata y el conteo de análisis rehechos, en menos de 2 segundos.
5. Clic en el pin A y en uno de los tres resultados: el mapa, el número y los pines cambian, en menos de 2 segundos.
6. Teclas `2`, `3`, `4` y `5`: taludes, flotación, flota y sismicidad. Cada una, en menos de 1 segundo, muestra su lista en tres colores y la curva de la unidad abierta, con el abanico y la línea del límite; en taludes, además, «cuánto falta» con su rango. La tecla de una tarjeta que salió del inicio no hace nada.
7. Tecla `M`: un archivo que no alcanza. Banda roja con el motivo en una línea, en menos de 1 segundo.
8. Tecla `L`: lámina de cierre con la frase y el QR.

**Lo que se lee**
9. Ningún término de la columna izquierda de la tabla de jerga del glosario aparece en pantalla, y ninguna palabra minera aparece sin su explicación la primera vez (`GLOSARIO.md`, «Minería en simple»).
10. Los rótulos son decisiones («conviene apartar», «conviene adelantar su mantención»), nunca pronósticos («este camión falla»). En taludes y sismicidad nada promete evitar accidentes.
11. Todo lo simulado dice «simulado», el examen dice «con datos simulados» y los costos dicen «supuesto». Ninguna tarjeta lleva el nombre de una minera, de una faena ni de un sponsor. El pie de cada respuesta dice quién respondió: «precalculado» si su motor no pasó `validar-motor`.
12. Cada cifra en pantalla tiene fila en `pitch/CIFRAS.md`.

**Sin red y en público**
13. Con el wifi apagado, el recorrido completo funciona igual.
14. La URL pública con `?estatico=1` hace el recorrido desde un teléfono.

**El computador que presenta**
15. Cargador conectado, brillo al máximo, notificaciones apagadas, no molestar.
16. Navegador en pantalla completa, zoom para que se lea desde el fondo, una sola ventana.
17. El video de respaldo abierto en la pestaña de al lado, sin sonido. Adaptador de video probado.

## Si algo falla

Lo que no pasa se arregla o se saca del guion. No se muestra nada que no haya pasado esta lista. Una tarjeta de las teclas `2` a `5` que no carga se salta: ninguna depende de otra. El mapa de `leyes` y «¿Dónde perforo?» no se saltan: si tardan más de 2 segundos, se sirve el resultado precalculado.

## Terminado cuando

Los diecisiete puntos están marcados en `estado/producto.md` con la hora.
