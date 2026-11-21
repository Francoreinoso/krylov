# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 03:00 · **Hito vigente:** antes de H0 (sáb 03:45) · **Producto terminado: sáb 18:00**

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | ⚪ sin empezar | |
| amortizacion (PC 2) | ⚪ sin empezar | |
| seguimiento (PC 3) | ⚪ sin empezar | |

## Siguiente tarea de cada uno

- **PC 1 · producto:** P-01, esqueleto que pinta los ejemplos fijos. Después P-02: primer despliegue, hoy, antes de dormir. Ojo: el ejemplo de tabla ahora se llama `analizar_tabla.json`, `espacial` trae `factores`, y P-12 («Sube tus datos») se cortó (D-26).
- **PC 2 · amortizacion:** dos sesiones. Sesión A: A-01 a A-04 (`espacial` y lo compartido). Sesión B: A-B1 a A-B4 (`supervivencia`). A las 05:15 quedan dos entrenamientos corriendo: `espacial` en PC 2 y `supervivencia` en PC 3. Detalle: `PC2_AMORTIZACION.md` y `WORKPLAN.md` 6.3.
- **PC 3 · seguimiento:** S-01, S-02, S-03 y S-04 (rotación y terreno). **Nuevo (D-26):** S-04 incluye bajar `meuse.grid` a `datos/demo/terreno_grilla.csv`; rotación conserva todas las columnas de `casos/rotacion.yaml`; y **no te duermes antes de las 05:15**: a las 04:55 haces `uv sync --group entrenar` y lanzas `entrenar-motor supervivencia` en tu computador.

## Qué cambió respecto del plan

**D-26 (03:00), cambio de fondo:** Krylov es inferencia basada en simulación amortizada, con cuatro motores (`supervivencia`, `jerarquico`, `estados`, `espacial`), cada uno con su modelo generativo y su red. `regresion` ya no existe. Al día: `contratos/`, `casos/`, `PC2_AMORTIZACION.md`, `WORKPLAN.md` 6.3 y 11. El resto se corrige en las rondas; donde choque, manda D-26.

## Próxima decisión

H0, sáb 03:45: ¿los tres empujan a los dos repositorios, el contrato está congelado y la web muestra un ejemplo fijo? Criterios en `WORKPLAN.md`, sección 6.5.

## Cifras que el guion todavía espera

Ver los corchetes de `pitch/GUION.md`. Ninguna medida aún.

## Casos en el inicio

Ver `casos/INICIO`. Meta: rotación y terreno con datos antes de dormir; los cuatro en H2.
