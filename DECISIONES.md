# Decisiones

Registro de solo agregar. No se edita ni se borra lo anterior: si una decisión cambia, se agrega otra que la reemplaza y lo dice. Lo mantiene `seguimiento`; cualquier rol puede pedir una entrada en su archivo de estado.

Formato: `D-NN · día hora · decisión · por qué · quién`.

---

**D-01 · sáb 21-nov 00:45 · Plan v2 generado.** Reemplaza al plan v1 y responde a la revisión adversarial. Detalle en `WORKPLAN.md`. · Propuesta del plan v2; el equipo la confirma o la cambia en PC-0.

**D-02 · sáb 21-nov 00:45 · Contrato entre computadores según `contratos/CONTRATO.md`.** Se congela en PC-0 (sáb 02:00); hasta entonces admite ajustes. Por qué: que producto avance sin esperar al entrenamiento. · Propuesta del plan v2; el equipo la confirma o la cambia en PC-0.

**D-03 · sáb 21-nov 00:45 · Una sola rama `main`, propiedad por directorio, estado en `estado/`.** Por qué: lo más simple que funciona para tres personas con sueño. · Propuesta del plan v2; el equipo la confirma o la cambia en PC-0.

**D-04 · sáb 21-nov 00:45 · La cuña es configuración (`cunas/`), no arquitectura.** La cuña principal se confirma en PC-2 (sáb 11:00) con la regla de `WORKPLAN.md`. · Propuesta del plan v2; el equipo la confirma o la cambia en PC-0.

**D-05 · sáb 21-nov 00:45 · Python 3.12 con `uv`, NumPy para simular, PyTorch + `zuko` para la red, sin MLX ni JAX.** CPU o MPS se decide con la skill `medir-rendimiento`. Por qué: es lo único que corre igual en el MacBook y en la nube si hay que salir. · Propuesta del plan v2; el equipo la confirma o la cambia en PC-0.

**D-06 · sáb 21-nov 01:00 · Replanteo v3: el producto es un data scientist artificial con catálogo de motores; minería es un caso más.** Reemplaza el enfoque de D-01 centrado en sondajes. Motores de la hackathon: `regresion` (primero), `espacial` (segundo), `extremos` (opcional). Por qué: el pitch es reemplazar el cargo de data scientist con modelos avanzados ya entrenados, y tiene que mostrar un uso para cada sponsor. · Pedido del equipo; el detalle lo confirma en PC-0.

**D-07 · sáb 21-nov 01:00 · Producto terminado sáb 18:00; después solo demo y pitch.** Reemplaza el congelamiento de las 22:00. Ya no hay PC-4: los hitos son `pc0`, `pc1`, `pc2`, `pc3`, `congelado`, `entrega`. Por qué: es una hackathon y el equipo quiere la tarde para iterar. · Pedido del equipo.

**D-08 · sáb 21-nov 01:00 · Sin validación externa; primer cliente = plataformas de software con miles de clientes.** No se contacta a expertos, consultoras ni clientes. Queda una consulta de formato a la organización, una pregunta a mentores si pasan por la mesa y la prueba del pitch con extraños. Por qué: no hay contactos ni tiempo. · Pedido del equipo; el primer cliente es propuesta del plan.

**D-09 · sáb 21-nov 01:00 · `cunas/` pasa a `casos/`; la palabra «cuña» sale del proyecto.** Reemplaza D-04. Un caso de uso es una pregunta de negocio resuelta con un motor, datos y costos; agregar uno no toca código. «Cuña» queda solo en `GLOSARIO.md` como sinónimo de primer cliente. Por qué: no se entendía. · Pedido del equipo.

**D-10 · sáb 21-nov 01:00 · Capa de lenguaje con Claude (`claude-haiku-5-5`) solo para entender la pregunta y redactar tres frases.** Ve encabezados y estadísticas por columna, nunca filas ni valores, y no produce números. Con reglas fijas de respaldo. Por qué: Anthropic es sponsor y el producto necesita conversar, pero el cálculo lo hacen los motores. · Propuesta del plan; el equipo la confirma en PC-0.

<!-- Pendientes de decidir, con su hora:
- PC-0: destino de despliegue (producto).
- PC-0: dispositivo y presupuesto de entrenamiento (entrenamiento).
- PC-2: qué caso abre el demo (seguimiento).
- PC-3: opcionales, máximo dos: motor `extremos`, voz, WhatsApp, «¿dónde mido?».
-->

**D-11 · sáb 21-nov 01:10 · El objetivo es ganar la hackathon: el mejor demo y el mejor pitch del evento.** No se pide inversión ni pilotos; el cierre es la frase y un QR a la app en línea. · Confirmado por el equipo.

**D-12 · sáb 21-nov 01:10 · Los doce sponsors están confirmados, pero no se asume que estén en el jurado.** El momento «elijan una empresa» se mantiene porque la sala reconoce los nombres. · Confirmado por el equipo.

**D-13 · sáb 21-nov 01:10 · Cognition no se usa ni se menciona.** El equipo no tiene acceso a sus herramientas. · Confirmado por el equipo.

**D-14 · sáb 21-nov 01:10 · Los roles se toman por computador, sin importar quién.** Las tareas de cada rol son las de `WORKPLAN.md`, sección 6. · Confirmado por el equipo.

---

## Plan final (sáb 21-nov 03:00). Responde a la crítica v3

Las entradas D-01 a D-14 son historia: hablan de «Sondea», de «PC-0 a PC-3» y del rol `entrenamiento`. Lo que sigue las reemplaza donde lo dice.

**D-15 · sáb 21-nov 03:00 · El producto y la empresa se llaman Krylov.** Reemplaza el nombre de trabajo «Sondea» en todo: pantalla, guion, láminas, variables de entorno (`KRYLOV_*`), archivos de entrega. El relato del nombre (Alekséi Krylov y sus tablas calculadas por adelantado) abre el pitch. · Decisión del equipo.

**D-16 · sáb 21-nov 03:00 · El momento estrella del show es «¿Dónde mido?».** Deja de ser opcional. Orden del show: problema y nombre → respuesta de rotación con deslizadores → archivo malo con la nube de simulaciones → terreno y «¿Dónde mido?» → cartera en diez segundos → cierre con QR. Lo primero que se corta si falta tiempo es la cartera, no el mapa. Por qué: en el plan anterior la simulación no se veía y ningún momento necesitaba la red; así se pierde en el track Simulaciones. · Crítica v3, punto 1 y 4.

**D-17 · sáb 21-nov 03:00 · Se corta: la red de `regresion`, el motor de eventos raros, la voz, WhatsApp, la caja de pregunta libre, las tres tarjetas sintéticas (licitaciones, obras, cargadores) y el análisis a mano con cronómetro.** Quedan cuatro tarjetas: rotación (tipo Buk), terreno, inasistencias (tipo AgendaPro) y crédito. Por qué: nada de lo cortado aparece en el show nuevo y juntos liberan cerca de siete horas. · Crítica v3, tabla «Cortar y agregar».

**D-18 · sáb 21-nov 03:00 · Los colores son decisiones y el número grande es «lo que te cuesta no saber».** Reemplaza las definiciones de «tres colores» y «plata en duda» de D-02. Estados `actuar`, `no_actuar`, `en_duda`. Regla única para los dos motores: en duda si hay más de 10% de probabilidad de que la decisión cambie al saber más. El número es el valor de despejar la duda y vale cero donde no la hay. Detalle en `contratos/CONTRATO.md`, sección 3. Por qué: los rótulos anteriores decían «se va, seguro» a alguien con 22% de riesgo, y la cifra anterior daba casi lo mismo con cualquier dato. · Crítica v3, puntos 2 y 3.

**D-19 · sáb 21-nov 03:00 · La noche de cómputo es para la red espacial, y esa red devuelve el mapa completo.** `regresion` usa el método exacto y no tiene red. La red espacial recibe una grilla fija de 32×32 con un canal que marca dónde hay medición y devuelve, para cada bloque, el valor esperado y su margen; se entrena con terrenos simulados al vuelo. La versión que devuelve los cuatro parámetros del terreno con un flujo normalizador queda como opcional (A-16). Por qué la diferencia con lo que propone la crítica: con el mapa directo, rehacer 500 análisis es una sola pasada de 500 grillas; con parámetros más un cálculo exacto por versión, ese cálculo vuelve a ser el cuello de botella justo en el momento estrella. · Crítica v3, punto 5, y decisión del plan.

**D-20 · sáb 21-nov 03:00 · La URL pública funciona sin servidor.** Toda respuesta del recorrido se precalcula y se sube como archivo junto a la web (Vercel). La API en Render queda para «Sube tus datos». El cálculo en vivo corre en el computador del escenario. La red se sirve con `onnxruntime`, nunca con `torch`. Por qué: el servidor gratuito tiene 0,1 de procesador y 512 MB y se duerme; se caería cuando la sala escanee el QR. · Crítica v3, y límites verificados en la documentación de Render.

**D-21 · sáb 21-nov 03:00 · Los puntos de control se llaman hitos (H0 a H3) y el horario parte a las 03:00.** Tags `h0`, `h1`, `h2`, `h3`, `congelado`, `entrega`. Los computadores son PC 1 (producto), PC 2 (amortizacion) y PC 3 (seguimiento); el rol `entrenamiento` pasa a llamarse `amortizacion`. Cada uno tiene su archivo `PC*.md`. Reemplaza los horarios de D-07; las 18:00 no se mueven. Por qué: «PC-1» se confundía con «PC 1». · Decisión del plan.

**D-22 · sáb 21-nov 03:00 · Se trabaja en dos repositorios espejo con un solo `git push`.** `platanus-hack/platanus-hack-26-cl-team-5` (oficial, público, se hace `pull` de aquí) y `Silent-math/krylov` (espejo, de aquí despliegan Vercel y Render). El plan completo se sube al repositorio, que es público: no se sube nada que no pueda leer un juez o un rival. Reemplaza D-03 en lo del repositorio único. Por qué: lo exige el README de la organización, y tres computadores necesitan compartir el estado por git. · Instrucción de la organización y decisión del equipo.

**D-23 · sáb 21-nov 03:00 · Validación con personas: se mantiene D-08, con dos ajustes.** No se sale a buscar expertos ni clientes y el plan no depende de nadie. Ajustes: la prueba con extraños se hace dos veces (12:30 con el guion v1 y 19:00), y si en el lugar hay alguien de Buk a mano, se le hace una pregunta de cinco minutos (`pitch/MENSAJES.md`). La meta de ingresos del primer año sale del pitch: se muestra solo la unidad (por cada 1.000 empresas activas). · Crítica v3, ajustada a la decisión previa del equipo.

**D-24 · sáb 21-nov 03:00 · Cifras: lo que se dice en voz alta se midió con datos reales.** La exactitud que se dice es la del examen con datos reales reservados; la medida en simulaciones va en la lámina técnica. Sale la cita de la prueba pública de 2024 y entra una prueba propia con un asistente genérico (S-09), sin nombrar a Claude como el malo. Ninguna frase del guion afirma un resultado antes de medirlo. Los costos por defecto de rotación y crédito cambian (K-01 a US$ 1.500, K-03 a US$ 800) para que el punto de corte quede cerca de la tasa real y la pantalla muestre los tres colores; siguen siendo supuestos, se dicen así y el deslizador los cambia en vivo. · Crítica v3.

**D-25 · sáb 21-nov 03:00 · Las herramientas se eligen con `STACK.md`.** Python 3.12 con `uv`; PyTorch para entrenar y ONNX para servir; Vite, React y TypeScript; FastAPI. La capa de lenguaje parte con `claude-opus-5-5` en esfuerzo bajo y pasa a `claude-haiku-5-5` si la llamada medida supera 3 segundos. Reemplaza D-05 y el modelo de D-10. Cada tabla de alternativas trae su regla para cambiar. · Decisión del plan; el equipo puede cambiarla con una entrada nueva.

**D-26 · sáb 21-nov 03:00 · Krylov es inferencia basada en simulación amortizada, caso por caso: cuatro motores, cada uno con su modelo generativo y su red.** Reemplaza la parte de D-17 que cortaba la red de `regresion`, reemplaza D-19 completa y cambia el contrato antes de H0.
- **Qué cambia.** `regresion` deja de existir como motor y como enfoque. Los motores son `supervivencia` (rotación: Weibull con censura, spline del sueldo, efecto por cargo y un compromiso latente que genera las cuatro encuestas), `jerarquico` (inasistencias: propensión por paciente y efecto por barrio), `estados` (crédito: cadena de estados ocultos sobre seis meses de historial) y `espacial` (terreno: proceso gaussiano anisotrópico con tendencia por la distancia al río). Cada uno tiene un modelo generativo explícito, un simulador, un codificador de conjuntos más un flujo normalizador condicional entrenado con NPE, y lo local resuelto exacto en NumPy. Detalle: `WORKPLAN.md`, sección 11.
- **Por qué.** El plan decía que Krylov «practicó con millones de casos simulados» y en tres de las cuatro tarjetas no era cierto: `regresion` no tenía red, y la red espacial aprendía el mapa y no el posterior de un modelo generativo. Un juez técnico, o la revisión automatizada del código, lo ve leyendo `nucleo/`.
- **Contrato.** Ids de motor nuevos; una variable `KRYLOV_MOTOR_<ID>` por motor con valores `red` o `mcmc`; un sello por motor; la nube son simulaciones del predictivo a priori con dos detectores (ejes con nombre, que es lo que se dibuja, y distancia en los resúmenes aprendidos); `analizar_regresion.json` pasa a llamarse `analizar_tabla.json`; `espacial` ahora trae `factores`. La forma de `analizar` no cambia.
- **Plan B por motor.** El que no pase la validación a su hora (H2 por motor; tope 16:00) sale con el posterior del MCMC de referencia precalculado, rotulado «precalculado», y el guion no dice que responde la red. Orden de corte: `estados`, `jerarquico`, `supervivencia`, la cabeza de flujo de `espacial`. La cabeza de mapa y «¿Dónde mido?» no se cortan.
- **Se corta «Sube tus datos» (P-12) y la capa de lenguaje.** Cada motor responde una familia de archivos, no un CSV cualquiera. Anthropic aparece solo como la herramienta con que se construyó el producto. Reemplaza lo que D-25 dice de la capa de lenguaje.
- **Cómputo.** De noche, `espacial` en PC 2 y `supervivencia` en PC 3; de día, `jerarquico` en PC 3 y `estados` en PC 2. PC 1 no entrena. Dos sesiones de Claude Code en PC 2, repartidas por archivos.
- **Lo que se pierde, dicho:** el respaldo instantáneo de tres tarjetas, la generalidad de «cualquier pregunta de sí o no», los opcionales y el colchón de PC 2. Comprometido para las 18:00: los cuatro modelos con su MCMC y las redes de `espacial` y `supervivencia`; las otras dos redes son meta.
- **Archivos todavía sin actualizar** (se corrigen en las rondas después de H0; hasta entonces manda esta entrada): `AGENTS.md`, `GLOSARIO.md`, `STACK.md`, `SKILLS.md` y las skills, `RESUMEN.md`, `PC1_PRODUCTO.md`, `PC3_SEGUIMIENTO.md`, `pitch/`, `estado/TABLERO.md` y el resto de `WORKPLAN.md`.
· Decisión del equipo.

**D-27 · sáb 21-nov 03:50 · H0: pasa en parte; el tag `h0` espera a la web.**
- **Pasa:** PC 2 y PC 3 empujan a los dos repositorios (los dos en el mismo commit). El contrato queda **congelado desde las 03:45**: `contratos/` no cambió desde el plan (1b740ac); cambiarlo exige una entrada aquí y aviso a los otros dos roles. PC 2 tiene dos sesiones de Claude Code trabajando (commits de las sesiones A y B), y PC 3 es el segundo computador de entrenamiento: el grupo `entrenar` está instalado y las 33 pruebas de `nucleo/` y `motor/` pasan aquí (03:47, `uv run pytest nucleo motor -q`).
- **No pasa:** PC 1 no tiene commits y la web no existe. Está arrancando (lo confirmó la persona de PC 3). Camino: PC 2 y PC 3 siguen, porque repositorio y contrato están; PC 1 sigue con P-01 y empuja apenas la web pinte un ejemplo fijo. El tag `h0` se pone en esa ronda. Si el primer despliegue (P-02) no sale antes de las 05:15, se deja para las 08:30.
- **Espejo público:** `Silent-math/krylov` ya es público (verificado por la API de GitHub a las 03:47). Vercel puede desplegar los commits de los tres.
- **Quién presenta:** se decide después. Pendiente para H1 a más tardar.
- **Datos crudos:** no hace falta copiar `datos_crudos/`. Rotación, terreno y crédito se bajaron de sus fuentes (S-03 a S-05). El archivo de inasistencias se bajó de una copia pública en GitHub del mismo archivo de Kaggle: 10.739.535 bytes, SHA-256 `9132d3e7…a27d`, 110.527 citas, 20,2% no llegó, 81 barrios (coincide con D-03). Queda en `datos/crudo/`, fuera del repositorio, por su licencia no comercial.
· Hito H0, con las respuestas de la persona de PC 3.

**D-28 · sáb 21-nov 04:00 · H0 cerrado: tag `h0`. El pitch se arma para 3 minutos.**
- PC 1 empujó P-01 a las 03:52. Verificado corriendo en PC 3 a las 03:58: la API local responde los ejemplos fijos (`POST /api/analizar`), la web pinta el inicio con las cuatro tarjetas y la respuesta de rotación y del terreno; con la API detenida, la web lee `web/public/estatico/` y el pie dice «Modo estático». Los tres empujan a los dos repositorios: H0 pasa completo y se pone el tag `h0`.
- S-02 tiene respuesta (`pitch/VALIDACION.md`): 3 minutos en generales y finales, por ahora; se presenta desde nuestro computador, con audio y video. El guion de 3 minutos pasa a ser el principal; los de 90 segundos y 5 minutos quedan de respaldo hasta la charla de las 20:00. Cifra J-04.
· Verificación de PC 3 y respuesta de la organización.

**D-29 · sáb 21-nov 04:36 (texto corregido a las 04:38) · Las horas del plan son topes, no horas de inicio: el trabajo se adelanta. Vale para los tres computadores.**
- Los tres computadores van adelantados (H0 cerrado, los dos entrenamientos corriendo desde antes de las 04:10). Esperar la hora escrita de cada tarea sería botar ese margen.
- **Regla:** cada tarea se empieza apenas existen sus insumos, en el orden de la lista de su rol. Al terminar una se toma la siguiente, sin esperar su hora. Los agentes de noche hacen primero su lista nocturna y después siguen con las tareas de día de su rol, en orden. Si a una tarea le falta un insumo (una red entrenada, muestras del MCMC, un archivo de otro rol), se construye contra el ejemplo fijo, datos simulados o la red sin entrenar, se anota en el estado «pendiente de <insumo>» y se pasa a la siguiente.
- **Lo que no se mueve**, porque no depende de la hora: un entrenamiento por computador; el MCMC nunca encima de un entrenamiento; los tiempos que van al guion se miden sin nada entrenando; un motor responde con `red` solo después de `validar-motor`; el contrato sigue congelado; cada rol en sus carpetas; lo que exige a una persona (enviar, desplegar, firmar una verificación, decidir, dormir) lo hace una persona; no se entrena después de las 16:00 y nada nuevo entra después de las 18:00.
- Los hitos H1 a H3 y los H2 por motor quedan como **plazo máximo**. Un hito se puede pasar antes: PC 3 lo verifica y pone el tag cuando se cumplen sus criterios.
- Adelantar no salta la verificación: «terminado» sigue siendo las cinco condiciones de `AGENTS.md`, y cada número sale de una ejecución.
- **Corrección:** entre las 04:44 y las 04:38 esta entrada y la regla 21 dijeron por error «solo PC 2». Vale el alcance original: los tres computadores.
· Pedido por Rodrigo (PC 2), que editó por esta vez `AGENTS.md`, `WORKPLAN.md`, los tres `PC*.md` y una línea del tablero para escribir la regla. Regla 21 de `AGENTS.md`.

**D-30 · sáb 21-nov 05:14 · Dos ajustes chicos de lo construido, registrados por PC 3.**
- **`estados` (crédito) se aparta de `WORKPLAN.md` 11.4** (lo decidió PC 2 a las 05:11 al mirar el archivo real): el atraso va en 5 niveles y no 6, porque el código 1 no aparece en los cinco meses más antiguos; θ queda en 33 parámetros y no 35; el prior es una normal independiente por parámetro en el espacio sin restricciones. Anotado en 11.4, en `pitch/LAMINAS.md` y en el borrador del README.
- **Los casos traen un bloque opcional `etiquetas`** (nombre en pantalla de cada columna o factor), a pedido de PC 2. Es un campo nuevo y opcional: no cambia la forma de nada de lo que ya existe; si falta, se muestra el nombre de la columna. Ya está en los cinco YAML.
· PC 2 (el modelo) y PC 3 (las etiquetas).

**D-31 · sáb 21-nov 05:36 · Madrugada sin hora fija de dormir; `jerarquico` con 20 parámetros; `supervivencia` sigue hasta las 08:30.**
- **Dormir a las 05:15 deja de ser obligatorio** (lo pidió Rodrigo a las 05:30 y ajustó A-05 y A-M1 a A-M3 en `WORKPLAN.md` 6.3). Cada persona decide cuándo duerme. Lo que no cambia: los dos entrenamientos siguen hasta las 08:30, no se corre MCMC encima de un entrenamiento, y las tareas de las 08:15 y 08:30 (S-06, S-06b, A-08) mantienen su hora. A las 05:36 la persona de PC 3 sigue despierta.
- **`jerarquico` se aparta de `WORKPLAN.md` 11.3** (PC 2, 05:26): 20 parámetros y no 22, con el primer coeficiente del spline fijo en 0, prior de suavidad sin τ y prior normal independiente. Anotado en 11.3, en `pitch/LAMINAS.md` y en el borrador del README. Su predictivo a priori calza con el archivo real (corrido en PC 3: percentiles 30 a 64).
- **`supervivencia` no se corta antes:** un SBC intermedio a las 05:35 (83 minutos, 3,9 millones de datasets) da cobertura del 90% en 0,904 y 0,898 en el peor grupo, contracción media 0,74, pero 15 de 32 parámetros con KS sobre el límite (cortes de las encuestas, λ, log k, μ_c): todavía no pasa. La pérdida sigue bajando y la tasa de aprendizaje recién empieza a bajar. `jerarquico` se lanza en PC 3 a las 08:30, como estaba.
· PC 2 (horario y modelo) y PC 3 (verificación).

**D-32 · sáb 21-nov 06:15 · `analizar` trae `unidad`; criterios del sello para los motores de tabla.**
- **`unidad` en `analizar`** (`{"singular", "plural"}`, copiado del YAML del caso): lo pidió PC 1 a las 05:04 y lo aprobó Rodrigo a las 05:52. Es un campo nuevo en el contrato congelado; no cambia ninguno de los que había. Con esto la web rehace el titular al mover los deslizadores sin leer el texto.
- **Criterios del sello de `estados`, `jerarquico` y `supervivencia`** (propuestos por PC 2 a las 06:12; PC 3 los confirma, aplican 11.8 de `WORKPLAN.md`): (1) «SBC sin sesgo visible» = cada parámetro con χ² de uniformidad bajo el 1% repartido entre los parámetros (Bonferroni) y rango medio a menos de 0,03 de 0,5; `espacial` sigue con 1% por parámetro (7 parámetros). (2) La cobertura del 90% que va al sello (`cobertura_90`) es la de **lo que se decide**: la probabilidad de cada unidad contra la del paso local con el θ verdadero, entre 85% y 95%; la de θ va en `cobertura_90_parametros`. (3) `cobertura_90_metodo_rapido`: la misma medida con el intervalo de Wald de la regresión logística, en las mismas simulaciones. La cobertura se cuenta por rangos del SBC, no con cuantiles (los cuantiles de 99 muestras dan 0,882 con un posterior perfecto).
- **Para que los cuatro sellos se lean igual, `supervivencia` usa los mismos criterios.** El SBC intermedio de D-31 (15 de 32 con KS sobre el límite, cobertura 0,904) se midió con el criterio anterior (KS al 5% sin repartir y cobertura por cuantiles): se vuelve a leer con este a las 08:30.
- **Queda para una persona, al validar cada motor de tabla:** si la nube se conecta al semáforo (`rojo_modelo`) en `estados` y `jerarquico`. El ensayo de PC 2 indica que el segundo detector podría marcar el archivo real de crédito por el uso del cupo (límite conocido de D-30); el sello escribe `nube_archivo_real_dentro`.
· PC 1 (pedido), Rodrigo (`unidad`), PC 2 (criterios) y PC 3 (confirmación).

**D-33 · sáb 21-nov 06:33 · Sello de `supervivencia`: los criterios de D-32 más dos, y dónde se valida.**
- Además de D-32, para pasar: (1) el archivo real de rotación cae dentro de la nube con los dos detectores (`nube_archivo_real_dentro`); (2) `rotacion_malo` cae fuera y, corregido, dentro. Propuestos por PC 2 a las 06:30; PC 3 los confirma. Ya se cumple con los ejes con nombre (M-29); el segundo detector espera a la red entrenada.
- **Dónde:** a las 08:30 PC 3 exporta y sube la red de `supervivencia` y lanza `jerarquico`, así que el sello de `supervivencia` (MCMC incluido) corre en **PC 2**, sin nada entrenando, después del sello de `espacial` y antes de lanzar `estados` (PC 2, 08:30 a 09:15). Nunca dos a la vez.
- Si con la red entrenada el segundo detector deja el archivo real de rotación fuera, la primera tarjeta del demo saldría en rojo. Salida ya escrita: `KRYLOV_NUBE_SEGUNDO_DETECTOR=aviso` la deja en amarillo con el motivo. **Lo decide una persona** al ver el sello.
· PC 2 (propuesta) y PC 3 (confirmación).

**D-34 · sáb 21-nov 07:12 · Krylov responde en un chat: el usuario elige el modelo, sube un archivo, la red amortizada lo resuelve y un modelo de lenguaje cuenta el resultado en palabras.** Reemplaza lo que D-26 corta sobre «Sube tus datos», la capa de lenguaje y Anthropic.

- **Qué cambia.**
  - El inicio es un chat.
  - El usuario elige uno de los cuatro modelos según lo que quiere preguntar: `supervivencia` (¿cuánto dura y quién se va?), `jerarquico` (¿quién falta?, con tendencia propia por persona y por grupo), `estados` (¿quién cae en problemas?, mes a mes) y `espacial` (¿qué manda en el terreno y dónde mido?).
  - Adjunta un archivo: uno de los cuatro del demo o uno propio.
  - Asigna cada columna a su papel en el modelo, con un selector que la app rellena según el tipo de columna.
  - La red del motor responde en milisegundos con la misma forma que `analizar`. La respuesta (titular, número grande, tres colores, deslizadores, qué pesa, examen, semáforo) se pinta dentro del chat.
  - Un modelo de lenguaje escribe la interpretación de ese JSON.
- **Por qué.** El valor de amortizar está en que **cualquier archivo de la misma familia** se responde al instante, no solo el del demo. Con un solo archivo por motor, eso no se veía en pantalla. Las redes que entrenan desde la madrugada ya son el motor de modelado del data scientist artificial; el chat solo lo deja a la vista.
- **El motor no depende del caso, pero sí del esquema.** Cada red se entrenó con papeles fijos. `supervivencia`: id, evento, tiempo, grupo, exactamente 3 efectos, 1 efecto suave y 4 encuestas ordinales de 1 a 4 (`nucleo/supervivencia.py`, `N_EFECTOS`, `N_ENCUESTAS`). Los papeles de los otros tres motores los confirma PC 2. Un archivo con otro número de columnas por papel nunca lo vio la red al practicar: el semáforo responde `rojo_modelo` y dice qué falta. **Los entrenamientos en curso no cambian.**
- **El modelo de lenguaje solo interpreta.**
  - No elige el motor, no calcula y no inventa cifras.
  - Recibe el JSON de la respuesta y devuelve un texto corto.
  - El servicio revisa que cada número del texto esté en el JSON. Si alguno no está, o si no hay clave o no hay internet, se muestra la plantilla de `casos/textos.yaml`.
  - La clave vive en una variable de entorno de Render y nunca entra al repositorio.
- **Dónde viven las redes.**
  - `validar-motor` las exporta a `motor/artefactos/<motor_id>/` (`codificador.onnx`, un solo archivo desde las 05:11, `flujo.npz`, `config.json`, `sello.json`, `nube.npz`), y esa carpeta se versiona.
  - `nucleo/` las carga con `onnxruntime` y NumPy, sin `torch`.
  - La API de Render se construye desde el espejo y trae esos archivos. Un archivo subido va a `POST /api/analizar_archivo` en Render.
  - Vercel solo sirve la web y las respuestas precalculadas de los archivos del demo.
  - Ninguna red corre en el navegador.
- **Modo estático.** Los cuatro archivos del demo tienen su respuesta y su interpretación precalculadas en `web/public/estatico/`, y la interpretación va rotulada. El QR y el escenario hacen el recorrido completo sin servidor. La subida de un archivo propio funciona solo cuando la API responde; si no responde, el chat lo dice.
- **Contrato** (cambio con aviso a los tres roles; detalle en la sección 4):
  - `nucleo/api.py` suma `papeles(motor_id)` y `analizar_archivo(motor_id, tabla, columnas, costos)`.
  - `servicio/` suma `POST /api/analizar_archivo` y `POST /api/interpretar`.
  - Lo que ya existe no cambia de forma.
- **Qué no cambia:** los cuatro motores y sus modelos generativos, los entrenamientos y sus horas, el MCMC como referencia y plan B (rotulado «precalculado»), los tres colores como decisiones, los deslizadores en el navegador (`decision.ts`), el semáforo, la nube, «¿Dónde mido?», la cartera, la regla de cifras registradas y el cierre a las 18:00.
- **Riesgos.**
  - Render gratis tiene 0,1 de procesador y 512 MB, y se duerme. Se mide la red con un archivo de 2.000 filas en Render; si pasa de 2 s, el plan B es Funciones de Python en Vercel (`STACK.md`, 2.6).
  - GitHub no acepta archivos de más de 100 MB. PC 2 confirma el tamaño de `codificador.onnx` (desde las 05:11 lleva los pesos dentro).
  - **La API de Render todavía no existe** (a las 07:11, `estado/producto.md` dice «sin desplegar»): la subida de un archivo propio y la interpretación en vivo dependen de desplegarla primero.
  - **El esquema es fijo** (3 efectos, 1 suave y 4 encuestas en `supervivencia`): casi ningún archivo propio calza. Para el escenario se prepara un archivo del mismo esquema que no sea el del demo, y se dice que es de prueba.
  - **El guion de 3 minutos ya no cabía** (176 s de habla): si se muestra la subida en el escenario, sale primero la cartera.
  - El modelo de lenguaje tarda unos segundos: los números salen primero y el texto llega después, sin bloquear.
  - Los archivos subidos caen fuera de lo que la red conoce mucho más que los del demo, así que los dos detectores de la nube tienen que correr también sobre ellos.
- **Orden de corte**, si a las 16:00 no está: primero la interpretación del modelo de lenguaje (queda la plantilla), después la subida de un archivo propio (quedan los cuatro del demo dentro del chat). El chat con los archivos del demo no se corta.
- **Lo que se gana, dicho:** el jurado ve que la misma red responde un archivo que no es el del demo, y Anthropic pasa a estar integrado de verdad, si funciona a las 18:00.
- **Aprobación:** la persona de PC 3, a las 07:12, con los seis puntos de lo que no calza a la vista (`estado/seguimiento.md`, «Propuesta de PC 1: chat»). Avisado a PC 1 y PC 2 en el tablero.
· Propuesta de PC 1, decisión del equipo.

**D-35 · sáb 21-nov 07:40 · El modelo de lenguaje propone el calce de columnas, el usuario lo confirma y las redes aceptan papeles opcionales.** Enmienda D-34. Krylov son cuatro modelos para cuatro preguntas (¿a quién conviene retener?, ¿qué citas conviene confirmar?, ¿a quién le apruebo el crédito?, ¿dónde limpio y dónde mido?) que responden el archivo de **cualquier negocio** con esa pregunta.
- **Qué cambia.**
  - **El calce lo propone un modelo de lenguaje.** Las columnas de un negocio casi nunca se llaman ni vienen como las del entrenamiento. `servicio/` arma un resumen por columna (nombre, tipo, valores distintos, rango, porcentaje vacío y tres valores de ejemplo) y se lo pasa al modelo de lenguaje junto con `papeles(motor_id)`. **Nunca manda filas completas.** El modelo devuelve, por papel, qué columnas van, qué transformación aplicar, por qué y qué tan seguro está, más las columnas que no usa.
  - **El usuario ve el calce y lo confirma.** El chat muestra «Tiempo en la empresa ← `antiguedad_meses` (÷ 12) · porque…» y un clic cambia una asignación. Después el código valida tipos, cantidades y rangos, y la nube dice si el archivo calzado se parece a lo que la red practicó.
  - **Transformaciones de una lista cerrada**, ejecutadas solo en `nucleo/preproceso.py` (regla 3): `dividir` (meses a años), `anios_desde_fecha`, `dias_entre` (dos fechas), `si_no_a_binario`, `reescalar_ordinal` (por ejemplo, de 1–5 a 1–4), `log` y `categoria_a_codigo`. El modelo de lenguaje solo las nombra; nunca toca los datos.
  - **Papeles opcionales.** Cada papel lleva `minimo` y `maximo`. El simulador sortea en cada dataset cuántas columnas de cada papel están presentes; el codificador recibe una máscara de presencia por columna y la columna ausente va en cero. Si sobran columnas, el calce elige hasta `maximo` y el resto queda «no usadas», a la vista. Si un papel queda bajo su `minimo`, la respuesta es `rojo_datos` con el motivo («falta el tiempo en la empresa»).
    - `jerarquico` y `estados`: se lanzan con papeles opcionales (todavía no entrenan).
    - `supervivencia`: su corrida termina a las 08:30 con esquema fijo; PC 2 evalúa un ajuste corto desde ese punto de guardado con la máscara. Si no cabe, sigue con esquema fijo y `rojo_modelo` con su motivo.
    - `espacial`: x, y y valor son obligatorios; PC 2 dice si la tendencia puede ser opcional.
    - Validación: el posterior de un efecto ausente tiene que salir igual al prior; el SBC se mide por cantidad de papeles presentes.
  - **Examen.** Un archivo propio no trae respuestas escondidas: en su lugar va el sello del motor («lo comprobamos en casos simulados nuevos»).
  - **Sin clave o sin internet**, el calce lo propone la regla por tipo de D-34 y el usuario lo ajusta. Los archivos del demo pasan por el mismo calce, precalculado en `web/public/estatico/calce/<caso>.json` y rotulado.
- **Por qué.** Con esquema fijo y selector por tipo, casi ningún archivo propio calzaba (riesgo escrito en D-34). El producto es «cuatro preguntas para cualquier negocio», y eso exige leer columnas que no se llaman como en el entrenamiento y aceptar menos columnas de las que se simularon.
- **Contrato** (cambio con aviso; detalle en `contratos/CONTRATO.md`): `papeles()` suma `minimo`, `maximo` y `texto_largo`; `analizar_archivo(..., columnas)` acepta además `{papel: {"columnas": [...], "transformacion": {...}}}`; ruta nueva `POST /api/calce`.
- **Personas.** «¿Mis datos salen de la empresa?»: al modelo de lenguaje solo van los nombres y un resumen de las columnas, nunca filas.
- **Riesgos.**
  - Carga para PC 2 el día del camino crítico. `jerarquico` se lanza a las 08:30 en PC 3: los papeles opcionales tienen que estar antes en su simulador, o el lanzamiento espera. Lo deciden PC 2 y PC 3.
  - Con papeles opcionales, la red aprende un problema más difícil con el mismo presupuesto. Si el sello no pasa, el motor vuelve al esquema fijo.
  - El modelo de lenguaje puede equivocarse en el calce: lo atajan la validación, la confirmación del usuario y la nube.
- **Orden de corte**, antes que lo de D-34: 1) el calce por modelo de lenguaje (queda la regla por tipo); 2) los papeles opcionales de `supervivencia` (queda el esquema fijo); 3) los de `jerarquico` y `estados`, si su sello no pasa.
- **Aprobación:** el equipo, conversado en el grupo. Lo registra PC 1 a pedido de su persona, sin pasar por PC 3. Aviso a PC 2 por Discord.
· Decisión del equipo.

**D-36 · sáb 21-nov 09:23 · H1 (08:45, corrido a las 09:23): pasa. Tag `h1`. Dos alertas para el camino crítico.**
- **Pasa:** (1) puntos de guardado de toda la noche en los dos computadores: `espacial` en PC 2 de 03:50 a 08:30 (7.750.592 terrenos, 279,6 min) y `supervivencia` en PC 3 de 04:05 a 08:30 (12.739.616 datasets, 267,5 min), uno cada 10 minutos, sin cortes; (2) la URL pública responde (página y respuestas precalculadas con 200, entre 0,47 y 0,74 s); (3) lo de la noche lo revisó una persona en cada computador: la de PC 3 siguió cada ronda y aprobó D-34; Rodrigo estuvo en A-M3 (07:31); la persona de PC 1 escribió D-34 y D-35. El paso local y el MCMC de `supervivencia` y `espacial` existen (A-N2 06:20, A-N3 04:49): lo de PC 2 no se corre.
- **Hecho después de las 08:30:** la red de `supervivencia` exportada y subida (13b3e42); `jerarquico` con papeles opcionales (D-35) entrena en PC 3 desde las 08:52 hasta las 11:30.
- **Alerta 1, PC 2 detenido desde las 08:30:** A-08 (sello de `espacial`), el sello de `supervivencia` (D-33) y el lanzamiento de `estados` esperan a Rodrigo. Es el camino crítico del H2 de las 12:15 (terreno y rotación) y del de las 14:00 (crédito). Si a las 10:00 no partió A-08, el H2 de `estados` corre al tope de las 16:00 y se decide en la ronda si `estados` sale con el MCMC precalculado.
- **Alerta 2, PC 1 sin código desde las 05:03:** P-12 (a) tiene tope 10:30. Si a las 10:30 no está en `main`, en la ronda se adelanta el orden de corte de D-34 y D-35: se cortan el calce por modelo de lenguaje y la interpretación, y queda el chat con los archivos del demo.
· Hito H1, con la aprobación de la persona de PC 3.

---

## Pivote a minería (sáb 21-nov 12:10)

Las entradas D-15 a D-36 hablan de cuatro tarjetas (rotación, inasistencias, crédito, terreno) y de los motores `supervivencia`, `jerarquico` y `estados`. Desde aquí son historia, salvo donde D-37 dice que algo se conserva.

**D-37 · sáb 21-nov 12:10 · Krylov pasa a ser el «Artificial Data Scientist de la minería»: cinco decisiones de una mina, cada una con su motor; se parte del motor `espacial`, que ya está validado, y los otros cuatro se incorporan.** Reemplaza de D-26 la lista de motores y de casos, de D-17 las cuatro tarjetas, de D-16 el orden del show y de D-23 y D-12 lo que toca a Buk y AgendaPro como casos. La referencia técnica es el documento del equipo «Inferencia Bayesiana Amortizada para la Gran Minería Chilena»; este plan lo baja a lo que cabe en lo que queda de hackathon y lo cuenta sin jerga.

- **Por qué.** Lo único validado de punta a punta es el motor espacial (sello PASA a las 09:39; «¿Dónde mido?» rehace 228 análisis en 0,69 s). Rotación no pasó su sello y crédito e inasistencias no tienen veredicto. Con cuatro industrias distintas el relato era ancho y poco profundo, y el criterio de impacto premia «la profundidad por sobre el alcance». En minería una misma idea (calcular antes, decidir al instante) sirve para cinco decisiones que no esperan y valen mucha plata, y en Chile cualquier jurado entiende por qué importa.
- **Qué es ahora.** Un data scientist artificial para una mina. Recibe los datos de una decisión operacional y responde al instante qué conviene hacer, cuánto cuesta no saber y dónde conviene medir más; y avisa cuando los datos no sirven. La frase no cambia: «Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo»; el remate pasa a «porque ya practicó con millones de minas simuladas».
- **Los cinco casos**, con la pregunta que ve el jurado:

  | # | Caso (`casos/`) | La pregunta, en simple | Motor | Estado al pivote |
  |---|---|---|---|---|
  | 1 | `leyes` | ¿Este bloque de roca va a la planta o se aparta? ¿Y dónde tomo una muestra más? | `espacial` | **Red validada.** Corre hoy con un banco minero simulado (verde; 480 análisis rehechos en menos de 1 s) |
  | 2 | `taludes` | La pared del rajo o el muro del tranque se mueve: ¿es ruido o va a ceder? ¿Cuánto falta? | `deformacion` | Por construir |
  | 3 | `flotacion` | ¿Se me está yendo cobre al relave? ¿Qué línea de la planta conviene ajustar? | `cinetica` | Por construir |
  | 4 | `flota` | ¿Qué camión conviene parar antes de que falle en la rampa? | `desgaste` | Por construir |
  | 5 | `sismicidad` | Después de una tronadura bajo tierra: ¿puede volver a entrar la gente? | `sismico` | Por construir |

- **Lo que se conserva sin tocar:** el nombre y su relato; el motor `espacial` con su red, su sello y sus cifras medidas (M-01, M-02, M-08 a M-10, M-13); los tres colores como decisiones y «lo que te cuesta no saber» (D-18); el chat, el calce y la interpretación (D-34, D-35); el modo estático (D-20); los dos repositorios (D-22); las horas como topes (D-29); el plan B rotulado «precalculado»; la regla de cifras. El caso `terreno` (suelo real junto al río Mosa) queda fuera del inicio, como el examen con datos reales del motor espacial.
- **La forma de las respuestas no cambia.** Los cuatro motores nuevos responden con la forma de lista que ya pinta la web (`unidades` con `muestras_p`): las unidades son sectores del muro, líneas de la planta, camiones y sectores de la mina. Se agrega un solo campo opcional, `curva` (lo medido y lo que Krylov cree que viene, con su rango), para dibujar el abanico de cada unidad. Los archivos de estos casos son **series**: una fila por medición, con `unidad`, `tiempo` y `valor`. Detalle en `contratos/CONTRATO.md`.
- **Motores chicos, a propósito.** La lección de la noche: un modelo de 7 parámetros pasó su sello y uno de 32 no. Cada motor nuevo tiene entre 5 y 7 parámetros globales, comparte un andamio (`motor/comun/series.py`: codificador por unidad, flujo global y un flujo local chico por unidad) y entrena en una ronda de unos 100 minutos. Los modelos completos del documento técnico (dominios geológicos, ecuaciones rígidas de varias fases, estado espacial con miles de nodos) quedan como hoja de ruta, y se dice así. Ecuaciones: `WORKPLAN.md`, sección 11.
- **Orden de incorporación y cómputo.** Ronda 1 (lanzar antes de las 14:30): `cinetica` en PC 2 y `deformacion` en PC 3. Ronda 2 (lanzar antes de las 16:30): `desgaste` en PC 2 y `sismico` en PC 3. Cada motor tiene primero su método lento precalculado (plan B). Se detienen los entrenamientos de `estados`, `jerarquico` y `supervivencia`: ya no se usan.
- **Horario.** El producto se sigue terminando el **sábado a las 18:00**: pantallas, recorrido y cinco tarjetas respondiendo. **Excepción única:** una red que ya estaba entrenando puede validarse y reemplazar al «precalculado» de su tarjeta hasta las **20:30** (cambia una variable y un rótulo; no entra ninguna pantalla). Después de las 20:30 no cambia quién responde. Hitos nuevos: H4 (14:30), H5 (16:30), H6 (18:00, tag `congelado`).
- **Orden de corte**, del primero que cae al último: `desgaste`, `sismico`, `cinetica`, `deformacion` (el orden inverso de factibilidad: para taludes hay datos reales abiertos y su método lento es tratable; para la flota no hay datos mineros públicos y su método lento es el más difícil). Una tarjeta sin red sale «precalculada»; sin método lento tampoco, sale del inicio y queda en el pitch como «hoja de ruta». **Nunca se cortan el mapa de `leyes` ni «¿Dónde perforo?».**
- **Se corta:** la cartera (vista 3) y las tarjetas de rotación, inasistencias y crédito. El código de `supervivencia`, `jerarquico` y `estados` se retira del repositorio antes de la entrega (tarea A-32), para que la revisión del código lea un producto minero. La nube («sabe cuando no sabe») se muestra donde exista; el semáforo rojo con su motivo funciona en los cinco.
- **Datos.** No hay datos públicos de faenas chilenas para estos problemas. Los archivos del demo son **simulados con la misma física, con una verdad escondida que el motor no ve, y rotulados «simulado»** (`datos/preparar/`). Donde exista un archivo real con licencia abierta, se usa y se dice: un agente encontró dos (sáb 12:20), los prismas de desplazamiento de un rajo australiano que falló (Zenodo 15003054, CC BY 4.0) y sondajes con cobre de un yacimiento real (Zenodo 7051975, CC BY 4.0); se incorporan en S-23 y S-24 si calzan con sus motores. Ninguna tarjeta lleva el nombre de una minera.
- **Sponsors.** Ya no hay casos con nombre de sponsor. Se dice Anthropic (un modelo de Claude propone el calce y escribe la interpretación; se construyó con Claude Code), Vercel y Render, y solo si funcionan a las 18:00.
- **Cifras del documento técnico que NO se usan** (un agente abrió las fuentes el sáb 12:30; detalle en `pitch/CIFRAS.md`): «menos de 2 horas» para decidir el destino de un bloque (lo documentado es 24 a 48 horas); «15 a 30 minutos» para evacuar o reingresar (los cierres son de 2 a 12 horas; lo que llega en minutos es el dato de cada sismo); «US$ 15.000 a 40.000 por hora» por un camión detenido (lo defendible es US$ 3.000 a 11.000); y que hay un reglamento nuevo de relaves (sigue vigente el DS 248).
- **Tareas.** Numeración nueva desde 21 para no chocar con lo ya hecho: P-21 en adelante, A-21 en adelante, S-21 en adelante. Los estados anteriores quedaron en `estado/historia/`.
- **Lo que se pierde, dicho:** tres redes en las que se invirtió la noche (más de 12 millones de empresas simuladas), los exámenes con datos reales de crédito e inasistencias, el gancho con el anfitrión y la cartera. **Lo que se gana:** un relato único, un caso estrella que ya funciona y cuatro decisiones más que cualquiera entiende.
- **Lo que una persona del equipo tiene que confirmar** (hasta entonces vale lo escrito): (1) la excepción de las 20:30; (2) el orden de las rondas; (3) que las tarjetas usen datos simulados rotulados; (4) quién presenta.
· Pedido del equipo. El detalle es propuesta del plan; el equipo lo confirma o lo cambia en el tablero.

**D-38 · sáb 21-nov 13:10 · El método lento de cada motor se corre al final, y cada modelo lleva un nivel explícito para el tamaño del dataset.** Reemplaza de D-37 «cada motor tiene primero su método lento precalculado (plan B)» y, de la sección 11 de `WORKPLAN.md`, los tamaños de dataset que eran casi fijos. No cambia la forma de ninguna respuesta.

- **Por qué lo primero.** El MCMC de referencia es lo que más tiempo de cómputo gasta, y con un entrenamiento por computador le quita minutos a las redes. Lo que primero interesa saber es qué da la inferencia amortizada; la comparación con el método lento se agrega después.
- **Orden por motor.** Modelo con su nivel de diseño del dataset → simulador y predictivo a priori contra el archivo del demo → red → prueba de humo → entrenar → validar con lo que no depende del MCMC (SBC global y local, cobertura de lo que se decide, examen con la verdad escondida, todo por tramos de tamaño) → exportar → `analizar` → app. El MCMC de los cinco motores va después de todo eso (tarea A-36).
- **Cuándo se adelanta.** Solo si dejarlo al final no es factible, y se anota en el estado con la hora. El caso previsto: una red no pasa su sello y esa tarjeta no tendría con qué responder a las 17:30. Para la ronda 1 se usa la ventana sin entrenamiento de las 16:10. Las redes de la ronda 2 validan a las 18:15: a las 17:30 el equipo decide por cada una entre detener su entrenamiento para adelantar el método lento de su archivo, o dejar la tarjeta fuera del inicio a las 18:00 y sumarla si su red pasa antes de las 20:30.
- **Presupuesto.** 10 minutos por dataset. Si el MCMC de un motor no converge en ese tiempo, se anota y se sigue.
- **El sello se escribe sin MCMC.** Los campos `mcmc_*` y `amortizacion` quedan en `null`, y «pasa» se decide con SBC, cobertura (también en el peor tramo de tamaño), examen y latencia. La comparación se agrega cuando exista; si contradice a la red (más de 0,3 desviaciones estándar en las medias de los parámetros globales, con el MCMC convergido), se informa en el sello y el equipo revisa el veredicto.
- **Se informa lo que salga, tal cual:** tiempo por dataset, r̂ y diferencia con la red. No se elige ni se degrada un método de referencia para que la red se vea mejor. Si el MCMC resulta rápido en un modelo chico, se dice. La comparación que se cuente tiene que ser cierta y decir exactamente qué se comparó (un análisis, rehacer cientos de análisis, o rehacerlo con cada dato nuevo). Qué se cuenta en el pitch lo decide el equipo con los números medidos.
- **Por qué lo segundo.** Krylov recibe datasets enteros, de tamaño distinto en cada uso. Una red que entrena con un tamaño fijo no extrapola al archivo de un usuario: antes del pivote, un archivo más chico que el del demo cayó fuera de lo simulado siendo de la misma familia (`estado/historia/amortizacion_hasta_el_pivote.md`, sáb 09:44).
- **El nivel de diseño del dataset.** Cada modelo jerárquico sortea, antes que sus parámetros, cuántas unidades hay, cuántas lecturas tiene cada unidad (distintas entre unidades), tiempos irregulares y lecturas faltantes. Va escrito en el primer grupo de cada bloque de ecuaciones de `WORKPLAN.md`, sección 11 (`Diseño del dataset:`), en el simulador y en el `config.json` de cada motor:

  | Motor | Unidades | Lecturas por unidad |
  |---|---|---|
  | `deformacion` | sectores: log-uniforme de 6 a 80 | de 24 a 200, hasta 15% faltantes |
  | `cinetica` | líneas: de 2 a 16 | celdas de 5 a 12; medidas, de 3 al total |
  | `desgaste` | camiones: log-uniforme de 8 a 120 | de 3 a 20 muestras, a intervalos irregulares |
  | `sismico` | sectores: de 2 a 16 | las genera el proceso (tope 300); ventana observada log-uniforme de 2 a 24 h |
  | `espacial` | muestras: log-uniforme de 30 a 400 (ya lo tenía) | no se reentrena; solo se documenta |

  Son puntos de partida: se ajustan con el predictivo a priori, y lo que quede manda desde el `config.json`.
- **En la red:** tensores con relleno y máscara hasta el máximo del motor; el tamaño entra además como dato explícito al codificador (el pooling normalizado no lo ve); cada lote de entrenamiento puede compartir un tamaño para no gastar relleno.
- **En la validación:** SBC y cobertura por tramos de tamaño, con el peor tramo en el sello (`peor_grupo`, `cobertura_90_peor_grupo`, que ya existían).
- **En el producto:** fuera del rango, `rojo_datos` con un motivo que nombra lo que hay y lo que el motor conoce; sobre el máximo, submuestra con semilla fija y aviso. `papeles()` y la tabla «Rangos que el motor conoce» de `contratos/CONTRATO.md` publican el mismo rango que el `config.json`. Los archivos del demo quedan bien adentro (36 sectores, 8 líneas, 40 camiones, 8 sectores y 340 pozos).
- **Qué se toca:** `WORKPLAN.md` (1.2, 6.1, 6.3, 6.5, 6.7, 6.8, 8 y 11), las tareas A-22, A-24, A-26, A-29, A-30, A-32 y A-35, la tarea nueva A-36, `PC2_AMORTIZACION.md`, las skills `entrenar-motor` y `validar-motor`, la tabla de rangos del contrato, y `estado/MODELOS.md` con el tablero en vivo, que desde ahora muestran el modelo de cada caso pieza por pieza.
· Pedido del equipo. Lo escribe PC 2 por encargo directo; PC 3 queda avisado en `estado/amortizacion.md`.

**Decisión abierta de D-38 · la toma una persona del equipo el sáb 21-nov a las 17:30 · `flota` y `sismicidad` no tienen con qué responder a las 18:00 si su red no validó.** Anotada por PC 3 a las 13:25, al revisar D-38 contra el resto del plan.

- **El problema.** Con el orden antiguo cada tarjeta tenía antes su método lento precalculado. Con D-38 ya no: las redes de la ronda 2 (`desgaste` y `sismico`) entrenan de 16:30 a 18:15 y validan después del cierre de las 18:00. A esa hora esas dos tarjetas no tienen ni red validada ni método lento.
- **Las dos salidas, por cada tarjeta y por separado:** (a) detener su entrenamiento a las 17:30 y adelantar el método lento de su archivo del demo (10 minutos de presupuesto): si converge, la tarjeta sale a las 18:00 rotulada «precalculado», y la red pierde esos minutos de práctica; (b) dejarla entrenando y fuera de `casos/INICIO` a las 18:00, y sumarla si su red pasa el sello antes de las 20:30 (la excepción de D-37).
- **Qué se sabe a las 17:30:** el avance de cada entrenamiento y los veredictos de la ronda 1 (16:10), que dicen si el andamio de series valida en una ronda. PC 3 lleva la pregunta a las 17:15 con esos números.
- **Hasta que alguien decida, vale (b):** la tarjeta sin respuesta de su motor sale del inicio a las 17:30 (`casos/INICIO`, P-27) y se nombra como hoja de ruta. El orden de corte no cambia: primero `desgaste`, después `sismico`.
- **No toca a la ronda 1:** `flotacion` y `taludes` validan a las 16:10 y, si no pasan, adelantan su método lento en esa ventana.
- **Respuesta para `sismicidad` · sáb 17:25 · decidió la persona de PC 3 (clementeferrer):** salida (b). `sismico` sigue entrenando hasta las 18:15 y no se adelanta su método lento. La tarjeta queda fuera del inicio a las 18:00 y entra si su red pasa el sello antes de las 20:30. A las 17:22 llevaba 1.696.000 datasets simulados en 67 minutos.
- **Respuesta para `flota` · sáb 17:36 · decidió la persona de PC 2 (Rodrigo):** salida (b). `desgaste` sigue entrenando hasta las 18:15 y no se adelanta su método lento. La tarjeta queda fuera del inicio a las 18:00 y entra si su red pasa el sello antes de las 20:30. A las 17:38 llevaba 5.836.800 flotas simuladas en 64 minutos.
· Respondida en parte (sismicidad). Falta `flota`.

**D-39 · sáb 21-nov 17:10 · El SBC local de los motores de series se decide por el tamaño de la desviación, y el examen se informa pero no decide el «pasa».** Completa D-32 (que fijó el criterio para los parámetros globales) y D-38 (que pidió «SBC global y local» sin decir cómo se decide el local). No cambia el contrato ni la forma de ningún sello.

- **Qué pasó.** `cinetica` (43,2 millones de plantas simuladas) y `deformacion` (1,68 millones de muros) fallaron un solo criterio, `sbc_local_sin_sesgo`, y pasaron los otros cinco. Con el criterio anterior no pasaban: χ² de uniformidad 92,2 en `log_k` de `cinetica` (umbral 23,6) y 208,9, 123,7 y 71,1 en los tres locales de `deformacion` (umbral 24,7). Esos números siguen en `validacion.json` (`chi2_uniformidad`).
- **Por qué el criterio anterior estaba mal armado para los locales.** El código aplicaba a los locales la prueba χ² de D-32, pensada para un rango por dataset (2.000). Los locales juntan todas las unidades de los 2.000 datasets (17.960 líneas, 50.800 sectores) contra el mismo umbral, y eso tiene dos defectos. (1) Con 9 a 25 veces más rangos, la prueba rechaza desviaciones de medio punto por caja, que con 2.000 rangos no alcanza a ver: la misma frase, «sin sesgo visible», exigía mucho más a los locales que a los globales. (2) Las unidades de un mismo dataset comparten η y no son independientes, que es lo que el umbral supone; medido, eso infla el χ² entre 1,8 y 2 veces en `cinetica` y entre 2,8 y 12 veces en `deformacion` (efecto de diseño por conglomerados).
- **El criterio nuevo, para cada parámetro local:** tamaño de la desviación w = √(χ²/n) bajo 0,1, y rango medio a menos de 0,03 de 0,5 (esto último no cambia). Con 10 cajas, w = 0,1 significa que las cajas se alejan en promedio 1 punto de su 10%. El 0,1 no se ajustó a estos datos: es el límite convencional de un efecto «chico» (Cohen) y es la misma vara del global, cuyo umbral con 2.000 rangos equivale a w ≈ 0,11. No depende de cuántas unidades se junten. Vale igual para los cuatro motores de series; los globales siguen con el χ² de D-32, y `espacial` no cambia.
- **Qué da con las redes del sábado 16:10.** `cinetica`: `log_k` 0,072 y `logit_rmax` 0,022. `deformacion`: `log_v` 0,064, `log_falta` 0,049 y `log_A` 0,037. Todos los rangos medios quedan a menos de 0,02 de 0,5. Pasan.
- **Lo que se descartó.** Probar con una unidad al azar por dataset: pasa o no según la unidad que toque (`log_k` pasa en el 88% de 300 sorteos; `log_v`, en el 92%) y bota el 90% de los rangos. El χ² corregido por conglomerados: es más justo que el anterior, pero sigue siendo una prueba cuyo rigor depende de n (`log_k` da 52,1; `log_A`, 25,6).
- **Lo que este cambio no borra, y va en `limitaciones` de cada sello.** En `cinetica` el sesgo de `log_k` es real y chico: el valor verdadero cae bajo el rango de 90% en 4,1% de los casos y sobre él en 5,5% (lo esperado es 5% y 5%). No llega a lo que se decide: la recuperación al final de la línea tiene χ² 10,1 juntando las 17.960 líneas, cobertura 0,905 y colas de 4,8% y 4,7%. En `deformacion`, en los sectores que se aceleran la red da una velocidad de fondo algo alta y un «cuánto falta» algo corto (diagnóstico de PC 3, `estado/seguimiento.md`, 16:28); lo que se decide mantiene su cobertura (0,905). Por eso `deformacion` sigue entrenando y se revalida antes de las 20:30.
- **El examen con la verdad escondida se retira como condición de «pasa».** `WORKPLAN.md` 11.8 y la skill `validar-motor` decían que su criterio quedaba en `criterios` del sello, pero ningún sello lo trae, y con 8 líneas o 36 sectores un examen no puede aprobar ni reprobar una red. Se sigue calculando, va en el sello (`examen`) y es lo que se dice en voz alta, con sus conteos.
- **Qué se toca:** `motor/comun/validacion.py` (`desviacion_w`, `sbc_local_sin_sesgo`), `motor/comun/series.py` (cada parámetro informa `desviacion_w`; los locales usan el criterio nuevo), `motor/comun/prueba_validacion.py`, las `LIMITACIONES` de `motor/cinetica/validar.py` y `motor/deformacion/validar.py`, `WORKPLAN.md` 11.8 y la skill `validar-motor`. Los sellos no se editan a mano: salen de volver a correr `validar`.
- **Cómo se repite:** `uv run python -m motor.<id>.validar` (2.000 datasets nuevos, semilla fija). La latencia de un sello revalidado con un entrenamiento corriendo se vuelve a medir a las 18:15.
· Análisis y propuesta de PC 2 (17:05); la acepta Rodrigo. Lo escribe PC 2 por encargo directo; PC 3 queda avisado en `estado/amortizacion.md`.

**H6 · sáb 21-nov 18:32 · Producto terminado, con tag `congelado`: tres tarjetas responden con su red en la app y una cuarta tiene su red validada; la URL pública no se pudo actualizar.** Punto de control corrido por PC 3.

- **Lo que pasa el criterio.** El recorrido en modo estático, en local y sin servidor (`?estatico=1`, la web de `main`): inicio con las tarjetas que responden, `leyes` con su mapa (147, 309 y 568 bloques; US$ 1.577.707) y «¿Dónde perforo?» (480 análisis), `taludes` (5, 2 y 29 sectores) y `flotacion` (2, 3 y 3 líneas), las tres rotuladas «responde la red». `pytest nucleo motor servicio`: 98 pasan.
- **Lo que no.** (1) La URL pública sigue mostrando la app de antes del pivote: Vercel limitó los despliegues por 24 horas (17:58). Lo resuelve una persona con otra cuenta o proyecto; mientras tanto el QR no se muestra. (2) El recorrido lo hizo un agente una vez, no una persona dos veces: queda para el ensayo de las 18:30.
- **Lo que entra hasta las 20:30 (excepción de D-37):** `sismicidad`, cuya red pasó su sello a las 18:15 y falta en el estático; y `flota`, si `desgaste` pasa. Nada más.
- **Motores:** `espacial`, `cinetica`, `deformacion` y `sismico` con sello PASA; `desgaste` sin veredicto. Ninguna tarjeta salió precalculada; el método lento de los cinco va al final (A-36).
· Hito. Si algo se rompe después, se vuelve al tag `congelado`.

**D-40 · sáb 21-nov 20:20 · Un sexto motor, `yacimiento` (un yacimiento en 3D leído desde sondajes), fuera del producto congelado.** Lo pide la persona de PC 3 a las 20:15, con el producto ya terminado (tag `congelado`, 18:32).

- **Qué pidió:** un problema amortizado más, relevante para la minería, con un dataset más complejo y realista que los cinco (un mapa con muchas covariables, que se pueda mostrar como un campo en tres dimensiones), caro para el método lento, que se pueda entrenar y comparar con MCMC en menos de 3 horas, con la misma arquitectura o parecida, **sin pisar ni interferir con lo que ya funciona**, y fácil de sumar al deck.
- **Qué se hace.** Carpeta nueva `yacimiento/` (modelo generativo, simulador, red, entrenamiento, validación, MCMC de referencia y sello propios). Modelo: ley de cobre en un modelo de bloques de 32 × 32 × 16 (16.384 bloques), proceso gaussiano anisotrópico en 3D con ocho covariables del modelo geológico y error de muestreo; 15 parámetros; de 15 a 60 sondajes por dataset. Red: U-Net 3D con cabeza de mapa y cabeza de flujo, como `espacial` pero en volumen. Demo: `pitch/deck/yacimiento.html`, una página aparte.
- **Lo que choca con el plan, dicho:** AGENTS dice «nada nuevo después del sábado a las 18:00» y «nada que no aparezca en `WORKPLAN.md`». Este motor es la excepción que pide una persona del equipo, y por eso **no entra a la app, ni a `casos/INICIO`, ni al contrato, ni toca `nucleo/`, `motor/`, `servicio/` o `web/`** (solo lee `motor/comun/flujo.py` y `nucleo/decision.py`). El recorrido del demo y el tag `congelado` no cambian.
- **Cómo se cuenta:** solo con los números de su sello (`yacimiento/artefactos/sello.json`) y como lo que es: un sexto modelo entrenado después del cierre, con datos simulados, que no está en la URL pública. Si su red no pasa su validación, se dice y no se muestra como resultado.
· Decide la persona de PC 3; lo escribe PC 3. PC 1 y PC 2 quedan avisados por el tablero.

<!-- Pendientes que decide una persona del equipo, con su hora:
- H0: hacer público el espejo `Silent-math/krylov`. Sin eso, Vercel no despliega los commits de quien no sea el dueño de la cuenta (STACK.md, 2.6). Lo decide el dueño de la cuenta. → Resuelto en D-27: ya es público.
- H0: quién toma cada computador y quién presenta. → D-27: quién presenta se decide después (a más tardar en H1).
- S-10 (10:00): lista real de sponsors en el lugar; si AgendaPro no auspicia, su tarjeta pierde el nombre.
- S-16 (15:20): qué hacer con la línea del README de la organización dirigida a modelos de lenguaje. Los agentes no la siguen por su cuenta.
- La partida de la ronda 1: ningún entrenamiento se lanza hasta que el equipo la dé (tope 14:30).
- D-37 (pivote a minería): confirmar la excepción de las 20:30, el orden de las rondas, los datos simulados rotulados y quién presenta.
- H5 (16:30) y tope de redes (20:30): red, o método lento adelantado (`mcmc`, rotulado «precalculado»), para cada tarjeta nueva.
- D-38, a las 17:30 (entrada «Decisión abierta de D-38», arriba): por cada tarjeta de la ronda 2 (`flota`, `sismicidad`), detener su entrenamiento para adelantar el método lento de su archivo, o dejarla fuera del inicio a las 18:00 y sumarla si su red pasa antes de las 20:30.
- Al validar `estados` y `jerarquico` (D-32): ¿la nube se conecta al semáforo? Depende de si el archivo real cae dentro de las simulaciones.
- D-34: la clave de Anthropic (`ANTHROPIC_API_KEY` en Render) la pone una persona; el despliegue de Render lo hace PC 1 con `desplegar`.
- Al validar `supervivencia` (D-33): si el archivo real de rotación cae fuera por el segundo detector, ¿`KRYLOV_NUBE_SEGUNDO_DETECTOR=aviso`?
- 03:15: confirmar que hay dos sesiones de Claude Code en PC 2 y que PC 3 es el segundo computador de entrenamiento (D-26 lo asume). → Confirmado en D-27.
-->
