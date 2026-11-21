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
    let h = '<div class="filas">';
    o.filas.forEach(function (f, i) {
      h += '<div class="fila" style="--d:' + (0.2 + i * 0.07).toFixed(2) + 's">' + (f.nombre ? '<span class="nom">' + f.nombre + '</span>' : '<span></span>') +
        '<span class="riel"><i class="barra ' + f.estado.replace('_', '-') + '" style="left:' + pc(f.bajo) + ';right:calc(100% - ' + pc(f.alto) + ')"></i>' +
        '<i class="punto" style="left:' + pc(f.medio) + '"></i>' + (f.verdad != null ? '<i class="real" style="left:' + pc(f.verdad) + '"></i>' : '') + '</span>' +
        '<span class="val">' + (o.valor ? o.valor(f) : '') + '</span></div>';
    });
    h += '</div><div class="eje"><span></span><span class="riel"><span class="izq">' + (o.rotuloMin || '') + '</span><span class="lim">' + o.rotuloLimite + '</span><span class="der">' + (o.rotuloMax || '') + '</span></span><span></span></div>';
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
      return { filas: filas, min: 110, max: 2400, log: true, limite: T.umbral, rotuloLimite: 'Límite: ' + K.miles(T.umbral) + ' ppm', rotuloMin: 'menos arsénico', rotuloMax: 'más' };
    },
    // la pared: cuántas horas le faltan a cada sector que se acelera
    taludes: function () {
      const S = K.datos.series.taludes, R = S.respuesta, filas = [];
      S.unidades.forEach(function (un) { const r = R.unidades[un.id], m = r && r.curva && r.curva.marca; if (m) filas.push({ nombre: K.nombreDe(un.id), bajo: m.bajo, medio: m.medio, alto: m.alto, estado: r.estado }); });
      filas.sort(function (x, y) { return x.medio - y.medio; });
      return { filas: filas, min: 0, max: 36, limite: S.horizonte, rotuloLimite: 'Próximas ' + S.horizonte + ' horas', rotuloMin: '', rotuloMax: '36 h',
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
      return { filas: filas, min: 0.75, max: 0.93, limite: S.umbral, rotuloLimite: 'Meta: ' + Math.round(S.umbral * 100) + '%', rotuloMin: '75%', rotuloMax: '93%',
        valor: function (f) { return Math.round(f.bajo * 100) + ' a ' + Math.round(f.alto * 100) + '%'; } };
    },
  };
  // En pantalla, el nombre de cada unidad se dice completo: «Sector 25», no «S-25».
  K.nombreDe = function (id) { return id.replace(/^S-0?/, 'Sector ').replace(/^L-0?/, 'Línea ').replace(/^CAEX-/, 'Camión '); };

  // la lámina de la roca tiene su escena en terreno.js; su gráfico se llena aquí, al cargar
  const roca = document.getElementById('int-leyes');
  if (roca) K.intervalos(roca, K.filasDe.leyes(13));
})();
