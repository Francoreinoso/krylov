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
| D-01 | Archivo de rotación | 1.470 personas, 35 columnas, 16,1% renunció (237). Ficticio, creado por IBM | fuente | Kaggle, calculado del archivo | Agente, 21-nov |
| D-02 | Archivo de crédito | 30.000 clientes, 22,1% no pagó. Taiwán, 2005 | fuente | UCI, calculado del archivo | Agente, 21-nov |
| D-03 | Archivo de inasistencias | 110.527 citas, 20,2% no llegó, 81 barrios | fuente | Kaggle, calculado del archivo. Licencia no comercial | Agente, 21-nov |
| D-04 | Archivo del terreno | 155 mediciones; 33 superan los 720 mg/kg de zinc | fuente | Paquete `sp` de R, calculado de una copia | Agente, 21-nov |

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

Todas pendientes. Cada una se registra con máquina, hora y comando.

| Id | Cifra | Valor | Cuándo se mide | Verificó |
|---|---|---|---|---|
| M-01 | Terrenos simulados con que practicó la red | pendiente | A-09 | |
| M-02 | Minutos de entrenamiento | pendiente | A-09 | |
| M-03 | Examen con datos reales, rotación: «dijimos N%, pasó M%», sobre cuántas personas | pendiente | A-08 | |
| M-04 | Lo que cuesta no saber, rotación, con los costos por defecto | pendiente | A-08 | |
| M-05 | Personas en cada color, rotación | pendiente | A-08 | |
| M-06 | Qué pesa en rotación: un factor «seguro» y uno «no se puede saber» | pendiente. No escribir el nombre de ningún factor antes de correr el motor | A-08 | |
| M-07 | Empresas simuladas de la nube | pendiente | A-13 | |
| M-08 | «¿Dónde mido?»: análisis completos rehechos | pendiente | A-11 | |
| M-09 | «¿Dónde mido?»: segundos con la red | pendiente | A-11 | |
| M-10 | Los mismos análisis con el método exacto: minutos | pendiente. Decir exactamente qué se comparó | A-11 | |
| M-11 | Acierto cuando se dice 90%: método rápido, Krylov | pendiente | A-14 | |
| M-12 | Lo que vale medir en el mejor punto del terreno | pendiente | A-11 | |
| M-13 | Examen con datos reales, terreno: mediciones escondidas que cayeron en el rango | pendiente | A-10 | |
| M-14 | Cartera: empresas analizadas y segundos | pendiente | A-12 | |
| M-15 | Prueba del asistente genérico: de tres intentos, cuántas respuestas distintas y cuántas dicen cuánto se pueden equivocar | pendiente | S-09 | |
| M-16 | Extraños que repiten la idea, prueba de las 12:30 | pendiente: de 3 | S-13 | |
| M-17 | Extraños que repiten la idea, prueba de las 19:00 | pendiente: de 3 | Sáb 19:00 | |
| M-18 | Tiempo de una tarjeta en la URL pública, desde un teléfono | pendiente | P-08 | |
| M-19 | Horas desde la primera línea del motor espacial hasta el mapa en la app | pendiente | H2 | |
| M-20 | Simular un conjunto de 300 puntos sueltos | 1,15 ms. MacBook M4 16 GB, 21-nov 00:24 | ya medido | |

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
