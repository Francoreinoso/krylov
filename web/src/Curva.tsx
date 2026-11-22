// La curva de una unidad (CONTRATO.md, sección 6): los puntos medidos, la línea de «ahora», el
// abanico de lo que Krylov cree que viene (bajo, medio, alto) y la línea del límite. Un abanico
// ancho es mucha duda. Tiene que leerse desde la última fila: textos grandes y pocas marcas.
// Los rótulos salen de casos/textos.yaml (`textos`); sin ellos, la curva se dibuja sin rótulos.

import { useId } from 'react'
import { FONDO } from './colores'
import type { Curva as DatosCurva, Estado, Textos, Unidad } from './tipos'

export type TextosCurva = Textos['curva']

const W = 640
const H = 330
const LETRA = 17
const M = { izq: 66, der: 22, arr: 60, aba: 58 }

// Marcas «redondas» del eje: 3 a 5 valores, para que no se pisen.
function marcas(min: number, max: number): number[] {
  if (!(max > min)) return [min]
  const crudo = (max - min) / 4
  const potencia = 10 ** Math.floor(Math.log10(crudo))
  const paso = [1, 2, 2.5, 5, 10].map((m) => m * potencia).find((p) => p >= crudo) ?? crudo
  const salida: number[] = []
  for (let v = Math.ceil(min / paso) * paso; v <= max + 1e-9; v += paso) salida.push(Number(v.toFixed(6)))
  return salida
}

// Una flecha hacia arriba con la punta en (x, y): el abanico sigue más allá del borde.
const flecha = (x: number, y: number) => `M${x.toFixed(1)},${(y - 12).toFixed(1)}L${(x + 9).toFixed(1)},${y.toFixed(1)}L${(x - 9).toFixed(1)},${y.toFixed(1)}Z`

const numero = (v: number) => v.toLocaleString('es-CL', { maximumFractionDigits: 2 })
const ancho = (texto: string) => texto.length * LETRA * 0.55 // aproximado, para no salirse del borde

interface Props {
  curva: DatosCurva
  textos: TextosCurva | null
  escalones?: boolean // un conteo acumulado (temblores): lo medido va en escalones hasta «ahora»
}

export default function Curva({ curva, textos, escalones = false }: Props) {
  const { t, y, ahora, t_banda, bajo, medio, alto, limite, eje_t, eje_y, marca } = curva
  const ts = [...t, ...t_banda, ahora]
  // El límite siempre queda dentro del eje: es la referencia que importa.
  const referencia = [...y, ...(limite !== null ? [limite] : [])]
  // Un abanico que se dispara (un muro que se acelera: de 10 a 110 mm) aplastaría lo medido contra
  // el fondo. Si sale a más del doble del rango medido, el eje se corta a un rango por encima (o por
  // debajo), el abanico se recorta al gráfico y una flecha marca que sigue.
  const refMin = Math.min(...referencia)
  const refMax = Math.max(...referencia)
  const refRango = refMax - refMin || Math.abs(refMax) || 1
  const seDispara = (v: number) => v > refMax + 2 * refRango || v < refMin - 2 * refRango
  const recortar = [...bajo, ...alto].some(seDispara)
  const acotar = (v: number) => (recortar ? Math.min(refMax + refRango, Math.max(refMin - refRango, v)) : v)
  const ys = [...referencia, ...bajo.map(acotar), ...alto.map(acotar)]
  const t0 = Math.min(...ts)
  const t1 = Math.max(...ts)
  const minimo = Math.min(...ys)
  const rango = Math.max(...ys) - minimo || 1
  const y0 = minimo >= 0 ? Math.max(0, minimo - rango * 0.08) : minimo - rango * 0.08
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
  const medido = escalones
    ? t.map((x, i) => (i ? `H${px(x).toFixed(1)}V${py(y[i]).toFixed(1)}` : `M${px(x).toFixed(1)},${py(y[i]).toFixed(1)}`)).join('') + `H${px(ahora).toFixed(1)}`
    : linea(t, y)

  // El rótulo de «ahora» va a la izquierda de su línea; si no cabe, a la derecha.
  const xHoy = px(ahora)
  const hoyALaDerecha = textos !== null && xHoy - 8 - ancho(textos.ahora) < M.izq
  // El límite, encima de su línea; si choca con el borde de arriba, debajo.
  const yLimite = limite !== null ? (py(limite) - 10 - LETRA < M.arr - 6 ? py(limite) + LETRA + 8 : py(limite) - 10) : 0
  // Cuánto falta (taludes): una franja tenue, recortada al final del eje; sin estirarlo.
  const franja = marca && ahora + marca.bajo <= t1 ? { x0: px(ahora + marca.bajo), x1: px(Math.min(ahora + marca.alto, t1)) } : null
  // Dónde el abanico sale por arriba del gráfico (el primer punto de `alto` fuera del eje).
  const salida = recortar ? t_banda.find((_, i) => alto[i] > y1) : undefined
  const recorte = `curva-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`

  return (
    <figure className="flex min-h-0 flex-col">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label={`${textos ? `${textos.titulo}. ` : ''}${eje_y} · ${eje_t}`}
      >
        {/* Los nombres de los ejes, dentro del dibujo: el vertical arriba a la izquierda, el del tiempo abajo a la derecha. */}
        <text x={4} y={LETRA + 4} fontSize={LETRA + 1} fill="var(--color-tinta-suave)">
          {eje_y}
        </text>
        <text x={W - M.der} y={H - 6} textAnchor="end" fontSize={LETRA + 1} fill="var(--color-tinta-suave)">
          {eje_t}
        </text>

        <g className="font-mono" fontSize={LETRA - 1} fill="var(--color-tenue)">
          {marcas(y0, y1).map((v) => (
            <g key={v}>
              <line x1={M.izq} x2={W - M.der} y1={py(v)} y2={py(v)} stroke="var(--color-linea)" strokeWidth={1} />
              <text x={M.izq - 8} y={py(v) + 5} textAnchor="end">
                {numero(v)}
              </text>
            </g>
          ))}
          {marcas(t0, t1).map((v) => (
            <text key={v} x={px(v)} y={H - M.aba + 24} textAnchor="middle">
              {numero(v)}
            </text>
          ))}
        </g>

        {franja && <rect x={franja.x0} y={M.arr} width={Math.max(2, franja.x1 - franja.x0)} height={H - M.arr - M.aba} fill="var(--color-actuar)" fillOpacity={0.14} />}

        {/* Lo que viene: el abanico y su línea media, recortados al gráfico. */}
        <clipPath id={recorte}>
          <rect x={M.izq} y={M.arr} width={W - M.izq - M.der} height={H - M.arr - M.aba} />
        </clipPath>
        <g clipPath={`url(#${recorte})`}>
          <path d={abanico} fill="var(--abanico)" fillOpacity={0.35} />
          <path d={linea(t_banda, alto)} fill="none" stroke="var(--abanico)" strokeWidth={2} />
          <path d={linea(t_banda, bajo)} fill="none" stroke="var(--abanico)" strokeWidth={2} />
          <path d={linea(t_banda, medio)} fill="none" stroke="var(--abanico)" strokeWidth={3} strokeDasharray="7 5" />
        </g>
        {salida !== undefined && <path d={flecha(px(salida), M.arr)} fill="var(--abanico)" />}

        {/* La línea de «ahora». */}
        <line x1={xHoy} x2={xHoy} y1={M.arr - 14} y2={H - M.aba} stroke="var(--color-tinta-suave)" strokeWidth={2} strokeDasharray="5 4" />
        {textos && (
          <text
            x={hoyALaDerecha ? xHoy + 8 : xHoy - 8}
            y={M.arr - 18}
            textAnchor={hoyALaDerecha ? 'start' : 'end'}
            fontSize={LETRA + 1}
            fontWeight={600}
            fill="var(--color-tinta)"
          >
            {textos.ahora}
          </text>
        )}

        {/* Lo medido. */}
        <path d={medido} fill="none" stroke="var(--color-tinta)" strokeOpacity={0.65} strokeWidth={2} />
        {t.map((x, i) => (
          <circle key={i} cx={px(x)} cy={py(y[i])} r={4} fill="var(--color-tinta)" />
        ))}

        {/* El límite, grueso. */}
        {limite !== null && (
          <g>
            <line x1={M.izq} x2={W - M.der} y1={py(limite)} y2={py(limite)} stroke="var(--color-actuar)" strokeWidth={4} />
            {textos && (
              <text x={M.izq + 8} y={yLimite} fontSize={LETRA + 1} fontWeight={600} fill="var(--color-actuar)">
                {textos.limite}
              </text>
            )}
          </g>
        )}
      </svg>
      {textos && (
        <figcaption className="mt-2 flex flex-wrap gap-x-6 gap-y-1 text-sm text-tinta-suave">
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 shrink-0 rounded-full bg-tinta" />
            {textos.medido}
          </span>
          <span className="flex items-start gap-2">
            <span className="mt-1 h-3 w-5 shrink-0" style={{ backgroundColor: 'var(--abanico)', opacity: 0.7 }} />
            <span>{textos.abanico}</span>
          </span>
          {salida !== undefined && textos.fuera && (
            <span className="flex items-start gap-2">
              <svg viewBox="0 0 20 14" className="mt-0.5 h-3.5 w-5 shrink-0" aria-hidden>
                <path d={flecha(10, 13)} fill="var(--abanico)" />
              </svg>
              <span>{textos.fuera}</span>
            </span>
          )}
        </figcaption>
      )}
    </figure>
  )
}

// Arriba el nombre de la unidad, su decisión y, si viene, cuánto falta en grande; abajo su curva.
export function CurvaDeUnidad({
  unidad,
  estado,
  rotulo,
  textos,
  escalones,
}: {
  unidad: Unidad | null
  estado: Estado | null
  rotulo: string | null
  textos: TextosCurva | null
  escalones: boolean
}) {
  if (!unidad?.curva) return null
  const { marca } = unidad.curva
  return (
    <div>
      <p className="mb-2 flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="titular text-3xl">{unidad.etiqueta}</span>
        {estado && rotulo && (
          <span className="flex items-center gap-2 text-tinta-suave">
            <span className={`h-3 w-5 ${FONDO[estado]}`} />
            {rotulo}
          </span>
        )}
        {marca && <span className="titular text-3xl text-actuar">{marca.texto}</span>}
      </p>
      <Curva curva={unidad.curva} textos={textos} escalones={escalones} />
    </div>
  )
}
