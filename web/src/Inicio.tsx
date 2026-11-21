// Vista 1 · «¿Qué quieres saber?»: la frase de Krylov y una pregunta por caso de uso, como
// entradas de una tabla.

import { lineaDelCaso } from './textos'
import type { Caso } from './tipos'

interface Props {
  casos: Caso[]
  alElegir: (caso: Caso) => void
}

export default function Inicio({ casos, alElegir }: Props) {
  return (
    <section className="max-w-4xl">
      <p className="max-w-[40ch] text-xl text-tinta-suave">
        Modelos que exigían un especialista y horas de cómputo, ahora en un segundo y para quien decide.
      </p>
      <h1 className="condensado mt-4 text-5xl font-bold">¿Qué quieres saber?</h1>
      <ul className="mt-5 border-t border-linea">
        {casos.map((caso) => (
          <li key={caso.nombre} className="border-b border-linea">
            <button onClick={() => alElegir(caso)} className="group block w-full py-3 text-left">
              <span className="block text-tinta-suave">
                {lineaDelCaso(caso)}
                {caso.sintetico && ', sintéticos'}
              </span>
              <span className="mt-0.5 block text-2xl font-semibold sm:text-3xl decoration-en-duda decoration-2 underline-offset-[6px] group-hover:underline group-focus-visible:underline">
                {caso.titulo}
              </span>
            </button>
          </li>
        ))}
      </ul>
      <p className="mt-4 text-sm text-tinta-suave">
        Casos de ejemplo con datos públicos. No son datos de estas empresas.
      </p>
    </section>
  )
}
