---
name: entrenar-motor
description: Lanza o retoma el entrenamiento de la red de un motor de series de Krylov (cinetica, deformacion, desgaste o sismico) con datasets simulados al vuelo desde su modelo generativo, puntos de guardado cada 10 minutos y el Mac protegido contra el sueño. Úsala en PC 2 o en PC 3 para las dos rondas del sábado (A-26 a las 14:30, A-31 a las 16:30), para retomar una corrida que se cayó y para seguir entrenando hasta el tope de redes. El motor espacial ya está validado y no se reentrena. Recibe el motor_id.
argument-hint: "[cinetica | deformacion | desgaste | sismico]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Entrenar la red de un motor

Rol: `amortizacion` (PC 2). En PC 3 la lanza su persona con el código que escribió PC 2, sin editar `motor/`. **Amortizar** es pagar el costo de cálculo una vez, por adelantado: la red mira millones de datasets simulados con el modelo generativo del motor, donde los parámetros verdaderos se conocen, y aprende a entregar su posterior al instante (NPE). Hay cinco motores (decisión D-37). **`espacial` ya entrenó y pasó su sello: no se reentrena.** Esta skill es para los cuatro **motores de series**, que comparten un andamio (`motor/comun/series.py`, `nucleo/series.py`): codificador por unidad, flujo global y un flujo local chico. Cada motor aporta su simulador, su lista de parámetros y su función «lo que se decide». Modelos y andamio: `WORKPLAN.md`, sección 11.

Los comandos son orientativos: ajústalos al código real. `<id>` es el `motor_id`.

## Lo mínimo para lanzar

Simulador, red del andamio, pérdida, puntos de guardado y una prueba de humo con un SBC chico de 200 datasets (11.7). **El MCMC en NumPyro y la integración con `api.py` no bloquean el lanzamiento**: el MCMC del archivo del demo se corre antes solo si tarda menos de 10 minutos (A-26); si no, al terminar la ronda, sin nada entrenando.

## Antes

- El simulador llama a la misma función de preprocesamiento de `nucleo/` que el servicio usa con el archivo del caso (en `deformacion`, incluida la corrección del modo común). Hay una prueba que lo comprueba. Si no, para y arréglalo.
- El predictivo a priori se miró contra el archivo del demo: cae dentro de lo simulado, y el prior quedó escrito en `motor/artefactos/<id>/config.json`. Si cambiaste un prior, avisa a PC 3 para que regenere el archivo (S-24).
- El andamio pasó su prueba (A-23) y la red **sin entrenar** ya exportó (`uv run python -m motor.<id>.exportar --prueba`): el codificador a ONNX con formas fijas con relleno y dos salidas, s(D) y los s_j; los flujos a `flujo.npz` y `flujo_local.npz`; y con los mismos pesos y el mismo ruido, NumPy y `torch` dan la misma muestra.
- `medir-rendimiento <id>` corrida y dispositivo elegido.
- **No hay otro entrenamiento corriendo en este computador.** Uno por computador.

## Dónde y cuándo corre cada uno (`WORKPLAN.md`, 6.3)

| Ronda | Motor | Computador | Cuándo |
|---|---|---|---|
| 1 | `cinetica` | PC 2 (MacBook Air M4) | sáb 14:30 a 16:10 |
| 1 | `deformacion` | PC 3 (MacBook Air M3) | sáb 14:30 a 16:10. Lo lanza la persona de PC 3 |
| 2 | `desgaste` | PC 2 | sáb 16:30 a 18:15 |
| 2 | `sismico` | PC 3 | sáb 16:30 a 18:15. Lo lanza la persona de PC 3 |

De 16:10 a 16:30 y de 18:15 a 19:00 no hay nada entrenando: ahí se valida y se miden tiempos. De 19:00 a 20:30 cada computador queda libre para seguir entrenando el motor que esté más cerca de pasar. PC 1 no entrena. Kaggle o Colab, solo si una persona abrió la sesión y vio la cuota (`STACK.md`, 3.3).

## Pasos

1. **Prueba de humo (3 a 5 min):** `uv run python -m motor.<id>.entrenar --minutos 3` y después un SBC chico de 200 datasets simulados (`uv run python -m motor.<id>.validar --sbc 200`). No tiene que pasar: tiene que correr, la pérdida tiene que bajar, no hay valores no numéricos y se escribe un punto de guardado.
2. **Lanza la corrida larga**, en una terminal aparte que no se cierre:
   `caffeinate -dims uv run python -m motor.<id>.entrenar --dispositivo <cpu|mps> --hasta <hora> --guardar-cada-min 10`
   El bucle cuenta los datasets simulados y lo escribe en cada punto de guardado: esa es la cifra «practicó con N millones».
3. **Anota** en el estado del computador donde corre (`estado/amortizacion.md` o `estado/seguimiento.md`), tabla «Entrenamiento en curso»: motor, comando exacto, hora de inicio, carpeta de los puntos de guardado y comando para retomar.
4. **Comprueba a los 10 minutos** que existe el primer punto de guardado y que `pmset -g assertions` muestra a `caffeinate` impidiendo el sueño. Enchufado, tapa abierta.
5. **Al terminar la ronda:** detén la corrida (Ctrl-C guarda), sube el último punto de guardado y corre `validar-motor <id>`. El motor de la ronda siguiente se lanza después.

## Si algo se atrasa

- **Se cayó la corrida:** retoma desde el último punto de guardado con el comando anotado y avisa a PC 3. La validación se corre igual a la hora de su ronda, con lo que alcanzó.
- **El motor no está listo a la hora de lanzar:** se lanza cuando esté. Si a las 15:15 un motor de la ronda 1 no tiene prueba de humo, sale con el método lento y su computador pasa a la ronda 2.
- **El andamio no está subido a las 13:45:** los motores de la ronda 1 se lanzan con el flujo global solamente, y lo propio de cada unidad se resuelve con el método lento para el archivo del demo.

## Topes

- Validación de la ronda 1 a las 16:10 y de la ronda 2 a las 18:15. **Tope de redes: 20:30.** Después no cambia quién responde cada tarjeta, y no se entrena más.
- El motor que no validó sale con la implementación `mcmc`, rotulado «precalculado», y el guion no dice que responde la red. Si a las 17:30 tampoco tiene su método lento, la tarjeta sale del inicio.

## Terminado cuando

El entrenamiento corre, el estado dice en qué computador y cómo retomarlo, y hay al menos un punto de guardado.
