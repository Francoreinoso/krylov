import { useState } from 'react'
import type { Unidad } from './tipos'

// La unidad cuya curva se dibuja: al abrir, la de más duda entre las que traen curva.
export function useUnidadElegida(unidades: Unidad[] | null) {
  return useState<string | null>(() => {
    const conCurva = unidades?.filter((u) => u.curva) ?? []
    return conCurva.length ? conCurva.reduce((a, b) => (b.duda > a.duda ? b : a)).id : null
  })
}
