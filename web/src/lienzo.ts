// Ayudas comunes de los dibujos en canvas: nitidez en pantallas densas y la trama de la duda.

import { useEffect, useRef } from 'react'

// Llama a `dibujar` con un contexto del tamaño en pantalla del canvas, cada vez que cambian las
// dependencias o el tamaño.
export function useLienzo(dibujar: (ctx: CanvasRenderingContext2D, ancho: number, alto: number) => void, deps: unknown[]) {
  const ref = useRef<HTMLCanvasElement>(null)
  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const pintar = () => {
      const { width, height } = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      canvas.width = Math.round(width * dpr)
      canvas.height = Math.round(height * dpr)
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, width, height)
      dibujar(ctx, width, height)
    }
    pintar()
    const observador = new ResizeObserver(pintar)
    observador.observe(canvas)
    return () => observador.disconnect()
  }, deps)
  return ref
}

// Ámbar con rayas diagonales, igual que la clase .achurado del CSS.
export function trama(ctx: CanvasRenderingContext2D, color: string, rayas: string): CanvasPattern | string {
  const celda = document.createElement('canvas')
  celda.width = celda.height = 8
  const c = celda.getContext('2d')
  if (!c) return color
  c.fillStyle = color
  c.fillRect(0, 0, 8, 8)
  c.strokeStyle = rayas
  c.lineWidth = 2
  c.beginPath()
  c.moveTo(-2, 2)
  c.lineTo(2, -2)
  c.moveTo(0, 8)
  c.lineTo(8, 0)
  c.moveTo(6, 10)
  c.lineTo(10, 6)
  c.stroke()
  return ctx.createPattern(celda, 'repeat') ?? color
}
