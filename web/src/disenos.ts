// Diseños para comparar en local: cada uno redefine los tokens del CSS (index.css).
// Se elige con ?diseno=<id>, lo guardado o el primero.

import { useSyncExternalStore } from 'react'

export interface Diseno {
  id: string
  nombre: string
  descripcion: string
  muestra: [fondo: string, tinta: string, acento: string]
}

export const DISENOS: Diseno[] = [
  { id: 'estudio', nombre: 'Estudio', descripcion: 'Claro, de asistente', muestra: ['#ffffff', '#1a1b25', '#5b5bd6'] },
  { id: 'arcilla', nombre: 'Arcilla', descripcion: 'Papel tibio, terracota, serifa', muestra: ['#faf8f3', '#24201b', '#c2562f'] },
  { id: 'marea', nombre: 'Marea', descripcion: 'Blanco roto, celeste y verde mar', muestra: ['#f7f6f2', '#17212b', '#174a5b'] },
  { id: 'tinta', nombre: 'Tinta', descripcion: 'Blanco y negro; color solo en los datos', muestra: ['#ffffff', '#0a0a0a', '#e5484d'] },
  { id: 'tablas', nombre: 'Tablas de Krylov', descripcion: 'Papel impreso, todo con serifa', muestra: ['#f4efe4', '#1d1a16', '#b8322a'] },
  { id: 'estudio-noche', nombre: 'Estudio noche', descripcion: 'Oscuro, de asistente', muestra: ['#1e1f24', '#ececf1', '#9191f8'] },
  { id: 'orbita', nombre: 'Órbita', descripcion: 'Casi negro y azul eléctrico', muestra: ['#090b10', '#eef2fa', '#5b8cff'] },
  { id: 'wasabi', nombre: 'Wasabi', descripcion: 'Grafito, celeste y lima', muestra: ['#0b0d10', '#f4f5f7', '#e9f056'] },
  { id: 'ciruela', nombre: 'Ciruela', descripcion: 'Ciruela oscura y durazno, serifa', muestra: ['#1a1216', '#f6ece8', '#f0b48a'] },
  { id: 'puente', nombre: 'Puente', descripcion: 'Oscuro, de proyector', muestra: ['#0d1f2b', '#e9eff2', '#f0b429'] },
]

const CLAVE = 'krylov.diseno'
const EVENTO = 'diseno'

const porId = (id: string | null | undefined) => DISENOS.find((d) => d.id === id)

export function disenoInicial(): string {
  const pedido = new URLSearchParams(window.location.search).get('diseno')
  let guardado: string | null = null
  try {
    guardado = localStorage.getItem(CLAVE)
  } catch {
    // Sin almacenamiento: se usa el primero.
  }
  return (porId(pedido) ?? porId(guardado) ?? DISENOS[0]).id
}

export function aplicarDiseno(id: string): void {
  document.documentElement.dataset.diseno = id
  try {
    localStorage.setItem(CLAVE, id)
  } catch {
    // Se pierde al recargar; no importa.
  }
  window.dispatchEvent(new Event(EVENTO))
}

export function siguienteDiseno(): void {
  const i = DISENOS.findIndex((d) => d.id === document.documentElement.dataset.diseno)
  aplicarDiseno(DISENOS[(i + 1) % DISENOS.length].id)
}

const suscribir = (avisar: () => void) => {
  window.addEventListener(EVENTO, avisar)
  return () => window.removeEventListener(EVENTO, avisar)
}

export function useDiseno(): Diseno {
  const id = useSyncExternalStore(suscribir, () => document.documentElement.dataset.diseno)
  return porId(id) ?? DISENOS[0]
}
