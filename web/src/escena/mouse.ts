// El mouse sobre la escena de una decisión (solo en la app; el deck no se toca y allá el recorrido sigue solo).
// Mientras el mouse está sobre el modelo, la cámara deja de mecerse y la tarjeta es la de lo que se apunta: el bloque del
// terreno, el sector de la pared, la línea de la planta, el camión o el sector de los túneles. Arrastrar gira el modelo;
// con Mayús o con el botón derecho, lo desplaza. Cuando el mouse sale, la vista vuelve a la suya y el recorrido sigue.
// Todo se hace envolviendo tres funciones del deck: el foco (quién se muestra), la cámara y el cuadro de la escena.

import type { Lamina } from './protocolo'

type Punto = { x: number; y: number; detras?: boolean } | null
interface Foco { ids?: string[]; fichas: Record<string, unknown>; a: string | null; b: string | null; e: number; t0: number }
interface Base { camera: unknown; mirar: (az: number, el: number, R: number, c: number[], dx: number) => void }
interface Terreno {
  s: { fase: number; arrastre: number; arrastreEl: number }
  T: { bajo: number[]; media: number[]; alto: number[]; estado: number[] }
  clic: number | null
  tres: { camera: unknown }
  bloqueBajo: (x: number, z: number) => number | null
  alturaDe: (i: number) => number
}
interface FocoRoca { bajo: number; medio: number; alto: number; c: number[]; y: number; estado?: number; x?: number; z?: number }
interface Escena {
  interactivo?: boolean
  cuadro: (t: number, dt?: number) => void
  // las escenas de lista
  B?: Base
  n?: number
  indice?: Record<string, number>
  pared?: (u: number, v: number) => number[]
  maximo?: number
  horas?: number
  geo?: { xFin: number; H: number; zDe: (l: number) => number }
  sector?: { x: number; z0: number; z1: number }[]
  // la roca
  m?: Terreno
  v?: FocoRoca | null
  colores?: number[][]
  foco?: (t: number, dt?: number) => FocoRoca | null
}
interface Rayo {
  ray: { origin: Record<'x' | 'y' | 'z', number>; direction: Record<'x' | 'y' | 'z', number> }
  setFromCamera: (lugar: { x: number; y: number }, camara: unknown) => void
}
interface DeckConMouse {
  escenas: Record<string, Escena | undefined>
  gl: { renderer: { domElement: HTMLCanvasElement } | null }
  foco: { cuadro: (F: Foco, t: number, punto: (id: string) => Punto, pausa?: number, viaje?: number, siguiente?: unknown) => void; rgb: (hex: string) => number[] }
  datos: { series: Record<string, { unidades: { id: string; puntos: number[][] }[]; rotulos: Record<string, string>; respuesta: { unidades: Record<string, { estado: string } | undefined> } }> }
  coloresDecision: Record<string, string>
  nombreDe: (id: string) => string
  coma: (v: number, decimales: number) => string
  proyectar: (x: number, y: number, z: number, camara: unknown) => NonNullable<Punto>
  donde: () => { paso: number }
  escala: number
  quieto: boolean
}

const RADIO = 110 // qué tan cerca de una unidad (en píxeles de la lámina, de 1920 × 1080) cuenta como apuntarla
const VUELTA = 3.5 // qué tan rápido vuelve la vista a la suya cuando el mouse sale (por segundo)
const acotar = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))

// Dónde está el mouse y qué hace: lo mismo para las cinco escenas.
function puntero(lienzo: HTMLCanvasElement) {
  const p = {
    en: null as { x: number; y: number } | null, // en píxeles de la lámina; null si no hay mouse sobre la escena
    movio: false,
    agarre: null as { x: number; y: number; desplaza: boolean } | null,
    tocado: false, // se arrastró: la vista se queda donde la dejaron hasta que el mouse salga
    alArrastrar: null as ((dx: number, dy: number, desplaza: boolean) => void) | null,
  }
  lienzo.addEventListener('pointerdown', (e) => {
    p.agarre = { x: e.clientX, y: e.clientY, desplaza: e.shiftKey || e.button !== 0 }
    p.tocado = true
    if (p.alArrastrar) lienzo.setPointerCapture(e.pointerId) // en la roca, el arrastre es del deck
  })
  lienzo.addEventListener('pointermove', (e) => {
    if (p.agarre) {
      p.alArrastrar?.(e.clientX - p.agarre.x, e.clientY - p.agarre.y, p.agarre.desplaza)
      p.agarre.x = e.clientX
      p.agarre.y = e.clientY
    }
    if (e.pointerType === 'touch') return // con el dedo no hay mouse que seguir
    const r = lienzo.getBoundingClientRect()
    p.en = { x: ((e.clientX - r.left) / r.width) * 1920, y: ((e.clientY - r.top) / r.height) * 1080 }
    p.movio = true
  })
  const soltar = () => (p.agarre = null)
  lienzo.addEventListener('pointerup', soltar)
  lienzo.addEventListener('pointercancel', soltar)
  lienzo.addEventListener('pointerleave', () => {
    p.en = null
    p.tocado = false
  })
  lienzo.addEventListener('contextmenu', (e) => e.preventDefault())
  return p
}

// ---------- la pared, la planta, los camiones y los túneles ----------

// Los lugares de la pantalla donde se ve una unidad. El deck da uno (donde se engancha el hilo de la tarjeta); aquí se
// suman otros a lo largo de la unidad, para que apuntar a cualquier parte de un sector o de una línea la elija.
function lugaresDe(K: DeckConMouse, lamina: Lamina, escena: Escena, id: string, punto: (id: string) => Punto): Punto[] {
  const i = escena.indice?.[id], camara = escena.B?.camera
  const en = (x: number, y: number, z: number) => K.proyectar(x, y, z, camara)
  if (i == null || !camara) return [punto(id)]
  if (lamina === 'taludes' && escena.pared && escena.n) {
    return [0.1, 0.3, 0.5, 0.7, 0.9].map((v) => {
      const q = escena.pared!((i + 0.5) / escena.n!, v)
      return en(q[0], q[1], q[2])
    })
  }
  if (lamina === 'flotacion' && escena.geo) {
    const g = escena.geo
    return [-1, -0.6, -0.2, 0.2, 0.6, 1].map((f) => en(g.xFin * f, g.H * 0.5, g.zDe(i)))
  }
  if (lamina === 'sismicidad' && escena.sector?.[i]) {
    const s = escena.sector[i]
    return [0, 0.33, 0.67, 1].map((f) => en(s.x, 0.3, s.z0 + (s.z1 - s.z0) * f))
  }
  return [punto(id)]
}

// En la pared, el deck arma la tarjeta solo de los sectores de su recorrido y de los que traen «horas que faltan». Para
// poder apuntar a cualquiera, aquí se arma la de los demás con lo que ya viene en la respuesta: la decisión del motor y lo
// que midió el radar. Es la misma tarjeta sin curva del deck, sin ninguna cifra nueva.
function fichasDeLaPared(K: DeckConMouse, escena: Escena, F: Foco) {
  const S = K.datos.series.taludes
  for (const un of S.unidades) {
    const estado = S.respuesta.unidades[un.id]?.estado
    if (F.fichas[un.id] || !estado || !un.puntos.length) continue
    const mm = un.puntos[un.puntos.length - 1][1]
    F.fichas[un.id] = {
      id: un.id, nombre: K.nombreDe(un.id), estado, decision: S.rotulos[estado], color: K.foco.rgb(K.coloresDecision[estado]),
      grande: K.coma(Math.max(0, mm), mm >= 10 ? 0 : 1).replace(',0', '') + ' mm', que: 'se movió en total',
      serie: un.puntos, tope: escena.maximo, rotuloSerie: 'Lo que midió el radar en ' + Math.round(escena.horas ?? 0) + ' horas',
    }
  }
}

function lista(K: DeckConMouse, lamina: Lamina, escena: Escena, p: ReturnType<typeof puntero>) {
  let sobre: string | null = null // la unidad apuntada
  const fija = () => sobre != null || p.agarre != null || p.tocado

  // El foco: la unidad más cercana al mouse. Si el mouse no se movió, sigue en la misma (un camión elegido no se suelta).
  const cuadroFoco = K.foco.cuadro
  let completa = false
  K.foco.cuadro = function (F, t, punto, pausa, viaje, siguiente) {
    camara()
    if (!completa && lamina === 'taludes') fichasDeLaPared(K, escena, F)
    completa = true
    const distancia = (id: string) =>
      Math.min(...lugaresDe(K, lamina, escena, id, punto).map((q) => (!q || q.detras ? Infinity : Math.hypot(q.x - p.en!.x, q.y - p.en!.y))))
    let id: string | null = null
    if (p.en) {
      if ((p.agarre || !p.movio) && sobre != null && distancia(sobre) < Infinity) id = sobre
      else if (!p.agarre) {
        let cerca = RADIO
        for (const otro of Object.keys(F.fichas)) { // cualquier unidad con tarjeta, no solo las del recorrido
          const d = distancia(otro)
          if (d < cerca) { cerca = d; id = otro }
        }
      }
      p.movio = false
    }
    sobre = id
    if (id != null) {
      if (F.a !== id || F.b != null) { F.a = id; F.b = null; F.e = 0 }
      F.t0 = t - 1.6 // el recorrido queda en pausa en esta unidad; al salir, sigue desde aquí
    }
    return cuadroFoco.call(K.foco, F, t, punto, pausa, viaje, siguiente)
  }

  // La cámara: mientras se apunta o se arrastra, se queda donde está (más lo que se arrastre); después vuelve a la suya.
  let sujeta: number[] | null = null // giro, elevación, distancia y el punto que mira
  let corrida = [0, 0, 0, 0, 0, 0] // lo que la vista se aparta de la del deck
  let antes = performance.now()
  let envuelta = false
  function camara() {
    const B = escena.B
    if (envuelta || !B) return
    envuelta = true
    const mirar = B.mirar
    B.mirar = (az, el, R, c, dx) => {
      const suya = [az, el, R, c[0], c[1], c[2]]
      const ahora = performance.now(), dt = Math.min(0.05, (ahora - antes) / 1000)
      antes = ahora
      if (fija()) {
        sujeta ??= suya.map((v, i) => v + corrida[i])
        corrida = sujeta.map((v, i) => v - suya[i])
      } else {
        sujeta = null
        const k = K.quieto ? 0 : Math.exp(-dt * VUELTA)
        corrida = corrida.map((v) => v * k)
      }
      const e = suya.map((v, i) => v + corrida[i])
      mirar(e[0], acotar(e[1], 0.05, 1.45), e[2], [e[3], e[4], e[5]], dx)
    }
  }
  p.alArrastrar = (dx, dy, desplaza) => {
    if (!sujeta) return
    if (desplaza) {
      const k = (sujeta[2] * 0.0011) / K.escala // lo que se arrastra, en unidades de la escena a esa distancia
      sujeta[3] -= Math.cos(sujeta[0]) * dx * k
      sujeta[5] += Math.sin(sujeta[0]) * dx * k
      sujeta[4] += dy * k
    } else {
      sujeta[0] -= (dx * 0.006) / K.escala
      sujeta[1] = acotar(sujeta[1] + (dy * 0.004) / K.escala, 0.05, 1.45)
    }
  }

  // Los camiones no se quedan quietos: mientras se apunta a uno, el tiempo de la escena se detiene para poder leerlo.
  if (lamina === 'flota') {
    const cuadro = escena.cuadro
    let atraso = 0, previo: number | null = null
    escena.cuadro = function (t, dt) {
      if (previo != null && t < previo) atraso = 0 // la escena volvió a empezar
      else if (previo != null && sobre != null) atraso += t - previo
      previo = t
      return cuadro.call(this, t - atraso, sobre != null ? 0 : dt)
    }
  }
}

// ---------- la roca ----------

function roca(K: DeckConMouse, escena: Escena, p: ReturnType<typeof puntero>) {
  const THREE = (window as unknown as { THREE: { Raycaster: new () => Rayo } }).THREE
  const rayo = new THREE.Raycaster()
  let ultimo: number | null = null // el último bloque apuntado: desde ahí sigue el recorrido

  // El punto del terreno que se ve bajo el mouse: se camina por el rayo hasta tocar el relieve (como `bloqueEn` del deck).
  const apuntado = (m: Terreno) => {
    rayo.setFromCamera({ x: (p.en!.x / 1920) * 2 - 1, y: 1 - (p.en!.y / 1080) * 2 }, m.tres.camera)
    const o = rayo.ray.origin, d = rayo.ray.direction
    for (let t = 20; t < 240; t += 0.2) {
      const x = o.x + d.x * t, z = o.z + d.z * t, i = m.bloqueBajo(x, z)
      if (i != null && o.y + d.y * t <= m.alturaDe(i)) return { i, x, z }
    }
    return null
  }

  const recorrido = escena.foco!
  escena.foco = function (this: Escena, t: number, dt?: number) {
    const m = this.m
    const a = m && p.en && !p.agarre && K.donde().paso === 0 ? apuntado(m) : null
    if (!m || !a) {
      if (ultimo != null && m && !p.agarre) { m.clic = ultimo; ultimo = null } // el mouse salió del terreno: el recorrido sigue desde ahí
      return recorrido.call(this, t, dt)
    }
    ultimo = a.i
    const T = m.T, c = this.colores![T.estado[a.i]], y = m.alturaDe(a.i)
    const v = this.v || (this.v = { bajo: T.bajo[a.i], medio: T.media[a.i], alto: T.alto[a.i], c: c.slice(), y })
    // la cifra sigue al bloque apuntado con la misma suavidad que en el recorrido: sin escalones entre bloques
    const q = K.quieto ? 1 : Math.min(1, (dt || 0.016) * 16)
    v.bajo += (T.bajo[a.i] - v.bajo) * q
    v.medio += (T.media[a.i] - v.medio) * q
    v.alto += (T.alto[a.i] - v.alto) * q
    for (let n = 0; n < 3; n++) v.c[n] += (c[n] - v.c[n]) * q
    v.y += (y - v.y) * q
    v.estado = T.estado[a.i]
    v.x = a.x
    v.z = a.z
    return v
  }

  // El terreno deja de mecerse mientras se apunta o se arrastra; cuando el mouse sale, el giro que se le dio se deshace.
  const cuadro = escena.cuadro
  escena.cuadro = function (this: Escena, t, dt) {
    const s = this.m?.s
    if (!s) return cuadro.call(this, t, dt)
    const fase = s.fase, fija = ultimo != null || p.agarre != null || p.tocado
    if (!fija) {
      const k = K.quieto ? 0 : Math.exp(-(dt || 0.016) * VUELTA)
      s.arrastre *= k
      s.arrastreEl *= k
    }
    cuadro.call(this, t, dt)
    if (fija) s.fase = fase
  }
}

export function conMouse(lamina: Lamina) {
  const K = window.K as unknown as DeckConMouse
  const escena = K.escenas[lamina], lienzo = K.gl.renderer?.domElement
  if (!escena || !lienzo || lamina === 'valor' || lamina === 'vision') return
  escena.interactivo = true // el lienzo del deck solo recibe el mouse en las escenas que lo piden
  lienzo.classList.add('interactivo')
  lienzo.style.cursor = 'grab'
  const p = puntero(lienzo)
  if (lamina === 'leyes') roca(K, escena, p)
  else lista(K, lamina, escena, p)
}
