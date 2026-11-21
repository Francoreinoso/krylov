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
    valor: '0:00 a 0:13', paradigma: '0:13 a 0:32', flujo: '0:32 a 0:49', mundos: '0:49 a 0:56', rafaga: '0:56 a 1:03', vision: '1:03 a 1:12', leyes: '1:12 a 1:36', taludes: '1:36 a 1:53', flotacion: '1:53 a 2:04', flota: '2:04 a 2:14', sismicidad: '2:14 a 2:26', confianza: '2:26 a 2:38', cierre: '2:38 a 2:48',
  },
};
