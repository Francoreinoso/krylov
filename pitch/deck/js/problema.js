/* 2 · El problema: la carrera. La barra de Krylov tarda de verdad 0,69 s (M-09); la del método lento avanza
   en tiempo real hacia sus 26.699 s (M-10) hasta que se pide adelantarla, y entonces dice «acelerado». */
(function () {
  'use strict';
  const K = window.K;

  function reloj(seg) {
    const s = Math.floor(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
    return h + ':' + (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
  }
  function falta(seg) {
    const s = Math.ceil(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
    return 'faltan ' + h + ' h ' + m + ' min ' + r + ' s';
  }

  K.registrar('problema', {
    crear: function (L) {
      const a = K.datos.sello.amortizacion;
      this.total = a.mcmc_s;                 // 26.698,8 s
      this.rapido = a.red_s;                 // 0,69 s
      this.el = {
        relojLento: L.querySelector('#reloj-lento'), barraLenta: L.querySelector('#barra-lenta'), falta: L.querySelector('#falta-lento'),
        relojK: L.querySelector('#reloj-krylov'), barraK: L.querySelector('#barra-krylov'), listo: L.querySelector('#listo-krylov'),
        acel: L.querySelector('#acel'),
      };
      this.o = { lento: 0 };
    },
    entrar: function () { this.tau = 0; this.corre = false; },
    pintar: function (lento, krylov) {
      const e = this.el, hecho = lento >= this.total - 0.5;
      e.barraLenta.style.width = Math.min(100, (lento / this.total) * 100) + '%';
      e.relojLento.textContent = reloj(hecho ? Math.round(this.total) : lento);
      e.falta.textContent = hecho ? 'listo' : (lento > 0 ? falta(this.total - lento) : 'en tiempo real');
      const k = K.acotar(krylov / this.rapido, 0, 1);
      e.barraK.style.width = k * 100 + '%';
      e.relojK.textContent = K.coma(Math.min(krylov, this.rapido), 2);
      e.listo.textContent = k >= 1 ? 'listo ✓' : ' ';
    },
    paso: function (p, inst) {
      const yo = this;
      gsap.killTweensOf(this.o);
      this.el.acel.style.opacity = p === 2 ? 1 : 0;
      if (p === 0) {
        this.corre = false; this.tau = 0;
        this.pintar(0, 0);
      } else if (p === 1) {
        this.tau = inst ? 12 : -1.0;         // un segundo para que la sala vea la largada
        this.corre = !inst;
        this.pintar(Math.max(this.tau, 0), Math.max(this.tau, 0));
      } else {
        this.corre = false;
        this.o.lento = Math.max(this.tau, 0);
        if (inst) { this.pintar(this.total, 1); return; }
        gsap.to(this.o, { lento: this.total, duration: 4.4, ease: 'power2.inOut', onUpdate: function () { yo.pintar(yo.o.lento, 1); } });
      }
    },
    cuadro: function (t, dt) {
      if (!this.corre) return;
      this.tau += dt;
      this.pintar(Math.max(this.tau, 0), Math.max(this.tau, 0));
    },
  });
})();
