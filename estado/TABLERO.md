# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 04:00 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: antes de dormir, 05:15 · **Producto terminado: sáb 18:00**

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟢 al día | P-01 en `main`, verificado en PC 3 con API y en modo estático. P-02 en curso |
| amortizacion (PC 2) | 🟢 adelantado | A-01 a A-04 y A-B1 a A-B3 en `main`. Sus 33 pruebas pasan también en PC 3 |
| seguimiento (PC 3) | 🟢 adelantado | S-02 con respuesta, S-03, S-04 y S-05 en `main`. Grupo `entrenar` instalado |

## H0: cerrado a las 04:00 (D-27, D-28)

- ✅ Los tres empujan a los dos repositorios. ✅ Contrato congelado desde las 03:45 (cambiarlo exige entrada en `DECISIONES.md` y aviso).
- ✅ La web pinta el inicio y las respuestas fijas, con API y sin ella (pie «Modo estático»). ✅ Espejo público.
- **El pitch dura 3 minutos** (respuesta de la organización, J-04). Se presenta desde nuestro computador, con audio y video.

## Siguiente tarea de cada uno

- **PC 1 · producto:** P-02, primer despliegue (lo importa en Vercel el dueño de `Silent-math`). Si a las 05:15 no salió, se deja para las 08:30. Después P-03. Ojo: el orden de las tarjetas lo manda `casos/INICIO` (rotación, terreno, inasistencias, crédito); el ejemplo fijo trae otro orden.
- **PC 2 · amortizacion:** sesión A: lanzar `espacial` (A-04, 04:45). Sesión B: A-B4, dejar `supervivencia` lista para lanzar en PC 3 a las 04:55. Rotación, terreno (con `terreno_grilla.csv`) y crédito ya están en `datos/demo/`.
- **PC 3 · seguimiento:** 04:55: S-05b, lanzar `entrenar-motor supervivencia`. Antes de dormir, lista nocturna (S-N1 ya tiene el crudo de inasistencias). Guion: la versión de 3 minutos pasa a ser la principal.

## Qué cambió respecto del plan

- D-26 sigue mandando donde un archivo choque. Pendientes de actualizar: `AGENTS.md`, `GLOSARIO.md`, `STACK.md`, `SKILLS.md`, skills, resto de `WORKPLAN.md` (uno o dos por ronda).
- S-05 (crédito) se adelantó a las 03:28. El crudo de inasistencias ya está en PC 3: no hace falta copiar `datos_crudos/`.
- PC 2 anotó en `pitch/VALIDACION.md` (carpeta de PC 3) las respuestas de la organización. Bien recibidas; la próxima vez, como pedido en su estado.

## Próxima decisión

- Quién presenta: se decide después (a más tardar en H1). Presentar dura 3 minutos.
- H1, sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito. Con datos: rotación, terreno y crédito. Inasistencias: S-N1 esta noche.
