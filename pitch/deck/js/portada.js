/* 1 · El valor, a primera vista: lo que con el método de siempre toma más de 7 horas, Krylov lo responde en 0,69 segundos.
   Las dos cifras salen del sello del motor espacial (M-09 y M-10: rehacer 228 análisis completos).
   La barra está a escala: mide las 7 horas y 25 minutos del método lento. A esa misma escala, los 0,69 segundos
   de Krylov miden menos de un píxel; por eso se dibuja como un punto, que late una vez cada 0,69 segundos. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 110, X1 = 1810, Y = 946;
  const MONO = '"JetBrains Mono", monospace', TEXTO = '"Instrument Sans", sans-serif';

  K.registrar('valor', {
    tQuieto: 9,
    crear: function (L) {
      const A = K.datos.sello.amortizacion;
      this.lento = A.mcmc_s;
      this.red = A.red_s;
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      const h = Math.floor(this.lento / 3600), min = Math.round((this.lento - h * 3600) / 60);
      this.horas = h;
      this.total = h + ' h ' + min + ' min';
      this.pixeles = (this.red / this.lento) * (X1 - X0);            // lo que mediría Krylov en esta barra
      L.querySelector('#valor-lento').textContent = h + ' horas';
      L.querySelector('#valor-red').textContent = K.coma(this.red, 2) + ' segundos';
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const largo = K.suave((t - 0.9) / 2.2), x = K.mezcla(X0, X1, largo), nace = K.acotar((t - 2.1) / 0.5, 0, 1);

      // el riel y lo que lleva recorrido el método de siempre
      ctx.fillStyle = '#2d2924'; ctx.fillRect(X0, Y - 3, X1 - X0, 6);
      ctx.fillStyle = '#8f8676'; ctx.fillRect(X0, Y - 3, x - X0, 6);
      ctx.font = '450 20px ' + MONO; ctx.textAlign = 'center';
      for (let h = 1; h <= this.horas; h++) {
        const xh = X0 + ((h * 3600) / this.lento) * (X1 - X0);
        if (xh > x) break;
        ctx.fillStyle = '#8f8676'; ctx.fillRect(xh - 1, Y - 12, 2, 24);
        ctx.fillStyle = '#7d7568'; ctx.fillText(h + ' h', xh, Y + 42);
      }
      if (largo >= 1) {
        ctx.textAlign = 'right'; ctx.fillStyle = '#b9b0a1'; ctx.font = '500 26px ' + TEXTO;
        ctx.fillText('El método de siempre: ' + this.total, X1, Y - 26);
      }

      // Krylov, a la misma escala: un punto que late cada vez que termina
      if (nace > 0) {
        const fase = ((t - 2.1) % this.red) / this.red;
        ctx.strokeStyle = 'rgba(226,133,74,' + (0.85 * (1 - fase) * nace) + ')'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(X0, Y, 10 + fase * 40, 0, 6.2832); ctx.stroke();
        ctx.fillStyle = 'rgba(226,133,74,' + nace + ')';
        ctx.beginPath(); ctx.arc(X0, Y, 9, 0, 6.2832); ctx.fill();
        ctx.globalAlpha = nace;
        ctx.textAlign = 'left'; ctx.fillStyle = '#e2854a'; ctx.font = '600 26px ' + TEXTO;
        ctx.fillText('Krylov: a esta escala, ' + (this.pixeles < 1 ? 'menos de un píxel' : K.coma(this.pixeles, 1) + ' píxeles'), X0 + 30, Y - 26);
        ctx.globalAlpha = 1;
      }
    },
  });
})();
