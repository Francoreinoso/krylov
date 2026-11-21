// Diseños para comparar en local: cada uno redefine los tokens del CSS (index.css) y elige cómo se
// envuelven los mensajes del chat. Se elige con ?diseno=<id>, lo guardado o el primero.

import { useSyncExternalStore } from 'react'

export type EstiloChat = 'burbujas' | 'documento' | 'terminal'

export interface Diseno {
  id: string
  nombre: string
  descripcion: string
  chat: EstiloChat
  muestra: [fondo: string, tinta: string, acento: string]
}

export const DISENOS: Diseno[] = [
  { id: 'puente', nombre: 'Puente', descripcion: 'Oscuro, de proyector', chat: 'burbujas', muestra: ['#0d1f2b', '#e9eff2', '#f0b429'] },
  { id: 'tablas', nombre: 'Tablas de Krylov', descripcion: 'Papel impreso, serif', chat: 'documento', muestra: ['#f4efe4', '#1d1a16', '#b8322a'] },
  { id: 'sonar', nombre: 'Sonar', descripcion: 'Terminal de fósforo', chat: 'terminal', muestra: ['#070b09', '#b8f5c8', '#39d98a'] },
  { id: 'estudio', nombre: 'Estudio', descripcion: 'Claro, de asistente', chat: 'burbujas', muestra: ['#f7f7fb', '#1b1c2a', '#5b5bd6'] },
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
