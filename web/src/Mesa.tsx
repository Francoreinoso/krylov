// El lienzo de la derecha del diseño Mesa, como el panel «En vivo» del respaldo técnico del deck:
// la respuesta elegida en grande, con el tiempo que tardó como en el cronómetro de la lámina 2.
// Sin respuesta todavía, muestra las cinco decisiones o la elegida.

import { useEffect, useRef } from 'react'
import Decisiones, { type Quien } from './Decisiones'
import Ilustracion from './Ilustracion'
import Interpretacion from './Interpretacion'
import { Logotipo } from './Marca'
import { MOTOR_EN_PALABRAS } from './preguntas'
import { CuerpoRespuesta, Titular, type DatosRespuesta } from './RespuestaEnChat'
import { rotuloQuien } from './textos'
import type { Candidata, Caso } from './tipos'
import { useDecision } from './useDecision'

function Encabezado({ izquierda, derecha }: { izquierda: string; derecha?: React.ReactNode }) {
  return (
    <header className="flex items-end justify-between gap-6 border-b border-linea pb-4">
      <p className="dato text-oxido">{izquierda}</p>
      {derecha}
    </header>
  )
}

function RespuestaGrande({ datos, caso, alPerforar, ocupado }: { datos: DatosRespuesta; caso: Caso | null; alPerforar: (c: Candidata) => void; ocupado: boolean }) {
  const d = useDecision(datos.analisis)
  const { analisis } = datos
  const quien = rotuloQuien(analisis)
  const segundos = (analisis.tiempo_ms / 1000).toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return (
    <>
      <Encabezado
        izquierda={`Krylov · ${caso?.empresa_o_industria ?? 'tu archivo'}`}
        derecha={
          <span className="text-right">
            {analisis._aviso ? (
              <span className={`dato ${quien.clase}`}>{quien.texto}</span>
            ) : (
              <>
                <span className="titular block text-5xl text-cobre">{segundos}</span>
                <span className="dato block">Segundos · {quien.texto.toLowerCase()}</span>
              </>
            )}
          </span>
        }
      />
      <div className="mt-6">
        <Titular texto={d.titular} animar={false} grande precalculado={analisis.precalculado} />
      </div>
      <div className="mt-8 space-y-6">
        <CuerpoRespuesta datos={{ ...datos, completa: true }} d={d} grande alPerforar={alPerforar} ocupado={ocupado} />
        <Interpretacion analisis={analisis} clave={datos.clave} d={d} />
        {analisis.sintetico && <p className="dato">{analisis.origen_datos}</p>}
      </div>
    </>
  )
}

interface Props {
  datos: DatosRespuesta | null
  clave: number | null // cambia al elegir otra respuesta: vuelve a los costos que trae
  caso: Caso | null
  casos: Caso[]
  quien: Record<string, Quien>
  pensando: boolean
  alElegir: (c: Caso) => void
  alPerforar: (c: Candidata) => void
}

export default function Mesa({ datos, clave, caso, casos, quien, pensando, alElegir, alPerforar }: Props) {
  const lienzo = useRef<HTMLElement>(null)
  // Cada respuesta nueva empieza arriba, con su titular.
  useEffect(() => {
    lienzo.current?.scrollTo({ top: 0 })
  }, [clave])
  return (
    <section ref={lienzo} className="desliza-lista relative min-h-0 flex-1 overflow-y-auto border-t border-linea bg-superficie/40 px-5 py-6 lg:border-t-0 lg:border-l lg:px-10 lg:py-8">
      {datos ? (
        <RespuestaGrande key={clave} datos={datos} caso={caso} alPerforar={alPerforar} ocupado={pensando} />
      ) : caso ? (
        <>
          <Encabezado izquierda={`Krylov · ${caso.empresa_o_industria}`} />
          <div className="mx-auto mt-10 max-w-3xl">
            <Ilustracion motor={caso.motor} className="mx-auto aspect-[5/3] w-full max-w-xl" />
            <p className="titular mt-8 text-5xl sm:text-6xl">{caso.titulo}</p>
            <p className="mt-3 text-lg text-tinta-suave">{MOTOR_EN_PALABRAS[caso.motor]}</p>
            <p className="dato mt-6">{caso.origen_datos}</p>
            {pensando && <p className="brillo mt-6 text-lg">Calculando con el modelo…</p>}
          </div>
        </>
      ) : (
        <>
          <Encabezado izquierda="Krylov · en vivo" derecha={<Logotipo className="text-lg text-tenue" />} />
          <p className="titular mt-8 text-5xl sm:text-6xl">Una mina decide esto todos los días.</p>
          <div className="mt-10">
            <Decisiones casos={casos} quien={quien} alElegir={alElegir} forma="grilla" />
          </div>
        </>
      )}
    </section>
  )
}
