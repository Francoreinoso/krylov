# Hoja de ruta: del motor chico al modelo completo

> Material de apoyo para la pregunta «¿y después qué?» y para la lámina de respaldo «qué existe y qué es hoja de ruta». **Nada de la columna «modelo completo» está construido ni se va a construir en la hackathon.** Este archivo usa nombres técnicos; en pantalla y en voz alta se usa `GLOSARIO.md`. Reemplaza a la lista de candidatos de antes del pivote (minería en 3D, clima, plataformas): con D-37 la hoja de ruta es una sola, hacer completos los cinco motores mineros.

La idea que se vende no cambió: un modelo difícil, de los que hoy exigen un especialista y horas de cómputo por análisis, **se entrena una vez con casos simulados y después responde en un paso**, con su rango, con lo que cuesta no saber y con dónde conviene medir.

El modelo completo de cada decisión está descrito en el documento técnico del equipo («Inferencia Bayesiana Amortizada para la Gran Minería Chilena», borrador interno). Lo que se construye en la hackathon es la versión chica, hecha para poder validarla en una tarde.

## Con qué vara se mide «chico»

Lo único medido que tenemos:

| Medido | Valor | Cifra |
|---|---|---|
| Motor de 7 parámetros (`espacial`), una noche de entrenamiento | Pasó su sello | M-01, M-02, M-28 |
| Motor de 32 parámetros (rotación, ya retirado), una noche de entrenamiento | **No** pasó su sello | M-21, M-28 |

Por eso los cuatro motores nuevos tienen entre 5 y 7 parámetros globales y 2 por unidad. **Una noche de entrenamiento no garantiza un motor validado**, y el modelo completo de cada fila de abajo es bastante más grande que el que falló.

## Los cinco, de lo que hay a lo que falta

| Decisión | Lo que se construye en la hackathon | El modelo completo (hoja de ruta) | Lo que lo hace difícil |
|---|---|---|---|
| Leyes y arsénico | Proceso gaussiano estacionario y anisotrópico en dos dimensiones, una variable, hasta 400 muestras. **Validado** | Dominios geológicos como un campo oculto (cada bloque pertenece a un tipo de roca, y los vecinos se parecen) más un proceso gaussiano distinto por dominio; cobre y arsénico a la vez; tres dimensiones | La cantidad de configuraciones de dominios crece sin control con el número de bloques: el método lento no puede ni escribir la cuenta. La grilla en tres dimensiones multiplica por decenas el tamaño de la red |
| Taludes y relaves | Sector por sector, dos historias posibles (estable o acelerando) y cuánto falta, con lo que aprende del resto del muro | El muro como un solo cuerpo: miles de puntos que se empujan entre sí, con la resistencia de la roca como incógnita y varios sensores a la vez (radar y presión de agua) | Seguir en el tiempo un estado de miles de dimensiones. Y las series reales no son limpias: hay sectores que se aceleran y después frenan |
| Flotación | Una curva por línea (el cobre flota rápido y después lento), leída desde las primeras celdas | Varias especies de mineral que compiten, la espuma que devuelve parte de lo flotado, y las ecuaciones resueltas en el tiempo con los datos del analizador en línea | Cada propuesta del método lento exige resolver ecuaciones rígidas; y con pocos datos, velocidad y tope se confunden |
| Flota de camiones | Un indicador de desgaste por camión, con la exigencia de su ruta | Varios componentes por camión, telemetría continua (carga, pendiente, temperatura) y mantenciones que reinician en parte el desgaste | Decenas de miles de incógnitas que solo pueden crecer; y el cambio de aceite hace que la señal vuelva a cero |
| Sismicidad | Cuándo ocurre cada temblor y de qué tamaño, por sector | Además, dónde: cada temblor gatilla otros cerca suyo, y los sectores se contagian | La cuenta crece con el cuadrado del número de temblores, y hay que rehacerla con cada uno nuevo |

## Qué se puede decir de esto en el pitch

- **Sí:** «Lo que ven son versiones chicas, hechas para poder comprobarlas en una tarde. La hoja de ruta es hacer completo cada modelo, partiendo por el del banco, que ya está validado.» Con el rótulo «hoja de ruta» en pantalla.
- **No:** horas, fechas, nombres de mineras, ni que alguno de los modelos completos existe.
- **Si preguntan «¿eso no existe ya?»:** en minería se usan modelos de este tipo fuera de línea, en horas. Buscamos redes ya entrenadas para estas familias y no encontramos (un agente lo revisó el sábado al mediodía): hay investigación reciente en modelos espaciales y en procesos de Hawkes, pero no un estimador listo para estos cinco problemas. No revisamos productos comerciales uno por uno: se responde «no conocemos uno que lo entregue al instante, y no lo revisamos todo».
- **Si preguntan por la investigación que hay:** estimadores neuronales para datos espaciales irregulares (Sainsbury-Dale et al., 2025); inferencia amortizada para modelos de efectos mixtos (Arruda et al., 2024); estimación por simulación del modelo de réplicas sísmicas (Stockman et al., 2024); pronóstico probabilístico del momento de falla de un talud (Zhang et al., 2020). Los enlaces los abrió un agente, no una persona: no se citan en una lámina.
