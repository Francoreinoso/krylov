// Cliente de la API con modo estático (CONTRATO.md, sección 6).
// Pide a la API; si no hay API configurada, si no responde en 1,5 s o si la URL trae
// ?estatico=1, lee la copia precalculada de /estatico/<archivo>.json.

import type { Analisis, Calce, CalcePapel, Casos, DondeMedir, Interpretacion, MedicionNueva, Nube, Papeles, Textos } from './tipos'

const API_URL: string =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8010' : '')
const TOPE_MS = 1500
const TOPE_ARCHIVO_MS = 25000 // el servidor gratuito puede estar dormido
const TOPE_INTERPRETAR_MS = 12000 // el modelo de lenguaje escribe después de los números y no los bloquea
const TOPE_DONDE_MEDIR_MS = 8000 // rehace cientos de análisis; en el computador del escenario tarda cerca de 1 s
const forzarEstatico = new URLSearchParams(window.location.search).has('estatico')

// Hay servidor al que preguntar: un archivo propio y una interpretación nueva lo necesitan.
export const hayApi = Boolean(API_URL) && !forzarEstatico

// Un archivo propio exige la API; sin ella el chat lo dice en vez de responder otra cosa.
// El servidor respondió con un error del contrato: el mensaje para la persona y su código (`no_disponible`, …).
export class ErrorDelServidor extends Error {
  codigo: string | null
  constructor(mensaje: string, codigo: string | null) {
    super(mensaje)
    this.codigo = codigo
  }
}

export class SinServidor extends Error {
  constructor() {
    super('No hay servidor')
  }
}

export type Origen = 'api' | 'estatico'

export interface Respuesta<T> {
  datos: T
  origen: Origen
}

// Nombre del archivo estático: el caso, más `__` y cada transformación y muestra nueva en orden
// (igual que `servicio/fijos.py`).
export function clave(caso: string, transformaciones: string[] = [], mediciones: MedicionNueva[] = []): string {
  return [caso, ...transformaciones.map((t) => t.replace(':', '-')), ...mediciones.map((m) => m.etiqueta)].join('__')
}

async function desdeApi<T>(ruta: string, cuerpo?: object, topeMs = TOPE_MS, senal?: AbortSignal): Promise<T> {
  const control = new AbortController()
  const tope = setTimeout(() => control.abort(), topeMs)
  senal?.addEventListener('abort', () => control.abort())
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
  // Sin el archivo, el servidor de desarrollo devuelve la página: tampoco está precalculado.
  if (!r.ok || !r.headers.get('content-type')?.includes('json')) throw new Error(`no está precalculado (${archivo})`)
  return (await r.json()) as T
}

async function pedir<T>(ruta: string, archivo: string, cuerpo?: object, topeMs = TOPE_MS): Promise<Respuesta<T>> {
  if (API_URL && !forzarEstatico) {
    try {
      return { datos: await desdeApi<T>(ruta, cuerpo, topeMs), origen: 'api' }
    } catch {
      // Sigue con la copia precalculada.
    }
  }
  return { datos: await desdeEstatico<T>(archivo), origen: 'estatico' }
}

// Un archivo subido, en un formulario: sin copia estática posible.
async function conArchivo<T>(ruta: string, campos: Record<string, string | Blob>): Promise<T> {
  if (!hayApi) throw new SinServidor()
  const form = new FormData()
  for (const [k, v] of Object.entries(campos)) form.append(k, v)
  const control = new AbortController()
  const tope = setTimeout(() => control.abort(), TOPE_ARCHIVO_MS)
  let r: Response
  try {
    r = await fetch(`${API_URL}/api/${ruta}`, { method: 'POST', body: form, signal: control.signal })
  } catch {
    throw new SinServidor()
  } finally {
    clearTimeout(tope)
  }
  const cuerpo = await r.json().catch(() => null)
  if (!r.ok) throw new ErrorDelServidor(cuerpo?.error ?? `El servidor respondió ${r.status}`, cuerpo?.codigo ?? null)
  return cuerpo as T
}

// Sin modelo de lenguaje: las frases de plantilla que ya trae la respuesta.
export const plantilla = (a: Analisis): Interpretacion => ({
  texto: a.en_palabras.join(' ') || a.titular,
  origen: 'plantilla',
  proveedor: null,
  precalculado: false,
})

// La interpretación de una respuesta. `clave` es la del archivo del demo (tiene copia estática);
// en un archivo propio es null y, sin servidor, queda la plantilla.
async function interpretar(analisis: Analisis, clave: string | null, senal?: AbortSignal): Promise<Interpretacion> {
  if (hayApi) {
    try {
      return await desdeApi<Interpretacion>('interpretar', analisis, TOPE_INTERPRETAR_MS, senal)
    } catch {
      if (senal?.aborted) throw new DOMException('Cancelada', 'AbortError')
    }
  }
  if (clave) {
    try {
      return await desdeEstatico<Interpretacion>(`interpretar/${clave}`)
    } catch {
      // Sigue con la plantilla.
    }
  }
  return plantilla(analisis)
}

export type ColumnasConfirmadas = Record<string, Pick<CalcePapel, 'columnas' | 'transformacion'>>

// Despierta al servidor gratuito apenas carga la página; la respuesta no importa.
export function despertarApi(): void {
  if (API_URL && !forzarEstatico) fetch(`${API_URL}/api/salud`).catch(() => {})
}

// En vivo tarda más de 2 s (AGENTS.md, regla 7): para un caso del demo manda el precalculado.
async function dondeMedir(caso: string): Promise<Respuesta<DondeMedir>> {
  try {
    return { datos: await desdeEstatico<DondeMedir>(`donde-medir/${clave(caso)}`), origen: 'estatico' }
  } catch {
    return pedir<DondeMedir>('donde-medir', `donde-medir/${clave(caso)}`, { caso, mediciones: [] }, TOPE_DONDE_MEDIR_MS)
  }
}

export const api = {
  casos: () => pedir<Casos>('casos', 'casos'),
  textos: () => pedir<Textos>('textos', 'textos'),
  // El archivo de prueba de un caso (`datos/demo/subida_<caso>.csv`, copiado a `web/public/pruebas/`).
  archivoDePrueba: async (caso: string): Promise<File> => {
    const nombre = `subida_${caso}.csv`
    const r = await fetch(`${import.meta.env.BASE_URL}pruebas/${nombre}`)
    if (!r.ok || r.headers.get('content-type')?.includes('html')) throw new Error(`no encontré ${nombre}`)
    return new File([await r.blob()], nombre, { type: 'text/csv' })
  },
  analizar: (caso: string, transformaciones: string[] = [], mediciones: MedicionNueva[] = []) =>
    pedir<Analisis>('analizar', `analizar/${clave(caso, transformaciones, mediciones)}`, {
      caso,
      transformaciones,
      mediciones,
    }),
  nube: (caso: string, transformaciones: string[] = []) =>
    pedir<Nube>('nube', `nube/${clave(caso, transformaciones)}`, { caso, transformaciones }),
  papeles: (motor: string) => pedir<Papeles>(`papeles/${motor}`, `papeles/${motor}`),
  calce: (caso: string) => pedir<Calce>(`calce/${caso}`, `calce/${caso}`),
  // `caso` es la tarjeta elegida: de su YAML sale una pista para la regla de columnas.
  calcePropio: (archivo: File, motor: string, caso: string) => conArchivo<Calce>('calce', { archivo, motor_id: motor, caso }),
  analizarArchivo: (archivo: File, motor: string, columnas: ColumnasConfirmadas) =>
    conArchivo<Analisis>('analizar_archivo', { archivo, motor_id: motor, columnas: JSON.stringify(columnas) }),
  interpretar,
  dondeMedir,
}
