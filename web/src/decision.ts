// Capa de decisión en el navegador: la misma cuenta que nucleo/decision.py (CONTRATO.md, sección 3),
// para que los deslizadores de costos respondan sin llamar a la API. Las dos copias se prueban
// contra contratos/ejemplos/decision_prueba.json.
//
// Los colores son decisiones, no pronósticos. Con cSi = costo de actuar cuando no hacía falta y
// cNo = costo de no actuar cuando sí:
//   punto de corte = cSi / (cSi + cNo); se actúa si p lo supera.
//   en duda = más de 10% de probabilidad de que la decisión cambie al saber más.

import type { Estado } from './tipos'

export const UMBRAL_DE_DUDA = 0.1

export interface Decision {
  p: number
  estado: Estado
  duda: number
}

export const puntoDeCorte = (cSi: number, cNo: number) => cSi / (cSi + cNo)

// Costo esperado de la mejor decisión con probabilidad p: el menor entre actuar y no actuar.
const costoEsperado = (p: number, cSi: number, cNo: number) => Math.min(cSi * (1 - p), cNo * p)

const estadoDe = (actuar: boolean, enDuda: boolean): Estado =>
  enDuda ? 'en_duda' : actuar ? 'actuar' : 'no_actuar'

// Motores de tabla: muestras de p de una unidad, una por versión creíble.
export function decidirTabla(muestras: number[], cSi: number, cNo: number): Decision {
  const corte = puntoDeCorte(cSi, cNo)
  const n = muestras.length
  const p = muestras.reduce((a, b) => a + b, 0) / n
  const actuar = p > corte
  const alOtroLado = muestras.filter((s) => s > corte !== actuar).length / n
  const promedio = muestras.reduce((a, s) => a + costoEsperado(s, cSi, cNo), 0) / n
  const duda = Math.max(costoEsperado(p, cSi, cNo) - promedio, 0)
  return { p, estado: estadoDe(actuar, alOtroLado > UMBRAL_DE_DUDA), duda }
}

// Espacial: p = probabilidad de superar el umbral en el bloque. Medirlo despeja toda la duda.
export function decidirEspacial(p: number, cSi: number, cNo: number): Decision {
  const actuar = p > puntoDeCorte(cSi, cNo)
  const equivocarse = actuar ? 1 - p : p
  return { p, estado: estadoDe(actuar, equivocarse > UMBRAL_DE_DUDA), duda: costoEsperado(p, cSi, cNo) }
}

export function resumenColores(estados: Estado[]): Record<Estado, number> {
  const resumen: Record<Estado, number> = { actuar: 0, no_actuar: 0, en_duda: 0 }
  for (const e of estados) resumen[e] += 1
  return resumen
}
