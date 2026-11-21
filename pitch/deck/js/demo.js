/* 2 · Demo: el mismo encargo en dos pantallas, al mismo tiempo.
   La de Krylov tarda de verdad 0,69 s (M-09) y muestra el mapa que respondió la red. La del método de siempre avanza en
   tiempo real hacia sus 26.699 s (M-10 = 228 × 117,1 s) hasta que se pide adelantarla; entonces dice «acelerado». */
(function () {
  'use strict';
  const K = window.K;

  function reloj(seg) {
    const s = Math.floor(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
    return h + ':' + (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
  }
  function falta(seg) {
    const s = Math.ceil(seg), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), r = s % 60;
    return 'Faltan ' + h + ' h ' + m + ' min ' + r + ' s';
  }

  // El mapa de decisiones visto desde arriba, con sus curvas de nivel: la misma respuesta de la lámina 4.
  function mapaDesdeArriba() {
    const T = K.datos.terreno, r = K.rejilla(), M = K.rejillaLado, duda = T.umbral_de_duda || 0.1;
    const cv = document.createElement('canvas');
    cv.width = cv.height = M;
    const ctx = cv.getContext('2d'), img = ctx.createImageData(M, M);
    for (let y = 0; y < M; y++) {
      for (let x = 0; x < M; x++) {
        const i = y * M + x, o = ((M - 1 - y) * M + x) * 4;                   // la fila 0 es el sur: se dibuja abajo
        if (r.masc[i] < 0.5) continue;
        const p = r.p[i], m = r.media[i];
        let c = p >= 1 - duda ? [228, 96, 60] : (p <= duda ? [42, 165, 150] : ((x + y) % 7 < 3 ? [140, 108, 40] : [238, 194, 90]));
        const der = r.media[Math.min(M - 1, x + 1) + y * M], arr = r.media[x + Math.min(M - 1, y + 1) * M];
        const curva = Math.floor(m / 100) !== Math.floor(der / 100) || Math.floor(m / 100) !== Math.floor(arr / 100);
        const corte = (m - T.umbral) * (der - T.umbral) < 0 || (m - T.umbral) * (arr - T.umbral) < 0;
        if (curva) c = c.map(function (v) { return v * 0.6; });
        if (corte) c = [255, 255, 255];
        img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2]; img.data[o + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return cv;
  }

  K.registrar('demo', {
    crear: function (L) {
      const a = K.datos.sello.amortizacion, q = function (s) { return L.querySelector(s); };
      this.total = a.mcmc_s;                 // 26.698,8 s
      this.rapido = a.red_s;                 // 0,69 s
      this.n = K.datos.donde.analisis_rehechos;
      this.el = {
        relojLento: q('#reloj-lento'), barraLenta: q('#barra-lenta'), falta: q('#falta-lento'), cualLento: q('#cual-lento'),
        relojK: q('#reloj-krylov'), barraK: q('#barra-krylov'), listo: q('#listo-krylov'), cualK: q('#cual-krylov'),
        acel: q('#acel'), mapa: q('#mapa-demo'),
      };
      this.imagen = mapaDesdeArriba();
      this.o = { lento: 0, mapa: 0 };
    },
    alAjustar: function () {
      const cv = this.el.mapa, lado = Math.round(340 * K.razon(1.6));
      if (cv.width !== lado) { cv.width = cv.height = lado; this.pintarMapa(); }
    },
    entrar: function () { this.tau = 0; this.corre = false; this.o.mapa = 0; },
    // El mapa aparece de arriba hacia abajo, como una imagen que termina de calcularse.
    pintarMapa: function () {
      const cv = this.el.mapa, ctx = cv.getContext('2d'), k = this.o.mapa, w = cv.width;
      ctx.clearRect(0, 0, w, w);
      cv.style.opacity = k > 0 ? 1 : 0;
      if (k <= 0) return;
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, w, w * k); ctx.clip();
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
      ctx.drawImage(this.imagen, 0, 0, w, w);
      ctx.restore();
      if (k < 1) { ctx.fillStyle = '#fff'; ctx.fillRect(0, w * k - 2, w, 2); }
    },
    pintar: function (lento, krylov) {
      const e = this.el, hecho = lento >= this.total - 0.5, partio = krylov > 0 || lento > 0;
      e.barraLenta.style.width = Math.min(100, (lento / this.total) * 100) + '%';
      K.cifra(e.relojLento, reloj(hecho ? Math.round(this.total) : lento));
      e.cualLento.textContent = !partio ? 'En espera' : 'Análisis ' + Math.min(this.n, Math.floor(lento / (this.total / this.n)) + (hecho ? 0 : 1)) + ' de ' + this.n;
      e.falta.textContent = !partio ? ' ' : (hecho ? 'Listo' : falta(this.total - lento));
      const k = K.acotar(krylov / this.rapido, 0, 1);
      e.barraK.style.width = k * 100 + '%';
      K.cifra(e.relojK, K.coma(Math.min(Math.max(krylov, 0), this.rapido), 2));
      e.cualK.textContent = !partio ? 'En espera' : 'Análisis ' + Math.floor(k * this.n) + ' de ' + this.n;
      e.listo.textContent = k >= 1 ? 'Listo' : ' ';
    },
    paso: function (p, inst) {
      const yo = this;
      gsap.killTweensOf(this.o);
      this.el.acel.style.opacity = p === 2 ? 1 : 0;
      if (p === 0) {
        this.corre = false; this.tau = 0; this.o.mapa = 0;
        this.pintar(0, 0); this.pintarMapa();
      } else if (p === 1) {
        this.tau = inst ? 12 : -0.9;         // un momento para que la sala vea la largada
        this.corre = !inst;
        this.o.mapa = inst ? 1 : 0;
        this.pintar(Math.max(this.tau, 0), Math.max(this.tau, 0)); this.pintarMapa();
      } else {
        this.corre = false;
        this.o.lento = Math.max(this.tau, 0);
        this.o.mapa = 1; this.pintarMapa();
        if (inst) { this.pintar(this.total, 1); return; }
        gsap.to(this.o, { lento: this.total, duration: 4.4, ease: 'power2.inOut', onUpdate: function () { yo.pintar(yo.o.lento, 1); } });
      }
    },
    cuadro: function (t, dt) {
      if (!this.corre) return;
      const antes = this.tau, yo = this;
      this.tau += dt;
      this.pintar(Math.max(this.tau, 0), Math.max(this.tau, 0));
      if (antes < this.rapido && this.tau >= this.rapido) {                  // Krylov terminó: aparece su mapa
        gsap.to(this.o, { mapa: 1, duration: 0.7, ease: 'power2.out', onUpdate: function () { yo.pintarMapa(); } });
      }
    },
  });
})();
