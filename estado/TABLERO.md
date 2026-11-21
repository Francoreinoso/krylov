# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 04:38 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: antes de dormir, 05:15 · **Producto terminado: sáb 18:00**

**URL pública:** https://krylov-tan.vercel.app/ (P-02, 03:59). Verificada en PC 3 en tamaño teléfono y por PC 1 desde un teléfono (04:01). Falta confirmar con datos móviles.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟢 al día | P-01 y P-02 verificados. P-03 en curso, sin commit desde las 03:59 (vence 05:00) |
| amortizacion (PC 2) | 🟢 adelantado | A-01 a A-04 y A-B1 a A-B4 en `main`. `espacial` entrena en PC 2 desde las 03:50 |
| seguimiento (PC 3) | 🟢 adelantado | S-02 a S-05 hechas. `supervivencia` entrena en PC 3 desde las 04:05: 1,58 millones de datasets y punto de guardado a las 04:35 |

## Antes de dormir (05:15): cómo vamos

- ✅ Dos entrenamientos corriendo con puntos de guardado: `espacial` en PC 2, `supervivencia` en PC 3. Los dos terminan solos a las 08:30.
- ✅ URL pública con el esqueleto. ✅ Datos de rotación y terreno (y crédito) en el repositorio.
- Falta: la lista nocturna de PC 1 y de PC 2 (A-05) escrita en su estado antes de dormir.

## Siguiente tarea de cada uno

- **PC 1 · producto:** terminar P-03 y empujar (un commit por hora como mínimo). Antes de dormir, lista nocturna (P-N1, P-N2) en `estado/producto.md`. Ojo: el orden de las tarjetas lo manda `casos/INICIO`. **Aviso de PC 2:** `codificador.onnx` viene con `codificador.onnx.data`; el servicio necesita los dos (antes de A-10).
- **PC 2 · amortizacion:** adelanta en orden (D-29). Sesión A: A-05 y a dormir a las 05:15; el agente sigue con A-N1 y A-N3. Sesión B: A-N2. Tu pedido a PC 3 está hecho: `supervivencia` corre en PC 3 desde las 04:05.
- **PC 3 · seguimiento:** nada pesado aquí. A dormir a las 05:15, enchufado y con la tapa abierta. El agente: solo la lista nocturna (S-N1 a S-N4, en `estado/seguimiento.md`). 08:15: S-06; 08:30: S-06b (exportar `supervivencia` y lanzar `jerarquico`).

## Qué cambió respecto del plan

- **D-29: las horas del plan son topes, no horas de inicio, en los tres computadores.** Quien termina una tarea toma la siguiente de su lista sin esperar; lo que no tiene insumo se hace contra el ejemplo fijo y se anota. No se adelanta el MCMC ni se mide encima de un entrenamiento (`AGENTS.md`, regla 21).
- `supervivencia` se lanzó a las 04:05 y `espacial` a las 03:50: casi una hora más de entrenamiento cada uno.
- Guion: la versión de 3 minutos es la principal (J-04). «Escondimos a 294 personas reales» pasó a «escondimos la respuesta de 294 personas del archivo»: el archivo de rotación es ficticio (D-01).
- D-26 sigue mandando donde un archivo choque. Pendientes: `AGENTS.md`, `GLOSARIO.md`, `STACK.md`, `SKILLS.md`, skills, resto de `WORKPLAN.md`.

## Próxima decisión

- Quién presenta: se decide después (a más tardar en H1). El pitch dura 3 minutos.
- H1, sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito. Con datos: rotación, terreno y crédito. Inasistencias: S-N1 esta noche.
