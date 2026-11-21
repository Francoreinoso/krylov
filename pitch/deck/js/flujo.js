/* 3 · En el pasado vs. hoy: el flujo de trabajo de un data scientist contra el de Bayesian Amortized Inference.
   Dos pasos, para que se mire una cosa a la vez:
   - Paso 0, «En el pasado»: tres pasos que se repiten con cada dataset (elegir el modelo, entrenar con ese dataset,
     inferir). Cada vuelta responde un dataset. Con el método lento son 117 s por dataset (M-25): «2 minutos cada uno».
   - Paso 1, «Hoy»: los tres primeros pasos se hacen una sola vez (elegir el modelo, simular datasets, pre-entrenar la
     red) y después inferir es un forward pass de 10 ms (latencia_ms del sello) por dataset.
   Los dos tiempos por dataset son mediciones del sello del motor espacial. Los contadores cuentan lo que la animación
   muestra (una vuelta, un dataset; un pulso, un dataset): dan la forma del trabajo, no son una medición.
   El ancho de cada caja es el de su texto, así ningún texto se sale de su caja. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 110, ALTO = 84, HUECO = 10;
  const TEXTO = '"Instrument Sans", sans-serif', TITULO = '"Big Shoulders Display", sans-serif';
  const ELEGIR = '54,194,174', SIMULAR = '238,194,90', ENTRENAR = '226,133,74', INFERIR = '244,239,230';
  const VUELTA = 2.4, PULSO = 0.05;                    // en pantalla: segundos por dataset en el pasado, y por dataset hoy

  K.registrar('flujo', {
    tQuieto: 30,
    crear: function (L) {
      const S = K.datos.sello;
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.minutos = Math.round(S.mcmc_s_por_dataset / 60);
      this.ms = S.latencia_ms;
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    entrar: function () { this.etapa = 0; this.t1 = 1e9; },
    paso: function (p, inst) {                           // el segundo paso muestra «Hoy»
      if (p >= 1 && this.etapa < 1) this.t1 = inst ? -100 : K.t - this._t0;
      this.etapa = p;
    },
    // una caja del flujo: su ancho sale de su texto. «lleno» (0 a 1) la pinta de izquierda a derecha
    caja: function (ctx, x, y, color, texto, lleno) {
      ctx.font = '600 31px ' + TEXTO;
      const ancho = Math.ceil(ctx.measureText(texto).width) + 64;
      ctx.fillStyle = 'rgba(' + color + ',0.12)'; ctx.fillRect(x, y, ancho, ALTO);
      if (lleno > 0) { ctx.fillStyle = 'rgba(' + color + ',0.42)'; ctx.fillRect(x, y, ancho * Math.min(1, lleno), ALTO); }
      ctx.fillStyle = 'rgb(' + color + ')'; ctx.fillRect(x, y, 8, ALTO);
      ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'left'; ctx.fillText(texto, x + 34, y + ALTO / 2 + 11);
      return x + ancho + HUECO;
    },
    cuenta: function (ctx, x, y, n, color, texto) {
      ctx.textAlign = 'left'; ctx.fillStyle = color; ctx.font = '800 120px ' + TITULO;
      const s = K.miles(n);
      ctx.fillText(s, x, y);
      const ancho = ctx.measureText(s).width;
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 34px ' + TEXTO; ctx.fillText(texto, x + ancho + 26, y - 8);
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const hoy = this.etapa >= 1;

      // ---------- En el pasado: la vuelta completa, con cada dataset ----------
      let y = 330;
      ctx.globalAlpha = hoy ? 0.45 : 1;
      ctx.textAlign = 'left'; ctx.fillStyle = '#b9b0a1'; ctx.font = '800 64px ' + TITULO; ctx.fillText('En el pasado', X0, y);
      const u = K.quieto ? 2.5 : Math.max(0, t - 0.6) / VUELTA, vuelta = Math.floor(u), f = (u - vuelta) * 3;       // en qué caja va
      let x = X0;
      x = this.caja(ctx, x, y + 34, ELEGIR, 'Elegir el modelo', f);
      x = this.caja(ctx, x, y + 34, ENTRENAR, 'Entrenar con ese dataset', f - 1);
      x = this.caja(ctx, x, y + 34, INFERIR, 'Inferir', f - 2);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 34px ' + TEXTO; ctx.fillText('↻  con cada dataset', x + 16, y + 34 + ALTO / 2 + 12);
      this.cuenta(ctx, X0, y + 250, vuelta, '#b9b0a1', 'datasets respondidos · ' + this.minutos + ' minutos cada uno');
      ctx.globalAlpha = 1;
      if (!hoy) return;

      // ---------- Hoy: se pre-entrena una vez; después, cada dataset es un instante ----------
      y = 700;
      const v = K.quieto ? 9 : t - this.t1, una = K.suave(v / 2.6), listo = v > 2.9;
      ctx.globalAlpha = K.acotar(v / 0.5, 0, 1);
      ctx.fillStyle = '#e2854a'; ctx.font = '800 64px ' + TITULO; ctx.fillText('Hoy', X0, y);
      x = X0;
      x = this.caja(ctx, x, y + 34, ELEGIR, 'Elegir el modelo', una * 3);
      x = this.caja(ctx, x, y + 34, SIMULAR, 'Simular datasets', una * 3 - 1);
      x = this.caja(ctx, x, y + 34, ENTRENAR, 'Pre-entrenar la red', una * 3 - 2);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 34px ' + TEXTO; ctx.textAlign = 'left';
      const nota = 'una sola vez', xi = x + 16;
      ctx.fillText(nota, xi, y + 34 + ALTO / 2 + 12);
      const pulsos = listo ? Math.floor((v - 2.9) / PULSO) : 0, late = listo ? 0.55 + 0.45 * Math.abs(Math.sin(v * 31)) : 0;
      this.caja(ctx, xi + ctx.measureText(nota).width + 40, y + 34, INFERIR, 'Inferir: un forward pass', late);
      this.cuenta(ctx, X0, y + 250, pulsos, '#e2854a', 'datasets respondidos · ' + this.ms + ' milisegundos cada uno');
      ctx.globalAlpha = 1;
    },
  });
})();
