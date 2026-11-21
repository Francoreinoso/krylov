import { useEffect, useState } from 'react'
import { api, despertarApi, type Origen } from './api'
import Inicio from './Inicio'
import Respuesta from './Respuesta'
import type { Analisis, Caso } from './tipos'

export default function App() {
  const [casos, setCasos] = useState<Caso[]>([])
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
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  const elegir = (caso: Caso) => {
    api
      .analizar(caso.nombre)
      .then((r) => {
        setAnalisis(r.datos)
        setOrigen(r.origen)
      })
      .catch((e: Error) => setError(e.message))
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 py-8 sm:px-8">
      <header className="mb-10 flex items-center justify-between">
        <button onClick={() => setAnalisis(null)} className="text-lg font-semibold tracking-tight">
          Krylov
        </button>
      </header>

      <main className="flex-1">
        {error && <p className="text-red-700">{error}</p>}
        {analisis ? <Respuesta analisis={analisis} /> : <Inicio casos={casos} alElegir={elegir} />}
      </main>

      <footer className="mt-12 text-xs text-stone-400">
        {origen === 'api' ? 'Respuesta de la API' : 'Modo estático'} · ejemplo fijo, números inventados
      </footer>
    </div>
  )
}
