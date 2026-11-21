// El calce de columnas dentro del chat (D-35): qué columna del archivo cumple cada papel que
// recibe el modelo. Se ve y se puede cambiar antes de analizar; analizar exige confirmarlo.

import { useState } from 'react'
import type { Calce, Papel } from './tipos'

export type Asignacion = Record<string, string[]>

const VACIA = ''

// La pantalla dice quién propuso: «Claude» solo si de verdad fue Claude.
const origen = (c: Calce) =>
  c.origen === 'equipo'
    ? 'Columnas elegidas por el equipo para este caso'
    : c.origen === 'regla'
      ? 'Columnas propuestas según el nombre y el tipo de cada columna'
      : c.proveedor === 'claude'
        ? 'Columnas propuestas por Claude, que leyó un resumen de cada columna (nunca las filas)'
        : 'Columnas propuestas por un modelo de prueba'

export const asignacionDe = (calce: Calce): Asignacion =>
  Object.fromEntries(Object.entries(calce.calce).map(([papel, c]) => [papel, c.columnas]))

export const mismaAsignacion = (a: Asignacion, b: Asignacion) =>
  Object.keys(b).every((papel) => (a[papel] ?? []).join('|') === b[papel].join('|'))

// Las posiciones de un papel: las que trae el calce y, si el papel acepta más, una vacía por cada una.
function posiciones(papel: Papel, columnas: string[]): string[] {
  return Array.from({ length: Math.max(papel.maximo, columnas.length) }, (_, i) => columnas[i] ?? VACIA)
}

export default function CalceEnChat({
  calce,
  papeles,
  confirmado,
  alConfirmar,
}: {
  calce: Calce
  papeles: Papel[]
  confirmado: boolean
  alConfirmar: (asignacion: Asignacion) => void
}) {
  const [asignacion, setAsignacion] = useState<Asignacion>(() => asignacionDe(calce))
  const editable = calce.columnas.length > 0

  const cambiar = (papel: string, i: number, columna: string) =>
    setAsignacion((a) => {
      const lista = [...posiciones(papeles.find((p) => p.papel === papel)!, a[papel] ?? [])]
      lista[i] = columna
      // Una posición del medio puede quedar vacía (los papeles van por posición); las del final, no.
      return { ...a, [papel]: lista.slice(0, lista.findLastIndex((c) => c !== VACIA) + 1) }
    })

  if (confirmado) {
    const n = Object.values(asignacion).flat().filter(Boolean).length
    return (
      <details className="text-sm text-tinta-suave">
        <summary className="cursor-pointer">
          Columnas confirmadas: {n} columnas en {papeles.length} papeles
        </summary>
        <ul className="mt-2 space-y-1">
          {papeles.map((p) => (
            <li key={p.papel}>
              {p.texto}: <span className="font-mono text-tinta">{(asignacion[p.papel] ?? []).filter(Boolean).join(', ') || '(ninguna)'}</span>
            </li>
          ))}
        </ul>
      </details>
    )
  }

  return (
    <div className="aparecer rounded-[2px] border border-linea p-4">
      <p className="text-sm text-tinta-suave">
        {origen(calce)}
        {calce.precalculado && ' · precalculado'}
      </p>
      <dl className="mt-3 divide-y divide-linea">
        {papeles.map((p) => (
          <div key={p.papel} className="grid gap-x-4 gap-y-1.5 py-2.5 sm:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
            <dt className="text-sm leading-snug" title={p.texto_largo}>
              {p.texto}
              {p.minimo === 0 && <span className="text-tinta-suave"> · opcional</span>}
            </dt>
            <dd className="flex flex-wrap gap-1.5">
              {posiciones(p, asignacion[p.papel] ?? []).map((columna, i) =>
                editable ? (
                  <select
                    key={i}
                    value={columna}
                    onChange={(e) => cambiar(p.papel, i, e.target.value)}
                    aria-label={`${p.texto}, columna ${i + 1}`}
                    className="max-w-full rounded-[2px] border border-linea bg-fondo px-2 py-1 font-mono text-sm"
                  >
                    {(p.minimo < p.maximo || columna === VACIA) && <option value={VACIA}>(ninguna)</option>}
                    {calce.columnas.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                ) : (
                  columna !== VACIA && (
                    <span key={i} className="rounded-[2px] bg-superficie px-2 py-1 font-mono text-sm">
                      {columna}
                    </span>
                  )
                ),
              )}
              {calce.calce[p.papel]?.transformacion && (
                <span className="self-center text-xs text-tinta-suave">en {calce.calce[p.papel].transformacion!.nombre}</span>
              )}
            </dd>
          </div>
        ))}
      </dl>
      {calce.no_usadas.length > 0 && (
        <p className="mt-2 text-xs text-tinta-suave">
          No se usan {calce.no_usadas.length} columnas: {calce.no_usadas.slice(0, 6).join(', ')}
          {calce.no_usadas.length > 6 && '…'}
        </p>
      )}
      <button
        onClick={() => alConfirmar(asignacion)}
        className="mt-4 bg-acento px-5 py-2 text-sm font-medium text-sobre-acento hover:opacity-90"
      >
        Confirmar y analizar
      </button>
    </div>
  )
}
