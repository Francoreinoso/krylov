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

## Para quien termina el deck (PC 2)

Todo lo necesario está versionado; no hace falta entrenar ni correr el método lento de nuevo.

- **La página:** `pitch/deck/yacimiento.html` y sus datos, `pitch/deck/datos/yacimiento.js`. Cuatro pasos (`#0` a `#3` en la dirección); `?quieto` apaga el giro. En el paso de la incertidumbre el punto baja por la perforación y el rango cambia con la profundidad.
- **Regenerar los datos de la página** (por ejemplo, tras cambiar la ley de corte o los costos en `validar.py`, constante `CASO`): `uv run python -m yacimiento.exportar_deck`. Usa `artefactos/pesos.pt` (la red final), `datos/demo.npz` (el yacimiento del demo) y `artefactos/mcmc_demo.npz` (el método lento, en copia liviana). Con la copia liviana, «la misma decisión» sale 92,0% en vez de 92,1% por redondeo; el archivo versionado de la página viene de la corrida completa.
- **Qué es dato y qué es ilustración:** el mineral bajo la zona marcada, el rango por profundidad y los números salen de la red. El relieve de la mina es la maqueta de la portada (`js/portada.js`): no representa datos.

**Qué se puede decir, con su fila en `pitch/CIFRAS.md`:**

| Frase | Cifra |
|---|---|
| Pre-entrenó con 126.696 yacimientos simulados (110 minutos) | M-63 |
| Responde los 16.384 bloques en unos 20 milisegundos (18 a 22 medidos) | M-64 |
| En 2.000 yacimientos nuevos, la ley verdadera cae dentro del rango de 90% en 0,90 de los bloques | M-63 |
| Donde se pronuncia, acierta 0,94 contra la verdad escondida (4.980 de 5.302 bloques); en 11.082 dice «no se sabe» | M-64 |
| El método de siempre tardó 913 segundos en este mismo archivo; la misma decisión en 92% de los bloques | M-65 |
| Ley de corte de 0,5% y costos por bloque: supuestos del demo | K-71 a K-73 |

**Qué no se puede decir:** que este motor «pasó su sello» (no pasa: la cabeza de parámetros falla el SBC y no coincide con el método lento); nada sobre sus parámetros ni sobre «qué tan lejos se parece la roca»; que son datos de una mina (es un yacimiento simulado); ni que está en la app (no tiene tarjeta). La comparación con el método lento es de un solo yacimiento.
