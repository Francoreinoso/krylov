// Qué puede mostrar este navegador: la escena del deck pide WebGL y una pantalla ancha; si no, va el respaldo.

export const hayWebgl = (() => {
  try {
    const c = document.createElement('canvas')
    return !!(c.getContext('webgl2') || c.getContext('webgl'))
  } catch {
    return false
  }
})()

export const ESCRITORIO = '(min-width: 900px)'
export const conEscena = () => hayWebgl && window.matchMedia(ESCRITORIO).matches
