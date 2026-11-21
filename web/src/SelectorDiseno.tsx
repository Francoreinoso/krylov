// Selector de diseño, fijo abajo a la derecha. La tecla D pasa al siguiente.

import { useEffect, useState } from 'react'
import { aplicarDiseno, DISENOS, siguienteDiseno, useDiseno, type Diseno } from './disenos'

function Muestra({ diseno }: { diseno: Diseno }) {
  const [fondo, tinta, acento] = diseno.muestra
  return (
    <span className="flex h-5 w-8 shrink-0 overflow-hidden rounded-sm border border-linea" aria-hidden>
      <span className="flex-1" style={{ background: fondo }} />
      <span className="flex-1" style={{ background: tinta }} />
      <span className="flex-1" style={{ background: acento }} />
    </span>
  )
}

export default function SelectorDiseno() {
  const actual = useDiseno()
  const [abierto, setAbierto] = useState(false)

  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      const escribiendo = e.target instanceof HTMLElement && e.target.closest('input, textarea, select')
      if (escribiendo || e.metaKey || e.ctrlKey || e.altKey) return
      if (e.key === 'd' || e.key === 'D') siguienteDiseno()
      if (e.key === 'Escape') setAbierto(false)
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  }, [])

  return (
    <div className="fixed right-3 bottom-3 z-50 text-sm">
      {abierto && (
        <ul className="mb-2 w-64 overflow-hidden rounded-(--radio) border border-linea bg-superficie shadow-(--sombra)">
          {DISENOS.map((d) => (
            <li key={d.id}>
              <button
                onClick={() => {
                  aplicarDiseno(d.id)
                  setAbierto(false)
                }}
                className={`flex w-full items-center gap-3 px-3 py-2 text-left hover:bg-fondo ${d.id === actual.id ? 'font-semibold' : ''}`}
              >
                <Muestra diseno={d} />
                <span>
                  <span className="block">{d.nombre}</span>
                  <span className="block text-xs font-normal text-tinta-suave">{d.descripcion}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <button
        onClick={() => setAbierto(!abierto)}
        aria-expanded={abierto}
        title="Cambiar diseño (tecla D)"
        className="ml-auto flex items-center gap-2 rounded-(--radio) border border-linea bg-superficie px-2.5 py-1.5 shadow-(--sombra)"
      >
        <Muestra diseno={actual} />
        <span className="hidden sm:inline">{actual.nombre}</span>
      </button>
    </div>
  )
}
