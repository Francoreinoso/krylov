// Dónde queda cada fila del archivo en la tarjeta de la coreografía, de 0 a 1: como un mapa si las columnas dicen dónde
// se midió (x, y), o como una serie por unidad si dicen cuándo (unidad, tiempo, valor). Sale de las filas de verdad: las
// del archivo que se subió, o las de la respuesta del demo.

import type { Orden } from './Coreografia'
import { numeros, textos, type InfoCsv } from './csv'
import type { Analisis } from './tipos'

type Punto = { x: number; y: number }

const escala = (v: number[]) => {
  const ok = v.filter(Number.isFinite)
  const min = Math.min(...ok)
  const max = Math.max(...ok)
  return (x: number) => (Number.isFinite(x) && max > min ? (x - min) / (max - min) : 0.5)
}

// Un mapa: x hacia la derecha, y hacia arriba, con la misma escala en los dos ejes.
function mapa(xs: number[], ys: number[]): Orden {
  const ok = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y))
  if (ok.length < 2) return null
  const [x0, x1] = [Math.min(...ok.map((p) => p[0])), Math.max(...ok.map((p) => p[0]))]
  const [y0, y1] = [Math.min(...ok.map((p) => p[1])), Math.max(...ok.map((p) => p[1]))]
  const lado = Math.max(x1 - x0, y1 - y0) || 1
  const dx = (lado - (x1 - x0)) / 2
  const dy = (lado - (y1 - y0)) / 2
  return xs.map((x, i) => (Number.isFinite(x) && Number.isFinite(ys[i]) ? { x: (x - x0 + dx) / lado, y: 1 - (ys[i] - y0 + dy) / lado } : { x: 0.5, y: 0.5 }))
}

// Las series: una franja por unidad, el tiempo hacia la derecha y el valor hacia arriba dentro de su franja.
function series(unidades: string[], ts: number[], vs: number[]): Orden {
  const ids = [...new Set(unidades)]
  if (ids.length < 1 || ts.every((t) => !Number.isFinite(t))) return null
  const franja = 1 / ids.length
  const t = escala(ts)
  const v = escala(vs)
  const fila = new Map(ids.map((id, i) => [id, i]))
  return unidades.map((u, i): Punto => ({ x: t(ts[i]), y: (fila.get(u)! + 1 - 0.15 - v(vs[i]) * 0.7) * franja }))
}

// Con el calce confirmado (o propuesto): el papel → la columna del archivo.
export function ordenDelArchivo(info: InfoCsv, columnaDe: Record<string, string | undefined>): Orden {
  if (columnaDe.x && columnaDe.y) return mapa(numeros(info, columnaDe.x), numeros(info, columnaDe.y))
  if (columnaDe.este && columnaDe.norte) return mapa(numeros(info, columnaDe.este), numeros(info, columnaDe.norte)) // el yacimiento, visto desde arriba
  if (columnaDe.unidad && columnaDe.tiempo && columnaDe.valor)
    return series(textos(info, columnaDe.unidad), numeros(info, columnaDe.tiempo), numeros(info, columnaDe.valor))
  return null
}

// Con una respuesta del motor: sus muestras (mapa) o lo que se leyó de cada unidad (series).
export function ordenDeRespuesta(a: Analisis): { n: number; orden: Orden } {
  if (a.mapa) {
    const p = a.mapa.puntos
    return { n: p.length, orden: mapa(p.map((q) => q.x), p.map((q) => q.y)) }
  }
  const filas = (a.unidades ?? []).flatMap((u) => (u.serie ?? u.curva?.t.map((t, i) => [t, u.curva!.y[i]] as [number, number]) ?? []).map(([t, v]) => ({ u: u.id, t, v })))
  return { n: filas.length, orden: series(filas.map((f) => f.u), filas.map((f) => f.t), filas.map((f) => f.v)) }
}
