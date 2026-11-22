// El cronómetro de Krylov: cuánto tarda en responder un archivo, contado de verdad (performance.now()).
// No cuenta lo que la persona se demora en revisar las columnas: eso es tiempo suyo, no de Krylov.

export interface Reloj {
  soltado?: number // se soltó el archivo (o se pidió el demo)
  calce?: number // llegó la propuesta de columnas
  confirmado?: number // la persona confirmó y el archivo partió a la red
  respuesta?: number // llegó la respuesta
}

// Los milisegundos de Krylov hasta `ahora` (o hasta la respuesta, si ya llegó).
export function msDeKrylov(r: Reloj, ahora = performance.now()): number {
  if (r.soltado === undefined) return 0
  const leer = r.calce !== undefined ? r.calce - r.soltado : r.confirmado === undefined ? ahora - r.soltado : 0
  const responder = r.confirmado === undefined ? 0 : (r.respuesta ?? ahora) - r.confirmado
  return leer + responder
}

export const segundos = (ms: number, decimales = 1) => (ms / 1000).toLocaleString('es-CL', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
