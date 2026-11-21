// Pie de la respuesta: quién respondió, de dónde vienen los datos y qué tan medido está.

import type { Analisis } from './tipos'

export default function Pie({ analisis }: { analisis: Analisis }) {
  const quien = analisis.precalculado
    ? 'Precalculado con el método lento de siempre.'
    : 'Respondió la red que practicó con casos simulados.'

  return (
    <footer className="mt-12 border-t border-linea pt-4 text-sm text-tinta-suave">
      <p>
        {quien} {analisis.origen_datos}
        {analisis.sintetico && ' Datos sintéticos.'}
      </p>
      {analisis.sello_resumen.frase && <p className="mt-1">{analisis.sello_resumen.frase}</p>}
    </footer>
  )
}
