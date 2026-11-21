// Inicio tipo chat: se elige un modelo, se sube un archivo y se pregunta. No hay modelo de lenguaje:
// las preguntas son plantillas (preguntas.ts) y cada respuesta sale del JSON del motor.
// Por ahora el archivo propio solo se lee; la respuesta usa el archivo de ejemplo del caso y lo dice.

import { useEffect, useRef, useState, type ReactNode } from 'react'
import { api, despertarApi, type Origen } from './api'
import { leerCsv, type InfoCsv } from './csv'
import { useDiseno, type EstiloChat } from './disenos'
import { elegirCaso, interpretar, MOTOR_EN_PALABRAS, normalizar, preguntasDe, type Intencion, type Pregunta } from './preguntas'
import Respuesta from './Respuesta'
import RespuestaEnChat, { type DatosRespuesta } from './RespuestaEnChat'
import { lineaDelCaso } from './textos'
import type { Caso } from './tipos'

type Mensaje =
  | { id: number; de: 'krylov'; tipo: 'texto'; texto: string; nota?: string }
  | { id: number; de: 'tu'; tipo: 'texto'; texto: string }
  | { id: number; de: 'tu'; tipo: 'archivo'; info: InfoCsv }
  | { id: number; de: 'krylov'; tipo: 'respuesta'; datos: DatosRespuesta }

type NuevoMensaje = Mensaje extends infer M ? (M extends Mensaje ? Omit<M, 'id'> : never) : never

type Paso = 'motor' | 'archivo' | 'pregunta'

const SALUDO = 'Sé cuánto no sé, y te digo cuánto vale averiguarlo. ¿Con qué modelo trabajamos?'
const SIN_ARCHIVO_PROPIO = 'Todavía no analizo archivos propios: respondo con el archivo de ejemplo del caso.'

let siguienteId = 0

export default function Chat() {
  const estilo = useDiseno().chat
  const [casos, setCasos] = useState<Caso[]>([])
  const [mensajes, setMensajes] = useState<Mensaje[]>([{ id: siguienteId++, de: 'krylov', tipo: 'texto', texto: SALUDO }])
  const [paso, setPaso] = useState<Paso>('motor')
  const [caso, setCaso] = useState<Caso | null>(null)
  const [archivoPropio, setArchivoPropio] = useState(false)
  const [pensando, setPensando] = useState(false)
  const [texto, setTexto] = useState('')
  const [arrastrando, setArrastrando] = useState(false)
  const [completa, setCompleta] = useState<DatosRespuesta | null>(null)
  const [origen, setOrigen] = useState<Origen | null>(null)
  const final = useRef<HTMLDivElement>(null)
  const selectorArchivo = useRef<HTMLInputElement>(null)

  const decir = (...nuevos: NuevoMensaje[]) =>
    setMensajes((m) => [...m, ...nuevos.map((n) => ({ ...n, id: siguienteId++ }) as Mensaje)])

  useEffect(() => {
    despertarApi()
    api
      .casos()
      .then((r) => {
        setCasos(r.datos.casos)
        setOrigen(r.origen)
      })
      .catch((e: Error) => decir({ de: 'krylov', tipo: 'texto', texto: `No pude cargar los modelos: ${e.message}` }))
  }, [])

  useEffect(() => {
    final.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [mensajes, pensando])

  const preguntas: Pregunta[] = caso ? preguntasDe(caso) : []

  const elegir = (c: Caso) => {
    setCaso(c)
    setPaso('archivo')
    decir(
      { de: 'tu', tipo: 'texto', texto: `${c.titulo} (${lineaDelCaso(c)})` },
      {
        de: 'krylov',
        tipo: 'texto',
        texto: `Uso el modelo de ${MOTOR_EN_PALABRAS[c.motor]?.toLowerCase() ?? c.motor}. Sube tu archivo en CSV o usa el de ejemplo del caso.`,
        nota: c.origen_datos,
      },
    )
  }

  const subir = async (archivo: File | undefined) => {
    if (!archivo) return
    if (!caso) {
      decir({ de: 'krylov', tipo: 'texto', texto: 'Primero elige con qué modelo trabajamos.' })
      return
    }
    try {
      const info = await leerCsv(archivo)
      setArchivoPropio(true)
      setPaso('pregunta')
      decir(
        { de: 'tu', tipo: 'archivo', info },
        {
          de: 'krylov',
          tipo: 'texto',
          texto: `Leí ${info.nombre}: ${info.filas.toLocaleString('es-CL')} filas y ${info.columnas.length} columnas. ¿Qué quieres saber?`,
          nota: SIN_ARCHIVO_PROPIO,
        },
      )
    } catch (e) {
      decir({ de: 'krylov', tipo: 'texto', texto: `No pude leer el archivo: ${(e as Error).message}` })
    }
  }

  const usarEjemplo = () => {
    setArchivoPropio(false)
    setPaso('pregunta')
    decir(
      { de: 'tu', tipo: 'texto', texto: 'Usa el archivo de ejemplo.' },
      { de: 'krylov', tipo: 'texto', texto: 'Listo, uso el archivo de ejemplo del caso. ¿Qué quieres saber?' },
    )
  }

  const preguntar = async (intencion: Intencion, pregunta: string) => {
    if (!caso) return
    decir({ de: 'tu', tipo: 'texto', texto: pregunta })
    setPensando(true)
    try {
      const r = await api.analizar(caso.nombre)
      const analisis = r.datos
      const [nube, donde] = await Promise.all([
        analisis.semaforo.estado === 'rojo_modelo' ? api.nube(caso.nombre).then((n) => n.datos) : null,
        intencion === 'donde_medir' ? api.dondeMedir(caso.nombre).then((d) => d.datos) : null,
      ])
      setOrigen(r.origen)
      decir({ de: 'krylov', tipo: 'respuesta', datos: { intencion, analisis, nube, donde, archivoPropio } })
    } catch (e) {
      decir({ de: 'krylov', tipo: 'texto', texto: `No pude responder: ${(e as Error).message}` })
    } finally {
      setPensando(false)
    }
  }

  const enviar = () => {
    const escrito = texto.trim()
    if (!escrito || pensando) return
    setTexto('')
    if (paso === 'motor') {
      const c = elegirCaso(escrito, casos)
      if (c) elegir(c)
      else {
        decir({ de: 'tu', tipo: 'texto', texto: escrito }, { de: 'krylov', tipo: 'texto', texto: 'No reconocí el modelo. Elige uno de la lista o escribe su número.' })
      }
    } else if (paso === 'archivo') {
      if (/ejemplo|^(si|dale|ok|usa)/.test(normalizar(escrito).trim())) usarEjemplo()
      else {
        decir({ de: 'tu', tipo: 'texto', texto: escrito }, { de: 'krylov', tipo: 'texto', texto: 'Sube un CSV con el botón del clip, o escribe «ejemplo».' })
      }
    } else {
      const intencion = interpretar(escrito, preguntas)
      if (intencion) preguntar(intencion, escrito)
      else {
        decir({ de: 'tu', tipo: 'texto', texto: escrito }, { de: 'krylov', tipo: 'texto', texto: 'Con estos datos sé responder estas preguntas. Elige una o escribe su número.' })
      }
    }
  }

  const reiniciar = () => {
    setMensajes([{ id: siguienteId++, de: 'krylov', tipo: 'texto', texto: SALUDO }])
    setPaso('motor')
    setCaso(null)
    setArchivoPropio(false)
    setTexto('')
  }

  if (completa) {
    return (
      <div className="mx-auto flex min-h-dvh max-w-[90rem] flex-col px-4 py-5 sm:px-8 md:h-dvh md:min-h-0">
        <header className="mb-5 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
          <button onClick={() => setCompleta(null)} className="text-tinta-suave hover:text-tinta">
            ← Volver al chat
          </button>
          {caso && <p className="text-tinta-suave">{lineaDelCaso(caso)}</p>}
        </header>
        <main className="flex min-h-0 flex-1 flex-col pb-10 lg:pb-0">
          <Respuesta key={completa.analisis.caso} analisis={completa.analisis} nube={completa.nube} />
        </main>
      </div>
    )
  }

  const opciones: { clave: string; contenido: ReactNode; alElegir: () => void }[] =
    paso === 'motor'
      ? casos.map((c) => ({
          clave: c.nombre,
          contenido: <OpcionCaso caso={c} />,
          alElegir: () => elegir(c),
        }))
      : paso === 'archivo'
        ? [
            { clave: 'subir', contenido: 'Subir un CSV', alElegir: () => selectorArchivo.current?.click() },
            { clave: 'ejemplo', contenido: 'Usar el archivo de ejemplo', alElegir: usarEjemplo },
          ]
        : preguntas.map((p) => ({ clave: p.intencion, contenido: p.texto, alElegir: () => preguntar(p.intencion, p.texto) }))

  // Número de cada párrafo de Krylov (diseño «documento»).
  const numeros = mensajes.reduce<number[]>((acc, m) => [...acc, (acc.at(-1) ?? 0) + (m.de === 'krylov' ? 1 : 0)], [])
  return (
    <div
      className="mx-auto flex h-dvh max-w-3xl flex-col px-4 sm:px-6"
      onDragOver={(e) => {
        e.preventDefault()
        setArrastrando(true)
      }}
      onDragLeave={(e) => {
        if (e.currentTarget === e.target) setArrastrando(false)
      }}
      onDrop={(e) => {
        e.preventDefault()
        setArrastrando(false)
        subir(e.dataTransfer.files[0])
      }}
    >
      <header className="flex items-baseline justify-between gap-4 py-4">
        <button onClick={reiniciar} className="condensado text-2xl font-bold">
          Krylov
        </button>
        <nav className="flex gap-4 text-sm text-tinta-suave">
          <button onClick={reiniciar} className="hover:text-tinta">
            Empezar de nuevo
          </button>
          <a href={`/clasico${window.location.search}`} className="hover:text-tinta">
            Vista clásica
          </a>
        </nav>
      </header>

      <main className="desliza-lista min-h-0 flex-1 overflow-y-auto" aria-live="polite">
        <ol className={estilo === 'terminal' ? 'space-y-3 py-2' : 'space-y-6 py-4'}>
          {mensajes.map((m, i) => (
            <li key={m.id}>
              <Envoltura estilo={estilo} de={m.de} numero={numeros[i]} ancho={m.tipo === 'respuesta'}>
                <ContenidoMensaje mensaje={m} alAbrir={setCompleta} />
              </Envoltura>
            </li>
          ))}
          {pensando && (
            <li>
              <Envoltura estilo={estilo} de="krylov" numero={(numeros.at(-1) ?? 0) + 1} ancho={false}>
                <span className={`text-tinta-suave ${estilo === 'terminal' ? 'cursor' : ''}`}>
                  {estilo === 'terminal' ? 'calculando' : 'Calculando…'}
                </span>
              </Envoltura>
            </li>
          )}
        </ol>
        <div ref={final} />
      </main>

      <footer className="pt-2 pb-14 lg:pb-4">
        <Opciones estilo={estilo} opciones={opciones} grande={paso === 'motor'} />
        <Compositor
          estilo={estilo}
          texto={texto}
          alEscribir={setTexto}
          alEnviar={enviar}
          alAdjuntar={() => selectorArchivo.current?.click()}
          placeholder={
            paso === 'motor' ? 'Escribe el número o el nombre del modelo' : paso === 'archivo' ? 'Escribe «ejemplo» o sube un CSV' : 'Pregúntale algo a tus datos'
          }
        />
        <input
          ref={selectorArchivo}
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={(e) => {
            subir(e.target.files?.[0])
            e.target.value = ''
          }}
        />
        <p className="mt-2 text-xs text-tinta-suave/70">
          {origen === 'api' ? 'Respuesta de la API' : 'Modo estático'}. Ejemplo fijo: números inventados.
        </p>
      </footer>

      {arrastrando && (
        <div className="pointer-events-none fixed inset-0 z-40 flex items-center justify-center bg-fondo/80">
          <p className="rounded-(--radio) border-2 border-dashed border-acento px-8 py-6 text-xl">Suelta tu CSV aquí</p>
        </div>
      )}
    </div>
  )
}

function OpcionCaso({ caso }: { caso: Caso }) {
  return (
    <span className="block">
      <span className="block font-semibold">{caso.titulo}</span>
      <span className="block text-sm text-tinta-suave">
        {MOTOR_EN_PALABRAS[caso.motor] ?? caso.motor} · {lineaDelCaso(caso)}
      </span>
    </span>
  )
}

function ContenidoMensaje({ mensaje: m, alAbrir }: { mensaje: Mensaje; alAbrir: (d: DatosRespuesta) => void }) {
  if (m.tipo === 'respuesta') return <RespuestaEnChat datos={m.datos} alAbrir={() => alAbrir(m.datos)} />
  if (m.tipo === 'archivo') {
    const { nombre, filas, columnas } = m.info
    const vistas = columnas.slice(0, 6)
    return (
      <span className="block">
        <span className="block font-semibold">📎 {nombre}</span>
        <span className="block text-sm opacity-80">
          {filas.toLocaleString('es-CL')} filas · {vistas.join(', ')}
          {columnas.length > vistas.length && ` y ${columnas.length - vistas.length} más`}
        </span>
      </span>
    )
  }
  return (
    <span className="block">
      {m.texto}
      {m.de === 'krylov' && m.nota && <span className="mt-1 block text-sm text-tinta-suave">{m.nota}</span>}
    </span>
  )
}

// La forma de cada mensaje según el diseño: burbuja, párrafo numerado o línea de terminal.
function Envoltura({ estilo, de, numero, ancho, children }: { estilo: EstiloChat; de: 'krylov' | 'tu'; numero: number; ancho: boolean; children: ReactNode }) {
  if (estilo === 'terminal') {
    return (
      <div className="flex gap-3">
        <span className={`w-14 shrink-0 text-right ${de === 'krylov' ? 'text-acento' : 'text-tinta-suave'}`}>{de === 'krylov' ? 'krylov:' : '›'}</span>
        <div className={`min-w-0 flex-1 ${de === 'tu' ? 'text-tinta-suave' : ''}`}>{children}</div>
      </div>
    )
  }
  if (estilo === 'documento') {
    return de === 'krylov' ? (
      <section className="border-l-2 border-tinta pl-5">
        <p className="mb-1 text-xs tracking-[0.2em] text-tinta-suave uppercase">§ {numero} · Krylov</p>
        <div className="condensado text-lg leading-relaxed">{children}</div>
      </section>
    ) : (
      <div className="pl-5 text-tinta-suave italic">— {children}</div>
    )
  }
  return de === 'krylov' ? (
    <div className="flex gap-3">
      <span className="condensado flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-acento font-bold text-sobre-acento" aria-hidden>
        K
      </span>
      <div className={`min-w-0 rounded-(--radio) bg-superficie px-4 py-3 shadow-(--sombra) ${ancho ? 'flex-1' : 'max-w-[85%]'}`}>{children}</div>
    </div>
  ) : (
    <div className="flex justify-end">
      <div className="max-w-[80%] rounded-(--radio) bg-acento px-4 py-2.5 text-sobre-acento">{children}</div>
    </div>
  )
}

function Opciones({ estilo, opciones, grande }: { estilo: EstiloChat; opciones: { clave: string; contenido: ReactNode; alElegir: () => void }[]; grande: boolean }) {
  if (opciones.length === 0) return null
  if (estilo === 'terminal' || estilo === 'documento') {
    return (
      <ol className="mb-3 space-y-1">
        {opciones.map((o, i) => (
          <li key={o.clave}>
            <button onClick={o.alElegir} className="group flex gap-3 text-left">
              <span className="text-tinta-suave">{estilo === 'terminal' ? `[${i + 1}]` : `${i + 1}.`}</span>
              <span className={estilo === 'terminal' ? 'group-hover:text-acento' : 'underline decoration-linea underline-offset-4 group-hover:decoration-tinta'}>{o.contenido}</span>
            </button>
          </li>
        ))}
      </ol>
    )
  }
  return (
    <ul className={`mb-3 ${grande ? 'grid gap-2 sm:grid-cols-2' : 'flex flex-wrap gap-2'}`}>
      {opciones.map((o) => (
        <li key={o.clave}>
          <button
            onClick={o.alElegir}
            className={`border border-linea bg-superficie text-left shadow-(--sombra) hover:border-acento ${grande ? 'h-full w-full rounded-(--radio) px-4 py-3' : 'rounded-full px-3.5 py-1.5 text-sm'}`}
          >
            {o.contenido}
          </button>
        </li>
      ))}
    </ul>
  )
}

interface PropsCompositor {
  estilo: EstiloChat
  texto: string
  placeholder: string
  alEscribir: (t: string) => void
  alEnviar: () => void
  alAdjuntar: () => void
}

function Compositor({ estilo, texto, placeholder, alEscribir, alEnviar, alAdjuntar }: PropsCompositor) {
  const marco =
    estilo === 'terminal'
      ? 'border-t border-linea pt-2'
      : estilo === 'documento'
        ? 'border-t-2 border-tinta pt-2'
        : 'rounded-(--radio) border border-linea bg-superficie px-2 py-1.5 shadow-(--sombra) focus-within:border-acento'
  return (
    <form
      className={`compositor flex items-center gap-2 ${marco}`}
      onSubmit={(e) => {
        e.preventDefault()
        alEnviar()
      }}
    >
      <button type="button" onClick={alAdjuntar} title="Subir un CSV" aria-label="Subir un CSV" className="px-2 py-1 text-lg text-tinta-suave hover:text-tinta">
        {estilo === 'terminal' ? '+' : '📎'}
      </button>
      {estilo === 'terminal' && <span className="text-acento">›</span>}
      <input
        value={texto}
        onChange={(e) => alEscribir(e.target.value)}
        placeholder={placeholder}
        className={`min-w-0 flex-1 bg-transparent py-1.5 caret-acento outline-none placeholder:text-tinta-suave/70 ${estilo === 'documento' ? 'condensado italic' : ''}`}
      />
      <button type="submit" className={estilo === 'burbujas' ? 'rounded-(--radio) bg-acento px-4 py-1.5 font-semibold text-sobre-acento' : 'px-2 py-1 font-semibold text-acento'}>
        {estilo === 'terminal' ? '⏎' : 'Enviar'}
      </button>
    </form>
  )
}
