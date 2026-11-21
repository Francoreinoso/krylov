/* 2 · El cambio de paradigma: no es una red que predice, es Generative AI para datasets.
   Dos filas con la misma forma, que se mueven a la vez: arriba un LLM (entra texto, sale texto); abajo Krylov
   (entra un dataset, sale la decisión con su incertidumbre). Ninguno de los dos se vuelve a entrenar para responder.
   Los datasets y los mapas de la fila de Krylov son los de la lámina de la ráfaga: la respuesta de la red para
   32 bancos distintos (datos.js → rafaga). El texto del LLM son barras, a propósito: no se inventa ninguna conversación. */
(function () {
  'use strict';
  const K = window.K;
  const XE = 1070, XN = 1405, XS = 1700;               // entrada, núcleo, salida
  const FILAS = [{ y: 318 }, { y: 742 }];
  const CICLO = 3.4;
  const MONO = '"JetBrains Mono", monospace', TEXTO = '"Instrument Sans", sans-serif', TITULO = '"Big Shoulders Display", sans-serif';

  K.registrar('paradigma', {
    tQuieto: 2.6,
    crear: function (L) {
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.bancos = K.mapasRafaga();
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    // una tarjeta de texto: renglones que se escriben de izquierda a derecha
    texto: function (ctx, x, y, lado, renglones, semilla, avance) {
      const azar = K.azar(semilla);
      ctx.fillStyle = '#17140f'; ctx.fillRect(x - lado / 2, y - lado / 2, lado, lado);
      ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 1.5; ctx.strokeRect(x - lado / 2, y - lado / 2, lado, lado);
      const alto = (lado - 44) / renglones;
      for (let i = 0; i < renglones; i++) {
        const largo = (0.45 + 0.55 * azar()) * (lado - 48) * (i === renglones - 1 ? 0.6 : 1);
        const k = K.acotar(avance * renglones - i, 0, 1);
        if (k <= 0) break;
        ctx.fillStyle = '#d9cfbd';
        ctx.fillRect(x - lado / 2 + 24, y - lado / 2 + 26 + i * alto, largo * k, Math.min(9, alto * 0.42));
      }
    },
    nucleo: function (ctx, x, y, t, color, pulso) {
      for (let a = 0; a < 3; a++) {
        ctx.strokeStyle = 'rgba(' + color + ',' + (0.9 - a * 0.26) + ')'; ctx.lineWidth = 3 - a * 0.7;
        ctx.beginPath(); ctx.arc(x, y, 30 + a * 15 + pulso * 7, t * (1.2 - a * 0.5) + a, t * (1.2 - a * 0.5) + a + 4.4); ctx.stroke();
      }
      ctx.fillStyle = 'rgba(' + color + ',' + (0.2 + 0.55 * pulso) + ')';
      ctx.beginPath(); ctx.arc(x, y, 21, 0, 6.2832); ctx.fill();
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const k = Math.floor(t / CICLO), u = t - k * CICLO, b = this.bancos[k % this.bancos.length];
      const escribe = K.acotar(u / 0.8, 0, 1), viaja = K.suave((u - 0.8) / 0.45), sale = K.fuera((u - 1.3) / 0.45);
      const pulso = Math.exp(-Math.pow((u - 1.28) / 0.22, 2));
      const fin = K.quieto ? 1 : 1 - K.acotar((u - (CICLO - 0.35)) / 0.35, 0, 1);

      for (let f = 0; f < 2; f++) {
        const y = FILAS[f].y, krylov = f === 1, color = krylov ? '226,133,74' : '217,207,189';
        // el carril
        ctx.strokeStyle = '#2d2924'; ctx.lineWidth = 2; ctx.setLineDash([4, 10]);
        ctx.beginPath(); ctx.moveTo(XE + 110, y); ctx.lineTo(XS - 120, y); ctx.stroke(); ctx.setLineDash([]);
        // lo que entra
        ctx.globalAlpha = fin;
        if (krylov) {
          ctx.globalAlpha = fin * K.acotar(escribe * 2, 0, 1);
          ctx.drawImage(b.datos, XE - 100, y - 100, 200, 200);
          ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 1.5; ctx.strokeRect(XE - 100, y - 100, 200, 200);
        } else this.texto(ctx, XE, y, 200, 4, 11 + k, escribe);
        // viaja al núcleo
        if (viaja > 0 && viaja < 1) {
          const x = K.mezcla(XE, XN, viaja), lado = K.mezcla(120, 34, viaja);
          ctx.globalAlpha = 0.9 * (1 - viaja * viaja);
          if (krylov) ctx.drawImage(b.datos, x - lado / 2, y - lado / 2, lado, lado);
          else { ctx.fillStyle = '#d9cfbd'; ctx.fillRect(x - lado / 2, y - 4, lado, 8); }
        }
        ctx.globalAlpha = 1;
        this.nucleo(ctx, XN, y, t, color, pulso);
        // lo que sale
        if (sale > 0) {
          const x = K.mezcla(XN, XS, sale), lado = K.mezcla(40, 220, sale);
          ctx.globalAlpha = fin;
          if (krylov) {
            ctx.drawImage(b.mapa, x - lado / 2, y - lado / 2, lado, lado);
            const brillo = 1 - K.acotar((u - 1.75) / 0.5, 0, 1);
            if (sale >= 1 && brillo > 0 && !K.quieto) { ctx.strokeStyle = 'rgba(255,240,210,' + brillo + ')'; ctx.lineWidth = 3; ctx.strokeRect(x - lado / 2, y - lado / 2, lado, lado); }
          } else this.texto(ctx, x, y, lado, 7, 301 + k, K.acotar((u - 1.5) / 1.1, 0, 1));
          ctx.globalAlpha = 1;
        }
        // quién es cada fila, y qué entra y qué sale
        ctx.textAlign = 'left';
        ctx.fillStyle = krylov ? '#e2854a' : '#b9b0a1'; ctx.font = '800 54px ' + TITULO;
        ctx.fillText(krylov ? 'Krylov' : 'Un LLM', XE - 100, y - 132);
        const ancho = ctx.measureText(krylov ? 'Krylov' : 'Un LLM').width;
        ctx.fillStyle = '#7d7568'; ctx.font = '500 20px ' + MONO;
        ctx.fillText(krylov ? 'DATASET  →  DECISIÓN, CON SU INCERTIDUMBRE' : 'TEXTO  →  TEXTO', XE - 100 + ancho + 26, y - 138);
        ctx.textAlign = 'center'; ctx.font = '500 18px ' + MONO;
        ctx.fillText(krylov ? 'RED YA ENTRENADA' : 'MODELO YA ENTRENADO', XN, y + 104);
        ctx.textAlign = 'left'; ctx.fillStyle = krylov ? '#f4efe6' : '#b9b0a1'; ctx.font = '500 29px ' + TEXTO;
        ctx.fillText(krylov ? 'Ninguna mina entrena un modelo para su dataset.' : 'Nadie lo entrena para hacerle una pregunta.', XE - 100, y + 158);
      }
    },
  });
})();
