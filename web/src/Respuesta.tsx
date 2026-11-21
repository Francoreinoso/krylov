// Vista 2 · la respuesta de un caso: titular, lo que cuesta no saber, las unidades en tres
// colores, qué pesa y el pie.

import { FONDO, ORDEN } from './colores'
import ListaUnidades from './ListaUnidades'
import Pie from './Pie'
import QuePesa from './QuePesa'
import type { Analisis } from './tipos'

const plata = (valor: number, moneda: string) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: moneda, maximumFractionDigits: 0 }).format(valor)

export default function Respuesta({ analisis }: { analisis: Analisis }) {
  const { semaforo, rotulos, costo_de_no_saber, resumen_colores, unidades, factores } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'

  return (
    <section>
      {analisis.precalculado && (
        <p className="mb-3 inline-block rounded-sm bg-tinta px-2 py-0.5 text-sm text-papel">Precalculado</p>
      )}
      <h1 className="condensado max-w-[30ch] text-4xl leading-[1.05] font-bold text-balance sm:text-5xl">{analisis.titular}</h1>

      {rojo && (
        <div className="mt-8 max-w-[60ch] border-l-4 border-red-700 bg-red-50 py-4 pr-4 pl-5 text-red-950">
          <p className="font-medium">{semaforo.motivo}</p>
          {semaforo.propuesta && <p className="mt-2">{semaforo.propuesta.texto}</p>}
        </div>
      )}

      {costo_de_no_saber && resumen_colores && (
        <div className="mt-8 flex flex-wrap items-end justify-between gap-x-12 gap-y-6">
          <div>
            <p className="text-tinta-suave">{rotulos.costo_de_no_saber}</p>
            <p className="condensado text-6xl leading-none font-extrabold sm:text-[6rem]">
              {plata(costo_de_no_saber.valor, costo_de_no_saber.moneda)}
            </p>
          </div>
          <ul className="space-y-2 text-lg">
            {ORDEN.map((estado) => (
              <li key={estado} className="flex items-center gap-3">
                <span className={`h-4 w-7 rounded-sm ${FONDO[estado]}`} />
                <span className="w-10 text-right font-semibold">{resumen_colores[estado]}</span>
                <span>{rotulos[estado]}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {(unidades || factores) && (
        <div className="mt-10 grid gap-12 md:grid-cols-[1fr_18rem]">
          {unidades && <ListaUnidades unidades={unidades} puntoDeCorte={analisis.punto_de_corte} />}
          {factores && <QuePesa factores={factores} />}
        </div>
      )}

      <Pie analisis={analisis} />
    </section>
  )
}
