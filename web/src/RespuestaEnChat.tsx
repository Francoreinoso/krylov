// Una respuesta de Krylov dentro del chat: el titular, que aparece palabra por palabra, y el panel
// que pidió la pregunta, con los mismos componentes de la vista 2. Debajo, las acciones.

import { useEffect, useState, type ReactNode } from 'react'
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
const MS_POR_PALABRA = 35
const RECIENTE_MS = 1500

const quieto = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

// El texto aparece palabra por palabra solo la primera vez; si después cambia (los deslizadores
// rehacen el titular), se muestra entero.
function Aparece({ texto, animar }: { texto: string; animar: boolean }) {
  const palabras = texto.split(' ')
  const [n, setN] = useState(animar ? 0 : Infinity)
  useEffect(() => {
    if (n >= palabras.length) return
    const t = setTimeout(() => setN(n + 1), MS_POR_PALABRA)
    return () => clearTimeout(t)
  }, [n, palabras.length])
  return <>{n >= palabras.length ? texto : palabras.slice(0, n).join(' ')}</>
}

function Tarjeta({ children }: { children: ReactNode }) {
  return <div className="rounded-2xl border border-linea p-4 sm:p-5">{children}</div>
}

function BotonAccion({ titulo, alHacer, children }: { titulo: string; alHacer: () => void; children: ReactNode }) {
  return (
    <button onClick={alHacer} title={titulo} aria-label={titulo} className="flex h-8 items-center gap-1.5 rounded-lg px-2 text-sm text-tinta-suave hover:bg-superficie hover:text-tinta">
      {children}
    </button>
  )
}

interface Props {
  datos: DatosRespuesta
  creado: number
  alAbrir: () => void
}

export default function RespuestaEnChat({ datos, creado, alAbrir }: Props) {
  const { intencion, analisis, nube, donde, archivoPropio } = datos
  const d = useDecision(analisis)
  const [animar] = useState(() => Date.now() - creado < RECIENTE_MS && !quieto())
  const [copiado, setCopiado] = useState(false)
  const { semaforo, rotulos, costo_de_no_saber, unidades, mapa, factores, examen } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'
  const moneda = costo_de_no_saber?.moneda ?? 'USD'
  const retraso = animar ? d.titular.split(' ').length * MS_POR_PALABRA : 0

  // Las unidades de más riesgo, con su decisión, para la vista corta de la lista.
  const primeras =
    unidades && d.unidades
      ? unidades
          .map((u, i) => ({ u, decision: d.unidades![i] }))
          .sort((a, b) => b.u.p - a.u.p)
          .slice(0, UNIDADES_EN_CHAT)
      : null

  const copiar = () => {
    const lineas = [d.titular, ...(d.resumen ? ORDEN.map((e) => `${rotulos[e]}: ${d.resumen![e]}`) : [])]
    navigator.clipboard?.writeText(lineas.join('\n')).then(() => {
      setCopiado(true)
      setTimeout(() => setCopiado(false), 1500)
    })
  }

  const colores = d.resumen && (
    <ul className="flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
      {ORDEN.map((estado) => (
        <li key={estado} className="flex items-center gap-2">
          <span className={`h-3.5 w-6 shrink-0 rounded-sm ${FONDO[estado]}`} />
          <span className="font-semibold">{d.resumen![estado]}</span>
          <span className="text-tinta-suave">{rotulos[estado]}</span>
        </li>
      ))}
    </ul>
  )

  const mapaChico = mapa && d.bloques && (
    <Tarjeta>
      <div className="flex h-80 flex-col">
        <Mapa mapa={mapa} bloques={d.bloques} />
      </div>
    </Tarjeta>
  )

  return (
    <div>
      {archivoPropio && (
        <p className="mb-3 inline-block rounded-full bg-en-duda/15 px-3 py-1 text-xs">Respondí con el archivo de ejemplo del caso: todavía no analizo archivos propios.</p>
      )}

      <p className="condensado text-xl leading-snug font-semibold text-balance">
        <Aparece texto={d.titular} animar={animar} />
        {analisis.precalculado && (
          <span className="ml-2 inline-block rounded-full border border-linea px-2 py-0.5 align-middle text-xs font-normal text-tinta-suave">Precalculado</span>
        )}
      </p>

      <div className={`mt-4 space-y-4 ${animar ? 'aparecer' : ''}`} style={{ animationDelay: `${retraso}ms` }}>
        {rojo ? (
          <>
            <div className="rounded-2xl border border-actuar/40 bg-actuar/10 p-4">
              <p className="font-medium">{semaforo.motivo}</p>
              {semaforo.propuesta && <p className="mt-1 text-sm text-tinta-suave">{semaforo.propuesta.texto}</p>}
            </div>
            {nube && (
              <Tarjeta>
                <div className="flex h-96 flex-col">
                  <Nube nube={nube} />
                </div>
              </Tarjeta>
            )}
          </>
        ) : (
          <>
            {intencion === 'decidir' && (
              <>
                {colores}
                {primeras && (
                  <Tarjeta>
                    <div className="flex max-h-96 flex-col">
                      <ListaUnidades unidades={primeras.map((f) => f.u)} decisiones={primeras.map((f) => f.decision)} corte={d.corte} />
                    </div>
                  </Tarjeta>
                )}
                {mapaChico}
              </>
            )}

            {intencion === 'costo' && costo_de_no_saber && d.total !== null && (
              <Tarjeta>
                <p className="text-sm text-tinta-suave">{rotulos.costo_de_no_saber}</p>
                <NumeroGrande valor={d.total} moneda={moneda} />
                <div className="mt-4">{colores}</div>
                <div className="mt-5">
                  <Deslizadores falsoSi={analisis.costos.falso_si} falsoNo={analisis.costos.falso_no} costos={d.costos} moneda={moneda} alCambiar={d.setCostos} />
                </div>
              </Tarjeta>
            )}

            {intencion === 'que_pesa' &&
              (factores ? (
                <Tarjeta>
                  <QuePesa factores={factores} titulo={mapa ? 'Qué manda en el terreno' : 'Qué pesa'} flechas={!mapa} />
                </Tarjeta>
              ) : (
                <p>Este caso todavía no trae qué pesa.</p>
              ))}

            {intencion === 'examen' &&
              (examen ? (
                <Tarjeta>
                  <Examen examen={examen} />
                </Tarjeta>
              ) : (
                <p>Este caso todavía no tiene examen.</p>
              ))}

            {intencion === 'donde_medir' && (
              <>
                {mapaChico}
                {donde && (
                  <ol className="grid gap-2 sm:grid-cols-3">
                    {donde.candidatas.map((c) => (
                      <li key={c.etiqueta} className="rounded-2xl border border-linea p-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-acento text-sm font-bold text-sobre-acento">{c.etiqueta}</span>
                        <p className="mt-2 text-sm">Medir aquí vale {plata(c.valor_de_medir, moneda)}</p>
                        <p className="text-xs text-tinta-suave">Cuesta {plata(c.costo_medicion, moneda)}</p>
                      </li>
                    ))}
                  </ol>
                )}
              </>
            )}
          </>
        )}

        <div className="flex flex-wrap items-center gap-1">
          <BotonAccion titulo="Copiar" alHacer={copiar}>
            <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
              <rect x="7" y="7" width="9" height="9" rx="2" />
              <path d="M13 7V5.5A1.5 1.5 0 0 0 11.5 4h-6A1.5 1.5 0 0 0 4 5.5v6A1.5 1.5 0 0 0 5.5 13H7" />
            </svg>
            {copiado && <span>Copiado</span>}
          </BotonAccion>
          <BotonAccion titulo="Ver en pantalla completa" alHacer={alAbrir}>
            <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden>
              <path d="M12 4h4v4M8 16H4v-4M16 4l-5 5M4 16l5-5" />
            </svg>
            <span>Pantalla completa</span>
          </BotonAccion>
          <span className="ml-auto text-xs text-tinta-suave">
            {analisis.precalculado ? 'Precalculado con el método lento de siempre' : 'Respondió la red que practicó con casos simulados'}
          </span>
        </div>
      </div>
    </div>
  )
}
