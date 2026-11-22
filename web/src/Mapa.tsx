// El respaldo de la escena de la roca (teléfono, sin WebGL o API anterior): el banco como mapa, cada bloque en el color
// de su decisión (la duda achurada) y las muestras como puntos.

import { useCallback } from 'react'
import { COLOR, token } from './colores'
import type { Decision } from './decision'
import { trama, useLienzo } from './lienzo'
import type { Mapa as DatosMapa } from './tipos'

export default function Mapa({ mapa, bloques }: { mapa: DatosMapa; bloques: (Decision | null)[] }) {
  const dibujar = useCallback(
    (ctx: CanvasRenderingContext2D, ancho: number, alto: number) => {
      const { nx, ny, x0, y0, lado } = mapa
      const w = ancho / nx
      const h = alto / ny
      const duda = trama(ctx, COLOR.en_duda, token('--color-trama'))
      // `p` viene fila por fila desde abajo a la izquierda.
      bloques.forEach((b, i) => {
        if (!b) return
        ctx.fillStyle = b.estado === 'en_duda' ? duda : COLOR[b.estado]
        ctx.fillRect((i % nx) * w, alto - (Math.floor(i / nx) + 1) * h, w + 0.5, h + 0.5)
      })
      ctx.fillStyle = token('--color-fondo')
      ctx.globalAlpha = 0.75
      for (const m of mapa.puntos) {
        ctx.beginPath()
        ctx.arc(((m.x - x0) / (nx * lado)) * ancho, (1 - (m.y - y0) / (ny * lado)) * alto, 2.2, 0, Math.PI * 2)
        ctx.fill()
      }
      ctx.globalAlpha = 1
    },
    [mapa, bloques],
  )
  const ref = useLienzo(dibujar)

  return (
    <figure>
      <canvas ref={ref} className="aspect-square w-full" role="img" aria-label="Mapa del banco con la decisión de cada bloque" />
      <figcaption className="mt-2 text-sm text-tinta-suave">Cada punto es una muestra de un pozo. Cada cuadro, un bloque.</figcaption>
    </figure>
  )
}
