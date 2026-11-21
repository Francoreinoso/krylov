/* 1 · El problema, en una mina   ·   8 · Negocio   ·   9 · Cierre
   Las tres comparten la nube de puntos de puntos.js: el deck abre con el rajo y cierra con él envuelto y disperso. */
(function () {
  'use strict';
  const K = window.K;

  // ============================== 1 · El problema ==============================
  K.registrar('mina', {
    tres: null, tQuieto: 5,
    crear: function () { this.p = K.puntos(); if (this.p) this.tres = this.p.tres; },
    alAjustar: function () { if (this.p) this.p.ajustar(); },
    entrar: function () {
      if (!this.p) return;
      const s = this.p.s;
      gsap.killTweensOf(s);
      Object.assign(s, { forma: 0, barrido: 0, brillo: 1, R: 58, el: 0.74, ty: -8, dx: -430 });
      K.anim(s, { barrido: 1 }, 3.6, false, 'power1.inOut', 0.2);
    },
    paso: function (p, inst) {
      if (!this.p) return;
      const s = this.p.s;
      if (inst) s.barrido = 1;
      // En el tercer paso la cámara baja y se acerca: el rajo queda detrás del nombre.
      K.anim(s, p === 2 ? { R: 54, el: 0.56, ty: -15, dx: -560, brillo: 0.9 } : { R: 58, el: 0.74, ty: -8, dx: -430, brillo: 1 }, 2.6, inst);
    },
    cuadro: function (t, dt) { if (this.p) this.p.cuadro(t, dt); },
  });

  // ============================== 8 · Negocio ==============================
  K.registrar('negocio', {
    tres: null, tQuieto: 5,
    crear: function () { this.p = K.puntos(); if (this.p) this.tres = this.p.tres; },
    alAjustar: function () { if (this.p) this.p.ajustar(); },
    entrar: function () {
      if (!this.p) return;
      const s = this.p.s;
      gsap.killTweensOf(s);
      Object.assign(s, { forma: Math.min(s.forma, 1), barrido: 1, brillo: 1, R: 58, el: 0.74, ty: -8, dx: -430 });
    },
    paso: function (p, inst) {
      if (!this.p) return;
      const s = this.p.s;
      K.anim(s, { forma: p === 0 ? 0 : 1 }, p === 0 ? 1.6 : 3.2, inst, 'power2.inOut');
      K.anim(s, p === 0 ? { R: 58, el: 0.74, ty: -8, dx: -430 } : { R: 62, el: 0.3, ty: -4, dx: -520 }, 3.0, inst);
    },
    cuadro: function (t, dt) { if (this.p) this.p.cuadro(t, dt); },
  });

  // ============================== 9 · Cierre ==============================
  K.registrar('cierre', {
    tres: null, tQuieto: 5,
    crear: function (L) {
      this.p = K.puntos();
      if (this.p) this.tres = this.p.tres;
      // El QR se dibuja desde config.js: al cambiar la dirección de la demo, cambia solo.
      const demo = K.config.demo || {}, caja = L.querySelector('#qr');
      L.querySelector('#qr-texto').textContent = demo.texto || demo.url || '';
      if (window.qrcode && demo.url) {
        const q = window.qrcode(0, 'M');
        q.addData(demo.url);
        q.make();
        const n = q.getModuleCount();
        let d = '';
        for (let f = 0; f < n; f++) for (let c = 0; c < n; c++) if (q.isDark(f, c)) d += 'M' + c + ' ' + f + 'h1v1h-1z';
        caja.innerHTML = '<svg viewBox="0 0 ' + n + ' ' + n + '" shape-rendering="crispEdges" role="img" aria-label="QR a ' + (demo.texto || demo.url) + '"><path d="' + d + '" fill="#0b0a09"/></svg>';
      }
    },
    alAjustar: function () { if (this.p) this.p.ajustar(); },
    entrar: function () {
      if (!this.p) return;
      const s = this.p.s;
      gsap.killTweensOf(s);
      s.barrido = 1;
      if (s.forma < 1) s.forma = 1;
      // La esfera de la lámina anterior se abre y queda a la deriva detrás de la frase.
      K.anim(s, { forma: 2, dx: 0, R: 70, el: 0.2, ty: -4, brillo: 0.95 }, 3.4, false, 'power2.inOut');
    },
    cuadro: function (t, dt) { if (this.p) this.p.cuadro(t, dt); },
  });
})();
