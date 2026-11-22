// De una respuesta de Krylov a los datos que lee una lámina del deck (`window.KRYLOV_DATOS`), con la misma forma que
// escribe pitch/deck/datos/generar.py. Aquí no se calcula ningún intervalo: todo viene de la respuesta del motor.
// Solo se arma la escena si la respuesta trae lo que la tarjeta dibuja (los campos de D-42); si no, la app muestra
// su respaldo.

import { decidirEspacial, UMBRAL_DE_DUDA, type Decision } from '../decision'
import type { Analisis, DondeMedir, Estado } from '../tipos'
import type { Lamina } from './protocolo'

const NUMERO: Record<Estado, number> = { no_actuar: 0, en_duda: 1, actuar: 2 } // el orden de generar.py

// Los segundos que tardó «¿Dónde perforo?» en el computador libre, medidos (M-44). Es lo que dice el deck.
export const DONDE_PERFORO_S = 1.3

// Las cinco láminas de decisión del deck, por el nombre del caso.
export const LAMINA_DE: Record<string, Lamina> = { leyes: 'leyes', taludes: 'taludes', flotacion: 'flotacion', flota: 'flota', sismicidad: 'sismicidad' }

// Una capa del terreno (el mapa entero, o el que sale de una muestra más), sobre los bloques que tienen dato.
export interface Capa {
  media: number[]
  alto: number[]
  bajo: number[]
  p: number[]
  estado: number[]
}

// `bloques`: las decisiones con los costos que puso el usuario (useDecision); sin ellas, con los del caso.
export function capaDe(a: Analisis, bloques: (Decision | null)[] | null = null): Capa | null {
  const m = a.mapa
  if (!m?.alto || !m.bajo) return null
  const dentro = m.media.flatMap((v, i) => (v == null ? [] : [i]))
  const decision = (i: number) => bloques?.[i] ?? decidirEspacial(m.p[i] ?? 0, a.costos.falso_si.valor, a.costos.falso_no.valor)
  return {
    media: dentro.map((i) => m.media[i]!),
    alto: dentro.map((i) => m.alto![i] ?? m.media[i]!),
    bajo: dentro.map((i) => m.bajo![i] ?? m.media[i]!),
    p: dentro.map((i) => m.p[i] ?? 0),
    estado: dentro.map((i) => NUMERO[decision(i).estado]),
  }
}

// Las decisiones de esta escena: las del motor o las recalculadas con otros costos.
export interface Decisiones {
  corte: number
  bloques: (Decision | null)[] | null
  unidades: Decision[] | null
}

// ¿Esta respuesta se puede dibujar en la escena de su lámina?
export function hayEscena(a: Analisis): boolean {
  if (a.semaforo.estado.startsWith('rojo') || !LAMINA_DE[a.caso]) return false
  if (a.mapa) return capaDe(a) !== null
  const u = a.unidades ?? []
  return a.escena !== undefined && u.length > 0 && u.every((x) => x.serie) && u.some((x) => x.posteriori)
}

const costos = (a: Analisis) => ({ falso_si: a.costos.falso_si.valor, falso_no: a.costos.falso_no.valor })

function terreno(a: Analisis, donde: DondeMedir | null, d: Decisiones | null) {
  const m = a.mapa!
  const capa = capaDe(a, d?.bloques ?? null)!
  const dentro = m.media.flatMap((v, i) => (v == null ? [] : [i]))
  // Un archivo propio no trae «¿Dónde perforo?»: la escena del deck igual arma sus tres lugares (A, B y C), que aquí
  // no se muestran nunca (ese paso no se ofrece sin «¿Dónde perforo?»).
  const relleno = ['A', 'B', 'C'].map((etiqueta, i) => ({ etiqueta, puesto: i + 1, x: m.x0 + (m.nx * m.lado * (i + 1)) / 4, y: m.y0 + (m.ny * m.lado) / 2, valor_de_medir: 1 }))
  const candidatas = donde?.candidatas.length ? donde.candidatas : relleno
  const lugares = donde?.lugares?.length ? donde.lugares : candidatas.map(({ x, y, valor_de_medir }) => ({ x, y, valor_de_medir }))
  return {
    terreno: {
      caso: a.caso, nx: m.nx, ny: m.ny, x0: m.x0, y0: m.y0, lado: m.lado, umbral: m.umbral, unidad_valor: m.unidad_valor,
      punto_de_corte: d?.corte ?? a.punto_de_corte, dentro, ...capa, colores: a.resumen_colores, costo_de_no_saber: a.costo_de_no_saber?.valor ?? null,
      puntos: m.puntos.map((p) => [p.x, p.y, p.valor]), orilla: [], costos: costos(a), rotulos: a.rotulos, unidad: a.unidad,
      examen: a.examen?.tramos[0] ?? null, origen_datos: a.origen_datos, sintetico: a.sintetico, umbral_de_duda: UMBRAL_DE_DUDA,
      implementacion: a.implementacion, precalculado: a.precalculado,
    },
    donde: {
      candidatas, lugares, n_lugares: lugares.length, analisis_rehechos: donde?.analisis_rehechos ?? 0,
      implementacion: a.implementacion, precalculado: donde?.precalculado ?? false,
    },
    mediciones: {},
    series: {},
  }
}

function serie(a: Analisis, d: Decisiones | null) {
  const unidades = a.unidades ?? []
  const estado = (i: number) => d?.unidades?.[i]?.estado ?? unidades[i].estado
  return {
    terreno: null,
    series: {
      [a.caso]: {
        caso: a.caso, unidad: a.unidad, rotulos: a.rotulos, ...a.escena,
        unidades: unidades.map((u) => ({ id: u.id, puntos: u.serie ?? [] })),
        lecturas: unidades.reduce((n, u) => n + (u.serie?.length ?? 0), 0),
        verdad: {},
        respuesta: {
          implementacion: a.implementacion, precalculado: a.precalculado, colores: a.resumen_colores,
          costo_de_no_saber: a.costo_de_no_saber?.valor ?? null, costos: costos(a), examen: a.examen, titular: a.titular,
          sello_pasa: a.implementacion === 'red', punto_de_corte: d?.corte ?? a.punto_de_corte,
          unidades: Object.fromEntries(unidades.map((u, i) => [u.id, { estado: estado(i), p: u.p, rango: [u.rango_bajo, u.rango_alto], curva: u.curva ?? null }])),
          posteriori: Object.fromEntries(unidades.flatMap((u) => (u.posteriori ? [[u.id, u.posteriori]] : []))),
        },
      },
    },
  }
}

// Los datos de la lámina de esta respuesta. `donde`: «¿Dónde perforo?» del caso, si se pidió.
export function datosDeEscena(a: Analisis, donde: DondeMedir | null = null, d: Decisiones | null = null) {
  return a.mapa ? terreno(a, donde, d) : serie(a, d)
}

// Lo que el deck toma de su config.js y que una lámina de la app también lee.
export function configDeEscena(donde: DondeMedir | null) {
  // En vivo, lo que tardó esta vez; guardado (el demo sin servidor), lo medido con el computador libre.
  const s = donde?.tiempo_ms && !donde.precalculado ? donde.tiempo_ms / 1000 : DONDE_PERFORO_S
  return { demo: { url: '', texto: '' }, equipo: [], tiempos: {}, cifras: { donde_perforo_s: Math.round(s * 10) / 10 } }
}
