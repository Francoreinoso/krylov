// Formas de las respuestas de la API (contratos/CONTRATO.md, sección 6).

export type Estado = 'actuar' | 'no_actuar' | 'en_duda'
export type Semaforo = 'verde' | 'amarillo' | 'rojo_datos' | 'rojo_modelo'
export type Certeza = 'seguro' | 'probable' | 'no_se_sabe'

export interface Caso {
  nombre: string
  titulo: string
  empresa_o_industria: string
  motor: string
  sintetico: boolean
  origen_datos: string
  quien?: string | null // quién toma esta decisión en la minera (casos/<caso>.yaml, tarjeta.quien)
  archivo?: string | null // qué archivo se sube para responderla (tarjeta.archivo)
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
  curva?: Curva | null
  // D-42, opcionales: la API anterior no los trae y entonces la app dibuja el respaldo, no la escena del deck.
  posteriori?: Posteriori // lo que se decide en esa unidad: la distribución entera, en 64 cuantiles
  serie?: [number, number][] // lo que se leyó de esa unidad, tal cual: [tiempo, valor]
}

export interface Posteriori {
  bajo: number
  medio: number
  alto: number
  muestras: number
  cuantiles: number[]
}

// D-42: lo del caso que dibuja su escena (casos/<caso>.yaml, columnas).
export interface EscenaDelCaso {
  umbral?: number
  horizonte?: number
  tiempo_final?: number
  unidad_tiempo?: string
  unidad_valor?: string
  eje_tiempo?: string
  eje_valor?: string
}

// D-37: lo medido de una unidad y lo que Krylov cree que viene (CONTRATO.md, sección 6).
export interface Curva {
  t: number[]
  y: number[]
  ahora: number
  t_banda: number[]
  bajo: number[]
  medio: number[]
  alto: number[]
  limite: number | null
  eje_t: string
  eje_y: string
  marca?: { texto: string; bajo: number; medio: number; alto: number } | null
}

// Los textos de pantalla que la web dibuja por su cuenta (casos/textos.yaml, GET /api/textos).
export interface Textos {
  curva: Record<'titulo' | 'medido' | 'ahora' | 'abanico' | 'limite' | 'falta' | 'sin_curva', string> & { fuera?: string } // fuera: el abanico sale del gráfico
  // El botón del archivo de prueba y la frase de una decisión que todavía no responde archivos propios.
  chat?: Partial<Record<'probar_archivo' | 'no_disponible', string>>
  // La sexta decisión (D-40): su recorrido calculado antes, o la respuesta de su red a un archivo subido.
  yacimiento?: Partial<TextosYacimiento>
}
export type TextosYacimiento = Record<'titulo' | 'quien' | 'archivo' | 'ver' | 'que_es' | 'sello' | 'angosto' | 'subir' | 'con_archivo' | 'de_ejemplo' | 'guardada', string>

// Lo que dibuja la página del yacimiento (pitch/deck/yacimiento.html): la respuesta de la red para cada bloque, en un
// byte por bloque. Con un archivo subido viene de `servicio/yacimiento.py`, sin examen (`acierto_decididos: null`).
export interface DatosYacimiento {
  dim: [number, number, number]
  red: Record<'media' | 'desv' | 'p', string>
  numeros: { compositos: number; bloques: number; colores: Record<Estado, number>; acierto_decididos: number | null; [k: string]: unknown }
  [k: string]: unknown
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
  bajo?: (number | null)[] // D-42: los extremos del intervalo de 90% de cada bloque
  alto?: (number | null)[]
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
  escena?: EscenaDelCaso
  examen: Examen | null
  semaforo: {
    estado: Semaforo
    motivo: string
    propuesta: { transformacion: string; texto: string } | null
  }
  sello_resumen: { frase: string; medido: boolean }
  rotulos: Record<Estado | 'costo_de_no_saber', string> & { donde_medir?: string }
  unidad: { singular: string; plural: string }
  en_palabras: string[]
  registro: string[]
  tiempo_ms: number
  sintetico: boolean
  origen_datos: string
  yacimiento?: DatosYacimiento | null // solo en la sexta decisión: su respuesta tiene forma propia y el resto de los campos no viene
  _aviso?: string // solo en el ejemplo fijo (contratos/ejemplos/), cuando el motor todavía no responde
}

export interface Candidata {
  puesto: number
  etiqueta: string
  x: number
  y: number
  valor_de_medir: number
  costo_medicion: number
  valor_neto: number
  resultados_posibles?: { bajo: number; medio: number; alto: number }
}

export interface DondeMedir {
  caso: string
  candidatas: Candidata[]
  lugares?: { x: number; y: number; valor_de_medir: number }[] // D-42: todos los lugares que se probaron
  analisis_rehechos?: number
  tiempo_ms?: number
  precalculado?: boolean // se sirve desde el estático: tarda más de 2 s en vivo
}

// Una muestra simulada en un pin de «¿Dónde perforo?».
export interface MedicionNueva {
  x: number
  y: number
  valor: number
  etiqueta: string
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
  caso: string | null // null en un archivo propio
  motor_id: string
  calce: Record<string, CalcePapel>
  columnas: string[]
  no_usadas: string[]
  origen: 'equipo' | 'modelo' | 'regla'
  proveedor?: Proveedor | null // quién escribió la propuesta, cuando la hizo un modelo de lenguaje (API anterior)
  propuesto_por?: PropuestoPor | null // D-42: quién la propuso, dicho por la API
  precalculado: boolean
}

// D-41: en Render escribe Groq; en local puede escribir cualquiera de los dos.
export type Proveedor = 'claude' | 'groq'

export interface PropuestoPor {
  tipo: 'modelo' | 'regla' | 'plantilla' | 'equipo'
  proveedor?: string | null
  modelo?: string | null
}

// D-34: el texto corto que acompaña a una respuesta. Sus números salen del JSON del motor.
export interface Interpretacion {
  texto: string
  origen: 'modelo' | 'plantilla'
  proveedor: Proveedor | null
  propuesto_por?: PropuestoPor | null // D-42: quién la escribió, dicho por la API
  precalculado: boolean
}
