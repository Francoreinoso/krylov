// Lo que se cambia a mano en el deck. Nada más depende de internet.
window.KRYLOV_CONFIG = {
  // La demo real del producto. De aquí salen el QR del cierre, el texto bajo el QR y lo que abre la tecla D.
  // Cuando el producto final (versión minera) esté publicado, se cambia esta dirección y nada más.
  demo: {
    url: 'https://krylov-tan.vercel.app/',
    texto: 'krylov-tan.vercel.app',
  },
  // Cifras que no salen de datos.js porque se midieron con el computador libre, no al generar los datos.
  cifras: {
    donde_perforo_s: 1.3,     // M-44: los 480 análisis de «¿Dónde perforo?» en `leyes`, sin nada entrenando
  },
  // Nombres para la lámina de cierre. Se escriben cuando cada persona confirme que se puede mostrar el suyo.
  equipo: [],
  // Tiempos del guion (pitch/PITCH_v2.md), para las notas de cada lámina.
  tiempos: {
    valor: '0:00 a 0:13', paradigma: '0:13 a 0:32', flujo: '0:32 a 0:45', mundos: '0:45 a 0:52', rafaga: '0:52 a 1:06', vision: '1:06 a 1:15', leyes: '1:15 a 1:39', taludes: '1:39 a 1:56', flotacion: '1:56 a 2:04', flota: '2:04 a 2:12', sismicidad: '2:12 a 2:23', confianza: '2:23 a 2:34', cierre: '2:34 a 2:43',
  },
};
