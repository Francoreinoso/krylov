// La portada del diseño Lámina: un terreno hecho de partículas de cobre y oro que respira despacio,
// eco de la lámina 1 del deck. Es ilustración, no datos. Quieto con movimiento reducido.

import { useEffect, useRef } from 'react'

const N = 9000

export default function Particulas({ className = '' }: { className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return
    // Semilla fija: la misma nube en cada carga.
    let a = 26
    const azar = () => {
      a = (a * 16807) % 2147483647
      return a / 2147483647
    }
    const puntos = Array.from({ length: N }, () => ({ u: azar() * 2 - 1, v: azar() * 2 - 1, r: azar() }))
    const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let cuadro = 0

    const pintar = (t: number) => {
      const { width, height } = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      if (canvas.width !== Math.round(width * dpr)) {
        canvas.width = Math.round(width * dpr)
        canvas.height = Math.round(height * dpr)
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, width, height)
      const s = t / 1000
      const escala = Math.min(width * 0.62, height * 1.1)
      for (const p of puntos) {
        const d = Math.hypot(p.u, p.v)
        if (d > 1) continue
        // Un cerro con terrazas que ondulan: la altura sube hacia el centro.
        const h = (1 - d) ** 1.3 * 0.55 + 0.05 * Math.sin(d * 18 - s * 0.6) + 0.03 * Math.sin(p.u * 7 + s * 0.4)
        // Vista oblicua: x a lo ancho, y hacia el fondo y la altura hacia arriba.
        const x = width * 0.58 + (p.u * 0.95 - p.v * 0.35) * escala
        const y = height * 0.52 + (p.v * 0.32 + p.u * 0.1) * escala - h * escala * 0.6
        const luz = Math.min(1, 0.25 + h * 1.4)
        ctx.globalAlpha = Math.min(1, 0.45 + luz * 0.6 * (0.6 + 0.4 * p.r))
        ctx.fillStyle = luz > 0.75 ? '#f6d68a' : luz > 0.5 ? '#eec25a' : '#e2854a'
        const r = 1 + luz * 1.6 * p.r
        ctx.fillRect(x, y, r, r)
      }
      ctx.globalAlpha = 1
      if (!quieto) cuadro = requestAnimationFrame(pintar)
    }
    cuadro = requestAnimationFrame(pintar)
    return () => cancelAnimationFrame(cuadro)
  }, [])

  return <canvas ref={ref} className={className} aria-hidden />
}
