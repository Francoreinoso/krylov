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
    mina: '0:00 a 0:23', demo: '0:23 a 0:45', mundos: '0:45 a 1:06', mapa: '1:06 a 1:30', donde: '1:30 a 1:51',
    nube: '1:51 a 2:11', vision: '2:11 a 2:23', negocio: '2:23 a 2:43', cierre: '2:43 a 2:51',
  },
};
