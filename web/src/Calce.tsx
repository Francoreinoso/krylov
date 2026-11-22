// Qué columna del archivo cumple cada papel del modelo (D-35). Se ve, se puede cambiar y hay que confirmarlo antes de
// analizar. Dice quién lo propuso y qué leyó: un modelo de lenguaje lee el nombre y un resumen de cada columna, nunca
// las filas. Mientras llega la propuesta, las columnas del archivo esperan arriba y después bajan a su papel.

import { useState } from 'react'
import { asignacionDe, transformacionEnPalabras, type Asignacion } from './asignacion'
import type { Calce as DatosCalce, Papel } from './tipos'

const NINGUNA = ''

// Quién propuso, en una línea que se puede decir en voz alta.
function quienPropuso(c: DatosCalce): string {
  if (c.origen === 'equipo') return 'Las columnas de este archivo ya las eligió el equipo.'
  if (c.origen === 'regla') return 'Krylov las eligió por el nombre y el tipo de cada columna.'
  if (c.propuesto_por?.tipo === 'equipo') return 'Las columnas de este archivo ya las eligió el equipo.'
  const quien = c.propuesto_por?.proveedor ?? (c.proveedor === 'claude' ? 'Claude' : c.proveedor === 'groq' ? 'Groq' : null)
  return `Las propuso un modelo de lenguaje${quien ? ` (${quien})` : ''}, que leyó el nombre y un resumen de cada columna, nunca las filas.`
}

interface Props {
  columnas: string[] // las del archivo, apenas se lee
  calce: DatosCalce | null // null mientras llega la propuesta
  papeles: Papel[]
  alConfirmar: (a: Asignacion) => void
}

export default function Calce({ columnas, calce, papeles, alConfirmar }: Props) {
  const [asignacion, setAsignacion] = useState<Asignacion | null>(null)
  const actual = asignacion ?? (calce ? asignacionDe(calce) : {})
  const usadas = new Set(Object.values(actual).flat())
  const cambiar = (papel: string, columna: string) => setAsignacion({ ...actual, [papel]: columna ? [columna] : [] })
  const faltan = papeles.filter((p) => p.minimo > 0 && !(actual[p.papel] ?? []).some(Boolean))

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="titular text-4xl">¿Qué columna es qué?</h1>
        <p className="mt-2 text-tinta-suave">{calce ? quienPropuso(calce) : 'Krylov está leyendo las columnas de tu archivo.'}</p>
      </div>

      <ul className="flex flex-wrap gap-1.5" aria-label="Columnas del archivo">
        {columnas.map((c) => (
          <li key={c} className={`border px-2 py-0.5 font-mono text-sm transition-opacity duration-500 ${usadas.has(c) ? 'border-cobre/60 text-tinta' : 'border-linea text-tenue'}`}>
            {c}
          </li>
        ))}
      </ul>

      <dl className="divide-y divide-linea border-y border-linea">
        {papeles.map((p, i) => {
          const columna = actual[p.papel]?.[0] ?? NINGUNA
          const t = transformacionEnPalabras(calce?.calce[p.papel]?.transformacion ?? null, columna)
          return (
            <div key={p.papel} className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)] items-center gap-4 py-3">
              <dt>
                {p.texto}
                {p.minimo === 0 && <span className="text-tenue"> · si lo tienes</span>}
              </dt>
              <dd className="min-w-0">
                {calce ? (
                  <div className="llega" style={{ animationDelay: `${i * 90}ms` }}>
                    <div className="selector">
                      <select value={columna} onChange={(e) => cambiar(p.papel, e.target.value)} aria-label={p.texto}>
                        {(p.minimo === 0 || columna === NINGUNA) && <option value={NINGUNA}>Ninguna</option>}
                        {calce.columnas.map((c) => (
                          <option key={c} value={c}>
                            {c}
                          </option>
                        ))}
                      </select>
                    </div>
                    {t && <p className="mt-1 font-mono text-sm text-oro">{t}</p>}
                  </div>
                ) : (
                  <div className="h-10 border border-dashed border-linea" />
                )}
              </dd>
            </div>
          )
        })}
      </dl>

      {calce && calce.no_usadas.length > 0 && (
        <p className="text-sm text-tenue">Krylov no usa {calce.no_usadas.length === 1 ? 'la columna' : 'las columnas'} {calce.no_usadas.join(', ')}.</p>
      )}

      <button
        disabled={!calce || faltan.length > 0}
        onClick={() => alConfirmar(actual)}
        className="self-start bg-cobre px-6 py-3 text-lg font-semibold text-fondo transition-opacity hover:opacity-90 disabled:opacity-40"
      >
        {faltan.length ? `Falta: ${faltan[0].texto.toLowerCase()}` : 'Confirmar y analizar'}
      </button>
    </div>
  )
}
