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

export interface Medicion {
  x: number
  y: number
  valor: number
}

export interface Mapa {
  nx: number
  ny: number
  x0: number
  y0: number
  lado: number
  p: (number | null)[]
  media: (number | null)[]
  puntos: Medicion[]
  umbral: number
  unidad_valor: string
}

export interface Examen {
  tipo: string
  n: number
  frase: string
  tramos: { dijimos: number; paso: number; n: number }[]
}

export interface Nube {
  caso: string
  n_simulaciones: number
  ejes: Record<'x' | 'y', { nombre: string; min: number; max: number }>
  puntos: [number, number][]
  archivo: { x: number; y: number; dentro: boolean }
  detectores: { ejes_con_nombre: { dentro: boolean; motivo?: string } }
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
  mapa?: Mapa
  examen: Examen | null
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

export interface Candidata {
  puesto: number
  etiqueta: string
  x: number
  y: number
  valor_de_medir: number
  costo_medicion: number
  valor_neto: number
}

export interface DondeMedir {
  caso: string
  candidatas: Candidata[]
}

// D-34 y D-35: los papeles de columna de cada motor y el calce de un archivo.
export interface Papel {
  papel: string
  cantidad: number
  minimo: number
  maximo: number
  tipo: string
  texto: string
  texto_largo: string
}

export interface Papeles {
  motor_id: string
  caso_base: string
  papeles: Papel[]
}

export interface CalcePapel {
  columnas: string[]
  transformacion: { nombre: string; [k: string]: unknown } | null
  motivo: string
  confianza: 'alta' | 'media' | 'baja'
}

export interface Calce {
  caso: string
  motor_id: string
  calce: Record<string, CalcePapel>
  columnas: string[]
  no_usadas: string[]
  origen: 'equipo' | 'modelo' | 'regla'
  precalculado: boolean
}
