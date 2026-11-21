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
    valor: '0:00 a 0:13', paradigma: '0:13 a 0:32', flujo: '0:32 a 0:48', mundos: '0:48 a 0:55', rafaga: '0:55 a 1:02', vision: '1:02 a 1:10', leyes: '1:10 a 1:34', taludes: '1:34 a 1:51', flotacion: '1:51 a 2:02', sismicidad: '2:02 a 2:19', confianza: '2:19 a 2:29', cierre: '2:29 a 2:39',
  },
};
