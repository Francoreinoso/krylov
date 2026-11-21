// Pie de la respuesta: quién respondió, de dónde vienen los datos y qué tan medido está.

import { quienRespondio } from './textos'
import type { Analisis } from './tipos'

export default function Pie({ analisis }: { analisis: Analisis }) {
  const quien = `${quienRespondio(analisis)}.`

  return (
    <footer className="mt-6 flex flex-wrap gap-x-6 gap-y-1 border-t border-linea pt-3 text-sm text-tinta-suave">
      <span>{quien}</span>
      <span>
        {analisis.origen_datos}
        {analisis.sintetico && '. Datos sintéticos'}
      </span>
      {analisis.sello_resumen.frase && <span>{analisis.sello_resumen.frase}</span>}
    </footer>
  )
}
