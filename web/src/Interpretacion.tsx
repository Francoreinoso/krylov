// La interpretación debajo de los números (D-34): un texto corto que escribe el modelo de lenguaje
// leyendo el JSON del motor. Llega después de los números y no los bloquea. Al soltar un
// deslizador se pide de nuevo con los costos nuevos; sin servidor, el texto queda atenuado y dice
// que se escribió con los costos iniciales.

import { useEffect, useState } from 'react'
import { api, hayApi } from './api'
import type { Analisis, Interpretacion as Texto } from './tipos'
import type { Recalculo } from './useDecision'

const ESPERA_MS = 800 // tiempo quieto de los deslizadores antes de pedir un texto nuevo

// El análisis con lo que rehízo el navegador al mover los costos, para que el texto y la revisión
// de números del servidor lean lo mismo que está en pantalla.
function conCostosNuevos(a: Analisis, d: Recalculo): Analisis {
  return {
    ...a,
    titular: d.titular,
    costos: {
      falso_si: { ...a.costos.falso_si, valor: d.costos.falsoSi },
      falso_no: { ...a.costos.falso_no, valor: d.costos.falsoNo },
    },
    punto_de_corte: d.corte,
    resumen_colores: d.resumen,
    costo_de_no_saber: a.costo_de_no_saber && d.total !== null ? { ...a.costo_de_no_saber, valor: Math.round(d.total) } : null,
    unidades: a.unidades && d.unidades ? a.unidades.map((u, i) => ({ ...u, ...d.unidades![i] })) : a.unidades,
    en_palabras: [], // las frases de plantilla traen los conteos de los costos iniciales
  }
}

function rotulo(t: Texto): string {
  const quien =
    t.origen === 'plantilla' ? 'Texto de plantilla' : t.proveedor === 'claude' ? 'Escrito por Claude a partir de estos números' : 'Escrito por un modelo de prueba'
  return t.precalculado ? `${quien} · precalculado` : quien
}

export default function Interpretacion({ analisis, clave, d }: { analisis: Analisis; clave: string | null; d: Recalculo }) {
  const [inicial, setInicial] = useState<Texto | null>(null)
  const [nuevo, setNuevo] = useState<{ costos: string; texto: Texto } | null>(null) // el último texto pedido con otros costos
  const { falsoSi, falsoNo } = d.costos
  const costos = `${falsoSi}|${falsoNo}`
  const iniciales = falsoSi === analisis.costos.falso_si.valor && falsoNo === analisis.costos.falso_no.valor

  useEffect(() => {
    api.interpretar(analisis, clave).then(setInicial).catch(() => {})
  }, [analisis, clave])

  useEffect(() => {
    if (iniciales || !hayApi) return
    const control = new AbortController()
    const espera = setTimeout(() => {
      api
        .interpretar(conCostosNuevos(analisis, d), null, control.signal)
        .then((texto) => setNuevo({ costos, texto }))
        .catch(() => {})
    }, ESPERA_MS)
    return () => {
      clearTimeout(espera)
      control.abort()
    }
    // `d` cambia con cada costo; basta con mirar los costos.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [costos])

  const texto = iniciales ? inicial : (nuevo?.texto ?? inicial)
  const viejo = !iniciales && nuevo?.costos !== costos // escrito con otros costos que los de la pantalla
  if (!texto) return <p className="animate-pulse text-sm text-tinta-suave">Krylov está escribiendo…</p>
  if (texto.origen === 'plantilla' && texto.texto === d.titular) return null // no repite el titular
  return (
    <div className={`border-l-2 border-linea pl-4 transition-opacity ${viejo ? 'opacity-50' : ''}`}>
      <p className="leading-relaxed">{texto.texto}</p>
      <p className="mt-1 text-xs text-tinta-suave">{viejo ? `${rotulo(texto)} · escrito con ${nuevo ? 'otros costos' : 'los costos iniciales'}` : rotulo(texto)}</p>
    </div>
  )
}
