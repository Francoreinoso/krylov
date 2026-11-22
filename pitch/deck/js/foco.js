/* El foco: un punto de la escena que viaja de unidad en unidad y, unida a él por un hilo, la tarjeta con lo que Krylov
   responde ahí: la decisión, la estimación con su intervalo de credibilidad de 90% y la distribución a posteriori completa,
   contra el límite con que se decide. Mientras el punto viaja, la curva, el color y las cifras pasan de una unidad a la otra:
   se ve que la respuesta es distinta en cada lugar.
   De dónde sale cada curva: lo mismo que js/zoom.js (64 cuantiles de las muestras del motor; en el terreno, la normal en el
   logaritmo que entrega la cabeza de mapa). Aquí no se calcula ningún intervalo: solo se dibuja y se mezcla para la transición.
   Lo usan las láminas de las seis decisiones (terreno.js, decisiones.js, flotacion.js, sismicidad.js). */
(function () {
  'use strict';
  const K = window.K, N = 160;
  const W = 780, H = 560;                                        // la tarjeta, en píxeles de la lámina
  const TINTA = '#f4efe6', SUAVE = '#b9b0a1', LINEA = '#3a352e';
  const rgb = function (hex) { const n = parseInt(hex.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const css = function (c, a) { return 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + (a == null ? 1 : a) + ')'; };
  const corto = function (v) { return v >= 10 ? String(Math.round(v)) : K.coma(v, 1); };
  const cien = function (v) { return K.coma(v * 100, 1); };

  // Cómo se dice cada caso en la tarjeta: la cifra grande, qué es, y el nombre de la línea del límite.
  const DICE = {
    leyes: { grande: function (v) { return K.miles(v); }, que: 'ppm de arsénico', rango: function (a, b) { return 'entre ' + K.miles(a) + ' y ' + K.miles(b); }, limite: 'Máximo que acepta la planta', pie: function (v) { return K.miles(v); } },
    taludes: { grande: function (v) { return corto(v) + ' h'; }, que: 'le quedan antes de ceder', rango: function (a, b) { return 'entre ' + corto(a) + ' y ' + corto(b) + ' horas'; }, limite: function (ax) { return 'Próximas ' + ax.limite + ' horas'; }, pie: function (v) { return corto(v) + ' h'; } },
    flotacion: { grande: function (v) { return cien(v) + '%'; }, que: 'del cobre va a recuperar', rango: function (a, b) { return 'entre ' + cien(a) + ' y ' + cien(b) + '%'; }, limite: function (ax) { return 'Meta de la planta: ' + Math.round(ax.limite * 100) + '%'; }, pie: function (v) { return cien(v) + '%'; } },
    flota: { grande: function (v) { return cien(v) + '%'; }, que: 'de riesgo de fallar|antes de su mantención', rango: function (a, b) { return 'entre ' + cien(a) + ' y ' + cien(b) + '%'; }, limite: function (ax) { return 'Sobre ' + cien(ax.limite).replace(',0', '') + '%, conviene parar'; }, pie: function (v) { return cien(v) + '%'; } },
    sismicidad: { grande: function (v) { return cien(v) + '%'; }, que: function () { return 'de riesgo de temblor fuerte en ' + K.datos.series.sismicidad.horizonte + ' horas'; }, rango: function (a, b) { return 'entre ' + cien(a) + ' y ' + cien(b) + '%'; }, limite: function (ax) { return 'Sobre ' + cien(ax.limite).replace(',0', '') + '%, sigue cerrado'; }, pie: function (v) { return cien(v) + '%'; } },
  };

  // El eje de la tarjeta: lineal, en logaritmo (el arsénico) o en raíz (un riesgo que va de 1% a 90%: así el camión sano
  // y el que está por fallar se leen en el mismo gráfico). Devuelve dónde cae un valor, de 0 a 1.
  function escala(eje) {
    const f = eje.log ? Math.log : eje.raiz ? Math.sqrt : function (v) { return v; }, a = f(Math.max(eje.min, eje.log ? 1e-9 : 0)), b = f(eje.max);
    return function (v) { return K.acotar((f(Math.max(v, eje.log ? 1e-9 : 0)) - a) / (b - a), 0, 1); };
  }
  // La curva, de 0 a 1 en alto, sobre ese eje: los cuantiles del motor suavizados (regla de Silverman), o una normal.
  function densidad(eje, cuantiles, normal) {
    const u = escala(eje), d = new Float32Array(N + 1);
    let puntos, ancho;
    if (normal) { puntos = [u(normal.centro)]; ancho = normal.ancho; }
    else {
      puntos = cuantiles.map(u);
      let m = 0, s = 0;
      puntos.forEach(function (p) { m += p / puntos.length; });
      puntos.forEach(function (p) { s += ((p - m) * (p - m)) / puntos.length; });
      ancho = Math.max(0.014, 1.06 * Math.sqrt(s) * Math.pow(puntos.length, -0.2));
    }
    let tope = 0;
    for (let i = 0; i <= N; i++) {
      let v = 0;
      for (let k = 0; k < puntos.length; k++) { const z = (i / N - puntos[k]) / ancho; v += Math.exp(-0.5 * z * z); }
      d[i] = v; tope = Math.max(tope, v);
    }
    for (let i = 0; i <= N; i++) d[i] /= tope;
    return d;
  }
  // La ficha de una unidad de un caso de lista: lo que la tarjeta necesita para dibujarla. null si el motor no dio su posteriori.
  function ficha(caso, id, eje) {
    const S = K.datos.series[caso], R = S.respuesta, q = R && R.posteriori && R.posteriori[id], r = q && R.unidades[id];
    if (!r) return null;
    return { id: id, nombre: K.nombreDe(id), estado: r.estado, decision: S.rotulos[r.estado], color: rgb(K.coloresDecision[r.estado]),
      bajo: q.bajo, medio: q.medio, alto: q.alto, q: q.cuantiles, d: densidad(eje, q.cuantiles) };
  }
  // El eje común de un recorrido: el del gráfico del caso, hasta donde llegan las unidades que se visitan.
  function ejeDe(caso, ids) {
    const S = K.datos.series[caso], R = S.respuesta, F = K.filasDe[caso]();
    let max = F.max;
    if (F.zoomMax) { max = 0; ids.forEach(function (id) { const q = R.posteriori[id]; if (q) max = Math.max(max, F.zoomMax(q)); }); }
    return { min: F.min, max: max, log: !!F.log, raiz: !F.log && F.min === 0 && max > 0.5 && max <= 1, limite: F.limite };
  }

  // Un número con cada dígito en su caja: no tiembla mientras cuenta. Devuelve el ancho que ocupó.
  function cifra(ctx, texto, x, y) {
    const an = ctx.measureText('0').width;
    let px = x;
    ctx.textAlign = 'center';
    for (let i = 0; i < texto.length; i++) {
      const c = texto[i], w = /[0-9]/.test(c) ? an : ctx.measureText(c).width;
      ctx.fillText(c, px + w / 2, y);
      px += w;
    }
    ctx.textAlign = 'left';
    return px - x;
  }
  function encaja(ctx, texto, peso, familia, desde, hasta, ancho) {
    let t = desde;
    for (; t > hasta; t -= 2) { ctx.font = peso + ' ' + t + 'px ' + familia; if (ctx.measureText(texto).width <= ancho) break; }
    ctx.font = peso + ' ' + t + 'px ' + familia;
  }

  K.foco = {
    ancho: W, alto: H, DICE: DICE, ficha: ficha, ejeDe: ejeDe, rgb: rgb, densidad: densidad, escala: escala,
    // La tarjeta y su hilo dentro de la lámina L. El lienzo es <canvas class="foco"> y el hilo va en .capa-etq.
    crear: function (L, caso) {
      const cv = L.querySelector('canvas.foco'), hilo = document.createElement('div');
      hilo.className = 'hilo-foco';
      hilo.innerHTML = '<i></i>';
      L.querySelector('.capa-etq').appendChild(hilo);
      const F = { L: L, caso: caso, cv: cv, ctx: cv.getContext('2d'), hilo: hilo, rc: 1, eje: null, fichas: {}, a: null, b: null, t0: 0, e: 0, llave: '' };
      K.foco.ajustar(F);
      return F;
    },
    ajustar: function (F) { F.rc = K.razon(1.5); F.cv.width = Math.round(W * F.rc); F.cv.height = Math.round(H * F.rc); F.llave = ''; F.caja = null; },
    // Prepara un recorrido por unidades de un caso de lista: su eje común y la ficha de cada una.
    recorrer: function (F, ids) {
      F.eje = ejeDe(F.caso, ids);
      F.ids = ids.filter(function (id) { return (F.fichas[id] = ficha(F.caso, id, F.eje)); });
      K.foco.reiniciar(F);
      return F.ids;
    },
    reiniciar: function (F) { F.a = F.ids && F.ids.length ? F.ids[0] : null; F.b = null; F.t0 = 0; F.e = 0; F.llave = ''; },
    // El paso del recorrido: se queda `pausa` segundos en una unidad y viaja `viaje` segundos a la siguiente.
    // siguiente(actual) → id (por omisión, la que sigue en la lista). Deja en F: a, b y e (0 a 1, ya suavizado).
    avanzar: function (F, t, pausa, viaje, siguiente) {
      if (K.quieto || F.a == null) { F.e = 0; F.b = null; return; }
      if (F.b == null) {
        if (t - F.t0 >= pausa) {
          const n = siguiente ? siguiente(F.a) : F.ids[(F.ids.indexOf(F.a) + 1) % F.ids.length];
          if (n != null && n !== F.a) { F.b = n; F.t1 = t; } else F.t0 = t;
        }
        F.e = 0;
      } else {
        const k = (t - F.t1) / viaje;
        if (k >= 1) { F.a = F.b; F.b = null; F.t0 = t; F.e = 0; } else F.e = K.suave(K.suave(k));
      }
    },
    // Dibuja la tarjeta: la ficha A, o la mezcla de A hacia B (e de 0 a 1). brota: la curva crece al entrar. eje: el del gráfico.
    // Una ficha sin curva (un sector que no se acelera no tiene «horas que faltan») trae `grande`, `que` y `serie`:
    // lo que se midió. Entre una ficha con curva y una sin ella no hay nada que mezclar: las dos se funden a la vez,
    // una saliendo y la otra entrando, y la tarjeta nunca queda vacía.
    pintar: function (F, A, B, e, brota, eje, dice) {
      eje = eje || F.eje; dice = dice || DICE[F.caso];
      if (!B) e = 0;
      brota = Math.round(K.acotar(brota, 0, 1) * 200) / 200;
      const llave = A.id + '|' + (B ? B.id : '') + '|' + e.toFixed(4) + '|' + brota + '|' + (A.sello || '');
      if (llave === F.llave) return;
      F.llave = llave;
      const ctx = F.ctx, T = e < 0.5 ? A : B, mezcla = !!(B && A.d && B.d);
      const igual = !B || (A.nombre === B.nombre && A.decision === B.decision), aTexto = igual ? 1 : K.suave(Math.abs(1 - 2 * e) * 1.6);
      ctx.setTransform(F.rc, 0, 0, F.rc, 0, 0);
      ctx.clearRect(0, 0, W, H);
      ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      // quién es y qué conviene: cambian a mitad de camino, con un fundido corto
      ctx.globalAlpha = aTexto;
      ctx.fillStyle = SUAVE; ctx.font = '700 46px "Big Shoulders Display", sans-serif'; ctx.fillText(T.nombre, 2, 42);
      ctx.fillStyle = css(T.color); encaja(ctx, T.decision, 800, '"Big Shoulders Display", sans-serif', 78, 50, W - 8); ctx.fillText(T.decision, 2, 118);
      ctx.globalAlpha = 1;
      if (mezcla || !B) K.foco.cuerpo(F, A, mezcla ? B : null, e, 1, brota, eje, dice);
      else {                                                    // la cifra cambia en su lugar, con el nombre; lo de abajo se funde, una saliendo y la otra entrando
        const k = K.suave(e);
        K.foco.cuerpo(F, T, null, 0, aTexto, brota, eje, dice, 'cifra');
        K.foco.cuerpo(F, A, null, 0, 1 - k, brota, eje, dice, 'abajo'); K.foco.cuerpo(F, B, null, 0, k, brota, eje, dice, 'abajo');
      }
    },
    // La estimación, su intervalo y la mitad de abajo (la distribución, o lo que se midió) de la ficha X, mezclada hacia Y.
    // parte (opcional): 'cifra' dibuja solo la estimación y su texto; 'abajo', solo la mitad de abajo.
    cuerpo: function (F, X, Y, e, alfa, brota, eje, dice, parte) {
      if (alfa <= 0.004) return;
      const ctx = F.ctx, m = function (a, b) { return a + (b - a) * e; }, T = Y && e >= 0.5 ? Y : X;
      const bajo = Y ? m(X.bajo, Y.bajo) : X.bajo, medio = Y ? m(X.medio, Y.medio) : X.medio, alto = Y ? m(X.alto, Y.alto) : X.alto;
      const tono = Y ? [m(X.color[0], Y.color[0]), m(X.color[1], Y.color[1]), m(X.color[2], Y.color[2])] : X.color;
      // la estimación, grande, y su intervalo: cuentan de una unidad a la otra
      ctx.globalAlpha = parte === 'abajo' ? 0 : alfa;
      ctx.fillStyle = TINTA; ctx.font = '800 112px "Big Shoulders Display", sans-serif';
      const an = cifra(ctx, X.grande || dice.grande(medio), 0, 226);
      ctx.font = '500 29px "Archivo", sans-serif';
      const que = T.que || (typeof dice.que === 'function' ? dice.que() : dice.que), cabe = W - 8 - (an + 22), rango = X.d ? dice.rango(bajo, alto) : null;
      let lineas = [];
      if (que.indexOf('|') >= 0) lineas = que.split('|');                   // un corte fijo: el texto no salta de una a dos líneas cuando cambia el ancho de la cifra
      else que.split(' ').forEach(function (p) { const u = lineas.length - 1, junto = u < 0 ? p : lineas[u] + ' ' + p; if (u >= 0 && ctx.measureText(junto).width <= cabe) lineas[u] = junto; else lineas.push(p); });
      const filas = lineas.length + (rango ? 1 : 0), y0 = filas > 2 ? 152 : filas > 1 ? 186 : 208;
      ctx.fillStyle = SUAVE; lineas.forEach(function (l, i) { ctx.fillText(l, an + 22, y0 + i * 37); });
      if (rango) { ctx.fillStyle = TINTA; ctx.font = '600 29px "Archivo", sans-serif'; ctx.fillText(rango, an + 22, y0 + lineas.length * 37 + 1); }
      // la mitad de abajo: la distribución, o lo que se midió
      if (parte === 'cifra') { ctx.globalAlpha = 1; return; }
      ctx.globalAlpha = alfa;
      const x = 2, w = W - 12, yt = 300, yb = H - 44;
      if (!X.d) {
        const pts = X.serie, t1 = pts[pts.length - 1][0], tope = X.tope || 1, px = function (q) { return x + (q[0] / t1) * w * brota; }, py = function (q) { return yb - (K.acotar(q[1], 0, tope) / tope) * (yb - yt - 20); };
        ctx.strokeStyle = LINEA; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, yb); ctx.lineTo(x + w, yb); ctx.stroke();
        ctx.strokeStyle = css(X.color); ctx.lineWidth = 3.5; ctx.lineJoin = 'round'; ctx.beginPath();
        pts.forEach(function (q, i) { if (i) ctx.lineTo(px(q), py(q)); else ctx.moveTo(px(q), py(q)); });
        ctx.stroke();
        const fin = pts[pts.length - 1]; ctx.fillStyle = css(X.color); ctx.beginPath(); ctx.arc(px(fin), py(fin), 7, 0, 6.2832); ctx.fill();
        ctx.font = '600 23px "Archivo", sans-serif'; ctx.fillStyle = TINTA; ctx.fillText(X.rotuloSerie || '', x, yt - 24);
        ctx.font = '500 22px "JetBrains Mono", monospace'; ctx.fillStyle = SUAVE; ctx.fillText('0 h', x, yb + 30);
        const tf = Math.round(t1) + ' h'; ctx.fillText(tf, x + w - ctx.measureText(tf).width, yb + 30);
        ctx.globalAlpha = 1;
        return;
      }
      // De una unidad a otra la curva se desplaza y cambia de ancho: se mezclan los cuantiles de las dos, no sus dibujos
      // (mezclar los dibujos mostraría, a mitad de camino, una curva de dos lomos que no es la respuesta de ninguna).
      const viaja = Y && e > 0 && e < 1 && X.q && Y.q ? densidad(eje, X.q.map(function (v, i) { return v + (Y.q[i] - v) * e; })) : null;
      const u = escala(eje), dA = viaja || (Y && e >= 1 ? Y.d : X.d), dB = viaja || (Y && e > 0 ? Y.d : X.d), alt = (yb - yt) * brota;
      const en = function (q) { q = K.acotar(q, 0, 1) * N; const i = Math.min(N - 1, Math.floor(q)), va = dA[i] + (dA[i + 1] - dA[i]) * (q - i), vb = dB[i] + (dB[i + 1] - dB[i]) * (q - i); return va + (vb - va) * e; };
      const tramo = function (p, q) {
        ctx.beginPath(); ctx.moveTo(x + p * w, yb);
        for (let i = 0; i <= 80; i++) { const s = p + (q - p) * (i / 80); ctx.lineTo(x + s * w, yb - en(s) * alt); }
        ctx.lineTo(x + q * w, yb); ctx.closePath();
      };
      ctx.lineJoin = 'round';
      ctx.fillStyle = css(tono, 0.15); tramo(0, 1); ctx.fill();
      ctx.fillStyle = css(tono, 0.5); tramo(u(bajo), u(alto)); ctx.fill();                   // el intervalo de credibilidad de 90%
      ctx.strokeStyle = css(tono); ctx.lineWidth = 3.5; ctx.beginPath();
      for (let i = 0; i <= N; i++) { const qx = x + (i / N) * w, qy = yb - en(i / N) * alt; if (i) ctx.lineTo(qx, qy); else ctx.moveTo(qx, qy); }
      ctx.stroke();
      ctx.strokeStyle = LINEA; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, yb); ctx.lineTo(x + w, yb); ctx.stroke();
      // el límite con que se decide, punteado y con su nombre
      const xl = x + u(eje.limite) * w, rotulo = typeof dice.limite === 'function' ? dice.limite(eje) : dice.limite;
      ctx.strokeStyle = TINTA; ctx.lineWidth = 2; ctx.setLineDash([6, 6]); ctx.beginPath(); ctx.moveTo(xl, yt - 14); ctx.lineTo(xl, yb); ctx.stroke(); ctx.setLineDash([]);
      ctx.font = '600 23px "Archivo", sans-serif'; ctx.fillStyle = TINTA;
      const ar = ctx.measureText(rotulo).width; ctx.fillText(rotulo, K.acotar(xl - ar / 2, x, x + w - ar), yt - 24);
      // la estimación, sólida, y los dos extremos del intervalo bajo el eje
      ctx.globalAlpha = alfa * brota;
      const xm = x + u(medio) * w; ctx.fillStyle = TINTA; ctx.fillRect(xm - 2, yb - en(u(medio)) * alt - 3, 4, en(u(medio)) * alt + 3);
      ctx.font = '500 22px "JetBrains Mono", monospace'; ctx.fillStyle = SUAVE;
      const tb = dice.pie(bajo), ta = dice.pie(alto), xb = x + u(bajo) * w, xa = x + u(alto) * w, wb = ctx.measureText(tb).width, wa = ctx.measureText(ta).width;
      const pb = K.acotar(xb - wb / 2, x, x + w - wb), pa = Math.max(K.acotar(xa - wa / 2, x, x + w - wa), pb + wb + 14);
      ctx.fillText(tb, pb, yb + 30); if (pa + wa <= x + w + 2) ctx.fillText(ta, pa, yb + 30);
      ctx.globalAlpha = 1;
    },
    // El hilo: del punto de la escena (px, py, en píxeles de la lámina) al borde derecho de la tarjeta.
    hilar: function (F, px, py, ver) {
      if (!F.caja) {                                            // dónde quedó la tarjeta dentro de la lámina
        let x = 0, y = 0;
        for (let el = F.cv; el && el !== F.L; el = el.offsetParent) { x += el.offsetLeft; y += el.offsetTop; }
        F.caja = { x: x + W + 14, y0: y + 150, y1: y + H - 60 };
      }
      const r = F.caja;
      const ax = r.x, ay = K.acotar(py, r.y0, r.y1), dx = px - ax, dy = py - ay, largo = Math.hypot(dx, dy);
      F.hilo.style.transform = 'translate(' + ax.toFixed(1) + 'px,' + ay.toFixed(1) + 'px) rotate(' + Math.atan2(dy, dx).toFixed(4) + 'rad)';
      F.hilo.style.width = largo.toFixed(1) + 'px';
      F.hilo.classList.toggle('ver', !!ver && px > ax + 30);
    },
    // Todo junto para un recorrido por unidades: avanza, pinta y tiende el hilo. punto(id) → { x, y } en la lámina (o null si no se ve).
    cuadro: function (F, t, punto, pausa, viaje, siguiente) {
      if (F.a == null) return;
      K.foco.avanzar(F, t - 1.6, pausa || 3.4, viaje || 1.1, siguiente);
      const A = F.fichas[F.a], B = F.b ? F.fichas[F.b] : null, brota = K.quieto ? 1 : K.suave((t - 0.45) / 0.7);
      K.foco.pintar(F, A, B, F.e, brota);
      const pa = punto(F.a), pb = B ? punto(F.b) : null;
      if (!pa || (B && !pb)) { K.foco.hilar(F, 0, 0, false); return; }
      const x = B ? K.mezcla(pa.x, pb.x, F.e) : pa.x, y = B ? K.mezcla(pa.y, pb.y, F.e) : pa.y;
      F.px = x; F.py = y;
      K.foco.hilar(F, x, y, t > 1.1 || K.quieto);
    },
  };
})();
