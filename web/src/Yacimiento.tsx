// La sexta decisión, «¿Dónde está el mineral?» (D-40, D-42): el recorrido del yacimiento del deck
// (pitch/deck/yacimiento.html), dentro de un marco. Sin archivo es el recorrido calculado antes, con su examen. Con un
// archivo subido, la misma página dibuja la respuesta de la red para ese archivo (`servicio/yacimiento.py`) y el
// recorrido termina antes del examen: un archivo subido no trae la respuesta correcta. De su sello se cuenta solo el mapa.

import { useEffect, useRef, useState } from 'react'
import type { Archivo } from './App'
import { conEscena } from './soporte'
import type { DatosYacimiento, TextosYacimiento } from './tipos'

const ALTO_BARRA = 88 // px: el recorrido y su barra caben enteros en la pantalla
const ALTO_BARRA_ARCHIVO = 112 // con un archivo, la barra dice además qué archivo respondió la red
const PAGINA = '/deck/yacimiento.html'
const SUS_DATOS = '<script src="datos/yacimiento.js"></script>' // la línea de la página que carga los datos calculados antes

// La página del deck, sin tocarla, con los datos de la respuesta en el lugar de los suyos.
async function paginaCon(datos: DatosYacimiento): Promise<string> {
  const r = await fetch(PAGINA)
  const html = await r.text()
  if (!r.ok || !html.includes(SUS_DATOS)) throw new Error('la página del yacimiento cambió')
  const base = `<base href="${new URL('/deck/', window.location.origin).href}">`
  // La página anota su paso en la dirección (`history.replaceState`), y un documento sin dirección propia no puede: aquí el paso lo lleva la app.
  const propios = `<script>history.replaceState = function () {}; window.YACIMIENTO = ${JSON.stringify(datos).replace(/</g, '\\u003c')};</script>`
  return html.replace('<head>', `<head>${base}`).replace(SUS_DATOS, () => propios) // con función: el texto de los datos no se lee como patrón
}

const miles = (n: number) => n.toLocaleString('es-CL')

interface Props {
  textos: Partial<TextosYacimiento>
  datos: DatosYacimiento | null // null: el recorrido calculado antes
  archivo: Archivo | null
  guardada: boolean // sin servidor, la respuesta del archivo de ejemplo sale de su copia
  alSubir: () => void
}

export default function Yacimiento({ textos, datos, archivo, guardada, alSubir }: Props) {
  const marco = useRef<HTMLIFrameElement>(null)
  const [paso, setPaso] = useState(0)
  const [pagina, setPagina] = useState<string | null>(null)
  const [falla, setFalla] = useState(false)
  const escena = conEscena()
  const PASOS = datos ? 3 : 4 // con un archivo subido no hay examen
  const alto = datos ? ALTO_BARRA_ARCHIVO : ALTO_BARRA

  useEffect(() => {
    if (!datos || !escena) return
    let vigente = true
    paginaCon(datos).then((html) => vigente && setPagina(html), () => vigente && setFalla(true))
    return () => {
      vigente = false
    }
  }, [datos, escena])

  useEffect(() => {
    marco.current?.contentWindow?.postMessage({ krylov: 1, paso }, window.location.origin)
  }, [paso])

  // La página del yacimiento devuelve las teclas que recibe: las flechas mueven el recorrido y el resto es de la app.
  useEffect(() => {
    const mover = (tecla: string) => {
      if (tecla === 'ArrowRight' || tecla === ' ') setPaso((p) => Math.min(PASOS - 1, p + 1))
      else if (tecla === 'ArrowLeft') setPaso((p) => Math.max(0, p - 1))
      else return false
      return true
    }
    const oir = (e: MessageEvent<{ krylov?: number; tecla?: string }>) => {
      if (e.source !== marco.current?.contentWindow || e.origin !== window.location.origin || e.data?.krylov !== 1) return
      if (typeof e.data.tecla === 'string' && !mover(e.data.tecla)) window.dispatchEvent(new KeyboardEvent('keydown', { key: e.data.tecla }))
    }
    const tecla = (e: KeyboardEvent) => {
      if (mover(e.key)) e.preventDefault()
    }
    window.addEventListener('message', oir)
    window.addEventListener('keydown', tecla)
    return () => {
      window.removeEventListener('message', oir)
      window.removeEventListener('keydown', tecla)
    }
  }, [PASOS])

  const aviso = (
    <div className="min-w-0 flex-1 text-sm leading-snug">
      <p className="text-oxido">
        {datos
          ? [
              (textos.con_archivo ?? '').replace('{archivo}', archivo?.nombre ?? '').replace('{muestras}', miles(datos.numeros.compositos)).replace('{bloques}', miles(datos.numeros.bloques)),
              archivo?.prueba ? textos.de_ejemplo : null,
              guardada ? textos.guardada : null,
            ].filter(Boolean).join(' ')
          : textos.que_es}
      </p>
      <p className="text-tinta-suave">{textos.sello}</p>
    </div>
  )
  const subir = textos.subir && (
    <button onClick={alSubir} className="border border-linea px-4 py-2.5 hover:border-cobre">
      {textos.subir}
    </button>
  )

  if (!escena) {
    return (
      <main className="flex-1 px-4 py-10">
        {textos.quien && <p className="text-lg text-cobre">Lo decide: {textos.quien}</p>}
        <h1 className="titular mt-2 text-6xl">{textos.titulo}</h1>
        <p className="mt-4 text-xl text-tinta-suave">{textos.archivo}</p>
        <div className="mt-8 border-t border-linea pt-4">{aviso}</div>
        <p className="mt-6 text-tinta-suave">{textos.angosto}</p>
        <div className="mt-6">{subir}</div>
      </main>
    )
  }

  return (
    <main className="flex-1">
      <h1 className="sr-only">{textos.titulo}</h1>
      {falla && (
        <p role="alert" className="mx-6 mt-4 border-l-4 border-actuar bg-superficie px-5 py-3">
          Krylov respondió, pero no pudo dibujar la respuesta en esta pantalla. Recarga la página y sube el archivo de nuevo.
        </p>
      )}
      <iframe
        ref={marco}
        {...(datos ? { srcDoc: pagina ?? '' } : { src: PAGINA })}
        onLoad={() => marco.current?.contentWindow?.postMessage({ krylov: 1, paso }, window.location.origin)}
        title={textos.titulo ?? ''}
        className="block w-full border-0 bg-fondo"
        // la página del deck no declara esquema de color: con el mismo en el marco, su fondo transparente deja ver el de la app
        style={{ height: `calc(100dvh - 3.5rem - ${alto}px)`, colorScheme: 'light' }}
      />
      <div className="flex items-center gap-8 border-t border-linea px-6 py-3" style={{ minHeight: alto }}>
        {aviso}
        <div className="flex shrink-0 items-center gap-3">
          <span className="text-tinta-suave" aria-live="polite">
            Paso {paso + 1} de {PASOS}
          </span>
          {subir}
          <button onClick={() => setPaso((p) => Math.max(0, p - 1))} disabled={paso === 0} className="border border-linea px-4 py-2.5 hover:border-cobre disabled:opacity-40">
            Anterior
          </button>
          <button onClick={() => setPaso((p) => Math.min(PASOS - 1, p + 1))} disabled={paso === PASOS - 1} className="bg-cobre px-5 py-2.5 font-semibold text-fondo hover:opacity-90 disabled:opacity-40">
            Siguiente
          </button>
        </div>
      </div>
    </main>
  )
}
