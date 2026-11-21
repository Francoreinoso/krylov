// Lo que se cambia a mano en el deck. Nada más depende de internet.
window.KRYLOV_CONFIG = {
  // La demo real del producto. De aquí salen el QR del cierre, el texto bajo el QR y lo que abre la tecla D.
  // Cuando el producto final (versión minera) esté publicado, se cambia esta dirección y nada más.
  demo: {
    url: 'https://krylov-tan.vercel.app/',
    texto: 'krylov-tan.vercel.app',
  },
  // Nombres para la lámina de cierre. Se escriben cuando cada persona confirme que se puede mostrar el suyo.
  equipo: [],
  // Tiempos del guion (pitch/PITCH_v2.md), para las notas de cada lámina.
  tiempos: {
    mina: '0:00 a 0:29', rafaga: '0:29 a 0:48', mundos: '0:48 a 1:05', vision: '1:05 a 1:14', leyes: '1:14 a 1:37', taludes: '1:37 a 1:46', flotacion: '1:46 a 1:55', flota: '1:55 a 2:03', sismicidad: '2:03 a 2:12', nube: '2:12 a 2:24', cierre: '2:24 a 2:34',
  },
};
