import type { Analisis, Caso } from './tipos'

// La línea chica de cada caso. Con sponsor, siempre «… · datos públicos de ejemplo» (CONTRATO.md, sección 4).
export const lineaDelCaso = (caso: Caso) =>
  caso.sponsor ? `${caso.empresa_o_industria} · datos públicos de ejemplo` : caso.empresa_o_industria

// Quién respondió, para el pie. En rojo no hubo respuesta, así que no se le atribuye a nadie.
export function quienRespondio(analisis: Analisis): string {
  if (analisis.semaforo.estado.startsWith('rojo')) return 'Krylov no respondió con este archivo'
  return analisis.precalculado ? 'Precalculado con el método lento de siempre' : 'Respondió la red que practicó con casos simulados'
}
