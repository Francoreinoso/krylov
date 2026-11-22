/* 3 · Antes y hoy: el trabajo de modelar un dataset, contra el de Bayesian Amortized Inference. Dos carriles.
   - Paso 0, «Antes»: cada dataset de la fila pasa por las tres cajas (elegir el modelo, entrenar, inferir) y recién
     entonces sale su respuesta. La vuelta se repite con cada dataset.
   - Paso 1, «Hoy»: las cajas del carril de arriba bajan y cambian de lugar. Elegir, simular y pre-entrenar quedan a un lado
     y se llenan una sola vez; «inferir» se encoge hasta ser la red ya entrenada, y los datasets la cruzan de corrido.
   La lámina no lleva tiempos: muestra la forma del trabajo. Los contadores cuentan lo que la animación muestra
   (una vuelta, un dataset; un pulso, un dataset): no son una medición. Los datasets y los mapas son los 32 bancos
   de la lámina 5 (datos.js → rafaga). */
(function () {
  'use strict';
  const K = window.K;
  const X0 = 110, XA = 250, ALTO = 96, HUECO = 12;
  const YA = 372, YB1 = 628, YB2 = 868, XC = 800, XG = 950;        // carril de antes; cajas de «una sola vez»; carril de hoy; la red; la grilla
  const TEXTO = '"Instrument Sans", sans-serif', TITULO = '"Big Shoulders Display", sans-serif';
  const ELEGIR = '54,194,174', SIMULAR = '238,194,90', ENTRENAR = '226,133,74', INFERIR = '244,239,230';
  const VUELTA = 2.4, PULSO = 0.05;                    // en pantalla: segundos por dataset antes, y por dataset hoy
  const LLEGA = 1.0, UNA = 2.4, LISTO = LLEGA + UNA + 0.5;
  const expo = function (t) { return 1 - Math.pow(1 - K.acotar(t, 0, 1), 4); };

  K.registrar('flujo', {
    tQuieto: 30,
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
    entrar: function () { this.etapa = 0; this.t1 = 1e9; },
    paso: function (p, inst) {                           // el segundo paso muestra «Hoy»
      if (p >= 1 && this.etapa < 1) this.t1 = inst ? -100 : K.t - this._t0;
      if (p < 1) this.t1 = 1e9;
      this.etapa = p;
    },
    ancho: function (ctx, texto, hueco) { ctx.font = '600 36px ' + TEXTO; return Math.ceil(ctx.measureText(texto).width) + 48 + (hueco || 0); },
    // una caja del flujo. «lleno» (0 a 1) la pinta de izquierda a derecha
    caja: function (ctx, x, y, w, color, texto, lleno, alfa) {
      const a = ctx.globalAlpha;
      ctx.globalAlpha = a * (alfa == null ? 1 : alfa);
      ctx.fillStyle = '#0b0a09'; ctx.fillRect(x, y, w, ALTO);
      ctx.fillStyle = 'rgba(' + color + ',0.13)'; ctx.fillRect(x, y, w, ALTO);
      if (lleno > 0) { ctx.fillStyle = 'rgba(' + color + ',0.42)'; ctx.fillRect(x, y, w * Math.min(1, lleno), ALTO); }
      ctx.strokeStyle = 'rgba(' + color + ',0.9)'; ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, w - 2, ALTO - 2);
      ctx.font = '600 36px ' + TEXTO; ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'left'; ctx.fillText(texto, x + 24, y + ALTO / 2 + 13);
      ctx.globalAlpha = a;
    },
    // la fila de datasets que esperan: una pila de tarjetas; la de arriba es la que sigue
    pila: function (ctx, x, y, desde, sale) {
      const n = this.bancos.length;
      for (let i = 3; i >= 0; i--) {
        const b = this.bancos[(desde + i) % n], d = i - sale, lado = 88;
        if (d < 0) continue;
        ctx.globalAlpha *= 1 - 0.2 * d;
        ctx.drawImage(b.datos, x + d * 9, y - lado / 2 - d * 7, lado, lado);
        ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 1.5; ctx.strokeRect(x + d * 9, y - lado / 2 - d * 7, lado, lado);
        ctx.globalAlpha /= 1 - 0.2 * d;
      }
    },
    cuenta: function (ctx, x, y, n, color) {
      ctx.textAlign = 'left'; ctx.fillStyle = color; ctx.font = '800 136px ' + TITULO;
      ctx.fillText(K.miles(n), x, y);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 32px ' + TEXTO; ctx.fillText(n === 1 ? 'respondido' : 'respondidos', x + 2, y + 46);
    },
    nucleo: function (ctx, x, y, t, vivo) {
      for (let a = 0; a < 3; a++) {
        ctx.strokeStyle = 'rgba(226,133,74,' + (0.25 + 0.65 * vivo - a * 0.2 * vivo) + ')'; ctx.lineWidth = 3 - a * 0.7;
        ctx.beginPath(); ctx.arc(x, y, 26 + a * 14, t * (1.2 - a * 0.5) * (0.2 + vivo) + a, t * (1.2 - a * 0.5) * (0.2 + vivo) + a + 4.4); ctx.stroke();
      }
      ctx.fillStyle = 'rgba(226,133,74,' + (0.15 + 0.6 * vivo) + ')';
      ctx.beginPath(); ctx.arc(x, y, 18, 0, 6.2832); ctx.fill();
    },
    cuadro: function (t) {
      const ctx = this.ctx, r = this.r, n = this.bancos.length, hoy = this.etapa >= 1;
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      const v = K.quieto ? (hoy ? 30 : -1) : t - this.t1, baja = hoy ? K.suave(v / 0.6) : 0;

      // ---------- Antes: la vuelta completa, con cada dataset ----------
      const cajasA = [['Elegir modelo', ELEGIR], ['Entrenar', ENTRENAR], ['Inferir', INFERIR]], xa = [], wa = [];
      let x = XA;
      cajasA.forEach(function (c, i) { wa[i] = this.ancho(ctx, c[0], 64); xa[i] = x; x += wa[i] + HUECO; }, this);
      const finA = x - HUECO;
      const u = K.quieto ? 2.55 : Math.max(0, t - 0.6) / VUELTA, vuelta = Math.floor(u), f = (u - vuelta) * 3, enCaja = Math.min(2, Math.floor(f));
      ctx.globalAlpha = 1 - 0.5 * baja;
      ctx.textAlign = 'left'; ctx.fillStyle = '#b9b0a1'; ctx.font = '800 64px ' + TITULO; ctx.fillText('Antes', X0, YA - 30);
      this.pila(ctx, X0, YA + ALTO / 2, vuelta + 1, 0);
      cajasA.forEach(function (c, i) { this.caja(ctx, xa[i], YA, wa[i], c[1], c[0], f - i); }, this);
      // el dataset que se está trabajando va dentro de la caja en que está
      const b = this.bancos[vuelta % n], entra = K.suave((f - enCaja) / 0.18);
      const desdeX = enCaja === 0 ? X0 + 12 : xa[enCaja - 1] + wa[enCaja - 1] - 70, hastaX = xa[enCaja] + wa[enCaja] - 70;
      ctx.drawImage(b.datos, K.mezcla(desdeX, hastaX, entra), YA + 20, 56, 56);
      // la vuelta atrás: con cada dataset, todo de nuevo
      const yv = YA + ALTO + 24, xv0 = xa[0] + 30, xv1 = finA - 30;
      ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 2; ctx.setLineDash([6, 8]); ctx.lineDashOffset = K.quieto ? 0 : t * 26;
      ctx.beginPath(); ctx.moveTo(xv1, YA + ALTO + 6); ctx.lineTo(xv1, yv); ctx.lineTo(xv0, yv); ctx.lineTo(xv0, YA + ALTO + 10); ctx.stroke();
      ctx.setLineDash([]); ctx.lineDashOffset = 0;
      ctx.fillStyle = '#7d7568'; ctx.beginPath(); ctx.moveTo(xv0, YA + ALTO + 4); ctx.lineTo(xv0 - 8, YA + ALTO + 16); ctx.lineTo(xv0 + 8, YA + ALTO + 16); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 32px ' + TEXTO; ctx.textAlign = 'center'; ctx.fillText('todo de nuevo, con cada dataset', (xv0 + xv1) / 2, yv + 42);
      // lo respondido: un mapa por vuelta
      const XS = finA + 44, porFila = 5;
      for (let i = Math.max(0, vuelta - 10); i < vuelta; i++) {
        const k = i - Math.max(0, vuelta - 10), sx = XS + (k % porFila) * 70, sy = YA - 22 + Math.floor(k / porFila) * 70;
        const nace = i === vuelta - 1 && !K.quieto ? expo(((u - vuelta) * VUELTA) / 0.45) : 1;
        ctx.drawImage(this.bancos[i % n].mapa, K.mezcla(xa[2] + wa[2] - 70, sx, nace), K.mezcla(YA + 20, sy, nace), K.mezcla(56, 64, nace), K.mezcla(56, 64, nace));
      }
      this.cuenta(ctx, 1560, YA + ALTO + 4, vuelta, '#b9b0a1');
      ctx.globalAlpha = 1;
      if (!hoy) return;

      // ---------- Hoy: lo caro se hace una sola vez; después, cada dataset cruza la red ----------
      const cajasB = [['Elegir modelo', ELEGIR], ['Simular datasets', SIMULAR], ['Pre-entrenar la red', ENTRENAR]], xb = [], wb = [];
      x = XA;
      cajasB.forEach(function (c, i) { wb[i] = this.ancho(ctx, c[0]); xb[i] = x; x += wb[i] + HUECO; }, this);
      const finB = x - HUECO, una = K.suave((v - LLEGA) / UNA), listo = v > LISTO, vivo = K.suave((v - LLEGA - UNA) / 0.5);
      ctx.globalAlpha = K.acotar(v / 0.4, 0, 1);
      ctx.fillStyle = '#e2854a'; ctx.font = '800 64px ' + TITULO; ctx.textAlign = 'left'; ctx.fillText('Hoy', X0, YB1 - 30);
      ctx.globalAlpha = 1;
      // las cajas bajan desde el carril de arriba: elegir sigue siendo elegir; entrenar pasa a ser pre-entrenar, una vez;
      // inferir se encoge hasta ser la red
      const k0 = expo(v / 0.9), k1 = expo((v - 0.1) / 0.9), k2 = expo((v - 0.2) / 0.9);
      this.caja(ctx, K.mezcla(xa[0], xb[0], k0), K.mezcla(YA, YB1, k0), K.mezcla(wa[0], wb[0], k0), ELEGIR, 'Elegir modelo', una * 3, 1);
      this.caja(ctx, xb[1], YB1, wb[1], SIMULAR, 'Simular datasets', una * 3 - 1, K.suave((v - 0.5) / 0.5));
      this.caja(ctx, K.mezcla(xa[1], xb[2], k1), K.mezcla(YA, YB1, k1), K.mezcla(wa[1], wb[2], k1), ENTRENAR, k1 < 0.5 ? 'Entrenar' : 'Pre-entrenar la red', una * 3 - 2, 1);
      if (k2 < 1) {
        const w = K.mezcla(wa[2], 60, k2), h = K.mezcla(ALTO, 60, k2), cx = K.mezcla(xa[2] + wa[2] / 2, XC, k2), cy = K.mezcla(YA + ALTO / 2, YB2, k2);
        ctx.globalAlpha = 1 - 0.75 * k2;
        ctx.fillStyle = 'rgba(' + INFERIR + ',0.16)'; ctx.fillRect(cx - w / 2, cy - h / 2, w, h);
        ctx.strokeStyle = 'rgba(' + INFERIR + ',0.9)'; ctx.lineWidth = 2; ctx.strokeRect(cx - w / 2, cy - h / 2, w, h);
        ctx.globalAlpha = 1;
      }
      // «una sola vez»: un corchete bajo las tres cajas
      const ac = K.suave((v - 0.7) / 0.5), yc = YB1 + ALTO + 16;
      ctx.globalAlpha = ac;
      ctx.strokeStyle = '#7d7568'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(xb[0], yc - 8); ctx.lineTo(xb[0], yc); ctx.lineTo(finB, yc); ctx.lineTo(finB, yc - 8); ctx.stroke();
      ctx.fillStyle = '#f4efe6'; ctx.font = '600 34px ' + TEXTO; ctx.textAlign = 'center'; ctx.fillText('una sola vez', (xb[0] + finB) / 2, yc + 44);
      ctx.globalAlpha = 1;
      // los datasets simulados corren de «simular» a «pre-entrenar» mientras se llenan
      const corre = K.acotar(una * 3 - 0.6, 0, 1) * (1 - vivo);
      if (corre > 0) {
        ctx.fillStyle = 'rgba(' + SIMULAR + ',0.9)';
        for (let i = 0; i < 14; i++) {
          const q = (v * 1.6 + i / 14) % 1, px = K.mezcla(xb[1] + wb[1] * 0.5, xb[2] + wb[2] * 0.6, q), py = YB1 - 14 - Math.sin(q * 3.1416) * 26 - (i % 3) * 5;
          ctx.globalAlpha = corre * Math.sin(q * 3.1416);
          ctx.fillRect(px, py, 9, 9);
        }
        ctx.globalAlpha = 1;
      }
      // el carril de hoy: los datasets esperan a la izquierda y la red queda en medio
      ctx.strokeStyle = '#2d2924'; ctx.lineWidth = 2; ctx.setLineDash([4, 10]);
      ctx.beginPath(); ctx.moveTo(X0 + 100, YB2); ctx.lineTo(XG - 16, YB2); ctx.stroke(); ctx.setLineDash([]);
      const pulsos = listo ? Math.floor((v - LISTO) / PULSO) : 0;
      ctx.globalAlpha = K.suave((v - 0.3) / 0.5);
      this.pila(ctx, X0, YB2, pulsos, 0);
      ctx.globalAlpha = 1;
      // de «pre-entrenar» a la red: cuando termina, la red se enciende
      ctx.strokeStyle = 'rgba(226,133,74,' + (0.25 + 0.6 * vivo) + ')'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(XC, yc + 66); ctx.lineTo(XC, YB2 - 62); ctx.stroke();
      this.nucleo(ctx, XC, YB2, t, K.acotar(k2 * 0.25 + vivo, 0, 1));
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 30px ' + TEXTO; ctx.textAlign = 'center';
      ctx.globalAlpha = K.suave((v - 0.9) / 0.5); ctx.fillText(listo ? 'la red, ya entrenada' : 'la red', XC, YB2 + 104); ctx.globalAlpha = 1;
      // los datasets cruzan la red de corrido, y cada uno sale respondido
      if (listo) {
        const w = v - LISTO;
        if (!K.quieto) for (let i = 0; i < 5; i++) {
          const q = (w / 0.3 + i / 5) % 1, lado = K.mezcla(70, 24, q), px = K.mezcla(X0 + 70, XC, q * q);
          ctx.globalAlpha = 0.9 * Math.sin(q * 3.1416);
          ctx.drawImage(this.bancos[(pulsos + i) % n].datos, px - lado / 2, YB2 - lado / 2, lado, lado);
        }
        ctx.globalAlpha = 1;
        const cols = 8, filas = 3, lado = 64, total = cols * filas, hay = Math.min(total, pulsos);
        for (let i = 0; i < hay; i++) {
          const sx = XG + (i % cols) * (lado + 6), sy = YB2 - 104 + Math.floor(i / cols) * (lado + 6);
          const cual = pulsos <= total ? i : pulsos - ((pulsos - i) % total + total) % total;       // cada casilla se renueva al llegar su turno
          ctx.drawImage(this.bancos[((cual % n) + n) % n].mapa, sx, sy, lado, lado);
          const edad = K.quieto ? 9 : ((pulsos - i) % total + total) % total;
          if (edad < 3) { ctx.strokeStyle = 'rgba(255,240,210,' + (1 - edad / 3) + ')'; ctx.lineWidth = 3; ctx.strokeRect(sx, sy, lado, lado); }
        }
      }
      this.cuenta(ctx, 1560, YB2 + 44, pulsos, '#e2854a');
    },
  });
})();
