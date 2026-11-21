// Qué pesa: cada factor con su flecha y qué tan seguro es. El número no se muestra.
// En el terreno es «qué manda»: lo que mueve el mapa, sin flechas.

import type { Certeza, Factor } from './tipos'

const CERTEZA: Record<Certeza, string> = {
  seguro: 'Seguro',
  probable: 'Probable',
  no_se_sabe: 'No se puede saber con estos datos',
}

interface Props {
  factores: Factor[]
  titulo: string
  flechas: boolean
}

export default function QuePesa({ factores, titulo, flechas }: Props) {
  return (
    <div>
      <h2 className="titular text-3xl">{titulo}</h2>
      <ul className="mt-2">
        {factores.map((f) => (
          <li
            key={f.nombre}
            className={`flex gap-3 border-b border-linea py-2 ${f.certeza === 'no_se_sabe' ? 'text-tinta-suave' : ''}`}
          >
            {flechas && (
              <span aria-label={f.direccion === 'sube' ? 'Sube el riesgo' : 'Baja el riesgo'} className="w-4 text-lg leading-6">
                {f.direccion === 'sube' ? '↑' : '↓'}
              </span>
            )}
            <span>
              <span className="block leading-6">{f.etiqueta}</span>
              <span className="block text-sm text-tinta-suave">{CERTEZA[f.certeza]}</span>
            </span>
          </li>
        ))}
      </ul>
      {flechas && <p className="mt-2 text-xs text-tinta-suave">↑ sube el riesgo, ↓ lo baja</p>}
    </div>
  )
}
