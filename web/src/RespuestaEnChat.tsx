// Una respuesta de Krylov, con la composición de la lámina 4 del deck: a la izquierda lo que cuesta
// no saber en grande, los tres colores con sus conteos y los costos; a la derecha el mapa del banco
// o la lista de unidades con la curva de la elegida. La primera respuesta de una conversación trae
// todo; las siguientes, el panel que pidió la pregunta. En «¿Dónde perforo?» el mapa trae sus tres
// pines; un clic simula la muestra y la respuesta siguiente muestra el mapa rehecho.

import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { FONDO, ORDEN } from './colores'
import { CurvaDeUnidad, useUnidadElegida, type TextosCurva } from './Curva'
import Deslizadores from './Deslizadores'
import Examen from './Examen'
import Interpretacion from './Interpretacion'
import ListaUnidades from './ListaUnidades'
import Mapa from './Mapa'
import Nube from './Nube'
import NumeroGrande from './NumeroGrande'
import type { Intencion } from './preguntas'
import QuePesa from './QuePesa'
import { quienRespondio, rotuloQuien } from './textos'
import { plata } from './titular'
import type { Analisis, Candidata, DondeMedir, MedicionNueva, Nube as DatosNube } from './tipos'
import { useDecision, type Recalculo } from './useDecision'

export interface Perforacion {
  candidata: Candidata
  valor: number
}

export interface DatosRespuesta {
  intencion: Intencion
  analisis: Analisis
  nube: DatosNube | null
  donde: DondeMedir | null
  clave: string | null // la del archivo del demo; null en un archivo propio
  completa: boolean // la primera respuesta de la conversación: todos los paneles
  nuevas: MedicionNueva[] // las muestras simuladas que ya entraron a este análisis
  perforacion: Perforacion | null // la muestra que se acaba de simular
  antes: number | null // lo que costaba no saber antes de esa muestra
  textos: TextosCurva | null // los rótulos de la curva (casos/textos.yaml)
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

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`panel p-4 sm:p-5 ${className}`}>{children}</div>
}

function BotonAccion({ titulo, alHacer, children }: { titulo: string; alHacer: () => void; children: ReactNode }) {
  return (
    <button onClick={alHacer} title={titulo} aria-label={titulo} className="flex h-8 items-center gap-1.5 px-2 text-sm text-tinta-suave hover:bg-superficie hover:text-tinta">
      {children}
    </button>
  )
}

// Los tres colores con su conteo grande, como la leyenda de la lámina 4.
function Leyenda({ analisis, d, grande }: { analisis: Analisis; d: Recalculo; grande: boolean }) {
  if (!d.resumen) return null
  return (
    <ul className="space-y-2.5">
      {ORDEN.map((estado) => (
        <li key={estado} className="grid grid-cols-[1.75rem_1fr_auto] items-center gap-3">
          <span className={`h-4 w-7 ${FONDO[estado]}`} />
          <span className={`leading-tight ${grande ? 'text-lg' : ''}`}>{analisis.rotulos[estado]}</span>
          <span className={`titular text-right ${grande ? 'text-5xl' : 'text-4xl'}`}>{d.resumen![estado]}</span>
        </li>
      ))}
    </ul>
  )
}

// Lo que cuesta no saber: el número de cobre. Después de una muestra, cuánto bajó.
function Costo({ analisis, d, antes, grande }: { analisis: Analisis; d: Recalculo; antes: number | null; grande: boolean }) {
  if (!analisis.costo_de_no_saber || d.total === null) return null
  const moneda = analisis.costo_de_no_saber.moneda
  const bajo = antes !== null ? antes - d.total : null
  return (
    <div>
      <p className={grande ? 'text-lg' : ''}>{bajo !== null ? 'El mapa se rehízo. Lo que cuesta no saber' : analisis.rotulos.costo_de_no_saber}</p>
      <NumeroGrande valor={d.total} moneda={moneda} tope={grande ? 6 : 4.25} />
      {bajo !== null ? (
        <p className="mt-1 text-no-actuar">
          {bajo >= 0 ? 'Bajó' : 'Subió'} <span className="titular text-2xl">{plata(Math.abs(bajo), moneda)}</span> con una sola muestra.
        </p>
      ) : (
        <p className="dato mt-1">Con los costos que tú pones</p>
      )}
    </div>
  )
}

// «Perforas en A: 375 ppm», con la escala de lo que podía salir y el límite (lámina 5).
function Perforado({ p, umbral, unidad }: { p: Perforacion; umbral: number; unidad: string }) {
  const r = p.candidata.resultados_posibles
  const valores = r ? [r.bajo, r.medio, r.alto, umbral] : [p.valor, umbral]
  const min = Math.min(...valores) * 0.8
  const max = Math.max(...valores) * 1.08
  const x = (v: number) => `${((v - min) / (max - min)) * 100}%`
  const n = (v: number) => Math.round(v).toLocaleString('es-CL')
  return (
    <div>
      <p className="titular text-4xl">
        Perforas en {p.candidata.etiqueta}: <span className="text-oro">{n(p.valor)} {unidad.split(' ')[0]}</span>
      </p>
      {r && (
        <div className="relative mt-4 mb-7 h-12 border-b border-tinta-suave/60">
          {(['bajo', 'medio', 'alto'] as const).map((k) => (
            <span key={k} className="absolute bottom-1 -translate-x-1/2 text-center" style={{ left: x(r[k]) }}>
              <span className={`dato block ${k === 'medio' ? 'text-oro' : ''}`}>{k}</span>
              <span className={`titular block text-2xl ${k === 'medio' ? 'text-oro' : 'text-tinta-suave'}`}>{n(r[k])}</span>
            </span>
          ))}
          <span className="absolute -bottom-1.5 h-3 w-px bg-actuar" style={{ left: x(umbral) }} />
          <span className="dato absolute top-full mt-1.5 -translate-x-1/2 whitespace-nowrap text-actuar" style={{ left: x(umbral) }}>
            Límite {n(umbral)} {unidad}
          </span>
        </div>
      )}
    </div>
  )
}

// Los tres lugares donde una muestra más vale más plata, cada uno con su botón.
function Candidatas({ donde, moneda, alPerforar, ocupado, hechas, columna = false }: { donde: DondeMedir; moneda: string; alPerforar?: (c: Candidata) => void; ocupado: boolean; hechas: Set<string>; columna?: boolean }) {
  return (
    <div>
      {donde.analisis_rehechos && (
        <p className="dato mb-2">
          Para elegirlos, Krylov rehízo el análisis completo {donde.analisis_rehechos.toLocaleString('es-CL')} veces
          {donde.precalculado
            ? ' · precalculado'
            : donde.tiempo_ms
              ? ` en ${(donde.tiempo_ms / 1000).toLocaleString('es-CL', { maximumFractionDigits: 1 })} s`
              : ''}
        </p>
      )}
      <ol className={`grid gap-2 ${columna ? '' : 'sm:grid-cols-3'}`}>
        {donde.candidatas.map((c) => (
          <li key={c.etiqueta} className="panel flex flex-col p-3">
            <span className="flex items-baseline gap-3">
              <span className="titular text-3xl text-oro">{c.etiqueta}</span>
              <span className="text-sm">Una muestra aquí vale {plata(c.valor_de_medir, moneda)}</span>
            </span>
            <span className="dato mt-1">Cuesta {plata(c.costo_medicion, moneda)}</span>
            {alPerforar && (
              <button
                onClick={() => alPerforar(c)}
                disabled={ocupado || hechas.has(c.etiqueta)}
                className="mt-3 border border-oro/60 px-3 py-1.5 text-sm text-oro hover:bg-oro hover:text-fondo disabled:border-linea disabled:text-tenue disabled:hover:bg-transparent"
              >
                {hechas.has(c.etiqueta) ? `Ya perforaste en ${c.etiqueta}` : `Perforar en ${c.etiqueta}`}
              </button>
            )}
          </li>
        ))}
      </ol>
    </div>
  )
}

interface Cuerpo {
  datos: DatosRespuesta
  d: Recalculo
  grande?: boolean
  alPerforar?: (c: Candidata) => void
  ocupado?: boolean
}

// Los paneles de una respuesta. `grande` es para la mesa y la lámina.
export function CuerpoRespuesta({ datos, d, grande = false, alPerforar, ocupado = false }: Cuerpo) {
  const { intencion, analisis, nube, donde, completa, nuevas, perforacion, antes, textos } = datos
  const { semaforo, costo_de_no_saber, unidades, mapa, factores, examen } = analisis
  const rojo = semaforo.estado === 'rojo_datos' || semaforo.estado === 'rojo_modelo'
  const moneda = costo_de_no_saber?.moneda ?? 'USD'
  const hechas = useMemo(() => new Set(nuevas.map((n) => n.etiqueta)), [nuevas])

  const [elegida, setElegida] = useUnidadElegida(unidades)
  const unidadElegida = unidades?.find((u) => u.id === elegida) ?? null
  const decisionElegida = unidades && d.unidades && unidadElegida ? d.unidades[unidades.indexOf(unidadElegida)] : null

  if (rojo) {
    return (
      <div className="space-y-4">
        <div className="border-l-4 border-actuar bg-actuar/10 px-5 py-4">
          <p className="dato text-actuar">Krylov no responde con este archivo</p>
          <p className="titular mt-1 text-3xl">{semaforo.motivo}</p>
          {semaforo.propuesta && <p className="mt-2 text-tinta-suave">{semaforo.propuesta.texto}</p>}
        </div>
        {nube && (
          <Panel>
            <div className="flex h-96 flex-col">
              <Nube nube={nube} />
            </div>
          </Panel>
        )}
      </div>
    )
  }

  const pinesActivos = intencion === 'donde_medir' && donde ? donde.candidatas : null
  const elMapa = mapa && d.bloques && (
    <div className={`${grande ? 'h-[min(36rem,72vh)]' : 'h-[min(80vw,30rem)]'}`}>
      <Mapa mapa={mapa} bloques={d.bloques} candidatas={pinesActivos} nuevas={nuevas} alPerforar={alPerforar} ocupado={ocupado} />
    </div>
  )

  const laCurva = unidadElegida?.curva && (
    <CurvaDeUnidad
      unidad={unidadElegida}
      estado={decisionElegida?.estado ?? null}
      rotulo={decisionElegida ? analisis.rotulos[decisionElegida.estado] : null}
      textos={textos}
      escalones={analisis.motor_id === 'sismico'} // temblores acumulados: lo sabe el motor, no el componente
    />
  )

  const laLista = (filas: number | null) => {
    if (!unidades || !d.unidades) return null
    const pares = unidades.map((u, i) => ({ u, decision: d.unidades![i] }))
    const vista = filas ? [...pares].sort((a, b) => b.u.p - a.u.p).slice(0, filas) : pares
    // La unidad de la curva siempre está en la lista: si quedó fuera, toma la última fila.
    const laElegida = pares.find((f) => f.u.id === elegida)
    if (filas && laElegida && !vista.includes(laElegida)) vista[vista.length - 1] = laElegida
    return (
      <div className={`flex flex-col ${filas ? 'max-h-96' : grande ? 'h-[22rem]' : 'h-72'}`}>
        <ListaUnidades unidades={vista.map((f) => f.u)} decisiones={vista.map((f) => f.decision)} corte={d.corte} elegida={elegida} alElegir={setElegida} />
      </div>
    )
  }

  const deslizadores = costo_de_no_saber && (
    <Deslizadores falsoSi={analisis.costos.falso_si} falsoNo={analisis.costos.falso_no} costos={d.costos} moneda={moneda} alCambiar={d.setCostos} />
  )
  const quePesa = factores && (
    <Panel>
      <QuePesa factores={factores} titulo="Qué pesa" flechas={!mapa} />
    </Panel>
  )
  const elExamen = examen && (
    <Panel>
      <Examen examen={examen} />
    </Panel>
  )
  const candidatas = (columna = false) =>
    pinesActivos && donde && <Candidatas donde={donde} moneda={moneda} alPerforar={alPerforar} ocupado={ocupado} hechas={hechas} columna={columna} />

  // En grande y sin mapa (los casos de lista), la curva necesita todo el ancho: arriba los números,
  // abajo la curva y la lista lado a lado.
  if ((completa || perforacion) && grande && !mapa) {
    return (
      <div className="space-y-8">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Leyenda analisis={analisis} d={d} grande />
          <div className="space-y-5">
            <Costo analisis={analisis} d={d} antes={null} grande />
            {deslizadores}
          </div>
        </div>
        {laCurva ? (
          <div className="grid gap-8 2xl:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
            <div className="min-w-0">{laCurva}</div>
            <div className="min-w-0">{laLista(null)}</div>
          </div>
        ) : (
          laLista(null)
        )}
        {(quePesa || elExamen) && (
          <div className={`grid gap-4 ${quePesa && elExamen ? 'sm:grid-cols-2' : ''}`}>
            {quePesa}
            {elExamen}
          </div>
        )}
      </div>
    )
  }

  // Todo a la vez, como la lámina 4.
  if (completa || perforacion) {
    return (
      <div className="space-y-5">
        <div className={`grid gap-6 ${grande ? 'lg:grid-cols-[minmax(20rem,26rem)_minmax(0,1fr)]' : 'md:grid-cols-[minmax(16rem,20rem)_minmax(0,1fr)]'}`}>
          <div className="space-y-6">
            {perforacion && mapa && <Perforado p={perforacion} umbral={mapa.umbral} unidad={mapa.unidad_valor} />}
            {!perforacion && <Leyenda analisis={analisis} d={d} grande={grande} />}
            <Costo analisis={analisis} d={d} antes={perforacion ? antes : null} grande={grande} />
            {!perforacion && deslizadores}
          </div>
          <div className="min-w-0 space-y-4">
            {elMapa}
            {laCurva}
            {laLista(null)}
          </div>
        </div>
        {candidatas()}
        {!perforacion && (quePesa || elExamen) && (
          <div className={`grid gap-4 ${quePesa && elExamen ? 'sm:grid-cols-2' : ''}`}>
            {quePesa}
            {elExamen}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {intencion === 'decidir' && (
        <>
          <Leyenda analisis={analisis} d={d} grande={grande} />
          {elMapa}
          {laCurva}
          {laLista(mapa ? null : UNIDADES_EN_CHAT)}
        </>
      )}
      {intencion === 'costo' && (
        <div className="grid gap-6 md:grid-cols-2">
          <Costo analisis={analisis} d={d} antes={null} grande={grande} />
          <div className="space-y-5">
            <Leyenda analisis={analisis} d={d} grande={false} />
            {deslizadores}
          </div>
        </div>
      )}
      {intencion === 'que_pesa' && (quePesa || <p>Este caso todavía no trae qué pesa.</p>)}
      {intencion === 'examen' && (elExamen || <p>Este caso todavía no tiene examen.</p>)}
      {intencion === 'donde_medir' && (
        // Como la lámina 5: lo que cuesta una muestra y los tres pines a la izquierda, el mapa a la derecha.
        <div className={`grid gap-6 ${grande ? 'lg:grid-cols-[minmax(18rem,24rem)_minmax(0,1fr)]' : 'md:grid-cols-[minmax(15rem,18rem)_minmax(0,1fr)]'}`}>
          <div className="space-y-4">
            {donde?.candidatas[0] && (
              <p className="titular text-3xl">
                Una muestra más cuesta {plata(donde.candidatas[0].costo_medicion, moneda)}.{' '}
                {analisis.rotulos.donde_medir && <span className="text-oro">{analisis.rotulos.donde_medir}</span>}
              </p>
            )}
            {candidatas(true)}
          </div>
          <div className="min-w-0">{elMapa}</div>
        </div>
      )}
    </div>
  )
}

// El titular, que aparece palabra por palabra la primera vez.
export function Titular({ texto, animar, grande = false, precalculado = false }: { texto: string; animar: boolean; grande?: boolean; precalculado?: boolean }) {
  return (
    <p className={`titular ${grande ? 'text-4xl sm:text-5xl lg:text-6xl' : 'text-3xl sm:text-4xl'}`}>
      <Aparece texto={texto} animar={animar} />
      {precalculado && <span className="dato ml-3 align-middle text-oro">Precalculado</span>}
    </p>
  )
}

interface Props {
  datos: DatosRespuesta
  creado: number
  alAbrir: () => void
  alPerforar?: (c: Candidata) => void
  ocupado?: boolean
  grande?: boolean
  soloTitular?: boolean // en la mesa, los paneles van al lienzo de la derecha
}

export default function RespuestaEnChat({ datos, creado, alAbrir, alPerforar, ocupado = false, grande = false, soloTitular = false }: Props) {
  const { analisis, clave } = datos
  const d = useDecision(analisis)
  const [animar] = useState(() => Date.now() - creado < RECIENTE_MS && !quieto())
  const [copiado, setCopiado] = useState(false)
  const retraso = animar ? d.titular.split(' ').length * MS_POR_PALABRA : 0
  const quien = rotuloQuien(analisis)

  const copiar = () => {
    const lineas = [d.titular, ...(d.resumen ? ORDEN.map((e) => `${analisis.rotulos[e]}: ${d.resumen![e]}`) : [])]
    navigator.clipboard?.writeText(lineas.join('\n')).then(() => {
      setCopiado(true)
      setTimeout(() => setCopiado(false), 1500)
    })
  }

  return (
    <div>
      {clave === null && <p className="dato mb-3 text-cobre">Tu archivo · columnas confirmadas por ti</p>}

      <Titular texto={soloTitular ? analisis.titular : d.titular} animar={animar} grande={grande} precalculado={analisis.precalculado} />

      <div className={`mt-5 space-y-5 ${animar ? 'aparecer' : ''}`} style={{ animationDelay: `${retraso}ms` }}>
        {!soloTitular && <CuerpoRespuesta datos={datos} d={d} grande={grande} alPerforar={alPerforar} ocupado={ocupado} />}

        {!soloTitular && <Interpretacion analisis={analisis} clave={clave} d={d} />}

        <div className="flex flex-wrap items-center gap-x-1 gap-y-2 border-t border-linea pt-2">
          {!soloTitular && (
            <>
              <BotonAccion titulo="Copiar" alHacer={copiar}>
                <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
                  <rect x="7" y="7" width="9" height="9" rx="1" />
                  <path d="M13 7V5.5A1.5 1.5 0 0 0 11.5 4h-6A1.5 1.5 0 0 0 4 5.5v6A1.5 1.5 0 0 0 5.5 13H7" />
                </svg>
                {copiado && <span>Copiado</span>}
              </BotonAccion>
              <BotonAccion titulo="Ver en pantalla completa" alHacer={alAbrir}>
                <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="square" aria-hidden>
                  <path d="M12 4h4v4M8 16H4v-4M16 4l-5 5M4 16l5-5" />
                </svg>
                <span>Pantalla completa</span>
              </BotonAccion>
            </>
          )}
          <span className="ml-auto flex flex-wrap items-center justify-end gap-x-3 gap-y-1 text-right" title={quienRespondio(analisis)}>
            <span className={`dato ${quien.clase}`}>{quien.texto}</span>
            {analisis.tiempo_ms > 0 && !analisis._aviso && !analisis.semaforo.estado.startsWith('rojo') && (
              <span className="dato">En {(analisis.tiempo_ms / 1000).toLocaleString('es-CL', { maximumFractionDigits: 2 })} s</span>
            )}
          </span>
        </div>
        {analisis.sintetico && !soloTitular && <p className="dato -mt-3">{analisis.origen_datos}</p>}
      </div>
    </div>
  )
}
