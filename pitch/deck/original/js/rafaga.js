/* 5 · Bayesian Amortized Inference: entra un archivo, sale la respuesta; y otro, y otro.
   Cada tarjeta que entra es un banco distinto y cada mapa que sale es lo que la red respondió para ese banco
   (datos.js → rafaga, generado con nucleo/espacial.inferir). El deck anima esas respuestas; no las calcula. */
(function () {
  'use strict';
  const K = window.K;
  const M = 96;                                        // píxeles de cada mapa
  const CARRIL = 856, NUCLEO = 500, VITRINA = 760;     // la fila por donde pasan: y, x del núcleo, x donde se muestra el mapa
  const COLS = 6, FILAS = 6, PASO = 133, LADO = 120, MX = 1016, MY = 138, CASILLAS = COLS * FILAS;
  const RITMO = 0.27;                                  // segundos entre un banco y el siguiente
  const MONO = '"JetBrains Mono", monospace';

  function subir(src, base, L) {
    const s = new Float32Array(M * M);
    for (let y = 0; y < M; y++) {
      const fy = K.acotar(((y + 0.5) / M) * L - 0.5, 0, L - 1), y0 = Math.floor(fy), y1 = Math.min(L - 1, y0 + 1), ty = fy - y0;
      for (let x = 0; x < M; x++) {
        const fx = K.acotar(((x + 0.5) / M) * L - 0.5, 0, L - 1), x0 = Math.floor(fx), x1 = Math.min(L - 1, x0 + 1), tx = fx - x0;
        s[y * M + x] = (src[base + y0 * L + x0] * (1 - tx) + src[base + y0 * L + x1] * tx) * (1 - ty) + (src[base + y1 * L + x0] * (1 - tx) + src[base + y1 * L + x1] * tx) * ty;
      }
    }
    return s;
  }

  // Un mapa de decisiones (con sus curvas de nivel) y la tarjeta de datos de la que salió.
  function preparar() {
    const R = K.datos.rafaga, L = R.lado, media = K.b64(R.media), p = K.b64(R.p), bits = K.b64(R.muestras), salida = [];
    const limite = ((R.limite + 2.5) / 5) * 255;
    for (let k = 0; k < R.n; k++) {
      const m = subir(media, k * L * L, L), q = subir(p, k * L * L, L);
      const mapa = document.createElement('canvas'), datos = document.createElement('canvas');
      mapa.width = mapa.height = datos.width = datos.height = M;
      const c = mapa.getContext('2d'), img = c.createImageData(M, M);
      for (let y = 0; y < M; y++) {
        for (let x = 0; x < M; x++) {
          const i = y * M + x, o = ((M - 1 - y) * M + x) * 4, pr = q[i] / 255, v = m[i];
          let col = pr >= 0.9 ? [228, 96, 60] : (pr <= 0.1 ? [31, 168, 122] : ((x + y) % 6 < 3 ? [150, 116, 44] : [238, 194, 90]));
          const der = m[Math.min(M - 1, x + 1) + y * M], arr = m[x + Math.min(M - 1, y + 1) * M];
          if (Math.floor(v / 20) !== Math.floor(der / 20) || Math.floor(v / 20) !== Math.floor(arr / 20)) col = col.map(function (z) { return z * 0.62; });
          if ((v - limite) * (der - limite) < 0 || (v - limite) * (arr - limite) < 0) col = [255, 255, 255];
          img.data[o] = col[0]; img.data[o + 1] = col[1]; img.data[o + 2] = col[2]; img.data[o + 3] = 255;
        }
      }
      c.putImageData(img, 0, 0);
      const d = datos.getContext('2d');
      d.fillStyle = '#17140f'; d.fillRect(0, 0, M, M);
      d.fillStyle = '#f4e8d4';
      for (let i = 0; i < L * L; i++) {
        if (!((bits[k * (L * L / 8) + (i >> 3)] >> (7 - (i & 7))) & 1)) continue;
        d.fillRect(((i % L) + 0.5) * (M / L) - 1, (L - 1 - Math.floor(i / L) + 0.5) * (M / L) - 1, 2.2, 2.2);
      }
      salida.push({ mapa: mapa, datos: datos });
    }
    return salida;
  }

  // Los mismos mapas sirven al cierre: se preparan una sola vez.
  let listos = null;
  K.mapasRafaga = function () { return listos || (listos = preparar()); };

  K.registrar('rafaga', {
    tQuieto: 14,
    crear: function (L) {
      this.cv = L.querySelector('#lienzo-rafaga');
      this.ctx = this.cv.getContext('2d');
      this.bancos = K.mapasRafaga();
      this.contador = L.querySelector('#rafaga-n');
      this.lento = L.querySelector('#rafaga-lento');
      this.riel = L.querySelector('#rafaga-riel');
      this.segundosLento = K.datos.sello.mcmc_s_por_dataset;       // 117 s por análisis (M-25)
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    casilla: function (i) {
      const k = i % CASILLAS;
      return { x: MX + (k % COLS) * PASO + LADO / 2, y: MY + Math.floor(k / COLS) * PASO + LADO / 2 };
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, n = this.bancos.length;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const ultimo = Math.floor(t / RITMO), respondidos = Math.max(0, Math.floor((t - 0.36) / RITMO) + 1);

      // el carril y el núcleo
      ctx.strokeStyle = '#2d2924'; ctx.lineWidth = 2; ctx.setLineDash([4, 10]);
      ctx.beginPath(); ctx.moveTo(0, CARRIL); ctx.lineTo(VITRINA + 110, CARRIL); ctx.stroke(); ctx.setLineDash([]);
      const pulso = 1 - K.acotar((((t - 0.3) % RITMO) + RITMO) % RITMO / RITMO, 0, 1);
      for (let a = 0; a < 3; a++) {
        ctx.strokeStyle = 'rgba(226,133,74,' + (0.9 - a * 0.26) + ')'; ctx.lineWidth = 3 - a * 0.7;
        ctx.beginPath(); ctx.arc(NUCLEO, CARRIL, 34 + a * 17 + pulso * 7, t * (1.2 - a * 0.5) + a, t * (1.2 - a * 0.5) + a + 4.4); ctx.stroke();
      }
      ctx.fillStyle = 'rgba(226,133,74,' + (0.22 + 0.5 * pulso) + ')';
      ctx.beginPath(); ctx.arc(NUCLEO, CARRIL, 24, 0, 6.2832); ctx.fill();
      ctx.fillStyle = '#7d7568'; ctx.font = '500 18px ' + MONO; ctx.textAlign = 'center';
      ctx.fillText('BAYESIAN AMORTIZED INFERENCE', NUCLEO, CARRIL + 120);

      // la muralla de mapas ya respondidos (los más nuevos tapan a los más viejos)
      for (let i = Math.max(0, ultimo - CASILLAS - 6); i <= ultimo; i++) {
        const edad = t - i * RITMO, b = this.bancos[i % n], c = this.casilla(i);
        if (edad < 0) continue;
        if (edad < 0.32) {                                   // el archivo entra
          const k = K.suave(edad / 0.32), x = K.mezcla(-110, NUCLEO, k), lado = K.mezcla(150, 50, k * k);
          ctx.globalAlpha = 1 - k * k * k * 0.9;
          ctx.drawImage(b.datos, x - lado / 2, CARRIL - lado / 2, lado, lado);
          ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 1.5; ctx.strokeRect(x - lado / 2, CARRIL - lado / 2, lado, lado);
          ctx.globalAlpha = 1;
        } else if (edad < 0.62) {                            // sale la respuesta
          const k = K.fuera((edad - 0.32) / 0.3), x = K.mezcla(NUCLEO, VITRINA, k), lado = K.mezcla(40, 200, k);
          ctx.drawImage(b.mapa, x - lado / 2, CARRIL - lado / 2, lado, lado);
        } else {                                             // y se va a su lugar
          // primero avanza por el carril y después sube a su casilla: no pasa por encima del texto
          const k = K.suave((edad - 0.62) / 0.46), x = K.mezcla(VITRINA, c.x, K.fuera(k * 1.7)), y = K.mezcla(CARRIL, c.y, k * k * k), lado = K.mezcla(200, LADO, k);
          ctx.drawImage(b.mapa, x - lado / 2, y - lado / 2, lado, lado);
          const brillo = 1 - K.acotar((edad - 1.04) / 0.5, 0, 1);
          if (k >= 1 && brillo > 0) { ctx.strokeStyle = 'rgba(255,240,210,' + brillo + ')'; ctx.lineWidth = 3; ctx.strokeRect(x - lado / 2, y - lado / 2, lado, lado); }
        }
      }

      K.cifra(this.contador, K.miles(respondidos));
      const avance = K.acotar(t / this.segundosLento, 0, 1);
      K.cifra(this.lento, avance >= 1 ? '1' : '0');
      this.riel.style.width = avance * 100 + '%';
    },
  });
})();
