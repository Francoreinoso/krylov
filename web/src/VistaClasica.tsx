import { useEffect, useState } from 'react'
import { api, despertarApi, type Origen } from './api'
import Inicio from './Inicio'
import Respuesta from './Respuesta'
import { lineaDelCaso } from './textos'
import type { Analisis, Caso, Nube } from './tipos'

export default function VistaClasica() {
  const [casos, setCasos] = useState<Caso[]>([])
  const [caso, setCaso] = useState<Caso | null>(null)
  const [analisis, setAnalisis] = useState<Analisis | null>(null)
  const [nube, setNube] = useState<Nube | null>(null)
  const [origen, setOrigen] = useState<Origen | null>(null)
  const [error, setError] = useState('')

  // Pide la respuesta de un caso y, si el archivo no se parece a nada conocido, también la nube.
  const abrir = async (nombre: string, tarjeta: Caso | null) => {
    setError('')
    try {
      const r = await api.analizar(nombre)
      const n = r.datos.semaforo.estado === 'rojo_modelo' ? (await api.nube(nombre)).datos : null
      setCaso(tarjeta)
      setAnalisis(r.datos)
      setNube(n)
      setOrigen(r.origen)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  useEffect(() => {
    despertarApi()
    api
      .casos()
      .then((r) => {
        setCasos(r.datos.casos)
        setOrigen(r.origen)
        // ?caso=<nombre> abre esa respuesta directo (también los casos ocultos, como el archivo malo).
        const pedido = new URLSearchParams(window.location.search).get('caso')
        if (pedido) abrir(pedido, r.datos.casos.find((c) => c.nombre === pedido) ?? null)
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  const volver = () => {
    setCaso(null)
    setAnalisis(null)
    setNube(null)
  }

  return (
    <div className={`mx-auto flex min-h-dvh max-w-[90rem] flex-col px-4 py-5 sm:px-8 ${analisis ? 'md:h-dvh md:min-h-0' : ''}`}>
      <header className="mb-5 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
        <button onClick={volver} className="condensado text-2xl font-bold">
          Krylov
        </button>
        {caso && <p className="text-tinta-suave">{lineaDelCaso(caso)}</p>}
      </header>

      <main className="flex min-h-0 flex-1 flex-col">
        {error && <p className="mb-4 text-actuar">{error}</p>}
        {analisis ? (
          <Respuesta key={analisis.caso} analisis={analisis} nube={nube} />
        ) : (
          <Inicio casos={casos} alElegir={(c) => abrir(c.nombre, c)} />
        )}
      </main>

      <p className="mt-3 text-xs text-tinta-suave/70">
        {origen === 'api' ? 'Respuesta de la API' : 'Modo estático'}.
      </p>
    </div>
  )
}
