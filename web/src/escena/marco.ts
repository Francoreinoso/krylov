// Dentro del marco: una lámina del deck con los datos de una respuesta de Krylov (D-42).
// La app manda un pedido (`Pedido`) y aquí se arma la lámina con el mismo HTML, la misma hoja de estilos y los mismos
// módulos del deck (pitch/deck), sin tocarlos: el deck lee `window.KRYLOV_DATOS`, y aquí ese objeto es el de la respuesta.
// Cada respuesta abre un marco nuevo, porque los módulos del deck arman su escena una sola vez.

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

// En la app, la tarjeta de la roca dice lo que hay bajo el mouse: quien mira un terreno pregunta por el lugar que apunta.
// El deck no se toca: aquí se envuelve el recorrido del foco de su lámina. Mientras el mouse está sobre el terreno, el foco
// es el bloque apuntado (la misma lectura de la respuesta de la red: rango, valor y decisión); al salir, el recorrido sigue
// desde ahí, como después de un clic. Con el dedo no hay mouse que seguir: el clic del deck sigue mandando.
interface Terreno {
  T: { bajo: number[]; media: number[]; alto: number[]; estado: number[] }
  clic: number | null
  tres: { camera: unknown }
  bloqueBajo: (x: number, z: number) => number | null
  alturaDe: (i: number) => number
}
interface FocoRoca { bajo: number; medio: number; alto: number; c: number[]; y: number; estado?: number; x?: number; z?: number }
interface EscenaRoca {
  m?: Terreno
  v?: FocoRoca | null
  colores: number[][]
  foco: (t: number, dt?: number) => FocoRoca | null
}
interface Rayo {
  ray: { origin: Record<'x' | 'y' | 'z', number>; direction: Record<'x' | 'y' | 'z', number> }
  setFromCamera: (lugar: { x: number; y: number }, camara: unknown) => void
}

function seguirAlMouse() {
  const K = window.K as unknown as { escenas: { leyes?: EscenaRoca }; gl: { renderer: { domElement: HTMLCanvasElement } | null }; donde: () => { paso: number } }
  const THREE = (window as unknown as { THREE: { Raycaster: new () => Rayo } }).THREE
  const escena = K.escenas.leyes
  const lienzo = K.gl.renderer?.domElement
  if (!escena || !lienzo) return
  const rayo = new THREE.Raycaster()
  let mouse: { x: number; y: number } | null = null // de −1 a 1 en cada eje, como lo pide la cámara
  let ultimo: number | null = null // el último bloque apuntado: desde ahí sigue el recorrido

  // El punto del terreno que se ve bajo el mouse: se camina por el rayo hasta tocar el relieve (como `bloqueEn` del deck).
  const apuntado = (m: Terreno) => {
    rayo.setFromCamera(mouse!, m.tres.camera)
    const o = rayo.ray.origin, d = rayo.ray.direction
    for (let t = 20; t < 240; t += 0.2) {
      const x = o.x + d.x * t, z = o.z + d.z * t, i = m.bloqueBajo(x, z)
      if (i != null && o.y + d.y * t <= m.alturaDe(i)) return { i, x, z }
    }
    return null
  }
  const soltar = () => {
    if (ultimo != null && escena.m) escena.m.clic = ultimo
    mouse = null
    ultimo = null
  }
  lienzo.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch' || e.buttons !== 0) return // arrastrar gira el terreno: ahí no se apunta
    const r = lienzo.getBoundingClientRect()
    mouse = { x: ((e.clientX - r.left) / r.width) * 2 - 1, y: 1 - ((e.clientY - r.top) / r.height) * 2 }
  })
  lienzo.addEventListener('pointerleave', soltar)

  const recorrido = escena.foco
  escena.foco = function (this: EscenaRoca, t: number, dt?: number) {
    const m = this.m
    const p = m && mouse && K.donde().paso === 0 ? apuntado(m) : null
    if (!m || !p) {
      if (ultimo != null) soltar() // el mouse salió del terreno sin salir del lienzo
      return recorrido.call(this, t, dt)
    }
    ultimo = p.i
    const T = m.T, c = this.colores[T.estado[p.i]], y = m.alturaDe(p.i)
    const v = this.v || (this.v = { bajo: T.bajo[p.i], medio: T.media[p.i], alto: T.alto[p.i], c: c.slice(), y })
    // la cifra sigue al bloque apuntado con la misma suavidad que en el recorrido: sin escalones entre bloques
    const q = window.K.quieto ? 1 : Math.min(1, (dt || 0.016) * 16)
    v.bajo += (T.bajo[p.i] - v.bajo) * q
    v.medio += (T.media[p.i] - v.medio) * q
    v.alto += (T.alto[p.i] - v.alto) * q
    for (let n = 0; n < 3; n++) v.c[n] += (c[n] - v.c[n]) * q
    v.y += (y - v.y) * q
    v.estado = T.estado[p.i]
    v.x = p.x
    v.z = p.z
    return v
  }
}

async function arrancar(p: Extract<AlMarco, { tipo: 'escena' }>) {
  window.KRYLOV_DATOS = p.datos
  window.KRYLOV_CONFIG = p.config
  const L = await seccion(p.lamina)
  enlazar(L, p.datos)
  document.getElementById('escenario')!.appendChild(L)
  for (const src of ['vendor/three.min.js', 'vendor/gsap.min.js', 'js/nucleo.js', ...MODULOS[p.lamina]]) await cargar(src)
  window.K.arrancar()
  if (p.lamina === 'leyes') seguirAlMouse()
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
