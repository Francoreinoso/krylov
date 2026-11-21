// Los tres colores son decisiones, no pronósticos (CONTRATO.md, sección 3).

import type { Estado } from './tipos'

export const FONDO: Record<Estado, string> = {
  actuar: 'bg-actuar',
  en_duda: 'achurado',
  no_actuar: 'bg-no-actuar',
}

export const ORDEN: Estado[] = ['actuar', 'en_duda', 'no_actuar']
