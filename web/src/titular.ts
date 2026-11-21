// El titular y la plata en palabras, armados igual que en nucleo/api.py y nucleo/casos.py, para
// rehacerlos en el navegador cuando se mueven los deslizadores.

const MONEDAS: Record<string, string> = { USD: 'dólares', CLP: 'pesos' }

// «18 mil dólares», «2,7 millones de dólares».
export function enPlata(valor: number, moneda: string): string {
  const nombre = MONEDAS[moneda] ?? moneda
  if (valor >= 1e6) return `${(valor / 1e6).toFixed(1).replace('.', ',')} millones de ${nombre}`
  if (valor >= 1e3) return `${Math.round(valor / 1e3)} mil ${nombre}`
  return `${Math.round(valor)} ${nombre}`
}

// La respuesta no trae el nombre de la unidad: se lee del titular que armó el servidor
// («49 personas están en duda…»). Así no hay texto de ningún caso escrito en el código.
export function unidadDelTitular(titular: string): string {
  return /^\d+ (.+?) (?:está|están) en duda/.exec(titular)?.[1] ?? ''
}

export function titular(enDuda: number, unidad: string, total: number, moneda: string): string {
  const verbo = enDuda === 1 ? 'está' : 'están'
  return `${enDuda} ${unidad} ${verbo} en duda. No saber te cuesta cerca de ${enPlata(total, moneda)}.`
}

// Plata en cifras para la pantalla: «US$ 7.420», con espacio, como en el deck.
export const plata = (valor: number, moneda: string) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: moneda, maximumFractionDigits: 0 })
    .format(valor)
    .replace(/^(US\$|\$)\s?/, '$1 ')
