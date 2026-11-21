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
| J-04 | Duración del pitch | **3 minutos, en las generales y en las finales, por ahora.** No dijeron si hay preguntas del jurado. (Antes: tres minutos en 2024; los tramos grabados de otras sedes de 2026 duran cerca de seis con preguntas) | fuente | Respuesta de la organización a la consulta S-02, anotada en `pitch/VALIDACION.md` a las 03:55. Se vuelve a confirmar en la charla del sábado a las 20:00 | |
| J-05 | Equipos en el track Simulaciones | 12 de 48 | fuente | Conteo de los README públicos de los equipos | Agente, 21-nov |

## Datos de los casos

| Id | Cifra | Valor | Tipo | Origen | Verificó |
|---|---|---|---|---|---|
| D-01 | Archivo de rotación | 1.470 personas, 35 columnas, 16,1% renunció (237). Ficticio, creado por IBM | fuente | Kaggle, calculado del archivo. Recalculado en PC 3 sobre la copia de IBM en GitHub (mismo archivo, 227.977 bytes), sáb 03:22, `python3 datos/preparar/rotacion.py` | Agente, 21-nov |
| D-01b | Personas por decidir en rotación | 294 de 1.470 (20%, elegidas al azar con semilla 2026). De ellas, 54 renunciaron de verdad (la verdad no entra al motor). Quedan 1.176 con respuesta: 183 renunciaron (15,6%) | medido | PC 3, sáb 03:22, `python3 datos/preparar/rotacion.py` | |
| D-02 | Archivo de crédito | 30.000 clientes, 22,1% no pagó. Taiwán, 2005 | fuente | UCI, calculado del archivo. Recalculado en PC 3 sobre el .xls de UCI, sáb 03:28, `datos/preparar/credito.py` | Agente, 21-nov |
| D-02b | Clientes del caso de crédito | Muestra de 2.000 de los 30.000 (semilla 2026). 400 por decidir (20% al azar); de ellos, 95 no pagaron de verdad (la verdad no entra al motor). Quedan 1.600 con respuesta: 373 no pagaron (23,3%) | medido | PC 3, sáb 03:28, `uv run --no-project --with pandas --with xlrd python datos/preparar/credito.py` | |
| D-03 | Archivo de inasistencias | 110.527 citas, 20,2% no llegó, 81 barrios | fuente | Kaggle, calculado del archivo. Licencia no comercial. Recalculado en PC 3 sobre una copia pública del mismo archivo (SHA-256 `9132d3e7…a27d`), sáb 03:49 | Agente, 21-nov |
| D-03b | Citas del caso de inasistencias | 1.980 citas de 1.147 pacientes en 30 barrios (66 por barrio; 38% de los pacientes con 2 o más citas). 396 por decidir (20% al azar); de ellas, 86 no llegaron de verdad (la verdad no entra al motor). Quedan 1.584 con respuesta: 21,0% no llegó | medido | PC 3, sáb 04:45, `uv run python datos/preparar/inasistencias.py` (semilla 2026). Los CSV no se suben | |
| D-05 | Archivo malo de rotación | El de rotación más `fecha_salida`, una columna agregada por nosotros que tiene fecha solo para las 237 personas que renunciaron (incluidas 54 de las 294 por decidir) | medido | PC 3, sáb 04:45, `python3 datos/preparar/rotacion_malo.py` | |
| D-06 | Archivos de prueba para la subida (D-34) | Subconjuntos reales del mismo archivo público de IBM, por área, presentados «como si fueran otra empresa» (no lo son): ventas, 446 personas y 3 cargos; investigación, 961 y 6; personas (RR. HH.), 63 y 2, que a propósito queda bajo el mínimo de 200. Columnas en español y en otro orden; 20% de respuestas vacías al azar (semilla 2027) | medido | PC 3, sáb 07:26, `python3 datos/preparar/prueba_subida.py` | |
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
| M-01 | Terrenos simulados con que practicó el motor del terreno | **7.750.592 terrenos simulados** | medido (PC 2, sello de `espacial`, sáb 09:39, MacBook Air M4; `motor/artefactos/espacial/sello.json`) | |
| M-02 | Minutos de entrenamiento del motor del terreno | **280 minutos** (03:50 a 08:30) | medido (PC 2, sello de `espacial`, sáb 09:39, MacBook Air M4; `motor/artefactos/espacial/sello.json`) | |
| M-03 | Examen con datos reales, rotación: «dijimos N%, pasó M%», sobre cuántas personas | pendiente | A-10 | |
| M-04 | Lo que cuesta no saber, rotación, con los costos por defecto | pendiente | A-10 | |
| M-05 | Personas en cada color, rotación | pendiente | A-10 | |
| M-06 | Qué pesa en rotación: un factor «seguro» y uno «no se puede saber» | pendiente. No escribir el nombre de ningún factor antes de correr el motor | A-10 | |
| M-07 | Empresas simuladas de la nube | pendiente | A-13 | |
| M-08 | «¿Dónde mido?»: análisis completos rehechos | **228 análisis completos** rehechos | medido (PC 2, sello de `espacial`, sáb 09:39, MacBook Air M4; `motor/artefactos/espacial/sello.json`) | |
| M-09 | «¿Dónde mido?»: segundos con Krylov, sin nada entrenando en ese computador | **0,69 s** con la red (medido con nada más entrenando en PC 2) | medido (PC 2, sello de `espacial`, sáb 09:39, MacBook Air M4; `motor/artefactos/espacial/sello.json`) | |
| M-10 | Los mismos análisis con el método lento de siempre: minutos | **26.699 s (unas 7 horas y media)** para rehacer los mismos 228 análisis con el MCMC de referencia; un solo análisis lento tarda 117 s | medido (PC 2, sello de `espacial`, sáb 09:39, MacBook Air M4; `motor/artefactos/espacial/sello.json`). Decir exactamente eso: «rehacer los 228 análisis» | |
| M-11 | Acierto cuando se dice 90%: método rápido de siempre, Krylov | Terreno, en simulaciones nuevas: el método rápido (kriging con parámetros fijos) cubre 89% y la red 90%. **No hay diferencia que contar** en el terreno; la frase del momento 4 sale (ver `pitch/GUION.md`). Rotación: lo que se decide, 0,58 el método rápido y 0,91 la red, pero esa red **no pasó su sello** (no se dice) | medido (PC 2, sellos de `espacial` 09:39 y `supervivencia` 09:54) | |
| M-12 | Lo que vale medir en el mejor punto del terreno | pendiente | A-12 | |
| M-13 | Examen con datos reales, terreno: mediciones escondidas que cayeron en el rango | **24 de 31** mediciones reales escondidas cayeron dentro del rango de 90% (77%) | medido (PC 3, sáb 10:04, `KRYLOV_MOTOR_ESPACIAL=red`, `api.analizar("terreno")`) | |
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
| M-21 | Empresas simuladas con que practicó el motor de rotación | **12.739.616 empresas simuladas** (supervivencia, 04:05 a 08:30). **La red no pasó su sello (09:54): no se dice que esa tarjeta respondió con ella** | medido (PC 3, `motor/checkpoints/supervivencia/corrida.log`) | |
| M-22 | Carteras simuladas con que practicaron los motores de inasistencias y de crédito | [pendiente], una por motor | A-14, A-15 | |
| M-23 | Minutos de entrenamiento por motor (rotación, inasistencias, crédito; el del terreno es M-02) | Terreno 280 min (M-02); rotación 267,5 min (PC 3, M3); inasistencias y crédito [pendiente] | A-10, A-14, A-15 | |
| M-24 | Acierto del rango de 90% en simulaciones nuevas, por motor y en su peor grupo. Lámina técnica | [pendiente] ×4 | `validar-motor`: A-08, A-10, 13:00, 14:00 | |
| M-25 | Segundos del método lento de siempre por archivo, por motor | Terreno 117 s por archivo (6 terrenos, M4); rotación 150,9 s en el archivo real y 109,2 s de promedio (M4, sello de las 09:54); inasistencias y crédito [pendiente] | A-08 (terreno, rotación), 11:30 (inasistencias), 12:30 (crédito) | |
| M-26 | Milisegundos de Krylov por archivo, por motor, sin nada entrenando | [pendiente] ×4 | 12:00 y A-16 | |
| M-27 | Cartera de 1.000 empresas: horas con el método lento (M-25 × 1.000, dicho como cálculo) contra segundos de Krylov (M-14) | [pendiente] | A-16 | |
| M-28 | Diferencia entre Krylov y el método lento en los mismos archivos, por motor. Lámina técnica | Terreno 0,263 desviaciones (pasa; en el archivo real la tendencia difiere 2,17 en β0); rotación 0,43 (**no pasa**, el límite es 0,3); inasistencias y crédito [pendiente] | `validar-motor` | |
| M-29 | El archivo malo cae fuera de la nube y, corregido, dentro | **Ejes con nombre: sí y sí.** Con `fecha_salida`, el mejor factor solo adivina con AUC 1,0 (fuera; el límite de 5.000 empresas simuladas es 0,912); sin ella, 0,669 (dentro), igual que el archivo limpio. Segundo detector (resúmenes aprendidos): [pendiente de la red entrenada] | medido (PC 2, sáb 06:26; repetido en PC 3 a las 06:33 con `api.nube`) | |
| M-30 | Qué manda en el terreno | [pendiente]. No escribir nada antes de correr el motor | A-11 | |
| M-31 | Examen con datos reales, inasistencias | [pendiente] | A-14 | |
| M-32 | Examen con datos reales, crédito | [pendiente] | A-15 | |
| M-33 | Qué tarjetas respondieron con lo que practicó y cuáles salieron precalculadas | [pendiente: se fija a las 16:00] | A-17 | |
| M-34 | Examen con datos reales del método rápido de siempre, en los mismos casos | **Crédito** (400 clientes reservados): AUC 0,762; tramos dijo → pasó: 7,3% → 8,1%, 14,4% → 13,4%, 27,2% → 27,1%, 57,3% → 60,6%. **Inasistencias** (396 citas): AUC 0,737; tramos 4,6% → 2,5%, 15,9% → 11,9%, 29,4% → 33,1%, 47,8% → 42,9%. Rotación y terreno: [pendiente]. **Ojo: es una vara alta.** Lo que se pierde sin el modelo completo se dice solo después de medir a Krylov en el mismo examen | medido (PC 2, sáb 06:12, `uv run python -m motor.comun.rapido --caso credito`; inasistencias dentro de `motor.jerarquico.sello --ensayo`) | |
| M-35 | Recuperación de parámetros: correlación entre el valor verdadero y el estimado, por parámetro y por motor. Lámina técnica | [pendiente] ×4. Sale de las simulaciones del SBC que ya corre cada sello | sello de cada motor | |
| M-36 | Desde cuántos análisis conviene Krylov frente al método lento: minutos de entrenamiento ÷ (segundos del método lento − segundos de la red) por análisis. Sostiene el momento de la cartera | [pendiente] ×4. Se calcula con M-23, M-25 y M-26; no se mide aparte | PC 3, cuando estén esas tres | |
| M-37 | Tiempo de `analizar_archivo` en Render con un archivo de 2.000 filas (D-34). Si pasa de 2 s, la subida propia sale del escenario | [pendiente] | PC 1 y PC 2, P-12 y A-19 | |

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

## Revisión de fuentes (S-N2, sáb 04:50)

La hizo un agente abriendo cada enlace de `WORKPLAN.md`, sección 12. **No es una firma:** la columna «Verificó» de arriba la llena una persona en S-10. Aquí va lo que dice cada página hoy.

| Id | Página consultada | Qué dice hoy | ¿Coincide? |
|---|---|---|---|
| N-01 | Wikipedia en inglés (Aleksey Krylov) | No da los años 1902 y 1903. Dice que sus tablas de inundación se usaron en todo el mundo, y atribuye a Makarov la idea de inundar compartimentos sanos | En parte: confirma el uso, no las fechas |
| N-01 | Biografía de divulgación (plam.ru; el certificado HTTPS está vencido, carga por HTTP) | Presentó las tablas en octubre de 1902 y de nuevo en 1903; con ellas el comandante decidía rápido y sin error qué compartimento inundar. **La Marina no las adoptó en ese momento** | Sí en fechas; ojo con la adopción |
| N-02 | Wikipedia en inglés y en ruso; MacTutor | Trabajo de 1931 | Sí |
| J-01, J-02, J-03 | Bases del evento | Pesos 15/20/20/25/20; final solo con demostración funcional; revisión automatizada del código posible | Sí |
| J-05 | — | No hay enlace en la sección 12 | No se pudo verificar |
| D-01, D-03 | Kaggle | La página necesita un navegador; no se pudo leer | No se pudo abrir (los conteos se recalcularon sobre el archivo en PC 3) |
| D-02 | UCI, dataset 350 | 30.000 instancias, CC BY 4.0, Taiwán, abril a septiembre de 2005 | Sí |
| D-04, D-04b | rdrr.io (`meuse`, `meuse.grid`) | Zinc en mg/kg; `meuse.grid` con 3.103 filas de 40 m. No muestra la licencia GPL | Sí (la licencia no aparece en esa página) |
| K-11 | Circular holandesa de remediación de suelos 2013, anexo 1 (copia en un sitio de terceros) | Zinc: 720 mg/kg de materia seca, suelo estándar | Sí |
| C-02 | INE, demografía de empresas | 1.207.333 empresas activas en 2025; micro más pequeñas suman **91,8%**. El 96% no aparece | **No (el 96%)** |
| P-01 | buk.mx y buk.cl | buk.mx ya no muestra «+10.000»; buk.cl dice «+6.000 empresas». Ya no hay conflicto | Corregir la fila: «+6.000» |
| P-04 | Nota de prensa sobre AgendaPro | Más de 22.000 comercios en 17 países; la fecha sale solo de la URL | Sí |
| A-01 | Anuncio de SAP | Adquisición pendiente de aprobación; compromiso de invertir más de 1.000 millones de euros en cuatro años; sin precio publicado | Sí |

**Para una persona antes de S-10:**
1. **C-02:** decir «91,8% micro o pequeñas» o precisar la definición; el 96% no está en la página.
2. **P-01:** la cifra verificable hoy es «+6.000» (buk.cl). En voz alta sigue siendo «miles».
3. **N-01 y la apertura del pitch:** las fechas salen solo de la biografía de divulgación, que además dice que la Marina no adoptó las tablas en ese momento. La frase «el capitán miraba una tabla y decidía en segundos» describe lo que las tablas permitían; no conviene decir que se usaban ya a comienzos del 1900.
4. **D-01, D-03 y J-05:** abrir Kaggle en un navegador (filas y licencias) y buscar la fuente del «12 de 48». Ninguna de las tres está hoy en el guion.
