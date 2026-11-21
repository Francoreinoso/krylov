// El banco como mapa: cada bloque en el color de su decisión (la duda achurada), las muestras como
// puntos y, en «¿Dónde perforo?», los pines A, B y C donde una muestra más vale más plata. Un clic
// en un pin simula esa muestra.

import { useMemo } from 'react'
import { COLOR, token } from './colores'
import type { Decision } from './decision'
import { trama, useLienzo } from './lienzo'
import type { Candidata, Mapa as DatosMapa, MedicionNueva } from './tipos'

interface Props {
  mapa: DatosMapa
  bloques: (Decision | null)[]
  candidatas?: Candidata[] | null
  nuevas?: MedicionNueva[]
  alPerforar?: (c: Candidata) => void
  ocupado?: boolean
}

export default function Mapa({ mapa, bloques, candidatas, nuevas = [], alPerforar, ocupado = false }: Props) {
  const { nx, ny, x0, y0, lado } = mapa
  // Posición en el lienzo, en fracción (0 a 1) de su ancho y alto.
  const fx = (x: number) => (x - x0) / (nx * lado)
  const fy = (y: number) => 1 - (y - y0) / (ny * lado)
  const perforadas = useMemo(() => new Set(nuevas.map((n) => n.etiqueta)), [nuevas])

  const ref = useLienzo(
    (ctx, ancho, alto) => {
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

      // Una cuadrícula tenue: cada celda es un bloque.
      ctx.strokeStyle = token('--color-fondo')
      ctx.globalAlpha = 0.35
      ctx.lineWidth = 0.6
      ctx.beginPath()
      for (let c = 1; c < nx; c++) {
        ctx.moveTo(c * w, 0)
        ctx.lineTo(c * w, alto)
      }
      for (let f = 1; f < ny; f++) {
        ctx.moveTo(0, f * h)
        ctx.lineTo(ancho, f * h)
      }
      ctx.stroke()
      ctx.globalAlpha = 1

      for (const m of mapa.puntos) {
        ctx.beginPath()
        ctx.arc(fx(m.x) * ancho, fy(m.y) * alto, 2.2, 0, Math.PI * 2)
        ctx.fillStyle = token('--color-fondo')
        ctx.globalAlpha = 0.75
        ctx.fill()
        ctx.globalAlpha = 1
      }
    },
    [mapa, bloques],
  )

  return (
    <figure className="flex h-full min-h-0 flex-col">
      <div className="relative aspect-square h-full max-w-full self-start">
        <canvas ref={ref} className="h-full w-full" role="img" aria-label="Mapa del banco con la decisión de cada bloque" />
        {nuevas.map((n) => (
          <span
            key={`n-${n.etiqueta}`}
            className="pointer-events-none absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-fondo bg-tinta"
            style={{ left: `${fx(n.x) * 100}%`, top: `${fy(n.y) * 100}%` }}
          />
        ))}
        {candidatas?.map((c) => {
          const hecha = perforadas.has(c.etiqueta)
          return (
            <button
              key={c.etiqueta}
              onClick={() => alPerforar?.(c)}
              disabled={!alPerforar || ocupado || hecha}
              title={hecha ? `Ya perforaste en ${c.etiqueta}` : `Simular una muestra en ${c.etiqueta}`}
              className="group absolute flex -translate-x-1/2 -translate-y-full flex-col items-center disabled:cursor-default"
              style={{ left: `${fx(c.x) * 100}%`, top: `${fy(c.y) * 100}%` }}
            >
              <span
                className={`titular flex h-7 w-7 items-center justify-center rounded-full text-base ${
                  hecha ? 'bg-tinta-suave text-fondo' : 'bg-tinta text-fondo group-enabled:group-hover:bg-oro'
                }`}
              >
                {c.etiqueta}
              </span>
              <span className={`h-5 w-0.5 ${hecha ? 'bg-tinta-suave' : 'bg-tinta'}`} />
            </button>
          )
        })}
      </div>
      <figcaption className="dato mt-2 flex items-center gap-2">
        <span className="inline-block h-2 w-2 rounded-full bg-fondo ring-1 ring-tinta-suave" />
        Cada punto es una muestra de un pozo. Cada cuadro, un bloque.
      </figcaption>
    </figure>
  )
}
