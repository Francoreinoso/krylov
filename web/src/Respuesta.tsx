// Vista 2 · la respuesta de un caso, en una sola pantalla de proyector:
// izquierda, lo que cuesta no saber, los tres colores y los costos; centro, las unidades (lista o
// mapa) o la nube si el archivo no se parece a nada conocido; derecha, qué pesa y el examen.

import { FONDO, ORDEN } from './colores'
import Deslizadores from './Deslizadores'
import Examen from './Examen'
import ListaUnidades from './ListaUnidades'
import Mapa from './Mapa'
import Nube from './Nube'
import NumeroGrande from './NumeroGrande'
import Pie from './Pie'
import QuePesa from './QuePesa'
import type { Analisis, Nube as DatosNube } from './tipos'
import { useDecision } from './useDecision'

interface Props {
  analisis: Analisis
  nube: DatosNube | null
}

export default function Respuesta({ analisis, nube }: Props) {
  const d = useDecision(analisis)
  const { semaforo, rotulos, costo_de_no_saber, unidades, mapa, factores, examen } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'

  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <h1 className="condensado max-w-[40ch] text-4xl leading-[1.05] font-bold text-balance 2xl:text-5xl">
        {d.titular}
        {analisis.precalculado && (
          <span className="ml-3 inline-block translate-y-[-0.3em] rounded-sm border border-tinta-suave px-2 py-0.5 align-middle text-sm font-normal text-tinta-suave [font-stretch:100%]">
            Precalculado
          </span>
        )}
      </h1>

      <div className="mt-6 grid min-h-0 flex-1 gap-x-10 gap-y-10 md:grid-cols-[17rem_1fr] xl:grid-cols-[19rem_1fr_16rem]">
        {/* Izquierda */}
        <div className="desliza-lista flex flex-col gap-5 md:min-h-0 md:overflow-y-auto">
          {rojo ? (
            <div className="border-l-4 border-actuar bg-actuar/10 py-4 pr-4 pl-5">
              <p className="font-medium">{semaforo.motivo}</p>
              {semaforo.propuesta && <p className="mt-2 text-tinta-suave">{semaforo.propuesta.texto}</p>}
            </div>
          ) : (
            costo_de_no_saber &&
            d.total !== null && (
              <div>
                <p className="text-tinta-suave">{rotulos.costo_de_no_saber}</p>
                <NumeroGrande valor={d.total} moneda={costo_de_no_saber.moneda} />
              </div>
            )
          )}

          {d.resumen && (
            <ul className="space-y-1.5">
              {ORDEN.map((estado) => (
                <li key={estado} className="flex items-center gap-3">
                  <span className={`h-4 w-7 shrink-0 rounded-sm transition-colors duration-150 ${FONDO[estado]}`} />
                  <span className="w-10 text-right font-semibold">{d.resumen![estado]}</span>
                  <span>{rotulos[estado]}</span>
                </li>
              ))}
            </ul>
          )}

          {!rojo && costo_de_no_saber && (
            <Deslizadores
              falsoSi={analisis.costos.falso_si}
              falsoNo={analisis.costos.falso_no}
              costos={d.costos}
              moneda={costo_de_no_saber.moneda}
              alCambiar={d.setCostos}
            />
          )}
        </div>

        {/* Centro */}
        <div className={`flex min-h-[22rem] flex-col md:min-h-0 ${semaforo.estado === 'rojo_modelo' ? 'xl:col-span-2' : ''}`}>
          {semaforo.estado === 'rojo_modelo' && nube ? (
            <Nube nube={nube} />
          ) : unidades && d.unidades ? (
            <ListaUnidades unidades={unidades} decisiones={d.unidades} corte={d.corte} />
          ) : (
            mapa && d.bloques && <Mapa mapa={mapa} bloques={d.bloques} />
          )}
        </div>

        {/* Derecha */}
        {(factores || examen) && (
          <div className="desliza-lista flex flex-col gap-8 md:col-span-2 md:grid md:grid-cols-2 xl:col-span-1 xl:flex xl:min-h-0 xl:overflow-y-auto">
            {factores && <QuePesa factores={factores} titulo={mapa ? 'Qué manda en el terreno' : 'Qué pesa'} flechas={!mapa} />}
            {examen && <Examen examen={examen} />}
          </div>
        )}
      </div>

      <Pie analisis={analisis} />
    </section>
  )
}
