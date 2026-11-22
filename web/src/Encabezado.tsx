// Arriba, siempre: la marca (vuelve al inicio) y la decisión en curso.

import Marca, { Logotipo } from './Marca'

export default function Encabezado({ titulo, alInicio }: { titulo: string | null; alInicio: () => void }) {
  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-linea/70 px-4 sm:px-6">
      <button onClick={alInicio} className="flex items-center gap-2.5" aria-label="Volver al inicio">
        <Marca />
        <Logotipo className="text-xl" />
      </button>
      {titulo && <p className="min-w-0 flex-1 truncate text-center text-tinta-suave">{titulo}</p>}
    </header>
  )
}
