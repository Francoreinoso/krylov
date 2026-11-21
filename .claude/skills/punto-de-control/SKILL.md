---
name: punto-de-control
description: Corre un hito del plan de Krylov después del pivote a minería (h4, h5, congelado, tope de redes, entrega). Lee los tres estados, los compara con el criterio escrito en WORKPLAN.md, decide seguir o cortar, escribe el TABLERO y DECISIONES y pone el tag. Úsala en PC 3 a la hora de cada hito.
argument-hint: "[h4 | h5 | congelado | tope-de-redes | entrega]"
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Hito

Rol: `seguimiento` (PC 3). Un **hito** es una hora fija en que se mide contra un criterio escrito y se decide seguir o cortar. Quince minutos. Sin reunión larga: se mira, se decide, se anota.

## Hitos

| Hito | Hora | Tiene que existir |
|---|---|---|
| `h4` | sáb 14:30 | `leyes` responde con la red en la URL pública, con «¿Dónde perforo?»; el inicio muestra las cinco tarjetas (cuatro con su ejemplo fijo, rotulado); la ronda 1 entrena en PC 2 y PC 3, o está lista para lanzarse en 15 minutos |
| `h5` | sáb 16:30 | `flotacion` y `taludes` responden en la app con datos del motor (red o precalculado, rotulado); la ronda 2 entrena; el guion minero cabe en 3 minutos |
| `congelado` (H6) | sáb 18:00 | **Producto terminado.** Alguien que no sea de PC 1 hace el recorrido dos veces seguidas, en la URL pública y con el wifi apagado en local. Nada nuevo entra |
| Tope de redes | sáb 20:30 | Última hora para pasar un motor a `red`. No lleva tag |
| `entrega` | dom 08:00 | Repositorio oficial con descripción, logo, README y URL pública |

Los criterios exactos y qué hacer si fallan están en `WORKPLAN.md`, sección 6.5. Los hitos `h0` y `h1` son de antes del pivote.

## Pasos

1. Corre primero la skill `ronda`.
2. **Verifica corriendo:** abre la URL pública desde un teléfono y recorre lo que el hito pide. Comprueba que el último commit está en los dos repositorios: `git ls-remote origin main` y `git ls-remote https://github.com/Silent-math/krylov.git main` dan el mismo identificador.
3. Compara con el criterio de `WORKPLAN.md` para ese hito. Por cada punto: pasa o no pasa.
4. **Si algo no pasa:** aplica el camino alternativo escrito. La regla general es **cortar**: lo que no está a su hora sale del demo. No se mueve la hora de las 18:00.
5. Escribe `estado/TABLERO.md`, con la tabla «Los cinco casos» al día, y agrega a `DECISIONES.md` lo decidido, con hora y motivo. Solo agregar.
6. Si el demo funciona: `git tag <hito> && git push origin main --tags`.
7. Avisa a los otros dos en voz alta qué cambió para ellos.

## En `h4`

Si `leyes` no está en la URL pública, PC 1 deja todo y la saca: es el demo mínimo. Si la ronda 1 no está lista, se lanza cuando esté y se valida igual a las 16:10, con lo que alcanzó. Si a las 15:15 un motor de la ronda 1 no tiene prueba de humo, sale con el método lento y su computador pasa a la ronda 2.

## En `h5` y en el tope de redes

Para cada motor nuevo se decide quién responde su tarjeta: la red (`KRYLOV_MOTOR_<ID>=red`) si pasó `validar-motor`; si no pasó pero mejora, puede seguir entrenando después de la ronda 2 en el computador que quede libre; si no, el MCMC precalculado (`mcmc`), rotulado «precalculado». Una tarjeta que no tiene ni su método lento sale del inicio a las 17:30 y queda en el pitch como hoja de ruta.

Orden de corte, del primero que cae al último: `desgaste`, `sismico`, `cinetica`, `deformacion`. El mapa de `leyes` y «¿Dónde perforo?» no se cortan nunca. La frase del guion para cada caso está en la sección 6.5.

A las 20:30 se cierra: la columna «Responde» del tablero queda fija, PC 1 regenera el estático de lo que haya cambiado (P-30) y el guion se cierra con quién responde cada tarjeta.

## En `congelado`

Lo que no funciona se saca de la pantalla. Desde aquí solo se corrigen errores y se pule lo que existe: textos, orden de las tarjetas, colores, velocidad. La única excepción es quién responde una tarjeta, hasta las 20:30. Cualquier pedido de función nueva se responde con «va a la lámina de hoja de ruta».

## Terminado cuando

TABLERO y DECISIONES están subidos, el tag existe en los dos repositorios (salvo en el tope de redes) y los tres saben qué sigue.
