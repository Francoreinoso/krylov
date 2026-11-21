// Vista 1 · «¿Qué quieres saber?»: una pregunta por caso de uso, como entradas de una tabla.

import { lineaDelCaso } from './textos'
import type { Caso } from './tipos'

interface Props {
  casos: Caso[]
  alElegir: (caso: Caso) => void
}

export default function Inicio({ casos, alElegir }: Props) {
  return (
    <section>
      <h1 className="condensado text-5xl font-bold">¿Qué quieres saber?</h1>
      <ul className="mt-10 border-t border-linea">
        {casos.map((caso) => (
          <li key={caso.nombre} className="border-b border-linea">
            <button
              onClick={() => alElegir(caso)}
              className="group block w-full py-6 text-left"
            >
              <span className="block text-tinta-suave">
                {lineaDelCaso(caso)}
                {caso.sintetico && ', sintéticos'}
              </span>
              <span className="mt-1 block text-3xl font-semibold decoration-2 underline-offset-[6px] group-hover:underline group-focus-visible:underline">
                {caso.titulo}
              </span>
            </button>
          </li>
        ))}
      </ul>
      <p className="mt-8 text-sm text-tinta-suave">
        Casos de ejemplo con datos públicos. No son datos de estas empresas.
      </p>
    </section>
  )
}
