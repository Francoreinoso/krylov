// La respuesta sin la escena del deck: en un teléfono, sin WebGL o con una API que todavía no trae lo que la tarjeta
// dibuja (D-42). Lo mismo que dice la escena, quieto: la decisión de cada unidad y la duda de la que se mira.

import { CurvaDeUnidad } from './Curva'
import { useUnidadElegida } from './unidadElegida'
import ListaUnidades from './ListaUnidades'
import Mapa from './Mapa'
import { nombreDeUnidad } from './textos'
import type { Analisis, Textos } from './tipos'
import type { Recalculo } from './useDecision'

export default function Respaldo({ analisis, d, textos, propio }: { analisis: Analisis; d: Recalculo; textos: Textos['curva'] | null; propio: boolean }) {
  const unidades = analisis.unidades
  const [elegida, setElegida] = useUnidadElegida(unidades)
  if (analisis.mapa && d.bloques) {
    return (
      <div className="mx-auto aspect-square w-full max-w-[min(100%,70dvh)]">
        <Mapa mapa={analisis.mapa} bloques={d.bloques} />
      </div>
    )
  }
  if (!unidades || !d.unidades) return null
  const i = unidades.findIndex((u) => u.id === elegida)
  const conNombre = unidades.map((u) => ({ ...u, etiqueta: nombreDeUnidad(u.id, propio) }))
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <ListaUnidades unidades={conNombre} decisiones={d.unidades} corte={d.corte} elegida={elegida} alElegir={setElegida} />
      {i >= 0 && (
        <CurvaDeUnidad
          unidad={conNombre[i]}
          estado={d.unidades[i].estado}
          rotulo={analisis.rotulos[d.unidades[i].estado]}
          textos={textos}
          escalones={analisis.motor_id === 'sismico'}
        />
      )}
    </div>
  )
}
