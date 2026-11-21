// Selector de diseño para comparar en local, fijo abajo a la derecha. La tecla V pasa al siguiente.

import { useEffect, useState } from 'react'
import { aplicarDiseno, DISENOS, siguienteDiseno, useDiseno, type Diseno } from './disenos'

function Muestra({ diseno }: { diseno: Diseno }) {
  const [fondo, tinta, acento] = diseno.muestra
  return (
    <span className="flex h-4 w-7 shrink-0 overflow-hidden border border-linea" aria-hidden>
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
      if (e.key === 'v' || e.key === 'V') siguienteDiseno()
      if (e.key === 'Escape') setAbierto(false)
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  }, [])

  return (
    <div className="fixed top-2.5 right-3 z-50 text-sm lg:top-auto lg:bottom-3">
      {abierto && (
        <ul className="absolute top-full right-0 mt-2 w-72 border border-linea bg-superficie lg:static lg:mt-0 lg:mb-2">
          {DISENOS.map((d) => (
            <li key={d.id}>
              <button
                onClick={() => {
                  aplicarDiseno(d.id)
                  setAbierto(false)
                }}
                className={`flex w-full items-center gap-3 px-3 py-2.5 text-left hover:bg-fondo ${d.id === actual.id ? 'text-cobre' : ''}`}
              >
                <Muestra diseno={d} />
                <span>
                  <span className="block font-medium">{d.nombre}</span>
                  <span className="block text-xs text-tinta-suave">{d.descripcion}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
      <button
        onClick={() => setAbierto(!abierto)}
        aria-expanded={abierto}
        title="Cambiar diseño (tecla V)"
        className="ml-auto flex items-center gap-2 border border-linea bg-superficie px-2.5 py-1.5"
      >
        <Muestra diseno={actual} />
        <span className="hidden font-mono text-xs sm:inline">{actual.nombre}</span>
      </button>
    </div>
  )
}
