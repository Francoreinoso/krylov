---
name: punto-de-control
description: Corre un hito del plan de Krylov (h0, h1, h2, h3, congelado, entrega). Lee los tres estados, los compara con el criterio escrito en WORKPLAN.md, decide seguir o cortar, escribe el TABLERO y DECISIONES y pone el tag. Úsala en PC 3 a la hora de cada hito.
argument-hint: "[h0 | h1 | h2 | h3 | congelado | entrega]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Hito

Rol: `seguimiento` (PC 3). Un **hito** es una hora fija en que se mide contra un criterio escrito y se decide seguir o cortar. Quince minutos. Sin reunión larga: se mira, se decide, se anota.

## Hitos

| Hito | Hora | Tiene que existir |
|---|---|---|
| `h0` | sáb 03:45 | Los tres empujan a los dos repositorios; contrato congelado; la web muestra un ejemplo fijo |
| `h1` | sáb 08:45 | Entrenamiento con puntos de guardado; URL pública viva; trabajo nocturno de los agentes revisado |
| `h2` | sáb 12:15 | Respuesta de rotación con datos reales; mapa del terreno; «¿Dónde mido?» calculando; red validada o plan B decidido |
| `h3` | sáb 15:00 | Recorrido completo, dos veces seguidas, en la URL pública y sin internet |
| `congelado` | sáb 18:00 | **Producto terminado.** Nada nuevo entra |
| `entrega` | dom 08:00 | Repositorio completo, descripción, logo, URL pública |

Los criterios exactos y qué hacer si fallan están en `WORKPLAN.md`, sección 6.5.

## Pasos

1. Corre primero la skill `ronda`.
2. **Verifica corriendo:** abre la URL pública desde un teléfono y recorre lo que el hito pide. Comprueba que el último commit está en los dos repositorios: `git ls-remote origin main` y `git ls-remote https://github.com/Silent-math/krylov.git main` dan el mismo identificador.
3. Compara con el criterio de `WORKPLAN.md` para ese hito. Por cada punto: pasa o no pasa.
4. **Si algo no pasa:** aplica el camino alternativo escrito. La regla general es **cortar**: lo que no está a su hora sale del demo. No se mueve la hora de las 18:00.
5. Escribe `estado/TABLERO.md` y agrega a `DECISIONES.md` lo decidido, con hora y motivo. Solo agregar.
6. Si el demo funciona: `git tag <hito> && git push origin main --tags`.
7. Avisa a los otros dos en voz alta qué cambió para ellos.

## En `h2`

Se decide con qué corre el momento estrella: la red (`KRYLOV_MOTOR_ESPACIAL=red`) si pasó `validar-motor`, o el método exacto con «¿Dónde mido?» precalculado. La frase del guion cambia según cuál sea.

## En `congelado`

Desde aquí solo se corrigen errores y se pule lo que existe: textos, orden de las tarjetas, colores, velocidad. Cualquier pedido de función nueva se responde con «va a la lámina de hoja de ruta».

## Terminado cuando

TABLERO y DECISIONES están subidos, el tag existe en los dos repositorios y los tres saben qué sigue.
