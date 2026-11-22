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
  // Tiempos propuestos para tres minutos con las 14 láminas del recorrido, para las notas de cada lámina.
  // El guion (pitch/PITCH_v2.md) es anterior a esta iteración: hay que cronometrarlo de nuevo en un ensayo.
  tiempos: {
    valor: '0:00 a 0:12', paradigma: '0:12 a 0:30', flujo: '0:30 a 0:46', mundos: '0:46 a 0:55', rafaga: '0:55 a 1:02', vision: '1:02 a 1:10', leyes: '1:10 a 1:30', taludes: '1:30 a 1:44', flotacion: '1:44 a 1:54', flota: '1:54 a 2:04', sismicidad: '2:04 a 2:16', yacimiento: '2:16 a 2:36', confianza: '2:36 a 2:48', cierre: '2:48 a 3:00',
  },
};
