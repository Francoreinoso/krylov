/* 3 · En el pasado vs. hoy: el flujo de trabajo de un data scientist contra el de Bayesian Amortized Inference.
   Una carrera con un solo reloj, el tiempo de cómputo, que corre de 0 a 7 h 25 min:
   - En el pasado, cada dataset repite los tres pasos (elegir el modelo, entrenar con ese dataset, inferir):
     117 s por dataset con el método lento (M-25). En 7 h 25 min salen 228 (M-08, M-10).
   - Hoy, los pasos se hacen una sola vez (elegir el modelo del problema, simular datasets con él, pre-entrenar la red):
     280 minutos (M-02). Después, inferir es un forward pass de 10 ms (latencia_ms del sello).
   Todo sale de motor/artefactos/espacial/sello.json. Lo que cuenta la fila de «Hoy» después de entrenar es una cuenta
   (segundos que quedan ÷ 10 ms), no una corrida. Los tres pasos del pasado se dibujan del mismo ancho: el archivo
   mide el total por dataset, no cuánto toma cada paso. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 110, X1 = 1810, HUECO = 8, A1 = 424, A2 = 408, A3 = 352;      // el ancho de cada paso: el que pide su texto
  const MONO = '"JetBrains Mono", monospace', TEXTO = '"Instrument Sans", sans-serif', TITULO = '"Big Shoulders Display", sans-serif';
  const ELEGIR = '54,194,174', SIMULAR = '238,194,90', ENTRENAR = '226,133,74', INFERIR = '244,239,230';
  const DURA = 8, ESPERA = 6;

  function horas(s) { const min = Math.round(s / 60), h = Math.floor(min / 60), m = min - h * 60; return h + ' h ' + (m < 10 ? '0' : '') + m + ' min'; }

  K.registrar('flujo', {
    tQuieto: 100,
    crear: function (L) {
      const S = K.datos.sello;
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.total = S.amortizacion.mcmc_s;                                  // 26.699 s
      this.porDataset = S.mcmc_s_por_dataset;                              // 117 s
      this.n = Math.round(this.total / this.porDataset);                   // 228
      this.entrena = S.entrenamiento_min * 60;                             // 280 min
      this.ms = S.latencia_ms;                                             // 10 ms
      this.minutos = Math.round(this.porDataset / 60);
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    // un paso del flujo: una caja con su color; «lleno» de 0 a 1 la va pintando de izquierda a derecha
    caja: function (ctx, x, y, ancho, color, texto, lleno, luz) {
      ctx.fillStyle = 'rgba(' + color + ',0.13)'; ctx.fillRect(x, y, ancho, 64);
      if (lleno > 0) { ctx.fillStyle = 'rgba(' + color + ',' + (0.3 + 0.3 * (luz || 0)) + ')'; ctx.fillRect(x, y, ancho * lleno, 64); }
      ctx.fillStyle = 'rgb(' + color + ')'; ctx.fillRect(x, y, 7, 64);
      ctx.fillStyle = '#f4efe6'; ctx.font = '600 27px ' + TEXTO; ctx.textAlign = 'left';
      ctx.fillText(texto, x + 26, y + 41);
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, n = this.n, paso = (X1 - X0) / n;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const ciclo = DURA + ESPERA, u = K.quieto ? DURA + 1 : (((t - 0.9) % ciclo) + ciclo) % ciclo;
      const avance = t < 0.9 && !K.quieto ? 0 : (u > ciclo - 0.7 ? 1 - K.suave((u - (ciclo - 0.7)) / 0.7) : Math.min(1, u / DURA));
      const reloj = avance * this.total, listo = reloj >= this.entrena;
      const desdeListo = listo ? (K.quieto ? 9 : (avance - this.entrena / this.total) * DURA + (avance >= 1 ? u - DURA : 0)) : 0;

      // el reloj que comparten las dos filas
      ctx.textAlign = 'right';
      ctx.fillStyle = '#7d7568'; ctx.font = '500 20px ' + MONO; ctx.fillText('TIEMPO DE CÓMPUTO', X1, 112);
      ctx.fillStyle = '#f4efe6'; ctx.font = '800 92px ' + TITULO; ctx.fillText(horas(reloj), X1, 198);

      // ---------- En el pasado ----------
      let y = 300;
      ctx.textAlign = 'left';
      ctx.fillStyle = '#b9b0a1'; ctx.font = '800 54px ' + TITULO; ctx.fillText('En el pasado', X0, y);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 29px ' + TEXTO; ctx.fillText('un data scientist repite todo el trabajo, con cada dataset', X0 + 290, y - 4);
      const turno = avance >= 1 || avance <= 0 ? -1 : Math.floor((t * 2.6) % 3);                 // la luz que recorre los tres pasos, una y otra vez
      const x2 = X0 + A1 + HUECO, x3 = x2 + A2 + HUECO, xi = x3 + A3 + HUECO + 14;
      this.caja(ctx, X0, y + 30, A1, ELEGIR, 'Elegir el modelo', turno === 0 ? 1 : 0, 1);
      this.caja(ctx, x2, y + 30, A2, ENTRENAR, 'Entrenar con ese dataset', turno === 1 ? 1 : 0, 1);
      this.caja(ctx, x3, y + 30, A3, INFERIR, 'Inferir', turno === 2 ? 1 : 0, 1);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 29px ' + TEXTO;
      ctx.fillText('↻  y de nuevo: ' + this.minutos + ' minutos por dataset', xi + 8, y + 71);
      const hechosA = Math.min(n, reloj / this.porDataset);
      for (let i = 0; i < n; i++) {
        ctx.fillStyle = i < Math.floor(hechosA) ? '#b9b0a1' : '#2d2924';
        ctx.fillRect(X0 + i * paso, y + 126, paso - 1.6, 26);
      }
      ctx.fillStyle = '#b9b0a1'; ctx.font = '800 60px ' + TITULO;
      const cuentaA = K.miles(Math.floor(hechosA));
      ctx.fillText(cuentaA, X0, y + 214);
      const anchoA = ctx.measureText(cuentaA).width;
      ctx.font = '500 29px ' + TEXTO; ctx.fillText('datasets respondidos', X0 + anchoA + 18, y + 210);

      // ---------- Hoy ----------
      y = 626;
      ctx.fillStyle = '#e2854a'; ctx.font = '800 54px ' + TITULO; ctx.fillText('Hoy', X0, y);
      ctx.fillStyle = '#f4efe6'; ctx.font = '500 29px ' + TEXTO; ctx.fillText('Bayesian Amortized Inference: se pre-entrena una vez, para todos los datasets', X0 + 100, y - 4);
      const una = Math.min(1, reloj / this.entrena);
      this.caja(ctx, X0, y + 30, A1, ELEGIR, 'Elegir el modelo del problema', una > 0 ? 1 : 0);
      this.caja(ctx, x2, y + 30, A2, SIMULAR, 'Simular millones de datasets', una);
      this.caja(ctx, x3, y + 30, A3, ENTRENAR, 'Pre-entrenar la red con ellos', una);
      const luz = listo ? 0.4 + 0.6 * Math.exp(-desdeListo * 1.2) : 0;
      this.caja(ctx, xi, y + 30, X1 - xi, INFERIR, 'Inferir: un forward pass', listo ? 1 : 0, luz);
      ctx.font = '500 25px ' + TEXTO;
      ctx.fillStyle = '#b9b0a1'; ctx.fillText('Una sola vez: ' + horas(this.entrena) + '. Lo hace Krylov, antes de que llegue tu dataset.', X0, y + 130);
      ctx.fillStyle = listo ? '#f4efe6' : '#7d7568'; ctx.fillText(this.ms + ' milisegundos por dataset', xi, y + 130);
      const barrido = listo ? K.acotar(desdeListo / 0.4, 0, 1) * n : 0;
      for (let i = 0; i < n; i++) {
        ctx.fillStyle = i < barrido ? '#e2854a' : '#2d2924';
        ctx.fillRect(X0 + i * paso, y + 156, paso - 1.6, 26);
      }
      const hechosB = listo ? Math.floor((reloj - this.entrena) / (this.ms / 1000)) : 0;
      ctx.fillStyle = '#e2854a'; ctx.font = '800 92px ' + TITULO;
      const cuentaB = K.miles(hechosB);
      ctx.fillText(cuentaB, X0, y + 274);
      const anchoB = ctx.measureText(cuentaB).width;
      ctx.fillStyle = '#f4efe6'; ctx.font = '500 29px ' + TEXTO; ctx.fillText('datasets respondidos', X0 + anchoB + 22, y + 268);

      // el remate, cuando el reloj llega al final
      if (avance >= 1) {
        ctx.globalAlpha = K.quieto ? 1 : K.acotar((u - DURA) / 0.6, 0, 1);
        ctx.textAlign = 'left'; ctx.fillStyle = '#f4efe6'; ctx.font = '600 33px ' + TEXTO;
        ctx.fillText('El mismo tiempo de cómputo: ' + K.miles(n) + ' datasets en el pasado. Hoy, ' + (hechosB >= 950000 ? 'casi un millón.' : K.miles(hechosB) + '.'), X0, y + 338);
        ctx.globalAlpha = 1;
      }
    },
  });
})();
