// Tecla L: el cierre. El mismo título y el mismo cuerpo de la lámina de cierre del deck (lámina 14), y el QR a esta
// misma app. El QR es un archivo fijo (public/qr.svg), dibujado con la biblioteca del deck.

import Topografia from './Topografia'

const DIRECCION = 'krylov-krylov.vercel.app'

export default function Cierre({ alCerrar }: { alCerrar: () => void }) {
  return (
    <div className="fixed inset-0 z-[60] overflow-y-auto bg-fondo" role="dialog" aria-modal="true" aria-labelledby="cierre-titulo" onClick={alCerrar}>
      <Topografia />
      <div className="relative mx-auto flex min-h-full max-w-[110rem] flex-col justify-center gap-12 px-6 py-12 sm:px-16 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-5xl">
          <h1 id="cierre-titulo" className="titular sube text-6xl leading-[0.95] sm:text-8xl">
            Decidir con el mejor modelo ya no toma horas. <span className="text-cobre">Toma lo que demora subir un archivo.</span>
          </h1>
          <p className="entra mt-8 max-w-3xl text-2xl text-tinta-suave" style={{ animationDelay: '300ms' }}>
            Krylov es el Artificial Data Scientist de la minería: seis decisiones respondidas hoy, con Bayesian Amortized Inference por dentro.
          </p>
        </div>
        <figure className="entra shrink-0 text-center" style={{ animationDelay: '600ms' }}>
          <img src={`${import.meta.env.BASE_URL}qr.svg`} alt={`Código QR a ${DIRECCION}`} className="mx-auto h-64 w-64 bg-tinta p-3 sm:h-80 sm:w-80" />
          <figcaption className="mt-4">
            <span className="titular block text-4xl">Pruébalo</span>
            <span className="font-mono text-lg text-tinta-suave">{DIRECCION}</span>
          </figcaption>
        </figure>
      </div>
    </div>
  )
}
