# Glosario de Krylov

Las palabras del proyecto, en una o dos líneas cada una. Se usan igual en todos los archivos, en la pantalla y en el pitch. Si un término no está aquí, no se usa sin explicarlo.

## El producto

- **Krylov.** El nombre del producto y de la empresa. Viene de Alekséi Krylov, ingeniero naval que calculó por adelantado qué hacer con un barco averiado para que el capitán decidiera en segundos. El relato, con su fuente, está en `pitch/GUION.md`.
- **Data scientist artificial.** Programa que hace el trabajo de un analista de datos: elige el método, lo aplica, dice qué conviene hacer, cuánto se puede equivocar y cuándo los datos no sirven.
- **Modelo avanzado.** Modelo estadístico que, además de predecir, dice cuánto se puede equivocar. Hoy exige un especialista.
- **Simular.** Inventar datos con reglas conocidas. Krylov practica con millones de casos simulados, donde la respuesta correcta se conoce, antes de ver datos reales.
- **Amortizar.** Pagar el costo de cálculo una sola vez, por adelantado, entrenando una red con casos simulados, para que después cada respuesta sea instantánea.
- **Motor.** Un modelo avanzado listo para responder al instante. Hay dos:
  - `regresion`: preguntas de sí o no (¿renuncia?, ¿paga?, ¿falta?) a partir de hasta 8 factores. Usa el método exacto, que aquí ya es instantáneo. No tiene red.
  - `espacial`: datos con ubicación (¿dónde está contaminado?). Usa una red entrenada con millones de terrenos simulados.
- **Método exacto.** La forma de siempre de hacer el cálculo: correcta, y lenta cuando hay que repetirla cientos de veces. Cada motor tiene una versión exacta, que es además el plan B si la red falla.
- **Red.** El programa que aprendió, mirando terrenos simulados, a dar la misma respuesta que el método exacto en una fracción del tiempo.

## Lo que se ve en pantalla

- **Caso de uso** (o «caso»). Una pregunta de negocio de una empresa o industria, resuelta con un motor, un archivo de datos y sus costos. Vive en `casos/<nombre>.yaml`. Cada tarjeta del inicio es un caso.
- **Unidad.** Aquello sobre lo que se decide: una persona, una cita, un cliente, un bloque de terreno.
- **Actuar.** Lo que la empresa haría si la respuesta es «sí»: retener, confirmar la cita, no aprobar el crédito, limpiar. Cada caso le pone su nombre.
- **Costos del caso.** Dos números que pone el usuario con deslizadores: cuánto cuesta actuar cuando no hacía falta y cuánto cuesta no actuar cuando sí hacía falta. Son supuestos del demo y se dicen como supuestos.
- **Punto de corte.** El nivel de riesgo desde el cual conviene actuar. Sale de los dos costos. Si actuar es barato y no actuar es caro, el punto de corte es bajo.
- **Tres colores.** Son decisiones, no pronósticos: «conviene actuar», «no hace falta» y «no sabemos si conviene». Una unidad está en el tercero cuando hay más de 10% de probabilidad de que la decisión cambie al saber más.
- **Lo que te cuesta no saber.** El número grande de la pantalla. Es la plata que se ahorraría, en promedio, si la duda se despejara antes de decidir. Vale cero cuando no hay duda.
- **¿Dónde mido?** En casos con mapa: los tres lugares donde una medición más vale más plata. Para calcularlo, Krylov imagina cientos de resultados posibles y rehace el análisis completo para cada uno.
- **Qué pesa.** Los factores que mueven la respuesta, cada uno con una etiqueta: seguro, probable, o no se puede saber con estos datos.
- **Examen.** Lo que pasó cuando Krylov respondió sobre datos reales que no había visto: «de las personas a las que dimos 30% de riesgo, se fue el 28%». Es la exactitud que se dice en voz alta.
- **Sello.** La ficha técnica de un motor: con cuántas simulaciones practicó, cuánto acierta en casos simulados, cuánto tarda. Va en el pie de la pantalla y en la lámina técnica.
- **Nube.** El dibujo de las simulaciones con que Krylov practicó, con el archivo del usuario encima. Si el archivo cae fuera, Krylov no responde.
- **Semáforo.** Verde: responde. Amarillo: responde con un aviso. Rojo: no responde y dice por qué, porque faltan datos o porque el archivo no se parece a nada que conozca; en ese caso propone una corrección.
- **Cartera.** La vista donde se analizan cientos o miles de clientes de una plataforma de una sola vez.
- **Modo estático.** Las respuestas del demo guardadas como archivos junto a la web. Así la URL pública responde aunque no haya servidor.

## El negocio

- **Primer cliente.** A quién se le vende primero: plataformas de software con miles de empresas cliente (tipo Buk o AgendaPro), que integran Krylov para darle un data scientist a cada una.
- **Sponsor como caso.** Una tarjeta con el nombre de un sponsor es una hipótesis de uso con datos públicos. No es una afirmación sobre cómo trabaja esa empresa ni usa datos suyos.

## El trabajo

- **PC 1, PC 2, PC 3.** Los tres computadores: producto, amortización y seguimiento. Sus instrucciones están en `PC1_PRODUCTO.md`, `PC2_AMORTIZACION.md` y `PC3_SEGUIMIENTO.md`.
- **Hito (H0 a H3).** Hora fija en que se mide contra un criterio escrito y se decide seguir o cortar. El plan anterior los llamaba «puntos de control (PC)»; se cambió el nombre para no confundirlos con los computadores.
- **Ronda.** La revisión que hace PC 3 cada 30 a 45 minutos: baja los cambios, mira qué terminó cada uno, lo verifica, escribe la siguiente tarea de cada rol en el tablero y ajusta el guion.
- **Producto terminado.** Sábado a las 18:00. Desde ahí no entra nada nuevo: solo se itera el demo y el pitch.
- **Contrato.** El acuerdo sobre qué datos se pasan los tres computadores. Está en `contratos/CONTRATO.md`.
- **Repositorios espejo.** El oficial de la organización y el personal `Silent-math/krylov`, que reciben exactamente los mismos commits con un solo `git push`.
- **Cifra registrada.** Número con fila en `pitch/CIFRAS.md`, clasificado como medido, con fuente o hipótesis. Lo que no está ahí no se muestra.

## Qué se dice en vez de la jerga

| Término técnico | En pantalla y en el pitch |
|---|---|
| Posterior, intervalo de credibilidad | «Rango creíble», «lo que de verdad sabemos» |
| Valor de la información | «Lo que te cuesta no saber», «cuánto vale averiguarlo» |
| Diseño de experimentos | «¿Dónde mido?» |
| Calibración, cobertura | «Cuando dimos 30% de riesgo, pasó el 28%» |
| Fuera de distribución, fuera del prior | «No se parece a nada que haya visto» |
| Inferencia amortizada | «Ya practicó con millones de casos simulados» |
| Modelo bayesiano | «Un modelo que dice cuánto se puede equivocar» |
| Coeficiente, efecto | «Qué pesa» |
| Umbral de decisión | «Punto de corte» |
| MCMC, muestreo por importancia | «El método exacto de siempre» (solo si preguntan) |
| Regresión logística, kriging, variograma | No se nombran. Si preguntan: «el método rápido de siempre» para el kriging con parámetros fijos |
| Simulación, simular | Se dicen tal cual: es el nombre del track |
