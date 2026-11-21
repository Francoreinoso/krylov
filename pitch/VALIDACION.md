# Lo que nos dijeron

> Hackathon: no se sale a validar con nadie externo. Aquí se anota solo lo que llegue. Si la tabla de personas queda vacía, en el pitch se dice «todavía no hablamos con clientes». Nunca se inventa una cita. El repositorio es público: no se anota aquí el nombre de nadie sin su permiso.

## Organización

| Pregunta | Respuesta | Hora |
|---|---|---|
| Minutos de pitch, generales y finales. ¿Hay preguntas? | 3 minutos siempre, por ahora. Lo de las preguntas del jurado no quedó respondido. | |
| ¿Los escenarios de las generales son por track? | No importa para nosotros. | |
| Computador, conexión del proyector, audio | Se presenta desde nuestro computador; video y audio listos. | |
| ¿Hay premios de sponsors? | No importa para nosotros. | |
| Lo que dijeron en la charla de las 20:00 sobre el demo | | |

## Gente de Buk o mentores

| Hora | Empresa | ¿La pregunta de la tarjeta existe? ¿Quién la responde hoy? | Frase textual | ¿Permiso para citar? |
|---|---|---|---|---|
| | | | | |

## Prueba del asistente genérico (tarea S-09)

El mismo archivo de rotación y la misma pregunta («¿A quién conviene retener y cuánto me cuesta no saberlo?»), tres veces, en conversaciones nuevas.

**Cómo se hace (fijado el sáb 06:05, antes de ver ningún resultado, para que la cifra M-15 no se acomode después):**
1. **Archivo:** `datos/demo/rotacion.csv`, tal cual está en el repositorio (1.470 filas, 294 con la respuesta vacía). Desde cualquier equipo: https://raw.githubusercontent.com/platanus-hack/platanus-hack-26-cl-team-5/main/datos/demo/rotacion.csv
2. **Pregunta exacta, sin nada más:** «Este archivo tiene empleados de una empresa; la columna Attrition dice si renunciaron y está vacía en los que todavía no sabemos. ¿A quién conviene retener y cuánto me cuesta no saberlo? Un plan de retención cuesta US$ 1.500 por persona y reemplazar a alguien cuesta US$ 6.000.» (Los costos son los de K-01 y K-02, los mismos de la tarjeta.)
3. Tres conversaciones nuevas, en un asistente genérico que acepte archivos, sin instrucciones previas ni memoria. La hace una persona.
4. **Qué se anota de cada intento:** cuántas personas dijo que había que retener y sus números de empleado (`EmployeeNumber`), si los dio; el monto en plata que dio por «no saber», si dio uno; y si dijo cuánto se puede equivocar (un rango, un intervalo o una probabilidad por persona). El texto completo de cada respuesta se guarda en un archivo local, fuera del repositorio.
5. **Criterio de «respuestas distintas»** (M-15): dos intentos son distintos si sus listas de personas a retener tienen menos de 80% en común (personas en las dos listas sobre personas en alguna de las dos) o si el monto en plata difiere en más de 20%. Un intento que no da lista ni monto cuenta como distinto de los que sí dan.
6. Se anota lo que pasó, sea cual sea, y se registra M-15 con la skill `registrar-cifra`.

| Intento | A quién dijo que había que retener (resumen) | ¿Dio un número en plata? | ¿Dijo cuánto se puede equivocar? |
|---|---|---|---|
| 1 (10:38) | 49 de 294 (umbral 25% = 1.500 / 6.000); ensamble de regresión logística y gradient boosting. De esas 49, renunciaron de verdad 33 (67%); encontró 33 de las 54 renuncias reales | Sí: «costo de la incertidumbre residual» US$ 122.307 (y US$ 181.258 de «no saber nada») | Da una probabilidad por persona y un AUC global de 0,835; ningún rango por persona |
| 2 | | | |
| 3 | | | |

**Nota del intento 1 (10:38):** el asistente pone el punto de corte en 25% (retener si 6.000 × p > 1.500, porque el plan se paga también a quien se iba a ir). Krylov usa 20% (1.500 / (1.500 + 6.000)), que solo es correcto si el plan no cuesta nada cuando sí hacía falta. Ver `estado/seguimiento.md`, «Hallazgo: punto de corte».

Si las tres respuestas coinciden y dicen cuánto se pueden equivocar, **no se usa** como argumento y la respuesta a «¿por qué no un chat?» se apoya solo en el mapa y en «¿Dónde mido?». No se nombra a ningún producto como el malo; se dice «un asistente genérico».

## Firma de fuentes y sponsors (tarea S-10)

Una persona abre cada enlace y anota si la página dice lo mismo que `pitch/CIFRAS.md`. Solo las cifras que se dicen en voz alta o van en una lámina. En «Verificó» va lo que la persona quiera que quede en un repositorio público (iniciales o «persona de PC 3»); después se copia a la columna «Verificó» de `CIFRAS.md`. Lo que dijo el agente a las 04:50 está en `CIFRAS.md`, «Revisión de fuentes».

| Id | Dónde se usa | Qué mirar | Enlace | ¿Coincide? | Verificó |
|---|---|---|---|---|---|
| N-01 | Apertura del pitch | Presentó tablas para decidir qué compartimento inundar; se usaron en todo el mundo. En el pitch: «a comienzos del 1900», sin fecha exacta | https://en.wikipedia.org/wiki/Aleksey_Krylov | Sí, en lo esencial (PC 3, 10:27): «después de 1900» trabajó en la inundabilidad de barcos y «sus tablas de inundabilidad se usan en todo el mundo». No da los años 1902 y 1903 (salen de la biografía) y atribuye a Makarov la idea de inundar compartimentos sanos. El pitch dice «a comienzos del 1900» y no nombra el barco: calza | (firma de una persona) |
| D-01 | Momento 2 | 1.470 personas, ficticio, creado por IBM, licencia ODbL | https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset | Sí (PC 3, 10:27, abierto en el navegador): «a fictional data set created by IBM data scientists»; licencia Open Database (ODbL); archivo de 227,98 kB, 35 columnas, 1.470 filas | (firma de una persona) |
| D-04 | Momento 4 | 155 muestras de suelo junto al río Mosa | https://rdrr.io/cran/sp/man/meuse.html | Sí, por el paquete (PC 3): la página describe el zinc en mg/kg junto al río Mosa pero no dice cuántas filas; `nrow(meuse)` en R da 155 (`datos/preparar/terreno.R`) | (firma de una persona) |
| K-11 | Mapa del terreno | 720 mg/kg de zinc: valor de intervención holandés, suelo estándar | https://enviroeng.eu/wp-content/uploads/2022/01/LISTA-HOLANDESA-2013.pdf (anexo 1, tabla 1) | Sí según el agente de las 04:50 (anexo 1, tabla 1: 720 mg/kg de materia seca, suelo estándar); copia en un sitio de terceros. No reabierto a las 10:27 | (firma de una persona) |
| A-01 | Lámina de negocio | SAP y Prior Labs, 4 de mayo de 2026; «más de 1.000 millones de euros en cuatro años»; no es el precio | https://news.sap.com/2026/05/sap-to-acquire-prior-labs-establish-frontier-ai-lab-europe/ | Sí (PC 3, 10:27): 4 de mayo de 2026; «more than €1 billion over the next four years»; «Terms of the deal were not disclosed»; cierre sujeto a aprobaciones | (firma de una persona) |
| P-01 | Lámina de negocio | Buk: hoy se verifica «+6.000 empresas»; en voz alta, «miles» | https://www.buk.cl/quienes-somos/buk-mejores-softwares-rh | Sí, «+6.000 empresas felices» (PC 3, 10:27). En voz alta, «miles» | (firma de una persona) |
| P-04 | Lámina de negocio | AgendaPro: más de 22.000 negocios | https://www.descubre.vc/noticia/agendapro-alcanza-50-millones-de-reservas-y-lanza-marketplace-regional-2026-08-20 | Sí (PC 3, 10:27): «más de 22,000 comercios en 17 países» | (firma de una persona) |

**Sponsors en el lugar** (`AGENTS.md`, «Sponsors»): mirar los carteles o preguntar a la organización. Web del evento revisada a las 10:27 (https://hack.platan.us/26-cl): once sponsors, Anthropic y Buk como principales, y ElevenLabs, Vercel, Render, Kairos, Kapso, CChC, AgendaPro, Copec y Lici. Calza con `AGENTS.md`.

| Pregunta | Respuesta | Hora |
|---|---|---|
| ¿Buk auspicia? (tarjeta «Caso tipo Buk») | Sí en la web del evento («sponsored by the big ones», junto a Anthropic). Falta mirarlo en el lugar | 10:27 |
| ¿AgendaPro auspicia? (tarjeta «Caso tipo AgendaPro»; si no, pierde el nombre) | Sí en la web del evento. Falta mirarlo en el lugar | 10:27 |
| ¿Vercel y Render auspician? (infraestructura) | Sí, los dos en la web del evento | 10:27 |
| ¿Anthropic auspicia? (D-34: se dice solo si la interpretación funciona a las 18:00) | Sí, sponsor principal en la web del evento | 10:27 |

## Prueba con extraños 1 (sábado 12:30)

| Qué dijo que hace (textual) | Qué dijo que simuló | Palabra que no entendió |
|---|---|---|
| | | |
| | | |
| | | |

## Prueba con extraños 2 (sábado 19:00)

| Qué dijo que hace (textual) | Qué dijo que simuló | Palabra que no entendió |
|---|---|---|
| | | |
| | | |
| | | |
