// La caja de texto del chat: el archivo adjunto como ficha, el texto, el botón para adjuntar, el
// modelo elegido y el botón de enviar. Enter envía; Mayúscula+Enter baja de línea.

import { useLayoutEffect, useRef } from 'react'
import type { InfoCsv } from './csv'
import SelectorModelo from './SelectorModelo'
import TarjetaArchivo from './TarjetaArchivo'
import type { Caso } from './tipos'

const ALTO_MAXIMO = 208

interface Props {
  texto: string
  adjunto: InfoCsv | null
  casos: Caso[]
  caso: Caso | null
  ocupado: boolean
  placeholder: string
  alEscribir: (t: string) => void
  alEnviar: () => void
  alAdjuntar: () => void
  alQuitarAdjunto: () => void
  alElegirCaso: (c: Caso) => void
}

export default function Compositor(p: Props) {
  const campo = useRef<HTMLTextAreaElement>(null)
  const vacio = !p.texto.trim() && !p.adjunto

  // La caja crece con el texto hasta un tope.
  useLayoutEffect(() => {
    const el = campo.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, ALTO_MAXIMO)}px`
  }, [p.texto])

  return (
    <form
      className="compositor rounded-(--radio-caja) border border-linea bg-fondo shadow-(--sombra) transition-colors focus-within:border-tinta-suave/50"
      onSubmit={(e) => {
        e.preventDefault()
        p.alEnviar()
      }}
    >
      {p.adjunto && (
        <div className="px-4 pt-4">
          <TarjetaArchivo info={p.adjunto} alQuitar={p.alQuitarAdjunto} />
        </div>
      )}
      <textarea
        ref={campo}
        rows={1}
        value={p.texto}
        autoFocus
        onChange={(e) => p.alEscribir(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
            e.preventDefault()
            p.alEnviar()
          }
        }}
        placeholder={p.placeholder}
        className="block w-full resize-none bg-transparent px-5 pt-4 pb-1 leading-relaxed outline-none placeholder:text-tinta-suave/80"
      />
      <div className="flex items-center gap-1 px-2.5 pb-2.5">
        <button
          type="button"
          onClick={p.alAdjuntar}
          title="Adjuntar un CSV"
          aria-label="Adjuntar un CSV"
          className="flex h-9 w-9 items-center justify-center rounded-full text-tinta-suave hover:bg-superficie hover:text-tinta"
        >
          <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden>
            <path d="M10 4v12M4 10h12" />
          </svg>
        </button>
        <SelectorModelo casos={p.casos} caso={p.caso} alElegir={p.alElegirCaso} />
        <span className="flex-1" />
        <button
          type="submit"
          disabled={vacio || p.ocupado}
          aria-label="Enviar"
          className="flex h-9 w-9 items-center justify-center rounded-full bg-tinta text-fondo transition-colors disabled:bg-linea disabled:text-tinta-suave"
        >
          <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <path d="M10 16V4M5 9l5-5 5 5" />
          </svg>
        </button>
      </div>
    </form>
  )
}
