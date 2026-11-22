// El viaje de un archivo hasta la respuesta: a la izquierda, sus filas como puntos (Coreografia); a la derecha, lo que
// toca en cada momento: el calce de columnas, la espera con el cronómetro, o por qué Krylov no responde.

import { useEffect, useRef, useState } from 'react'
import type { Archivo } from './App'
import Calce from './Calce'
import type { Asignacion } from './asignacion'
import Coreografia, { type Fase, type Orden } from './Coreografia'
import { msDeKrylov, segundos, type Reloj } from './reloj'
import type { Calce as DatosCalce, Caso, Papel } from './tipos'

interface Props {
  caso: Caso
  archivo: Archivo | null
  calce: DatosCalce | null
  papeles: Papel[]
  fase: Fase
  n: number
  orden: Orden
  motivo: string | null
  reloj: Reloj
  alConfirmar: (a: Asignacion) => void
  alProbar: () => void
  alOtroArchivo: () => void
}

const DORMIDO_MS = 4000 // pasado esto, lo más probable es que el servidor gratuito esté despertando

// El cronómetro corre de verdad: es el tiempo de Krylov, sin lo que la persona tarda en revisar las columnas.
export function Cronometro({ reloj, corre, className = '' }: { reloj: Reloj; corre: boolean; className?: string }) {
  const texto = useRef<HTMLSpanElement>(null)
  useEffect(() => {
    let cuadro = 0
    const pintar = () => {
      if (texto.current) texto.current.textContent = `${segundos(msDeKrylov(reloj))} s`
      if (corre) cuadro = requestAnimationFrame(pintar)
    }
    pintar()
    return () => cancelAnimationFrame(cuadro)
  }, [reloj, corre])
  return <span ref={texto} className={`titular tabular-nums ${className}`} />
}

export default function Viaje({ caso, archivo, calce, papeles, fase, n, orden, motivo, reloj, alConfirmar, alProbar, alOtroArchivo }: Props) {
  // la fase en que se cumplió el tope sin respuesta: si la fase cambió, ya no está dormido
  const [dormidoEn, setDormidoEn] = useState<Fase | null>(null)
  useEffect(() => {
    if (fase !== 'entra' && fase !== 'cae') return
    const t = setTimeout(() => setDormidoEn(fase), DORMIDO_MS)
    return () => clearTimeout(t)
  }, [fase])
  const dormido = dormidoEn === fase

  const panel = (() => {
    if (fase === 'rechazo')
      return (
        <div className="entra">
          <p className="text-lg text-actuar">Krylov no respondió</p>
          <p className="titular mt-2 text-5xl">{motivo}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button onClick={alOtroArchivo} className="bg-cobre px-6 py-3 text-lg font-semibold text-fondo hover:opacity-90">
              Subir otro archivo
            </button>
            {archivo?.prueba !== caso.nombre && (
              <button onClick={alProbar} className="border border-linea px-5 py-3 text-lg hover:border-cobre">
                Probar con el de ejemplo
              </button>
            )}
          </div>
        </div>
      )
    if (archivo && (fase === 'cae' || fase === 'ordena'))
      return <Calce key={calce ? 'con' : 'sin'} columnas={archivo.columnas} calce={calce} papeles={papeles} alConfirmar={alConfirmar} />
    return (
      <div className="entra">
        <p className="text-lg text-tinta-suave">{fase === 'sale' ? 'Respondió' : 'Krylov está respondiendo'}</p>
        <Cronometro reloj={reloj} corre={fase === 'entra'} className="mt-1 block text-8xl" />
        <p className="mt-4 max-w-md text-lg text-tinta-suave">
          {archivo ? 'La red responde en milisegundos. El resto es el viaje de tu archivo hasta el servidor y de vuelta.' : 'Datos del demo, guardados: la respuesta de la red ya está calculada.'}
        </p>
        {dormido && fase === 'entra' && <p className="entra mt-4 max-w-md text-oro">El servidor gratuito se duerme cuando nadie lo usa. Está despertando: la primera vez tarda hasta 25 segundos.</p>}
      </div>
    )
  })()

  return (
    <main className="grid flex-1 items-center gap-6 px-4 py-8 sm:px-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)]">
      <div className="relative">
        {archivo && (
          <p className="text-tinta-suave">
            <span className="font-mono text-tinta">{archivo.nombre}</span> · {archivo.filas.toLocaleString('es-CL')} filas · {archivo.columnas.length} columnas
          </p>
        )}
        {!archivo && <p className="text-tinta-suave">{caso.origen_datos}</p>}
        <div className="aspect-[16/9] w-full">
          <Coreografia n={n} orden={orden} fase={fase} />
        </div>
      </div>
      <div className="max-w-xl">
        {fase === 'cae' && !archivo ? null : panel}
        {dormido && fase === 'cae' && <p className="entra mt-4 text-oro">El servidor gratuito está despertando: la primera vez tarda hasta 25 segundos.</p>}
      </div>
    </main>
  )
}
