/* 12 · «¿Y cómo sé que acierta?»: dos medidas de accuracy, de 0 a 1, cada una con su dibujo.
   - Las decisiones (arriba): el examen del terreno de `leyes` contra su verdad escondida (nucleo/espacial.examen_de_bloques).
     De las partes donde Krylov decidió («conviene apartar» o «puede ir a la planta»), en cuántas acertó. Un cuadrado por
     decisión. Las partes que dejó «en duda» no cuentan: ahí dijo que no sabía.
   - Los intervalos (abajo): el examen que se toma con cada archivo (nucleo/espacial._examen): esconde 68 muestras, responde
     con las demás y da un intervalo de credibilidad de 90% para cada una. Cada barra es un intervalo; el punto, lo que había.
   Todo viene de datos.js (terreno.examen_bloques y examen_puntos), generado con la red. El terreno es simulado. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 1010, X1 = 1810, MONO = '"JetBrains Mono", monospace', TEXTO = '"Instrument Sans", sans-serif';

  K.registrar('confianza', {
    tQuieto: 12,
    crear: function (L) {
      const C = K.datos.terreno.examen_bloques.colores, E = (this.E = K.datos.examen_puntos), dos = function (x) { return K.coma(x, 2); };
      const buenasA = C.actuar.sobre_el_limite, buenasN = C.no_actuar.bloques - C.no_actuar.sobre_el_limite;
      this.decididas = C.actuar.bloques + C.no_actuar.bloques;
      this.correctas = buenasA + buenasN;
      // qué cuadrados son errores: repartidos al azar (con semilla) dentro de su grupo
      const azar = K.azar(5), malas = {};
      const repartir = function (desde, cuantos, errores) { while (errores > 0) { const i = desde + Math.floor(azar() * cuantos); if (!malas[i]) { malas[i] = 1; errores--; } } };
      repartir(0, C.actuar.bloques, C.actuar.bloques - buenasA);
      repartir(C.actuar.bloques, C.no_actuar.bloques, C.no_actuar.sobre_el_limite);
      this.malas = malas;
      this.cols = 55; this.filas = Math.ceil(this.decididas / this.cols);
      this.pts = E.puntos.slice().sort(function (a, b) { return a[0] - b[0]; });
      let lo = Infinity, hi = 0;
      this.pts.forEach(function (p) { lo = Math.min(lo, p[1], p[3]); hi = Math.max(hi, p[2], p[3]); });
      this.lo = Math.log(lo * 0.85); this.hi = Math.log(hi * 1.12);
      const poner = function (id, v) { L.querySelector(id).innerHTML = v; };
      poner('#conf-decisiones', dos(this.correctas / this.decididas));
      poner('#conf-decisiones-texto', 'Decidió en <span class="nb">' + K.miles(this.decididas) + ' partes</span> del terreno y acertó en <span class="nb">' + K.miles(this.correctas) + '</span>. En las otras <span class="nb">' + C.en_duda.bloques + '</span> dijo «no sabemos».');
      poner('#conf-intervalos', dos(E.dentro / E.n));
      poner('#conf-intervalos-texto', 'Escondimos <span class="nb">' + E.n + ' valores</span>: <span class="nb">' + E.dentro + ' cayeron</span> dentro de su intervalo de credibilidad de 90%.');
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, E = this.E;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);

      // ---- arriba: un cuadrado por decisión ----
      const paso = (X1 - X0) / this.cols, lado = paso - 2.4, y0 = 330, vistos = K.acotar((t - 0.5) / 1.6, 0, 1) * this.decididas;
      for (let i = 0; i < this.decididas && i < vistos; i++) {
        ctx.fillStyle = this.malas[i] ? '#ff7a50' : '#2fbf8f';
        ctx.fillRect(X0 + (i % this.cols) * paso, y0 + Math.floor(i / this.cols) * paso, lado, lado);
      }
      const yPie = y0 + this.filas * paso + 34;
      ctx.font = '500 25px ' + TEXTO; ctx.textAlign = 'left';
      ctx.fillStyle = '#2fbf8f'; ctx.fillRect(X0, yPie - 19, 20, 20); ctx.fillStyle = '#f4efe6'; ctx.fillText('decisión correcta', X0 + 32, yPie);
      ctx.fillStyle = '#ff7a50'; ctx.fillRect(X0 + 280, yPie - 19, 20, 20); ctx.fillStyle = '#f4efe6'; ctx.fillText('decisión equivocada', X0 + 312, yPie);

      // ---- abajo: un intervalo por valor escondido, y lo que de verdad había ----
      const Y0 = 930, Y1 = 660, n = this.pts.length, ancho = (X1 - X0) / n, lo = this.lo, hi = this.hi;
      const Y = function (ppm) { return Y0 - ((Math.log(ppm) - lo) / (hi - lo)) * (Y0 - Y1); };
      const yL = Y(E.limite);
      ctx.strokeStyle = '#f4efe6'; ctx.lineWidth = 2; ctx.setLineDash([10, 8]);
      ctx.beginPath(); ctx.moveTo(X0, yL); ctx.lineTo(X1, yL); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO; ctx.fillText('LÍMITE: ' + K.miles(E.limite) + ' PPM', X0, yL - 12);
      for (let i = 0; i < n; i++) {
        const p = this.pts[i], x = X0 + (i + 0.5) * ancho;
        const crece = K.fuera((t - 2.3 - i * 0.02) / 0.5), cae = K.acotar((t - 4.0 - i * 0.02) / 0.3, 0, 1);
        if (crece <= 0) continue;
        const ye = Y(p[0]), ya = K.mezcla(ye, Y(p[2]), crece), yb = K.mezcla(ye, Y(p[1]), crece), ok = p[3] >= p[1] && p[3] <= p[2];
        ctx.fillStyle = cae > 0 && !ok ? 'rgba(228,96,60,0.55)' : 'rgba(185,176,161,0.42)';
        ctx.fillRect(x - 3, ya, 6, yb - ya);
        if (cae > 0) {
          ctx.globalAlpha = cae;
          ctx.fillStyle = ok ? '#2fbf8f' : '#ff7a50';
          ctx.beginPath(); ctx.arc(x, Y(p[3]), 5.2 + (1 - cae) * 6, 0, 6.2832); ctx.fill();
          ctx.globalAlpha = 1;
        }
      }
      ctx.font = '500 25px ' + TEXTO; ctx.textAlign = 'left';
      ctx.fillStyle = 'rgba(185,176,161,0.6)'; ctx.fillRect(X0 + 7, Y0 + 32, 6, 28); ctx.fillStyle = '#f4efe6'; ctx.fillText('el intervalo que dio', X0 + 32, Y0 + 55);
      ctx.fillStyle = '#2fbf8f'; ctx.beginPath(); ctx.arc(X0 + 300, Y0 + 46, 7, 0, 6.2832); ctx.fill(); ctx.fillStyle = '#f4efe6'; ctx.fillText('lo que había', X0 + 318, Y0 + 55);
    },
  });
})();
