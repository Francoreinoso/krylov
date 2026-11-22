// El calce confirmado: qué columna del archivo va en cada papel del modelo, y cómo se dice su transformación.

import type { Calce as DatosCalce, CalcePapel } from './tipos'

export type Asignacion = Record<string, string[]>

export const asignacionDe = (calce: DatosCalce): Asignacion =>
  Object.fromEntries(Object.entries(calce.calce).map(([papel, c]) => [papel, c.columnas]))

// Lo que significa dividir por ciertos números, en palabras.
const DIVISION: Record<number, string> = { 60: 'de minutos a horas', 100: 'de porcentaje a fracción' }

// Una transformación, como se diría en voz alta: «minutos ÷ 60, de minutos a horas».
export function transformacionEnPalabras(t: CalcePapel['transformacion'], columna: string): string | null {
  if (!t || !columna) return null
  if (t.nombre === 'dividir' && typeof t.por === 'number') return `${columna} ÷ ${t.por.toLocaleString('es-CL')}${DIVISION[t.por] ? `, ${DIVISION[t.por]}` : ''}`
  if (t.nombre === 'log') return `Krylov lee ${columna} en escala logarítmica`
  if (t.nombre === 'dias_entre') return `días entre ${t.desde as string} y ${columna}`
  return null
}
