// La sexta decisión, «¿Dónde está el mineral?» (D-40, D-42): el recorrido del yacimiento del deck
// (pitch/deck/yacimiento.html), dentro de un marco. Su red no corre en el servicio, así que es un recorrido calculado
// antes, y la pantalla lo dice: yacimiento simulado, todavía no recibe archivos, y de su sello se cuenta solo el mapa.

import { useEffect, useRef, useState } from 'react'
import { conEscena } from './soporte'
import type { TextosYacimiento } from './tipos'

const PASOS = 4
const ALTO_BARRA = 88 // px: el recorrido y su barra caben enteros en la pantalla

export default function Yacimiento({ textos }: { textos: Partial<TextosYacimiento> }) {
  const marco = useRef<HTMLIFrameElement>(null)
  const [paso, setPaso] = useState(0)
  const escena = conEscena()

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
  }, [])

  const aviso = (
    <div className="min-w-0 flex-1 text-sm">
      <p className="text-oxido">{textos.que_es}</p>
      <p className="text-tinta-suave">{textos.sello}</p>
    </div>
  )

  if (!escena) {
    return (
      <main className="flex-1 px-4 py-10">
        {textos.quien && <p className="text-lg text-cobre">Lo decide: {textos.quien}</p>}
        <h1 className="titular mt-2 text-6xl">{textos.titulo}</h1>
        <p className="mt-4 text-xl text-tinta-suave">{textos.archivo}</p>
        <div className="mt-8 border-t border-linea pt-4">{aviso}</div>
        <p className="mt-6 text-tinta-suave">{textos.angosto}</p>
      </main>
    )
  }

  return (
    <main className="flex-1">
      <iframe
        ref={marco}
        src="/deck/yacimiento.html"
        title={textos.titulo ?? ''}
        className="block w-full border-0 bg-fondo"
        // la página del deck no declara esquema de color: con el mismo en el marco, su fondo transparente deja ver el de la app
        style={{ height: `calc(100dvh - 3.5rem - ${ALTO_BARRA}px)`, colorScheme: 'light' }}
      />
      <div className="flex items-center gap-8 border-t border-linea px-6 py-3" style={{ minHeight: ALTO_BARRA }}>
        {aviso}
        <div className="flex shrink-0 items-center gap-3">
          <span className="text-tinta-suave" aria-live="polite">
            Paso {paso + 1} de {PASOS}
          </span>
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
