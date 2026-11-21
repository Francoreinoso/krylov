---
name: preparar-demo
description: Revisa que el demo de Krylov está listo para mostrarse - recorrido completo, URL pública en modo estático, modo sin internet, video de respaldo y el computador que presenta. Úsala en PC 1 antes de cada ensayo, de grabar el video y de subir al escenario, y en cada vuelta de la fase de iteración del sábado de 18:00 a 22:00.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Preparar el demo

Rol: `producto` (PC 1); verifica `seguimiento`. Quince minutos.

## Fase de iteración (sáb 18:00 a 22:00)

El producto ya está terminado. El ciclo es: **ensayo → una mejora → ensayo**. En cada vuelta se elige UNA cosa de la lista que dejó el ensayo.

Se puede cambiar: textos, orden de las tarjetas, colores, tamaños, velocidad de las animaciones, valores por defecto de los deslizadores, errores.
No se puede: funciones nuevas, vistas nuevas, cambios al contrato, reentrenar.

## Lista

**El recorrido** (`WORKPLAN.md`, sección 4.3)
1. Las cuatro tarjetas cargan. Cada una dice de dónde vienen sus datos.
2. Rotación responde en menos de 2 segundos, tres veces seguidas, con los mismos números (semilla fija).
3. Mover un deslizador de costos cambia colores y «lo que te cuesta no saber» sin espera.
4. Tecla `M`: aparece la nube con el archivo fuera, el motivo y la corrección. Un clic y pasa a verde.
5. Tecla `T`: el mapa del terreno en tres colores, con las mediciones.
6. «¿Dónde mido?»: tres pines con plata y el conteo de análisis rehechos. Clic en un pin, elegir un resultado, y el mapa cambia. En menos de 2 segundos.
7. Cartera: el contador y la tabla.
8. Tecla `L`: lámina de cierre con la frase y el QR.

**Lo que se lee**
9. Ningún término de la columna izquierda de la tabla de jerga del glosario aparece en pantalla.
10. Los rótulos son decisiones («conviene retener»), nunca pronósticos («se va»).
11. Todo lo simulado dice «simulado». Toda tarjeta de sponsor dice «caso tipo … · datos públicos de ejemplo». Los costos dicen «supuesto».
12. Cada cifra en pantalla tiene fila en `pitch/CIFRAS.md`.

**Sin red y en público**
13. Con el wifi apagado, el recorrido completo funciona igual.
14. La URL pública con `?estatico=1` hace el recorrido desde un teléfono.

**El computador que presenta**
15. Cargador conectado, brillo al máximo, notificaciones apagadas, no molestar.
16. Navegador en pantalla completa, zoom para que se lea desde el fondo, una sola ventana.
17. El video de respaldo abierto en la pestaña de al lado, sin sonido. Adaptador de video probado.

## Si algo falla

Lo que no pasa se arregla o se saca del guion. No se muestra nada que no haya pasado esta lista.

## Terminado cuando

Los diecisiete puntos están marcados en `estado/producto.md` con la hora.
