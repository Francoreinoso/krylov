// Krylov, la app (D-42): la misma cosa que el deck. Una idea por pantalla:
//   inicio → (una decisión) → el archivo cae y se ordena → ¿qué columna es qué? → entra a la red → la respuesta,
//   en la escena de la lámina de esa decisión, con los datos del archivo.
// Las teclas del escenario: 1 a 5, cada decisión con los datos del demo; M, un archivo con el que Krylov no responde;
// D, «¿Dónde perforo?»; L, el cierre; F, pantalla completa; Esc, volver.

import { useEffect, useRef, useState } from 'react'
import { api, despertarApi, ErrorDelServidor, SinServidor, type ColumnasConfirmadas } from './api'
import { asignacionDe, type Asignacion } from './asignacion'
import Cierre from './Cierre'
import type { Fase, Orden } from './Coreografia'
import { leerCsv, type InfoCsv } from './csv'
import Encabezado from './Encabezado'
import Inicio from './Inicio'
import { ordenDeRespuesta, ordenDelArchivo } from './orden'
import type { Reloj } from './reloj'
import Resultado, { type Resuelta } from './Resultado'
import { ElegirDecision, PantallaDecision } from './Subir'
import type { Analisis, Calce, Caso, DondeMedir, Papel } from './tipos'
import Viaje from './Viaje'

// Un archivo de la app: lo que el navegador leyó y, si es uno de los de prueba, de qué caso es.
export type Archivo = InfoCsv & { prueba: string | null }

type Etapa =
  | { e: 'inicio' }
  | { e: 'decision'; caso: Caso }
  | { e: 'elegir'; archivo: Archivo }
  | { e: 'viaje'; caso: Caso; archivo: Archivo | null; calce: Calce | null; papeles: Papel[]; fase: Fase; n: number; orden: Orden; motivo: string | null }
  | { e: 'respuesta'; caso: Caso; r: Resuelta; id: number }

const SIN_SERVIDOR = 'Para leer un archivo propio, Krylov necesita su servidor, y ahora no responde. El archivo de ejemplo funciona sin servidor.'
const DEMO_MINIMO_MS = 1100 // con los datos guardados, la entrada a la red se alcanza a ver
const ENTRADA_MINIMA_MS = 900 // con un servidor rápido, igual: el cronómetro dice el tiempo real, la animación solo termina

const columnaDe = (a: Asignacion) => Object.fromEntries(Object.entries(a).map(([papel, cols]) => [papel, cols[0]]))
const espera = (ms: number) => new Promise((r) => setTimeout(r, ms))

export default function App() {
  const [casos, setCasos] = useState<Caso[]>([])
  const [etapa, setEtapa] = useState<Etapa>({ e: 'inicio' })
  const [cierre, setCierre] = useState(false)
  const [aviso, setAviso] = useState<string | null>(null)
  const [arrastrando, setArrastrando] = useState(false)
  const reloj = useRef<Reloj>({}) // para la lógica, sin esperar un render
  const [relojVisto, setRelojVisto] = useState<Reloj>({}) // el mismo, para dibujar
  const selector = useRef<HTMLInputElement>(null)
  const pendiente = useRef<Caso | null>(null) // la decisión a la que va el archivo que se está eligiendo
  const turno = useRef(0) // cada viaje nuevo deja sin efecto las respuestas del anterior

  useEffect(() => {
    api.casos().then((r) => {
      setCasos(r.datos.casos)
      // Desde el deck (tecla D): ?decision=<caso> abre esa decisión, con el archivo de prueba a un clic.
      const pedido = new URLSearchParams(window.location.search).get('decision')
      const caso = r.datos.casos.find((c) => c.nombre === pedido)
      if (caso) setEtapa({ e: 'decision', caso })
    }, () => setAviso('No pude cargar las decisiones. Recarga la página.'))
    despertarApi()
  }, [])

  // Anota un momento del cronómetro. `desdeCero`: empieza un viaje nuevo.
  const marcar = (cambio: Reloj, desdeCero = false) => {
    reloj.current = desdeCero ? cambio : { ...reloj.current, ...cambio }
    setRelojVisto(reloj.current)
  }

  const viaje = (cambio: Partial<Extract<Etapa, { e: 'viaje' }>>, mio: number) =>
    setEtapa((s) => (s.e === 'viaje' && turno.current === mio ? { ...s, ...cambio } : s))

  // La respuesta llegó: el núcleo se abre y aparece la escena. En rojo, los puntos se quedan en la puerta.
  const resolver = async (caso: Caso, analisis: Analisis, archivo: Archivo | null, origen: Resuelta['origen'], mio: number) => {
    if (reloj.current.respuesta === undefined) marcar({ respuesta: performance.now() }) // el demo la anota al llegar, antes de su espera mínima
    await espera(Math.max(0, ENTRADA_MINIMA_MS - ((reloj.current.respuesta ?? 0) - (reloj.current.confirmado ?? 0))))
    if (analisis.semaforo.estado.startsWith('rojo')) {
      viaje({ fase: 'rechazo', motivo: analisis.semaforo.motivo }, mio)
      return
    }
    const donde: DondeMedir | null = analisis.mapa && !archivo ? await api.dondeMedir(caso.nombre).then((d) => d.datos, () => null) : null
    viaje({ fase: 'sale' }, mio)
    await espera(650)
    if (turno.current !== mio) return
    setEtapa({ e: 'respuesta', id: mio, caso, r: { analisis, donde, archivo, origen, reloj: { ...reloj.current }, clave: archivo ? null : caso.nombre } })
  }

  // Un archivo para una decisión: cae, Krylov lee sus columnas y propone qué es cada una.
  const viajar = async (caso: Caso, archivo: Archivo) => {
    const mio = ++turno.current
    marcar({ soltado: performance.now() }, true)
    setEtapa({ e: 'viaje', caso, archivo, calce: null, papeles: [], fase: 'cae', n: archivo.muestra.length, orden: null, motivo: null })
    try {
      // El archivo de prueba trae las columnas que eligió el equipo (con su transformación, como hierro ÷ 120 en los
      // camiones). Uno propio, las que propone Krylov en vivo.
      const pedirCalce = () =>
        archivo.prueba === caso.nombre
          ? api.calceDePrueba(caso.nombre).catch(() => api.calcePropio(archivo.archivo, caso.motor, caso.nombre))
          : api.calcePropio(archivo.archivo, caso.motor, caso.nombre)
      const [calce, papeles] = await Promise.all([pedirCalce(), api.papeles(caso.motor).then((p) => p.datos.papeles)])
      marcar({ calce: performance.now() })
      viaje({ calce, papeles, fase: 'ordena', orden: ordenDelArchivo(archivo, columnaDe(asignacionDe(calce))) }, mio)
    } catch (e) {
      viaje({ fase: 'rechazo', motivo: e instanceof SinServidor ? SIN_SERVIDOR : `Krylov no pudo leer el archivo: ${(e as Error).message}` }, mio)
    }
  }

  const confirmar = async (caso: Caso, archivo: Archivo, calce: Calce, asignacion: Asignacion) => {
    const mio = turno.current
    marcar({ confirmado: performance.now() })
    viaje({ fase: 'entra', orden: ordenDelArchivo(archivo, columnaDe(asignacion)) }, mio)
    const columnas: ColumnasConfirmadas = Object.fromEntries(
      Object.entries(asignacion).map(([papel, cols]) => [papel, { columnas: cols, transformacion: calce.calce[papel]?.transformacion ?? null }]),
    )
    const comoPropuso = JSON.stringify(asignacion) === JSON.stringify(asignacionDe(calce))
    try {
      try {
        resolver(caso, await api.analizarArchivo(archivo.archivo, caso.motor, columnas), archivo, 'api', mio)
      } catch (e) {
        // sin servidor, el archivo de prueba con sus columnas de siempre tiene su respuesta guardada
        if (archivo.prueba !== caso.nombre || !comoPropuso || e instanceof ErrorDelServidor) throw e
        resolver(caso, await api.analisisDePrueba(caso.nombre), archivo, 'guardada', mio)
      }
    } catch (e) {
      viaje({ fase: 'rechazo', motivo: e instanceof SinServidor ? SIN_SERVIDOR : (e as Error).message }, mio)
    }
  }

  // Los datos del demo de una decisión: el archivo entra a la red y sale la respuesta guardada.
  const demo = async (caso: Caso) => {
    const mio = ++turno.current
    setCierre(false)
    const ahora = performance.now()
    marcar({ soltado: ahora, confirmado: ahora }, true)
    try {
      const r = await api.analizar(caso.nombre)
      marcar({ respuesta: performance.now() })
      const { n, orden } = ordenDeRespuesta(r.datos)
      setEtapa({ e: 'viaje', caso, archivo: null, calce: null, papeles: [], fase: 'entra', n, orden, motivo: null })
      await espera(DEMO_MINIMO_MS)
      if (turno.current === mio) resolver(caso, r.datos, null, r.origen === 'api' ? 'api' : 'guardada', mio)
    } catch (e) {
      setAviso(`No pude abrir los datos del demo: ${(e as Error).message}`)
    }
  }

  const soltar = async (archivo: File | undefined, caso: Caso | null, prueba: string | null = null) => {
    if (!archivo) return
    setAviso(null)
    try {
      const info: Archivo = { ...(await leerCsv(archivo)), prueba }
      if (caso) viajar(caso, info)
      else setEtapa({ e: 'elegir', archivo: info })
    } catch (e) {
      setAviso(`Krylov no pudo leer ${archivo.name}: ${(e as Error).message}`)
    }
  }

  const probar = async (caso: Caso) => {
    try {
      soltar(await api.archivoDePrueba(caso.nombre), caso, caso.nombre)
    } catch (e) {
      setAviso(`No encontré el archivo de ejemplo: ${(e as Error).message}`)
    }
  }

  const elegirArchivo = (caso: Caso | null) => {
    pendiente.current = caso
    selector.current?.click()
  }

  const casoActual = etapa.e === 'decision' || etapa.e === 'viaje' || etapa.e === 'respuesta' ? etapa.caso : null

  // Las teclas del escenario. Las que se apretaron con el foco en la escena también llegan aquí (LaminaDeck).
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if ((e.target instanceof HTMLElement && e.target.closest('input, textarea, select')) || e.metaKey || e.ctrlKey || e.altKey) return
      const k = e.key.toLowerCase()
      if (k === 'escape') {
        if (cierre) setCierre(false)
        else {
          ++turno.current
          setEtapa({ e: 'inicio' })
        }
      } else if (k === 'l') setCierre((c) => !c)
      else if (k === 'f') {
        if (document.fullscreenElement) document.exitFullscreen().catch(() => {})
        else document.documentElement.requestFullscreen().catch(() => {})
      } else if (k === 'm') {
        const base = casos.find((c) => c.motor === 'espacial')
        if (base) demo({ ...base, nombre: 'leyes_pocos' })
      } else if (/^[1-9]$/.test(k)) {
        const caso = casos[Number(k) - 1]
        if (caso) demo(caso)
      }
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  })

  const pantalla = (() => {
    switch (etapa.e) {
      case 'inicio':
        return <Inicio casos={casos} alElegirArchivo={() => elegirArchivo(null)} alProbar={() => casos[0] && probar(casos[0])} alElegir={(caso) => setEtapa({ e: 'decision', caso })} />
      case 'decision':
        return <PantallaDecision caso={etapa.caso} alElegirArchivo={() => elegirArchivo(etapa.caso)} alProbar={() => probar(etapa.caso)} alVerDemo={() => demo(etapa.caso)} />
      case 'elegir':
        return <ElegirDecision archivo={etapa.archivo} casos={casos} alElegir={(caso) => viajar(caso, etapa.archivo)} />
      case 'viaje':
        return (
          <Viaje
            {...etapa}
            reloj={relojVisto}
            alConfirmar={(a) => etapa.archivo && etapa.calce && confirmar(etapa.caso, etapa.archivo, etapa.calce, a)}
            alProbar={() => probar(etapa.caso)}
            alOtroArchivo={() => elegirArchivo(etapa.caso)}
          />
        )
      case 'respuesta':
        return <Resultado key={etapa.id} caso={etapa.caso} r={etapa.r} alOtroArchivo={() => elegirArchivo(etapa.caso)} />
    }
  })()

  return (
    <div
      className="flex min-h-dvh flex-col"
      onDragOver={(e) => {
        e.preventDefault()
        setArrastrando(true)
      }}
      onDragLeave={(e) => {
        if (e.relatedTarget === null) setArrastrando(false)
      }}
      onDrop={(e) => {
        e.preventDefault()
        setArrastrando(false)
        soltar(e.dataTransfer.files[0], casoActual)
      }}
    >
      <Encabezado caso={etapa.e === 'inicio' ? null : casoActual} alInicio={() => (++turno.current, setEtapa({ e: 'inicio' }))} />
      {aviso && (
        <p role="alert" className="mx-auto mt-4 w-full max-w-3xl border-l-4 border-actuar bg-superficie px-5 py-3">
          {aviso}
        </p>
      )}
      {pantalla}

      <input
        ref={selector}
        type="file"
        accept=".csv,.txt,text/csv"
        className="hidden"
        onChange={(e) => {
          soltar(e.target.files?.[0], pendiente.current)
          e.target.value = ''
        }}
      />

      {arrastrando && (
        <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center bg-fondo/85">
          <div className="border-2 border-dashed border-cobre px-14 py-10 text-center">
            <p className="titular text-6xl">Suéltalo aquí</p>
            <p className="mt-3 text-lg text-tinta-suave">{casoActual ? casoActual.titulo : 'Después eliges qué decisión es.'}</p>
          </div>
        </div>
      )}

      {cierre && <Cierre alCerrar={() => setCierre(false)} />}
    </div>
  )
}

