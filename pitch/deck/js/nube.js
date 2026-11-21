/* 6 · Sabe cuando no sabe: todo lo que Krylov practicó, y un archivo que cae lejos.
   Cada punto es un terreno del simulador del motor, puesto según cuántas muestras tenía (datos.js → practica).
   El archivo que no alcanza es el caso `leyes_pocos`; el motivo en pantalla es el que entrega api.analizar.
   La altura de cada punto no significa nada: solo los separa para que se vean. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 990, X1 = 1810, YC = 560, ALTO = 250, YEJE = 850;
  const N0 = 7, N1 = 620;                  // extremos del eje, en muestras (escala logarítmica)
  const F = '"Instrument Sans", sans-serif', MONO = '"JetBrains Mono", monospace';
  const ROJO = [228, 96, 60], VERDE = [31, 168, 122];

  K.registrar('nube', {
    tQuieto: 10,
    crear: function (L) {
      const P = (this.P = K.datos.practica), azar = K.azar(29), yo = this;
      this.cv = L.querySelector('#lienzo-nube');
      this.ctx = this.cv.getContext('2d');
      this.pocas = K.datos.pocos.muestras;                 // 12
      this.todas = K.datos.terreno.puntos.length;          // 340
      this.pts = P.muestras.map(function (n) {
        // dos uniformes sumadas: una nube más densa al centro, sin forma de campana exagerada
        const v = (azar() + azar() - 1) * ALTO, ang = azar() * 6.2832, r = 160 + azar() * 520;
        return { x: yo.px(n + azar()), y: YC + v, d: azar() * 1.9, dx: Math.cos(ang) * r, dy: Math.sin(ang) * r };
      });
      this.s = { forma: 0, cae: 0, mueve: 0, lejos: 0 };
      this.mota = document.createElement('canvas');
      this.mota.width = this.mota.height = 64;
      const g = this.mota.getContext('2d'), grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, 'rgba(226,133,74,0.085)');
      grad.addColorStop(1, 'rgba(226,133,74,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, 64, 64);
      const motivo = L.querySelector('#motivo-pocos');
      if (motivo) motivo.textContent = '«' + K.datos.pocos.semaforo.motivo + '»';
    },
    px: function (n) { return X0 + (Math.log(n / N0) / Math.log(N1 / N0)) * (X1 - X0); },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
      this.cache = null;
    },
    entrar: function () { Object.assign(this.s, { forma: 0, cae: 0, mueve: 0, lejos: 0 }); },
    paso: function (p, inst) {
      const s = this.s;
      if (p === 0) {
        s.cae = 0; s.mueve = 0; s.lejos = 0;
        if (!inst) s.forma = 0;
        K.anim(s, { forma: 1 }, 3.4, inst, 'none');
      } else if (p === 1) {
        K.anim(s, { forma: 1 }, 0.3, inst);
        s.mueve = 0;
        if (!inst) { s.cae = 0; s.lejos = 0; }
        K.anim(s, { cae: 1 }, 1.5, inst, 'bounce.out');
        K.anim(s, { lejos: 1 }, 0.9, inst, 'power2.out', 1.5);
      } else {
        K.anim(s, { forma: 1, cae: 1 }, 0.3, inst);
        K.anim(s, { lejos: 0 }, 0.4, inst);
        if (!inst) s.mueve = 0;
        K.anim(s, { mueve: 1 }, 2.2, inst, 'power2.inOut', 0.5);
      }
    },
    pintarNube: function (ctx, tau) {
      const yo = this;
      ctx.globalCompositeOperation = 'lighter';
      this.pts.forEach(function (p) {
        const k = tau == null ? 1 : K.fuera((tau - p.d) / 1.4);
        if (k <= 0) return;
        const x = p.x + (1 - k) * p.dx, y = p.y + (1 - k) * p.dy;
        ctx.globalAlpha = k;
        ctx.drawImage(yo.mota, x - 22, y - 22, 44, 44);
        ctx.fillStyle = 'rgba(244,224,196,0.58)';
        ctx.fillRect(x - 1.6, y - 1.6, 3.2, 3.2);
      });
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
    },
    // El archivo, dibujado como una hoja con la esquina doblada.
    hoja: function (ctx, x, y, color) {
      const w = 34, h = 44, e = 12;
      ctx.save();
      ctx.translate(x - w / 2, y - h / 2);
      ctx.shadowColor = color; ctx.shadowBlur = 34;
      ctx.fillStyle = color;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(w - e, 0); ctx.lineTo(w, e); ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath(); ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = 'rgba(11,10,9,0.55)';
      ctx.beginPath(); ctx.moveTo(w - e, 0); ctx.lineTo(w, e); ctx.lineTo(w - e, e); ctx.closePath(); ctx.fill();
      ctx.fillRect(6, 18, w - 12, 3); ctx.fillRect(6, 26, w - 12, 3); ctx.fillRect(6, 34, w - 18, 3);
      ctx.restore();
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, s = this.s, P = this.P;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const izq = this.px(P.minimo), der = this.px(P.maximo + 1), arriba = YC - ALTO - 40, listo = K.acotar((s.forma - 0.8) * 5, 0, 1);

      // las dos zonas donde nunca practicó: muy pocas muestras, o demasiadas
      if (listo > 0) {
        ctx.globalAlpha = listo;
        ctx.fillStyle = 'rgba(228,96,60,0.085)';
        ctx.fillRect(X0 - 30, arriba, izq - X0 + 30, YEJE - arriba);
        ctx.fillRect(der, arriba, X1 + 30 - der, YEJE - arriba);
        ctx.globalAlpha = 1;
      }

      // el eje: cuántas muestras trae el banco
      ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(X0 - 30, YEJE); ctx.lineTo(X1 + 30, YEJE); ctx.stroke();
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 25px ' + F; ctx.textAlign = 'center';
      [10, P.minimo, 100, P.maximo].forEach(function (n) {
        const x = this.px(n);
        ctx.beginPath(); ctx.moveTo(x, YEJE); ctx.lineTo(x, YEJE + 12); ctx.stroke();
        ctx.fillText(K.miles(n), x, YEJE + 44);
      }, this);
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO;
      ctx.fillText('MUESTRAS QUE TRAE EL BANCO', (X0 + X1) / 2, YEJE + 86);

      // la nube
      if (s.forma >= 1) {
        if (!this.cache) {
          this.cache = document.createElement('canvas');
          this.cache.width = this.cv.width; this.cache.height = this.cv.height;
          const c = this.cache.getContext('2d');
          c.setTransform(r, 0, 0, r, 0, 0);
          this.pintarNube(c, null);
        }
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.drawImage(this.cache, 0, 0);
        ctx.setTransform(r, 0, 0, r, 0, 0);
      } else {
        this.pintarNube(ctx, s.forma * 3.4);
      }

      if (listo > 0) {
        ctx.globalAlpha = listo;
        ctx.setLineDash([10, 10]); ctx.strokeStyle = '#e4603c'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(izq, arriba); ctx.lineTo(izq, YEJE); ctx.moveTo(der, arriba); ctx.lineTo(der, YEJE); ctx.stroke(); ctx.setLineDash([]);
        ctx.font = '650 27px ' + F;
        ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'center'; ctx.fillText('Todo lo que practicó', (izq + der) / 2, arriba - 22);
        ctx.fillStyle = '#e4603c'; ctx.textAlign = 'right'; ctx.fillText('Nunca practicó', izq - 16, arriba - 22);
        ctx.globalAlpha = 1;
      }

      // el archivo
      if (s.cae > 0) {
        const m = s.mueve, xa = this.px(this.pocas), xb = this.px(this.todas);
        const x = K.mezcla(xa, xb, m), y = YC - (1 - s.cae) * 760 - Math.sin(Math.PI * m) * 150;
        const color = 'rgb(' + ROJO.map(function (v, i) { return Math.round(K.mezcla(v, VERDE[i], m)); }).join(',') + ')';
        if (m > 0) {                                  // de dónde venía
          ctx.setLineDash([6, 9]); ctx.strokeStyle = 'rgba(228,96,60,0.6)'; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.moveTo(xa, YC);
          for (let j = 1; j <= 30; j++) { const q = (m * j) / 30; ctx.lineTo(K.mezcla(xa, xb, q), YC - Math.sin(Math.PI * q) * 150); }
          ctx.stroke(); ctx.setLineDash([]);
        }
        if (s.lejos > 0 && m === 0) {                 // cuánto le falta para parecerse a lo que conoce
          const x0 = xa + 30, x1 = K.mezcla(x0, izq - 6, s.lejos);
          ctx.globalAlpha = s.lejos;
          ctx.strokeStyle = '#e4603c'; ctx.lineWidth = 3;
          ctx.beginPath(); ctx.moveTo(x0, YC); ctx.lineTo(x1, YC); ctx.moveTo(x1, YC - 12); ctx.lineTo(x1, YC + 12); ctx.stroke();
          ctx.globalAlpha = 1;
        }
        const pulso = (t * 0.9) % 1;
        if (s.cae >= 1) {
          ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.globalAlpha = 1 - pulso;
          ctx.beginPath(); ctx.arc(x, y, 30 + pulso * 50, 0, 6.2832); ctx.stroke();
          ctx.globalAlpha = 1;
        }
        this.hoja(ctx, x, y, color);
        const muestras = Math.round(K.mezcla(this.pocas, this.todas, K.suave(m)));
        ctx.font = '700 29px ' + F; ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'center';
        ctx.shadowColor = '#0b0a09'; ctx.shadowBlur = 16;
        ctx.fillText(K.miles(muestras) + ' muestras', x, y - 44);
        ctx.shadowBlur = 0;
      }
    },
  });
})();
