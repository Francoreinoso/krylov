// Formas de las respuestas de la API (contratos/CONTRATO.md, sección 6).

export type Estado = 'actuar' | 'no_actuar' | 'en_duda'
export type Semaforo = 'verde' | 'amarillo' | 'rojo_datos' | 'rojo_modelo'
export type Certeza = 'seguro' | 'probable' | 'no_se_sabe'

export interface Caso {
  nombre: string
  titulo: string
  empresa_o_industria: string
  sponsor: string | null
  motor: string
  sintetico: boolean
  origen_datos: string
  tiene_cartera: boolean
}

export interface Casos {
  casos: Caso[]
}

export interface Costo {
  valor: number
  min: number
  max: number
  etiqueta: string
}

export interface Unidad {
  id: string
  etiqueta: string
  p: number
  rango_bajo: number
  rango_alto: number
  muestras_p: number[]
  estado: Estado
  duda: number
}

export interface Factor {
  nombre: string
  etiqueta: string
  direccion: 'sube' | 'baja'
  efecto: number
  rango_bajo: number
  rango_alto: number
  certeza: Certeza
}

export interface Analisis {
  caso: string
  motor_id: string
  implementacion: 'red' | 'mcmc'
  precalculado: boolean
  titular: string
  costo_de_no_saber: { valor: number; moneda: string } | null
  costos: { falso_si: Costo; falso_no: Costo }
  punto_de_corte: number
  unidades: Unidad[] | null
  resumen_colores: Record<Estado, number> | null
  factores: Factor[] | null
  semaforo: {
    estado: Semaforo
    motivo: string
    propuesta: { transformacion: string; texto: string } | null
  }
  sello_resumen: { frase: string; medido: boolean }
  rotulos: Record<Estado | 'costo_de_no_saber', string>
  registro: string[]
  tiempo_ms: number
  sintetico: boolean
  origen_datos: string
}
