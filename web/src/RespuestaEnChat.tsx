// Una respuesta de Krylov dentro del chat: el titular y el panel que pidió la pregunta, con los
// mismos componentes de la vista 2. «Ver en pantalla completa» abre la vista 2 entera.

import { FONDO, ORDEN } from './colores'
import Deslizadores from './Deslizadores'
import Examen from './Examen'
import ListaUnidades from './ListaUnidades'
import Mapa from './Mapa'
import Nube from './Nube'
import NumeroGrande from './NumeroGrande'
import type { Intencion } from './preguntas'
import QuePesa from './QuePesa'
import { plata } from './titular'
import type { Analisis, DondeMedir, Nube as DatosNube } from './tipos'
import { useDecision } from './useDecision'

export interface DatosRespuesta {
  intencion: Intencion
  analisis: Analisis
  nube: DatosNube | null
  donde: DondeMedir | null
  archivoPropio: boolean
}

const UNIDADES_EN_CHAT = 12

export default function RespuestaEnChat({ datos, alAbrir }: { datos: DatosRespuesta; alAbrir: () => void }) {
  const { intencion, analisis, nube, donde, archivoPropio } = datos
  const d = useDecision(analisis)
  const { semaforo, rotulos, costo_de_no_saber, unidades, mapa, factores, examen } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'
  const moneda = costo_de_no_saber?.moneda ?? 'USD'

  // Las unidades de más riesgo, con su decisión, para la vista corta de la lista.
  const primeras =
    unidades && d.unidades
      ? unidades
          .map((u, i) => ({ u, decision: d.unidades![i] }))
          .sort((a, b) => b.u.p - a.u.p)
          .slice(0, UNIDADES_EN_CHAT)
      : null

  const numero = !rojo && costo_de_no_saber && d.total !== null && (
    <div>
      <p className="text-sm text-tinta-suave">{rotulos.costo_de_no_saber}</p>
      <NumeroGrande valor={d.total} moneda={moneda} />
    </div>
  )

  const colores = d.resumen && (
    <ul className="flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
      {ORDEN.map((estado) => (
        <li key={estado} className="flex items-center gap-2">
          <span className={`h-3.5 w-6 shrink-0 rounded-sm ${FONDO[estado]}`} />
          <span className="font-semibold">{d.resumen![estado]}</span>
          <span>{rotulos[estado]}</span>
        </li>
      ))}
    </ul>
  )

  const mapaChico = mapa && d.bloques && (
    <div className="flex h-80 flex-col">
      <Mapa mapa={mapa} bloques={d.bloques} />
    </div>
  )

  return (
    <div className="space-y-4">
      <p className="condensado text-2xl leading-tight font-bold text-balance">
        {d.titular}
        {analisis.precalculado && (
          <span className="ml-2 inline-block rounded-sm border border-tinta-suave px-1.5 py-0.5 align-middle text-xs font-normal text-tinta-suave">
            Precalculado
          </span>
        )}
      </p>

      {rojo ? (
        <>
          <div className="border-l-4 border-actuar bg-actuar/10 py-3 pr-4 pl-4">
            <p className="font-medium">{semaforo.motivo}</p>
            {semaforo.propuesta && <p className="mt-1 text-sm text-tinta-suave">{semaforo.propuesta.texto}</p>}
          </div>
          {nube && (
            <div className="flex h-96 flex-col">
              <Nube nube={nube} />
            </div>
          )}
        </>
      ) : (
        <>
          {intencion === 'decidir' && (
            <>
              {colores}
              {primeras && (
                <div className="flex max-h-96 flex-col">
                  <ListaUnidades unidades={primeras.map((f) => f.u)} decisiones={primeras.map((f) => f.decision)} corte={d.corte} />
                </div>
              )}
              {mapaChico}
            </>
          )}

          {intencion === 'costo' && (
            <>
              {numero}
              {colores}
              {costo_de_no_saber && (
                <Deslizadores falsoSi={analisis.costos.falso_si} falsoNo={analisis.costos.falso_no} costos={d.costos} moneda={moneda} alCambiar={d.setCostos} />
              )}
            </>
          )}

          {intencion === 'que_pesa' &&
            (factores ? (
              <QuePesa factores={factores} titulo={mapa ? 'Qué manda en el terreno' : 'Qué pesa'} flechas={!mapa} />
            ) : (
              <p>Este caso todavía no trae qué pesa.</p>
            ))}

          {intencion === 'examen' && (examen ? <Examen examen={examen} /> : <p>Este caso todavía no tiene examen.</p>)}

          {intencion === 'donde_medir' && (
            <>
              {mapaChico}
              {donde && (
                <ol className="space-y-1.5">
                  {donde.candidatas.map((c) => (
                    <li key={c.etiqueta} className="flex items-baseline gap-3">
                      <span className="condensado w-6 text-xl font-bold">{c.etiqueta}</span>
                      <span>
                        Medir aquí vale {plata(c.valor_de_medir, moneda)}; cuesta {plata(c.costo_medicion, moneda)}.
                      </span>
                    </li>
                  ))}
                </ol>
              )}
            </>
          )}
        </>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-linea pt-3">
        <p className="text-xs text-tinta-suave">
          {archivoPropio && 'Respondí con el archivo de ejemplo del caso, no con el tuyo. '}
          {analisis.precalculado ? 'Precalculado con el método lento de siempre.' : 'Respondió la red que practicó con casos simulados.'}
        </p>
        <button onClick={alAbrir} className="text-sm font-semibold text-acento hover:underline">
          Ver en pantalla completa →
        </button>
      </div>
    </div>
  )
}
