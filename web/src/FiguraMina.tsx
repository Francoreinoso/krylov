// Las cinco figuras de la lámina 7 del deck (pitch/deck/js/vision.js), portadas de WebGL a Canvas 2D:
// los mismos puntos con la misma semilla, la misma animación de cada figura y la luz que se suma
// (composición «lighter»). Son ilustraciones, no datos. Cada tarjeta dibuja la suya con su propia
// cámara; se detienen fuera de la pantalla y quedan quietas con movimiento reducido.

import { useEffect, useRef } from 'react'
import Ilustracion from './Ilustracion'

type V3 = [number, number, number]

const COBRE: V3 = [0.91, 0.52, 0.27]
const ORO: V3 = [1.0, 0.82, 0.45]
const OXIDO: V3 = [0.21, 0.76, 0.68]
const ARENA: V3 = [0.5, 0.45, 0.38]
const ROJO: V3 = [0.92, 0.36, 0.22]
const GRIS = '107,97,86' // 0x6b6156, las líneas de las figuras

const T_QUIETO = 9.3 // el instante que muestra el deck sin movimiento
const DISTANCIA = 60 // cámara del deck: en z = 60, mirando al origen
const ALTO_VISIBLE = 8.2 // unidades de escena que caben de arriba abajo en cada tarjeta
const ALTURA_GRUPO = 0.9 // el deck sube cada figura 0,9

const mezcla = (a: V3, b: V3, t: number): V3 => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]
const acotar = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x))
const paso = (a: number, b: number, x: number) => {
  const t = acotar((x - a) / (b - a), 0, 1)
  return t * t * (3 - 2 * t)
}
const modulo = (x: number, y: number) => x - y * Math.floor(x / y) // como mod() de GLSL

// El mismo generador con semilla del deck (K.azar).
function azar(semilla: number) {
  let a = semilla >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// Un punto en un instante: posición en el grupo, color (ya multiplicado por su brillo) y diámetro en
// unidades de escena.
interface Punto {
  p: V3
  color: V3
  brillo: number
  tamano: number
}

interface Figura {
  escala: number
  rotacion: (t: number) => [x: number, y: number, z: number]
  lineas: { v: number[]; color: string; opacidad: number }[]
  puntos: (t: number, salida: Punto[]) => void
}

// Las cinco figuras, construidas en el orden del deck para que el azar dé los mismos puntos.
function construir(): Record<string, Figura> {
  const r = azar(7)

  // 1 · Leyes: un cuerpo mineralizado bajo tierra y los sondajes que lo cruzan.
  const ley = (x: number, y: number, z: number) => {
    const a = Math.exp(-((x - 0.9) ** 2 / 4.5 + (y + 1.3) ** 2 / 1.5 + (z + 0.4) ** 2 / 4))
    const b = Math.exp(-((x + 1.8) ** 2 / 2 + (y + 0.1) ** 2 / 1.1 + (z - 1.2) ** 2 / 2))
    return Math.min(1, a + 0.75 * b)
  }
  const pl: V3[] = []
  const vl: number[] = []
  for (let i = 0; i < 2800; i++) {
    const x = (r() - 0.5) * 8
    const y = r() * 5 - 3.4
    const z = (r() - 0.5) * 8
    pl.push([x, y, z])
    vl.push(ley(x, y, z))
  }
  const malla: number[] = []
  for (let k = -4; k <= 4; k++) malla.push(k, 1.7, -4, k, 1.7, 4, -4, 1.7, k, 4, 1.7, k)
  const sondas: number[] = []
  for (const [x, z] of [[-2.6, 1.6], [-0.9, -2.3], [0.7, 0.3], [2.1, -1.0], [2.9, 2.4], [-1.9, -0.3], [1.0, 2.7]]) sondas.push(x, 1.7, z, x + 0.4, -3.4, z - 0.25)

  // 5 · Sismicidad: una galería y los sismos que se encadenan después de una tronadura.
  const arcos: number[] = []
  for (let k = 0; k < 9; k++) {
    const z = -4 + k
    for (let j = 0; j < 14; j++) {
      const a0 = (j / 14) * Math.PI
      const a1 = ((j + 1) / 14) * Math.PI
      arcos.push(Math.cos(a0) * 1.25, Math.sin(a0) * 1.25 - 0.9, z, Math.cos(a1) * 1.25, Math.sin(a1) * 1.25 - 0.9, z)
    }
  }
  const piso = [-1.25, -0.9, -4, -1.25, -0.9, 4, 1.25, -0.9, -4, 1.25, -0.9, 4]
  const focos = [[2.2, 1.6, -2.4, 0.4], [-2.4, 0.6, 0.5, 2.6], [1.6, -2.2, 2.2, 4.4], [-1.4, 2.4, 3.0, 6.0]]
  const ps: V3[] = []
  const ts: number[] = []
  for (let i = 0; i < 420; i++) {
    const f = focos[i % focos.length]
    const rr = 0.25 + r() * 1.5
    const a = r() * 6.283
    const b = Math.acos(2 * r() - 1)
    ps.push([f[0] + rr * Math.sin(b) * Math.cos(a), f[1] + rr * Math.cos(b), f[2] + rr * Math.sin(b) * Math.sin(a)])
    ts.push(f[3] - Math.log(1 - r() * 0.97) * 0.45) // réplicas: muchas al principio, cada vez menos
  }

  // 4 · Flota: el desgaste de cada equipo, lo ya visto y lo que podría venir.
  const pf: V3[] = []
  const uf: number[] = []
  const rf: number[] = []
  for (let c = 0; c < 11; c++) {
    const ritmo = 0.45 + r() * 1.0
    const curva = 1.6 + r() * 1.6
    const dato = r()
    for (let j = 0; j < 80; j++) {
      const q = j / 79
      const y = -2.9 + 5.6 * ritmo * (0.25 * q + 0.75 * q ** curva) + (r() - 0.5) * 0.09
      pf.push([-4.2 + 8.4 * q, y, 0])
      uf.push(q)
      rf.push(dato + (r() - 0.5) * 0.25)
    }
  }
  const umbral: number[] = []
  for (let k = 0; k < 21; k++) umbral.push(-4.2 + k * 0.4, 2.0, 0, -4.2 + k * 0.4 + 0.2, 2.0, 0)

  // 3 · Flotación: burbujas que suben en tres celdas y la espuma que se lleva el metal.
  const pb: V3[] = []
  const ab: V3[] = []
  const cajas: number[] = []
  for (let c = 0; c < 3; c++) {
    const x0 = -2.9 + c * 2.9
    cajas.push(x0 - 1.15, -2.9, 0, x0 - 1.15, 2.3, 0, x0 + 1.15, -2.9, 0, x0 + 1.15, 2.3, 0, x0 - 1.15, -2.9, 0, x0 + 1.15, -2.9, 0)
    for (let i = 0; i < 300; i++) {
      pb.push([x0 + (r() - 0.5) * 2.0, r() * 5.2, (r() - 0.5) * 1.2])
      ab.push([r(), r(), c / 2])
    }
  }

  // 2 · Taludes: un muro con sus bancos, el barrido del radar y una zona que empieza a moverse.
  const pt: V3[] = []
  const at: [number, number][] = []
  for (let f = 0; f < 34; f++) {
    for (let c = 0; c < 52; c++) {
      const ux = -4.1 + (c / 51) * 8.2 + (r() - 0.5) * 0.08
      const v = f / 33
      const banco = Math.floor(v * 5)
      const resto = v * 5 - banco
      const sube = (banco + paso(0, 1, (resto - 0.55) / 0.45)) / 5
      const dx = (ux - 0.9) / 1.9
      const dv = (v - 0.56) / 0.2
      pt.push([ux, -3.0 + sube * 5.6, 2.4 - v * 4.8])
      at.push([Math.exp(-(dx * dx + dv * dv)), r()])
    }
  }

  return {
    espacial: {
      escala: 0.95,
      rotacion: (t) => [0.36, 0.5 + t * 0.16, 0],
      lineas: [
        { v: malla, color: GRIS, opacidad: 0.55 },
        { v: sondas, color: '255,255,255', opacidad: 0.8 },
      ],
      puntos: (t, s) => {
        pl.forEach((p, i) => {
          const aV = vl[i]
          const late = 0.85 + 0.15 * Math.sin(t * 1.6 + p[0] * 0.9 + p[2] * 0.7)
          const color = aV < 0.45 ? mezcla([OXIDO[0] * 0.55, OXIDO[1] * 0.55, OXIDO[2] * 0.55], COBRE, aV / 0.45) : mezcla(COBRE, ORO, (aV - 0.45) / 0.55)
          s.push({ p, color, brillo: (0.22 + 1.15 * aV) * late, tamano: 0.085 + 0.24 * aV })
        })
      },
    },
    deformacion: {
      escala: 0.92,
      rotacion: (t) => [0.32, -0.5 + Math.sin(t * 0.2) * 0.12, 0],
      lineas: [],
      puntos: (t, s) => {
        const barrido = -4.4 + 8.8 * modulo(t * 0.13, 1)
        pt.forEach((q, i) => {
          const [zona] = at[i]
          const mueve = zona * (0.5 + 0.5 * Math.sin(t * 0.6))
          const dr = (q[0] - barrido) / 0.22
          const radar = Math.exp(-dr * dr)
          const base = mezcla(ARENA, ROJO, paso(0.15, 0.7, zona))
          s.push({
            p: [q[0], q[1] - 0.42 * mueve, q[2] + 0.42 * mueve],
            color: [base[0] + ORO[0] * radar * 0.9, base[1] + ORO[1] * radar * 0.9, base[2] + ORO[2] * radar * 0.9],
            brillo: 0.42 + 0.6 * zona + radar * 0.8,
            tamano: 0.085 + 0.07 * zona + 0.06 * radar,
          })
        })
      },
    },
    cinetica: {
      escala: 1.12,
      rotacion: () => [0, 0, 0],
      lineas: [{ v: cajas, color: GRIS, opacidad: 0.75 }],
      puntos: (t, s) => {
        pb.forEach((q, i) => {
          const b = ab[i]
          const sube = modulo(q[1] + t * (0.35 + 0.75 * b[0]), 5.2)
          const espuma = paso(4.1, 4.9, sube)
          s.push({
            p: [q[0] + Math.sin(t * 1.3 + b[1] * 30) * 0.07, sube - 2.9, q[2]],
            color: mezcla(OXIDO, mezcla(COBRE, ORO, b[2]), espuma),
            brillo: 0.28 + 0.9 * espuma,
            tamano: 0.07 + 0.11 * b[1] + 0.12 * espuma,
          })
        })
      },
    },
    desgaste: {
      escala: 0.95,
      rotacion: () => [0, 0, 0],
      lineas: [
        { v: umbral, color: '234,92,56', opacidad: 0.95 },
        { v: [-4.2, -3.1, 0, 4.2, -3.1, 0, -4.2, -3.1, 0, -4.2, 2.9, 0], color: GRIS, opacidad: 0.7 },
      ],
      puntos: (t, s) => {
        const ahora = 0.32 + 0.3 * (0.5 + 0.5 * Math.sin(t * 0.35))
        pf.forEach((q, i) => {
          const futuro = Math.max(uf[i] - ahora, 0)
          const y = q[1] + (rf[i] - 0.5) * futuro * 4.2 // el abanico de lo que podría pasar
          const falla = paso(1.7, 2.0, y)
          s.push({
            p: [q[0], y, q[2]],
            color: mezcla(mezcla(OXIDO, COBRE, acotar(y * 0.2 + 0.5, 0, 1)), ROJO, falla),
            brillo: futuro > 0 ? 0.26 + 0.5 * falla : 0.95,
            tamano: futuro > 0 ? 0.1 : 0.15,
          })
        })
      },
    },
    sismico: {
      escala: 1.12,
      rotacion: (t) => [0.3, 0.7 + Math.sin(t * 0.25) * 0.45, 0],
      lineas: [
        { v: arcos, color: GRIS, opacidad: 0.7 },
        { v: piso, color: GRIS, opacidad: 0.7 },
      ],
      puntos: (t, s) => {
        ps.forEach((p, i) => {
          const golpe = Math.exp(-modulo(t - ts[i], 7.6) * 1.7)
          s.push({ p, color: mezcla(COBRE, ORO, golpe), brillo: 0.22 + 1.5 * golpe, tamano: 0.09 + 0.46 * golpe })
        })
      },
    },
  }
}

let FIGURAS: Record<string, Figura> | null = null
const figuras = () => (FIGURAS ??= construir())

// Rotación con el orden de three.js (Euler XYZ): primero z, después y, después x.
function rotar([x, y, z]: V3, [rx, ry, rz]: [number, number, number]): V3 {
  const [cz, sz, cy, sy, cx, sx] = [Math.cos(rz), Math.sin(rz), Math.cos(ry), Math.sin(ry), Math.cos(rx), Math.sin(rx)]
  const x1 = x * cz - y * sz
  const y1 = x * sz + y * cz
  const x2 = x1 * cy + z * sy
  const z2 = -x1 * sy + z * cy
  return [x2, y1 * cx - z2 * sx, y1 * sx + z2 * cx]
}

function dibujar(ctx: CanvasRenderingContext2D, ancho: number, alto: number, figura: Figura, t: number, cola: Punto[]) {
  const focal = alto / ALTO_VISIBLE // píxeles por unidad de escena a la distancia de la cámara
  const rot = figura.rotacion(t)
  const proyectar = (p: V3) => {
    const [x, y, z] = rotar([p[0] * figura.escala, p[1] * figura.escala, p[2] * figura.escala], rot)
    const k = (focal * DISTANCIA) / (DISTANCIA - z)
    return { x: ancho / 2 + x * k, y: alto / 2 - (y + ALTURA_GRUPO) * k, k }
  }

  ctx.globalCompositeOperation = 'source-over'
  ctx.clearRect(0, 0, ancho, alto)
  ctx.lineWidth = 1
  for (const l of figura.lineas) {
    ctx.strokeStyle = `rgba(${l.color},${l.opacidad})`
    ctx.beginPath()
    for (let i = 0; i < l.v.length; i += 6) {
      const a = proyectar([l.v[i], l.v[i + 1], l.v[i + 2]])
      const b = proyectar([l.v[i + 3], l.v[i + 4], l.v[i + 5]])
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
    }
    ctx.stroke()
  }

  // La luz se suma, como el AdditiveBlending del deck.
  cola.length = 0
  figura.puntos(t, cola)
  ctx.globalCompositeOperation = 'lighter'
  for (const pt of cola) {
    if (pt.brillo < 0.004) continue
    const { x, y, k } = proyectar(pt.p)
    const d = Math.max(0.6, pt.tamano * k)
    const c = (v: number) => Math.round(255 * Math.min(1, v * pt.brillo * 0.8))
    ctx.fillStyle = `rgb(${c(pt.color[0])},${c(pt.color[1])},${c(pt.color[2])})`
    if (d < 2) {
      ctx.fillRect(x - d / 2, y - d / 2, d, d)
    } else {
      ctx.beginPath()
      ctx.arc(x, y, d / 2, 0, Math.PI * 2)
      ctx.fill()
    }
  }
  ctx.globalCompositeOperation = 'source-over'
}

export default function FiguraMina({ motor, className = '' }: { motor: string; className?: string }) {
  const ref = useRef<HTMLCanvasElement>(null)
  const existe = motor in figuras()

  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas?.getContext('2d')
    const figura = figuras()[motor]
    if (!canvas || !ctx || !figura) return
    const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const cola: Punto[] = []
    let visible = true
    let cuadro = 0
    const inicio = performance.now()

    const pintar = (ahora: number) => {
      const { width, height } = canvas.getBoundingClientRect()
      const dpr = Math.min(2, window.devicePixelRatio || 1)
      if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) {
        canvas.width = Math.round(width * dpr)
        canvas.height = Math.round(height * dpr)
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      dibujar(ctx, width, height, figura, quieto ? T_QUIETO : T_QUIETO + (ahora - inicio) / 1000, cola)
      if (!quieto && visible) cuadro = requestAnimationFrame(pintar)
    }

    // Fuera de la pantalla no se dibuja.
    const observador = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting
      cancelAnimationFrame(cuadro)
      if (visible) cuadro = requestAnimationFrame(pintar)
    })
    observador.observe(canvas)
    cuadro = requestAnimationFrame(pintar)
    return () => {
      observador.disconnect()
      cancelAnimationFrame(cuadro)
    }
  }, [motor])

  if (!existe) return <Ilustracion motor={motor} className={className} />
  return <canvas ref={ref} className={className} aria-hidden />
}
