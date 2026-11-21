// Las unidades de mayor a menor riesgo. Cada fila muestra sus 32 versiones creíbles del riesgo como
// puntos, en el color de su decisión; una sola línea del punto de corte atraviesa toda la lista.
// Cuando los puntos caen a los dos lados de la línea, la decisión está en duda.

import { memo } from 'react'
import { COLOR_SVG } from './colores'
import type { Decision } from './decision'
import type { Estado, Unidad } from './tipos'

interface Props {
  unidades: Unidad[]
  decisiones: Decision[]
  corte: number
}

const pct = (p: number) => `${Math.round(p * 100)}%`
const COLUMNAS = 'grid grid-cols-[4rem_1fr_3rem] gap-x-3'

// Solo se vuelve a dibujar si cambia su decisión: arrastrar un deslizador no rehace 3.840 puntos.
const Fila = memo(function Fila({ unidad, estado, tope }: { unidad: Unidad; estado: Estado; tope: number }) {
  const x = (p: number) => `${(p / tope) * 100}%`
  return (
    <li className={`${COLUMNAS} h-6 items-center`}>
      <span className="text-sm">{unidad.etiqueta}</span>
      <svg className="h-3 w-full overflow-visible" aria-hidden>
        {unidad.muestras_p.map((s, i) => (
          <circle key={i} cx={x(s)} cy={6} r={3} fill={COLOR_SVG[estado]} fillOpacity={0.6} className="transition-[fill] duration-150" />
        ))}
        <line x1={x(unidad.p)} x2={x(unidad.p)} y1={-1} y2={13} stroke="var(--color-tinta)" strokeWidth={2} />
      </svg>
      <span className="text-right text-sm">{pct(unidad.p)}</span>
    </li>
  )
})

export default function ListaUnidades({ unidades, decisiones, corte }: Props) {
  const tope = Math.min(1, Math.ceil(Math.max(corte, ...unidades.flatMap((u) => u.muestras_p)) * 10) / 10)
  const x = (p: number) => `${(p / tope) * 100}%`
  const filas = unidades.map((u, i) => ({ u, estado: decisiones[i].estado })).sort((a, b) => b.u.p - a.u.p)
  const marcas = Array.from({ length: Math.floor(tope * 5 + 1e-9) + 1 }, (_, i) => i / 5)

  return (
    <div className="flex min-h-0 flex-col">
      <h2 className="text-xl font-semibold">De más a menos riesgo</h2>
      <p className="text-sm text-tinta-suave">Cada punto es una versión creíble del riesgo; la raya, el promedio.</p>

      <div className={`${COLUMNAS} mt-3 text-xs text-tinta-suave`}>
        <span />
        <div className="relative h-10">
          <span
            className="absolute top-0 -translate-x-1/2 whitespace-nowrap text-sm font-semibold text-tinta transition-[left] duration-150"
            style={{ left: x(corte) }}
          >
            Punto de corte {pct(corte)}
          </span>
          {marcas.map((m) => (
            <span key={m} className="absolute bottom-0 -translate-x-1/2" style={{ left: x(m) }}>
              {pct(m)}
            </span>
          ))}
        </div>
        <span className="self-end text-right">Riesgo</span>
      </div>

      <div className="desliza-lista relative max-h-[28rem] min-h-0 flex-1 overflow-y-auto border-t border-linea md:max-h-none">
        <ul className="relative py-1">
          <li aria-hidden className={`${COLUMNAS} pointer-events-none absolute inset-0 z-10`}>
            <span />
            <span className="relative">
              <span
                className="absolute inset-y-0 w-0.5 -translate-x-1/2 bg-tinta transition-[left] duration-150"
                style={{ left: x(corte) }}
              />
            </span>
          </li>
          {filas.map(({ u, estado }) => (
            <Fila key={u.id} unidad={u} estado={estado} tope={tope} />
          ))}
        </ul>
      </div>
    </div>
  )
}
