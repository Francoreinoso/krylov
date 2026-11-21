// La barra lateral: nuevo análisis, los modelos y las conversaciones de esta sesión (solo en memoria).

import Marca from './Marca'
import { lineaDelCaso } from './textos'
import type { Caso } from './tipos'

export interface Reciente {
  id: number
  titulo: string
}

interface Props {
  casos: Caso[]
  recientes: Reciente[]
  activa: number
  alNuevo: () => void
  alElegirModelo: (c: Caso) => void
  alAbrir: (id: number) => void
  alCerrar: () => void
}

export function IconoLateral() {
  return (
    <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
      <rect x="3" y="4" width="14" height="12" rx="2.5" />
      <path d="M8 4v12" />
    </svg>
  )
}

export default function Lateral({ casos, recientes, activa, alNuevo, alElegirModelo, alAbrir, alCerrar }: Props) {
  const fila = 'block w-full truncate rounded-xl px-3 py-2 text-left text-sm hover:bg-linea/60'
  return (
    <aside className="flex h-full w-72 flex-col bg-superficie px-3 py-3">
      <div className="flex items-center justify-between px-1">
        <span className="flex items-center gap-2.5 text-lg font-semibold">
          <Marca />
          Krylov
        </span>
        <button onClick={alCerrar} title="Cerrar la barra" aria-label="Cerrar la barra" className="rounded-lg p-1.5 text-tinta-suave hover:bg-linea/60 hover:text-tinta">
          <IconoLateral />
        </button>
      </div>

      <button onClick={alNuevo} className="mt-4 flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm font-medium hover:bg-linea/60">
        <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden>
          <path d="M14 3.5l2.5 2.5L8 14.5l-3.5 1 1-3.5z" />
        </svg>
        Nuevo análisis
      </button>

      <nav className="desliza-lista mt-5 min-h-0 flex-1 overflow-y-auto">
        <p className="px-3 pb-1 text-xs font-medium text-tinta-suave">Modelos</p>
        <ul>
          {casos.map((c) => (
            <li key={c.nombre}>
              <button onClick={() => alElegirModelo(c)} className={fila} title={c.titulo}>
                {c.titulo}
                <span className="block truncate text-xs text-tinta-suave">{lineaDelCaso(c)}</span>
              </button>
            </li>
          ))}
        </ul>

        {recientes.length > 0 && (
          <>
            <p className="mt-5 px-3 pb-1 text-xs font-medium text-tinta-suave">Esta sesión</p>
            <ul>
              {recientes.map((r) => (
                <li key={r.id}>
                  <button onClick={() => alAbrir(r.id)} className={`${fila} ${r.id === activa ? 'bg-linea/70 font-medium' : ''}`}>
                    {r.titulo}
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      <a href={`/clasico${window.location.search}`} className="mt-2 rounded-xl px-3 py-2 text-sm text-tinta-suave hover:bg-linea/60 hover:text-tinta">
        Vista clásica ↗
      </a>
    </aside>
  )
}
