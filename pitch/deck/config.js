// Lo que se cambia a mano en el deck. Nada más depende de internet.
window.KRYLOV_CONFIG = {
  // La demo real del producto. De aquí salen el QR del cierre, el texto bajo el QR y lo que abre la tecla D.
  // Cuando el producto final (versión minera) esté publicado, se cambia esta dirección y nada más.
  demo: {
    url: 'https://krylov-krylov.vercel.app/',
    texto: 'krylov-krylov.vercel.app',
  },
  // Cifras que no salen de datos.js porque se midieron con el computador libre, no al generar los datos.
  cifras: {
    donde_perforo_s: 1.3,     // M-44: los 480 análisis de «¿Dónde perforo?» en `leyes`, sin nada entrenando
    yacimiento: { simulaciones_entrenamiento: 126696, entrenamiento_min: 110, latencia_ms: 19 },   // M-63 y M-64: la ficha del sexto modelo (tecla 0)
    yacimiento_cobertura_90: 0.901,   // M-63: el mapa del yacimiento, en 2.000 yacimientos simulados nuevos (yacimiento/artefactos/sello.json)
  },
  // Nombres para la lámina de cierre. Se escriben cuando cada persona confirme que se puede mostrar el suyo.
  equipo: [],
  // Tiempos del guion final (pitch/PITCH_FINAL.md) para las notas de cada lámina: contados a 150 palabras por minuto
  // más 1,2 segundos por pulsación. Es una cuenta: el cronómetro de verdad es el ensayo.
  tiempos: {
    valor: '0:00 a 0:13', paradigma: '0:13 a 0:23', flujo: '0:23 a 0:34', mundos: '0:34 a 0:38', rafaga: '0:38 a 0:43', vision: '0:43 a 0:48', leyes: '0:48 a 1:03', taludes: '1:03 a 1:10', flotacion: '1:10 a 1:14', flota: '1:14 a 1:17', sismicidad: '1:17 a 1:23', yacimiento: '1:23 a 1:44', confianza: '1:44 a 1:52', cierre: '1:52 a 2:00',
  },
};
