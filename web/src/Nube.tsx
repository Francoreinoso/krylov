// La nube: las empresas simuladas con que Krylov practicó, en dos ejes con nombre, y el archivo
// del usuario encima. Si cae afuera, Krylov no responde.

import { COLOR, token } from './colores'
import { useLienzo } from './lienzo'
import type { Nube as DatosNube } from './tipos'

const MARGEN = { izq: 64, der: 16, arr: 16, aba: 52 }

export default function Nube({ nube }: { nube: DatosNube }) {
  const { ejes, puntos, archivo } = nube
  const ref = useLienzo(
    (ctx, ancho, alto) => {
      const w = ancho - MARGEN.izq - MARGEN.der
      const h = alto - MARGEN.arr - MARGEN.aba
      const px = (v: number) => MARGEN.izq + ((v - ejes.x.min) / (ejes.x.max - ejes.x.min)) * w
      const py = (v: number) => MARGEN.arr + h - ((v - ejes.y.min) / (ejes.y.max - ejes.y.min)) * h

      // Ejes
      ctx.strokeStyle = token('--color-linea')
      ctx.lineWidth = 1
      ctx.strokeRect(MARGEN.izq, MARGEN.arr, w, h)
      // Los nombres de los ejes, grandes y en tinta: se leen desde el fondo de la sala.
      const fuente = token('--font-sans')
      ctx.fillStyle = token('--color-tinta-suave')
      ctx.font = `15px ${fuente}`
      ctx.textAlign = 'center'
      ctx.fillText(String(ejes.x.min), MARGEN.izq, MARGEN.arr + h + 18)
      ctx.fillText(String(ejes.x.max), MARGEN.izq + w, MARGEN.arr + h + 18)
      ctx.textAlign = 'right'
      ctx.fillText(String(ejes.y.max), MARGEN.izq - 8, MARGEN.arr + 12)
      ctx.fillText(String(ejes.y.min), MARGEN.izq - 8, MARGEN.arr + h)
      ctx.fillStyle = token('--color-tinta')
      ctx.font = `600 17px ${fuente}`
      ctx.textAlign = 'center'
      ctx.fillText(ejes.x.nombre, MARGEN.izq + w / 2, alto - 8)
      ctx.save()
      ctx.translate(20, MARGEN.arr + h / 2)
      ctx.rotate(-Math.PI / 2)
      ctx.fillText(ejes.y.nombre, 0, 0)
      ctx.restore()

      // Simulaciones
      ctx.fillStyle = token('--color-tinta-suave') + '59'
      for (const [x, y] of puntos) {
        ctx.fillRect(px(x) - 1.25, py(y) - 1.25, 2.5, 2.5)
      }

      // El archivo
      const color = archivo.dentro ? COLOR.no_actuar : COLOR.actuar
      const ax = px(archivo.x)
      const ay = py(archivo.y)
      ctx.beginPath()
      ctx.arc(ax, ay, 18, 0, Math.PI * 2)
      ctx.fillStyle = color + '33'
      ctx.fill()
      ctx.beginPath()
      ctx.arc(ax, ay, 8, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.fill()
      ctx.lineWidth = 2
      ctx.strokeStyle = token('--color-tinta')
      ctx.stroke()
    },
    [nube],
  )

  return (
    <figure className="flex min-h-0 flex-col">
      <h2 className="text-xl font-semibold">
        {archivo.dentro ? 'Se parece a lo que practicó' : 'No se parece a nada que haya visto'}
      </h2>
      <p className="text-sm text-tinta-suave">
        Cada punto gris es una empresa simulada con que Krylov practicó. El punto grande es tu archivo.
      </p>
      <canvas ref={ref} className="mt-3 min-h-64 w-full flex-1" role="img" aria-label="Nube de simulaciones con el archivo encima" />
    </figure>
  )
}
