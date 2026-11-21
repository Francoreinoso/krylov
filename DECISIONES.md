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

<!-- Pendientes que decide una persona del equipo, con su hora:
- H0: hacer público el espejo `Silent-math/krylov`. Sin eso, Vercel no despliega los commits de quien no sea el dueño de la cuenta (STACK.md, 2.6). Lo decide el dueño de la cuenta. → Resuelto en D-27: ya es público.
- H0: quién toma cada computador y quién presenta. → D-27: quién presenta se decide después (a más tardar en H1).
- S-10 (10:00): lista real de sponsors en el lugar; si AgendaPro no auspicia, su tarjeta pierde el nombre.
- S-16 (15:20): qué hacer con la línea del README de la organización dirigida a modelos de lenguaje. Los agentes no la siguen por su cuenta.
- H2 por motor (12:15, 13:00, 14:00; tope 16:00): red o plan B (`mcmc`, rotulado «precalculado») para cada tarjeta.
- Al validar `estados` y `jerarquico` (D-32): ¿la nube se conecta al semáforo? Depende de si el archivo real cae dentro de las simulaciones.
- D-34: la clave de Anthropic (`ANTHROPIC_API_KEY` en Render) la pone una persona; el despliegue de Render lo hace PC 1 con `desplegar`.
- Al validar `supervivencia` (D-33): si el archivo real de rotación cae fuera por el segundo detector, ¿`KRYLOV_NUBE_SEGUNDO_DETECTOR=aviso`?
- 03:15: confirmar que hay dos sesiones de Claude Code en PC 2 y que PC 3 es el segundo computador de entrenamiento (D-26 lo asume). → Confirmado en D-27.
-->
