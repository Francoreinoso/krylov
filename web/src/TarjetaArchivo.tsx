// Un CSV adjunto, como ficha: en la caja de texto antes de enviar y sobre el mensaje enviado.

import type { InfoCsv } from './csv'

export default function TarjetaArchivo({ info, alQuitar }: { info: InfoCsv; alQuitar?: () => void }) {
  return (
    <div className="relative inline-flex max-w-full items-center gap-3 rounded-[2px] border border-linea bg-fondo py-2 pr-4 pl-2 text-left">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[2px] bg-acento text-xs font-bold text-sobre-acento">CSV</span>
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium">{info.nombre}</span>
        <span className="block text-xs text-tinta-suave">
          {info.filas.toLocaleString('es-CL')} filas · {info.columnas.length} columnas
        </span>
      </span>
      {alQuitar && (
        <button
          type="button"
          onClick={alQuitar}
          aria-label="Quitar el archivo"
          className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-tinta text-xs text-fondo"
        >
          ×
        </button>
      )}
    </div>
  )
}
