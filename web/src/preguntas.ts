// Las preguntas que sabe responder cada motor, y cómo se reconoce una escrita a mano: palabras
// clave, sin modelo de lenguaje (AGENTS.md, regla 11). Ningún texto de industria: la pregunta
// principal es el título del caso.

import type { Caso } from './tipos'

export type Intencion = 'decidir' | 'costo' | 'que_pesa' | 'examen' | 'donde_medir'

export interface Pregunta {
  intencion: Intencion
  texto: string
}

// Lo que hace cada motor, en palabras de pantalla (GLOSARIO.md).
export const MOTOR_EN_PALABRAS: Record<string, string> = {
  supervivencia: 'Cuánto tarda en pasar algo, aunque muchos casos sigan abiertos',
  jerarquico: 'Cada unidad y cada grupo con su propia tendencia',
  estados: 'Estados que no se ven, mes a mes',
  espacial: 'Datos con ubicación: qué manda y dónde medir',
}

export function preguntasDe(caso: Caso): Pregunta[] {
  const espacial = caso.motor === 'espacial'
  return [
    { intencion: 'decidir', texto: caso.titulo },
    { intencion: 'costo', texto: '¿Cuánto me cuesta no saber?' },
    { intencion: 'que_pesa', texto: espacial ? '¿Qué manda en el terreno?' : '¿Qué pesa?' },
    { intencion: 'examen', texto: '¿Qué tan bien le fue a Krylov?' },
    ...(espacial ? [{ intencion: 'donde_medir' as const, texto: '¿Dónde mido?' }] : []),
  ]
}

export const normalizar = (texto: string) =>
  texto.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[¿?¡!.,;:]/g, ' ')

const CLAVES: [Intencion, RegExp][] = [
  ['donde_medir', /\b(medir|mido|medicion|muestre|muestreo)/],
  ['examen', /\b(examen|acierta|acerto|confia|exact|precis|calibr)|bien le fue|que tan bien/],
  ['que_pesa', /\b(pesa|importa|factor|influye|manda|explica|por que|causa)/],
  ['costo', /\b(cuesta|cuanto vale|plata|costo|dinero|no saber|averiguar)/],
  ['decidir', /\b(conviene|quien|quienes|cuales|que hago|decid|actuar|recomiend|riesgo|prioriz)/],
]

// Un número elige la pregunta con ese puesto; si no, gana la primera intención que calce.
export function interpretar(texto: string, preguntas: Pregunta[]): Intencion | null {
  const n = Number(texto.trim())
  if (Number.isInteger(n) && n >= 1 && n <= preguntas.length) return preguntas[n - 1].intencion
  const limpio = normalizar(texto)
  const disponibles = new Set(preguntas.map((p) => p.intencion))
  for (const [intencion, patron] of CLAVES) {
    if (disponibles.has(intencion) && patron.test(limpio)) return intencion
  }
  // Las palabras largas del título del caso también cuentan como «decidir».
  const titulo = normalizar(preguntas[0].texto).split(/\s+/).filter((p) => p.length > 4)
  return titulo.some((p) => limpio.includes(p)) ? 'decidir' : null
}

// Elige un caso por lo que se escribió: su número, su nombre, su motor o una palabra de su título.
export function elegirCaso(texto: string, casos: Caso[]): Caso | null {
  const n = Number(texto.trim())
  if (Number.isInteger(n) && n >= 1 && n <= casos.length) return casos[n - 1]
  const limpio = normalizar(texto)
  return (
    casos.find((c) => {
      const palabras = [c.nombre, c.motor, ...normalizar(`${c.titulo} ${c.empresa_o_industria}`).split(/\s+/)]
      return palabras.some((p) => p.length > 4 && limpio.includes(normalizar(p)))
    }) ?? null
  )
}
