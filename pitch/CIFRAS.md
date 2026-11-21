# Registro de cifras

> Hackathon: proyecto chico, producto terminado el sábado a las 18:00. Este archivo existe para que ningún número del pitch sea inventado. Mantenerlo toma un minuto por cifra.

**Regla:** un número que no tiene fila aquí no aparece en pantalla, en una lámina ni en el guion.

**Tipos.** `medido`: lo medimos nosotros (decir en qué máquina, cuándo y con qué comando). `fuente`: tiene enlace y alguien abrió la página. `hipótesis`: supuesto nuestro; en pantalla y en voz alta se dice que lo es.

La columna «Verificó» lleva el nombre de la persona que abrió la fuente o repitió la medición. «Agente, 21-nov» significa que un agente de investigación leyó la página ese día: sirve para trabajar, pero **antes de ir a una lámina la abre una persona** (tarea S-10). Los enlaces están en `WORKPLAN.md`, sección 12.

## El nombre

| Id | Cifra | Valor | Tipo | Origen | Verificó |
|---|---|---|---|---|---|
| N-01 | Las tablas de Krylov | Presentó sus tablas en 1902 y 1903; con ellas el comandante podía determinar rápido qué compartimento inundar para enderezar el barco; se usaron en todo el mundo | fuente | Wikipedia en inglés y en ruso (artículo de Aleksey Krylov) y una biografía de divulgación. En el pitch se dice «a comienzos del 1900», sin fecha exacta ni nombre de barco | Agente, 21-nov |
| N-02 | Subespacio de Krylov | Artículo de 1931 | fuente | Wikipedia; MacTutor. Solo si preguntan | Agente, 21-nov |

## El jurado y el formato

| Id | Cifra | Valor | Tipo | Origen | Verificó |
|---|---|---|---|---|---|
| J-01 | Criterios de evaluación | Originalidad 15%, ambición 20%, ejecución 20%, aspecto técnico 25%, impacto 20% | fuente | Bases, hack.platan.us/26-cl/bases | Agente, 21-nov |
| J-02 | Quién llega a la final | Solo equipos con una demostración funcional | fuente | Bases | Agente, 21-nov |
| J-03 | Revisión del código | El jurado puede apoyarse en una revisión automatizada del código | fuente | Bases, criterio de aspecto técnico | Agente, 21-nov |
| J-04 | Duración del pitch | Sin publicar. Tres minutos en 2024; los tramos grabados de otras sedes de 2026 duran cerca de seis minutos con preguntas | sin confirmar | Se confirma en la charla del sábado a las 20:00 y con la consulta S-02 | |
| J-05 | Equipos en el track Simulaciones | 12 de 48 | fuente | Conteo de los README públicos de los equipos | Agente, 21-nov |

## Datos de los casos

| Id | Cifra | Valor | Tipo | Origen | Verificó |
|---|---|---|---|---|---|
| D-01 | Archivo de rotación | 1.470 personas, 35 columnas, 16,1% renunció (237). Ficticio, creado por IBM | fuente | Kaggle, calculado del archivo. Recalculado en PC 3 sobre la copia de IBM en GitHub (mismo archivo, 227.977 bytes), sáb 03:22, `python3 datos/preparar/rotacion.py` | Agente, 21-nov |
| D-01b | Personas por decidir en rotación | 294 de 1.470 (20%, elegidas al azar con semilla 2026). De ellas, 54 renunciaron de verdad (la verdad no entra al motor). Quedan 1.176 con respuesta: 183 renunciaron (15,6%) | medido | PC 3, sáb 03:22, `python3 datos/preparar/rotacion.py` | |
| D-02 | Archivo de crédito | 30.000 clientes, 22,1% no pagó. Taiwán, 2005 | fuente | UCI, calculado del archivo. Recalculado en PC 3 sobre el .xls de UCI, sáb 03:28, `datos/preparar/credito.py` | Agente, 21-nov |
| D-02b | Clientes del caso de crédito | Muestra de 2.000 de los 30.000 (semilla 2026). 400 por decidir (20% al azar); de ellos, 95 no pagaron de verdad (la verdad no entra al motor). Quedan 1.600 con respuesta: 373 no pagaron (23,3%) | medido | PC 3, sáb 03:28, `uv run --no-project --with pandas --with xlrd python datos/preparar/credito.py` | |
| D-03 | Archivo de inasistencias | 110.527 citas, 20,2% no llegó, 81 barrios | fuente | Kaggle, calculado del archivo. Licencia no comercial | Agente, 21-nov |
| D-04 | Archivo del terreno | 155 mediciones; 33 superan los 720 mg/kg de zinc | fuente | Paquete `sp` de R, calculado de una copia. Recalculado en PC 3 con `sp` 2.1.4, sáb 03:22, `Rscript datos/preparar/terreno.R` | Agente, 21-nov |
| D-04b | Grilla del terreno | 3.103 celdas de 40 m con su distancia al río (`meuse.grid`) | fuente | Paquete `sp` 2.1.4, `Rscript datos/preparar/terreno.R` | |

## Supuestos de cada caso (van en pantalla como deslizadores)

Ninguno tiene fuente, salvo K-11. Definen la plata que se ve, así que en voz alta se dice «con estos costos, que puedes cambiar». Los valores por defecto de rotación y crédito se eligieron para que el punto de corte quede cerca de la tasa real del archivo y la pantalla muestre los tres colores.

| Id | Caso | Supuesto | Valor | Punto de corte que resulta |
|---|---|---|---|---|
| K-01 | rotacion | Costo de un plan de retención | US$ 1.500 | 20% |
| K-02 | rotacion | Costo de reemplazar a alguien | US$ 6.000 | |
| K-03 | credito | Ganancia perdida por rechazar a quien pagaba | US$ 800 | 24% |
| K-04 | credito | Pérdida por aprobar a quien no pagó | US$ 2.500 | |
| K-05 | inasistencias | Costo de confirmar o sobrerreservar una cita | US$ 15 | 27% |
| K-06 | inasistencias | Costo de una hora perdida | US$ 40 | |
| K-11 | terreno | Nivel de zinc que obliga a limpiar | 720 mg/kg. **Con fuente:** valor de intervención holandés para suelo estándar (Circular de remediación de suelos, 2013) | |
| K-12 | terreno | Costo de limpiar un bloque | US$ 20.000 | 29% |
| K-13 | terreno | Costo de dejar un bloque contaminado | US$ 50.000 | |
| K-17 | terreno | Costo de una medición | US$ 3.000 | |

## Medidas nuestras

Todas pendientes. Cada una se registra con máquina, hora y comando. Las mide PC 2 salvo que se diga otra cosa. Las tareas A-xx son las de `WORKPLAN.md`, sección 6.3, reescrita por D-26.

| Id | Cifra | Valor | Cuándo se mide | Verificó |
|---|---|---|---|---|
| M-01 | Terrenos simulados con que practicó el motor del terreno | pendiente | A-08 | |
| M-02 | Minutos de entrenamiento del motor del terreno | pendiente | A-08 | |
| M-03 | Examen con datos reales, rotación: «dijimos N%, pasó M%», sobre cuántas personas | pendiente | A-10 | |
| M-04 | Lo que cuesta no saber, rotación, con los costos por defecto | pendiente | A-10 | |
| M-05 | Personas en cada color, rotación | pendiente | A-10 | |
| M-06 | Qué pesa en rotación: un factor «seguro» y uno «no se puede saber» | pendiente. No escribir el nombre de ningún factor antes de correr el motor | A-10 | |
| M-07 | Empresas simuladas de la nube | pendiente | A-13 | |
| M-08 | «¿Dónde mido?»: análisis completos rehechos | pendiente | A-12 | |
| M-09 | «¿Dónde mido?»: segundos con Krylov, sin nada entrenando en ese computador | pendiente | A-12, 12:00 | |
| M-10 | Los mismos análisis con el método lento de siempre: minutos | pendiente. Decir exactamente qué se comparó: rehacer cada análisis completo. Un solo análisis lento del terreno tarda segundos | A-12, 12:00 | |
| M-11 | Acierto cuando se dice 90%: método rápido de siempre, Krylov | pendiente | A-16 | |
| M-12 | Lo que vale medir en el mejor punto del terreno | pendiente | A-12 | |
| M-13 | Examen con datos reales, terreno: mediciones escondidas que cayeron en el rango | pendiente | A-11 | |
| M-14 | Cartera: empresas analizadas y segundos. Si rotación salió precalculada, es el número de empresas precalculadas y no se dice «1.000» | pendiente | A-13 | |
| M-15 | Prueba del asistente genérico: de tres intentos, cuántas respuestas distintas y cuántas dicen cuánto se pueden equivocar | pendiente | S-09 | |
| M-16 | Extraños que repiten la idea, prueba de las 12:30 | pendiente: de 3 | S-13 | |
| M-17 | Extraños que repiten la idea, prueba de las 19:00 | pendiente: de 3 | Sáb 19:00 | |
| M-18 | Tiempo de una tarjeta en la URL pública, desde un teléfono | pendiente | P-08 | |
| M-19 | Horas desde la primera línea del motor espacial hasta el mapa en la app | pendiente | H2 | |
| M-20 | Simular un conjunto de 300 puntos sueltos | 1,15 ms. MacBook M4 16 GB, 21-nov 00:24. Medido para el plan anterior; no va al guion | ya medido | |

### Por motor (decisión D-26)

Una fila por motor y por medida. `sup` = rotación, `jer` = inasistencias, `est` = crédito, `esp` = terreno. Los valores van entre corchetes hasta medirlos; lo que no se alcance a medir se queda sin decir. Las de «lámina técnica» no se dicen en voz alta.

| Id | Cifra | Valor | Cuándo se mide | Verificó |
|---|---|---|---|---|
| M-21 | Empresas simuladas con que practicó el motor de rotación | [pendiente] | A-10 | |
| M-22 | Carteras simuladas con que practicaron los motores de inasistencias y de crédito | [pendiente], una por motor | A-14, A-15 | |
| M-23 | Minutos de entrenamiento por motor (rotación, inasistencias, crédito; el del terreno es M-02) | [pendiente] | A-10, A-14, A-15 | |
| M-24 | Acierto del rango de 90% en simulaciones nuevas, por motor y en su peor grupo. Lámina técnica | [pendiente] ×4 | `validar-motor`: A-08, A-10, 13:00, 14:00 | |
| M-25 | Segundos del método lento de siempre por archivo, por motor | [pendiente] ×4. Máquina y cuántos archivos se promediaron | A-08 (terreno, rotación), 11:30 (inasistencias), 12:30 (crédito) | |
| M-26 | Milisegundos de Krylov por archivo, por motor, sin nada entrenando | [pendiente] ×4 | 12:00 y A-16 | |
| M-27 | Cartera de 1.000 empresas: horas con el método lento (M-25 × 1.000, dicho como cálculo) contra segundos de Krylov (M-14) | [pendiente] | A-16 | |
| M-28 | Diferencia entre Krylov y el método lento en los mismos archivos, por motor. Lámina técnica | [pendiente] ×4 | `validar-motor` | |
| M-29 | El archivo malo cae fuera de la nube y, corregido, dentro | [pendiente: sí o no, por cada uno de los dos chequeos] | A-13 | |
| M-30 | Qué manda en el terreno | [pendiente]. No escribir nada antes de correr el motor | A-11 | |
| M-31 | Examen con datos reales, inasistencias | [pendiente] | A-14 | |
| M-32 | Examen con datos reales, crédito | [pendiente] | A-15 | |
| M-33 | Qué tarjetas respondieron con lo que practicó y cuáles salieron precalculadas | [pendiente: se fija a las 16:00] | A-17 | |
| M-34 | Examen con datos reales del método rápido de siempre, en los mismos casos | [pendiente] | A-16 | |

**Retiradas por D-26** (no se usan; los ids no se reciclan): todo tiempo o acierto del método exacto de las tres tarjetas con lista del plan anterior; «Krylov eligió N de M columnas» y cualquier cifra de la propuesta de columnas o de «Sube tus datos»; M-19 se reemplaza por M-23 y M-02.

## Negocio (solo lámina de respaldo)

| Id | Cifra | Valor | Tipo | Origen | Verificó |
|---|---|---|---|---|---|
| C-01 | Sueldo de un data scientist en Chile | entre $1,4 y $2,1 millones de pesos al mes | fuente débil | Avisos de empleo, 2026. Decir «según avisos» | |
| C-02 | Empresas activas en Chile | 1.207.333; 96% micro o pequeñas | fuente | INE, 2025 | |
| C-05 | Precio | US$ 20 al mes por empresa que lo usa | hipótesis | Sin validar | |
| C-06 | Ingreso por cada 1.000 empresas activas | US$ 240.000 al año | cálculo sobre hipótesis | C-05 | |
| P-01 | Clientes de Buk | «miles». Su sitio dice +10.000 en una página y +6.000 en otra | fuente, con conflicto | buk.mx y buk.cl. En voz alta se dice «miles» | |
| P-04 | Negocios en AgendaPro | más de 22.000 | fuente (prensa) | 20-ago-2026 | |
| A-01 | SAP y Prior Labs | compromiso de invertir «más de 1.000 millones de euros en los próximos cuatro años». No es el precio de compra | fuente | Anuncio de SAP, 4-may-2026 | |

**Fuera del pitch:** la meta de ingresos del primer año (se veía ingenua) y la cita de la prueba pública de 2024 sobre agentes de análisis de datos (está vieja). Las reemplaza la prueba propia M-15.
