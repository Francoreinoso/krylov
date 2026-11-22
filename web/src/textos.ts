import type { Analisis } from './tipos'

// El nombre de una unidad en pantalla, como en el deck (pitch/deck/js/decisiones.js, nombre()): «Sector 25» y no
// «S-25», «Camión 05» y no «CAEX-05». En un archivo propio se respeta el nombre que trae.
export const nombreDeUnidad = (id: string, propio: boolean) =>
  propio ? id : id.replace(/^S-0?/, 'Sector ').replace(/^L-0?/, 'Línea ').replace(/^CAEX-/, 'Camión ')

// Quién respondió, en una línea. En rojo no hubo respuesta, así que no se le atribuye a nadie (regla 5).
export function quienRespondio(a: Analisis): string {
  if (a.semaforo.estado.startsWith('rojo')) return 'Krylov no respondió con este archivo'
  return a.precalculado && a.implementacion === 'mcmc' ? 'Respondió el método lento de siempre, calculado antes' : 'Respondió la red, que practicó con casos simulados'
}
