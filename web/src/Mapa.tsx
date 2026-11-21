// El terreno como mapa: cada bloque en el color de su decisión (la duda achurada) y las mediciones
// reales como puntos.

import { COLOR, token } from './colores'
import type { Decision } from './decision'
import { trama, useLienzo } from './lienzo'
import type { Mapa as DatosMapa } from './tipos'

interface Props {
  mapa: DatosMapa
  bloques: (Decision | null)[]
}

export default function Mapa({ mapa, bloques }: Props) {
  const ref = useLienzo(
    (ctx, ancho, alto) => {
      const { nx, ny, x0, y0, lado } = mapa
      const w = ancho / nx
      const h = alto / ny
      const duda = trama(ctx, COLOR.en_duda, token('--color-trama'))

      // `p` viene fila por fila desde abajo a la izquierda.
      bloques.forEach((b, i) => {
        if (!b) return
        const col = i % nx
        const fila = Math.floor(i / nx)
        ctx.fillStyle = b.estado === 'en_duda' ? duda : COLOR[b.estado]
        ctx.fillRect(col * w, alto - (fila + 1) * h, w + 0.5, h + 0.5)
      })

      for (const m of mapa.puntos) {
        const px = ((m.x - x0) / (nx * lado)) * ancho
        const py = alto - ((m.y - y0) / (ny * lado)) * alto
        ctx.beginPath()
        ctx.arc(px, py, 3.5, 0, Math.PI * 2)
        ctx.fillStyle = token('--color-tinta')
        ctx.fill()
        ctx.lineWidth = 1.5
        ctx.strokeStyle = token('--color-fondo')
        ctx.stroke()
      }
    },
    [mapa, bloques],
  )

  return (
    <figure className="flex min-h-0 flex-col">
      <canvas
        ref={ref}
        className="aspect-square max-h-full w-full max-w-full self-center rounded-sm bg-superficie md:w-auto md:flex-1"
        role="img"
        aria-label="Mapa del terreno con la decisión de cada bloque"
      />
      <figcaption className="mt-2 flex items-center gap-2 text-sm text-tinta-suave">
        <span className="inline-block h-2.5 w-2.5 rounded-full border border-fondo bg-tinta" />
        Cada punto es una medición real.
      </figcaption>
    </figure>
  )
}
