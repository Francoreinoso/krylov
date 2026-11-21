// El número grande: cuando cambia, cuenta hasta su valor nuevo en 300 ms.

import { useEffect, useRef, useState } from 'react'
import { plata } from './titular'

const DURACION_MS = 300

// `tope`: el tamaño máximo en rem. La cifra va en cobre, como en la lámina 4.
export default function NumeroGrande({ valor, moneda, tope = 4.25 }: { valor: number; moneda: string; tope?: number }) {
  const [mostrado, setMostrado] = useState(valor)
  const desde = useRef(valor)

  useEffect(() => {
    const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const inicio = desde.current
    if (quieto || inicio === valor) {
      desde.current = valor
      setMostrado(valor)
      return
    }
    const t0 = performance.now()
    let cuadro = 0
    const paso = (t: number) => {
      const avance = Math.min(1, (t - t0) / DURACION_MS)
      const actual = inicio + (valor - inicio) * (1 - (1 - avance) ** 3)
      desde.current = actual
      setMostrado(actual)
      if (avance < 1) cuadro = requestAnimationFrame(paso)
    }
    cuadro = requestAnimationFrame(paso)
    return () => cancelAnimationFrame(cuadro)
  }, [valor])

  // «US$ 1.577.707», con espacio después del símbolo, como en el deck.
  const texto = plata(mostrado, moneda)
  // La cifra se achica para caber en su columna. Big Shoulders es angosta: medio em por carácter.
  return (
    <div className="@container">
      <p className="titular leading-[0.9] text-cobre" style={{ fontSize: `min(${tope}rem, ${(100 / (texto.length * 0.5)).toFixed(1)}cqi)` }}>
        {texto}
      </p>
    </div>
  )
}
