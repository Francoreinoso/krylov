/* 8 · Negocio: una plataforma y sus 1.000 empresas. Cada punto es una empresa: ilustración (no son clientes). */
(function () {
  'use strict';
  const K = window.K;
  const CX = 1470, CY = 610, R = 280, HX = 1470, HY = 212, N = 1000;

  K.registrar('negocio', {
    tQuieto: 12,
    crear: function (L) {
      this.cv = L.querySelector('#lienzo-negocio');
      this.ctx = this.cv.getContext('2d');
      const azar = K.azar(1000);
      this.pts = [];
      for (let i = 0; i < N; i++) {
        const r = R * Math.sqrt((i + 0.5) / N), a = i * 2.39996323;
        this.pts.push({ x: CX + Math.cos(a) * r, y: CY + Math.sin(a) * r * 0.86, k: i / N, fase: azar() * 6.28, tono: azar() });
      }
      this.s = { luz: 0, ola: 0 };
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    entrar: function () { this.s.luz = 0; this.s.ola = 0; },
    paso: function (p, inst) {
      if (p === 0) { if (!inst) this.s.luz = 0; K.anim(this.s, { luz: 1 }, 3.6, inst, 'power1.inOut', 0.4); }
      else { K.anim(this.s, { luz: 1 }, 0.4, inst); this.s.ola = 0; K.anim(this.s, { ola: 1 }, 2.2, inst, 'power1.out'); }
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, s = this.s, F = '"Archivo Variable", sans-serif';
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);

      // de la plataforma a sus empresas
      const abanico = ctx.createLinearGradient(0, HY, 0, CY);
      abanico.addColorStop(0, 'rgba(139,139,245,' + 0.30 * s.luz + ')');
      abanico.addColorStop(1, 'rgba(139,139,245,0)');
      ctx.fillStyle = abanico;
      ctx.beginPath(); ctx.moveTo(HX - 12, HY + 34); ctx.lineTo(HX + 12, HY + 34); ctx.lineTo(CX + R, CY); ctx.lineTo(CX - R, CY); ctx.closePath(); ctx.fill();

      const frente = s.luz * 1.15;
      for (let i = 0; i < N; i++) {
        const p = this.pts[i], k = K.acotar((frente - p.k) / 0.12, 0, 1);
        const late = 0.78 + 0.22 * Math.sin(t * 1.7 + p.fase);
        const ola = Math.exp(-Math.pow((s.ola * 1.3 - p.k) / 0.07, 2)) * (s.ola < 1 ? 1 : 0);
        if (k <= 0) { ctx.fillStyle = '#2a2c48'; ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, 6.2832); ctx.fill(); continue; }
        const a = p.tono, rr = Math.round(K.mezcla(133, 240, a)), gg = Math.round(K.mezcla(133, 153, a)), bb = Math.round(K.mezcla(247, 92, a));
        ctx.globalAlpha = (0.35 + 0.65 * k) * late;
        ctx.fillStyle = 'rgb(' + rr + ',' + gg + ',' + bb + ')';
        ctx.beginPath(); ctx.arc(p.x, p.y, 3 + 1.6 * k + 3.5 * ola, 0, 6.2832); ctx.fill();
      }
      ctx.globalAlpha = 1;

      // la plataforma
      const w = 300, h = 68;
      ctx.fillStyle = '#0f1020'; ctx.strokeStyle = '#8b8bf5'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.roundRect(HX - w / 2, HY - h / 2, w, h, 34); ctx.fill(); ctx.stroke();
      ctx.fillStyle = '#f5f5fa'; ctx.font = '700 31px ' + F; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('Una plataforma', HX, HY + 2);
      ctx.fillStyle = '#a9abc4'; ctx.font = '600 27px ' + F;
      ctx.fillText('1.000 empresas cliente', CX, CY + R * 0.86 + 46);
      ctx.fillStyle = '#6d6f8a'; ctx.font = '500 24px ' + F;
      ctx.fillText('Ilustración: cada punto es una empresa', CX, CY + R * 0.86 + 84);
      ctx.textBaseline = 'alphabetic';
    },
  });
})();
