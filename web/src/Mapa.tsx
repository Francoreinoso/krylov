// El respaldo de la escena de la roca (teléfono, sin WebGL o API anterior): el banco como mapa, cada bloque en el color
// de su decisión (la duda achurada) y las muestras como puntos.

import { useCallback } from 'react'
import { COLOR, token } from './colores'
import type { Decision } from './decision'
import { trama, useLienzo } from './lienzo'
import type { Estado, Mapa as DatosMapa } from './tipos'

const ORDEN: Estado[] = ['actuar', 'en_duda', 'no_actuar']

export default function Mapa({ mapa, bloques, rotulos }: { mapa: DatosMapa; bloques: (Decision | null)[]; rotulos: Record<Estado, string> }) {
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
      <figcaption className="mt-3 text-sm text-tinta-suave">
        <ul className="mb-2 flex flex-wrap gap-x-5 gap-y-1 text-base text-tinta">
          {ORDEN.map((e) => (
            <li key={e} className="flex items-center gap-2">
              <span aria-hidden className="h-3.5 w-3.5" style={{ background: e === 'en_duda' ? `repeating-linear-gradient(135deg, ${COLOR.en_duda} 0 3px, ${token('--color-trama')} 3px 5px)` : COLOR[e] }} />
              {rotulos[e]}
            </li>
          ))}
        </ul>
        Cada punto es una muestra de un pozo. Cada cuadro, un bloque.
      </figcaption>
    </figure>
  )
}
