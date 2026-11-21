# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 03:50 (H0) · **Hito vigente:** H0, abierto hasta que la web muestre el ejemplo fijo · **Producto terminado: sáb 18:00**

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🔴 sin commits | Está arrancando. Falta el primer push y la web con el ejemplo fijo (P-01) |
| amortizacion (PC 2) | 🟢 adelantado | A-01, A-02, A-03, A-B1, A-B2 y A-B3 en `main`. Sus 33 pruebas pasan también en PC 3 |
| seguimiento (PC 3) | 🟢 adelantado | S-03, S-04 y S-05 en `main`. Grupo `entrenar` instalado. S-02 lo envía una persona |

## H0 (03:45): pasa en parte, sin tag todavía (D-27)

- ✅ PC 2 y PC 3 empujan a los dos repositorios (mismo commit en los dos). ❌ PC 1, sin commits.
- ✅ Contrato congelado desde las 03:45. Cambiarlo exige entrada en `DECISIONES.md` y aviso.
- ❌ La web no existe todavía. El tag `h0` se pone cuando PC 1 suba P-01 y la web pinte un ejemplo fijo.
- ✅ Espejo `Silent-math/krylov`: ya es público (verificado 03:47). Vercel puede desplegar los commits de los tres.

## Siguiente tarea de cada uno

- **PC 1 · producto:** P-01 ya, y **empuja apenas la web pinte un ejemplo fijo** (cierra H0). Después P-02, primer despliegue: el espejo ya es público. Si a las 05:15 no salió, se deja para las 08:30. Ojo: el ejemplo de tabla es `analizar_tabla.json`, `espacial` trae `factores`, P-12 está cortado (D-26).
- **PC 2 · amortizacion:** sesión A: A-04 (prueba de humo y lanzar `espacial`, 04:45). Sesión B: A-B4, dejar `supervivencia` lista para lanzar en PC 3 a las 04:55. Rotación, terreno (con `terreno_grilla.csv`) y crédito ya están en `datos/demo/`.
- **PC 3 · seguimiento:** ronda a las 04:15 (revisar P-01 y poner `h0`). 04:55: S-05b, lanzar `entrenar-motor supervivencia`. Antes de dormir, lista nocturna (S-N1 ya tiene el crudo de inasistencias).

## Qué cambió respecto del plan

- D-26 sigue mandando donde un archivo choque. Pendientes de actualizar: `AGENTS.md`, `GLOSARIO.md`, `STACK.md`, `SKILLS.md`, skills, resto de `WORKPLAN.md` (uno o dos por ronda).
- S-05 (crédito) se adelantó a las 03:28. El crudo de inasistencias ya está en PC 3: no hace falta copiar `datos_crudos/`.

## Próxima decisión

- Quién presenta: se decide después (a más tardar en H1).
- H1, sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito. Con datos: rotación, terreno y crédito. Inasistencias: S-N1 esta noche.
