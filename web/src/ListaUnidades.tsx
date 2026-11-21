// Las unidades de mayor a menor riesgo: cada una con su rango creíble como barra, un punto en su
// riesgo y una sola línea del punto de corte que atraviesa toda la lista.

import { FONDO } from './colores'
import type { Unidad } from './tipos'

interface Props {
  unidades: Unidad[]
  puntoDeCorte: number
}

const pct = (p: number) => `${Math.round(p * 100)}%`

export default function ListaUnidades({ unidades, puntoDeCorte }: Props) {
  const ordenadas = [...unidades].sort((a, b) => b.p - a.p)
  const tope = Math.min(1, Math.ceil(Math.max(puntoDeCorte, ...unidades.map((u) => u.rango_alto)) * 10) / 10)
  const x = (p: number) => `${(p / tope) * 100}%`
  const marcas = Array.from({ length: Math.round(tope * 10) + 1 }, (_, i) => i / 10).filter((_, i) => i % 2 === 0)

  return (
    <div>
      <h2 className="text-xl font-semibold">De más a menos riesgo</h2>

      {/* Eje: rótulo del punto de corte y marcas */}
      <div className="mt-4 grid grid-cols-[4.5rem_1fr_3.5rem] gap-x-3 text-xs text-tinta-suave sm:text-sm">
        <span />
        <div className="relative h-10">
          <span
            className="absolute bottom-5 -translate-x-1/2 whitespace-nowrap font-semibold text-tinta"
            style={{ left: x(puntoDeCorte) }}
          >
            Punto de corte {pct(puntoDeCorte)}
          </span>
          {marcas.map((m) => (
            <span key={m} className="absolute bottom-0 -translate-x-1/2" style={{ left: x(m) }}>
              {pct(m)}
            </span>
          ))}
        </div>
        <span className="self-end text-right">Riesgo</span>
      </div>

      <div className="lista-unidades relative max-h-[26rem] overflow-y-auto border-t border-linea">
        <ul className="relative">
          {/* La línea del punto de corte, una sola para toda la lista */}
          <li
            aria-hidden
            className="pointer-events-none absolute inset-y-0 z-10 grid w-full grid-cols-[4.5rem_1fr_3.5rem] gap-x-3"
          >
            <span />
            <span className="relative">
              <span className="absolute inset-y-0 w-0.5 -translate-x-1/2 bg-tinta" style={{ left: x(puntoDeCorte) }} />
            </span>
          </li>
          {ordenadas.map((u) => (
            <li key={u.id} className="grid grid-cols-[4.5rem_1fr_3.5rem] items-center gap-x-3 py-1">
              <span className="text-sm font-medium">{u.etiqueta}</span>
              <span className="relative h-3">
                <span className="absolute inset-y-[5px] w-full bg-linea/60" />
                <span
                  className={`absolute inset-y-0 rounded-sm ${FONDO[u.estado]}`}
                  style={{ left: x(u.rango_bajo), width: `calc(${x(u.rango_alto - u.rango_bajo)} + 2px)` }}
                />
                <span
                  className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-papel bg-tinta"
                  style={{ left: x(u.p) }}
                />
              </span>
              <span className="text-right text-sm">{pct(u.p)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
