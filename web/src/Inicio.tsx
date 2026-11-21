// Vista 1 · «¿Qué quieres saber?»: una tarjeta por caso de uso.

import type { Caso } from './tipos'

interface Props {
  casos: Caso[]
  alElegir: (caso: Caso) => void
}

export default function Inicio({ casos, alElegir }: Props) {
  return (
    <section>
      <h1 className="text-4xl font-semibold tracking-tight">¿Qué quieres saber?</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {casos.map((caso) => (
          <button
            key={caso.nombre}
            onClick={() => alElegir(caso)}
            className="rounded-2xl border border-stone-200 bg-white p-6 text-left shadow-sm transition hover:border-stone-400 hover:shadow"
          >
            <p className="text-sm text-stone-500">
              {caso.sponsor
                ? `${caso.empresa_o_industria} · datos públicos de ejemplo`
                : caso.empresa_o_industria}
            </p>
            <p className="mt-2 text-xl font-medium">{caso.titulo}</p>
            {caso.sintetico && <p className="mt-2 text-xs text-stone-500">Datos sintéticos</p>}
          </button>
        ))}
      </div>
    </section>
  )
}
