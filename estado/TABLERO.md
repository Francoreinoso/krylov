# Tablero · cómo vamos contra el plan

Lo escribe solo `seguimiento` (PC 3), en cada ronda y en cada hito. Se carga en cada sesión de los tres computadores: mantenerlo bajo 45 líneas.

**Actualizado:** sáb 21-nov 05:03 · **Hito vigente:** H0 cerrado (tag `h0`). Próximo: antes de dormir, 05:15; H1 a más tardar 08:45 · **Producto terminado: sáb 18:00**

**URL pública:** https://krylov-tan.vercel.app/ (P-02, 03:59). Verificada en PC 3 en tamaño teléfono y por PC 1 desde un teléfono (04:01). Falta confirmar con datos móviles.

## Semáforo

| Rol | Estado | Nota |
|---|---|---|
| producto (PC 1) | 🟢 adelantado | P-01, P-02, P-03 y P-N1 verificados en PC 3 (`decision.ts`: 45 casos pasan) |
| amortizacion (PC 2) | 🟢 adelantado | A-01 a A-04, A-B1 a A-B4, A-N1, A-N3, el código de A-11 y A-12, la nube común (A-13) y parte de A-N5 en `main`; 15 pruebas de `nucleo/` pasan en PC 3. `espacial` entrena desde las 03:50 |
| seguimiento (PC 3) | 🟢 adelantado | S-02 a S-05, S-N1 a S-N3, S-08, S-12 y los textos de pantalla v1 hechos (D-29). `supervivencia` entrena en PC 3 desde las 04:05: 2,1 millones de datasets a las 04:46 |

## Antes de dormir (05:15): cómo vamos

- ✅ Dos entrenamientos corriendo con puntos de guardado: `espacial` en PC 2, `supervivencia` en PC 3. Los dos terminan solos a las 08:30.
- ✅ URL pública con el esqueleto. ✅ Datos de rotación, terreno, crédito y el archivo malo en el repositorio. Inasistencias: solo en PC 3 (licencia no comercial); se regenera con `datos/preparar/inasistencias.py`.
- Falta: la lista nocturna de PC 1 escrita en su estado antes de dormir.

## Siguiente tarea de cada uno, y la que viene después (D-29)

- **PC 1 · producto:** ahora P-N2 (mapa en canvas con el ejemplo espacial); después P-N3 (nube). El texto de portada y cierre para P-13 ya está en `pitch/LAMINAS.md`. Ojo: P-03 agregó `@fontsource-variable/archivo`: quien tenga la web abierta hace `npm ci` y reinicia `npm run dev`. **Aviso de PC 2:** `codificador.onnx` viene con `codificador.onnx.data`; el servicio necesita los dos (antes de A-10).
- **PC 2 · amortizacion:** sesión A: A-05 y a dormir a las 05:15; el agente sigue con A-N3. Sesión B: A-N2. **Nuevo:** las plantillas de texto están en `casos/textos.yaml`; `nucleo/api.py` las lee en vez de escribir frases en el código. Tu pedido a PC 3 está hecho: `supervivencia` corre en PC 3 desde las 04:05.
- **PC 3 · seguimiento:** ahora S-N4 (rondas de lectura 06:15, 07:15, 08:15); lo demás de la mañana exige a una persona o números de los motores. Para una persona en la mañana: borradores `pitch/README_borrador.md` y `pitch/descripcion_borrador.md`, y tres cifras por revisar (sección «Revisión de fuentes» de `pitch/CIFRAS.md`). Nada pesado aquí. A dormir a las 05:15, enchufado y con la tapa abierta. 08:15: S-06; 08:30: S-06b (exportar `supervivencia` y lanzar `jerarquico`).

## Qué cambió respecto del plan

- **D-29 (texto final de las 04:38): las horas del plan son topes, no horas de inicio, en los tres computadores.** Quien termina una tarea toma la siguiente de su lista sin esperar; lo que no tiene insumo se hace contra el ejemplo fijo y se anota. No se adelanta el MCMC ni se mide encima de un entrenamiento (`AGENTS.md`, regla 21).
- `supervivencia` se lanzó a las 04:05 y `espacial` a las 03:50: casi una hora más de entrenamiento cada uno.
- Guion: la versión de 3 minutos es la principal (J-04). «Escondimos a 294 personas reales» pasó a «escondimos la respuesta de 294 personas del archivo»: el archivo de rotación es ficticio (D-01).
- D-26 ya está en todos los archivos del plan (revisado 04:47 con `git grep`: lo que nombra a `regresion` o «Sube tus datos» dice que se cortó).

## Próxima decisión

- Quién presenta: se decide después (a más tardar en H1). El pitch dura 3 minutos.
- H1, a más tardar sáb 08:45: ¿sobrevivió la noche? Criterios en `WORKPLAN.md`, sección 6.5.

## Casos en el inicio

`casos/INICIO`: rotación, terreno, inasistencias, crédito. Con datos: rotación, terreno y crédito. Inasistencias: S-N1 esta noche.
