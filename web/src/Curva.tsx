// La curva de una unidad (CONTRATO.md, sección 6): los puntos medidos, la línea de «ahora», el
// abanico de lo que Krylov cree que viene (bajo, medio, alto) y la línea del límite. Un abanico
// ancho es mucha duda.

import type { Curva as DatosCurva } from './tipos'

const W = 640
const H = 300
const M = { izq: 52, der: 18, arr: 18, aba: 40 }

// Marcas «redondas» del eje: 4 a 6 valores.
function marcas(min: number, max: number): number[] {
  const crudo = (max - min) / 5
  const potencia = 10 ** Math.floor(Math.log10(crudo))
  const paso = [1, 2, 5, 10].map((m) => m * potencia).find((p) => p >= crudo) ?? crudo
  const salida: number[] = []
  for (let v = Math.ceil(min / paso) * paso; v <= max + 1e-9; v += paso) salida.push(Number(v.toFixed(6)))
  return salida
}

const numero = (v: number) => v.toLocaleString('es-CL', { maximumFractionDigits: 2 })

export default function Curva({ curva, titulo }: { curva: DatosCurva; titulo?: string }) {
  const { t, y, ahora, t_banda, bajo, medio, alto, limite, eje_t, eje_y, marca } = curva
  const ts = [...t, ...t_banda]
  const ys = [...y, ...bajo, ...alto, ...(limite !== null ? [limite] : [])]
  const t0 = Math.min(...ts)
  const t1 = Math.max(...ts)
  const rango = Math.max(...ys) - Math.min(...ys) || 1
  const y0 = Math.min(...ys) - rango * 0.08
  const y1 = Math.max(...ys) + rango * 0.08

  const px = (v: number) => M.izq + ((v - t0) / (t1 - t0 || 1)) * (W - M.izq - M.der)
  const py = (v: number) => H - M.aba - ((v - y0) / (y1 - y0)) * (H - M.arr - M.aba)
  const linea = (xs: number[], vs: number[]) => xs.map((x, i) => `${i ? 'L' : 'M'}${px(x).toFixed(1)},${py(vs[i]).toFixed(1)}`).join('')
  const abanico =
    linea(t_banda, alto) +
    t_banda
      .map((_, i) => t_banda.length - 1 - i)
      .map((i) => `L${px(t_banda[i]).toFixed(1)},${py(bajo[i]).toFixed(1)}`)
      .join('') +
    'Z'

  return (
    <figure className="flex min-h-0 flex-col">
      {titulo && <figcaption className="mb-1 text-sm text-tinta-suave">{titulo}</figcaption>}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${eje_y} según ${eje_t.toLowerCase()}, con lo que Krylov cree que viene`}>
        <g className="font-mono" fontSize="11" fill="var(--color-tenue)">
          {marcas(y0, y1).map((v) => (
            <g key={v}>
              <line x1={M.izq} x2={W - M.der} y1={py(v)} y2={py(v)} stroke="var(--color-linea)" strokeWidth={1} />
              <text x={M.izq - 8} y={py(v) + 4} textAnchor="end">
                {numero(v)}
              </text>
            </g>
          ))}
          {marcas(t0, t1).map((v) => (
            <text key={v} x={px(v)} y={H - M.aba + 18} textAnchor="middle">
              {numero(v)}
            </text>
          ))}
          <text x={W - M.der} y={H - 4} textAnchor="end" fill="var(--color-tinta-suave)">
            {eje_t}
          </text>
        </g>

        {/* Lo que viene: el abanico y su línea media. */}
        <path d={abanico} fill="var(--abanico)" fillOpacity={0.22} />
        <path d={linea(t_banda, alto)} fill="none" stroke="var(--abanico)" strokeOpacity={0.55} strokeWidth={1} />
        <path d={linea(t_banda, bajo)} fill="none" stroke="var(--abanico)" strokeOpacity={0.55} strokeWidth={1} />
        <path d={linea(t_banda, medio)} fill="none" stroke="var(--abanico)" strokeWidth={2} strokeDasharray="5 4" />

        {/* Ahora. */}
        <line x1={px(ahora)} x2={px(ahora)} y1={M.arr - 6} y2={H - M.aba} stroke="var(--color-tinta-suave)" strokeWidth={1} />
        <text x={px(ahora) - 6} y={M.arr + 4} textAnchor="end" className="font-mono" fontSize="11" fill="var(--color-tinta-suave)">
          AHORA
        </text>

        {/* Lo medido. */}
        <path d={linea(t, y)} fill="none" stroke="var(--color-tinta)" strokeOpacity={0.35} strokeWidth={1} />
        {t.map((x, i) => (
          <circle key={i} cx={px(x)} cy={py(y[i])} r={2.6} fill="var(--color-tinta)" />
        ))}

        {/* El límite, grueso. */}
        {limite !== null && (
          <g>
            <line x1={M.izq} x2={W - M.der} y1={py(limite)} y2={py(limite)} stroke="var(--color-actuar)" strokeWidth={3} />
            <text x={M.izq + 6} y={py(limite) - 7} className="font-mono" fontSize="11" fill="var(--color-actuar)">
              LÍMITE
            </text>
          </g>
        )}
      </svg>
      <div className="mt-1 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <span className="text-sm text-tinta-suave">{eje_y}</span>
        {marca && <span className="font-medium text-cobre">{marca.texto}</span>}
      </div>
    </figure>
  )
}
