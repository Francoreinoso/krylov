---
name: entrenar-motor
description: Lanza o retoma el entrenamiento de la red del motor espacial de Krylov, con terrenos simulados al vuelo, puntos de guardado cada 10 minutos y el Mac protegido contra el sueño. Úsala en PC 2 para la corrida nocturna (A-04), para retomarla si se cayó y para reentrenar con otro ajuste.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Entrenar la red espacial

Rol: `amortizacion` (PC 2). **Amortizar** es pagar el costo de cálculo una vez, por adelantado: la red mira millones de terrenos simulados, donde la respuesta correcta se conoce, y aprende a dar esa respuesta al instante. Es la única red del proyecto. `regresion` no se entrena: usa el método exacto.

Los comandos son orientativos: ajústalos al código real.

## Antes

- `nucleo/preproceso.py` existe y **el simulador llama a esa misma función**, igual que el servicio con los datos reales. Hay una prueba que lo comprueba. Si no, para y arréglalo.
- La exportación a ONNX ya se probó con la red **sin entrenar** (`uv run python -m motor.exportar --prueba`). No se descubre a las 9 de la mañana que no exporta.
- `medir-rendimiento` corrida y dispositivo elegido.

## Qué conoce la red (`motor/artefactos/espacial/config.json`)

- Grilla de 32×32. Entran dos canales: el valor medido (estandarizado, cero donde no hay medición) y la marca de dónde hay medición.
- Entre 30 y 400 mediciones por terreno, repartidas al azar o agrupadas.
- Terrenos con continuidad corta o larga, con una dirección preferente cualquiera, y con más o menos ruido de medición.
- Sale, para cada bloque, el valor esperado y su margen.

## Pasos

1. **Prueba de humo (2 min):** `uv run python -m motor.entrenar --minutos 2`. La pérdida baja, no hay valores no numéricos, se escribe un punto de guardado.
2. **Lanza la corrida larga**, en una terminal aparte que no se cierre:
   `caffeinate -dims uv run python -m motor.entrenar --dispositivo <cpu|mps> --hasta 12:00 --guardar-cada-min 10`
   El guion cuenta los terrenos simulados y lo escribe en cada punto de guardado: esa es la cifra «practicó con N millones de terrenos».
3. **Anota** en `estado/amortizacion.md`, tabla «Entrenamiento en curso»: comando exacto, hora de inicio, carpeta de los puntos de guardado y comando para retomar.
4. **Comprueba antes de dormir** que existe el primer punto de guardado y que `pmset -g assertions` muestra a `caffeinate` impidiendo el sueño.
5. **En la mañana:** toma el último punto de guardado y corre `validar-motor`. El entrenamiento sigue de fondo hasta las 12:00; el punto de guardado final reemplaza al de la mañana solo si valida mejor.

## Si se cayó en la noche

Retoma desde el último punto de guardado con el comando anotado. Con una hora de entrenamiento suele alcanzar para una red que sirve; valida y decide en H1.

## Topes

- Red validada antes de H2 (sáb 12:15). Si no, el momento estrella corre con el método exacto y «¿Dónde mido?» precalculado, y el guion lo dice así.
- No se entrena después de las 16:30.

## Terminado cuando

El entrenamiento corre, el estado dice cómo retomarlo, y hay al menos un punto de guardado.
