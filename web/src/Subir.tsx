// Subir el archivo es lo primero que se hace en Krylov: la caja para soltarlo, la pantalla de una decisión (desde el
// inicio o desde el deck con la tecla D) y la pregunta «¿qué decisión es?» cuando el archivo llegó primero.

import type { Archivo } from './App'
import type { Caso } from './tipos'

export function ZonaArchivo({ alElegirArchivo, alProbar, prueba, compacta = false }: { alElegirArchivo: () => void; alProbar: () => void; prueba: string; compacta?: boolean }) {
  return (
    <div className={`border-2 border-dashed border-cobre/70 bg-fondo/80 ${compacta ? 'px-6 py-5' : 'px-8 py-8'}`}>
      <p className={`titular ${compacta ? 'text-4xl' : 'text-5xl'}`}>Sube el archivo de tu decisión</p>
      <p className="mt-2 text-tinta-suave">Un CSV, como sale de tu planilla. Arrástralo aquí o elígelo.</p>
      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3">
        <button onClick={alElegirArchivo} className="bg-cobre px-6 py-3 text-lg font-semibold text-fondo transition-opacity hover:opacity-90">
          Elegir archivo
        </button>
        <button onClick={alProbar} className="border border-linea px-5 py-3 text-lg transition-colors hover:border-cobre">
          Probar con un archivo de ejemplo
        </button>
      </div>
      <p className="mt-3 text-sm text-tenue">{prueba}</p>
    </div>
  )
}

// Una decisión elegida: quién la toma, qué archivo se sube, y el de ejemplo a un clic.
export function PantallaDecision({ caso, alElegirArchivo, alProbar, alVerDemo }: { caso: Caso; alElegirArchivo: () => void; alProbar: () => void; alVerDemo: () => void }) {
  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col justify-center px-4 py-12 sm:px-8">
      {caso.quien && <p className="entra text-lg text-cobre">Lo decide: {caso.quien}</p>}
      <h1 className="titular sube mt-2 text-6xl sm:text-7xl">{caso.titulo}</h1>
      {caso.archivo && <p className="entra mt-4 max-w-2xl text-xl text-tinta-suave">{caso.archivo}</p>}
      <div className="entra mt-10" style={{ animationDelay: '120ms' }}>
        <ZonaArchivo alElegirArchivo={alElegirArchivo} alProbar={alProbar} prueba="El archivo de ejemplo es simulado: no son datos de ninguna minera." />
      </div>
      <button onClick={alVerDemo} className="entra mt-6 self-start text-lg text-tinta-suave underline decoration-linea underline-offset-4 hover:text-tinta" style={{ animationDelay: '200ms' }}>
        O ver la respuesta con los datos del demo
      </button>
    </main>
  )
}

// El archivo llegó sin decisión: Krylov no adivina cuál es (ni un modelo de lenguaje la elige); la elige la persona.
export function ElegirDecision({ archivo, casos, alElegir }: { archivo: Archivo; casos: Caso[]; alElegir: (c: Caso) => void }) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-12 sm:px-8">
      <h1 className="titular sube text-6xl">¿Qué decisión es?</h1>
      <p className="entra mt-3 text-xl text-tinta-suave">
        Krylov leyó {archivo.nombre}: {archivo.filas.toLocaleString('es-CL')} filas y {archivo.columnas.length} columnas ({archivo.columnas.slice(0, 5).join(', ')}
        {archivo.columnas.length > 5 ? '…' : ''}). Elige qué pregunta responde.
      </p>
      <ul className="mt-8 grid gap-3 sm:grid-cols-2">
        {casos.map((c, i) => (
          <li key={c.nombre} className="entra" style={{ animationDelay: `${i * 50}ms` }}>
            <button onClick={() => alElegir(c)} className="h-full w-full border border-linea p-5 text-left transition-colors hover:border-cobre">
              <span className="titular block text-3xl">{c.titulo}</span>
              {c.quien && <span className="mt-2 block text-tinta-suave">Lo decide: {c.quien}</span>}
            </button>
          </li>
        ))}
      </ul>
    </main>
  )
}
