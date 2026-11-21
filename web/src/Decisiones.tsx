// Las cinco decisiones de la mina, como la lámina 7 del deck: el dibujo de lo que mira cada una,
// la pregunta en grande y quién la responde hoy. Todo texto sale del caso.

import FiguraMina from './FiguraMina'
import Ilustracion from './Ilustracion'
import { MOTOR_EN_PALABRAS } from './preguntas'
import type { Caso } from './tipos'

export interface Quien {
  texto: string
  corto: string
  clase: string
  borde: string
}

interface Props {
  casos: Caso[]
  quien: Record<string, Quien>
  alElegir: (c: Caso) => void
  activo?: string | null
  forma?: 'fila' | 'grilla' | 'lista'
  desactivadas?: boolean
}

export default function Decisiones({ casos, quien, alElegir, activo = null, forma = 'fila', desactivadas = false }: Props) {
  if (forma === 'lista') {
    return (
      <ul className="space-y-1">
        {casos.map((c) => (
          <li key={c.nombre}>
            <button
              onClick={() => alElegir(c)}
              disabled={desactivadas}
              aria-current={activo === c.nombre}
              className={`grid w-full grid-cols-[4.5rem_1fr] items-center gap-3 border-l-2 py-2 pr-2 pl-2 text-left transition-colors hover:bg-linea/40 disabled:opacity-50 ${
                activo === c.nombre ? 'border-acento bg-linea/40' : 'border-transparent'
              }`}
            >
              <Ilustracion motor={c.motor} className="h-11 w-full" />
              <span className="min-w-0">
                <span className="titular block text-xl leading-tight">{c.titulo}</span>
                <span className={`dato mt-0.5 block ${quien[c.nombre]?.clase ?? ''}`}>{quien[c.nombre]?.corto ?? ' '}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    )
  }

  return (
    <ul className={`grid gap-x-5 gap-y-6 ${forma === 'fila' ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-5' : 'grid-cols-2 xl:grid-cols-3'}`}>
      {casos.map((c) => (
        <li key={c.nombre} className="min-w-0">
          <button
            onClick={() => alElegir(c)}
            disabled={desactivadas}
            className="group flex h-full w-full flex-col text-left disabled:opacity-50"
          >
            <FiguraMina motor={c.motor} className="aspect-[4/3] w-full transition-transform duration-300 group-enabled:group-hover:-translate-y-1" />
            <span className={`mt-3 block border-t pt-3 transition-colors ${activo === c.nombre ? 'border-acento' : `${quien[c.nombre]?.borde ?? 'border-linea'} group-enabled:group-hover:border-cobre`}`}>
              <span className="titular block text-2xl leading-[1.02] sm:text-[1.7rem]">{c.titulo}</span>
              <span className="mt-1.5 block text-sm leading-snug text-tinta-suave">{MOTOR_EN_PALABRAS[c.motor] ?? c.empresa_o_industria}</span>
              <span className={`dato mt-2 block ${quien[c.nombre]?.clase ?? ''}`}>{quien[c.nombre]?.texto ?? ' '}</span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
