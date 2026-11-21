/* 1 · El valor, a primera vista: dos filas iguales, «En el pasado» y «Hoy», cada una con su cifra y su barra.
   Las dos cifras salen del sello del motor espacial (M-08, M-09, M-10): los mismos 228 análisis completos tardan
   26.699 s con el método lento (228 × 117 s) y 0,69 s con la red.
   Las dos barras comparten escala. La de arriba tiene un tramo por análisis: 228 tramos de 2 minutos.
   La de abajo, a esa escala, mide menos de un píxel; por eso es un punto, que late una vez cada 0,69 segundos. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 110, X1 = 1810, YA = 560, YB = 968;
  const TEXTO = '"Instrument Sans", sans-serif';

  K.registrar('valor', {
    tQuieto: 9,
    crear: function (L) {
      const S = K.datos.sello, A = S.amortizacion;
      this.lento = A.mcmc_s;
      this.red = A.red_s;
      this.n = Math.round(A.mcmc_s / S.mcmc_s_por_dataset);               // 228 análisis
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      const h = Math.floor(this.lento / 3600), min = Math.round((this.lento - h * 3600) / 60);
      this.total = h + ' h ' + min + ' min';
      this.pixeles = (this.red / this.lento) * (X1 - X0);                 // lo que mediría Krylov en la barra de arriba
      L.querySelector('#valor-lento').textContent = h + ' horas';
      L.querySelector('#valor-red').textContent = K.coma(this.red, 2) + ' segundos';
      L.querySelectorAll('.valor-n').forEach(function (el) { el.textContent = this.n; }, this);
      L.querySelector('#valor-cada').textContent = Math.round(S.mcmc_s_por_dataset / 60) + ' minutos';
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, n = this.n, paso = (X1 - X0) / n;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);

      // En el pasado: un tramo por análisis, uno tras otro
      const hechos = K.acotar((t - 0.8) / 3.0, 0, 1) * n;
      for (let i = 0; i < n; i++) {
        const lleno = K.acotar(hechos - i, 0, 1);
        ctx.fillStyle = lleno > 0 ? 'rgba(185,176,161,' + (0.35 + 0.65 * lleno) + ')' : '#2d2924';
        ctx.fillRect(X0 + i * paso, YA - 9, paso - 1.6, 18);
      }
      if (hechos >= n) {
        ctx.textAlign = 'right'; ctx.fillStyle = '#b9b0a1'; ctx.font = '600 30px ' + TEXTO;
        ctx.fillText(this.total, X1, YA - 28);
      }

      // Hoy: la misma escala. Krylov es un punto que late cada vez que termina los mismos análisis.
      const nace = K.acotar((t - 1.9) / 0.5, 0, 1);
      ctx.textAlign = 'left'; ctx.font = '600 30px ' + TEXTO;
      const rotulo = 'A la misma escala: ' + (this.pixeles < 1 ? 'menos de un píxel' : K.coma(this.pixeles, 1) + ' píxeles');
      const ancho = ctx.measureText(rotulo).width;
      ctx.globalAlpha = nace;
      ctx.fillStyle = '#2d2924'; ctx.fillRect(X0 + 44 + ancho + 24, YB - 2, X1 - (X0 + 44 + ancho + 24), 4);
      ctx.fillStyle = '#e2854a'; ctx.fillText(rotulo, X0 + 44, YB + 10);
      ctx.globalAlpha = 1;
      if (nace > 0) {
        const fase = ((t - 1.9) % this.red) / this.red;
        ctx.strokeStyle = 'rgba(226,133,74,' + (0.85 * (1 - fase) * nace) + ')'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(X0 + 12, YB, 12 + fase * 26, 0, 6.2832); ctx.stroke();
        ctx.fillStyle = 'rgba(226,133,74,' + nace + ')';
        ctx.beginPath(); ctx.arc(X0 + 12, YB, 11, 0, 6.2832); ctx.fill();
      }
    },
  });
})();
