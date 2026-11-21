/* Lo que Krylov entrega: para cada unidad, una estimación con su intervalo de credibilidad de 90% (los cuantiles 5% y 95%
   de la posteriori que devuelve el motor), contra el límite con que se decide. Cada barra es un intervalo; la marca clara,
   la estimación; el color, la decisión. Lo usan las láminas de cada decisión, la de «¿cómo sé que acierta?» y la de la tecla M.
   Todo sale de datos.js: aquí no se calcula ningún intervalo. */
(function () {
  'use strict';
  const K = window.K;
  const ESTADOS = ['no_actuar', 'en_duda', 'actuar'];           // el orden con que generar.py numera los estados del terreno

  // caja: el elemento donde se dibuja. o: { filas: [{nombre?, bajo, medio, alto, estado, verdad?}], min, max, log?, limite,
  //   rotuloLimite, rotuloMin, rotuloMax, valor?: fila → texto }
  K.intervalos = function (caja, o) {
    const a = o.log ? Math.log(o.min) : o.min, b = o.log ? Math.log(o.max) : o.max;
    const pc = function (v) { return (K.acotar(((o.log ? Math.log(Math.max(v, 1e-9)) : v) - a) / (b - a), 0, 1) * 100).toFixed(2) + '%'; };
    // la línea blanca lleva su nombre arriba, grande, y una frase abajo que dice de dónde sale
    let h = '<div class="cabeza-eje"><span></span><span class="riel"><span class="lim">' + o.rotuloLimite + '</span></span><span></span></div><div class="filas">';
    o.filas.forEach(function (f, i) {
      h += '<div class="fila" style="--d:' + (0.2 + i * 0.07).toFixed(2) + 's">' + (f.nombre ? '<span class="nom">' + f.nombre + '</span>' : '<span></span>') +
        '<span class="riel"><i class="barra ' + f.estado.replace('_', '-') + '" style="left:' + pc(f.bajo) + ';right:calc(100% - ' + pc(f.alto) + ')"></i>' +
        '<i class="punto" style="left:' + pc(f.medio) + '"></i>' + (f.verdad != null ? '<i class="real" style="left:' + pc(f.verdad) + '"></i>' : '') + '</span>' +
        '<span class="val">' + (o.valor ? o.valor(f) : '') + '</span></div>';
    });
    h += '</div><div class="eje"><span></span><span class="riel"><span class="izq">' + (o.rotuloMin || '') + '</span><span class="der">' + (o.rotuloMax || '') + '</span></span><span></span></div>' +
      (o.nota ? '<div class="nota-linea"><i></i>' + o.nota + '</div>' : '');
    caja.classList.add('intervalos');
    caja.classList.toggle('sin-nombres', !o.filas[0].nombre);
    caja.classList.toggle('sin-valores', !o.valor);
    caja.style.setProperty('--limite', pc(o.limite));
    caja.innerHTML = h;
  };

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
      return { filas: filas, min: 0, max: 36, limite: S.horizonte, rotuloLimite: S.horizonte + ' horas', rotuloMin: 'ahora', rotuloMax: '36 horas',
        nota: 'La línea blanca son las próximas ' + S.horizonte + ' horas: lo que puede ceder antes, conviene cerrarlo hoy.',
        valor: function (f) { return K.coma(f.bajo, 1) + ' a ' + K.coma(Math.min(f.alto, 99), f.alto < 10 ? 1 : 0) + ' h'; } };
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
        valor: function (f) { return Math.round(f.bajo * 100) + ' a ' + Math.round(f.alto * 100) + '%'; } };
    },
  };
  // Para cualquier otro caso: el riesgo de cada unidad (la probabilidad de lo que se quiere evitar) con su intervalo,
  // contra el punto de corte, que es el riesgo desde el cual conviene actuar y sale de comparar los dos costos del caso.
  K.filasDe.riesgo = function (caso, nota) {
    const S = K.datos.series[caso], R = S.respuesta, filas = [];
    let tope = R.punto_de_corte;
    S.unidades.forEach(function (un) {
      const r = R.unidades[un.id];
      if (r && r.rango && r.rango[0] != null) { filas.push({ nombre: K.nombreDe(un.id), bajo: r.rango[0], medio: r.p, alto: r.rango[1], estado: r.estado }); tope = Math.max(tope, r.rango[1]); }
    });
    filas.sort(function (x, y) { return y.medio - x.medio; });
    const max = Math.min(1, Math.ceil(tope * 1.25 * 20) / 20), pct = function (v) { return K.coma(v * 100, v < 0.1 ? 1 : 0).replace(',0', '') + '%'; };
    return { filas: filas, min: 0, max: max, limite: R.punto_de_corte, rotuloLimite: pct(R.punto_de_corte) + ' de riesgo', rotuloMin: '0%', rotuloMax: Math.round(max * 100) + '%', nota: nota,
      valor: function (f) { return Math.round(f.bajo * 100) + ' a ' + Math.round(f.alto * 100) + '%'; } };
  };
  K.filasDe.sismicidad = function () { return K.filasDe.riesgo('sismicidad', 'La línea blanca es el riesgo desde el cual conviene mantener cerrado: sale de lo que cuesta cerrar y lo que cuesta equivocarse.'); };
  K.filasDe.flota = function () { return K.filasDe.riesgo('flota', 'La línea blanca es el riesgo desde el cual conviene adelantar la mantención: sale de comparar lo que cuesta parar con lo que cuesta una falla.'); };

  // En pantalla, el nombre de cada unidad se dice completo: «Sector 25», no «S-25».
  K.nombreDe = function (id) { return id.replace(/^S-0?/, 'Sector ').replace(/^L-0?/, 'Línea ').replace(/^CAEX-/, 'Camión '); };

  // la lámina de la roca tiene su escena en terreno.js; su gráfico se llena aquí, al cargar
  const roca = document.getElementById('int-leyes'), valor = document.getElementById('valor-leyes');
  if (roca) K.intervalos(roca, K.filasDe.leyes(13));
  if (valor) valor.textContent = K.orden(K.datos.terreno.costo_de_no_saber);
})();
