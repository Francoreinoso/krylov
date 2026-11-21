// El examen: qué pasó cuando Krylov respondió sobre datos reales que no había visto.
// Cada tramo compara lo que dijimos con lo que pasó. Todo sale del JSON.

import type { Examen as DatosExamen } from './tipos'

const pct = (p: number) => `${Math.round(p * 100)}%`

export default function Examen({ examen }: { examen: DatosExamen }) {
  return (
    <div>
      <h2 className="titular text-3xl">El examen</h2>
      <p className="mt-2 text-sm">{examen.frase}</p>
      {examen.tramos.length > 1 && (
        <ul className="mt-3 space-y-1.5 text-xs text-tinta-suave">
          <li className="grid grid-cols-[4.5rem_1fr] gap-2">
            <span>Dijimos</span>
            <span>Pasó</span>
          </li>
          {examen.tramos.map((t) => (
            <li key={t.dijimos} className="grid grid-cols-[4.5rem_1fr] items-center gap-2">
              <span className="text-tinta">{pct(t.dijimos)}</span>
              <span className="relative h-2.5 rounded-sm bg-linea">
                <span className="absolute inset-y-0 left-0 rounded-sm bg-tinta-suave" style={{ width: pct(t.paso) }} />
                <span className="absolute -inset-y-0.5 w-0.5 bg-tinta" style={{ left: pct(t.dijimos) }} />
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
