import type { Caso } from './tipos'

// La línea chica de cada caso. Con sponsor, siempre «… · datos públicos de ejemplo» (CONTRATO.md, sección 4).
export const lineaDelCaso = (caso: Caso) =>
  caso.sponsor ? `${caso.empresa_o_industria} · datos públicos de ejemplo` : caso.empresa_o_industria
