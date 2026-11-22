// Lo que se dicen la app y el marco de la escena (marco.ts). Mismo origen: los mensajes son objetos, no texto.

// Las láminas del deck que la app abre: la portada, las seis preguntas y las cinco decisiones con motor.
export type Lamina = 'valor' | 'vision' | 'leyes' | 'taludes' | 'flotacion' | 'flota' | 'sismicidad'

export type AlMarco =
  | { tipo: 'escena'; lamina: Lamina; datos: unknown; config: unknown; paso?: number }
  | { tipo: 'paso'; paso: number }
  | { tipo: 'pausa'; si: boolean }
  | { tipo: 'perforar'; letra: string; capa: Record<string, unknown>; valor: number }

export type DelMarco = { tipo: 'esperando' } | { tipo: 'lista' } | { tipo: 'falla'; mensaje: string } | { tipo: 'tecla'; tecla: string }
