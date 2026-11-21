import { useEffect, useState } from 'react'
import { api, despertarApi, type Origen } from './api'
import Inicio from './Inicio'
import Respuesta from './Respuesta'
import { lineaDelCaso } from './textos'
import type { Analisis, Caso } from './tipos'

export default function App() {
  const [casos, setCasos] = useState<Caso[]>([])
  const [caso, setCaso] = useState<Caso | null>(null)
  const [analisis, setAnalisis] = useState<Analisis | null>(null)
  const [origen, setOrigen] = useState<Origen | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    despertarApi()
    api
      .casos()
      .then((r) => {
        setCasos(r.datos.casos)
        setOrigen(r.origen)
        const pedido = new URLSearchParams(window.location.search).get('caso')
        const inicial = r.datos.casos.find((c) => c.nombre === pedido)
        if (inicial) elegir(inicial)
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  const elegir = (elegido: Caso) => {
    setError('')
    api
      .analizar(elegido.nombre)
      .then((r) => {
        setCaso(elegido)
        setAnalisis(r.datos)
        setOrigen(r.origen)
      })
      .catch((e: Error) => setError(e.message))
  }

  const volver = () => {
    setCaso(null)
    setAnalisis(null)
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6 sm:px-10 sm:py-8">
      <header className="mb-10 flex flex-wrap items-baseline justify-between gap-2">
        <button onClick={volver} className="condensado text-2xl font-bold">
          Krylov
        </button>
        {caso && (
          <p className="text-tinta-suave">{lineaDelCaso(caso)}</p>
        )}
      </header>

      <main className="flex-1">
        {error && <p className="mb-6 text-red-800">{error}</p>}
        {analisis ? <Respuesta analisis={analisis} /> : <Inicio casos={casos} alElegir={elegir} />}
      </main>

      <p className="mt-10 text-xs text-tinta-suave">
        {origen === 'api' ? 'Respuesta de la API' : 'Modo estático'}. Ejemplo fijo: números inventados.
      </p>
    </div>
  )
}
