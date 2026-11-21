---
name: entrenar-motor
description: Lanza o retoma el entrenamiento de la red de un motor de Krylov (espacial, supervivencia, jerarquico o estados) con datasets simulados al vuelo desde su modelo generativo, puntos de guardado cada 10 minutos y el Mac protegido contra el sueño. Úsala en PC 2 o en PC 3 para cada corrida (A-04, A-B4, A-08, A-09), para retomarla si se cayó y para reentrenar con otro ajuste. Recibe el motor_id.
argument-hint: "[espacial | supervivencia | jerarquico | estados]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Entrenar la red de un motor

Rol: `amortizacion` (PC 2). En PC 3 la lanza su persona con el código que escribió PC 2, sin editar `motor/`. **Amortizar** es pagar el costo de cálculo una vez, por adelantado: la red mira millones de datasets simulados con el modelo generativo del motor, donde los parámetros verdaderos se conocen, y aprende a entregar su posterior al instante (NPE). Hay cuatro motores y cada uno tiene su red (decisión D-26). Los modelos están en `WORKPLAN.md`, sección 11.

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`.

## Lo mínimo para lanzar

Simulador, codificador, flujo, pérdida, puntos de guardado y una prueba de humo con un SBC chico. **La cuadratura local, el MCMC en NumPyro y la integración con `api.py` no bloquean el lanzamiento**: van en la lista nocturna o en la mañana.

## Antes

- El simulador llama a la misma función de `nucleo/preproceso.py` que el servicio usa con los datos reales. Hay una prueba que lo comprueba. Si no, para y arréglalo.
- El predictivo a priori se miró contra el archivo real del caso (tasas, rangos) y el prior quedó escrito en `motor/artefactos/<id>/config.json`.
- El codificador **sin entrenar** ya exportó a ONNX con n variable (`uv run python -m motor.<id>.exportar --prueba`), y la prueba del flujo pasa: con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra.
- `medir-rendimiento <id>` corrida y dispositivo elegido.
- **No hay otro entrenamiento corriendo en este computador.** Uno por computador.

## Dónde y cuándo corre cada uno (`WORKPLAN.md`, 6.3)

| Motor | Computador | Cuándo |
|---|---|---|
| `espacial` | PC 2 (MacBook Air M4) | sáb 05:15 a 08:30 |
| `supervivencia` | PC 3 (MacBook Air M3) | sáb 05:15 a 08:30. Lo lanza la persona de PC 3, que no se duerme antes |
| `jerarquico` | PC 3 | sáb 08:30 a 11:30 |
| `estados` | PC 2, de fondo | sáb 09:15 a 12:00 |

PC 1 no entrena. Kaggle o Colab, solo si una persona abrió la sesión y vio la cuota (`STACK.md`, 3.3).

## Pasos

1. **Prueba de humo (3 a 5 min):** `uv run python -m motor.<id>.entrenar --minutos 3` y después un SBC chico de 200 datasets simulados (`uv run python -m motor.<id>.validar --sbc 200`). No tiene que pasar: tiene que correr, la pérdida tiene que bajar, no hay valores no numéricos y se escribe un punto de guardado.
   - **Solo `espacial`:** la cabeza de flujo recibe el resumen con el gradiente cortado, y la pérdida de la cabeza de mapa es idéntica con y sin ella. **Si la red de tres canales no pasa la prueba de humo a las 04:45, se lanza la de dos canales** (sin tendencia); la tendencia sale después del flujo o del MCMC.
2. **Lanza la corrida larga**, en una terminal aparte que no se cierre:
   `caffeinate -dims uv run python -m motor.<id>.entrenar --dispositivo <cpu|mps> --hasta <hora> --guardar-cada-min 10`
   El bucle cuenta los datasets simulados y lo escribe en cada punto de guardado: esa es la cifra «practicó con N millones».
3. **Anota** en el estado del computador donde corre (`estado/amortizacion.md` o `estado/seguimiento.md`), tabla «Entrenamiento en curso»: motor, comando exacto, hora de inicio, carpeta de los puntos de guardado y comando para retomar.
4. **Comprueba antes de dormir** que existe el primer punto de guardado y que `pmset -g assertions` muestra a `caffeinate` impidiendo el sueño. Enchufado, tapa abierta.
5. **Al terminar su turno:** detén la corrida, sube el último punto de guardado y corre `validar-motor <id>`. El siguiente motor de ese computador se lanza después.

## Si se cayó

Retoma desde el último punto de guardado con el comando anotado, valida una hora después y avisa a PC 3: el H2 de ese motor se corre. Si `supervivencia` no sirve a las 08:30, se relanza en PC 3 y tiene prioridad sobre `jerarquico`.

## Topes

- H2 por motor: `espacial` y `supervivencia` 12:15, `jerarquico` 13:00, `estados` 14:00. **Tope para cualquier motor: 16:00.**
- El motor que no validó a su hora sale con la implementación `mcmc`, rotulado «precalculado», y el guion no dice que responde la red.
- No se entrena después de las 16:00.

## Terminado cuando

El entrenamiento corre, el estado dice en qué computador y cómo retomarlo, y hay al menos un punto de guardado.
