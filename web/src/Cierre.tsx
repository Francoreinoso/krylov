// Tecla L: la lámina de cierre del demo (WORKPLAN.md 4.3, paso 11). La frase, el QR y la dirección
// de la URL pública. El QR es un archivo fijo (public/qr.svg), dibujado con la librería del deck.

import Particulas from './Particulas'

const FRASE = 'Krylov sabe cuánto no sabe, y te dice cuánto vale averiguarlo.'
const SEGUNDA = 'En un segundo, porque ya practicó con millones de minas simuladas.'
const DIRECCION = 'krylov-tan.vercel.app'

export default function Cierre({ alCerrar }: { alCerrar: () => void }) {
  return (
    <div className="fixed inset-0 z-[60] overflow-y-auto bg-fondo" role="dialog" aria-label="Cierre" onClick={alCerrar}>
      <Particulas className="pointer-events-none absolute inset-0 h-full w-full opacity-60" />
      <div className="relative mx-auto flex min-h-full max-w-7xl flex-col justify-center gap-10 px-4 py-10 sm:px-10 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-3xl">
          <h1 className="titular text-[5rem] leading-[0.85] sm:text-[8rem]">Krylov</h1>
          <p className="titular mt-6 text-4xl leading-[1.05] sm:text-6xl">{FRASE}</p>
          <p className="mt-5 text-xl text-tinta-suave sm:text-2xl">{SEGUNDA}</p>
        </div>
        <figure className="shrink-0 text-center">
          <img src={`${import.meta.env.BASE_URL}qr.svg`} alt={`Código QR a ${DIRECCION}`} className="mx-auto h-64 w-64 sm:h-80 sm:w-80" />
          <figcaption className="dato mt-4 text-base">{DIRECCION}</figcaption>
        </figure>
      </div>
    </div>
  )
}
