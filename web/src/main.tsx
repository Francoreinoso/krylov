import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/archivo/wdth.css'
import '@fontsource-variable/fraunces'
import '@fontsource-variable/space-grotesk'
import '@fontsource-variable/jetbrains-mono'
import '@fontsource-variable/bricolage-grotesque'
import '@fontsource-variable/instrument-sans'
import '@fontsource-variable/newsreader'
import './index.css'
import App from './App.tsx'
import { aplicarDiseno, disenoInicial } from './disenos'

aplicarDiseno(disenoInicial())

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
