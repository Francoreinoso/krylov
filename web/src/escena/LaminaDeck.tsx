// Una lámina del deck dentro de la app (D-42): un marco con escena.html, que corre los módulos de pitch/deck con los
// datos que recibe. Cada vez que cambian los datos se abre un marco nuevo (`key` en quien lo usa), porque el deck arma
// su escena una sola vez. Fuera de la vista, la escena se pausa.

import { useEffect, useImperativeHandle, useRef, useState, type Ref } from 'react'
import type { AlMarco, DelMarco, Lamina } from './protocolo'

export interface MandoLamina {
  paso: (n: number) => void
  perforar: (letra: string, capa: Record<string, unknown>, valor: number) => void
}

interface Props {
  lamina: Lamina
  datos: unknown
  config?: unknown
  paso?: number
  titulo: string
  className?: string
  alFallar?: (mensaje: string) => void
  ref?: Ref<MandoLamina>
}

export default function LaminaDeck({ lamina, datos, config = {}, paso = 0, titulo, className = '', alFallar, ref }: Props) {
  const marco = useRef<HTMLIFrameElement>(null)
  const [lista, setLista] = useState(false)
  const enviar = (m: AlMarco) => marco.current?.contentWindow?.postMessage(m, window.location.origin)

  useImperativeHandle(ref, () => ({
    paso: (n) => enviar({ tipo: 'paso', paso: n }),
    perforar: (letra, capa, valor) => enviar({ tipo: 'perforar', letra, capa, valor }),
  }))

  useEffect(() => {
    const oir = (e: MessageEvent<DelMarco>) => {
      if (e.source !== marco.current?.contentWindow || e.origin !== window.location.origin) return
      const m = e.data
      if (m.tipo === 'esperando') enviar({ tipo: 'escena', lamina, datos, config, paso })
      else if (m.tipo === 'lista') setLista(true)
      else if (m.tipo === 'falla') alFallar?.(m.mensaje)
      // las teclas que se apretaron con el foco en la escena son de la app: se repiten aquí
      else if (m.tipo === 'tecla') window.dispatchEvent(new KeyboardEvent('keydown', { key: m.tecla }))
    }
    window.addEventListener('message', oir)
    return () => window.removeEventListener('message', oir)
    // el pedido sale una sola vez, cuando el marco avisa que está esperando
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // fuera de la vista, la escena no gasta cuadros
  useEffect(() => {
    const el = marco.current
    if (!el) return
    const visto = new IntersectionObserver(([e]) => enviar({ tipo: 'pausa', si: !e.isIntersecting }))
    visto.observe(el)
    return () => visto.disconnect()
  }, [])

  return (
    <iframe
      ref={marco}
      src="/escena.html"
      title={titulo}
      className={`block aspect-video w-full border-0 bg-fondo transition-opacity duration-500 ${lista ? 'opacity-100' : 'opacity-0'} ${className}`}
    />
  )
}
