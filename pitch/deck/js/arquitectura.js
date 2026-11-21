/* 0 · Cómo funciona (respaldo): la arquitectura en dos mitades. A la izquierda, lo que se hace una sola vez
   (reglas → simulador → casos → la red practica). A la derecha, lo que pasa con cada archivo (la misma red responde).
   Es la inferencia bayesiana amortizada de siempre, dibujada con las palabras del producto y los nombres técnicos debajo. */
(function () {
  'use strict';
  const K = window.K;

  function caja(clase, x, y, w, h, titulo, sub) {
    return '<g class="' + clase + '"><rect class="caja" x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '"/>' +
      '<text x="' + (x + w / 2) + '" y="' + (y + h / 2 - (sub ? 8 : -10)) + '">' + titulo + '</text>' +
      (sub ? '<text class="sub" x="' + (x + w / 2) + '" y="' + (y + h / 2 + 26) + '">' + sub + '</text>' : '') + '</g>';
  }

  K.registrar('arquitectura', {
    tQuieto: 3,
    crear: function (L) {
      const s = K.datos.sello;
      const hilos = [
        ['a', 'M 330 434 L 330 500'],                                  // reglas → simulador
        ['a', 'M 330 604 L 330 670'],                                  // simulador → casos
        ['a', 'M 510 382 C 660 382 660 488 795 488'],                  // reglas → red (la respuesta correcta, θ)
        ['a', 'M 510 722 C 660 722 660 548 795 548'],                  // casos → red (lo que la red ve, x)
        ['b', 'M 1410 382 C 1260 382 1260 488 1125 488'],              // tu archivo → red
        ['b', 'M 1125 548 C 1260 548 1260 552 1410 552'],              // red → respuesta
        ['b', 'M 1590 604 L 1590 670'],                                // respuesta → decisión
      ];
      let svg = '<svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">' +
        '<rect class="zona-a" x="110" y="190" width="820" height="640"/>' +
        '<rect class="zona-b" x="990" y="190" width="820" height="640"/>' +
        '<g class="a"><text class="zona" x="150" y="262">Antes</text><text class="zona-sub" x="318" y="258">SE HACE UNA SOLA VEZ</text></g>' +
        '<g class="b"><text class="zona" x="1030" y="262">En vivo</text><text class="zona-sub" x="1228" y="258">CON CADA ARCHIVO</text></g>';
      hilos.forEach(function (h, i) { svg += '<g class="' + h[0] + '"><path class="hilo" id="hilo-' + i + '" d="' + h[1] + '"/></g>'; });
      svg += caja('a', 150, 330, 360, 104, 'Las reglas del modelo', 'modelo generativo · prior p(θ)') +
        caja('a', 150, 500, 360, 104, 'Simulador', 'p(x | θ)') +
        caja('a', 150, 670, 360, 104, 'Casos simulados', K.miles(s.simulaciones_entrenamiento) + ' terrenos') +
        caja('b', 1410, 330, 360, 104, 'Tu archivo', 'datos reales · x') +
        caja('b', 1410, 500, 360, 104, 'Respuesta con su rango', 'posterior q(θ | x)') +
        caja('b', 1410, 670, 360, 104, 'Decisión', 'colores · costo · dónde medir') +
        caja('red', 795, 446, 330, 144, 'La red', 'codificador + flujo (NPE)') +
        '<g class="a"><text class="sub" x="672" y="398" style="fill:#e2854a">θ: la respuesta</text>' +
        '<text class="sub" x="672" y="706" style="fill:#e2854a">x: lo que se ve</text></g>' +
        '<text class="sub" x="960" y="640">practica aquí · responde allá</text>' +
        '<text class="sub" x="960" y="672">comprobada con SBC y contra MCMC</text>';
      hilos.forEach(function (h, i) { for (let k = 0; k < 3; k++) svg += '<g class="' + h[0] + '"><circle class="gota" r="6" data-hilo="' + i + '" data-fase="' + (k / 3) + '"/></g>'; });
      svg += '</svg>';
      L.querySelector('#plano-arquitectura').innerHTML = svg;
      const raiz = L.querySelector('svg');
      this.gotas = Array.prototype.slice.call(raiz.querySelectorAll('circle.gota')).map(function (c) {
        const camino = raiz.querySelector('#hilo-' + c.dataset.hilo);
        return { c: c, camino: camino, largo: camino.getTotalLength(), fase: +c.dataset.fase };
      });
    },
    cuadro: function (t) {
      this.gotas.forEach(function (g) {
        const u = (t * 0.22 + g.fase) % 1, p = g.camino.getPointAtLength(u * g.largo);
        g.c.setAttribute('cx', p.x.toFixed(1));
        g.c.setAttribute('cy', p.y.toFixed(1));
        g.c.setAttribute('opacity', (Math.sin(u * Math.PI) * 0.9 + 0.1).toFixed(2));
      });
    },
  });
})();
