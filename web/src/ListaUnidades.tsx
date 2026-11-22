// Las unidades de mayor a menor riesgo. Cada fila muestra sus 32 versiones creíbles del riesgo como
// puntos, en el color de su decisión; una sola línea del punto de corte atraviesa toda la lista.
// Cuando los puntos caen a los dos lados de la línea, la decisión está en duda. Si la unidad trae
// curva, un clic la elige.

import { memo } from 'react'
import { COLOR_SVG, FONDO } from './colores'
import type { Decision } from './decision'
import type { Estado, Unidad } from './tipos'

interface Props {
  unidades: Unidad[]
  decisiones: Decision[]
  corte: number
  elegida?: string | null
  alElegir?: (id: string) => void
}

const pct = (p: number) => `${Math.round(p * 100)}%`
const COLUMNAS = 'grid grid-cols-[0.5rem_4.5rem_1fr_3rem] gap-x-3'

// Solo se vuelve a dibujar si cambia su decisión o la elección: arrastrar un deslizador no rehace 3.840 puntos.
const Fila = memo(function Fila({
  unidad,
  estado,
  tope,
  elegida,
  alElegir,
}: {
  unidad: Unidad
  estado: Estado
  tope: number
  elegida: boolean
  alElegir?: (id: string) => void
}) {
  const x = (p: number) => `${(p / tope) * 100}%`
  const contenido = (
    <>
      <span className={`h-3 w-2 ${FONDO[estado]}`} />
      <span className={`truncate text-left font-mono text-xs ${elegida ? 'text-tinta' : 'text-tinta-suave'}`}>{unidad.etiqueta}</span>
      <svg className="h-3 w-full overflow-visible" aria-hidden>
        {unidad.muestras_p.map((s, i) => (
          <circle key={i} cx={x(s)} cy={6} r={2.6} fill={COLOR_SVG[estado]} fillOpacity={0.65} className="transition-[fill] duration-150" />
        ))}
        <line x1={x(unidad.p)} x2={x(unidad.p)} y1={-1} y2={13} stroke="var(--color-tinta)" strokeWidth={2} />
      </svg>
      <span className="text-right font-mono text-xs">{pct(unidad.p)}</span>
    </>
  )
  const clase = `${COLUMNAS} h-7 w-full items-center ${elegida ? 'bg-linea/60' : ''}`
  return (
    <li>
      {alElegir && unidad.curva ? (
        <button onClick={() => alElegir(unidad.id)} aria-pressed={elegida} className={`${clase} hover:bg-linea/40`}>
          {contenido}
        </button>
      ) : (
        <div className={clase}>{contenido}</div>
      )}
    </li>
  )
})

export default function ListaUnidades({ unidades, decisiones, corte, elegida = null, alElegir }: Props) {
  const tope = Math.min(1, Math.ceil(Math.max(corte, ...unidades.flatMap((u) => u.muestras_p)) * 10) / 10)
  const x = (p: number) => `${(p / tope) * 100}%`
  const filas = unidades.map((u, i) => ({ u, estado: decisiones[i].estado })).sort((a, b) => b.u.p - a.u.p)
  const marcas = Array.from({ length: Math.floor(tope * 5 + 1e-9) + 1 }, (_, i) => i / 5)

  return (
    <div className="flex min-h-0 flex-col">
      <div className={`${COLUMNAS} text-tinta-suave`}>
        <span />
        <span className="dato self-end">Riesgo</span>
        <div className="relative h-10">
          <span
            className="absolute top-0 -translate-x-1/2 font-mono text-xs whitespace-nowrap text-tinta transition-[left] duration-150"
            style={{ left: x(corte) }}
          >
            Punto de corte {pct(corte)}
          </span>
          {marcas.map((m) => (
            <span key={m} className="absolute bottom-0 -translate-x-1/2 font-mono text-[0.65rem] text-tenue" style={{ left: x(m) }}>
              {pct(m)}
            </span>
          ))}
        </div>
        <span />
      </div>

      <div className="desliza-lista relative max-h-[28rem] min-h-0 flex-1 overflow-y-auto border-t border-linea md:max-h-none">
        <ul className="relative py-1">
          <li aria-hidden className={`${COLUMNAS} pointer-events-none absolute inset-0 z-10`}>
            <span />
            <span />
            <span className="relative">
              <span className="absolute inset-y-0 w-px -translate-x-1/2 bg-tinta transition-[left] duration-150" style={{ left: x(corte) }} />
            </span>
          </li>
          {filas.map(({ u, estado }) => (
            <Fila key={u.id} unidad={u} estado={estado} tope={tope} elegida={u.id === elegida} alElegir={alElegir} />
          ))}
        </ul>
      </div>
      <p className="mt-2 text-sm text-tinta-suave">Cada punto es una versión creíble del riesgo; la raya, el promedio.</p>
    </div>
  )
}
