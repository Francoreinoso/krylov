// Cliente de la API con modo estático (CONTRATO.md, sección 6).
// Pide a la API; si no hay API configurada, si no responde en 1,5 s o si la URL trae
// ?estatico=1, lee la copia precalculada de /estatico/<archivo>.json.

import type { Analisis, Casos } from './tipos'

const API_URL: string =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8010' : '')
const TOPE_MS = 1500
const forzarEstatico = new URLSearchParams(window.location.search).has('estatico')

export type Origen = 'api' | 'estatico'

export interface Respuesta<T> {
  datos: T
  origen: Origen
}

// Nombre del archivo estático: el caso, más `__` y cada transformación en orden.
export function clave(caso: string, transformaciones: string[] = []): string {
  return [caso, ...transformaciones.map((t) => t.replace(':', '-'))].join('__')
}

async function desdeApi<T>(ruta: string, cuerpo?: object): Promise<T> {
  const control = new AbortController()
  const tope = setTimeout(() => control.abort(), TOPE_MS)
  try {
    const r = await fetch(`${API_URL}/api/${ruta}`, {
      method: cuerpo ? 'POST' : 'GET',
      headers: cuerpo ? { 'Content-Type': 'application/json' } : undefined,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
      signal: control.signal,
    })
    if (!r.ok) throw new Error(`API ${r.status}`)
    return (await r.json()) as T
  } finally {
    clearTimeout(tope)
  }
}

async function desdeEstatico<T>(archivo: string): Promise<T> {
  const r = await fetch(`${import.meta.env.BASE_URL}estatico/${archivo}.json`)
  if (!r.ok) throw new Error(`No está precalculado: ${archivo}`)
  return (await r.json()) as T
}

async function pedir<T>(ruta: string, archivo: string, cuerpo?: object): Promise<Respuesta<T>> {
  if (API_URL && !forzarEstatico) {
    try {
      return { datos: await desdeApi<T>(ruta, cuerpo), origen: 'api' }
    } catch {
      // Sigue con la copia precalculada.
    }
  }
  return { datos: await desdeEstatico<T>(archivo), origen: 'estatico' }
}

// Despierta al servidor gratuito apenas carga la página; la respuesta no importa.
export function despertarApi(): void {
  if (API_URL && !forzarEstatico) fetch(`${API_URL}/api/salud`).catch(() => {})
}

export const api = {
  casos: () => pedir<Casos>('casos', 'casos'),
  analizar: (caso: string, transformaciones: string[] = []) =>
    pedir<Analisis>('analizar', `analizar/${clave(caso, transformaciones)}`, {
      caso,
      transformaciones,
    }),
}
