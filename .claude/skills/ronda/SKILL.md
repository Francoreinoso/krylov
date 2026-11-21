---
name: ronda
description: Ronda de seguimiento de Krylov. Baja los cambios, lee los tres estados, verifica corriendo lo que cada computador dice haber terminado, pone al día en el TABLERO la tabla de los cinco casos (contra el sello de cada motor) y la siguiente tarea de cada rol, ajusta el plan si algo se atrasó y pone al día el guion con lo que de verdad existe. Úsala en PC 3 cada 30 a 45 minutos (por ejemplo con /loop 30m /ronda) y cada vez que otro computador avise que terminó algo.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Ronda de seguimiento

Rol: `seguimiento` (PC 3). Diez minutos como máximo. Es el trabajo principal de PC 3: que los otros dos computadores siempre sepan qué sigue, y que el pitch nunca prometa algo que no está construido. (No confundir con la ronda de entrenamiento.)

## Pasos

1. `date "+%a %H:%M"` y `git pull --rebase`.
2. **Lee** `estado/producto.md` y `estado/amortizacion.md`: qué pasó a «Hecho» desde la ronda anterior (cada línea empieza con el identificador de su tarea), qué bloqueos y qué pedidos hay.
3. **Verifica corriendo, no leyendo.** Por cada tarea que pasó a «Hecho», ejecuta su comando o abre la app y míralo. Si no funciona como dice, vuelve a «En curso» en el tablero, con el motivo.
4. **Compara con el reloj.** Busca la tarea en `WORKPLAN.md`, sección 6. Si lleva el doble de su duración, aplica la regla: se corta o se simplifica. Propón el recorte concreto (qué se saca, qué queda) y escríbelo.
5. **Atiende pedidos.** Los que son para ti (un dato, un texto, una cifra), hazlos ahora. Los que son entre los otros dos, cópialos al tablero para que se vean.
6. **Pon al día la tabla «Los cinco casos»** de `estado/TABLERO.md`, una fila por caso (`leyes`, `taludes`, `flotacion`, `flota`, `sismicidad`):
   - Las celdas de Datos, Simulador, Método lento, Red, Sello y En la app solo admiten `listo`, `en curso`, `pendiente`, `no pasa` o `cortado`. La columna «Responde» solo admite `red`, `precalculado`, `ejemplo` o `nada`. El tablero en vivo lee esas palabras tal cual.
   - **Contrasta con `motor/artefactos/<motor>/sello.json`:** «Sello» es `listo` solo si el archivo existe y dice `"pasa": true`; si dice `false`, `no pasa`; si no existe, `pendiente` o `en curso`. «Responde» es `red` solo con el sello en `listo`. Lo que diga un estado no basta.
   - Una tarjeta fuera del inicio queda en `cortado` y responde `nada`.
7. **Escribe el resto del tablero** (todo el archivo bajo 50 líneas): semáforo por rol, **la siguiente tarea de cada rol con su identificador** y la que viene después, qué cambió respecto del plan y la próxima decisión.
8. **Pon al día el relato.** Abre `pitch/GUION.md`:
   - Cada corchete cuya cifra ya está medida y registrada se reemplaza por el número.
   - Cada frase que describe algo que se cortó o cambió se reescribe ahora, no en la noche.
   - De cada tarjeta se dice quién responde de verdad, según la columna «Responde». Si un motor no pasó su sello, la frase cuenta lo que pasó («esta la calculamos con el método lento»). Eso suele ser mejor historia.
9. Si cambiaste horarios, alcance o el orden del show: edita `WORKPLAN.md` y agrega una entrada en `DECISIONES.md`.
10. Anota la ronda en `estado/seguimiento.md` (sección «Rondas») y sube: `git add -A estado pitch WORKPLAN.md DECISIONES.md && git commit -m "ronda HH:MM" && git pull --rebase && git push`.
11. Avisa en voz alta a quien le cambió algo.

## Reglas

- No edites `servicio/`, `web/`, `nucleo/` ni `motor/`. Si ves un error ahí, va como pedido en el tablero.
- No muevas las 18:00 ni los hitos.
- Si los dos estados llevan más de una hora sin cambios y no es hora de dormir, pregunta en voz alta antes de asumir nada.

## Terminado cuando

El tablero está subido con la hora de ahora, la tabla «Los cinco casos» coincide con los sellos y cada rol tiene escrita su siguiente tarea.
