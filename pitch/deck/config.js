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
    valor: '0:00 a 0:17', paradigma: '0:17 a 0:36', flujo: '0:36 a 0:51', mundos: '0:51 a 0:58', rafaga: '0:58 a 1:13', vision: '1:13 a 1:22', leyes: '1:22 a 1:40', taludes: '1:40 a 1:49', flotacion: '1:49 a 1:59', flota: '1:59 a 2:07', sismicidad: '2:07 a 2:16', confianza: '2:16 a 2:29', cierre: '2:29 a 2:39',
  },
};
