# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 07:08 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: H1, a más tardar 08:45 · **Producto terminado: sáb 18:00**

**URL pública:** https://krylov-tan.vercel.app/ (P-02, 03:59). Verificada en tamaño teléfono y desde un teléfono (04:01). Falta confirmar con datos móviles.

**Para las 08:15:** A-N2 terminado (06:20) y el código de rotación listo: el archivo malo ya sale rojo con su corrección (verificado en PC 3). Falta la red de las 08:30. **PC 1 sin commits desde las 05:04: confirmar que sigue trabajando.**

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟢 adelantado | P-01 a P-03 y P-N1 a P-N3 verificados en PC 3. Sin commits desde las 05:04: empuja lo que tengas (uno por hora como mínimo) |
| amortizacion (PC 2) | 🟢 adelantado | `espacial` entrena desde las 03:50. `jerarquico` (20 parámetros) y `estados` (33) con código, prueba de humo y `analizar`; cartera en lote (mecánica); textos desde `casos/textos.yaml` |
| seguimiento (PC 3) | 🟢 adelantado | S-02 a S-05, S-N1 a S-N3, S-08, S-12 y textos v1 hechos. `supervivencia` entrena aquí: 7,1 millones de datasets a las 06:15. `jerarquico` exporta bien en el M3. S-09 listo para una persona |

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora P-07 (tecla `M` y corrección); después P-09 (pines de «¿Dónde mido?»). Dos arreglos chicos: en rojo, el pie no dice «Respondió la red»; ejes de la nube más grandes. Portada y cierre (P-13): texto en `pitch/LAMINAS.md`. Desde las 05:11 `codificador.onnx` es un solo archivo, con los pesos dentro.
- **PC 2 · amortizacion:** sesión B: `supervivencia` lista salvo la red; a las 08:30, su sello en PC 2 (D-33). Sesión A: mirar `espacial` a las 07:10, A-M3 a las 07:30 y A-08 a las 08:30. Criterios del sello confirmados en D-32; `supervivencia` los usa también. **Pedido nuevo:** en cada `sello.json`, la recuperación por parámetro (correlación verdadero contra estimado, M-35), sin reentrenar. Pruebas de `nucleo/`: 24 pasan en PC 3. Variantes en singular en `casos/textos.yaml` (`hay_actuar_una`, `hay_en_duda_una`). Terreno con `KRYLOV_ESPACIAL_THETA=mcmc`: «qué manda» lleva «precalculado» y el pie, `precalculado.pie_espacial_mixto`.
- **PC 3 · seguimiento:** ahora S-N4 (rondas 06:15, 07:15, 08:15); a las 08:15 S-06 y a las 08:30 S-06b (`git pull`, exportar `supervivencia` y lanzar `jerarquico`). Para una persona: los borradores `pitch/README_borrador.md` y `pitch/descripcion_borrador.md`, y tres cifras por revisar en `pitch/CIFRAS.md` («Revisión de fuentes»).

## Qué cambió respecto del plan

- **D-29:** las horas del plan son topes, no horas de inicio, en los tres computadores. No se adelanta el MCMC ni se mide encima de un entrenamiento (`AGENTS.md`, regla 21).
- **D-30 y D-31:** `estados` con 33 parámetros y `jerarquico` con 20 (anotado en `WORKPLAN.md` 11.3 y 11.4); los casos traen `etiquetas`; dormir a las 05:15 ya no es obligatorio; `supervivencia` sigue hasta las 08:30.
- Guion: la versión de 3 minutos es la principal (J-04) y, contando palabras, no cabe (176 s de habla): recorte propuesto del momento 2 en `pitch/GUION.md`.

## Próxima decisión

- Al validar `estados` y `jerarquico`: ¿la nube va al semáforo? (D-32). El equipo: quién presenta, a más tardar en H1.
- H1, a más tardar sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito. Los cuatro tienen datos (inasistencias solo en PC 3 y en PC 2, fuera del repositorio por su licencia) y el archivo malo está en el repositorio.
