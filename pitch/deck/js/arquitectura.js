/* 0 · Cómo funciona (fuera del recorrido): Bayesian Amortized Inference en dos mitades, en tres pasos.
   Paso 0, lo que se hace una sola vez: el modelo bayesiano, el simulador, los datasets simulados y la red que se
   pre-entrena con ellos. Paso 1, lo que pasa con cada dataset: entra, la misma red entrega la posteriori, y de ahí sale
   la decisión. Paso 2, la ficha de los seis modelos: qué modelo es cada uno, con cuántas simulaciones pre-entrenó, en
   cuánto tiempo y cuánto tarda en responder (el sello de cada motor). Sin fórmulas: todo dicho en palabras. */
(function () {
  'use strict';
  const K = window.K;
  const ANCHO = 420, ALTO = 120;

  function caja(clase, x, y, w, titulo, sub) {
    return '<g class="' + clase + '"><rect class="caja" x="' + x + '" y="' + y + '" width="' + w + '" height="' + ALTO + '"/>' +
      '<text x="' + (x + w / 2) + '" y="' + (y + 52) + '">' + titulo + '</text>' +
      '<text class="sub" x="' + (x + w / 2) + '" y="' + (y + 90) + '">' + sub + '</text></g>';
  }

  K.registrar('arquitectura', {
    tQuieto: 3,
    crear: function (L) {
      const xa = 160, xb = 1340, xr = 760, wr = 400, ya = [340, 530, 720], yr = 520;
      const hilos = [
        ['a', 'M ' + (xa + ANCHO / 2) + ' ' + (ya[0] + ALTO) + ' L ' + (xa + ANCHO / 2) + ' ' + ya[1]],                                   // modelo → simulador
        ['a', 'M ' + (xa + ANCHO / 2) + ' ' + (ya[1] + ALTO) + ' L ' + (xa + ANCHO / 2) + ' ' + ya[2]],                                   // simulador → datasets
        ['a', 'M ' + (xa + ANCHO) + ' ' + (ya[2] + ALTO / 2) + ' C 690 ' + (ya[2] + ALTO / 2) + ' 650 ' + (yr + ALTO / 2) + ' ' + xr + ' ' + (yr + ALTO / 2)],   // datasets → red
        ['b', 'M ' + xb + ' ' + (ya[0] + ALTO / 2) + ' C 1250 ' + (ya[0] + ALTO / 2) + ' 1270 ' + (yr + 36) + ' ' + (xr + wr) + ' ' + (yr + 36)],                // tu dataset → red
        ['b', 'M ' + (xr + wr) + ' ' + (yr + 88) + ' C 1250 ' + (yr + 88) + ' 1260 ' + (ya[1] + ALTO / 2) + ' ' + xb + ' ' + (ya[1] + ALTO / 2)],               // red → posteriori
        ['b', 'M ' + (xb + ANCHO / 2) + ' ' + (ya[1] + ALTO) + ' L ' + (xb + ANCHO / 2) + ' ' + ya[2]],                                   // posteriori → decisión
      ];
      let svg = '<svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">' +
        '<rect class="zona-a" x="110" y="200" width="840" height="700"/>' +
        '<rect class="zona-b" x="970" y="200" width="840" height="700"/>' +
        '<g class="a"><text class="zona" x="160" y="278">Antes</text><text class="zona-sub" x="334" y="274">Se hace una sola vez</text></g>' +
        '<g class="b"><text class="zona" x="1020" y="278">En vivo</text><text class="zona-sub" x="1226" y="274">Con cada dataset</text></g>';
      hilos.forEach(function (h, i) { svg += '<g class="' + h[0] + '"><path class="hilo" id="hilo-' + i + '" d="' + h[1] + '"/></g>'; });
      svg += caja('a', xa, ya[0], ANCHO, 'El modelo bayesiano', 'Las reglas del problema') +
        caja('a', xa, ya[1], ANCHO, 'El simulador', 'Genera datasets con esas reglas') +
        caja('a', xa, ya[2], ANCHO, 'Datasets simulados', 'Millones, con su respuesta conocida') +
        caja('red', xr, yr, wr, 'La red', 'Se pre-entrena con ellos') +
        caja('b', xb, ya[0], ANCHO, 'Tu dataset', 'Datos reales') +
        caja('b', xb, ya[1], ANCHO, 'La posteriori', 'La respuesta, con su intervalo') +
        caja('b', xb, ya[2], ANCHO, 'La decisión', 'Qué conviene hacer, y cuánto vale');
      hilos.forEach(function (h, i) { for (let k = 0; k < 3; k++) svg += '<g class="' + h[0] + '"><circle class="gota" r="6" data-hilo="' + i + '" data-fase="' + (k / 3) + '"/></g>'; });
      svg += '</svg>';
      L.querySelector('#plano-arquitectura').innerHTML = svg;
      // Tercer paso: la ficha de los seis modelos, con lo que dice el sello de cada uno (datos.js y, para el yacimiento, config.js).
      const d = K.datos, Y = (K.config.cifras && K.config.cifras.yacimiento) || null;
      const filas = [['La roca', 'Proceso gaussiano espacial', d.sello], ['La pared', 'Fluencia con dos regímenes', d.series.taludes.respuesta.sello],
        ['La planta', 'Cinética de flotación', d.series.flotacion.respuesta.sello], ['Los camiones', 'Proceso gamma de desgaste', d.series.flota.respuesta.sello],
        ['Los túneles', 'Proceso de Hawkes', d.series.sismicidad.respuesta.sello]];
      if (Y) filas.push(['El yacimiento', 'Proceso gaussiano en 3D', Y]);
      L.querySelector('#ficha-modelos').innerHTML =
        '<div class="fila cabeza"><span>Decisión</span><span>Modelo bayesiano</span><span>Simulaciones</span><span>Pre-entrenamiento</span><span>Cada respuesta</span></div>' +
        filas.map(function (f) {
          const S = f[2];
          return '<div class="fila"><span class="t3">' + f[0] + '</span><span class="p">' + f[1] + '</span><span class="num">' + K.miles(S.simulaciones_entrenamiento) + '</span>' +
            '<span class="num">' + S.entrenamiento_min + ' min</span><span class="num cobre">' + S.latencia_ms + ' ms</span></div>';
        }).join('');
      const raiz = L.querySelector('svg');
      this.gotas = Array.prototype.slice.call(raiz.querySelectorAll('circle.gota')).map(function (c) {
        const camino = raiz.querySelector('#hilo-' + c.dataset.hilo);
        return { c: c, camino: camino, largo: camino.getTotalLength(), fase: +c.dataset.fase };
      });
    },
    cuadro: function (t) {
      if (K.donde().paso > 1) return;                             // en la ficha, el diagrama no se ve
      this.gotas.forEach(function (g) {
        const u = (t * 0.22 + g.fase) % 1, p = g.camino.getPointAtLength(u * g.largo);
        g.c.setAttribute('cx', p.x.toFixed(1));
        g.c.setAttribute('cy', p.y.toFixed(1));
        g.c.setAttribute('opacity', (Math.sin(u * Math.PI) * 0.9 + 0.1).toFixed(2));
      });
    },
  });
})();
