// La barra lateral: nuevo análisis, las cinco decisiones con su dibujo y quién responde, y las
// conversaciones de esta sesión (solo en memoria).

import Decisiones, { type Quien } from './Decisiones'
import Marca, { Logotipo } from './Marca'
import type { Caso } from './tipos'

export interface Reciente {
  id: number
  titulo: string
}

interface Props {
  casos: Caso[]
  quien: Record<string, Quien>
  activo: string | null
  recientes: Reciente[]
  activa: number
  alNuevo: () => void
  alElegirModelo: (c: Caso) => void
  alAbrir: (id: number) => void
  alCerrar?: () => void
}

export function IconoLateral() {
  return (
    <svg viewBox="0 0 20 20" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden>
      <rect x="3" y="4" width="14" height="12" />
      <path d="M8 4v12" />
    </svg>
  )
}

export default function Lateral({ casos, quien, activo, recientes, activa, alNuevo, alElegirModelo, alAbrir, alCerrar }: Props) {
  const fila = 'block w-full truncate px-3 py-2 text-left text-sm hover:bg-linea/40'
  return (
    <aside className="flex h-full w-80 flex-col border-r border-linea bg-superficie/95 px-3 py-4 backdrop-blur">
      <div className="flex items-center justify-between px-2">
        <button onClick={alNuevo} className="flex items-center gap-2.5">
          <Marca />
          <Logotipo className="text-xl" />
        </button>
        {alCerrar && (
          <button onClick={alCerrar} title="Cerrar la barra" aria-label="Cerrar la barra" className="p-1.5 text-tinta-suave hover:bg-linea/60 hover:text-tinta">
            <IconoLateral />
          </button>
        )}
      </div>

      <button onClick={alNuevo} className="mx-2 mt-5 border border-linea px-3 py-2 text-left text-sm hover:border-acento">
        + Nuevo análisis
      </button>

      <nav className="desliza-lista mt-6 min-h-0 flex-1 overflow-y-auto">
        <p className="dato px-2 pb-2">Decisiones de la mina</p>
        <Decisiones casos={casos} quien={quien} activo={activo} alElegir={alElegirModelo} forma="lista" />

        {recientes.length > 0 && (
          <>
            <p className="dato mt-6 px-2 pb-1">Esta sesión</p>
            <ul>
              {recientes.map((r) => (
                <li key={r.id}>
                  <button onClick={() => alAbrir(r.id)} className={`${fila} ${r.id === activa ? 'bg-linea/50 text-tinta' : 'text-tinta-suave'}`}>
                    {r.titulo}
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      <p className="dato px-2 pt-3">Datos simulados · los costos son supuestos</p>
    </aside>
  )
}
