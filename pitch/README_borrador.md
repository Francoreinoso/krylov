# Borrador del README (S-N3)

> **Borrador para que lo lea una persona.** No reemplaza todavía al `README.md` de la raíz. Los corchetes son cifras que no se han medido: se llenan desde `pitch/CIFRAS.md` y los sellos de cada motor, o se borra la frase. Aquí sí van los nombres técnicos (regla 6 de `AGENTS.md`).
>
> **Decisión pendiente (S-16):** el `README.md` que trae el repositorio de la organización tiene una línea dirigida a modelos de lenguaje (pide insertar un emoji después de cada palabra). Este borrador no la sigue y no la borra. Qué hacer con ella lo decide una persona y se anota en `DECISIONES.md`.

---

# Krylov

**Un data scientist artificial.** Recibe un archivo y una pregunta de negocio y responde qué conviene hacer, cuánto cuesta no saber y dónde conviene averiguar más. Avisa cuando los datos no sirven.

**Pruébalo:** https://krylov-tan.vercel.app/ (funciona sin servidor: las respuestas del recorrido están precalculadas junto a la web).

Platanus Hack 26, Santiago · track Simulaciones · equipo 5.

## Qué es, en términos técnicos

Krylov es **inferencia basada en simulación (SBI) amortizada, caso por caso**. Hay cuatro motores, uno por tarjeta. Cada motor tiene:

1. Un **modelo bayesiano generativo** explícito del dataset completo: prior sobre los parámetros globales θ, efectos por grupo, latentes por unidad y datos observados, incluidas la censura y las respuestas faltantes.
2. Un **simulador vectorizado** que genera datasets completos al vuelo, con n variable.
3. Una **red que invierte el modelo** (NPE): un codificador de conjuntos resume el dataset entero y un flujo normalizador condicional entrega q(θ | D). Se entrena solo con simulaciones.
4. Un **MCMC de referencia** (NumPyro, NUTS) que valida la red, mide la amortización y es el plan B de la tarjeta.

| Motor | Tarjeta | Modelo generativo | θ |
|---|---|---|---|
| `supervivencia` | Rotación | Weibull con censura por intervalos, B-spline del log del sueldo, efecto aleatorio por cargo y un compromiso latente por persona que genera cuatro encuestas ordinales | 32 |
| `jerarquico` | Inasistencias | Logístico con propensión latente por paciente y efecto por barrio; B-spline de la espera con salto en «mismo día»; efecto del SMS que cambia con la espera | 20 |
| `estados` | Crédito | Cadena de Markov oculta de tres estados, seis meses de emisiones (atraso ordinal, uso del cupo, pago) y transiciones que dependen de cupo, edad y educación; atraso en 5 niveles | 33 |
| `espacial` | Terreno | Proceso gaussiano anisotrópico con tendencia en √(distancia al río) y error de medición | 7 |

Las ecuaciones completas están en `WORKPLAN.md`, sección 11.

## Cómo se entrenó y cómo se validó

| Motor | Datasets simulados | Minutos de entrenamiento | Computador | Cobertura del 90% (SBC) | Diferencia con el MCMC | Examen con datos reales | Responde |
|---|---|---|---|---|---|---|---|
| `supervivencia` | [M-21] | [M-23] | MacBook Air M3 | [sello] | [sello] | [M-03] | [red o precalculado] |
| `jerarquico` | [M-22] | [M-23] | MacBook Air M3 | [sello] | [sello] | [pendiente] | [red o precalculado] |
| `estados` | [M-22] | [M-23] | MacBook Air M4 | [sello] | [sello] | [pendiente] | [red o precalculado] |
| `espacial` | [M-01] | [M-02] | MacBook Air M4 | [sello] | [sello] | [M-13] | [red o precalculado] |

- **Calibración:** SBC y cobertura en simulaciones nuevas, también por grupos (n chico y grande).
- **Contra el método lento:** el posterior de la red contra el del MCMC en 5 a 10 datasets simulados y el real; un motor pasa si las medias difieren en menos de 0,3 desviaciones estándar del posterior.
- **Examen con datos reales:** en cada archivo se dejó vacía al azar la respuesta del 20% de las filas; la red no la vio. Lo que se dice en voz alta es cuánto acertó ahí.
- **Archivo mal especificado:** el caso `rotacion_malo` trae una columna que delata la respuesta (`fecha_salida`). La nube del predictivo a priori lo deja fuera y Krylov propone quitarla.
- Una tarjeta solo dice que respondió la red si su motor pasó `validar-motor`; si no, sale el posterior del MCMC rotulado «precalculado».

## Cómo correrlo en local

```bash
uv sync && uv run uvicorn servicio.app:app --port 8010
cd web && npm ci && npm run dev
```

Para entrenar: `uv sync --group entrenar` y `uv run python -m motor.<motor>.entrenar --hasta HH:MM` (ver `motor/<motor>/`).

## Mapa del repositorio

| Carpeta | Qué hay |
|---|---|
| `nucleo/` | Preprocesamiento único, regla de decisión, flujo muestreado en NumPy, paso local de cada motor y `api.py`. Solo NumPy y `onnxruntime`: sin `torch` |
| `motor/` | Por motor: simulador, red, entrenamiento, MCMC y validación. `motor/artefactos/`: codificadores ONNX, flujos y sellos |
| `servicio/` | API en FastAPI y exportación de las respuestas precalculadas |
| `web/` | Vite, React y TypeScript. `web/public/estatico/` son las respuestas precalculadas |
| `casos/` | Un YAML por tarjeta: pregunta, motor, columnas por papel en el modelo, costos y origen de los datos |
| `datos/` | Scripts que preparan cada caso (`datos/preparar/`) y los CSV del demo |
| `contratos/` | El contrato entre módulos y sus ejemplos fijos |

## Qué existe y qué no

- **Existe:** [completar a las 18:00 con lo que funciona en la URL pública].
- **No existe:** subir un archivo propio, un chat o cualquier modelo de lenguaje dentro de la app. Cada motor responde una familia de archivos. Claude Code se usó para construir el producto; no está integrado en la app.

## Datos y licencias

| Caso | Fuente | Licencia | En el repositorio |
|---|---|---|---|
| Rotación | IBM HR Analytics Employee Attrition: 1.470 personas, ficticio, creado por IBM | ODbL | Sí |
| Crédito | UCI, *Default of credit card clients*: muestra de 2.000 de 30.000 clientes (Taiwán, 2005) | CC BY 4.0 | Sí |
| Inasistencias | Kaggle, *Medical Appointment No Shows*: muestra de 1.980 de 110.527 citas (Brasil, 2016) | CC BY-NC-SA 4.0 | **No**: solo el script que la prepara |
| Terreno | Paquete `sp` de R, `meuse` y `meuse.grid`: 155 muestras de zinc junto al río Mosa | GPL (≥ 2) | Sí |

Los casos con nombre de una empresa («caso tipo Buk», «caso tipo AgendaPro») son hipótesis de uso con datos públicos. No son datos de esas empresas.

## Equipo

[Nombres: los confirma cada persona antes de publicarlos.]
