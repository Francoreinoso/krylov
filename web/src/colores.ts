// Los tres colores son decisiones, no pronósticos (CONTRATO.md, sección 3).
// Los valores viven en el CSS (index.css).

import type { Estado } from './tipos'

// Valor actual de un token del CSS, para dibujar en canvas.
export const token = (nombre: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(nombre).trim()

const VARIABLE: Record<Estado, string> = {
  actuar: '--color-actuar',
  en_duda: '--color-en-duda',
  no_actuar: '--color-no-actuar',
}

// Clases para HTML: la duda va achurada.
export const FONDO: Record<Estado, string> = {
  actuar: 'bg-actuar',
  en_duda: 'achurado',
  no_actuar: 'bg-no-actuar',
}

// Para SVG: la variable CSS.
export const COLOR_SVG: Record<Estado, string> = {
  actuar: `var(${VARIABLE.actuar})`,
  en_duda: `var(${VARIABLE.en_duda})`,
  no_actuar: `var(${VARIABLE.no_actuar})`,
}

// Para canvas: el valor resuelto en el momento de dibujar.
export const COLOR: Record<Estado, string> = {
  get actuar() {
    return token(VARIABLE.actuar)
  },
  get en_duda() {
    return token(VARIABLE.en_duda)
  },
  get no_actuar() {
    return token(VARIABLE.no_actuar)
  },
}

export const ORDEN: Estado[] = ['actuar', 'en_duda', 'no_actuar']
