// Lectura mínima de un CSV en el navegador: nombre, filas y columnas. No se analiza todavía.

export interface InfoCsv {
  nombre: string
  filas: number
  columnas: string[]
}

export async function leerCsv(archivo: File): Promise<InfoCsv> {
  const lineas = (await archivo.text()).split(/\r?\n/).filter((l) => l.trim())
  const cabecera = lineas[0] ?? ''
  const cuenta = (c: string) => cabecera.split(c).length - 1
  const separador = cuenta(';') > cuenta(',') ? ';' : ','
  const columnas = cabecera
    .split(separador)
    .map((c) => c.trim().replace(/^"(.*)"$/, '$1'))
    .filter(Boolean)
  return { nombre: archivo.name, filas: Math.max(0, lineas.length - 1), columnas }
}
