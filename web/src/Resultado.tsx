// La respuesta: la escena de la lámina de esa decisión, con los datos del archivo (D-42). El punto recorre la escena y
// la tarjeta dice, en cada lugar, la decisión, la estimación, su rango de 90% y la distribución contra el límite.
// Debajo, una barra con el cronómetro (cuánto tardó la red y cuánto el viaje), quién respondió y qué es simulado.
// Más abajo, lo que no cabe en la escena: la interpretación, qué pesa, el examen y los supuestos de costo, plegados.

import { useEffect, useMemo, useRef, useState } from 'react'
import type { Archivo } from './App'
import { api } from './api'
import Deslizadores from './Deslizadores'
import { capaDe, configDeEscena, datosDeEscena, hayEscena, LAMINA_DE } from './escena/datos'
import LaminaDeck, { type MandoLamina } from './escena/LaminaDeck'
import Examen from './Examen'
import Interpretacion from './Interpretacion'
import QuePesa from './QuePesa'
import { msDeKrylov, segundos, type Reloj } from './reloj'
import Respaldo from './Respaldo'
import { conEscena } from './soporte'
import { quienRespondio } from './textos'
import type { Analisis, Candidata, Caso, DondeMedir, Textos } from './tipos'
import { useDecision } from './useDecision'

export interface Resuelta {
  analisis: Analisis
  donde: DondeMedir | null
  archivo: Archivo | null
  origen: 'api' | 'guardada'
  reloj: Reloj
  clave: string | null // la de la copia estática, para la interpretación guardada
}

interface Props {
  caso: Caso
  r: Resuelta
  alOtroArchivo: () => void
}

const ALTO_BARRA = 88 // px: la escena y su barra caben enteras en la pantalla, sin bajar

export default function Resultado({ caso, r, alOtroArchivo }: Props) {
  const { analisis, donde, archivo, origen, reloj } = r
  const d = useDecision(analisis)
  const mando = useRef<MandoLamina>(null)
  const [textos, setTextos] = useState<Textos['curva'] | null>(null)
  const [paso, setPaso] = useState(0)
  const [perforado, setPerforado] = useState<{ c: Candidata; valor: number; duda: number } | null>(null)
  const escena = conEscena() && hayEscena(analisis)
  const perforo = escena && !archivo && donde && analisis.rotulos.donde_medir

  // la escena se vuelve a armar con otros costos solo cuando se dejan de mover
  const [costosEscena, setCostosEscena] = useState(d.costos)
  useEffect(() => {
    const t = setTimeout(() => setCostosEscena(d.costos), 450)
    return () => clearTimeout(t)
  }, [d.costos])
  const datos = useMemo(
    () => datosDeEscena(analisis, donde, { corte: d.corte, bloques: d.bloques, unidades: d.unidades }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [analisis, donde, costosEscena],
  )

  useEffect(() => {
    api.textos().then((t) => setTextos(t.datos.curva), () => {})
  }, [])

  const verPerforo = (si: boolean) => {
    setPaso(si ? 1 : 0)
    mando.current?.paso(si ? 1 : 0)
  }
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === 'd' && perforo) verPerforo(paso === 0)
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  })

  // Una muestra más en A, B o C: el resultado del medio de lo esperado ahí. El mapa se rehace con ella, en la escena.
  const perforar = async (c: Candidata) => {
    const valor = c.resultados_posibles?.medio
    if (valor === undefined) return
    const nueva = await api.analizar(caso.nombre, [], [{ x: c.x, y: c.y, valor, etiqueta: c.etiqueta }]).then((x) => x.datos, () => null)
    const capa = nueva && capaDe(nueva)
    if (!nueva || !capa) return
    mando.current?.perforar(c.etiqueta, { ...capa }, valor)
    setPerforado({ c, valor, duda: nueva.resumen_colores?.en_duda ?? 0 })
    setPaso(0)
  }

  const red = analisis.tiempo_ms
  const total = msDeKrylov(reloj)
  const leer = reloj.calce !== undefined && reloj.soltado !== undefined ? reloj.calce - reloj.soltado : 0
  const viaje = Math.max(0, total - leer - red)
  const unidad = analisis.unidad.plural

  return (
    <main className="flex-1">
      <section className="mx-auto px-4 sm:px-0" style={escena ? { width: `min(100%, calc((100dvh - 3.5rem - ${ALTO_BARRA}px) * 16 / 9))` } : { maxWidth: '72rem' }}>
        {escena ? (
          <LaminaDeck key={JSON.stringify(costosEscena)} ref={mando} lamina={LAMINA_DE[analisis.caso]} datos={datos} config={configDeEscena(donde)} titulo={caso.titulo} />
        ) : (
          <div className="py-6">
            <h1 className="titular mb-6 text-5xl">{caso.titulo}</h1>
            <Respaldo analisis={analisis} d={d} textos={textos} propio={!!archivo} />
          </div>
        )}

        <div className="flex flex-wrap items-center gap-x-8 gap-y-3 border-t border-linea py-3" style={{ minHeight: ALTO_BARRA }}>
          <p className="flex items-baseline gap-3">
            <span className="text-tinta-suave">{origen === 'guardada' ? 'Respuesta guardada' : 'Krylov respondió en'}</span>
            <span className="titular text-5xl leading-none">{origen === 'guardada' ? `${segundos(red, 2)} s` : `${segundos(total)} s`}</span>
          </p>
          <p className={`max-w-sm text-sm text-tinta-suave ${paso === 1 ? 'hidden' : ''}`}>
            {origen === 'guardada'
              ? `Es lo que tardó la red cuando se calculó esta respuesta${archivo ? '' : ' del demo'}.`
              : `La red, ${segundos(red, 2)} s.${leer ? ` Leer tus columnas, ${segundos(leer)} s.` : ''} El viaje hasta el servidor y de vuelta, ${segundos(viaje)} s.`}
          </p>
          <div className={`min-w-0 flex-1 text-sm ${paso === 1 ? 'max-w-xs' : 'max-w-md'}`}>
            <p className="text-oxido">{quienRespondio(analisis)}</p>
            {paso === 0 && <p className="text-tinta-suave">{archivo ? `Tu archivo: ${archivo.nombre}` : analisis.origen_datos}</p>}
          </div>
          <div className="ml-auto flex flex-wrap gap-2">
            {perforo && (
              <button onClick={() => verPerforo(paso === 0)} className="border border-oro px-4 py-2.5 text-oro hover:bg-oro/10">
                {paso === 0 ? analisis.rotulos.donde_medir : 'Volver al terreno'}
              </button>
            )}
            {perforo && paso === 1 && (
              <span className="flex items-center gap-2" role="group" aria-label="Perforar en un lugar">
                <span className="text-tinta-suave">Perforar en</span>
                {donde!.candidatas.map((c) => (
                  <button key={c.etiqueta} onClick={() => perforar(c)} aria-label={`Perforar en ${c.etiqueta}`} className="titular h-11 w-11 bg-oro text-2xl text-fondo hover:opacity-90">
                    {c.etiqueta}
                  </button>
                ))}
              </span>
            )}
            {paso === 0 && (
              <button onClick={alOtroArchivo} className="bg-cobre px-5 py-2.5 font-semibold text-fondo hover:opacity-90">
                Subir otro archivo
              </button>
            )}
          </div>
        </div>
        {perforado && (
          <p className="entra border-l-4 border-oro py-1 pl-4 text-lg">
            Perforaste en {perforado.c.etiqueta}: la muestra dio {perforado.valor.toLocaleString('es-CL')} {analisis.mapa?.unidad_valor}, lo más probable ahí. El terreno se rehízo con ella y ahora quedan {perforado.duda} {unidad} en duda (antes, {analisis.resumen_colores?.en_duda}).
          </p>
        )}
      </section>

      <section className="mx-auto grid max-w-6xl gap-x-10 gap-y-8 px-4 py-12 sm:px-8 lg:grid-cols-2">
        <div className="lg:col-span-2">
          <Interpretacion analisis={analisis} clave={r.clave} d={d} />
        </div>
        {analisis.factores && (
          <div>
            <QuePesa factores={analisis.factores} titulo="Qué pesa" flechas={!analisis.mapa} />
          </div>
        )}
        {analisis.examen && (
          <div>
            <Examen examen={analisis.examen} />
          </div>
        )}
        <details className="border-t border-linea pt-4 lg:col-span-2">
          <summary className="cursor-pointer text-lg">Supuestos de costo</summary>
          <p className="mt-3 max-w-3xl text-tinta-suave">
            Para decidir, Krylov compara dos costos. Son supuestos del demo, no precios de una minera: muévelos y la decisión de cada {analisis.unidad.singular} cambia con ellos.
          </p>
          <div className="mt-4 max-w-3xl">
            <Deslizadores falsoSi={analisis.costos.falso_si} falsoNo={analisis.costos.falso_no} costos={d.costos} moneda={analisis.costo_de_no_saber?.moneda ?? 'USD'} alCambiar={d.setCostos} />
          </div>
          {d.total !== null && (
            <p className="mt-4 text-tinta-suave">
              Con estos supuestos, despejar la duda valdría unos US$ {Math.round(d.total).toLocaleString('es-CL')}. Es una cuenta sobre costos inventados: por eso no está arriba.
            </p>
          )}
        </details>
      </section>
    </main>
  )
}
