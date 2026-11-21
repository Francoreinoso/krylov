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

<!-- Pendientes que decide una persona del equipo, con su hora:
- H0: hacer público el espejo `Silent-math/krylov`. Sin eso, Vercel no despliega los commits de quien no sea el dueño de la cuenta (STACK.md, 2.6). Lo decide el dueño de la cuenta. → Resuelto en D-27: ya es público.
- H0: quién toma cada computador y quién presenta. → D-27: quién presenta se decide después (a más tardar en H1).
- S-10 (10:00): lista real de sponsors en el lugar; si AgendaPro no auspicia, su tarjeta pierde el nombre.
- S-16 (15:20): qué hacer con la línea del README de la organización dirigida a modelos de lenguaje. Los agentes no la siguen por su cuenta.
- H2 por motor (12:15, 13:00, 14:00; tope 16:00): red o plan B (`mcmc`, rotulado «precalculado») para cada tarjeta.
- 03:15: confirmar que hay dos sesiones de Claude Code en PC 2 y que PC 3 es el segundo computador de entrenamiento (D-26 lo asume). → Confirmado en D-27.
-->
