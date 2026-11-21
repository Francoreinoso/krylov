// Inicio tipo chat (D-34) con la cara del deck. Las preguntas son plantillas (preguntas.ts) y cada
// respuesta sale del JSON del motor. Antes de la primera respuesta se confirma el calce de columnas
// (D-35): el del equipo en un archivo del demo; en un archivo propio, el que propone el servidor.
// Un archivo propio exige el servidor: sin él, el chat lo dice.
//
// Cuatro disposiciones para comparar (disenos.ts): Carta (una columna), Mesa (chat y lienzo),
// Lámina (cada respuesta como una lámina) y Óxido (las cinco decisiones siempre a la vista).

import { useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from 'react'
import { api, clave as claveEstatica, despertarApi, ErrorDelServidor, SinServidor, type ColumnasConfirmadas, type Origen } from './api'
import CalceEnChat, { asignacionDe, mismaAsignacion, type Asignacion } from './CalceEnChat'
import Cierre from './Cierre'
import Compositor from './Compositor'
import { leerCsv, type InfoCsv } from './csv'
import Decisiones, { type Quien } from './Decisiones'
import { useDiseno } from './disenos'
import Lateral, { IconoLateral } from './Lateral'
import Marca, { Logotipo } from './Marca'
import Mesa from './Mesa'
import Particulas from './Particulas'
import { elegirCaso, interpretar, MOTOR_EN_PALABRAS, preguntasDe, type Intencion } from './preguntas'
import Respuesta from './Respuesta'
import RespuestaEnChat, { type DatosRespuesta } from './RespuestaEnChat'
import SelectorDiseno from './SelectorDiseno'
import TarjetaArchivo from './TarjetaArchivo'
import { lineaDelCaso, rotuloQuien } from './textos'
import type { Calce, Candidata, Caso, MedicionNueva, Papel, Textos } from './tipos'
import Topografia from './Topografia'

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
  columnas: ColumnasConfirmadas | null // el calce confirmado del archivo propio
  mensajes: Mensaje[]
}

type Nueva = Omit<DatosRespuesta, 'completa' | 'nuevas' | 'perforacion' | 'antes' | 'textos'> & Partial<Pick<DatosRespuesta, 'nuevas' | 'perforacion' | 'antes'>>

const FRASE = 'Modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide.'
const SIN_SERVIDOR =
  'Para analizar un archivo propio necesito el servidor, y no responde ahora. Puedo responder con el archivo del demo: quita el adjunto y pregunta de nuevo.'
const OTRAS_COLUMNAS =
  'En el archivo del demo respondo con las columnas que eligió el equipo. Para probar otras, súbelo como archivo propio.'
const ESCRITORIO = '(min-width: 1024px)'
// Tecla M: archivos con los que Krylov no responde y dice por qué, cada uno con la tarjeta de su motor.
// Se recorren en orden; el que no está exportado (su caso o su motor todavía no existe) se salta.
const ARCHIVOS_QUE_NO_ALCANZAN = [
  { nombre: 'leyes_pocos', base: 'leyes' }, // el mismo banco con 12 pozos
  { nombre: 'taludes_corto', base: 'taludes' }, // una serie demasiado corta
]

// Escritorio o teléfono, al día con el tamaño de la ventana.
const consulta = window.matchMedia(ESCRITORIO)
const useEscritorio = () =>
  useSyncExternalStore(
    (avisar) => {
      consulta.addEventListener('change', avisar)
      return () => consulta.removeEventListener('change', avisar)
    },
    () => consulta.matches,
  )

let siguienteId = 0
const nueva = (caso: Caso | null = null): Conversacion => ({
  id: siguienteId++,
  caso,
  archivo: null,
  pendiente: null,
  calceListo: false,
  columnas: null,
  mensajes: [],
})

const tituloDe = (c: Conversacion) => {
  const primero = c.mensajes.find((m) => m.de === 'tu')
  return (primero?.de === 'tu' && (primero.texto || primero.adjunto?.nombre)) || c.caso?.titulo || 'Nuevo análisis'
}

export default function Chat() {
  const { id: disposicion } = useDiseno()
  const enEscritorio = useEscritorio()
  // En Óxido la barra queda siempre a la vista en escritorio; en los demás se abre con su botón.
  const fijaYVisible = disposicion === 'oxido' && enEscritorio
  const [casos, setCasos] = useState<Caso[]>([])
  const [quien, setQuien] = useState<Record<string, Quien>>({})
  const [rotulosMedir, setRotulosMedir] = useState<Record<string, string>>({}) // «¿Dónde perforo?» de cada caso
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
  const [abierta, setLateral] = useState(false)
  const [enPanel, setEnPanel] = useState<number | null>(null) // Mesa: la respuesta que muestra el lienzo
  const [cierre, setCierre] = useState(false) // tecla L: la lámina de cierre con el QR
  const textos = useRef<Textos | null>(null) // los rótulos de la curva; sin ellos, la curva va sin rótulos
  const [textosChat, setTextosChat] = useState<NonNullable<Textos['chat']>>({}) // sin ellos, no hay botón de prueba
  const ultimaPregunta = useRef<HTMLLIElement>(null)
  const selectorArchivo = useRef<HTMLInputElement>(null)

  const conv = estado.conversaciones.find((c) => c.id === estado.activa)!
  const lateral = abierta || fijaYVisible
  const escritorio = () => window.matchMedia(ESCRITORIO).matches

  useEffect(() => {
    despertarApi()
    api
      .textos()
      .then((r) => {
        textos.current = r.datos
        setTextosChat(r.datos.chat ?? {})
      })
      .catch(() => {})
    api
      .casos()
      .then((r) => {
        setCasos(r.datos.casos)
        setOrigen(r.origen)
        // Quién responde cada tarjeta hoy: red, precalculado o ejemplo.
        for (const c of r.datos.casos) {
          api
            .analizar(c.nombre)
            .then((a) => {
              setQuien((q) => ({ ...q, [c.nombre]: rotuloQuien(a.datos) }))
              const medir = a.datos.rotulos.donde_medir
              if (medir) setRotulosMedir((m) => ({ ...m, [c.nombre]: medir }))
            })
            .catch(() => {})
        }
      })
      .catch(() => setOrigen('estatico'))
  }, [])

  // Como en los chats conocidos: la última pregunta sube al borde de arriba y la respuesta llega debajo.
  useEffect(() => {
    ultimaPregunta.current?.scrollIntoView({ block: 'start', behavior: 'smooth' })
  }, [conv.mensajes.length, conv.id])

  const cerrarLateralEnTelefono = () => {
    if (!escritorio()) setLateral(false)
  }

  const modificar = (id: number, cambio: (c: Conversacion) => Conversacion) =>
    setEstado((s) => ({ ...s, conversaciones: s.conversaciones.map((c) => (c.id === id ? cambio(c) : c)) }))

  const decir = (id: number, ...contenidos: Contenido[]) =>
    modificar(id, (c) => ({
      ...c,
      mensajes: [...c.mensajes, ...contenidos.map((m) => ({ ...m, id: siguienteId++, creado: Date.now() }))],
    }))

  // La primera respuesta de una conversación trae todos los paneles; las siguientes, el que se pidió.
  const decirRespuesta = (id: number, datos: Nueva) => {
    const mensaje = siguienteId++
    modificar(id, (c) => {
      const completa = !c.mensajes.some((m) => m.de === 'krylov' && m.tipo === 'respuesta')
      const todo: DatosRespuesta = { nuevas: [], perforacion: null, antes: null, ...datos, completa, textos: textos.current?.curva ?? null }
      return { ...c, mensajes: [...c.mensajes, { de: 'krylov', tipo: 'respuesta', datos: todo, id: mensaje, creado: Date.now() }] }
    })
    setEnPanel(mensaje)
  }

  // Abre una conversación vacía, o reusa la actual si todavía no tiene mensajes.
  const empezar = (caso: Caso | null = null) => {
    setEstado((s) => {
      const actual = s.conversaciones.find((c) => c.id === s.activa)
      if (actual && actual.mensajes.length === 0) {
        return { ...s, conversaciones: s.conversaciones.map((c) => (c.id === actual.id ? { ...c, caso, calceListo: false, columnas: null } : c)) }
      }
      const c = nueva(caso)
      return { conversaciones: [c, ...s.conversaciones], activa: c.id }
    })
    setTexto('')
    setAdjunto(null)
    setEnPanel(null)
    cerrarLateralEnTelefono()
  }

  // `propio` es el archivo subido con su calce confirmado; sin él responde el archivo del demo.
  const responder = async (id: number, caso: Caso, intencion: Intencion, propio: { archivo: InfoCsv; columnas: ColumnasConfirmadas } | null) => {
    setPensando(id)
    try {
      if (propio) {
        const analisis = await api.analizarArchivo(propio.archivo.archivo, caso.motor, propio.columnas)
        setOrigen('api')
        decirRespuesta(id, { intencion, analisis, nube: null, donde: null, clave: null })
        return
      }
      // «¿Dónde perforo?» se pide a la par del análisis; la nube depende de él (solo en rojo_modelo).
      const [r, pedidoDonde] = await Promise.all([
        api.analizar(caso.nombre),
        intencion === 'donde_medir' ? api.dondeMedir(caso.nombre).then((d) => d.datos) : null,
      ])
      const analisis = r.datos
      const nube = analisis.semaforo.estado === 'rojo_modelo' ? (await api.nube(caso.nombre)).datos : null
      const donde = analisis.mapa ? pedidoDonde : null
      setOrigen(r.origen)
      decirRespuesta(id, { intencion, analisis, nube, donde, clave: caso.nombre })
    } catch (e) {
      // Una decisión cuya red todavía no responde archivos propios no es un error: se dice con su frase.
      const texto =
        e instanceof SinServidor
          ? SIN_SERVIDOR
          : e instanceof ErrorDelServidor && e.codigo === 'no_disponible'
            ? (textosChat.no_disponible ?? e.message)
            : `No pude responder: ${(e as Error).message}`
      decir(id, { de: 'krylov', tipo: 'texto', texto })
    } finally {
      setPensando(null)
    }
  }

  // «¿Dónde perforo?»: simula una sola muestra en el pin elegido (su resultado medio) sobre el
  // análisis original y lo rehace. Así A, B y C se comparan en cualquier orden, con o sin servidor.
  const perforar = async (desde: DatosRespuesta, c: Candidata) => {
    const caso = conv.caso
    const valor = c.resultados_posibles?.medio
    if (!caso || valor === undefined || pensando !== null) return
    const id = conv.id
    const medicion: MedicionNueva = { x: c.x, y: c.y, valor, etiqueta: c.etiqueta }
    const nuevas = [medicion]
    decir(id, { de: 'tu', texto: `Perforar en ${c.etiqueta}` })
    setPensando(id)
    try {
      const r = await api.analizar(caso.nombre, [], nuevas)
      setOrigen(r.origen)
      decirRespuesta(id, {
        intencion: 'donde_medir',
        analisis: r.datos,
        nube: null,
        donde: desde.donde,
        clave: claveEstatica(caso.nombre, [], nuevas),
        nuevas,
        perforacion: { candidata: c, valor },
        antes: desde.antes ?? desde.analisis.costo_de_no_saber?.valor ?? null, // antes de cualquier muestra
      })
    } catch (e) {
      decir(id, { de: 'krylov', tipo: 'texto', texto: `No pude simular esa muestra: ${(e as Error).message}` })
    } finally {
      setPensando(null)
    }
  }

  // Antes de la primera respuesta, el chat muestra qué columna del archivo cumple cada papel.
  const mostrarCalce = async (id: number, caso: Caso, intencion: Intencion, archivo: InfoCsv | null) => {
    setPensando(id)
    const modelo = MOTOR_EN_PALABRAS[caso.motor]?.toLowerCase() ?? caso.motor
    try {
      const [calce, papeles] = await Promise.all([
        archivo ? api.calcePropio(archivo.archivo, caso.motor, caso.nombre) : api.calce(caso.nombre).then((c) => c.datos),
        api.papeles(caso.motor),
      ])
      decir(id, {
        de: 'krylov',
        tipo: 'texto',
        texto: archivo
          ? `Leí las columnas de ${archivo.nombre}. Esta es mi propuesta de qué columna cumple cada papel del modelo («${modelo}»): revísala antes de analizar.`
          : `Antes de analizar, revisa qué columna del archivo cumple cada papel del modelo («${modelo}»).`,
      })
      decir(id, { de: 'krylov', tipo: 'calce', calce, papeles: papeles.datos.papeles, intencion, confirmado: false })
    } catch (e) {
      if (archivo) {
        decir(id, { de: 'krylov', tipo: 'texto', texto: e instanceof SinServidor ? SIN_SERVIDOR : `No pude leer tu archivo: ${(e as Error).message}` })
        return
      }
      // Sin calce que mostrar, se analiza con las columnas del caso.
      modificar(id, (c) => ({ ...c, calceListo: true }))
      await responder(id, caso, intencion, null)
    } finally {
      setPensando((p) => (p === id ? null : p))
    }
  }

  const confirmarCalce = (id: number, mensaje: number, caso: Caso, calce: Calce, intencion: Intencion, asignacion: Asignacion) => {
    const propio = calce.origen !== 'equipo' && conv.archivo !== null
    const columnas: ColumnasConfirmadas | null = propio
      ? Object.fromEntries(
          Object.entries(asignacion).map(([papel, cols]) => [papel, { columnas: cols, transformacion: calce.calce[papel]?.transformacion ?? null }]),
        )
      : null
    modificar(id, (c) => ({
      ...c,
      calceListo: true,
      columnas,
      mensajes: c.mensajes.map((m) => (m.id === mensaje && m.de === 'krylov' && m.tipo === 'calce' ? { ...m, confirmado: true } : m)),
    }))
    if (!propio && !mismaAsignacion(asignacion, asignacionDe(calce))) decir(id, { de: 'krylov', tipo: 'texto', texto: OTRAS_COLUMNAS })
    responder(id, caso, intencion, columnas && conv.archivo ? { archivo: conv.archivo, columnas } : null)
  }

  // El rótulo de medir del caso («¿Dónde perforo?»): el de la última respuesta o, antes de la
  // primera, el del análisis que se pidió al cargar.
  const rotuloMedir = (c: Conversacion) => {
    const r = c.mensajes.findLast((m) => m.de === 'krylov' && m.tipo === 'respuesta')
    const deRespuesta = r?.de === 'krylov' && r.tipo === 'respuesta' ? r.datos.analisis.rotulos.donde_medir : undefined
    return deRespuesta ?? (c.caso ? rotulosMedir[c.caso.nombre] : undefined)
  }

  // Qué hacer con una pregunta, una vez que hay modelo.
  const atender = (
    id: number,
    caso: Caso,
    pregunta: string,
    archivo: InfoCsv | null,
    recienElegido: boolean,
    calceListo: boolean,
    columnas: ColumnasConfirmadas | null,
  ) => {
    // Con el rótulo de medir del caso: sin él, «¿Dónde perforo?» no se reconoce.
    const intencion = interpretar(pregunta, preguntasDe(caso, rotulosMedir[caso.nombre] ?? rotuloMedir(conv)))
    if (intencion && !calceListo) {
      mostrarCalce(id, caso, intencion, archivo)
      return
    }
    if (intencion) {
      responder(id, caso, intencion, archivo && columnas ? { archivo, columnas } : null)
      return
    }
    decir(id, {
      de: 'krylov',
      tipo: 'texto',
      texto: recienElegido
        ? `Listo, trabajo con la decisión «${caso.titulo}». ¿Qué quieres saber?`
        : 'Con esta decisión sé responder estas preguntas. Elige una o escribe su número.',
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
    // Un archivo nuevo pide confirmar de nuevo su calce.
    modificar(id, (c) => ({ ...c, caso, archivo, pendiente: caso ? null : pregunta, ...(adj ? { calceListo: false, columnas: null } : {}) }))
    decir(id, { de: 'tu', texto: pregunta, adjunto: adj ?? undefined })

    if (!caso) {
      decir(id, { de: 'krylov', tipo: 'texto', texto: '¿Qué decisión es?', accion: 'modelos' })
    } else if (!pregunta && adj) {
      decir(id, {
        de: 'krylov',
        tipo: 'texto',
        texto: `Leí ${adj.nombre}: ${adj.filas.toLocaleString('es-CL')} filas y ${adj.columnas.length} columnas. ¿Qué quieres saber?`,
        accion: 'preguntas',
      })
    } else {
      atender(id, caso, pregunta, archivo, reconocido !== null && !casoElegido, conv.calceListo && conv.caso !== null && !adj, adj ? null : conv.columnas)
    }
  }

  // Elegir una decisión desde las tarjetas que ofrece Krylov retoma la pregunta que quedó esperando.
  const elegirModelo = (caso: Caso) => {
    const { id, pendiente, archivo } = conv
    modificar(id, (c) => ({ ...c, caso, pendiente: null, calceListo: false, columnas: null }))
    decir(id, { de: 'tu', texto: caso.titulo })
    atender(id, caso, pendiente ?? '', archivo, true, false, null)
  }

  // Tecla M: un archivo que no alcanza. Krylov no responde y dice por qué. Otra M, desde esa
  // conversación, abre el siguiente de la lista que exista.
  const archivoQueNoAlcanza = async () => {
    if (pensando !== null) return
    const actual = ARCHIVOS_QUE_NO_ALCANZAN.findIndex((a) => a.nombre === conv.caso?.nombre)
    const orden = ARCHIVOS_QUE_NO_ALCANZAN.map((_, i) => ARCHIVOS_QUE_NO_ALCANZAN[(actual + 1 + i) % ARCHIVOS_QUE_NO_ALCANZAN.length])
    for (const archivo of orden) {
      const base = casos.find((c) => c.nombre === archivo.base)
      if (!base) continue
      // El primero siempre está; los demás, solo si su respuesta existe.
      if (archivo !== ARCHIVOS_QUE_NO_ALCANZAN[0] && !(await api.analizar(archivo.nombre).then(() => true, () => false))) continue
      abrirConRespuesta({ ...base, nombre: archivo.nombre }, base.titulo)
      return
    }
  }

  // Modo demo (WORKPLAN.md 4.3): una conversación nueva que responde de inmediato con el archivo del
  // demo y las columnas del equipo, sin el paso del calce.
  const abrirConRespuesta = (caso: Caso, pregunta: string) => {
    if (pensando !== null) return
    const c = { ...nueva(caso), calceListo: true }
    setEstado((s) => ({ conversaciones: [c, ...s.conversaciones], activa: c.id }))
    setEnPanel(null)
    setCompleta(null)
    setCierre(false)
    setTimeout(() => {
      decir(c.id, { de: 'tu', texto: pregunta })
      responder(c.id, caso, 'decidir', null)
    })
  }

  // Teclas del demo: 1 a 9 abren la tarjeta de ese lugar del inicio; D, «¿Dónde perforo?» en la
  // conversación activa; M, un archivo que no alcanza; L, el cierre; F, pantalla completa.
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      const escribiendo = e.target instanceof HTMLElement && e.target.closest('input, textarea, select')
      if (escribiendo || e.metaKey || e.ctrlKey || e.altKey) return
      const k = e.key.toLowerCase()
      if (k === 'escape') setCierre(false)
      else if (k === 'l') setCierre((c) => !c)
      else if (k === 'f') {
        if (document.fullscreenElement) document.exitFullscreen().catch(() => {})
        else document.documentElement.requestFullscreen().catch(() => {})
      } else if (k === 'm') archivoQueNoAlcanza()
      else if (k === 'd') {
        const medir = rotuloMedir(conv)
        if (!medir || conv.caso?.motor !== 'espacial') return
        setCompleta(null)
        setCierre(false)
        enviar(medir)
      } else if (/^[1-9]$/.test(k)) {
        const caso = casos[Number(k) - 1]
        if (caso) abrirConRespuesta(caso, caso.titulo)
      }
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  })

  const adjuntar = async (archivo: File | undefined) => {
    if (!archivo) return
    try {
      setAdjunto(await leerCsv(archivo))
    } catch (e) {
      decir(conv.id, { de: 'krylov', tipo: 'texto', texto: `No pude leer el archivo: ${(e as Error).message}` })
    }
  }

  // El archivo de prueba del caso elegido, adjunto como si se hubiera arrastrado.
  const probarArchivo = async (caso: Caso) => {
    try {
      await adjuntar(await api.archivoDePrueba(caso.nombre))
    } catch (e) {
      decir(conv.id, { de: 'krylov', tipo: 'texto', texto: `No pude abrir el archivo de prueba: ${(e as Error).message}` })
    }
  }

  if (completa) {
    return (
      <div className="mx-auto flex min-h-dvh max-w-[90rem] flex-col px-4 py-5 sm:px-8 md:h-dvh md:min-h-0">
        <Topografia />
        <header className="mb-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-1">
          <button onClick={() => setCompleta(null)} className="border border-linea px-4 py-1.5 text-sm hover:border-acento">
            ← Volver al chat
          </button>
          {conv.caso && <p className="text-tinta-suave">{lineaDelCaso(conv.caso)}</p>}
        </header>
        <main className="flex min-h-0 flex-1 flex-col pb-10 lg:pb-0">
          <Respuesta key={completa.analisis.caso} analisis={completa.analisis} nube={completa.nube} textos={completa.textos} />
        </main>
        <SelectorDiseno />
        {cierre && <Cierre alCerrar={() => setCierre(false)} />}
      </div>
    )
  }

  const vacia = conv.mensajes.length === 0
  const ultimo = conv.mensajes.at(-1)
  const ultimaDelUsuario = conv.mensajes.findLast((m) => m.de === 'tu' || (m.de === 'krylov' && m.tipo === 'calce' && m.confirmado))
  const preguntas = conv.caso ? preguntasDe(conv.caso, rotuloMedir(conv)) : []
  const seguimiento =
    ultimo?.de === 'krylov' &&
    pensando === null &&
    ((ultimo.tipo === 'respuesta' && !ultimo.datos.analisis.semaforo.estado.startsWith('rojo')) || (ultimo.tipo === 'texto' && ultimo.accion === 'preguntas'))
      ? preguntas.filter((p) => ultimo.tipo !== 'respuesta' || p.intencion !== ultimo.datos.intencion || ultimo.datos.perforacion)
      : []
  const recientes = estado.conversaciones.filter((c) => c.mensajes.length > 0).map((c) => ({ id: c.id, titulo: tituloDe(c) }))
  const respuestas = conv.mensajes.filter((m): m is Extract<Mensaje, { tipo: 'respuesta' }> => m.de === 'krylov' && m.tipo === 'respuesta')
  // La mesa necesita ancho: en teléfono la respuesta va entera en el chat, como en Carta.
  const mesa = disposicion === 'mesa' && enEscritorio
  const lamina = disposicion === 'lamina'
  const enLienzo = mesa ? (respuestas.find((m) => m.id === enPanel) ?? respuestas.at(-1) ?? null) : null

  const compositor = (
    <Compositor
      texto={texto}
      adjunto={adjunto}
      casos={casos}
      caso={conv.caso}
      ocupado={pensando !== null}
      comando={lamina}
      placeholder={conv.caso ? 'Pregúntale algo a tus datos' : 'Elige una decisión o escribe qué quieres saber'}
      alEscribir={setTexto}
      alEnviar={() => enviar()}
      alAdjuntar={() => selectorArchivo.current?.click()}
      alQuitarAdjunto={() => setAdjunto(null)}
      alElegirCaso={(c) => modificar(conv.id, (x) => ({ ...x, caso: c, calceListo: false, columnas: null }))}
      probarArchivo={
        conv.caso && textosChat.probar_archivo
          ? { rotulo: textosChat.probar_archivo, alProbar: () => conv.caso && probarArchivo(conv.caso) }
          : undefined
      }
    />
  )

  const aviso = (
    <p className="dato mt-3 text-center" title={origen === 'api' ? 'Respuesta de la API' : 'Modo estático'}>
      Krylov practicó con minas simuladas · los costos son supuestos
    </p>
  )

  const chips = (lista: typeof preguntas, alinear = 'justify-start') => (
    <div className={`flex flex-wrap gap-2 ${alinear}`}>
      {lista.map((p) => (
        <Chip key={p.intencion} texto={p.texto} alElegir={() => enviar(p.texto)} />
      ))}
    </div>
  )

  const decisiones = (forma: 'fila' | 'grilla' = 'fila') => (
    <Decisiones casos={casos} quien={quien} alElegir={(c) => enviar(c.titulo, c)} forma={forma} />
  )

  // El inicio, distinto en cada disposición.
  const inicio = (() => {
    if (conv.caso) {
      return (
        <div className={`w-full ${mesa ? '' : 'max-w-3xl'}`}>
          <p className="dato">{conv.caso.empresa_o_industria}</p>
          <h1 className="titular mt-2 text-5xl sm:text-6xl">{conv.caso.titulo}</h1>
          <p className="mt-3 text-lg text-tinta-suave">{MOTOR_EN_PALABRAS[conv.caso.motor]}</p>
          <div className="mt-8">{compositor}</div>
          <div className="mt-5">{chips(preguntas)}</div>
          {aviso}
        </div>
      )
    }
    if (mesa) {
      return (
        <div className="w-full">
          <Marca grande />
          <h1 className="titular mt-6 text-5xl">¿Qué decisión tienes que tomar?</h1>
          <p className="mt-3 text-tinta-suave">{FRASE} Elige una a la derecha, o escríbela.</p>
          <div className="mt-8">{compositor}</div>
          {aviso}
        </div>
      )
    }
    if (lamina) {
      return (
        <div className="w-full max-w-7xl">
          <section className="relative -mx-4 overflow-hidden px-4 pt-4 pb-10 sm:min-h-[24rem]">
            <Particulas className="pointer-events-none absolute inset-0 h-full w-full opacity-90" />
            <div className="relative max-w-2xl">
              <h1 className="titular text-[5.5rem] leading-[0.85] sm:text-[9rem]">Krylov</h1>
              <p className="titular mt-3 text-4xl leading-[1.02] sm:text-5xl">
                Un <span className="text-cobre">data scientist artificial</span> para la minería.
              </p>
              <p className="mt-4 max-w-xl text-xl text-tinta-suave">{FRASE}</p>
            </div>
          </section>
          <div className="max-w-3xl">{compositor}</div>
          <p className="titular mt-16 mb-8 border-t border-linea pt-8 text-4xl">Una mina decide esto todos los días.</p>
          {decisiones()}
          <div className="mt-8">{aviso}</div>
        </div>
      )
    }
    if (disposicion === 'oxido') {
      return (
        <div className="w-full max-w-3xl">
          <h1 className="titular text-5xl sm:text-7xl">¿Qué decisión tienes que tomar?</h1>
          <p className="mt-3 text-lg text-tinta-suave">{FRASE}</p>
          <div className="mt-8">{compositor}</div>
          <div className="mt-5 hidden lg:block">
            <p className="dato mb-2">O empieza por una</p>
            <div className="flex flex-wrap gap-2">
              {casos.map((c) => (
                <Chip key={c.nombre} texto={c.titulo} alElegir={() => enviar(c.titulo, c)} />
              ))}
            </div>
          </div>
          <div className="mt-10 lg:hidden">{decisiones('grilla')}</div>
          {aviso}
        </div>
      )
    }
    // Carta.
    return (
      <div className="w-full max-w-6xl">
        <h1 className="titular max-w-4xl text-6xl sm:text-8xl">¿Qué decisión tienes que tomar?</h1>
        <p className="mt-4 max-w-2xl text-xl text-tinta-suave">{FRASE}</p>
        <div className="mt-12">{decisiones()}</div>
        <div className="mt-12 max-w-3xl">{compositor}</div>
        <div className="max-w-3xl">{aviso}</div>
      </div>
    )
  })()

  const mensajeRespuesta = (m: Extract<Mensaje, { tipo: 'respuesta' }>, n: number) => {
    const contenido = (
      <RespuestaEnChat
        datos={m.datos}
        creado={m.creado}
        alAbrir={() => setCompleta(m.datos)}
        alPerforar={(c) => perforar(m.datos, c)}
        ocupado={pensando !== null}
        grande={lamina}
        soloTitular={mesa}
      />
    )
    if (mesa) {
      const activa = enLienzo?.id === m.id
      return (
        <MensajeKrylov>
          <button onClick={() => setEnPanel(m.id)} className={`block w-full border-l-2 pl-4 text-left ${activa ? 'border-oxido' : 'border-linea hover:border-tinta-suave'}`}>
            {contenido}
            <span className={`dato mt-2 block ${activa ? 'text-oxido' : ''}`}>{activa ? 'En el lienzo' : 'Ver en el lienzo'}</span>
          </button>
        </MensajeKrylov>
      )
    }
    if (lamina) {
      return (
        <section className="panel flex flex-col px-5 py-6 sm:px-10 sm:py-9 lg:min-h-[min(82vh,48rem)]">
          {contenido}
          <footer className="mt-auto flex items-end justify-between pt-8">
            <Logotipo className="text-base text-tenue" />
            <span className="dato">
              {String(n).padStart(2, '0')} / {String(respuestas.length).padStart(2, '0')}
            </span>
          </footer>
        </section>
      )
    }
    return <MensajeKrylov>{contenido}</MensajeKrylov>
  }

  const listaMensajes = (
    <ol className={`mx-auto space-y-10 py-8 ${mesa ? 'max-w-none' : lamina ? 'max-w-6xl' : 'max-w-5xl'}`}>
      {conv.mensajes.map((m) => {
        const ancha = m.de === 'krylov' && m.tipo === 'respuesta' && (m.datos.completa || m.datos.perforacion || lamina)
        return (
          <li key={m.id} ref={m === ultimaDelUsuario ? ultimaPregunta : undefined} className={`mx-auto scroll-mt-4 ${ancha || mesa ? '' : 'max-w-3xl'}`}>
            {m.de === 'tu' ? (
              <MensajeTu texto={m.texto} adjunto={m.adjunto} />
            ) : m.tipo === 'respuesta' ? (
              <>
                {mensajeRespuesta(m, respuestas.indexOf(m) + 1)}
                {m === ultimo && seguimiento.length > 0 && <div className={`aparecer mt-5 ${mesa || lamina ? '' : 'pl-11'}`}>{chips(seguimiento)}</div>}
              </>
            ) : (
              <MensajeKrylov>
                {m.tipo === 'calce' ? (
                  <CalceEnChat
                    calce={m.calce}
                    papeles={m.papeles}
                    confirmado={m.confirmado}
                    alConfirmar={(a) => conv.caso && confirmarCalce(conv.id, m.id, conv.caso, m.calce, m.intencion, a)}
                  />
                ) : (
                  <>
                    <p className="text-lg leading-relaxed">{m.texto}</p>
                    {m.nota && <p className="dato mt-2">{m.nota}</p>}
                    {m.accion === 'modelos' && (
                      <div className="mt-5">
                        <Decisiones casos={casos} quien={quien} alElegir={elegirModelo} forma="grilla" desactivadas={conv.caso !== null} />
                      </div>
                    )}
                  </>
                )}
                {m === ultimo && seguimiento.length > 0 && <div className="aparecer mt-5">{chips(seguimiento)}</div>}
              </MensajeKrylov>
            )}
          </li>
        )
      })}
      {pensando === conv.id && (
        <li className={`mx-auto ${mesa ? '' : 'max-w-3xl'}`}>
          <MensajeKrylov pensando>
            <p className="brillo text-lg">Calculando con el modelo…</p>
          </MensajeKrylov>
        </li>
      )}
    </ol>
  )

  const pie = (
    <footer className="relative shrink-0 px-4 pb-3">
      <div className="pointer-events-none absolute inset-x-0 -top-8 h-8 bg-linear-to-t from-fondo" />
      <div className={`mx-auto ${mesa ? '' : 'max-w-3xl'}`}>
        {compositor}
        {aviso}
      </div>
    </footer>
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
      <Topografia />

      {lateral && (
        <>
          <div className="fixed inset-0 z-30 bg-fondo/60 lg:hidden" onClick={() => setLateral(false)} />
          <div className="fixed inset-y-0 left-0 z-40 lg:static">
            <Lateral
              casos={casos}
              quien={quien}
              activo={conv.caso?.nombre ?? null}
              recientes={recientes}
              activa={conv.id}
              alNuevo={() => empezar()}
              alElegirModelo={(c) => empezar(c)}
              alAbrir={(id) => {
                setEstado((s) => ({ ...s, activa: id }))
                setEnPanel(null)
                cerrarLateralEnTelefono()
              }}
              alCerrar={fijaYVisible ? undefined : () => setLateral(false)}
            />
          </div>
        </>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-3 border-b border-linea/60 pr-24 pl-4 lg:pr-4">
          {!lateral && (
            <>
              <button onClick={() => setLateral(true)} title="Abrir la barra" aria-label="Abrir la barra" className="p-1.5 text-tinta-suave hover:text-tinta">
                <IconoLateral />
              </button>
              <button onClick={() => empezar()} className="flex items-center gap-2" title="Nuevo análisis">
                <Marca />
                <Logotipo className="text-lg" />
              </button>
            </>
          )}
          <p className="min-w-0 flex-1 truncate text-center text-sm text-tinta-suave">{vacia ? '' : tituloDe(conv)}</p>
          {conv.caso && <span className="dato hidden sm:block">{conv.caso.empresa_o_industria}</span>}
        </header>

        {mesa ? (
          <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
            <section className="flex min-h-0 flex-col lg:w-[27rem] lg:shrink-0 xl:w-[30rem]">
              {vacia ? (
                <main className="flex min-h-0 flex-1 flex-col overflow-y-auto px-5 py-8">
                  <div className="my-auto">{inicio}</div>
                </main>
              ) : (
                <>
                  <main className="desliza-lista min-h-0 flex-1 overflow-y-auto px-5" aria-live="polite">
                    {listaMensajes}
                  </main>
                  {pie}
                </>
              )}
            </section>
            <Mesa
              datos={enLienzo?.datos ?? null}
              clave={enLienzo?.id ?? null}
              caso={conv.caso}
              casos={casos}
              quien={quien}
              pensando={pensando === conv.id}
              alElegir={(c) => enviar(c.titulo, c)}
              alPerforar={(c) => enLienzo && perforar(enLienzo.datos, c)}
            />
          </div>
        ) : vacia ? (
          <main className="desliza-lista flex min-h-0 flex-1 flex-col items-center overflow-y-auto px-4 pb-16 sm:px-8">
            <div className="my-auto flex w-full flex-col items-center py-10">{inicio}</div>
          </main>
        ) : (
          <>
            <main className="desliza-lista min-h-0 flex-1 overflow-y-auto px-4 sm:px-8" aria-live="polite">
              {listaMensajes}
            </main>
            {pie}
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
          <div className="border border-dashed border-acento px-10 py-8 text-center">
            <p className="titular text-4xl">Suelta tu CSV</p>
            <p className="mt-2 text-sm text-tinta-suave">Queda adjunto a tu próxima pregunta</p>
          </div>
        </div>
      )}

      <SelectorDiseno />
      {cierre && <Cierre alCerrar={() => setCierre(false)} />}
    </div>
  )
}

function MensajeTu({ texto, adjunto }: { texto: string; adjunto?: InfoCsv }) {
  return (
    <div className="flex flex-col items-end gap-2">
      {adjunto && <TarjetaArchivo info={adjunto} />}
      {texto && (
        <p className="max-w-[85%] border-r-2 border-cobre bg-superficie/80 px-4 py-2 font-mono text-sm leading-relaxed whitespace-pre-wrap text-tinta-suave">
          {texto}
        </p>
      )}
    </div>
  )
}

function MensajeKrylov({ children, pensando = false }: { children: ReactNode; pensando?: boolean }) {
  return (
    <div className="flex gap-4">
      <span className="mt-1">
        <Marca pensando={pensando} />
      </span>
      <div className="min-w-0 flex-1 pt-0.5">{children}</div>
    </div>
  )
}

function Chip({ texto, alElegir }: { texto: string; alElegir: () => void }) {
  return (
    <button onClick={alElegir} className="border border-linea bg-fondo/60 px-3.5 py-2 text-sm transition-colors hover:border-acento hover:text-tinta">
      {texto}
    </button>
  )
}
