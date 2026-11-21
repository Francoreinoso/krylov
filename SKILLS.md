# Procedimientos de Krylov

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

Índice para humanos de los procedimientos repetibles del proyecto. **Claude Code no lee este archivo por sí solo:** un `SKILLS.md` en la raíz no tiene significado especial para la herramienta. La versión que Claude Code ejecuta está en `.claude/skills/<nombre>/SKILL.md`, una carpeta por procedimiento. Si este índice y esas carpetas difieren, manda la carpeta.

## Cómo se relacionan los archivos

```
CLAUDE.md               Claude Code lo carga solo al abrir el repo
 ├─ @AGENTS.md          contexto, reglas, roles
 ├─ @GLOSARIO.md        las palabras del proyecto
 └─ @estado/TABLERO.md  cómo vamos y la siguiente tarea de cada rol
CLAUDE.local.md         el rol de ESTE computador; no se sube a git
 └─ @PC1_PRODUCTO.md | @PC2_AMORTIZACION.md | @PC3_SEGUIMIENTO.md
.claude/skills/*/       los procedimientos que Claude Code puede ejecutar
.claude/settings.json   permisos comunes para pedir menos confirmaciones
STACK.md                qué instalar y qué herramienta elegir
WORKPLAN.md             el plan hora a hora y los criterios de cada hito
SKILLS.md               este índice, para leer de pie
```

Por qué así: Claude Code carga `CLAUDE.md` y `CLAUDE.local.md` automáticamente, y sigue los `@` que encuentra en ellos. `AGENTS.md` no lo leería por su cuenta habiendo un `CLAUDE.md`, por eso el import explícito. Los permisos de `.claude/settings.json` aplican después de aceptar el diálogo de confianza de la carpeta.

## Cómo se usa una skill

- Escribiendo `/nombre` en Claude Code (por ejemplo `/punto-de-control h1` o `/validar-motor supervivencia`).
- O pidiéndolo con palabras: Claude Code la elige por su descripción («prepara el caso de crédito»).
- Para repetirla sola: `/loop 30m /ronda`.

## Primera vez en cada computador

Está paso a paso en el archivo `PC*.md` de ese computador, sección «Arranque». En corto:

1. Clonar el repositorio de la organización y agregar el espejo como segundo destino de push.
2. Copiar `CLAUDE.local.md.ejemplo` a `CLAUDE.local.md` y dejar el rol y el import de este computador.
3. Instalar lo que dice `STACK.md`.
4. Abrir Claude Code, aceptar el diálogo de confianza y preguntarle: «¿cuál es tu rol y qué te toca ahora?». Debe responder con el rol y la primera tarea.

## Índice

| Skill | Quién | Cuándo | Qué deja |
|---|---|---|---|
| `ronda` | PC 3 | Cada 30 a 45 minutos, y cuando alguien termina algo | Tablero con la siguiente tarea de cada rol; guion al día |
| `punto-de-control` | PC 3 | A la hora de cada hito (H0 a H3, congelado, entrega) | Tablero, decisiones y tag en los dos repositorios |
| `actualizar-estado` | todos | Al terminar algo, al bloquearse, antes de cada hito | `estado/<rol>.md` al día y subido |
| `registrar-cifra` | todos proponen, PC 3 registra | Cada número que verá el jurado | Fila en `pitch/CIFRAS.md` |
| `agregar-caso` | PC 3 | Para cada tarjeta y para el archivo malo | CSV con las columnas que pide el modelo del motor, archivo de verdad y YAML que calzan. 25 minutos |
| `medir-rendimiento <motor>` | PC 2, PC 3 | Antes de lanzar cada entrenamiento | Procesador o GPU del Mac, decidido midiendo; presupuesto del paso local |
| `entrenar-motor <motor>` | PC 2, PC 3 | Una corrida por motor (`espacial`, `supervivencia`, `jerarquico`, `estados`), o para retomarla | Entrenamiento corriendo, con puntos de guardado |
| `validar-motor <motor>` | PC 2, PC 3 | Antes de activar la red de un motor en el producto | Sello del motor con números medidos, codificador en ONNX, flujo en `flujo.npz`, muestras del MCMC; pasa o no pasa |
| `desplegar` | PC 1 | Primer despliegue (hoy, antes de dormir) y antes de cada hito | URL pública verificada desde un teléfono |
| `preparar-demo` | PC 1 | Antes de cada ensayo y en la fase de iteración | Demo revisado en 17 puntos |
| `ensayo-pitch` | PC 3 | Sáb 12:30, 17:00, 18:30, 19:00, 21:00; dom 06:30, 07:30 | Tiempos y una corrección |
| `preparar-entrega` | PC 3 | Sáb 15:20 y 22:00; dom antes de las 08:00 | Los cuatro archivos de entrega y el tag |

## Resumen de cada una

### ronda
Es el trabajo principal de PC 3. Baja los cambios, lee los estados, verifica corriendo lo que cada uno dice haber terminado, escribe en el tablero la siguiente tarea de cada rol, recorta el plan si algo lleva el doble de su tiempo y reemplaza en el guion cada corchete que ya tiene su número. Diez minutos.

### punto-de-control
Un hito: se mide contra el criterio escrito en `WORKPLAN.md`, se decide seguir o cortar, se anota y se deja un tag. Hay un H2 por motor (12:15, 13:00, 14:00; tope 16:00): ahí se decide si cada tarjeta responde con su red o con el plan B, el posterior del MCMC precalculado y rotulado.

### actualizar-estado
Un minuto: hecho, en curso, bloqueos, pedidos a otros y números medidos, con hora y con el identificador de la tarea.

### registrar-cifra
Cada número que verá el jurado se clasifica como medido, con fuente o hipótesis. Lo que se dice sobre exactitud sale del examen con datos reales. Una comparación dice exactamente qué se comparó.

### agregar-caso
Deja listo el archivo de datos de un caso: 20% de las respuestas vacías al azar, con la verdad guardada aparte para el examen. Los YAML ya vienen escritos, con cada columna en su papel dentro del modelo del motor; hay que comprobar que calzan. Inasistencias se muestrea por pacientes completos dentro de barrios, y el terreno necesita además la grilla con la distancia al río.

### medir-rendimiento
Ocho minutos por motor, con la red real, antes de lanzar su entrenamiento. Tapa abierta, enchufado y sin nada más entrenando. También mide el presupuesto del paso local: un análisis en menos de 1 segundo y la cartera en segundos.

### entrenar-motor
La corrida larga de la red de un motor, con datasets simulados al vuelo desde su modelo generativo y puntos de guardado cada 10 minutos. Un entrenamiento por computador: `espacial` y `estados` en PC 2, `supervivencia` y `jerarquico` en PC 3. Para lanzar basta simulador, codificador, flujo, pérdida, puntos de guardado y una prueba de humo con un SBC chico.

### validar-motor
Cuatro chequeos por motor: SBC y cobertura en simulaciones nuevas, comparación con el MCMC de referencia (5 a 10 datasets simulados más el real, con su tiempo), examen con datos reales reservados y la nube con el archivo malo. Además mide el método rápido de siempre, para poder decir qué se pierde sin el modelo completo. Exporta el codificador a ONNX, comprueba que el flujo en NumPy da lo mismo que en `torch` y escribe el sello. Si no pasa, la tarjeta sale con el MCMC precalculado.

### desplegar
Web y respuestas precalculadas en Vercel, API en Render, las dos desde el repositorio espejo. La URL pública funciona sin servidor. En el escenario el demo corre en local.

### preparar-demo
Diecisiete puntos antes de mostrar nada: el recorrido, lo que se lee, sin internet, y el computador que presenta.

### ensayo-pitch
De pie, cronometrado, con el demo real. Una sola corrección por ensayo. Incluye las dos pruebas con extraños: la de las 12:30 todavía puede cambiar el producto.

### preparar-entrega
Los cuatro archivos que pide la hackathon, con contenido real y leídos por una persona. El README cuenta para la nota técnica y la descripción se muestra en la página de votación.

## Agregar una skill nueva

Crear `.claude/skills/<nombre>/SKILL.md` con `name` y `description` en el encabezado (qué hace y cuándo usarla), el recordatorio de hackathon en la primera línea, pasos numerados y criterio de terminado. Agregar su fila aquí.
