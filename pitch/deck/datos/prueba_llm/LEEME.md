# La prueba: el mismo archivo, a un LLM con 3 minutos

Para responder con datos a «¿y por qué no subirle el archivo a un LLM?». Hecha el sábado 21-nov-2026 a las 16:00, en PC 3, **con un entrenamiento corriendo en el mismo computador** (los tiempos del LLM lo sufren; los 3 minutos eran el plazo que se le dio).

## Qué se hizo

Es el mismo examen que Krylov se toma con cada archivo (`nucleo/espacial._examen`): al banco del caso `leyes` (340 pozos, **simulado**) se le esconden 68 muestras; con las otras 272 hay que decir, para cada lugar escondido, cuánto arsénico hay y entre qué valores puede estar (rango de 90%).

- `preparar.py` arma `muestras.csv` (272) y `puntos.csv` (68 lugares, sin valor) y guarda lo que respondió Krylov en `krylov.csv`.
- A **Claude Fable 5.2** (un agente nuevo de Claude Code, sin contexto, con herramientas: podía escribir y correr código) se le entregaron los dos archivos con este pedido, **dos veces, por separado**:

> Te subo las muestras de arsénico de los pozos de un banco de una mina a rajo abierto. Necesito una respuesta rápida: tienes 3 minutos de reloj, no más. […] Para cada lugar de puntos.csv, cuánto arsénico estimas que hay (as_ppm) y entre qué valores puede estar, con 90% de confianza (bajo, alto). Con eso decido si esa roca supera el límite de 500 ppm. […] Puedes usar las herramientas que quieras. […] Prefiero una respuesta rápida a una perfecta.

- `a/` y `b/` guardan lo que entregó cada corrida: `respuesta.csv`, las marcas de tiempo y el código que escribió.
- `medir.py` compara todo contra las 68 muestras escondidas y escribe `resultado.json`.

## Qué salió

| | Krylov | LLM, corrida A | LLM, corrida B |
|---|---|---|---|
| Muestras escondidas dentro del rango (de 68) | 61 | 61 | 63 |
| Ancho medio del rango (ppm) | 749 | 730 | 863 |
| Error medio (ppm) | 182 | 182 | 193 |
| Lado correcto del límite de 500 ppm (de 68) | 56 | 55 | 56 |
| Tiempo | 10 ms (sello del motor) | 152 s | 177 s |
| Método | el del sello: siempre el mismo | kriging en logaritmo, parámetros elegidos en una grilla | promedio de los 8 vecinos más cercanos (dos intentos de un modelo completo no terminaron a tiempo) |

**El LLM no respondió mal: acertó parecido a Krylov.** La diferencia no está en la calidad de esta respuesta. Está en:

1. **El tiempo.** 152 y 177 segundos contra 10 milisegundos. Por eso «¿Dónde perforo?», que exige rehacer el análisis 480 veces (M-43), le toma a Krylov 1,3 s (M-44) y a ese ritmo tomaría unas 20 horas (480 × 152 s: **una cuenta, no una corrida**).
2. **Que no es el mismo método cada vez.** Las dos corridas escribieron programas distintos; sus estimaciones difieren 33 ppm en promedio y hasta 459 ppm en un lugar, y los rangos de una son 18% más anchos que los de la otra. Una de las dos terminó con su método de respaldo.
3. **Que nadie certificó ese programa.** El de Krylov pasó su sello antes de ver un archivo: 2.000 casos nuevos, y la comparación con el método lento.

## Lo que esta prueba no es

Una sola prueba, dos corridas, un archivo simulado, en un computador cargado. No dice que un LLM siempre acierte ni que siempre falle. En la app de Krylov el modelo de lenguaje sí se usa, para lo que hace mejor: proponer qué columna es cuál y escribir la respuesta en palabras. Los números salen del motor.
