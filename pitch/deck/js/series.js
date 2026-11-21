/* 6 a 9 · Las otras cuatro decisiones de la mina: taludes, flotación, flota y sismicidad.
   Cada lámina dibuja las series del archivo de su caso (datos.js → series), con el mismo estilo:
   - taludes: una cordillera, un sector del muro por línea (lo que midió el radar);
   - flotación y flota: curvas que avanzan hacia su límite (la meta de la planta, la falla del camión);
   - sismicidad: los temblores de cada sector después de la tronadura.
   Si el motor del caso ya responde (series.<caso>.respuesta), cada unidad se pinta con el color de su decisión y la
   leyenda trae cuántas hay de cada una. Mientras no responda, se dibujan los datos, sin decisión. */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 960, X1 = 1810, Y0 = 200, Y1 = 880;
  const F = '"Instrument Sans", sans-serif', MONO = '"JetBrains Mono", monospace';
  const HUESO = '#e9dfcc', COLOR = { actuar: '#e4603c', en_duda: '#eec25a', no_actuar: '#1fa87a' };

  function colorDe(S, id) {
    const u = S.respuesta && S.respuesta.unidades[id];
    return u ? COLOR[u.estado] : HUESO;
  }

  function ejeX(ctx, S, tMax, marcas, sufijo) {
    ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(X0, Y1); ctx.lineTo(X1, Y1); ctx.stroke();
    ctx.fillStyle = '#b9b0a1'; ctx.font = '500 24px ' + F; ctx.textAlign = 'center';
    marcas.forEach(function (m) {
      const x = X0 + (m / tMax) * (X1 - X0);
      ctx.beginPath(); ctx.moveTo(x, Y1); ctx.lineTo(x, Y1 + 10); ctx.stroke();
      ctx.fillText(K.miles(m) + (sufijo || ''), x, Y1 + 42);
    });
    ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO;
    ctx.fillText((S.eje_tiempo || '').toUpperCase(), (X0 + X1) / 2, Y1 + 84);
  }

  function limite(ctx, y, texto) {
    ctx.setLineDash([12, 10]); ctx.strokeStyle = '#e4603c'; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(X0, y); ctx.lineTo(X1, y); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = '#e4603c'; ctx.font = '650 25px ' + F; ctx.textAlign = 'right';
    ctx.fillText(texto, X1, y - 14);
  }

  // ---------- taludes: una línea por sector del muro, apiladas ----------
  function cordillera(ctx, S, k, t) {
    const n = S.unidades.length, tMax = 48 + (S.horizonte || 0), alto = Y1 - Y0 - 60;
    let vMax = 0;
    S.unidades.forEach(function (u) { u.puntos.forEach(function (p) { vMax = Math.max(vMax, p[1]); }); });
    const x = function (tt) { return X0 + (tt / tMax) * (X1 - X0); }, ahora = x(48), corte = X0 + k * (ahora - X0);
    // lo que viene: la ventana sobre la que se decide
    ctx.fillStyle = 'rgba(244,239,230,0.045)'; ctx.fillRect(ahora, Y0 - 20, X1 - ahora, Y1 - Y0 + 20);
    ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO; ctx.textAlign = 'center';
    ctx.fillText('PRÓXIMAS ' + S.horizonte + ' HORAS', (ahora + X1) / 2, Y0 + 6);
    for (let j = n - 1; j >= 0; j--) {                      // de atrás hacia adelante
      const u = S.unidades[j], base = Y1 - 26 - (j / (n - 1)) * alto * 0.72, esc = (alto * 0.62) / vMax, col = colorDe(S, u.id);
      ctx.save();
      ctx.beginPath(); ctx.rect(X0, 0, Math.max(0, corte - X0), 1080); ctx.clip();
      ctx.beginPath(); ctx.moveTo(x(u.puntos[0][0]), base);
      u.puntos.forEach(function (p) { ctx.lineTo(x(p[0]), base - Math.max(p[1], 0) * esc); });
      ctx.lineTo(x(u.puntos[u.puntos.length - 1][0]), base);
      ctx.closePath(); ctx.fillStyle = '#0b0a09'; ctx.fill();
      const relleno = ctx.createLinearGradient(0, base - alto * 0.3, 0, base);
      relleno.addColorStop(0, 'rgba(226,133,74,0.30)'); relleno.addColorStop(1, 'rgba(226,133,74,0)');
      ctx.fillStyle = relleno; ctx.fill();
      ctx.beginPath();
      u.puntos.forEach(function (p, i) { const px = x(p[0]), py = base - Math.max(p[1], 0) * esc; if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py); });
      ctx.strokeStyle = col; ctx.globalAlpha = 0.7 + 0.3 * (1 - j / n); ctx.lineWidth = 2.6; ctx.stroke();
      ctx.restore();
      // la cabeza de cada línea: la última lectura
      const tt = k * 48;
      let ult = u.puntos[0];
      for (let i = 0; i < u.puntos.length && u.puntos[i][0] <= tt; i++) ult = u.puntos[i];
      const late = 0.6 + 0.4 * Math.sin(t * 2.2 + j);
      ctx.fillStyle = col === HUESO ? '#e2854a' : col; ctx.globalAlpha = k > 0 ? late : 0;
      ctx.beginPath(); ctx.arc(x(ult[0]), base - Math.max(ult[1], 0) * esc, 3.4, 0, 6.2832); ctx.fill();
      ctx.globalAlpha = 1;
      // si el motor responde: lo que cree que viene, con su rango
      const r = S.respuesta && S.respuesta.unidades[u.id], c = r && r.curva;
      if (c && c.t_banda && k >= 1) {
        ctx.beginPath();
        c.t_banda.forEach(function (tb, i) { const px = x(tb), py = base - Math.max(c.alto[i], 0) * esc; if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py); });
        for (let i = c.t_banda.length - 1; i >= 0; i--) ctx.lineTo(x(c.t_banda[i]), base - Math.max(c.bajo[i], 0) * esc);
        ctx.closePath(); ctx.fillStyle = col; ctx.globalAlpha = 0.16; ctx.fill(); ctx.globalAlpha = 1;
      }
    }
    ctx.strokeStyle = '#f4efe6'; ctx.lineWidth = 2; ctx.globalAlpha = 0.8;
    ctx.beginPath(); ctx.moveTo(ahora, Y0 - 20); ctx.lineTo(ahora, Y1); ctx.stroke(); ctx.globalAlpha = 1;
    ejeX(ctx, S, tMax, [0, 12, 24, 36, 48], '');
    ctx.fillStyle = '#f4efe6'; ctx.font = '650 24px ' + F; ctx.textAlign = 'center'; ctx.fillText('ahora', ahora, Y0 - 34);
  }

  // ---------- flotación y flota: curvas que avanzan hacia su límite ----------
  function curvas(ctx, S, k, t, o) {
    let tDato = 0, vMax = 0;
    S.unidades.forEach(function (u) { u.puntos.forEach(function (p) { tDato = Math.max(tDato, p[0]); vMax = Math.max(vMax, p[1]); }); });
    const tMax = tDato * o.margen, tope = Math.max(vMax, S.umbral || 0) * 1.12;
    const x = function (tt) { return X0 + (tt / tMax) * (X1 - X0); }, y = function (v) { return Y1 - (Math.max(v, 0) / tope) * (Y1 - Y0); };
    if (o.margen > 1.3) {                                   // lo que falta: lo que el archivo todavía no trae
      ctx.fillStyle = 'rgba(244,239,230,0.045)'; ctx.fillRect(x(tDato), Y0 - 20, X1 - x(tDato), Y1 - Y0 + 20);
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO; ctx.textAlign = 'center';
      ctx.fillText(o.falta, (x(tDato) + X1) / 2, Y1 - 24);
    }
    if (S.umbral != null) limite(ctx, y(S.umbral), o.limite);
    const corte = X0 + k * (x(tDato) - X0) + 4;
    S.unidades.forEach(function (u, j) {
      const col = colorDe(S, u.id);
      ctx.save();
      ctx.beginPath(); ctx.rect(X0 - 10, 0, Math.max(0, corte - X0 + 10), 1080); ctx.clip();
      ctx.beginPath(); ctx.moveTo(x(0), y(0));
      u.puntos.forEach(function (p) { ctx.lineTo(x(p[0]), y(p[1])); });
      ctx.strokeStyle = col; ctx.globalAlpha = o.alfa; ctx.lineWidth = o.grosor; ctx.lineJoin = 'round'; ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = col;
      if (o.puntos) u.puntos.forEach(function (p) { ctx.beginPath(); ctx.arc(x(p[0]), y(p[1]), 5, 0, 6.2832); ctx.fill(); });
      ctx.restore();
      const ult = u.puntos[u.puntos.length - 1], visto = x(ult[0]) <= corte;
      if (visto) {
        const late = 0.65 + 0.35 * Math.sin(t * 2.4 + j * 1.7);
        ctx.fillStyle = col === HUESO ? '#e2854a' : col; ctx.globalAlpha = late;
        ctx.beginPath(); ctx.arc(x(ult[0]), y(ult[1]), o.puntos ? 8 : 4.5, 0, 6.2832); ctx.fill(); ctx.globalAlpha = 1;
      }
      const r = S.respuesta && S.respuesta.unidades[u.id], c = r && r.curva;
      if (c && c.t_banda && k >= 1) {                       // si el motor responde: lo que cree que viene
        ctx.beginPath();
        c.t_banda.forEach(function (tb, i) { if (i) ctx.lineTo(x(tb), y(c.alto[i])); else ctx.moveTo(x(tb), y(c.alto[i])); });
        for (let i = c.t_banda.length - 1; i >= 0; i--) ctx.lineTo(x(c.t_banda[i]), y(c.bajo[i]));
        ctx.closePath(); ctx.fillStyle = col; ctx.globalAlpha = 0.14; ctx.fill(); ctx.globalAlpha = 1;
      }
    });
    ejeX(ctx, S, tMax, o.marcas, '');
  }

  // ---------- sismicidad: los temblores de cada sector después de la tronadura ----------
  function pulsos(ctx, S, k, t) {
    const n = S.unidades.length, tMax = 6 + (S.horizonte || 0), fila = (Y1 - Y0 - 20) / n;
    let vMin = 9, vMax = -9;
    S.unidades.forEach(function (u) { u.puntos.forEach(function (p) { vMin = Math.min(vMin, p[1]); vMax = Math.max(vMax, p[1]); }); });
    const x = function (tt) { return X0 + 110 + (tt / tMax) * (X1 - X0 - 110); }, ahora = x(6), corte = x(0) + k * (ahora - x(0));
    ctx.fillStyle = 'rgba(244,239,230,0.045)'; ctx.fillRect(ahora, Y0 - 20, X1 - ahora, Y1 - Y0 + 20);
    ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO; ctx.textAlign = 'center';
    ctx.fillText('PRÓXIMAS ' + S.horizonte + ' HORAS', (ahora + X1) / 2, Y0 + 6);
    S.unidades.forEach(function (u, j) {
      const base = Y0 + 30 + (j + 0.82) * fila, col = colorDe(S, u.id);
      ctx.strokeStyle = '#2d2924'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x(0), base); ctx.lineTo(X1, base); ctx.stroke();
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 23px ' + F; ctx.textAlign = 'left'; ctx.fillText(u.id, X0, base - 6);
      u.puntos.forEach(function (p) {
        const px = x(p[0]);
        if (px > corte) return;
        const m = (p[1] - vMin) / (vMax - vMin), h = 10 + m * (fila - 20), fuerte = S.umbral != null && p[1] >= S.umbral;
        const nuevo = 1 - K.acotar((corte - px) / 60, 0, 1);
        ctx.strokeStyle = fuerte ? '#e4603c' : col; ctx.globalAlpha = fuerte ? 1 : 0.6 + 0.4 * m; ctx.lineWidth = fuerte ? 5 : 3;
        ctx.beginPath(); ctx.moveTo(px, base); ctx.lineTo(px, base - h); ctx.stroke();
        ctx.fillStyle = fuerte ? '#e4603c' : col;
        ctx.beginPath(); ctx.arc(px, base - h, (fuerte ? 8 : 4) + nuevo * 5, 0, 6.2832); ctx.fill();
        if (fuerte) {
          const onda = (t * 0.8 + px * 0.01) % 1;
          ctx.globalAlpha = 1 - onda; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(px, base - h, 8 + onda * 26, 0, 6.2832); ctx.stroke();
        }
        ctx.globalAlpha = 1;
      });
    });
    ctx.strokeStyle = '#f4efe6'; ctx.lineWidth = 2; ctx.globalAlpha = 0.8;
    ctx.beginPath(); ctx.moveTo(ahora, Y0 - 20); ctx.lineTo(ahora, Y1); ctx.stroke(); ctx.globalAlpha = 1;
    ctx.fillStyle = '#f4efe6'; ctx.font = '650 24px ' + F; ctx.textAlign = 'center'; ctx.fillText('ahora', ahora, Y0 - 34);
    // el eje, en horas desde la tronadura
    ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x(0), Y1); ctx.lineTo(X1, Y1); ctx.stroke();
    ctx.fillStyle = '#b9b0a1'; ctx.font = '500 24px ' + F;
    [0, 2, 4, 6].forEach(function (m) { ctx.beginPath(); ctx.moveTo(x(m), Y1); ctx.lineTo(x(m), Y1 + 10); ctx.stroke(); ctx.fillText(m, x(m), Y1 + 42); });
    ctx.fillStyle = '#7d7568'; ctx.font = '450 19px ' + MONO; ctx.fillText((S.eje_tiempo || '').toUpperCase(), (x(0) + X1) / 2, Y1 + 84);
  }

  const DIBUJOS = {
    taludes: function (ctx, S, k, t) { cordillera(ctx, S, k, t); },
    flotacion: function (ctx, S, k, t) {
      curvas(ctx, S, k, t, { margen: 2.0, marcas: [0, 10, 20, 30], limite: 'La meta: ' + Math.round(S.umbral * 100) + '% del cobre', falta: 'LO QUE FALTA DE LA LÍNEA', alfa: 0.95, grosor: 3.4, puntos: true });
    },
    flota: function (ctx, S, k, t) {
      curvas(ctx, S, k, t, { margen: 1.12, marcas: [0, 500, 1000, 1500, 2000, 2500], limite: 'Falla', falta: '', alfa: 0.8, grosor: 2.6, puntos: false });
    },
    sismicidad: function (ctx, S, k, t) { pulsos(ctx, S, k, t); },
  };

  Object.keys(DIBUJOS).forEach(function (caso) {
    K.registrar(caso, {
      tQuieto: 6,
      crear: function (L) {
        const S = (this.S = K.datos.series[caso]);
        this.cv = L.querySelector('canvas');
        this.ctx = this.cv.getContext('2d');
        this.s = { traza: 0 };
        // la leyenda: las tres respuestas posibles y, si el motor ya responde, cuántas unidades hay en cada una
        ['actuar', 'en_duda', 'no_actuar'].forEach(function (e) {
          const texto = L.querySelector('[data-rotulo="' + e + '"]'), num = L.querySelector('[data-cuenta="' + e + '"]');
          if (texto) texto.textContent = S.rotulos[e];
          if (num) num.textContent = S.respuesta ? S.respuesta.colores[e] : '';
        });
        const cuantas = L.querySelector('.cuantas .num');
        if (cuantas) cuantas.textContent = S.unidades.length;
        const cuesta = L.querySelector('.cuesta');
        if (cuesta && S.respuesta && S.respuesta.costo_de_no_saber != null) {
          cuesta.querySelector('.monto').textContent = K.miles(S.respuesta.costo_de_no_saber);
          cuesta.hidden = false;
        }
      },
      alAjustar: function () {
        const r = (this.r = K.razon(1.5));
        this.cv.width = Math.round(1920 * r);
        this.cv.height = Math.round(1080 * r);
      },
      entrar: function () { this.s.traza = 0; },
      paso: function (p, inst) { K.anim(this.s, { traza: 1 }, 3.4, inst, 'power1.inOut', 0.3); },
      cuadro: function (t) {
        const ctx = this.ctx, r = this.r;
        ctx.setTransform(r, 0, 0, r, 0, 0);
        ctx.clearRect(0, 0, 1920, 1080);
        DIBUJOS[caso](ctx, this.S, this.s.traza, t);
      },
    });
  });
})();
