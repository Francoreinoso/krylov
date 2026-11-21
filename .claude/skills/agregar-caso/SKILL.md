---
name: agregar-caso
description: Prepara un caso de uso de Krylov (una decisión de la mina, una tarjeta del inicio) sin tocar código - genera el archivo de datos con semilla fija o usa uno real con licencia abierta, guarda aparte la verdad escondida, comprueba que cada columna cumple su papel en el modelo del motor, completa el YAML con el origen de los datos y registra sus cifras. Úsala en PC 3 para leyes, taludes, flotacion, flota, sismicidad y el archivo que no alcanza. Tope de 25 minutos por caso.
argument-hint: "[nombre del caso]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Preparar un caso de uso

Rol: `seguimiento`; `producto` verifica que se ve. Un **caso de uso** es una decisión de la mina resuelta con un motor, un archivo de datos y sus costos. Son cinco (`AGENTS.md`, «Las cinco decisiones»), cada uno en `casos/<nombre>.yaml`, con las columnas **por papel en el modelo generativo del motor** (`WORKPLAN.md`, sección 11; formato en `contratos/CONTRATO.md`). Esta skill deja listo el archivo de datos, su verdad escondida y un YAML que calza. **Tope: 25 minutos por caso.**

## Las dos formas de archivo

| Forma | Casos | Una fila por | Columnas |
|---|---|---|---|
| Espacial | `leyes` (motor `espacial`) | muestra | `x`, `y`, `valor` |
| Series | `taludes`, `flotacion`, `flota`, `sismicidad` (motores de series) | medición | `unidad`, `tiempo`, `valor`, más lo propio que pida el modelo del motor (sección 11) |

## Pasos

1. **Datos reales primero, 20 minutos como máximo.** Si existe un archivo real con licencia abierta que calce con el motor, se usa y se dice. Los candidatos ya encontrados están en D-37 (`DECISIONES.md`). Mira la licencia: el repositorio es público; lo que no permite redistribuir no se sube. Si el archivo real cae fuera de lo simulado, el semáforo lo dice y el demo usa el simulado.
2. **Si no hay real, escribe `datos/preparar/<caso>.py`** (semilla fija; el modelo a seguir es `datos/preparar/leyes.py`). Genera los datos con las mismas ecuaciones del motor (sección 11) y parámetros fijos que el motor no ve. Deja dos archivos:
   - `datos/demo/<caso>.csv`, con la forma de la tabla de arriba y tamaños dentro de los rangos del simulador.
   - `datos/demo/<caso>_verdad.csv`, la **verdad escondida**: lo que pasó de verdad con cada unidad. Nunca entra al motor; sirve solo para el examen.
3. **Los archivos de apoyo** que pide el plan: uno de prueba por caso para subir en el chat (`datos/demo/subida_<caso>.csv`, S-24) y el archivo que no alcanza de la tecla `M` (`leyes_pocos`, un banco con 12 pozos; si alcanza, una serie demasiado corta). El segundo tiene que dar rojo con su motivo.
4. **Con PC 2 (S-24):** el archivo cae dentro de lo que simula el motor (predictivo a priori: `uv run python -m motor.<motor>.simular --revisar`). Si PC 2 cambió un prior, regenera con la misma semilla.
5. **Completa el YAML:** cada nombre de columna contra el archivo; `motor`; `unidad`; rótulos que sean decisiones, no pronósticos; el límite y el horizonte donde el modelo los pida. **`origen_datos` dice de dónde vienen los datos** (se ve en pantalla tal cual) y **`sintetico: true` si el archivo es simulado**. `tarjeta.sponsor` va en `null`: ya no hay casos con nombre de sponsor, y ninguna tarjeta lleva el nombre de una minera ni de una faena (regla 10).
6. **Costos.** Cada uno necesita valor, mínimo y máximo del deslizador, etiqueta y un id de `pitch/CIFRAS.md`. Son supuestos: se dicen como supuestos. En `taludes` y `sismicidad` hablan de producción y equipos; no se le pone precio a una vida (regla 22).
7. **Míralo en la app** cuando el motor responda: los tres colores aparecen (no todo de un color), el semáforo no está en rojo, el examen muestra números y dice «con datos simulados», y en los casos de lista la curva se ve con su abanico.

Los textos de minería de la tarjeta van en el YAML y en `casos/textos.yaml`, nunca en el código, y cada palabra del rubro se explica la primera vez (`GLOSARIO.md`, «Minería en simple»).

## Si los colores no dicen nada

- Todo de un color: mira dónde queda el punto de corte respecto de las probabilidades de las unidades. Mueve los costos por defecto a valores que puedas defender en voz alta y registra el cambio. No los ajustes para que el número se vea más grande.
- Todo en duda: pocos datos. Prueba con más unidades o series más largas, dentro de los rangos que el motor conoce (`WORKPLAN.md`, sección 11).

## Terminado cuando

El CSV, la verdad escondida y el script están subidos, PC 2 confirmó que el archivo cae dentro de lo simulado, el YAML calza con el archivo y dice el origen de los datos, y las cifras tienen fila en `pitch/CIFRAS.md`.
