// Los tres colores son decisiones, no pronósticos (CONTRATO.md, sección 3).

import type { Estado } from './tipos'

// Clases para HTML: la duda va achurada.
export const FONDO: Record<Estado, string> = {
  actuar: 'bg-actuar',
  en_duda: 'achurado',
  no_actuar: 'bg-no-actuar',
}

// Colores para SVG y canvas.
export const COLOR: Record<Estado, string> = {
  actuar: '#e5534b',
  en_duda: '#f0b429',
  no_actuar: '#3daa74',
}

export const ORDEN: Estado[] = ['actuar', 'en_duda', 'no_actuar']
