import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { cpSync, existsSync, readFileSync, statSync } from 'node:fs'
import { extname, join, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, type Plugin } from 'vite'

const AQUI = fileURLToPath(new URL('.', import.meta.url))
const DECK = resolve(AQUI, '../pitch/deck')

// D-42: la app y el deck son la misma cosa. La app toma del deck, tal cual y sin copias en el repositorio, sus láminas
// (`laminas.html` es el `index.html` del deck: de ahí salen las secciones de cada decisión), su hoja de estilos, sus
// módulos de escena y sus bibliotecas y tipografías. En desarrollo se sirven desde pitch/deck; al compilar se copian a
// dist/deck. Los datos del deck (datos/datos.js) no se copian: cada lámina de la app recibe los de su respuesta.
const COMPARTIDO: Record<string, string> = { 'deck.css': 'deck.css', 'index.html': 'laminas.html', js: 'js', vendor: 'vendor' }
const TIPOS: Record<string, string> = {
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.woff2': 'font/woff2',
}

function deckCompartido(): Plugin {
  const enDeck = (publicada: string): string | null => {
    const [primera, ...resto] = publicada.split('/').filter(Boolean)
    const origen = Object.entries(COMPARTIDO).find(([, destino]) => destino === primera)?.[0]
    if (!origen) return null
    const ruta = resolve(DECK, origen, ...resto)
    return ruta.startsWith(DECK + sep) && existsSync(ruta) && statSync(ruta).isFile() ? ruta : null
  }
  return {
    name: 'deck-compartido',
    configureServer(server) {
      server.middlewares.use('/deck', (req, res, next) => {
        const ruta = enDeck(decodeURIComponent((req.url ?? '').split('?')[0]))
        if (!ruta) return next()
        res.setHeader('Content-Type', TIPOS[extname(ruta)] ?? 'application/octet-stream')
        res.end(readFileSync(ruta))
      })
    },
    writeBundle(opciones) {
      const salida = join(opciones.dir ?? resolve(AQUI, 'dist'), 'deck')
      for (const [origen, destino] of Object.entries(COMPARTIDO)) cpSync(join(DECK, origen), join(salida, destino), { recursive: true })
    },
  }
}

export default defineConfig({
  plugins: [react(), tailwindcss(), deckCompartido()],
  build: {
    rollupOptions: { input: { inicio: resolve(AQUI, 'index.html'), escena: resolve(AQUI, 'escena.html') } },
  },
})
