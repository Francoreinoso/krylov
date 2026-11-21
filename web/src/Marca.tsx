// La marca de Krylov: tres curvas de nivel de cobre, el cerro de la carta topográfica del deck.
// Va en el encabezado y junto a cada respuesta.

export default function Marca({ grande = false, pensando = false }: { grande?: boolean; pensando?: boolean }) {
  return (
    <svg viewBox="0 0 28 28" className={`shrink-0 ${grande ? 'h-12 w-12' : 'h-7 w-7'} ${pensando ? 'animate-pulse' : ''}`} fill="none" stroke="var(--color-cobre)" aria-hidden>
      <path d="M14 3.5c6 0 11 3.2 11 8.8 0 6.6-5.6 12.2-11.6 12.2C7.8 24.5 3 20 3 14.2 3 8.2 8 3.5 14 3.5Z" strokeWidth="1.4" opacity="0.55" />
      <path d="M14.6 8c3.4 0 6.4 2 6.4 5.4 0 4-3.3 7-7 7-3.4 0-6-2.6-6-5.7C8 11 10.9 8 14.6 8Z" strokeWidth="1.6" opacity="0.8" />
      <path d="M15 12c1.6 0 2.8 1 2.8 2.4 0 1.7-1.5 2.8-3 2.8-1.4 0-2.4-1-2.4-2.3 0-1.6 1.1-2.9 2.6-2.9Z" fill="var(--color-cobre)" stroke="none" />
    </svg>
  )
}

// El nombre, como el pie de cada lámina.
export function Logotipo({ className = '' }: { className?: string }) {
  return <span className={`titular tracking-[0.18em] ${className}`}>KRYLOV</span>
}
