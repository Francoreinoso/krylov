// Lectura de un CSV en el navegador. El archivo entero viaja al servidor, que es quien lo lee para el calce y el
// análisis; aquí se leen sus columnas y una muestra de sus filas, que son los puntos que se ven caer y entrar a la red.
// Aguanta lo que sale de un Excel en español: punto y coma, coma decimal, marca BOM y archivos en latin-1.

export interface InfoCsv {
  archivo: File
  nombre: string
  filas: number
  columnas: string[]
  muestra: string[][] // hasta MUESTRA filas, repartidas en todo el archivo
}

const MUESTRA = 2400
export const TOPE_MB = 8 // más que esto no es un archivo de una decisión: es otra cosa

// Un texto que no es UTF-8 trae caracteres de reemplazo; entonces se lee como latin-1 (Excel en Windows).
async function texto(archivo: File): Promise<string> {
  const bytes = await archivo.arrayBuffer()
  const utf8 = new TextDecoder('utf-8').decode(bytes)
  return (utf8.includes('�') ? new TextDecoder('latin1').decode(bytes) : utf8).replace(/^﻿/, '')
}

const separadorDe = (cabecera: string) =>
  [';', '\t', ','].map((s) => [s, cabecera.split(s).length - 1] as const).sort((a, b) => b[1] - a[1])[0][0]

const celdas = (linea: string, separador: string) => linea.split(separador).map((c) => c.trim().replace(/^"(.*)"$/, '$1'))

export async function leerCsv(archivo: File): Promise<InfoCsv> {
  if (archivo.size > TOPE_MB * 1024 * 1024)
    throw new Error(`pesa ${(archivo.size / 1024 / 1024).toFixed(0)} MB, y una decisión cabe en menos de ${TOPE_MB} MB. Sube solo las columnas y filas de esa decisión.`)
  const lineas = (await texto(archivo)).split(/\r?\n/).filter((l) => l.trim())
  if (lineas.length < 2) throw new Error('no trae filas: solo la cabecera, o nada. Revisa que sea el archivo que querías subir.')
  const separador = separadorDe(lineas[0])
  const columnas = celdas(lineas[0], separador).filter(Boolean)
  if (columnas.length < 2) throw new Error('no se ven columnas separadas por coma ni por punto y coma. Guárdalo como CSV desde tu planilla.')
  const filas = lineas.length - 1
  const paso = Math.max(1, filas / MUESTRA)
  const muestra: string[][] = []
  for (let k = 0; k < Math.min(filas, MUESTRA); k++) muestra.push(celdas(lineas[1 + Math.floor(k * paso)], separador))
  return { archivo, nombre: archivo.name, filas, columnas, muestra }
}

// Una columna de la muestra como números (acepta coma decimal). Lo que no es número queda en NaN.
export function numeros(info: InfoCsv, columna: string): number[] {
  const j = info.columnas.indexOf(columna)
  return info.muestra.map((f) => (j < 0 ? NaN : Number((f[j] ?? '').replace(/\s/g, '').replace(',', '.'))))
}

export function textos(info: InfoCsv, columna: string): string[] {
  const j = info.columnas.indexOf(columna)
  return info.muestra.map((f) => (j < 0 ? '' : (f[j] ?? '')))
}
