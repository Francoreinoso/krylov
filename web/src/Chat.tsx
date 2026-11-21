// Inicio tipo chat. No hay modelo de lenguaje: las preguntas son plantillas (preguntas.ts) y cada
// respuesta sale del JSON del motor. Por ahora el archivo propio solo se lee; la respuesta usa el
// archivo de ejemplo del caso y lo dice.

import { useEffect, useRef, useState, type ReactNode } from 'react'
import { api, despertarApi, type Origen } from './api'
import CalceEnChat, { asignacionDe, mismaAsignacion, type Asignacion } from './CalceEnChat'
import Compositor from './Compositor'
import { leerCsv, type InfoCsv } from './csv'
import Lateral, { IconoLateral } from './Lateral'
import Marca from './Marca'
import { elegirCaso, interpretar, MOTOR_EN_PALABRAS, preguntasDe, type Intencion } from './preguntas'
import Respuesta from './Respuesta'
import RespuestaEnChat, { type DatosRespuesta } from './RespuestaEnChat'
import TarjetaArchivo from './TarjetaArchivo'
import { lineaDelCaso } from './textos'
import type { Calce, Caso, Papel } from './tipos'

type Contenido =
  | { de: 'tu'; texto: string; adjunto?: InfoCsv }
  | { de: 'krylov'; tipo: 'texto'; texto: string; nota?: string; accion?: 'modelos' | 'preguntas' }
  | { de: 'krylov'; tipo: 'respuesta'; datos: DatosRespuesta }
  | { de: 'krylov'; tipo: 'calce'; calce: Calce; papeles: Papel[]; intencion: Intencion; confirmado: boolean }

type Mensaje = Contenido & { id: number; creado: number }

interface Conversacion {
  id: number
  caso: Caso | null
  archivo: InfoCsv | null // el archivo propio que se subió en esta conversación
  pendiente: string | null // la pregunta que espera a que se elija un modelo
  calceListo: boolean // se confirmó qué columna cumple cada papel
  mensajes: Mensaje[]
}

const FRASE = 'Sé cuánto no sé, y te digo cuánto vale averiguarlo.'
const SIN_ARCHIVO_PROPIO = 'Todavía no analizo archivos propios: respondo con el archivo de ejemplo del caso.'
const OTRAS_COLUMNAS =
  'Con otras columnas tengo que analizar el archivo de nuevo en el servidor, y todavía no está en línea. Respondo con las columnas del caso.'
const ESCRITORIO = '(min-width: 1024px)'

let siguienteId = 0
const nueva = (caso: Caso | null = null): Conversacion => ({
  id: siguienteId++,
  caso,
  archivo: null,
  pendiente: null,
  calceListo: false,
  mensajes: [],
})

const tituloDe = (c: Conversacion) => {
  const primero = c.mensajes.find((m) => m.de === 'tu')
  return (primero?.de === 'tu' && (primero.texto || primero.adjunto?.nombre)) || c.caso?.titulo || 'Nuevo análisis'
}

export default function Chat() {
  const [casos, setCasos] = useState<Caso[]>([])
  const [estado, setEstado] = useState(() => {
    const c = nueva()
    return { conversaciones: [c], activa: c.id }
  })
  const [texto, setTexto] = useState('')
  const [adjunto, setAdjunto] = useState<InfoCsv | null>(null)
  const [pensando, setPensando] = useState<number | null>(null)
  const [arrastrando, setArrastrando] = useState(false)
  const [completa, setCompleta] = useState<DatosRespuesta | null>(null)
  const [origen, setOrigen] = useState<Origen | null>(null)
  const [lateral, setLateral] = useState(() => window.matchMedia(ESCRITORIO).matches)
  const ultimaPregunta = useRef<HTMLLIElement>(null)
  const selectorArchivo = useRef<HTMLInputElement>(null)

  const conv = estado.conversaciones.find((c) => c.id === estado.activa)!

  useEffect(() => {
    despertarApi()
    api
      .casos()
      .then((r) => {
        setCasos(r.datos.casos)
        setOrigen(r.origen)
      })
      .catch(() => setOrigen('estatico'))
  }, [])

  // Como en los chats conocidos: la última pregunta (o el calce recién confirmado) sube al borde de
  // arriba y la respuesta llega debajo.
  useEffect(() => {
    ultimaPregunta.current?.scrollIntoView({ block: 'start', behavior: 'smooth' })
  }, [conv.mensajes.length, conv.id])

  const cerrarLateralEnTelefono = () => {
    if (!window.matchMedia(ESCRITORIO).matches) setLateral(false)
  }

  const modificar = (id: number, cambio: (c: Conversacion) => Conversacion) =>
    setEstado((s) => ({ ...s, conversaciones: s.conversaciones.map((c) => (c.id === id ? cambio(c) : c)) }))

  const decir = (id: number, ...contenidos: Contenido[]) =>
    modificar(id, (c) => ({
      ...c,
      mensajes: [...c.mensajes, ...contenidos.map((m) => ({ ...m, id: siguienteId++, creado: Date.now() }))],
    }))

  // Abre una conversación vacía, o reusa la actual si todavía no tiene mensajes.
  const empezar = (caso: Caso | null = null) => {
    setEstado((s) => {
      const actual = s.conversaciones.find((c) => c.id === s.activa)
      if (actual && actual.mensajes.length === 0) {
        return { ...s, conversaciones: s.conversaciones.map((c) => (c.id === actual.id ? { ...c, caso, calceListo: false } : c)) }
      }
      const c = nueva(caso)
      return { conversaciones: [c, ...s.conversaciones], activa: c.id }
    })
    setTexto('')
    setAdjunto(null)
    cerrarLateralEnTelefono()
  }

  const responder = async (id: number, caso: Caso, intencion: Intencion, archivoPropio: boolean) => {
    setPensando(id)
    try {
      const r = await api.analizar(caso.nombre)
      const analisis = r.datos
      const [nube, donde] = await Promise.all([
        analisis.semaforo.estado === 'rojo_modelo' ? api.nube(caso.nombre).then((n) => n.datos) : null,
        intencion === 'donde_medir' ? api.dondeMedir(caso.nombre).then((d) => d.datos) : null,
      ])
      setOrigen(r.origen)
      decir(id, { de: 'krylov', tipo: 'respuesta', datos: { intencion, analisis, nube, donde, archivoPropio } })
    } catch (e) {
      decir(id, { de: 'krylov', tipo: 'texto', texto: `No pude responder: ${(e as Error).message}` })
    } finally {
      setPensando(null)
    }
  }

  // Antes de la primera respuesta, el chat muestra qué columna del archivo cumple cada papel.
  const mostrarCalce = async (id: number, caso: Caso, intencion: Intencion) => {
    setPensando(id)
    try {
      const [calce, papeles] = await Promise.all([api.calce(caso.nombre), api.papeles(caso.motor)])
      decir(id, {
        de: 'krylov',
        tipo: 'texto',
        texto: `Antes de analizar, revisa qué columna del archivo cumple cada papel del modelo de ${MOTOR_EN_PALABRAS[caso.motor]?.toLowerCase() ?? caso.motor}.`,
      })
      decir(id, { de: 'krylov', tipo: 'calce', calce: calce.datos, papeles: papeles.datos.papeles, intencion, confirmado: false })
    } catch {
      // Sin calce que mostrar, se analiza con las columnas del caso.
      modificar(id, (c) => ({ ...c, calceListo: true }))
      await responder(id, caso, intencion, false)
    } finally {
      setPensando((p) => (p === id ? null : p))
    }
  }

  const confirmarCalce = (id: number, mensaje: number, caso: Caso, calce: Calce, intencion: Intencion, asignacion: Asignacion) => {
    modificar(id, (c) => ({
      ...c,
      calceListo: true,
      mensajes: c.mensajes.map((m) => (m.id === mensaje && m.de === 'krylov' && m.tipo === 'calce' ? { ...m, confirmado: true } : m)),
    }))
    if (!mismaAsignacion(asignacion, asignacionDe(calce))) decir(id, { de: 'krylov', tipo: 'texto', texto: OTRAS_COLUMNAS })
    responder(id, caso, intencion, false)
  }

  // Qué hacer con una pregunta, una vez que hay modelo.
  const atender = (id: number, caso: Caso, pregunta: string, archivo: InfoCsv | null, recienElegido: boolean, calceListo: boolean) => {
    const intencion = interpretar(pregunta, preguntasDe(caso))
    if (intencion && !calceListo && archivo === null) {
      mostrarCalce(id, caso, intencion)
      return
    }
    if (intencion) {
      responder(id, caso, intencion, archivo !== null)
      return
    }
    decir(id, {
      de: 'krylov',
      tipo: 'texto',
      texto: recienElegido
        ? `Listo, trabajo con el modelo de ${MOTOR_EN_PALABRAS[caso.motor]?.toLowerCase() ?? caso.motor}. ¿Qué quieres saber?`
        : 'Con este modelo sé responder estas preguntas. Elige una o escribe su número.',
      nota: recienElegido ? caso.origen_datos : undefined,
      accion: 'preguntas',
    })
  }

  const enviar = (escrito = texto, casoElegido: Caso | null = null) => {
    const pregunta = escrito.trim()
    if ((!pregunta && !adjunto) || pensando !== null) return
    const id = conv.id
    const adj = adjunto
    const archivo = adj ?? conv.archivo
    const reconocido = conv.caso ? null : (casoElegido ?? (pregunta ? elegirCaso(pregunta, casos) : null))
    const caso = conv.caso ?? reconocido
    setTexto('')
    setAdjunto(null)
    modificar(id, (c) => ({ ...c, caso, archivo, pendiente: caso ? null : pregunta }))
    decir(id, { de: 'tu', texto: pregunta, adjunto: adj ?? undefined })

    if (!caso) {
      decir(id, { de: 'krylov', tipo: 'texto', texto: '¿Con qué modelo lo vemos?', accion: 'modelos' })
    } else if (!pregunta && adj) {
      decir(id, {
        de: 'krylov',
        tipo: 'texto',
        texto: `Leí ${adj.nombre}: ${adj.filas.toLocaleString('es-CL')} filas y ${adj.columnas.length} columnas. ¿Qué quieres saber?`,
        nota: SIN_ARCHIVO_PROPIO,
        accion: 'preguntas',
      })
    } else {
      atender(id, caso, pregunta, archivo, reconocido !== null && !casoElegido, conv.calceListo && conv.caso !== null)
    }
  }

  // Elegir un modelo desde las tarjetas que ofrece Krylov retoma la pregunta que quedó esperando.
  const elegirModelo = (caso: Caso) => {
    const { id, pendiente, archivo } = conv
    modificar(id, (c) => ({ ...c, caso, pendiente: null, calceListo: false }))
    decir(id, { de: 'tu', texto: caso.titulo })
    atender(id, caso, pendiente ?? '', archivo, true, false)
  }

  const adjuntar = async (archivo: File | undefined) => {
    if (!archivo) return
    try {
      setAdjunto(await leerCsv(archivo))
    } catch (e) {
      decir(conv.id, { de: 'krylov', tipo: 'texto', texto: `No pude leer el archivo: ${(e as Error).message}` })
    }
  }

  if (completa) {
    return (
      <div className="mx-auto flex min-h-dvh max-w-[90rem] flex-col px-4 py-5 sm:px-8 md:h-dvh md:min-h-0">
        <header className="mb-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-1">
          <button onClick={() => setCompleta(null)} className="rounded-full border border-linea px-4 py-1.5 text-sm hover:bg-superficie">
            ← Volver al chat
          </button>
          {conv.caso && <p className="text-tinta-suave">{lineaDelCaso(conv.caso)}</p>}
        </header>
        <main className="flex min-h-0 flex-1 flex-col pb-10 lg:pb-0">
          <Respuesta key={completa.analisis.caso} analisis={completa.analisis} nube={completa.nube} />
        </main>
      </div>
    )
  }

  const vacia = conv.mensajes.length === 0
  const ultimo = conv.mensajes.at(-1)
  const ultimaDelUsuario = conv.mensajes.findLast((m) => m.de === 'tu' || (m.de === 'krylov' && m.tipo === 'calce' && m.confirmado))
  const preguntas = conv.caso ? preguntasDe(conv.caso) : []
  const seguimiento =
    ultimo?.de === 'krylov' && pensando === null && (ultimo.tipo === 'respuesta' || (ultimo.tipo === 'texto' && ultimo.accion === 'preguntas'))
      ? preguntas.filter((p) => ultimo.tipo !== 'respuesta' || p.intencion !== ultimo.datos.intencion)
      : []
  const recientes = estado.conversaciones.filter((c) => c.mensajes.length > 0).map((c) => ({ id: c.id, titulo: tituloDe(c) }))

  const compositor = (
    <Compositor
      texto={texto}
      adjunto={adjunto}
      casos={casos}
      caso={conv.caso}
      ocupado={pensando !== null}
      placeholder={conv.caso ? 'Pregúntale algo a tus datos' : 'Elige un modelo o escribe qué quieres saber'}
      alEscribir={setTexto}
      alEnviar={() => enviar()}
      alAdjuntar={() => selectorArchivo.current?.click()}
      alQuitarAdjunto={() => setAdjunto(null)}
      alElegirCaso={(c) => modificar(conv.id, (x) => ({ ...x, caso: c, calceListo: false }))}
    />
  )

  const aviso = (
    <p className="mt-2.5 text-center text-xs text-tinta-suave" title={origen === 'api' ? 'Respuesta de la API' : 'Modo estático'}>
      Krylov practicó con casos simulados. Los costos son supuestos y los números, de ejemplo.
    </p>
  )

  return (
    <div
      className="flex h-dvh"
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
        adjuntar(e.dataTransfer.files[0])
      }}
    >
      {lateral && (
        <>
          <div className="fixed inset-0 z-30 bg-tinta/20 lg:hidden" onClick={() => setLateral(false)} />
          <div className="fixed inset-y-0 left-0 z-40 lg:static">
            <Lateral
              casos={casos}
              recientes={recientes}
              activa={conv.id}
              alNuevo={() => empezar()}
              alElegirModelo={(c) => empezar(c)}
              alAbrir={(id) => {
                setEstado((s) => ({ ...s, activa: id }))
                cerrarLateralEnTelefono()
              }}
              alCerrar={() => setLateral(false)}
            />
          </div>
        </>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-2 px-3">
          {!lateral && (
            <>
              <button onClick={() => setLateral(true)} title="Abrir la barra" aria-label="Abrir la barra" className="rounded-lg p-1.5 text-tinta-suave hover:bg-superficie hover:text-tinta">
                <IconoLateral />
              </button>
              <button onClick={() => empezar()} className="rounded-lg px-2 py-1 text-lg font-semibold hover:bg-superficie">
                Krylov
              </button>
            </>
          )}
          {!vacia && <p className="min-w-0 flex-1 truncate text-center text-sm text-tinta-suave">{tituloDe(conv)}</p>}
        </header>

        {vacia ? (
          <main className="flex min-h-0 flex-1 flex-col items-center overflow-y-auto px-4 pb-16">
            <div className="my-auto flex w-full max-w-3xl flex-col items-center py-6">
              <Marca grande />
              <h1 className="condensado texto-degradado mt-5 pb-1 text-center text-4xl font-semibold tracking-tight sm:text-5xl">¿Qué quieres saber?</h1>
              <p className="mt-2 text-center text-tinta-suave">
                {conv.caso ? `${MOTOR_EN_PALABRAS[conv.caso.motor] ?? conv.caso.motor} · ${lineaDelCaso(conv.caso)}` : FRASE}
              </p>
              <div className="mt-8 w-full">{compositor}</div>
              <div className="mt-5 w-full">
                {conv.caso ? (
                  <div className="flex flex-wrap justify-center gap-2">
                    {preguntas.map((p) => (
                      <Chip key={p.intencion} texto={p.texto} alElegir={() => enviar(p.texto)} />
                    ))}
                  </div>
                ) : (
                  <TarjetasModelo casos={casos} alElegir={(c) => enviar(c.titulo, c)} />
                )}
              </div>
              {aviso}
            </div>
          </main>
        ) : (
          <>
            <main className="desliza-lista min-h-0 flex-1 overflow-y-auto px-4" aria-live="polite">
              <ol className="mx-auto max-w-3xl space-y-8 py-6">
                {conv.mensajes.map((m) => (
                  <li key={m.id} ref={m === ultimaDelUsuario ? ultimaPregunta : undefined} className="scroll-mt-4">
                    {m.de === 'tu' ? (
                      <MensajeTu texto={m.texto} adjunto={m.adjunto} />
                    ) : (
                      <MensajeKrylov>
                        {m.tipo === 'respuesta' ? (
                          <RespuestaEnChat datos={m.datos} creado={m.creado} alAbrir={() => setCompleta(m.datos)} />
                        ) : m.tipo === 'calce' ? (
                          <CalceEnChat
                            calce={m.calce}
                            papeles={m.papeles}
                            confirmado={m.confirmado}
                            alConfirmar={(a) => conv.caso && confirmarCalce(conv.id, m.id, conv.caso, m.calce, m.intencion, a)}
                          />
                        ) : (
                          <>
                            <p className="leading-relaxed">{m.texto}</p>
                            {m.nota && <p className="mt-1 text-sm text-tinta-suave">{m.nota}</p>}
                            {m.accion === 'modelos' && (
                              <div className="mt-4">
                                <TarjetasModelo casos={casos} alElegir={elegirModelo} desactivadas={conv.caso !== null} />
                              </div>
                            )}
                          </>
                        )}
                        {m === ultimo && seguimiento.length > 0 && (
                          <div className="aparecer mt-5 flex flex-wrap gap-2">
                            {seguimiento.map((p) => (
                              <Chip key={p.intencion} texto={p.texto} alElegir={() => enviar(p.texto)} />
                            ))}
                          </div>
                        )}
                      </MensajeKrylov>
                    )}
                  </li>
                ))}
                {pensando === conv.id && (
                  <li>
                    <MensajeKrylov pensando>
                      <p className="brillo">Calculando con el modelo…</p>
                    </MensajeKrylov>
                  </li>
                )}
              </ol>
            </main>
            <footer className="relative shrink-0 px-4 pb-14 lg:pb-3">
              <div className="pointer-events-none absolute inset-x-0 -top-8 h-8 bg-linear-to-t from-fondo" />
              <div className="mx-auto max-w-3xl">
                {compositor}
                {aviso}
              </div>
            </footer>
          </>
        )}
      </div>

      <input
        ref={selectorArchivo}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={(e) => {
          adjuntar(e.target.files?.[0])
          e.target.value = ''
        }}
      />

      {arrastrando && (
        <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center bg-fondo/85 backdrop-blur-sm">
          <div className="rounded-3xl border-2 border-dashed border-acento px-10 py-8 text-center">
            <p className="text-xl font-semibold">Suelta tu CSV</p>
            <p className="mt-1 text-sm text-tinta-suave">Queda adjunto a tu próxima pregunta</p>
          </div>
        </div>
      )}
    </div>
  )
}

function MensajeTu({ texto, adjunto }: { texto: string; adjunto?: InfoCsv }) {
  return (
    <div className="flex flex-col items-end gap-2">
      {adjunto && <TarjetaArchivo info={adjunto} />}
      {texto && <p className="max-w-[80%] rounded-3xl bg-superficie px-5 py-2.5 leading-relaxed whitespace-pre-wrap">{texto}</p>}
    </div>
  )
}

function MensajeKrylov({ children, pensando = false }: { children: ReactNode; pensando?: boolean }) {
  return (
    <div className="flex gap-4">
      <span className={`mt-0.5 ${pensando ? 'animate-pulse' : ''}`}>
        <Marca />
      </span>
      <div className="min-w-0 flex-1 pt-0.5">{children}</div>
    </div>
  )
}

function Chip({ texto, alElegir }: { texto: string; alElegir: () => void }) {
  return (
    <button onClick={alElegir} className="rounded-full border border-linea px-4 py-2 text-sm hover:bg-superficie">
      {texto}
    </button>
  )
}

function TarjetasModelo({ casos, alElegir, desactivadas = false }: { casos: Caso[]; alElegir: (c: Caso) => void; desactivadas?: boolean }) {
  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {casos.map((c) => (
        <li key={c.nombre}>
          <button
            onClick={() => alElegir(c)}
            disabled={desactivadas}
            className="h-full w-full rounded-2xl border border-linea p-4 text-left transition-colors hover:bg-superficie disabled:opacity-50 disabled:hover:bg-transparent"
          >
            <span className="block font-medium">{c.titulo}</span>
            <span className="mt-1 block text-sm text-tinta-suave">{MOTOR_EN_PALABRAS[c.motor] ?? c.motor}</span>
            <span className="mt-2 block text-xs text-tinta-suave">{lineaDelCaso(c)}</span>
          </button>
        </li>
      ))}
    </ul>
  )
}
