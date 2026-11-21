/* 12 · «¿Y cómo sé que acierta?»: un número de 0 a 1, y el rango a la vista.
   A la derecha, el examen que Krylov se toma con el archivo de `leyes` (nucleo/espacial._examen): esconde 68 muestras,
   responde con las otras 272 y dice, para cada escondida, entre qué valores puede estar (rango de 90%). Cada barra es
   ese rango; el punto es lo que de verdad había. Lo calcula generar.py con la red (datos.js → examen_puntos).
   A la izquierda, tres veces la misma pregunta («cuando dio un rango, ¿la respuesta cayó adentro?»):
   con este archivo, en los 2.000 casos de validación del sello, y con datos reales públicos (sello: examen_5_particiones). */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 1040, X1 = 1810, Y0 = 860, Y1 = 200;
  const MONO = '"JetBrains Mono", monospace', TEXTO = '"Instrument Sans", sans-serif';

  K.registrar('confianza', {
    tQuieto: 9,
    crear: function (L) {
      const E = (this.E = K.datos.examen_puntos), S = K.datos.sello, R = S.examen_5_particiones;
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.pts = E.puntos.slice().sort(function (a, b) { return a[0] - b[0]; });
      let lo = Infinity, hi = 0;
      this.pts.forEach(function (p) { lo = Math.min(lo, p[1], p[3]); hi = Math.max(hi, p[2], p[3]); });
      this.lo = Math.log(lo * 0.85); this.hi = Math.log(hi * 1.12);
      const dos = function (x) { return K.coma(x, 2); };
      L.querySelector('#conf-numero').textContent = dos(S.cobertura_90);
      const filas = [
        [dos(E.dentro / E.n), 'Con este archivo: escondimos <span class="nb">' + E.n + ' muestras</span> y <span class="nb">' + E.dentro + ' cayeron</span> dentro de su rango.'],
        [dos(S.cobertura_90), 'En <span class="nb">' + K.miles(S.casos_validacion) + ' casos</span> nuevos, que nunca había visto.'],
      ];
      if (R) filas.push([dos(R.dentro_del_rango_de_90 / R.mediciones_escondidas), 'Con datos reales públicos: <span class="nb">' + R.dentro_del_rango_de_90 + ' de ' + R.mediciones_escondidas + '</span> mediciones escondidas.']);
      L.querySelector('#conf-filas').innerHTML = filas.map(function (f) { return '<div class="fila"><span class="num">' + f[0] + '</span><span>' + f[1] + '</span></div>'; }).join('');
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    y: function (ppm) { return Y0 - ((Math.log(ppm) - this.lo) / (this.hi - this.lo)) * (Y0 - Y1); },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, E = this.E, n = this.pts.length, paso = (X1 - X0) / n;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      // el eje: partes por millón, en escala de multiplicar
      ctx.font = '450 19px ' + MONO; ctx.textAlign = 'right';
      [100, 200, 500, 1000, 2000].forEach(function (v) {
        const y = this.y(v);
        if (y < Y1 - 10 || y > Y0 + 10) return;
        ctx.fillStyle = '#2d2924'; ctx.fillRect(X0, y, X1 - X0, 1.5);
        ctx.fillStyle = '#7d7568'; ctx.fillText(K.miles(v), X0 - 16, y + 6);
      }, this);
      ctx.textAlign = 'left'; ctx.fillStyle = '#7d7568'; ctx.fillText(E.unidad.toUpperCase(), X0, Y1 - 26);
      // el límite con que se decide
      const yL = this.y(E.limite);
      ctx.strokeStyle = '#f4efe6'; ctx.lineWidth = 2; ctx.setLineDash([10, 8]);
      ctx.beginPath(); ctx.moveTo(X0, yL); ctx.lineTo(X1, yL); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = '#f4efe6'; ctx.font = '600 22px ' + TEXTO; ctx.textAlign = 'left';
      ctx.fillText('límite: ' + K.miles(E.limite) + ' ppm', X0 + 6, yL - 12);                 // a la izquierda, donde las barras quedan por debajo

      let adentro = 0, afuera = 0;
      for (let i = 0; i < n; i++) {
        const p = this.pts[i], x = X0 + (i + 0.5) * paso;
        const crece = K.fuera((t - 0.4 - i * 0.022) / 0.5), cae = K.acotar((t - 2.1 - i * 0.02) / 0.3, 0, 1);
        if (crece <= 0) continue;
        const ye = this.y(p[0]), ya = K.mezcla(ye, this.y(p[2]), crece), yb = K.mezcla(ye, this.y(p[1]), crece), ok = p[3] >= p[1] && p[3] <= p[2];
        ctx.fillStyle = cae > 0 && !ok ? 'rgba(228,96,60,0.55)' : 'rgba(185,176,161,0.42)';
        ctx.fillRect(x - 3, ya, 6, yb - ya);                                 // el rango que dio
        ctx.fillStyle = '#b9b0a1'; ctx.fillRect(x - 5, ye - 1, 10, 2);       // su estimación
        if (cae > 0) {                                                       // lo que de verdad había
          if (ok) adentro++; else afuera++;
          ctx.globalAlpha = cae;
          ctx.fillStyle = ok ? '#36c2ae' : '#ff7a50';
          ctx.beginPath(); ctx.arc(x, this.y(p[3]), 5.2 + (1 - cae) * 6, 0, 6.2832); ctx.fill();
          ctx.globalAlpha = 1;
        }
      }
      // la leyenda, que cuenta mientras caen los puntos
      ctx.textAlign = 'left'; ctx.font = '500 25px ' + TEXTO;
      ctx.fillStyle = 'rgba(185,176,161,0.6)'; ctx.fillRect(X0, Y0 + 46, 6, 28);
      ctx.fillStyle = '#b9b0a1'; ctx.fillText('el rango que dio Krylov', X0 + 18, Y0 + 69);
      ctx.fillStyle = '#36c2ae'; ctx.beginPath(); ctx.arc(X0 + 334, Y0 + 60, 6, 0, 6.2832); ctx.fill();
      ctx.fillStyle = '#f4efe6'; ctx.fillText('lo que había: ' + adentro + ' adentro', X0 + 350, Y0 + 69);
      ctx.fillStyle = '#ff7a50'; ctx.beginPath(); ctx.arc(X0 + 640, Y0 + 60, 6, 0, 6.2832); ctx.fill();
      ctx.fillStyle = '#f4efe6'; ctx.fillText(afuera + ' afuera', X0 + 656, Y0 + 69);
    },
  });
})();
