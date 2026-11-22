// El inicio es la portada del deck (lámina 1, el rajo en relieve) con la acción principal encima: subir un archivo,
// o probar con el de ejemplo sin elegir nada antes. Debajo, la lámina de las seis preguntas (lámina 6), y bajo cada una,
// quién la toma en la minera y qué archivo se sube. En un teléfono o sin WebGL, lo mismo sin las escenas.

import LaminaDeck from './escena/LaminaDeck'
import { conEscena } from './soporte'
import { ZonaArchivo } from './Subir'
import type { Caso } from './tipos'

interface Props {
  casos: Caso[]
  alElegirArchivo: () => void
  alProbar: () => void
  alElegir: (c: Caso) => void
}

const PRUEBA = 'El de ejemplo es un banco de roca simulado: no son datos de ninguna minera.'
// Las seis columnas de la lámina de las preguntas: 110 px de margen a cada lado de 1920 (pitch/deck/deck.css, #l-vision .cinco).
const MARGEN = `${(110 / 1920) * 100}%`

export default function Inicio({ casos, alElegirArchivo, alProbar, alElegir }: Props) {
  const escena = conEscena()
  const zona = <ZonaArchivo alElegirArchivo={alElegirArchivo} alProbar={alProbar} prueba={PRUEBA} compacta={escena} />

  return (
    <main className="flex-1">
      {escena ? (
        <section className="relative">
          <LaminaDeck lamina="valor" datos={{}} titulo="Krylov, el Artificial Data Scientist de la minería" />
          <div className="absolute bottom-[4%] w-[46%]" style={{ left: MARGEN }}>
            {zona}
          </div>
        </section>
      ) : (
        <section className="px-4 pt-10 pb-12">
          <h1 className="titular text-8xl leading-[0.9]">Krylov</h1>
          <p className="titular mt-3 text-4xl">
            El <span className="text-cobre">Artificial Data Scientist</span> de la minería
          </p>
          <p className="mt-4 text-xl text-tinta-suave">Responde en milisegundos lo que a un especialista le toma horas de cálculo, y dice cuánto se puede equivocar.</p>
          <div className="mt-8">{zona}</div>
        </section>
      )}

      <section aria-labelledby="preguntas" className={escena ? 'relative' : 'px-4 pb-16'}>
        {escena ? (
          <div className="relative">
            <LaminaDeck lamina="vision" datos={{}} titulo="Una minera se pregunta esto todos los días" />
            <h2 id="preguntas" className="sr-only">
              Una minera se pregunta esto todos los días
            </h2>
            {/* cada columna de la lámina se puede tocar: abre esa decisión */}
            <div className="absolute inset-y-[24%] grid grid-cols-6" style={{ left: MARGEN, right: MARGEN }}>
              {casos.map((c) => (
                <button key={c.nombre} onClick={() => alElegir(c)} aria-label={c.titulo} className="transition-colors hover:bg-tinta/5" />
              ))}
            </div>
          </div>
        ) : (
          <h2 id="preguntas" className="titular mb-6 text-5xl">
            Una minera se pregunta esto todos los días.
          </h2>
        )}
        <ul className={`grid gap-6 ${escena ? 'grid-cols-6 gap-x-5 pb-16' : 'sm:grid-cols-2'}`} style={escena ? { paddingLeft: MARGEN, paddingRight: MARGEN } : undefined}>
          {casos.map((c) => (
            <li key={c.nombre} className="flex flex-col border-t border-linea pt-4">
              {!escena && <p className="titular text-3xl">{c.titulo}</p>}
              {c.quien && <p className="font-semibold">{c.quien}</p>}
              {c.archivo && <p className="mt-1 text-tinta-suave">{c.archivo}</p>}
              <button onClick={() => alElegir(c)} className="mt-4 self-start text-cobre underline decoration-cobre/40 underline-offset-4 hover:decoration-cobre">
                Responder con un archivo
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
