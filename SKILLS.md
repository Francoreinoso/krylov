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

- Escribiendo `/nombre` en Claude Code (por ejemplo `/punto-de-control h4` o `/validar-motor cinetica`).
- O pidiéndolo con palabras: Claude Code la elige por su descripción («prepara el caso de taludes»).
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
| `ronda` | PC 3 | Cada 30 a 45 minutos, y cuando alguien termina algo | Tablero con la tabla «Los cinco casos» y la siguiente tarea de cada rol; guion al día |
| `punto-de-control` | PC 3 | A la hora de cada hito (H4, H5, H6 o congelado, tope de redes, entrega) | Tablero, decisiones y tag en los dos repositorios |
| `actualizar-estado` | todos | Al terminar algo, al bloquearse, antes de cada hito | `estado/<rol>.md` al día y subido, con el identificador de la tarea al inicio de cada línea |
| `registrar-cifra` | todos proponen, PC 3 registra | Cada número que verá el jurado | Fila en `pitch/CIFRAS.md` |
| `agregar-caso` | PC 3 | Para cada una de las cinco tarjetas y para el archivo que no alcanza | CSV con la forma que pide el motor (espacial o de series), verdad escondida y YAML que calzan, con el origen de los datos. 25 minutos |
| `medir-rendimiento <motor>` | PC 2, PC 3 | Antes de lanzar cada entrenamiento | Procesador o GPU del Mac, decidido midiendo; presupuesto de un análisis |
| `entrenar-motor <motor>` | PC 2, PC 3 | Una corrida por motor de series (`cinetica`, `deformacion`, `desgaste`, `sismico`), en dos rondas, o para retomarla | Entrenamiento corriendo, con puntos de guardado |
| `validar-motor <motor>` | PC 2, PC 3 | Al terminar cada ronda y antes de activar la red de un motor en el producto | Sello del motor con números medidos (por tramos de tamaño; sin MCMC), codificador en ONNX, flujos en `flujo.npz` y `flujo_local.npz`; pasa o no pasa. Al final, las muestras del MCMC y su comparación |
| `desplegar` | PC 1 | En cada redespliegue, agrupados en H4, H5 y H6, y cuando un motor pasa a `red` | URL pública verificada desde un teléfono |
| `preparar-demo` | PC 1 | Antes de cada ensayo y en la fase de iteración | Demo revisado en 17 puntos |
| `ensayo-pitch` | PC 3 | Sáb 14:00, 16:40, 18:00, 18:30, 19:00, 21:00; dom 06:30, 07:30 | Tiempos y una corrección |
| `preparar-entrega` | PC 3 | Sáb 17:10 y 23:00; dom antes de las 08:00 | Los cuatro archivos de entrega y el tag |

## Resumen de cada una

### ronda
Es el trabajo principal de PC 3. Baja los cambios, lee los estados, verifica corriendo lo que cada uno dice haber terminado, pone al día la tabla «Los cinco casos» del tablero contra el sello de cada motor, escribe la siguiente tarea de cada rol, recorta el plan si algo lleva el doble de su tiempo y reemplaza en el guion cada corchete que ya tiene su número. Diez minutos.

### punto-de-control
Un hito: se mide contra el criterio escrito en `WORKPLAN.md`, sección 6.5, se decide seguir o cortar, se anota y se deja un tag. Después del pivote son H4 (14:30), H5 (16:30) y H6 (18:00, tag `congelado`). En H5 y en el tope de redes (20:30) se decide si cada tarjeta nueva responde con su red o con el plan B, el posterior del MCMC precalculado y rotulado.

### actualizar-estado
Un minuto: hecho, en curso, bloqueos, pedidos a otros y números medidos, con hora y con el identificador de la tarea al inicio de la línea («A-23 terminada: …»), que es lo que lee el tablero en vivo.

### registrar-cifra
Cada número que verá el jurado se clasifica como medido, con fuente o hipótesis. Las cifras de minería (ids `I-xx`) llevan fuente y la firma de una persona que la abrió; los números del documento técnico del equipo no se usan sin fila. Lo que se dice sobre exactitud sale del examen. Una comparación dice exactamente qué se comparó.

### agregar-caso
Deja listo el archivo de datos de un caso, en una de dos formas: espacial (`x`, `y`, `valor`) o de series (`unidad`, `tiempo`, `valor`). Si hay un archivo real con licencia abierta que calce, se usa; si no, lo genera `datos/preparar/<caso>.py` con semilla fija, con la verdad escondida guardada aparte para el examen. El YAML dice de dónde vienen los datos y lleva `sintetico: true` cuando son simulados.

### medir-rendimiento
Ocho minutos por motor, con la red real, antes de lanzar su entrenamiento. Tapa abierta, enchufado y sin nada más entrenando. También mide el presupuesto de un análisis: menos de 1 segundo.

### entrenar-motor
La corrida de la red de un motor de series, con datasets simulados al vuelo desde su modelo generativo y puntos de guardado cada 10 minutos. Un entrenamiento por computador, en dos rondas: `cinetica` (PC 2) y `deformacion` (PC 3) de 14:30 a 16:10; `desgaste` (PC 2) y `sismico` (PC 3) de 16:30 a 18:15. Para lanzar basta simulador (que sortea el tamaño de cada dataset), la red del andamio de series, pérdida, puntos de guardado y una prueba de humo con un SBC chico. No se corre ningún MCMC antes (D-38). `espacial` no se reentrena.

### validar-motor
Los chequeos de `WORKPLAN.md`, 11.8: SBC global y local y cobertura de lo que se decide en simulaciones nuevas, por tramos de tamaño del dataset y con el peor tramo en el sello; examen con la verdad escondida; y semáforo. Con eso se decide «pasa». La comparación con el MCMC de referencia (3 a 5 datasets simulados más el del demo, 10 minutos de presupuesto por dataset) se corre al final para los cinco motores y se agrega al sello, tal cual salga (D-38). Además mide el método rápido de siempre, para poder decir qué se pierde sin el modelo completo. Exporta el codificador a ONNX, comprueba que los flujos en NumPy dan lo mismo que en `torch` y escribe el sello. Si no pasa, se adelanta el MCMC de su archivo del demo y la tarjeta sale «precalculada».

### desplegar
Web y respuestas precalculadas en Vercel, API en Render, las dos desde el repositorio espejo. La URL pública funciona sin servidor. Los redespliegues se agrupan en los hitos, porque Vercel tiene un límite diario. En el escenario el demo corre en local.

### preparar-demo
Diecisiete puntos antes de mostrar nada: el recorrido de `WORKPLAN.md`, 4.3 (teclas `1` a `5`, `D`, `M` y `L`), lo que se lee, sin internet, y el computador que presenta.

### ensayo-pitch
De pie, cronometrado, con el demo real. Una sola corrección por ensayo. Revisa que ninguna palabra minera quede sin explicar. Incluye las dos pruebas con extraños: la de las 16:40 todavía puede cambiar la pantalla.

### preparar-entrega
Los cuatro archivos que pide la hackathon, con contenido real, contando el producto minero, y leídos por una persona. El README cuenta para la nota técnica y la descripción se muestra en la página de votación.

## Agregar una skill nueva

Crear `.claude/skills/<nombre>/SKILL.md` con `name` y `description` en el encabezado (qué hace y cuándo usarla), el recordatorio de hackathon en la primera línea, pasos numerados y criterio de terminado. Agregar su fila aquí.
