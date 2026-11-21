// El modelo con que se responde, dentro de la caja de texto: un botón que abre la lista hacia arriba.

import { useState } from 'react'
import { MOTOR_EN_PALABRAS } from './preguntas'
import { lineaDelCaso } from './textos'
import type { Caso } from './tipos'

interface Props {
  casos: Caso[]
  caso: Caso | null
  alElegir: (caso: Caso) => void
}

export default function SelectorModelo({ casos, caso, alElegir }: Props) {
  const [abierto, setAbierto] = useState(false)
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setAbierto(!abierto)}
        aria-expanded={abierto}
        className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm text-tinta-suave hover:bg-superficie hover:text-tinta"
      >
        {caso ? caso.empresa_o_industria : 'Elegir modelo'}
        <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
          <path d="M4 6l4 4 4-4" />
        </svg>
      </button>
      {abierto && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setAbierto(false)} />
          <ul className="absolute bottom-full left-0 z-40 mb-2 w-[min(22rem,80vw)] overflow-hidden rounded-2xl border border-linea bg-fondo p-1.5 shadow-(--sombra)">
            {casos.map((c) => (
              <li key={c.nombre}>
                <button
                  type="button"
                  onClick={() => {
                    alElegir(c)
                    setAbierto(false)
                  }}
                  className="flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left hover:bg-superficie"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-medium">{c.titulo}</span>
                    <span className="block text-xs text-tinta-suave">
                      {MOTOR_EN_PALABRAS[c.motor] ?? c.motor} · {lineaDelCaso(c)}
                    </span>
                  </span>
                  {caso?.nombre === c.nombre && <span className="text-acento">✓</span>}
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
