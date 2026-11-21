# Láminas · esqueleto (S-12, adelantado por D-29)

> Portada y cierre van **dentro de la app** (tecla `L`, tarea P-13 de PC 1): aquí está su texto. Las tres de respaldo van en un archivo aparte que **solo se abre si preguntan**. Cada número lleva su id de `pitch/CIFRAS.md`; los corchetes no se muestran hasta medirlos. Portada, cierre y negocio, sin jerga (`GLOSARIO.md`). La lámina técnica sí usa los nombres técnicos.
>
> Para distinguir **lo construido de lo que es lámina** (regla 17): todo lo que se ve en la app existe; lo que solo está en una lámina lleva la marca «hoja de ruta».

## 1. Portada (en la app)

**Krylov**

Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo.

*(Debajo, chico:)* Platanus Hack 26 · track Simulaciones

## 2. Cierre (en la app)

**Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo.**

En un segundo, porque ya practicó con millones de mundos simulados.

- QR a **https://krylov-tan.vercel.app/** con la leyenda: «Escanea y mueve los costos tú».
- Franja de terrenos simulados pasando (PC 1, P-13): rotular «terrenos simulados».
- Equipo: [nombres, cuando cada persona confirme que se pueden mostrar].
- Pie chico: «Construido con Claude Code». Nada más sobre Anthropic.

**Por confirmar antes de decir «millones»:** la cifra de casos simulados de la noche (M-01, M-21). Si no llega a un millón en algún motor, la frase de la lámina dice «miles de mundos simulados» o el número exacto.

## 3. Respaldo técnico (archivo aparte; nombres técnicos)

**Krylov: inferencia basada en simulación amortizada, caso por caso.** Por motor: un modelo bayesiano generativo explícito, un simulador vectorizado, una red (codificador de conjuntos + flujo normalizador condicional, NPE) entrenada solo con simulaciones, y un MCMC de referencia (NumPyro, NUTS).

| Motor | Modelo en una línea | Entrenamiento | Sello (simulaciones nuevas) | Contra el MCMC | Examen con datos reales | Responde |
|---|---|---|---|---|---|---|
| Terreno (`espacial`) | Proceso gaussiano anisotrópico con tendencia en √(distancia al río) y error de medición; 7 parámetros | [M-01] terrenos, [M-02] min, MacBook Air M4 | Cobertura del 90%: [sello] | [sello] | [M-13] | [red o precalculado] |
| Rotación (`supervivencia`) | Weibull con censura, B-spline del sueldo, efecto por cargo y compromiso latente que genera cuatro encuestas; 32 parámetros | [M-21] empresas, [M-23] min, MacBook Air M3 | [sello] | [sello] | [M-03] | [red o precalculado] |
| Inasistencias (`jerarquico`) | Logístico con propensión por paciente y efecto por barrio; espera no lineal; SMS que cambia con la espera; 20 parámetros | [M-22], [M-23] | [sello] | [sello] | [pendiente] | [red o precalculado] |
| Crédito (`estados`) | Cadena de Markov oculta de tres estados con seis meses de emisiones; 33 parámetros | [M-22], [M-23] | [sello] | [sello] | [pendiente] | [red o precalculado] |

- **«¿Dónde mido?»:** rehace el análisis completo [M-08] veces en [M-09] segundos. Los mismos análisis con el MCMC: [M-10]. Un solo análisis lento del terreno tarda segundos; lo que se compara es rehacer los [M-08].
- **El método rápido de siempre** (regresión logística, kriging con parámetros fijos) cuando dice 90% acierta [P]% (M-11).
- **Qué no hace todavía:** archivos fuera de las cuatro familias; más de 2.000 filas por análisis; terrenos en tres dimensiones; más de 400 mediciones.

## 4. Respaldo de negocio (archivo aparte)

- **Primer cliente:** plataformas de software con miles de empresas cliente (tipo Buk o AgendaPro), que integran Krylov para darle un data scientist a cada una.
- **La unidad:** US$ 20 al mes por empresa que lo usa (C-05, **hipótesis sin validar**) → US$ 240.000 al año por cada 1.000 empresas activas (C-06, cálculo sobre esa hipótesis). Cada plataforma nueva es una sola venta.
- **Por qué ahora:** SAP anunció en mayo de 2026 la compra de Prior Labs, que entrena modelos con datos sintéticos para tablas, con el compromiso de invertir más de 1.000 millones de euros en cuatro años; no es el precio de compra (A-01).
- **En qué nos diferenciamos:**

| Frente a | Ellos | Nosotros |
|---|---|---|
| Subirle el archivo a un asistente genérico | [resultado de la prueba S-09, sea cual sea] | La misma respuesta siempre, con la duda medida en plata y un examen con datos reales |
| Modelos para tablas | Predicen una columna | Decimos qué hacer, cuánto cuesta no saber y dónde averiguar más; y un motor para datos con ubicación |
| Un data scientist | Días por análisis | [tiempo medido], para todas las empresas a la vez |

- **Lo que todavía no es ventaja:** la tecnología se puede copiar. Hoy la ventaja es el equipo y llegar primero. Se dice así.
- Buk: «miles» de clientes (P-01; hoy se verifica «+6.000» en su sitio). AgendaPro: más de 22.000 negocios (P-04). Sin citas de nadie: «todavía no hablamos con clientes».

## 5. Respaldo: qué existe hoy y qué es hoja de ruta (archivo aparte)

| Existe a las 18:00 (se ve en la app) | Hoja de ruta (solo lámina) |
|---|---|
| App en línea con cuatro preguntas, también sin servidor | Series de tiempo, eventos raros, segmentación |
| Cuatro modelos generativos, cada uno con su simulador y su método lento de referencia | Integración real con una plataforma |
| Terreno: red entrenada con terrenos simulados, validada; «¿Dónde mido?» y la medición simulada | Clientes, pilotos, precios validados |
| Rotación: red validada o «precalculado», **se dice cuál** | Terrenos en tres dimensiones |
| Inasistencias y crédito: red validada si pasó; si no, «precalculado». **Se dice cuál** | Subir un archivo cualquiera |
| Cuatro tarjetas con datos públicos (tres reales y una ficticia), con examen sobre respuestas reales escondidas | Datos de cualquier sponsor |
| Cartera de 1.000 empresas simuladas, rotuladas (o las precalculadas) | |

Se llena a las 17:30 con lo que de verdad quedó; lo que no esté, pasa a la columna derecha.
