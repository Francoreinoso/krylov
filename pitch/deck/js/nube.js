/* 6 · Sabe cuando no sabe: todo lo que Krylov practicó, y un archivo que cae lejos.
   Puntos y posiciones: api.nube("rotacion_malo") y la misma con la corrección (datos.js → nube). */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 990, X1 = 1800, Y0 = 250, Y1 = 850;
  const LIMITE_X = 0.912;       // M-29: hasta ahí llegan las 5.000 simulaciones (nucleo/nube.py, x_maximo)
  const F = '"Instrument Sans", sans-serif', MONO = '"JetBrains Mono", monospace';

  K.registrar('nube', {
    tQuieto: 10,
    crear: function (L) {
      const N = (this.N = K.datos.nube), azar = K.azar(29);
      this.cv = L.querySelector('#lienzo-nube');
      this.ctx = this.cv.getContext('2d');
      let maxY = 0;
      this.pts = N.puntos.map(function (p) {
        maxY = Math.max(maxY, p[1]);
        const ang = azar() * 6.2832, r = 160 + azar() * 520;
        return { x: p[0], y: p[1], d: azar() * 1.9, dx: Math.cos(ang) * r, dy: Math.sin(ang) * r };
      });
      this.topeY = Math.min(1, Math.ceil(maxY * 10) / 10);
      this.s = { forma: 0, cae: 0, mueve: 0, lejos: 0 };
      this.mota = document.createElement('canvas');
      this.mota.width = this.mota.height = 64;
      const g = this.mota.getContext('2d'), grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, 'rgba(226,133,74,0.085)');
      grad.addColorStop(1, 'rgba(226,133,74,0)');
      g.fillStyle = grad;
      g.fillRect(0, 0, 64, 64);
    },
    px: function (x) { return X0 + ((x - this.N.ejes.x.min) / (this.N.ejes.x.max - this.N.ejes.x.min)) * (X1 - X0); },
    py: function (y) { return Y1 - (y / this.topeY) * (Y1 - Y0); },
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
        const x = yo.px(p.x) + (1 - k) * p.dx, y = yo.py(p.y) + (1 - k) * p.dy;
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
      const ctx = this.ctx, r = this.r, s = this.s, N = this.N;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const borde = this.px(LIMITE_X), listo = K.acotar((s.forma - 0.8) * 5, 0, 1);

      // la zona donde nunca practicó
      if (listo > 0) {
        ctx.globalAlpha = listo;
        ctx.fillStyle = 'rgba(228,96,60,0.085)';
        ctx.fillRect(borde, Y0 - 10, X1 + 24 - borde, Y1 - Y0 + 10);
        ctx.globalAlpha = 1;
      }

      // ejes, en palabras
      ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(X0, Y0 - 20); ctx.lineTo(X0, Y1); ctx.lineTo(X1 + 24, Y1); ctx.stroke();
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 25px ' + F;
      ctx.textAlign = 'left'; ctx.fillText('Ninguna columna adivina la respuesta', X0, Y1 + 44);
      ctx.textAlign = 'right'; ctx.fillText('Una la adivina siempre', X1 + 24, Y1 + 44);
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO;
      ctx.save(); ctx.translate(X0 - 26, (Y0 + Y1) / 2); ctx.rotate(-Math.PI / 2);
      ctx.textAlign = 'center'; ctx.fillText(N.ejes.y.nombre.toUpperCase(), 0, 0); ctx.restore();

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
        ctx.beginPath(); ctx.moveTo(borde, Y0 - 10); ctx.lineTo(borde, Y1); ctx.stroke(); ctx.setLineDash([]);
        ctx.font = '650 27px ' + F;
        ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'right'; ctx.fillText('Todo lo que practicó', borde - 18, Y0 - 28);
        ctx.fillStyle = '#e4603c'; ctx.textAlign = 'left'; ctx.fillText('Nunca practicó', borde + 16, Y0 - 28);
        ctx.globalAlpha = 1;
      }

      // el archivo
      if (s.cae > 0) {
        const m = s.mueve, xa = this.px(N.malo.x) - 22, xb = this.px(N.corregido.x), yF = this.py(N.malo.y);
        const x = K.mezcla(xa, xb, m), y = yF - (1 - s.cae) * 760 - Math.sin(Math.PI * m) * 120;
        const rojo = [228, 96, 60], verde = [54, 194, 174];
        const color = 'rgb(' + rojo.map(function (v, i) { return Math.round(K.mezcla(v, verde[i], m)); }).join(',') + ')';
        if (m > 0) {                                  // de dónde venía
          ctx.setLineDash([6, 9]); ctx.strokeStyle = 'rgba(228,96,60,0.6)'; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.moveTo(xa, yF);
          for (let j = 1; j <= 30; j++) { const q = (m * j) / 30; ctx.lineTo(K.mezcla(xa, xb, q), yF - Math.sin(Math.PI * q) * 120); }
          ctx.stroke(); ctx.setLineDash([]);
        }
        if (s.lejos > 0 && m === 0) {                 // qué tan lejos cae de lo que conoce
          const x0 = borde + 6, x1 = K.mezcla(x0, xa - 30, s.lejos);
          ctx.globalAlpha = s.lejos;
          ctx.strokeStyle = '#e4603c'; ctx.lineWidth = 3;
          ctx.beginPath(); ctx.moveTo(x0, yF); ctx.lineTo(x1, yF); ctx.moveTo(x0, yF - 12); ctx.lineTo(x0, yF + 12); ctx.moveTo(x1, yF - 12); ctx.lineTo(x1, yF + 12); ctx.stroke();
          ctx.fillStyle = '#e4603c'; ctx.font = '500 19px ' + MONO; ctx.textAlign = 'center';
          ctx.fillText('LEJOS', (x0 + x1) / 2, yF + 38);
          ctx.globalAlpha = 1;
        }
        const pulso = (t * 0.9) % 1;
        if (s.cae >= 1) {
          ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.globalAlpha = 1 - pulso;
          ctx.beginPath(); ctx.arc(x, y, 30 + pulso * 50, 0, 6.2832); ctx.stroke();
          ctx.globalAlpha = 1;
        }
        this.hoja(ctx, x, y, color);
        ctx.font = '700 29px ' + F; ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'center';
        ctx.shadowColor = '#0b0a09'; ctx.shadowBlur = 14;
        ctx.fillText('Tu archivo', x - (m < 0.5 ? 40 : 0), y - 44);
        ctx.shadowBlur = 0;
      }
    },
  });
})();
