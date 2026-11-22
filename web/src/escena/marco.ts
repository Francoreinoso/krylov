// Dentro del marco: una lámina del deck con los datos de una respuesta de Krylov (D-42).
// La app manda un pedido (`Pedido`) y aquí se arma la lámina con el mismo HTML, la misma hoja de estilos y los mismos
// módulos del deck (pitch/deck), sin tocarlos: el deck lee `window.KRYLOV_DATOS`, y aquí ese objeto es el de la respuesta.
// Cada respuesta abre un marco nuevo, porque los módulos del deck arman su escena una sola vez.

import { conMouse } from './mouse'
import type { AlMarco, DelMarco, Lamina } from './protocolo'

interface EscenaDeck {
  m?: {
    s: Record<string, number>
    T: Record<string, unknown>
    clic: number | null
    pinDe: (letra: string, valor: number) => { i: number }
    morfar: (capa: unknown, desde: unknown, inst: boolean, demora?: number) => void
  }
}
interface Deck {
  escenas: Record<string, EscenaDeck>
  arrancar: () => void
  ir: (lamina: number, paso: number, inst: boolean) => void
  pausar: (si: boolean) => void
  quieto: boolean
}
declare global {
  interface Window {
    K: Deck
    KRYLOV_DATOS: unknown
    KRYLOV_CONFIG: unknown
    gsap: { to: (obj: object, vars: Record<string, unknown>) => unknown }
  }
}

// Los módulos que necesita cada lámina, en el orden en que los carga el deck (pitch/deck/index.html).
const DECISION = ['js/terreno.js', 'js/decisiones.js', 'js/flotacion.js', 'js/sismicidad.js', 'js/intervalos.js', 'js/foco.js']
const MODULOS: Record<Lamina, string[]> = {
  leyes: DECISION,
  taludes: DECISION,
  flotacion: DECISION,
  flota: DECISION,
  sismicidad: DECISION,
  valor: ['js/portada.js'],
  vision: ['js/vision.js'],
}

const decirAlPadre = (m: DelMarco) => window.parent.postMessage(m, window.location.origin)

const cargar = (src: string) =>
  new Promise<void>((listo, falla) => {
    const s = document.createElement('script')
    s.src = '/deck/' + src
    s.async = false
    s.onload = () => listo()
    s.onerror = () => falla(new Error('No cargó ' + src))
    document.body.appendChild(s)
  })

// La sección de la lámina, tal cual está en el deck. Sus notas para quien presenta no se muestran (deck.css las oculta).
async function seccion(lamina: Lamina): Promise<HTMLElement> {
  const html = await fetch('/deck/laminas.html').then((r) => r.text())
  const s = new DOMParser().parseFromString(html, 'text/html').getElementById('l-' + lamina)
  if (!s) throw new Error('El deck no tiene la lámina ' + lamina)
  s.querySelector('aside.notas')?.remove()
  return document.importNode(s, true)
}

// Como K.miles del deck, que todavía no está cargado cuando se llena la lámina.
const miles = (n: number) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')

// Los números del HTML de la lámina (<span data-dato="donde.n_lugares">), como K.enlazarDatos del deck pero solo para
// esta lámina: el resto de los datos del deck no viene en una respuesta.
function enlazar(L: HTMLElement, datos: unknown) {
  L.querySelectorAll<HTMLElement>('[data-dato]').forEach((el) => {
    let v: unknown = datos
    for (const k of el.dataset.dato!.split('.')) v = v == null ? v : (v as Record<string, unknown>)[k]
    if (v == null) return
    el.textContent = typeof v === 'number' ? miles(v) : String(v)
  })
}

// «¿Dónde perforo?» en la escena: el taladro baja al lugar elegido, deja la muestra y el terreno se rehace desde ahí
// hacia la capa nueva (la respuesta de la red con esa muestra más). Después el foco se va a ese bloque.
function perforar(letra: string, capa: Record<string, unknown>, valor: number) {
  const m = window.K.escenas.leyes?.m
  if (!m) return
  const pin = m.pinDe(letra, valor)
  m.s.taladro = 0
  m.s.medido = 0
  m.morfar(capa, pin, window.K.quieto, 1.1)
  if (window.K.quieto) {
    Object.assign(m.s, { taladro: 1, medido: 1 })
  } else {
    window.gsap.to(m.s, { taladro: 1, duration: 0.9, ease: 'power2.in' })
    window.gsap.to(m.s, { medido: 1, duration: 0.4, delay: 0.9 })
  }
  // la tarjeta del foco lee el terreno base: cuando el mapa nuevo termina de llegar, pasa a ser el base
  window.setTimeout(
    () => {
      for (const k of ['media', 'alto', 'bajo', 'p', 'estado']) if (capa[k]) m.T[k] = capa[k]
      m.clic = pin.i
      window.K.ir(0, 0, false)
    },
    window.K.quieto ? 0 : 4200,
  )
}

async function arrancar(p: Extract<AlMarco, { tipo: 'escena' }>) {
  window.KRYLOV_DATOS = p.datos
  window.KRYLOV_CONFIG = p.config
  const L = await seccion(p.lamina)
  enlazar(L, p.datos)
  document.getElementById('escenario')!.appendChild(L)
  for (const src of ['vendor/three.min.js', 'vendor/gsap.min.js', 'js/nucleo.js', ...MODULOS[p.lamina]]) await cargar(src)
  window.K.arrancar()
  conMouse(p.lamina)
  if (p.paso) window.K.ir(0, p.paso, true)
  decirAlPadre({ tipo: 'lista' })
}

window.addEventListener('message', (e: MessageEvent<AlMarco>) => {
  if (e.origin !== window.location.origin || e.source !== window.parent) return
  const m = e.data
  if (m.tipo === 'escena') arrancar(m).catch((error: Error) => decirAlPadre({ tipo: 'falla', mensaje: error.message }))
  else if (!window.K?.escenas) return
  else if (m.tipo === 'paso') window.K.ir(0, m.paso, false)
  else if (m.tipo === 'pausa') window.K.pausar(m.si)
  else if (m.tipo === 'perforar') perforar(m.letra, m.capa, m.valor)
})

// Las teclas son de la app, no del deck: el marco las pasa y no deja que el deck las use (sus flechas, su F, su D).
window.addEventListener(
  'keydown',
  (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return
    e.stopImmediatePropagation()
    decirAlPadre({ tipo: 'tecla', tecla: e.key })
  },
  true,
)

decirAlPadre({ tipo: 'esperando' })
