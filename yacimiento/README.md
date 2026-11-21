# `yacimiento` · el sexto motor: un yacimiento en 3D leído desde sondajes

Fuera del producto congelado el sábado a las 18:00 (decisión D-40): no tiene tarjeta en la app y no toca `nucleo/`, `motor/`, `servicio/` ni `web/`. Reutiliza, solo leyendo, el flujo de `motor/comun/flujo.py` y la regla de decisión de `nucleo/decision.py`.

**La decisión.** Con una campaña de sondajes (perforaciones que sacan muestras de roca en profundidad): ¿qué bloques del yacimiento son mineral, cuáles son estéril y en cuáles no se sabe todavía y conviene perforar más?

## El modelo generativo

Un modelo de bloques de 32 × 32 × 16 (16.384 bloques). La ley, en log de % de cobre:

    Z(x) = β0 + Σ_k β_k·c_k(x) + W(x),     W ~ GP(0, σ²·exp(−h)),     y_i = Z(x_i) + ε_i,  ε_i ~ Normal(0, τ)

con anisotropía geométrica en 3D (alcance horizontal con rumbo y razón, y alcance vertical) y ocho covariables conocidas en todos los bloques: profundidad, cercanía a una falla, dos indicadores de litología, alteración, dos campos geofísicos y densidad de vetillas. Son 15 parámetros con prior normal en espacio sin restricciones. El diseño del dataset se sortea: de 15 a 60 sondajes inclinados, de 8 a 16 compósitos cada uno.

El campo se simula exacto en toda la grilla con *circulant embedding* (FFT), sin factorizar matrices: por eso se pueden simular decenas de yacimientos por segundo en un notebook.

## La red (inferencia amortizada)

U-Net 3D con dos cabezas, como `espacial` pero en volumen (`red.py`):

- **mapa:** media y desviación del predictivo posterior marginal de la ley de cada bloque;
- **flujo:** q(θ | D), flujo de acoplamiento condicional (NPE) sobre los 15 parámetros.

## El método lento (MCMC de referencia)

`mcmc.py`: NUTS (NumPyro) sobre θ con la verosimilitud marginal exacta del proceso gaussiano (una factorización de n × n por evaluación) y después kriging exacto de los 16.384 bloques por cada muestra de θ.

## Cómo se corre

    uv run python -m yacimiento.demo                      # el yacimiento del demo (simulado, semilla fija)
    uv run python -m yacimiento.entrenar --minutos 80     # entrena; guarda en yacimiento/checkpoints/
    uv run python -m yacimiento.mcmc --demo --simulados 1 # el método lento; nunca encima de un entrenamiento
    uv run python -m yacimiento.validar                   # escribe yacimiento/artefactos/sello.json
    uv run python -m yacimiento.exportar_deck             # deja los datos de pitch/deck/yacimiento.html

Los números medidos están en `artefactos/sello.json`. Lo que no existe: sondajes reales, correlación entre bloques en la salida de la red, y una tarjeta en la app.
