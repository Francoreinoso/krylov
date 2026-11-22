// Entra un archivo, sale la respuesta (la lámina 5 del deck, pitch/deck/js/rafaga.js, con el archivo de verdad).
// Las filas del archivo caen como puntos y se ordenan en una tarjeta: como un mapa si traen ubicación, como una
// serie por unidad si traen tiempo. Al analizar, viajan por el carril y entran al núcleo, que gira mientras dure la
// espera real: no hay barra de avance inventada. Cuando llega la respuesta, el núcleo se abre. Si Krylov no responde,
// los puntos se detienen en la puerta y el núcleo no se enciende.

import { useEffect, useRef } from 'react'

export type Fase = 'cae' | 'ordena' | 'entra' | 'sale' | 'rechazo'

// Dónde queda cada punto en la tarjeta ordenada, de 0 a 1 (y hacia abajo). Sin orden, los puntos quedan en filas.
export type Orden = { x: number; y: number }[] | null

interface Props {
  n: number
  orden: Orden
  fase: Fase
  className?: string
}

const W = 1600
const H = 900
const TARJETA = { x: 90, y: 110, lado: 680 }
const NUCLEO = { x: 1300, y: 450 }
const COBRE = [226, 133, 74]
const PUNTO = '#f4e8d4'
const LINEA = '#2d2924'

const acotar = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v))
const suave = (t: number) => {
  t = acotar(t)
  return t * t * (3 - 2 * t)
}
const fuera = (t: number) => 1 - (1 - acotar(t)) ** 3

// Azar con semilla: la misma caída cada vez.
function azar(semilla: number) {
  let a = semilla >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = Math.imul(a ^ (a >>> 15), a | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const enTarjeta = (p: { x: number; y: number }) => ({ x: TARJETA.x + 24 + p.x * (TARJETA.lado - 48), y: TARJETA.y + 24 + p.y * (TARJETA.lado - 48) })

export default function Coreografia({ n, orden, fase, className = '' }: Props) {
  const lienzo = useRef<HTMLCanvasElement>(null)
  const estado = useRef({ fase, desde: 0, previo: [] as { x: number; y: number }[] })

  // Al cambiar de fase, cada punto parte desde donde estaba.
  useEffect(() => {
    const e = estado.current
    if (e.fase !== fase) {
      e.fase = fase
      e.desde = performance.now()
    }
  }, [fase])

  useEffect(() => {
    const cv = lienzo.current!
    const ctx = cv.getContext('2d')!
    const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const r = azar(42)
    const lado = Math.ceil(Math.sqrt(n))
    const filas = Array.from({ length: n }, (_, i) => enTarjeta({ x: (i % lado) / Math.max(1, lado - 1), y: Math.floor(i / lado) / Math.max(1, lado - 1) }))
    const ordenados = orden ? orden.map(enTarjeta) : filas
    const demora = filas.map(() => r() * 0.9)
    const arriba = filas.map((f) => ({ x: f.x + (r() - 0.5) * 80, y: -40 - r() * 300 }))
    let visible = true
    let cuadro = 0
    estado.current.desde = performance.now()

    const ajustar = () => {
      const razon = Math.min(window.devicePixelRatio || 1, 2)
      cv.width = Math.round(cv.clientWidth * razon)
      cv.height = Math.round(cv.clientHeight * razon)
    }
    ajustar()
    const alCambiar = new ResizeObserver(ajustar)
    alCambiar.observe(cv)
    const visto = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting
    })
    visto.observe(cv)

    const nucleo = (t: number, encendido: number, abre: number) => {
      const giro = t / 1000
      for (let a = 0; a < 3; a++) {
        const al = (0.9 - a * 0.26) * (0.25 + 0.75 * encendido) * (1 - abre)
        ctx.strokeStyle = encendido > 0 ? `rgba(${COBRE},${al})` : `rgba(132,124,111,${al})`
        ctx.lineWidth = 3.4 - a * 0.8
        const radio = 46 + a * 22 + abre * 260
        ctx.beginPath()
        ctx.arc(NUCLEO.x, NUCLEO.y, radio, giro * (1.2 - a * 0.5) * encendido + a, giro * (1.2 - a * 0.5) * encendido + a + 4.4)
        ctx.stroke()
      }
      const pulso = encendido * (0.5 + 0.5 * Math.sin(t / 160))
      ctx.fillStyle = encendido > 0 ? `rgba(${COBRE},${(0.25 + 0.5 * pulso) * (1 - abre)})` : 'rgba(132,124,111,0.35)'
      ctx.beginPath()
      ctx.arc(NUCLEO.x, NUCLEO.y, 30, 0, Math.PI * 2)
      ctx.fill()
    }

    const pintar = (ahora: number) => {
      const { fase, desde } = estado.current
      const t = quieto ? 1e6 : ahora - desde
      const s = t / 1000
      const k = Math.min(cv.width / W, cv.height / H)
      ctx.setTransform(k, 0, 0, k, (cv.width - W * k) / 2, (cv.height - H * k) / 2)
      ctx.clearRect(-W, -H, W * 3, H * 3)

      // la tarjeta del archivo y el carril hasta el núcleo
      const tarjeta = fase === 'cae' || fase === 'ordena' ? 1 : fase === 'entra' ? 1 - suave(s / 0.9) : fase === 'rechazo' ? 0.35 : 0
      ctx.globalAlpha = tarjeta
      ctx.fillStyle = '#17140f'
      ctx.fillRect(TARJETA.x, TARJETA.y, TARJETA.lado, TARJETA.lado)
      ctx.strokeStyle = '#4a443b'
      ctx.lineWidth = 1.5
      ctx.strokeRect(TARJETA.x, TARJETA.y, TARJETA.lado, TARJETA.lado)
      ctx.globalAlpha = 1
      ctx.strokeStyle = LINEA
      ctx.lineWidth = 2
      ctx.setLineDash([4, 10])
      ctx.beginPath()
      ctx.moveTo(TARJETA.x + TARJETA.lado, NUCLEO.y)
      ctx.lineTo(NUCLEO.x - 90, NUCLEO.y)
      ctx.stroke()
      ctx.setLineDash([])

      const encendido = fase === 'entra' || fase === 'sale' ? 1 : fase === 'rechazo' ? 0 : 0.35
      nucleo(ahora, encendido, fase === 'sale' ? fuera(s / 0.7) : 0)

      // los puntos
      ctx.fillStyle = PUNTO
      const previo = estado.current.previo
      for (let i = 0; i < n; i++) {
        const meta = fase === 'cae' ? filas[i] : ordenados[i]
        let x: number
        let y: number
        let a = 1
        if (fase === 'cae') {
          const q = fuera((s - demora[i]) / 0.9)
          x = arriba[i].x + (meta.x - arriba[i].x) * q
          y = arriba[i].y + (meta.y - arriba[i].y) * q
          a = q > 0 ? 1 : 0
        } else if (fase === 'ordena') {
          const de = previo[i] ?? filas[i]
          const q = suave((s - (i / n) * 0.35) / 0.9)
          x = de.x + (meta.x - de.x) * q
          y = de.y + (meta.y - de.y) * q
        } else {
          // entran de izquierda a derecha: los más cercanos al carril primero
          const de = previo[i] ?? meta
          const parte = (de.x - TARJETA.x) / TARJETA.lado
          const q = fase === 'sale' ? 1 : suave((s - 0.05 - (1 - parte) * 0.45) / 0.55)
          const tope = fase === 'rechazo' ? 0.82 : 1 // en el rechazo se detienen antes de la puerta
          const qq = Math.min(q, tope)
          const cx = (de.x + NUCLEO.x) / 2
          const cy = Math.min(de.y, NUCLEO.y) - 120
          x = (1 - qq) ** 2 * de.x + 2 * (1 - qq) * qq * cx + qq * qq * NUCLEO.x
          y = (1 - qq) ** 2 * de.y + 2 * (1 - qq) * qq * cy + qq * qq * NUCLEO.y
          if (fase === 'rechazo') {
            // no entran: se quedan amontonados frente a la puerta, apagándose
            const cae = acotar((s - 1.4) / 1.0)
            y += cae * cae * 70 * ((i % 7) / 7)
            a = 1 - 0.6 * cae
          } else a = 1 - acotar((q - 0.88) / 0.12)
        }
        if (a <= 0.01) continue
        ctx.globalAlpha = a
        ctx.fillRect(x - 2.2, y - 2.2, 4.4, 4.4)
        if (fase === 'cae' || fase === 'ordena') previo[i] = { x, y }
      }
      ctx.globalAlpha = 1
    }

    const bucle = (ahora: number) => {
      cuadro = requestAnimationFrame(bucle)
      if (visible) pintar(ahora)
    }
    cuadro = requestAnimationFrame(bucle)
    return () => {
      cancelAnimationFrame(cuadro)
      alCambiar.disconnect()
      visto.disconnect()
    }
  }, [n, orden])

  return <canvas ref={lienzo} className={`block h-full w-full ${className}`} aria-hidden="true" />
}
