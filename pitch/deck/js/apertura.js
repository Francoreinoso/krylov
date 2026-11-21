/* 1 · Apertura: un plano naval que se dibuja solo, un casco roto y la tabla que ya traía la respuesta.
   Es una ilustración (va rotulada): ni el barco ni la tabla reproducen un documento histórico. */
(function () {
  'use strict';
  const K = window.K;
  const ROM = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'];
  const CASCO = 'M 92 250 L 1500 244 C 1532 244 1550 266 1553 298 C 1556 332 1540 372 1488 380 L 172 380 C 122 380 98 338 92 250 Z';
  const ROTO = 9, CONTRA = 2;                         // compartimentos X y III
  const ESCORA = 2.6;

  function plano() {
    const xs = [];
    for (let i = 0; i <= 12; i++) xs.push(190 + i * 105);
    const cubierta = function (x) { return 250 - (6 * (x - 92)) / 1408; };
    let cuad = '';
    for (let x = 0; x <= 1920; x += 80) cuad += '<line x1="' + x + '" y1="0" x2="' + x + '" y2="1080"/>';
    for (let y = 40; y <= 1080; y += 80) cuad += '<line x1="0" y1="' + y + '" x2="1920" y2="' + y + '"/>';

    let mamparos = '', numeros = '', ojos = '';
    xs.forEach(function (x) { mamparos += '<path class="tz mamparo" d="M ' + x + ' ' + cubierta(x).toFixed(1) + ' L ' + x + ' 380"/>'; });
    for (let k = 0; k < 12; k++) numeros += '<text class="num" x="' + (xs[k] + 52.5) + '" y="350">' + ROM[k] + '</text>';
    for (let x = 240; x <= 1420; x += 105) ojos += '<circle class="tz fino" cx="' + x + '" cy="274" r="6"/>';

    const obra = [
      'M 300 246 L 312 212 L 398 212 L 410 246', 'M 312 222 L 196 215',                       // torre de popa y su cañón
      'M 600 246 L 600 196 L 1010 196 L 1010 246', 'M 900 196 L 900 158 L 992 158 L 992 196',  // superestructura y puente
      'M 680 196 L 688 94 L 748 94 L 756 196', 'M 800 196 L 808 94 L 868 94 L 876 196',        // chimeneas
      'M 520 246 L 520 58', 'M 488 110 L 552 110', 'M 508 86 L 532 86 L 532 72 L 508 72 Z',     // palo de popa
      'M 1060 246 L 1060 38', 'M 1022 96 L 1098 96', 'M 1048 70 L 1072 70 L 1072 56 L 1048 56 Z', // palo de proa
      'M 1150 246 L 1162 212 L 1250 212 L 1262 246', 'M 1250 222 L 1376 213',                   // torre de proa
      'M 100 250 L 84 168',                                                                       // asta
    ].map(function (d) { return '<path class="tz obra" d="' + d + '"/>'; }).join('');
    const finos = [
      'M 150 300 L 1528 300', 'M 520 58 L 112 248', 'M 520 58 L 1060 38', 'M 1060 38 L 1498 244',
      'M 686 120 L 750 120', 'M 806 120 L 870 120', 'M 122 372 L 98 392 L 124 398',
      'M 92 420 L 1553 420', 'M 92 410 L 92 430', 'M 1553 410 L 1553 430', 'M 1612 318 L 1612 380', 'M 1602 318 L 1622 318', 'M 1602 380 L 1622 380',
    ].map(function (d) { return '<path class="tz fino" d="' + d + '"/>'; }).join('');

    // La tabla: «si se rompe → se inunda». Pares simétricos respecto del centro del barco.
    const pares = [[7, 4], [8, 3], [9, 2], [10, 1]], tx = 1330, ty = 650;
    let tabla = '<text class="cab t" x="' + (tx + 110) + '" y="' + (ty + 14) + '">SI SE ROMPE</text><text class="cab t" x="' + (tx + 360) + '" y="' + (ty + 14) + '">SE INUNDA</text>';
    pares.forEach(function (par, r) {
      const y = ty + 44 + r * 72;
      tabla += '<g class="t">' +
        '<rect class="celda" x="' + tx + '" y="' + y + '" width="220" height="62" rx="8"/>' +
        '<rect class="celda" x="' + (tx + 250) + '" y="' + y + '" width="220" height="62" rx="8"/>' +
        (par[0] === ROTO ? '<rect class="luz" id="fila-luz" x="' + (tx - 8) + '" y="' + (y - 7) + '" width="486" height="76" rx="12"/>' : '') +
        '<text x="' + (tx + 110) + '" y="' + (y + 33) + '">' + ROM[par[0]] + '</text>' +
        '<text class="fl" x="' + (tx + 235) + '" y="' + (y + 33) + '">→</text>' +
        '<text x="' + (tx + 360) + '" y="' + (y + 33) + '">' + ROM[par[1]] + '</text></g>';
    });

    return '<svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">' +
      '<defs><clipPath id="clip-casco"><path d="' + CASCO + '"/></clipPath></defs>' +
      '<g class="cuad" id="cuad">' + cuad + '</g>' +
      '<g id="barco"><g transform="translate(160,130)">' +
        '<g clip-path="url(#clip-casco)">' +
          '<rect class="inunda" id="inunda" x="' + xs[ROTO] + '" y="380" width="105" height="0"/>' +
          '<rect class="contra" id="contra" x="' + xs[CONTRA] + '" y="380" width="105" height="0"/></g>' +
        '<path class="tz casco" d="' + CASCO + '"/>' + mamparos + obra + ojos + finos + numeros +
        '<text class="cota" x="822" y="446" text-anchor="middle">ESLORA</text>' +
        '<text class="cota" x="1634" y="355">CALADO</text>' +
        '<path id="rotura" d="M ' + (xs[ROTO] + 18) + ' 381 l 12 -20 l 11 15 l 12 -24 l 11 19 l 12 -14 l 10 24" fill="none" stroke="#ff6b6b" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" opacity="0"/>' +
      '</g></g>' +
      '<line class="tz agua" id="agua" x1="40" y1="448" x2="1880" y2="448" opacity="0"/>' +
      '<g class="tabla" id="tabla">' + tabla + '</g>' +
      '</svg>';
  }

  K.registrar('apertura', {
    crear: function (L) {
      const raiz = L.querySelector('#plano-barco');
      raiz.innerHTML = plano();
      const q = function (sel) { return Array.prototype.slice.call(raiz.querySelectorAll(sel)); };
      this.e = {
        cuad: q('#cuad'), barco: q('#barco'), casco: q('.tz.casco'), mamparos: q('.tz.mamparo'), obra: q('.tz.obra'), finos: q('.tz.fino'),
        nums: q('.num, .cota'), agua: q('#agua'), inunda: q('#inunda'), contra: q('#contra'), rotura: q('#rotura'),
        tabla: q('#tabla .t'), luz: q('#fila-luz'),
      };
      this.trazos = this.e.casco.concat(this.e.mamparos, this.e.obra, this.e.finos);
      this.trazos.forEach(function (t) {
        t._largo = Math.ceil(t.getTotalLength()) + 2;
        t.style.strokeDasharray = t._largo;
      });
    },
    fijar: function (p) {
      const e = this.e, dib = p >= 1;
      gsap.set(this.trazos, { strokeDashoffset: function (i, t) { return dib ? 0 : t._largo; } });
      gsap.set(e.cuad, { opacity: dib ? 1 : 0 });
      gsap.set(e.nums, { opacity: dib ? 1 : 0 });
      gsap.set(e.agua, { opacity: dib ? 0.8 : 0 });
      gsap.set(e.inunda, { attr: { y: p >= 2 ? 296 : 380, height: p >= 2 ? 84 : 0 }, opacity: p >= 2 ? 0.78 : 0 });
      gsap.set(e.rotura, { opacity: p >= 2 ? 1 : 0 });
      gsap.set(e.contra, { attr: { y: 380, height: 0 }, opacity: 0 });
      gsap.set(e.barco, { rotation: p >= 2 ? ESCORA : 0, svgOrigin: '960 448' });
      gsap.set(e.tabla, { opacity: 0 });
      gsap.set(e.luz, { opacity: 0 });
    },
    paso: function (p, inst) {
      const e = this.e;
      if (this.tl) this.tl.kill();
      this.fijar(p);
      const tl = (this.tl = K.linea(inst));
      if (p === 0) {
        tl.to(e.cuad, { opacity: 1, duration: 0.9 }, 0)
          .to(e.casco, { strokeDashoffset: 0, duration: 1.9, ease: 'power2.inOut' }, 0.15)
          .to(e.mamparos, { strokeDashoffset: 0, duration: 0.55, stagger: 0.05, ease: 'power1.out' }, 1.0)
          .to(e.obra, { strokeDashoffset: 0, duration: 1.0, stagger: 0.07, ease: 'power1.inOut' }, 1.2)
          .to(e.finos, { strokeDashoffset: 0, duration: 0.9, stagger: 0.03, ease: 'power1.inOut' }, 1.9)
          .to(e.nums, { opacity: 1, duration: 0.4, stagger: 0.04 }, 2.3)
          .to(e.agua, { opacity: 0.8, duration: 0.9 }, 2.5);
      } else if (p === 1) {
        tl.to(e.rotura, { opacity: 1, duration: 0.12, repeat: 3, yoyo: true }, 0)
          .to(e.inunda, { opacity: 0.78, attr: { y: 296, height: 84 }, duration: 1.7, ease: 'power1.in' }, 0.15)
          .to(e.barco, { rotation: ESCORA, duration: 2.6, ease: 'power2.inOut' }, 0.25);
      } else {
        tl.to(e.tabla, { opacity: 1, duration: 0.45, stagger: 0.08 }, 0)
          .to(e.luz, { opacity: 1, duration: 0.4 }, 0.9)
          .to(e.contra, { opacity: 0.72, attr: { y: 296, height: 84 }, duration: 1.5, ease: 'power1.inOut' }, 1.2)
          .to(e.barco, { rotation: 0, duration: 2.4, ease: 'power2.inOut' }, 1.4);
      }
    },
  });
})();
