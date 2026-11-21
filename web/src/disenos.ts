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
  { id: 'estudio-noche', nombre: 'Estudio noche', descripcion: 'Oscuro, de asistente', muestra: ['#1e1f24', '#ececf1', '#9191f8'] },
  { id: 'puente', nombre: 'Puente', descripcion: 'Oscuro, de proyector', muestra: ['#0d1f2b', '#e9eff2', '#f0b429'] },
  { id: 'tablas', nombre: 'Tablas de Krylov', descripcion: 'Papel impreso, serif', muestra: ['#f4efe4', '#1d1a16', '#b8322a'] },
  { id: 'sonar', nombre: 'Sonar', descripcion: 'Terminal de fósforo', muestra: ['#070b09', '#b8f5c8', '#39d98a'] },
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
