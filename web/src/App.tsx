// Dos rutas, sin librería: /clasico es el inicio de tarjetas de antes; todo lo demás, el chat.

import Chat from './Chat'
import VistaClasica from './VistaClasica'

const clasica = window.location.pathname.startsWith('/clasico')

export default function App() {
  return clasica ? <VistaClasica /> : <Chat />
}
