# Krylov · Resumen del plan final

Sábado 21 de noviembre, 03:00. Para leer de pie. El detalle está en `WORKPLAN.md`.

## Lo primero

- **Se llama Krylov.** Un data scientist artificial que te dice qué conviene hacer, cuánto te cuesta no saber y dónde averiguar más.
- **La frase:** «Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo. En un segundo, porque ya practicó con millones de mundos simulados.»
- **El momento estrella es «¿Dónde mido?».** Un terreno real, tres pines con plata, un clic simula la medición y el mapa cambia. Es el único lugar donde la red es indispensable y donde la simulación se ve.
- **Producto terminado: sábado 18:00.** Entrega: domingo 08:00.
- **Lo único que no puede fallar esta noche:** que el entrenamiento de la red del terreno quede corriendo antes de dormir, con la tapa abierta.

## Cómo puntúa el jurado (está en las bases)

| Criterio | Peso | Dónde lo ganamos |
|---|---|---|
| Aspecto técnico | 25% | Red entrenada con simulaciones propias, validada tres veces. **Revisan el código de forma automática: el README cuenta** |
| Ambición | 20% | Una noche, un notebook sin ventilador, millones de terrenos simulados |
| Ejecución | 20% | Nada tarda más de 2 segundos; el QR abre la app y no se cae |
| Impacto | 20% | Plata en cada pantalla. Profundidad antes que alcance |
| Originalidad | 15% | No es un chat con un archivo |

El negocio no puntúa: una frase y una lámina de respaldo. Solo llegan a la final los equipos con demo funcional. Somos 12 equipos en Simulaciones.

## Qué cambió respecto del plan anterior

| Antes | Ahora |
|---|---|
| Sondea | Krylov, y el pitch abre con la historia del nombre |
| «¿Dónde mido?» era opcional | Es el momento estrella |
| Dos redes; la noche entrenaba la de regresión | Una red, la del terreno. La regresión usa el método exacto |
| «Se va, seguro» con 22% de riesgo | Los colores son decisiones: «conviene retener» |
| «Plata en duda» daba casi lo mismo con cualquier dato | «Lo que te cuesta no saber»: vale cero si no hay duda |
| Costos escritos por nosotros | Deslizadores que cambian la respuesta en vivo |
| Siete tarjetas, voz, WhatsApp, tercer motor | Cuatro tarjetas, dos motores |
| La URL dependía de un servidor gratuito | Todo el recorrido está precalculado junto a la web |
| «PC-1» era un punto de control | PC 1, 2 y 3 son los computadores; los puntos de control son hitos H0 a H3 |

## Quién hace qué

| Computador | Rol | Archivo | En una línea |
|---|---|---|---|
| PC 1 | Producto | `PC1_PRODUCTO.md` | Backend, frontend y despliegue. Primer despliegue hoy, antes de dormir |
| PC 2 | Amortización | `PC2_AMORTIZACION.md` | La red del terreno, los métodos exactos y cada número medido |
| PC 3 | Seguimiento | `PC3_SEGUIMIENTO.md` | Ronda cada 30 minutos, ajustes al plan, casos, pitch y entrega |

Da lo mismo quién toma cuál. PC 2 es el MacBook Air M4.

## La línea de tiempo

| Hora | Qué |
|---|---|
| 03:00 | Arranque: plan al repositorio, clonar, espejo, entorno |
| **03:45 · H0** | Los tres empujan a los dos repositorios; la web muestra un ejemplo |
| 05:15 | A dormir. Entrenamiento corriendo, URL pública con el esqueleto. Los agentes siguen con su lista nocturna |
| **08:45 · H1** | ¿Sobrevivió la noche? |
| 09:00 a 12:00 | Rotación real, validar la red, mapa del terreno, «¿Dónde mido?», cartera |
| **12:15 · H2** | ¿Está la pieza estrella? Se decide red o plan B |
| 12:30 | Primera prueba con tres extraños |
| **15:00 · H3** | Recorrido completo, dos veces, sin internet |
| 15:00 a 18:00 | Opcionales, pulido, entrega en borrador, ensayo |
| **18:00** | **Producto terminado** |
| 18:30, 21:00 | Ensayos. 19:00, segunda prueba con extraños. 20:00, charla de la organización |
| 22:00 | Video de respaldo y README técnico |
| 00:00 a 06:00 | Dormir |
| Dom 08:00 | Entrega. 09:30 presentaciones, 12:00 finales |

## El show en tres minutos

1. **El nombre.** Krylov calculó por adelantado qué hacer con un barco averiado. Nosotros hicimos eso con el trabajo de un data scientist.
2. **Buk.** ¿A quién conviene retener? Colores de decisión, deslizador en vivo, lo que cuesta no saber, y el examen con personas reales.
3. **Archivo malo.** La nube de empresas simuladas y el archivo cayendo afuera.
4. **Terreno y «¿Dónde mido?».** Rehízo cientos de análisis en segundos. Clic, y el mapa cambia.
5. **Cartera.** Mil empresas a la vez. Diez segundos.
6. **Cierre.** Anoche practicó con millones de terrenos simulados. QR. La frase.

Si hay que acortar: sale la cartera, después el archivo malo. **El mapa no se corta nunca.**

## Tres decisiones que tienen que tomar ustedes, ahora

1. **¿Se hace público el espejo `Silent-math/krylov`?** En el plan gratuito, Vercel no despliega los commits de quien no es dueño de la cuenta si el repositorio es privado. El oficial ya es público.
2. **¿Quién toma cada computador y quién presenta?**
3. **¿Qué hacemos con la línea del README de la organización que les pide a los modelos de lenguaje poner un emoji tras cada palabra?** Los agentes no la siguen por su cuenta.

## Dónde está cada cosa

| Archivo | Para qué |
|---|---|
| `WORKPLAN.md` | El plan completo, hora a hora, y la respuesta a la crítica |
| `PC1_…`, `PC2_…`, `PC3_…` | Las instrucciones de cada computador |
| `STACK.md` | Qué instalar y qué herramienta elegir, con alternativas |
| `AGENTS.md`, `GLOSARIO.md` | Contexto y palabras para los agentes |
| `contratos/` | Qué se pasan los computadores, con ejemplos para maquetar |
| `casos/` | Las cuatro tarjetas y el archivo malo |
| `pitch/GUION.md`, `pitch/CIFRAS.md` | El guion con corchetes y el registro de cifras |
| `.claude/skills/` | Doce procedimientos |
