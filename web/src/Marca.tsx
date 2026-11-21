// La marca de Krylov: dos olas en el degradado del diseño. Va en la barra lateral, el inicio y
// junto a cada respuesta.

export default function Marca({ grande = false }: { grande?: boolean }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center text-sobre-acento ${grande ? 'h-12 w-12 rounded-2xl' : 'h-7 w-7 rounded-lg'}`}
      style={{ background: 'var(--degradado)' }}
      aria-hidden
    >
      <svg viewBox="0 0 24 24" className={grande ? 'h-7 w-7' : 'h-4 w-4'} fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
        <path d="M3 9.5c3-3 6 3 9 0s6 3 9 0" />
        <path d="M3 15.5c3-3 6 3 9 0s6 3 9 0" />
      </svg>
    </span>
  )
}
