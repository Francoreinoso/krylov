# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 07:26 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: H1, a más tardar 08:45 · **Producto terminado: sáb 18:00**

**⚠️ PC 3 sin cargador (07:15):** `supervivencia` sigue viva (9,1 millones de datasets, punto de guardado 07:05), pero el computador está a batería (98%, descargando). Enchufarlo antes de las 08:30.

**URL pública:** https://krylov-tan.vercel.app/ (P-02, 03:59). Verificada en tamaño teléfono y desde un teléfono (04:01). Falta confirmar con datos móviles.

**📣 A PC 1 y PC 2: D-34 aprobada (07:12). Krylov responde en un chat.** El usuario elige el modelo, adjunta un archivo (el del demo o uno propio), asigna cada columna a su papel; la red responde y un modelo de lenguaje solo interpreta el JSON (regla 11 nueva). **Cambia el contrato:** `api.papeles`, `api.analizar_archivo`, `GET /api/papeles/{motor_id}`, `POST /api/analizar_archivo`, `POST /api/interpretar` (`contratos/CONTRATO.md`, secciones 2, 5 y 6). Lo que ya existía no cambia de forma. Riesgos y orden de corte en `DECISIONES.md`, D-34.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 tarea nueva grande | P-01 a P-03 y P-N1 a P-N3 verificados. Último commit 07:02 (la propuesta de chat). Ahora P-12 (D-34) |
| amortizacion (PC 2) | 🟢 adelantado | `supervivencia` lista salvo la red (A-N2, A-10, A-13 en código). `espacial` entrena desde las 03:50. Tarea nueva A-19 (D-34) |
| seguimiento (PC 3) | 🟢 adelantado | `supervivencia` entrena aquí: 9,6 millones de datasets; de nuevo enchufado. Archivos de prueba para la subida listos (D-06). D-34 aplicada en el plan, el contrato y el guion |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-12 (a)**, tope 10:30: chat con los cuatro archivos del demo, selector de papeles y respuesta dentro del chat, también en modo estático. Después **P-12 (b)**, tope 14:30: desplegar la API en Render (no existe todavía), `analizar_archivo` e `interpretar` (SDK `anthropic` solo en `servicio/`, clave en Render que pone una persona). **Empuja lo que tengas antes de empezar.** Arreglos chicos pendientes: en rojo, el pie no dice «Respondió la red»; ejes de la nube más grandes.
- **PC 2 · amortizacion:** **urgente D-35, antes de las 08:30:** papeles opcionales (máscara de presencia) en el simulador de `jerarquico`, o avisar a PC 3 que su lanzamiento espera. Sesión B: ahora **A-19** (D-34 y D-35), tope 10:30: `papeles` y `analizar_archivo`, con rojo y motivo si el archivo no calza y la nube sobre el archivo subido; confirmar los papeles de los cuatro motores y el tamaño de `codificador.onnx`. Sesión A: `espacial` a las 07:10, A-M3 a las 07:30, A-08 a las 08:30; sello de `supervivencia` en PC 2 (D-33). Pedido: recuperación por parámetro en cada `sello.json` (M-35).
- **PC 3 · seguimiento:** 08:15 S-06; 08:30 S-06b (`git pull`, exportar y subir `supervivencia`, lanzar `jerarquico`). **Hecho:** archivos de prueba para la subida, `datos/demo/subida_rotacion_{ventas,investigacion,rrhh}.csv` (asignación de papeles en `estado/seguimiento.md`; RR. HH. tiene que dar «faltan datos»).

## Qué cambió respecto del plan

- **D-35 (07:40):** el modelo de lenguaje propone el calce de columnas (sin filas) y el usuario lo confirma; papeles opcionales en `jerarquico` y `estados`, y en `supervivencia` si cabe. Registrada por PC 1, conversada en el grupo.
- **D-34 (07:12):** chat, subida propia y modelo de lenguaje que interpreta. Revierte lo que D-26 cortó de «Sube tus datos» y la capa de lenguaje. **Orden de corte a las 16:00:** primero la interpretación, después la subida propia; el chat con los archivos del demo no se corta.
- **D-29:** las horas son topes, no horas de inicio. **D-30 a D-33:** `estados` 33 parámetros, `jerarquico` 20, `etiquetas` en los casos, `unidad` en `analizar`, criterios del sello, `supervivencia` se valida en PC 2.
- Guion: 3 minutos (J-04) y no cabía (176 s de habla). Si se muestra la subida en el escenario, sale la cartera.

## Próxima decisión

- Una persona: la clave de Anthropic para Render. Al validar: ¿la nube va al semáforo? (D-32, D-33). El equipo: quién presenta, a más tardar en H1.
- H1, a más tardar sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito: son los archivos del demo precargados en el chat. Inasistencias, solo en PC 2 y PC 3 (licencia no comercial).
