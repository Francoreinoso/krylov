/* Las filas de cada caso, tal como las entrega su motor: para cada unidad, una estimación con su intervalo de credibilidad
   de 90% (los cuantiles 5% y 95% de la posteriori), el eje en que se dibuja y el límite con que se decide.
   De aquí toma su eje la tarjeta del foco (js/foco.js). Todo sale de datos.js: aquí no se calcula ningún intervalo. */
(function () {
  'use strict';
  const K = window.K;
  const ESTADOS = ['no_actuar', 'en_duda', 'actuar'];           // el orden con que generar.py numera los estados del terreno

  // ---- las filas de cada caso, tal como las entrega su motor ----
  K.filasDe = {
    // el terreno: una muestra pareja de sus partes, de la que menos arsénico tiene a la que más
    leyes: function (cuantas) {
      const T = K.datos.terreno, orden = T.media.map(function (m, i) { return i; }).sort(function (x, y) { return T.media[x] - T.media[y]; }), filas = [];
      for (let k = 0; k < cuantas; k++) { const i = orden[Math.floor(((k + 0.5) / cuantas) * orden.length)]; filas.push({ bajo: T.bajo[i], medio: T.media[i], alto: T.alto[i], estado: ESTADOS[T.estado[i]] }); }
      return { filas: filas, min: 110, max: 2400, log: true, limite: T.umbral, rotuloLimite: 'Máximo que acepta la planta', rotuloMin: 'menos arsénico', rotuloMax: 'más arsénico',
        nota: 'La línea blanca es el arsénico máximo con que la roca puede ir a la planta.' };
    },
    // la pared: cuántas horas le faltan a cada sector que se acelera
    taludes: function () {
      const S = K.datos.series.taludes, R = S.respuesta, filas = [];
      S.unidades.forEach(function (un) { const r = R.unidades[un.id], m = r && r.curva && r.curva.marca; if (m) filas.push({ nombre: K.nombreDe(un.id), bajo: m.bajo, medio: m.medio, alto: m.alto, estado: r.estado }); });
      filas.sort(function (x, y) { return x.medio - y.medio; });
      // sin columna de valores: las barras ya lo dicen y la tarjeta da el número. La tarjeta usa un eje más corto (0 a 18 h).
      return { filas: filas, min: 0, max: 36, limite: S.horizonte, rotuloLimite: S.horizonte + ' horas', rotuloMin: 'ahora', rotuloMax: '36 horas',
        nota: 'La línea blanca son las próximas ' + S.horizonte + ' horas: lo que puede ceder antes, conviene cerrarlo hoy.',
        zoomMax: function () { return 18; } };
    },
    // la planta: el cobre que va a recuperar cada línea al final (el último punto del abanico de su curva)
    flotacion: function (conVerdad) {
      const S = K.datos.series.flotacion, R = S.respuesta, filas = [];
      S.unidades.forEach(function (un) {
        const r = R.unidades[un.id], c = r && r.curva, n = c && c.t_banda.length - 1, v = S.verdad[un.id];
        if (c) filas.push({ nombre: K.nombreDe(un.id), bajo: c.bajo[n], medio: c.medio[n], alto: c.alto[n], estado: r.estado, verdad: conVerdad && v ? +v.recuperacion_final : null });
      });
      filas.sort(function (x, y) { return x.medio - y.medio; });
      return { filas: filas, min: 0.75, max: 0.93, limite: S.umbral, rotuloLimite: 'Meta de la planta: ' + Math.round(S.umbral * 100) + '%', rotuloMin: '75%', rotuloMax: '93%',
        nota: 'La línea blanca es la meta de recuperación de la planta: bajo ella, se pierde cobre.',
        // la columna de valores queda solo en la lámina de la tecla M (conVerdad), donde el gráfico es todo el contenido
        valor: conVerdad ? function (f) { return Math.round(f.bajo * 100) + ' a ' + Math.round(f.alto * 100) + '%'; } : null };
    },
  };
  // Para cualquier otro caso: el riesgo de cada unidad (la probabilidad de lo que se quiere evitar) con su intervalo,
  // contra el punto de corte, que es el riesgo desde el cual conviene actuar y sale de comparar los dos costos del caso.
  // cuantas (opcional): solo las de más riesgo, y siempre hasta la unidad que abre la tarjeta del zoom.
  K.filasDe.riesgo = function (caso, nota, cuantas) {
    const S = K.datos.series[caso], R = S.respuesta;
    let filas = [];
    let tope = R.punto_de_corte;
    S.unidades.forEach(function (un) {
      const r = R.unidades[un.id];
      if (r && r.rango && r.rango[0] != null) { filas.push({ id: un.id, nombre: K.nombreDe(un.id), bajo: r.rango[0], medio: r.p, alto: r.rango[1], estado: r.estado }); tope = Math.max(tope, r.rango[1]); }
    });
    filas.sort(function (x, y) { return y.medio - x.medio; });
    if (cuantas && filas.length > cuantas) {
      filas = filas.slice(0, cuantas);
    }
    const max = Math.min(1, Math.ceil(tope * 1.25 * 20) / 20), pct = function (v) { return K.coma(v * 100, v < 0.1 ? 1 : 0).replace(',0', '') + '%'; };
    // sin columna de valores. La tarjeta acorta el eje cuando el gráfico va mucho más allá de su unidad.
    return { filas: filas, min: 0, max: max, limite: R.punto_de_corte, rotuloLimite: pct(R.punto_de_corte) + ' de riesgo', rotuloMin: '0%', rotuloMax: Math.round(max * 100) + '%', nota: nota,
      zoomMax: function (q) { return Math.min(max, Math.ceil(Math.max(R.punto_de_corte, q.alto) * 2 * 20) / 20); } };
  };
  K.filasDe.sismicidad = function () { return K.filasDe.riesgo('sismicidad', 'La línea blanca es el riesgo desde el cual conviene mantener cerrado: sale de lo que cuesta cerrar y lo que cuesta equivocarse.'); };
  // la flota trae 40 camiones: van los de más riesgo (ocho, o hasta el que abre la tarjeta), para que la columna quepa en el cuadro
  K.filasDe.flota = function () { return K.filasDe.riesgo('flota', 'La línea blanca es el riesgo desde el cual conviene adelantar la mantención: sale de comparar lo que cuesta parar con lo que cuesta una falla.', 8); };

  // En pantalla, el nombre de cada unidad se dice completo: «Sector 25», no «S-25».
  K.nombreDe = function (id) { return id.replace(/^S-0?/, 'Sector ').replace(/^L-0?/, 'Línea ').replace(/^CAEX-/, 'Camión '); };

})();
