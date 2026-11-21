// Un dibujo chico por motor, como los de la lámina 7 del deck: lo que mira cada decisión. Son
// ilustraciones con semilla fija, no datos.

import { memo } from 'react'

// Generador con semilla fija (mulberry32): el dibujo es el mismo en cada carga.
function azar(semilla: number) {
  let a = semilla
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// Normal aproximada: suma de tres uniformes.
const normal = (r: () => number) => (r() + r() + r() - 1.5) / 1.5

const W = 200
const H = 120
const ORO = 'var(--color-oro)'
const OXIDO = 'var(--color-oxido)'
const COBRE = 'var(--color-cobre)'
const ROJO = 'var(--color-actuar)'
const LINEA = 'var(--color-tinta-suave)'

// Leyes: una malla en perspectiva, pozos verticales y una nube de arsénico.
function Espacial() {
  const r = azar(7)
  const malla = []
  for (let i = 0; i <= 6; i++) {
    const t = i / 6
    malla.push(<line key={`a${i}`} x1={20 + t * 120} y1={30 - t * 10} x2={60 + t * 120} y2={60 - t * 10} />)
    malla.push(<line key={`b${i}`} x1={20 + t * 40} y1={30 + t * 30} x2={140 + t * 40} y2={20 + t * 30} />)
  }
  const pozos = [40, 70, 98, 128, 156].map((x, i) => <line key={i} x1={x} y1={30 + (i % 2) * 8} x2={x} y2={100 + (i % 3) * 5} />)
  const nube = Array.from({ length: 110 }, (_, i) => {
    const x = 100 + normal(r) * 45
    const y = 72 + normal(r) * 16
    const cerca = Math.hypot((x - 100) / 45, (y - 72) / 16)
    return <circle key={i} cx={x} cy={y} r={cerca < 0.6 ? 1.8 : 1.1} fill={cerca < 0.7 ? ORO : OXIDO} opacity={cerca < 0.7 ? 0.9 : 0.55} />
  })
  return (
    <>
      <g stroke={LINEA} strokeOpacity={0.45} strokeWidth={0.6}>
        {malla}
      </g>
      {nube}
      <g stroke={LINEA} strokeOpacity={0.7} strokeWidth={0.8}>
        {pozos}
      </g>
    </>
  )
}

// Taludes: las filas del radar sobre el muro; un tramo que se mueve más, en rojo.
function Deformacion() {
  const r = azar(11)
  const filas = []
  for (let f = 0; f < 9; f++) {
    for (let i = 0; i < 40; i++) {
      const x = 20 + f * 4 + i * 4
      const y = 18 + f * 10 - i * 0.6
      const enTramo = i > 14 && i < 26 && f > 2 && f < 6
      const brillo = i === 3 + f || enTramo
      filas.push(
        <circle
          key={`${f}-${i}`}
          cx={x}
          cy={y + (enTramo ? normal(r) * 1.2 : 0)}
          r={brillo ? 1.4 : 0.8}
          fill={enTramo ? ROJO : brillo ? ORO : LINEA}
          opacity={enTramo ? 0.85 : brillo ? 0.95 : 0.35}
        />,
      )
    }
  }
  return <>{filas}</>
}

// Flotación: tres celdas; el cobre sube con las burbujas y lo demás se hunde.
function Cinetica() {
  const r = azar(23)
  const celdas = [0, 1, 2].map((c) => {
    const x0 = 34 + c * 48
    const puntos = Array.from({ length: 60 }, (_, i) => {
      const arriba = i < 22
      const y = arriba ? 16 + r() * 10 : 30 + r() * 78
      return <circle key={i} cx={x0 + 3 + r() * 34} cy={y} r={arriba ? 1.5 + r() * 1.6 : 1} fill={arriba ? ORO : OXIDO} opacity={arriba ? 0.9 : 0.45} />
    })
    return (
      <g key={c}>
        <rect x={x0} y={12} width={40} height={100} fill="none" stroke={LINEA} strokeOpacity={0.5} strokeWidth={0.7} />
        {puntos}
      </g>
    )
  })
  return <>{celdas}</>
}

// Flota: un abanico de desgaste que sube hacia la línea del límite.
function Desgaste() {
  const r = azar(31)
  const curvas = Array.from({ length: 14 }, (_, k) => {
    const g = 0.6 + r() * 1.4
    let d = 'M40,104'
    for (let i = 1; i <= 30; i++) {
      const t = i / 30
      d += `L${40 + t * 140},${104 - 70 * Math.pow(t, 1.8) * g}`
    }
    return <path key={k} d={d} fill="none" stroke={g > 1.35 ? COBRE : OXIDO} strokeWidth={0.8} opacity={0.75} />
  })
  return (
    <>
      <path d="M40,14V104H184" fill="none" stroke={LINEA} strokeOpacity={0.6} strokeWidth={0.7} />
      <line x1={40} y1={36} x2={184} y2={36} stroke={ROJO} strokeDasharray="3 3" strokeWidth={0.9} />
      {curvas}
    </>
  )
}

// Sismicidad: un racimo de sismos sobre los túneles.
function Sismico() {
  const r = azar(41)
  const racimo = Array.from({ length: 36 }, (_, i) => (
    <circle key={i} cx={78 + normal(r) * 22} cy={38 + normal(r) * 14} r={1 + r() * 3.2} fill={ORO} opacity={0.35 + r() * 0.6} />
  ))
  const sueltos = Array.from({ length: 40 }, (_, i) => <circle key={i} cx={120 + r() * 70} cy={20 + r() * 60} r={0.8} fill={COBRE} opacity={0.4} />)
  const tuneles = Array.from({ length: 8 }, (_, i) => {
    const x = 34 + i * 18
    return <path key={i} d={`M${x},${104 - i * 2}v-12a7,7 0 0 1 14,0v12`} />
  })
  return (
    <>
      {racimo}
      {sueltos}
      <g fill="none" stroke={LINEA} strokeOpacity={0.6} strokeWidth={0.7}>
        <path d="M28,106L182,90" />
        {tuneles}
      </g>
    </>
  )
}

const DIBUJO: Record<string, () => React.JSX.Element> = {
  espacial: Espacial,
  deformacion: Deformacion,
  cinetica: Cinetica,
  desgaste: Desgaste,
  sismico: Sismico,
}

function Ilustracion({ motor, className = '' }: { motor: string; className?: string }) {
  const Dibujo = DIBUJO[motor]
  if (!Dibujo) return null
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className={className} aria-hidden>
      <Dibujo />
    </svg>
  )
}

export default memo(Ilustracion)
