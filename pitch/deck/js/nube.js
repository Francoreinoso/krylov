/* 6 · Sabe cuando no sabe: la nube de empresas simuladas y el archivo que cae afuera.
   Puntos y posiciones: api.nube("rotacion_malo") y la misma con la corrección (datos.js → nube). */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 960, X1 = 1790, Y0 = 250, Y1 = 880;
  const LIMITE_X = 0.912;       // M-29: hasta ahí llegan las 5.000 empresas simuladas (nucleo/nube.py, x_maximo)

  K.registrar('nube', {
    tQuieto: 10,
    crear: function (L) {
      const N = (this.N = K.datos.nube), azar = K.azar(29);
      this.cv = L.querySelector('#lienzo-nube');
      this.ctx = this.cv.getContext('2d');
      let maxX = 0, maxY = 0;
      this.pts = N.puntos.map(function (p) {
        maxX = Math.max(maxX, p[0]); maxY = Math.max(maxY, p[1]);
        const ang = azar() * 6.2832, r = 160 + azar() * 520;
        return { x: p[0], y: p[1], d: azar() * 1.9, dx: Math.cos(ang) * r, dy: Math.sin(ang) * r };
      });
      this.maxX = maxX;
      this.topeY = Math.min(1, Math.ceil(maxY * 10) / 10);
      this.s = { forma: 0, cae: 0, mueve: 0 };
      this.mota = document.createElement('canvas');
      this.mota.width = this.mota.height = 64;
      const g = this.mota.getContext('2d'), grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, 'rgba(120,118,255,0.10)');
      grad.addColorStop(1, 'rgba(120,118,255,0)');
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
    entrar: function () { Object.assign(this.s, { forma: 0, cae: 0, mueve: 0 }); },
    paso: function (p, inst) {
      const s = this.s;
      if (p === 0) {
        s.cae = 0; s.mueve = 0;
        if (!inst) s.forma = 0;
        K.anim(s, { forma: 1 }, 3.4, inst, 'none');
      } else if (p === 1) {
        K.anim(s, { forma: 1 }, 0.3, inst);
        s.mueve = 0;
        if (!inst) s.cae = 0;
        K.anim(s, { cae: 1 }, 1.5, inst, 'bounce.out');
      } else {
        K.anim(s, { forma: 1, cae: 1 }, 0.3, inst);
        if (!inst) s.mueve = 0;
        K.anim(s, { mueve: 1 }, 2.0, inst, 'power2.inOut', 0.35);
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
        ctx.fillStyle = 'rgba(160,160,255,0.62)';
        ctx.fillRect(x - 1.6, y - 1.6, 3.2, 3.2);
      });
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, s = this.s, N = this.N, F = '"Archivo Variable", sans-serif';
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);

      // ejes
      ctx.strokeStyle = '#34365a'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(X0, Y0 - 20); ctx.lineTo(X0, Y1); ctx.lineTo(X1 + 20, Y1); ctx.stroke();
      ctx.fillStyle = '#a9abc4'; ctx.font = '600 26px ' + F; ctx.textAlign = 'center';
      ctx.fillText(N.ejes.x.nombre, (X0 + X1) / 2, Y1 + 84);
      ctx.fillStyle = '#6d6f8a'; ctx.font = '500 24px ' + F;
      ctx.textAlign = 'left'; ctx.fillText('no adivina nada', X0, Y1 + 40);
      ctx.textAlign = 'right'; ctx.fillText('adivina siempre', X1, Y1 + 40);
      ctx.fillText(Math.round(this.topeY * 100) + '%', X0 - 16, Y0 + 8);
      ctx.fillText('0%', X0 - 16, Y1 + 8);
      ctx.save(); ctx.translate(X0 - 46, (Y0 + Y1) / 2); ctx.rotate(-Math.PI / 2);
      ctx.fillStyle = '#a9abc4'; ctx.font = '600 26px ' + F; ctx.textAlign = 'center'; ctx.fillText(N.ejes.y.nombre, 0, 0); ctx.restore();

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

      // hasta dónde llegan las simulaciones
      const borde = this.px(LIMITE_X), aBorde = K.acotar((s.forma - 0.8) * 5, 0, 1);
      if (aBorde > 0) {
        ctx.globalAlpha = aBorde;
        ctx.setLineDash([10, 10]); ctx.strokeStyle = '#8b8bf5'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(borde, Y0 - 10); ctx.lineTo(borde, Y1); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(240,96,95,0.07)'; ctx.fillRect(borde, Y0 - 10, X1 + 20 - borde, Y1 - Y0 + 10);
        ctx.fillStyle = '#8b8bf5'; ctx.font = '650 24px ' + F; ctx.textAlign = 'right';
        ctx.fillText('lo que Krylov simuló', borde - 14, Y0 - 22);
        ctx.fillStyle = '#f0605f'; ctx.textAlign = 'left';
        ctx.fillText('afuera', borde + 12, Y0 - 22);
        ctx.globalAlpha = 1;
      }

      // el archivo
      if (s.cae > 0) {
        const m = s.mueve, xa = this.px(N.malo.x), xb = this.px(N.corregido.x), yF = this.py(N.malo.y);
        const x = K.mezcla(xa, xb, m), y = yF - (1 - s.cae) * 760 - Math.sin(Math.PI * m) * 110;
        const rojo = [240, 96, 95], verde = [56, 196, 135];
        const c = rojo.map(function (v, i) { return Math.round(K.mezcla(v, verde[i], m)); });
        const color = 'rgb(' + c.join(',') + ')';
        if (m > 0) {                                  // de dónde venía
          ctx.setLineDash([6, 9]); ctx.strokeStyle = 'rgba(240,96,95,0.55)'; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.arc(xa, yF, 17, 0, 6.2832); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(xa, yF);
          for (let j = 1; j <= 24; j++) { const q = (m * j) / 24; ctx.lineTo(K.mezcla(xa, xb, q), yF - Math.sin(Math.PI * q) * 110); }
          ctx.stroke(); ctx.setLineDash([]);
        }
        const pulso = (t * 0.9) % 1;
        if (s.cae >= 1) {
          ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.globalAlpha = 1 - pulso;
          ctx.beginPath(); ctx.arc(x, y, 18 + pulso * 46, 0, 6.2832); ctx.stroke();
          ctx.globalAlpha = 1;
        }
        ctx.shadowColor = color; ctx.shadowBlur = 40;
        ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, 15, 0, 6.2832); ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x, y, 5.5, 0, 6.2832); ctx.fill();
        ctx.font = '700 30px ' + F;
        const izq = m <= 0.5, ancho = ctx.measureText('tu archivo').width + 28, ex = izq ? x - 30 - ancho : x + 30;
        ctx.fillStyle = 'rgba(8,9,18,0.86)'; ctx.beginPath(); ctx.roundRect(ex, y - 62, ancho, 44, 12); ctx.fill();
        ctx.fillStyle = '#f5f5fa'; ctx.textAlign = 'left'; ctx.fillText('tu archivo', ex + 14, y - 30);
      }
    },
  });
})();
