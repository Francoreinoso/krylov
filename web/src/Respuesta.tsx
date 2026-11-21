// Vista 2 · la respuesta de un caso: titular, lo que cuesta no saber y las unidades en tres colores.

import type { Analisis, Estado } from './tipos'

const COLOR: Record<Estado, string> = {
  actuar: 'bg-actuar',
  en_duda: 'bg-en-duda',
  no_actuar: 'bg-no-actuar',
}
const ORDEN: Estado[] = ['actuar', 'en_duda', 'no_actuar']

const plata = (valor: number, moneda: string) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: moneda, maximumFractionDigits: 0 }).format(valor)

const porcentaje = (p: number) => `${Math.round(p * 100)}%`

export default function Respuesta({ analisis }: { analisis: Analisis }) {
  const { semaforo, rotulos, costo_de_no_saber, resumen_colores, unidades } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'

  return (
    <section>
      {analisis.precalculado && (
        <span className="rounded-full bg-stone-200 px-3 py-1 text-xs font-medium uppercase tracking-wide text-stone-700">
          Precalculado
        </span>
      )}
      <h1 className="mt-3 text-3xl font-semibold tracking-tight">{analisis.titular}</h1>

      {rojo && (
        <div className="mt-6 rounded-2xl bg-red-50 p-5 text-red-900 ring-1 ring-red-200">
          <p className="font-medium">{semaforo.motivo}</p>
          {semaforo.propuesta && <p className="mt-2 text-sm">{semaforo.propuesta.texto}</p>}
        </div>
      )}

      {costo_de_no_saber && (
        <div className="mt-8">
          <p className="text-sm text-stone-500">{rotulos.costo_de_no_saber}</p>
          <p className="text-6xl font-semibold tabular-nums">
            {plata(costo_de_no_saber.valor, costo_de_no_saber.moneda)}
          </p>
        </div>
      )}

      {resumen_colores && (
        <ul className="mt-8 flex flex-wrap gap-6">
          {ORDEN.map((estado) => (
            <li key={estado} className="flex items-center gap-2">
              <span className={`h-3 w-3 rounded-full ${COLOR[estado]}`} />
              <span className="tabular-nums font-medium">{resumen_colores[estado]}</span>
              <span className="text-stone-600">{rotulos[estado]}</span>
            </li>
          ))}
        </ul>
      )}

      {unidades && (
        <ul className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {[...unidades]
            .sort((a, b) => b.duda - a.duda)
            .map((u) => (
              <li key={u.id} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm ring-1 ring-stone-200">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${COLOR[u.estado]}`} />
                <span className="font-medium">{u.etiqueta}</span>
                <span className="ml-auto tabular-nums text-stone-500">{porcentaje(u.p)}</span>
              </li>
            ))}
        </ul>
      )}

      <p className="mt-8 text-sm text-stone-500">{analisis.origen_datos}</p>
    </section>
  )
}
