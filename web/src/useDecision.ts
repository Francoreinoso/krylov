// Los costos que elige el usuario y todo lo que cambia con ellos: colores, lo que cuesta no saber
// y el titular. Se recalcula en el navegador, sin llamar a la API.

import { useMemo, useState } from 'react'
import { decidirEspacial, decidirTabla, puntoDeCorte, resumenColores, type Decision } from './decision'
import { titular, unidadDelTitular } from './titular'
import type { Analisis, Estado } from './tipos'

export interface Costos {
  falsoSi: number
  falsoNo: number
}

export interface Recalculo {
  costos: Costos
  setCostos: (c: Costos) => void
  corte: number
  unidades: Decision[] | null // en el orden de analisis.unidades
  bloques: (Decision | null)[] | null // en el orden de analisis.mapa.p
  resumen: Record<Estado, number> | null
  total: number | null
  titular: string
}

const costosDe = (a: Analisis): Costos => ({ falsoSi: a.costos.falso_si.valor, falsoNo: a.costos.falso_no.valor })

export function useDecision(analisis: Analisis): Recalculo {
  // Al cambiar de respuesta se vuelve a los costos que trae (la clave del componente cambia).
  const [costos, setCostos] = useState<Costos>(() => costosDe(analisis))

  return useMemo(() => {
    const { falsoSi, falsoNo } = costos
    const unidades = analisis.unidades?.map((u) => decidirTabla(u.muestras_p, falsoSi, falsoNo)) ?? null
    const bloques =
      analisis.mapa?.p.map((p) => (p === null ? null : decidirEspacial(p, falsoSi, falsoNo))) ?? null
    const decisiones = unidades ?? bloques?.filter((b): b is Decision => b !== null) ?? null
    const resumen = decisiones ? resumenColores(decisiones.map((d) => d.estado)) : null
    const total = decisiones ? decisiones.reduce((a, d) => a + d.duda, 0) : null
    const sinCambios = falsoSi === analisis.costos.falso_si.valor && falsoNo === analisis.costos.falso_no.valor
    const texto =
      sinCambios || !resumen || total === null || !analisis.costo_de_no_saber
        ? analisis.titular
        : titular(resumen.en_duda, unidadDelTitular(analisis.titular), total, analisis.costo_de_no_saber.moneda)

    return { costos, setCostos, corte: puntoDeCorte(falsoSi, falsoNo), unidades, bloques, resumen, total, titular: texto }
  }, [analisis, costos])
}
