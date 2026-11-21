# Caso del terreno (S-04): deja datos/demo/terreno.csv y datos/demo/terreno_grilla.csv.
#
# Fuente: paquete `sp` de R (versión 2.1.4 en PC 3), datos `meuse` y `meuse.grid`. Licencia GPL (>= 2).
#   meuse:      155 muestras de suelo junto al río Mosa (Países Bajos), 14 columnas.
#   meuse.grid: 3.103 celdas de 40 m que cubren el área de estudio.
# `dist` es la distancia al río normalizada entre 0 y 1. En `meuse` se tomó de la celda más cercana de
# `meuse.grid`, así que las dos columnas están en la misma escala.
#
# Qué deja:
#   terreno.csv:        x, y, zinc, dist (155 filas). zinc en mg/kg; x, y en metros (RD New, EPSG:28992).
#   terreno_grilla.csv: x, y, dist (3.103 celdas).
# No se esconde ninguna medición aquí: el examen del terreno lo arma `amortizacion` (A-11).
#
# Uso, desde la raíz del repositorio (no baja nada; necesita R con el paquete sp):
#   Rscript datos/preparar/terreno.R
# Sin R: las mismas tablas se pueden leer de los .rda del paquete con `uv run --with pyreadr` (STACK.md, 4.2).

suppressMessages(library(sp))
data(meuse)
data(meuse.grid)

stopifnot(nrow(meuse) == 155, ncol(meuse) == 14, nrow(meuse.grid) == 3103)
stopifnot(!anyNA(meuse[, c("x", "y", "zinc", "dist")]), !anyNA(meuse.grid[, c("x", "y", "dist")]))

puntos <- meuse[, c("x", "y", "zinc", "dist")]
grilla <- meuse.grid[, c("x", "y", "dist")]

dir.create("datos/demo", recursive = TRUE, showWarnings = FALSE)
write.csv(puntos, "datos/demo/terreno.csv", row.names = FALSE, quote = FALSE)
write.csv(grilla, "datos/demo/terreno_grilla.csv", row.names = FALSE, quote = FALSE)

cat(sprintf("datos/demo/terreno.csv: %d filas; %d superan 720 mg/kg de zinc\n", nrow(puntos), sum(puntos$zinc > 720)))
cat(sprintf("datos/demo/terreno_grilla.csv: %d celdas; dist entre %.3f y %.3f\n", nrow(grilla), min(grilla$dist), max(grilla$dist)))
