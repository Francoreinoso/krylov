/* El zoom de una unidad: un punto fijo de la escena y, unido a él por un hilo, una tarjeta con lo que Krylov sabe ahí:
   la decisión, la estimación con su intervalo de credibilidad de 90% y la distribución a posteriori completa, contra el
   límite con que se decide. Es la misma barra del gráfico de la izquierda, abierta.
   De dónde sale la distribución:
     - leyes: la posteriori de un bloque es normal en el logaritmo del arsénico (la cabeza de mapa del motor espacial entrega
       su media y su desviación); se dibuja con el centro y el intervalo de 90% que ya trae datos.js.
     - los casos de lista: 64 cuantiles de las muestras con que el motor armó su respuesta (datos.js → series.<caso>.respuesta.
       posteriori, de generar.py). Aquí solo se suavizan para dibujarlas; no se calcula ningún intervalo.
   Lo usan terreno.js (lámina 7) y decisiones.js (láminas 8 a 11). */
(function () {
  'use strict';
  const K = window.K;
  // los colores de las decisiones son los tokens de deck.css (:root): la barra y su tarjeta pintan el mismo tono
  const COLOR = K.coloresDecision;
  const ESTADOS = ['no_actuar', 'en_duda', 'actuar'];           // el orden con que generar.py numera los estados del terreno
  const N = 160;                                                // puntos con que se dibuja la curva
  const MONO = '450 19px "JetBrains Mono", monospace';

  function eje(o) {
    const f = o.log ? Math.log : function (v) { return v; }, a = f(o.min), b = f(o.max);
    return function (v) { return (f(Math.max(v, 1e-9)) - a) / (b - a); };
  }
  // La curva, de 0 a 1 en alto, sobre el eje del gráfico.
  function densidad(o) {
    const u = eje(o), d = new Float32Array(N + 1);
    let puntos, ancho;
    if (o.normal) { puntos = [u(o.normal.centro)]; ancho = o.normal.ancho; }
    else {
      puntos = o.cuantiles.map(u);
      let m = 0, s = 0;
      puntos.forEach(function (p) { m += p / puntos.length; });
      puntos.forEach(function (p) { s += ((p - m) * (p - m)) / puntos.length; });
      ancho = Math.max(0.012, 1.06 * Math.sqrt(s) * Math.pow(puntos.length, -0.2));       // la regla de Silverman
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

  // La distribución en la caja (x, y, w, h) del lienzo. brota: de 0 a 1, cuánto ha crecido la curva.
  function dibujar(ctx, x, y, w, h, o, brota) {
    const u = eje(o), d = o._d || (o._d = densidad(o)), yb = y + h - 32, yt = y + 34, alto = (yb - yt) * brota;
    const X = function (v) { return x + K.acotar(u(v), 0, 1) * w; };
    const en = function (q) { q = K.acotar(q, 0, 1) * N; const i = Math.min(N - 1, Math.floor(q)); return d[i] + (d[i + 1] - d[i]) * (q - i); };
    const Y = function (q) { return yb - en(q) * alto; };
    const tramo = function (a, b) {                              // el área bajo la curva entre dos lugares del eje
      a = K.acotar(a, 0, 1); b = K.acotar(b, 0, 1);
      ctx.beginPath(); ctx.moveTo(x + a * w, yb); ctx.lineTo(x + a * w, Y(a));
      for (let i = Math.ceil(a * N); i <= Math.floor(b * N); i++) ctx.lineTo(x + (i / N) * w, yb - d[i] * alto);
      ctx.lineTo(x + b * w, Y(b)); ctx.lineTo(x + b * w, yb); ctx.closePath();
    };
    ctx.save();
    ctx.lineJoin = 'round';
    ctx.fillStyle = o.color + '26'; tramo(0, 1); ctx.fill();
    ctx.fillStyle = o.color + '7a'; tramo(u(o.bajo), u(o.alto)); ctx.fill();          // el intervalo de credibilidad de 90%
    ctx.strokeStyle = o.color; ctx.lineWidth = 3; ctx.beginPath();
    for (let i = 0; i <= N; i++) { const px = x + (i / N) * w, py = yb - d[i] * alto; if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py); }
    ctx.stroke();
    ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, yb); ctx.lineTo(x + w, yb); ctx.stroke();
    // el límite con que se decide, de arriba abajo, con su nombre
    const xl = X(o.limite);
    ctx.strokeStyle = '#f4efe6'; ctx.lineWidth = 2; ctx.setLineDash([6, 6]); ctx.beginPath(); ctx.moveTo(xl, y + 26); ctx.lineTo(xl, yb); ctx.stroke(); ctx.setLineDash([]);   // el límite, punteado; la estimación, sólida
    ctx.font = MONO; ctx.textBaseline = 'alphabetic';
    const rotulo = o.rotuloLimite.toUpperCase(), ar = ctx.measureText(rotulo).width, xr = K.acotar(xl - ar / 2, x, x + w - ar);
    ctx.fillStyle = '#f4efe6'; ctx.textAlign = 'left'; ctx.fillText(rotulo, xr, y + 18);
    // la estimación: la misma marca clara del gráfico de la izquierda
    const um = u(o.medio);
    ctx.globalAlpha *= brota;
    ctx.fillStyle = '#f4efe6'; ctx.fillRect(X(o.medio) - 2, Y(um) - 3, 4, yb - Y(um) + 3);
    // los extremos del intervalo no se escriben bajo la curva: la frase de arriba ya los dice, y ahí la escena los pisaba
    ctx.restore();
  }

  const corto = function (rotulo) { return rotulo.split(':')[0].toLowerCase(); };          // «No sabemos: seguir midiendo» → «no sabemos»
  const horas = function (v) { return v >= 10 ? String(Math.round(v)) : K.coma(v, 1); };
  const cien = function (v, d) { return K.coma(v * 100, d == null ? 1 : d); };

  // Lo que dice la tarjeta de cada caso, con el mismo eje y el mismo límite que su gráfico de la izquierda.
  const DE = {
    leyes: function (i) {
      const T = K.datos.terreno, F = K.filasDe.leyes(1), estado = ESTADOS[T.estado[i]];
      return Object.assign(F, {
        titulo: 'Este punto: ' + corto(T.rotulos[estado]), color: COLOR[estado], bajo: T.bajo[i], medio: T.media[i], alto: T.alto[i],
        texto: K.miles(T.media[i]) + ' ' + T.unidad_valor + ', entre ' + K.miles(T.bajo[i]) + ' y ' + K.miles(T.alto[i]),
        normal: { centro: T.media[i], ancho: Math.log(T.alto[i] / T.bajo[i]) / 3.29 / Math.log(F.max / F.min) },
        formato: function (v) { return K.miles(v); },
      });
    },
    taludes: function (q) { return { texto: 'Faltan ' + horas(q.medio) + ' horas, entre ' + horas(q.bajo) + ' y ' + horas(q.alto), formato: function (v) { return horas(v) + ' h'; } }; },
    flotacion: function (q) { return { texto: 'Recupera ' + cien(q.medio) + '% del cobre, entre ' + cien(q.bajo) + ' y ' + cien(q.alto) + '%', formato: function (v) { return cien(v) + '%'; } }; },
    flota: function (q) { return { texto: 'Riesgo de falla: ' + cien(q.medio) + '%, entre ' + cien(q.bajo) + ' y ' + cien(q.alto) + '%', formato: function (v) { return cien(v) + '%'; } }; },
    sismicidad: function (q) { return { texto: 'Riesgo de temblor fuerte: ' + cien(q.medio) + '%, entre ' + cien(q.bajo) + ' y ' + cien(q.alto) + '%', formato: function (v) { return cien(v) + '%'; } }; },
  };

  K.zoom = {
    dibujar: dibujar, densidad: densidad,
    // La tarjeta de un bloque del terreno (índice dentro de terreno.dentro).
    bloque: function (i) { return DE.leyes(i); },
    // La tarjeta de una unidad de un caso de lista; null si su motor no entregó su posteriori.
    unidad: function (caso, id) {
      const S = K.datos.series[caso], R = S.respuesta, q = R && R.posteriori && R.posteriori[id], r = q && R.unidades[id];
      if (!r || !K.filasDe[caso]) return null;
      const F = K.filasDe[caso]();
      // el eje de la tarjeta es el de su gráfico, o uno más corto si el gráfico lo pide (zoomMax): la curva no queda arrinconada
      return Object.assign({ min: F.min, max: F.zoomMax ? F.zoomMax(q) : F.max, log: F.log, limite: F.limite, rotuloLimite: F.rotuloLimite },
        { titulo: K.nombreDe(id) + ': ' + corto(S.rotulos[r.estado]), color: COLOR[r.estado], bajo: q.bajo, medio: q.medio, alto: q.alto, cuantiles: q.cuantiles }, DE[caso](q));
    },
    // Qué unidad se fija: la que está en duda más cerca del punto de corte (donde más se nota para qué sirve el intervalo);
    // si ninguna está en duda, la de más riesgo.
    elegir: function (caso) {
      const S = K.datos.series[caso], R = S.respuesta;
      if (!R || !R.posteriori) return null;
      let mejor = null, nota = -Infinity;
      S.unidades.forEach(function (un) {
        const r = R.unidades[un.id];
        if (!r || !R.posteriori[un.id]) return;
        const n = r.estado === 'en_duda' ? 10 - Math.abs(r.p - (R.punto_de_corte == null ? 0.5 : R.punto_de_corte)) : r.p;
        if (n > nota) { nota = n; mejor = un.id; }
      });
      return mejor;
    },
    // El lienzo de la tarjeta y su hilo, dentro de la lámina L. ancho y alto, en píxeles de la lámina (1920 × 1080).
    crear: function (L, ancho, alto) {
      const cv = L.querySelector('canvas.zoom'), hilo = document.createElement('div');
      hilo.className = 'hilo-zoom';
      hilo.appendChild(document.createElement('i'));
      L.querySelector('.capa-etq').appendChild(hilo);
      const z = { cv: cv, ctx: cv.getContext('2d'), hilo: hilo, w: ancho, h: alto, rc: 1, _o: null, _b: -1 };
      K.zoom.ajustar(z);
      return z;
    },
    ajustar: function (z) { z.rc = K.razon(1.5); z.cv.width = Math.round(z.w * z.rc); z.cv.height = Math.round(z.h * z.rc); z._b = -1; },
    // En el gráfico de intervalos de la lámina L, la fila de la unidad que abre la tarjeta queda en tinta y las demás, suaves.
    enfocar: function (L, id) {
      const g = L.querySelector('.grafico'), nom = id && K.nombreDe(id);
      if (!g || !nom) return;
      Array.prototype.forEach.call(g.querySelectorAll('.fila'), function (f) { const n = f.querySelector('.nom'); if (n && n.textContent === nom) { f.classList.add('foco'); g.classList.add('con-foco'); } });
    },
    // Dibuja la tarjeta entera: la decisión, la estimación con su intervalo, y la distribución.
    // alfa (opcional, de 0 a 1): la tarjeta entera se funde; la usa el terreno, donde la tarjeta espera a que el banco se levante.
    pintar: function (z, o, brota, alfa) {
      brota = Math.round(K.acotar(brota, 0, 1) * 100) / 100;
      alfa = alfa == null ? 1 : Math.round(K.acotar(alfa, 0, 1) * 50) / 50;
      if (z._o === o && z._b === brota && z._a === alfa) return;
      z._o = o; z._b = brota; z._a = alfa;
      const ctx = z.ctx;
      ctx.setTransform(z.rc, 0, 0, z.rc, 0, 0);
      ctx.clearRect(0, 0, z.w, z.h);
      ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.globalAlpha = alfa;
      ctx.fillStyle = o.color; ctx.font = '800 42px "Big Shoulders Display", sans-serif'; ctx.fillText(o.titulo, 4, 36);
      ctx.fillStyle = '#f4efe6'; ctx.font = '600 28px "Instrument Sans", sans-serif'; ctx.fillText(o.texto, 4, 76);
      dibujar(ctx, 4, 96, z.w - 14, z.h - 96, o, brota);
      ctx.globalAlpha = 1;
    },
    // El hilo: del punto de la escena (px, py) al borde de la tarjeta más cercano. caja: { x0, x1, y } de ese borde.
    hilar: function (z, px, py, caja, ver) {
      const ax = K.acotar(px, caja.x0, caja.x1), ay = caja.y, dx = ax - px, dy = ay - py;
      z.hilo.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px) rotate(' + Math.atan2(dy, dx).toFixed(4) + 'rad)';
      z.hilo.style.width = Math.hypot(dx, dy).toFixed(1) + 'px';
      z.hilo.classList.toggle('ver', !!ver);
    },
  };
})();
