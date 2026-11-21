// Cuatro diseños para comparar en local, todos con la cara del deck. Cada uno redefine tokens del
// CSS (index.css) y elige una disposición de la pantalla. Se elige con ?diseno=<id>, lo guardado o
// el primero; la tecla V pasa al siguiente (la D queda para el modo demo).

import { useSyncExternalStore } from 'react'

export type Disposicion = 'columna' | 'mesa' | 'lamina' | 'oxido'

export interface Diseno {
  id: Disposicion
  nombre: string
  descripcion: string
  muestra: [fondo: string, tinta: string, acento: string]
}

export const DISENOS: Diseno[] = [
  { id: 'columna', nombre: 'Carta', descripcion: 'Fiel al deck: una columna sobre la carta topográfica', muestra: ['#0b0a09', '#f4efe6', '#e2854a'] },
  { id: 'mesa', nombre: 'Mesa', descripcion: 'Chat a la izquierda, la respuesta en grande a la derecha', muestra: ['#0d0c0a', '#e2854a', '#36c2ae'] },
  { id: 'lamina', nombre: 'Lámina', descripcion: 'Cada respuesta llega como una lámina del deck', muestra: ['#070605', '#f4efe6', '#eec25a'] },
  { id: 'oxido', nombre: 'Óxido', descripcion: 'Turquesa, con las cinco decisiones siempre a la vista', muestra: ['#070d0c', '#eef3f1', '#36c2ae'] },
]

const CLAVE = 'krylov.diseno'
const EVENTO = 'diseno'
// El atributo del CSS usa el nombre corto del diseño.
const ATRIBUTO: Record<Disposicion, string> = { columna: 'carta', mesa: 'mesa', lamina: 'lamina', oxido: 'oxido' }

const porId = (id: string | null | undefined) => DISENOS.find((d) => d.id === id || ATRIBUTO[d.id] === id)

export function disenoInicial(): Disposicion {
  const pedido = new URLSearchParams(window.location.search).get('diseno')
  let guardado: string | null = null
  try {
    guardado = localStorage.getItem(CLAVE)
  } catch {
    // Sin almacenamiento: se usa el primero.
  }
  return (porId(pedido) ?? porId(guardado) ?? DISENOS[0]).id
}

export function aplicarDiseno(id: Disposicion): void {
  document.documentElement.dataset.diseno = ATRIBUTO[id]
  try {
    localStorage.setItem(CLAVE, id)
  } catch {
    // Se pierde al recargar; no importa.
  }
  window.dispatchEvent(new Event(EVENTO))
}

export function siguienteDiseno(): void {
  const i = DISENOS.findIndex((d) => ATRIBUTO[d.id] === document.documentElement.dataset.diseno)
  aplicarDiseno(DISENOS[(i + 1) % DISENOS.length].id)
}

const suscribir = (avisar: () => void) => {
  window.addEventListener(EVENTO, avisar)
  return () => window.removeEventListener(EVENTO, avisar)
}

export function useDiseno(): Diseno {
  const atributo = useSyncExternalStore(suscribir, () => document.documentElement.dataset.diseno)
  return porId(atributo) ?? DISENOS[0]
}
