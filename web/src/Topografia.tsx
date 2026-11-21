// El fondo de carta topográfica del deck: curvas de nivel tenues alrededor de dos cerros, con
// semilla fija. Va detrás de todo y no se lee: solo da el terreno.

import { memo } from 'react'

const ANCHO = 1600
const ALTO = 1000

// Un cerro: curvas cerradas cada vez más grandes, deformadas con dos ondas.
function cerro(cx: number, cy: number, r0: number, paso: number, n: number, fase: number): string[] {
  const curvas: string[] = []
  for (let k = 0; k < n; k++) {
    const r = r0 + k * paso
    const puntos: string[] = []
    for (let i = 0; i <= 96; i++) {
      const t = (i / 96) * Math.PI * 2
      const deforma = 1 + 0.16 * Math.sin(3 * t + fase + k * 0.21) + 0.07 * Math.sin(5 * t - fase * 1.7 + k * 0.13)
      const x = cx + Math.cos(t) * r * deforma * 1.25
      const y = cy + Math.sin(t) * r * deforma * 0.82
      puntos.push(`${x.toFixed(1)},${y.toFixed(1)}`)
    }
    curvas.push(`M${puntos.join('L')}Z`)
  }
  return curvas
}

const CURVAS = [...cerro(1180, 260, 40, 46, 16, 0.6), ...cerro(260, 860, 30, 52, 12, 2.1)]

function Topografia() {
  return (
    <svg
      className="pointer-events-none fixed inset-0 -z-10 h-full w-full"
      viewBox={`0 0 ${ANCHO} ${ALTO}`}
      preserveAspectRatio="xMidYMid slice"
      aria-hidden
    >
      <g fill="none" stroke="var(--color-curva)" strokeWidth="1.2">
        {CURVAS.map((d, i) => (
          <path key={i} d={d} strokeWidth={i % 5 === 4 ? 2 : 1.1} />
        ))}
      </g>
    </svg>
  )
}

export default memo(Topografia)
