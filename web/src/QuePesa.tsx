// Qué pesa: cada factor con su flecha y qué tan seguro es. El número no se muestra.

import type { Certeza, Factor } from './tipos'

const CERTEZA: Record<Certeza, string> = {
  seguro: 'Seguro',
  probable: 'Probable',
  no_se_sabe: 'No se puede saber con estos datos',
}

export default function QuePesa({ factores }: { factores: Factor[] }) {
  return (
    <div>
      <h2 className="text-xl font-semibold">Qué pesa</h2>
      <ul className="mt-4 border-t border-linea">
        {factores.map((f) => (
          <li
            key={f.nombre}
            className={`flex gap-3 border-b border-linea py-3 ${f.certeza === 'no_se_sabe' ? 'text-tinta-suave' : ''}`}
          >
            <span aria-label={f.direccion === 'sube' ? 'Sube el riesgo' : 'Baja el riesgo'} className="w-5 text-xl leading-6">
              {f.direccion === 'sube' ? '↑' : '↓'}
            </span>
            <span>
              <span className="block font-medium">{f.etiqueta}</span>
              <span className="block text-sm text-tinta-suave">{CERTEZA[f.certeza]}</span>
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-sm text-tinta-suave">↑ sube el riesgo · ↓ lo baja</p>
    </div>
  )
}
