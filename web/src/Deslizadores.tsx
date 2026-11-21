// Los dos costos del caso como deslizadores. Son supuestos del demo y se dicen como supuestos.

import { plata } from './titular'
import type { Costos } from './useDecision'
import type { Costo } from './tipos'

interface Props {
  falsoSi: Costo
  falsoNo: Costo
  costos: Costos
  moneda: string
  alCambiar: (c: Costos) => void
}


function Deslizador({ costo, valor, moneda, alCambiar }: { costo: Costo; valor: number; moneda: string; alCambiar: (v: number) => void }) {
  const paso = Math.max(1, Math.round((costo.max - costo.min) / 200))
  return (
    <label className="block">
      <span className="block text-sm leading-snug text-tinta-suave">{costo.etiqueta}</span>
      <span className="flex items-center gap-3">
        <input
        type="range"
        className="deslizador"
        min={costo.min}
        max={costo.max}
        step={paso}
        value={valor}
        onChange={(e) => {
          // Imán al valor del caso: no cae en la cuadrícula del paso y si no, no se podría volver a él.
          const v = Number(e.target.value)
          alCambiar(Math.abs(v - costo.valor) <= paso / 2 ? costo.valor : v)
        }}
        />
        <span className="w-28 shrink-0 text-right font-mono text-sm whitespace-nowrap">{plata(valor, moneda)}</span>
      </span>
    </label>
  )
}

export default function Deslizadores({ falsoSi, falsoNo, costos, moneda, alCambiar }: Props) {
  return (
    <div className="space-y-3">
      <p className="dato">Supuestos del demo · muévelos y la respuesta cambia</p>
      <Deslizador costo={falsoSi} valor={costos.falsoSi} moneda={moneda} alCambiar={(v) => alCambiar({ ...costos, falsoSi: v })} />
      <Deslizador costo={falsoNo} valor={costos.falsoNo} moneda={moneda} alCambiar={(v) => alCambiar({ ...costos, falsoNo: v })} />
    </div>
  )
}
