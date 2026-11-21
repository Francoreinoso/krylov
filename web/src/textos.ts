import type { Analisis, Caso } from './tipos'

// La línea chica de cada caso. Con sponsor, siempre «… · datos públicos de ejemplo» (CONTRATO.md, sección 4).
export const lineaDelCaso = (caso: Caso) =>
  caso.sponsor ? `${caso.empresa_o_industria} · datos públicos de ejemplo` : caso.empresa_o_industria

// Quién respondió, para el pie. En rojo no hubo respuesta, así que no se le atribuye a nadie.
export function quienRespondio(analisis: Analisis): string {
  if (analisis._aviso) return 'Ejemplo fijo con números inventados: este modelo todavía no responde'
  if (analisis.semaforo.estado.startsWith('rojo')) return 'Krylov no respondió con este archivo'
  return analisis.precalculado ? 'Precalculado con el método lento de siempre' : 'Respondió la red que practicó con casos simulados'
}

// Quién respondió, como rótulo corto del pie de las láminas.
export function rotuloQuien(a: Analisis): { texto: string; corto: string; clase: string; borde: string } {
  if (a._aviso) return { texto: 'Ejemplo · números inventados', corto: 'Ejemplo', clase: 'text-tenue', borde: 'border-linea' }
  if (a.semaforo.estado.startsWith('rojo')) return { texto: 'No respondió', corto: 'No respondió', clase: 'text-actuar', borde: 'border-actuar' }
  if (a.precalculado) return { texto: 'Precalculado', corto: 'Precalculado', clase: 'text-oro', borde: 'border-oro' }
  return { texto: 'Responde la red', corto: 'Responde la red', clase: 'text-oxido', borde: 'border-oxido' }
}
