# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 08:52 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: H1, a más tardar 08:45 · **Producto terminado: sáb 18:00**

**La noche (S-06, 08:16):** ✅ `espacial` vivo en PC 2 (7,2 millones de terrenos, punto de guardado 08:10; validación intermedia de las 07:31: cobertura de θ 0,905 y del mapa 0,901, los 7 parámetros pasan el χ²). ✅ `supervivencia` vivo en PC 3 (12,0 millones de datasets, 25 puntos de guardado, el último a las 08:05; enchufado de nuevo). Los dos terminan solos a las 08:30. ✅ URL pública responde (página 0,57 s, `casos.json` 0,49 s). ⚠️ **PC 1: sin código en `web/` ni `servicio/` desde las 05:03** (solo diseño de D-34 y D-35); P-07, P-09 y P-12 pendientes.

**URL pública:** https://krylov-tan.vercel.app/ (P-02, 03:59). Verificada en tamaño teléfono y desde un teléfono (04:01). Falta confirmar con datos móviles.

**📣 A PC 1 y PC 2: D-34 aprobada (07:12). Krylov responde en un chat.** El usuario elige el modelo, adjunta un archivo (el del demo o uno propio), asigna cada columna a su papel; la red responde y un modelo de lenguaje solo interpreta el JSON (regla 11 nueva). **Cambia el contrato:** `api.papeles`, `api.analizar_archivo`, `GET /api/papeles/{motor_id}`, `POST /api/analizar_archivo`, `POST /api/interpretar` (`contratos/CONTRATO.md`, secciones 2, 5 y 6). Lo que ya existía no cambia de forma. Riesgos y orden de corte en `DECISIONES.md`, D-34.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟡 tarea nueva grande | P-01 a P-03 y P-N1 a P-N3 verificados. Último código 05:03; después, diseño de D-34 y D-35 (07:35). Ahora P-12 (D-34) |
| amortizacion (PC 2) | 🟢 adelantado | `supervivencia` lista salvo la red. D-34 y D-35 en `estados`, `jerarquico` y `espacial` (08:14). `espacial` termina 08:30 |
| seguimiento (PC 3) | 🟢 al día | `supervivencia` exportada y subida (12,74 millones de datasets, 13b3e42). `jerarquico` (D-35) entrena aquí desde las 08:52 hasta las 11:30 |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora **P-12 (a)**, tope 10:30: chat con los cuatro archivos del demo, selector de papeles y respuesta dentro del chat, también en modo estático. Después **P-12 (b)**, tope 14:30: desplegar la API en Render (no existe todavía), `analizar_archivo` e `interpretar` (SDK `anthropic` solo en `servicio/`, clave en Render que pone una persona). **Empuja lo que tengas antes de empezar.** Arreglos chicos pendientes: en rojo, el pie no dice «Respondió la red»; ejes de la nube más grandes.
- **PC 2 · amortizacion:** D-35 en `jerarquico` hecho (08:14). Sesión B: ahora **A-19** (D-34 y D-35), tope 10:30: `papeles` y `analizar_archivo`, con rojo y motivo si el archivo no calza y la nube sobre el archivo subido; confirmar los papeles de los cuatro motores y el tamaño de `codificador.onnx`. Sesión A: a las 08:30 A-08 (detener y validar `espacial`), después el sello de `supervivencia` (D-33) y recién entonces lanzar `estados`. Pedido: recuperación por parámetro en cada `sello.json` (M-35).
- **PC 3 · seguimiento:** S-06b hecha. Ahora H1 (con la persona) y S-07, S-09 y S-10 (personas). 11:30: detener `jerarquico`; su sello va a un computador sin nada entrenando. H2 de `jerarquico`: 13:00.

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
