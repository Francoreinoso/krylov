/* 8 a 11 · Las otras cuatro decisiones de la mina, cada una como una escena hecha de puntos que se mueve con
   los datos del archivo de su caso (datos.js → series). Nada de lo que se mueve es adorno:
   - taludes: la pared de la mina, partida en sus sectores; cada sector se desplaza lo que el radar midió, hora a hora;
   - flotación: las líneas de estanques; la espuma de cada estanque brilla según el cobre que flotó ahí,
     y la columna del final de cada línea es el cobre recuperado hasta ese punto, contra la meta;
   - flota: los camiones subiendo la rampa; la columna sobre cada uno es su desgaste, y la marca roja, la falla;
   - sismicidad: los túneles después de una explosión; cada destello es un temblor del archivo, a su hora y con su magnitud.
   Si el motor del caso ya responde (series.<caso>.respuesta), cada unidad toma el color de su decisión y la columna
   de texto muestra cuántas hay de cada una. Mientras no responda, el color solo dice cuánto se midió. */
(function () {
  'use strict';
  const K = window.K;
  const GLSL = `
    const vec3 COBRE = vec3(0.91, 0.52, 0.27);
    const vec3 ORO = vec3(1.0, 0.82, 0.45);
    const vec3 OXIDO = vec3(0.21, 0.76, 0.68);
    const vec3 ARENA = vec3(0.50, 0.45, 0.38);
    const vec3 ROJO = vec3(0.92, 0.36, 0.22);`;
  const FRAG = `
    precision highp float;
    varying vec3 vColor;
    varying float vA;
    void main() {
      vec2 d = gl_PointCoord - 0.5;
      float r = dot(d, d);
      if (r > 0.25 || vA < 0.004) discard;
      gl_FragColor = vec4(vColor * vA * (1.0 - r * 2.4), 1.0);
    }`;
  const FRAG_LINEA = 'precision highp float;\nvarying vec3 vColor;\nvarying float vA;\nvoid main() { gl_FragColor = vec4(vColor * vA, 1.0); }';
  const DECISION = { actuar: [0.92, 0.36, 0.22], en_duda: [0.95, 0.78, 0.36], no_actuar: [0.12, 0.68, 0.49] };
  const ROJO = [0.92, 0.36, 0.22], COBRE = [0.91, 0.52, 0.27];

  // ---------- lo común a las cuatro ----------
  function base(fov) {
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(fov, 16 / 9, 1, 300);
    const u = { uT: { value: 0 }, uEsc: { value: 2000 } };
    const B = {
      scene: scene, camera: camera, u: u, tres: { scene: scene, camera: camera },
      material: function (vertex, extra, lineas) {
        return new THREE.ShaderMaterial({
          uniforms: Object.assign({}, u, extra || {}),
          vertexShader: 'uniform float uT;\nuniform float uEsc;\nvarying vec3 vColor;\nvarying float vA;\n' + GLSL + vertex,
          fragmentShader: lineas ? FRAG_LINEA : FRAG, transparent: true, depthWrite: false,
          // la luz solo suma: el lienzo no se vuelve opaco donde un punto ya casi se apagó
          blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
          blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor,
        });
      },
      geometria: function (atributos) {
        const g = new THREE.BufferGeometry();
        Object.keys(atributos).forEach(function (k) { g.setAttribute(k, new THREE.BufferAttribute(new Float32Array(atributos[k][0]), atributos[k][1])); });
        return g;
      },
      puntos: function (atributos, vertex, extra) {
        const p = new THREE.Points(B.geometria(atributos), B.material(vertex, extra));
        p.frustumCulled = false; scene.add(p);
        return p;
      },
      trazos: function (atributos, vertex, extra) {
        const l = new THREE.LineSegments(B.geometria(atributos), B.material(vertex, extra, true));
        l.frustumCulled = false; scene.add(l);
        return l;
      },
      lineas: function (v, color, opacidad) {
        const l = new THREE.LineSegments(B.geometria({ position: [v, 3] }), new THREE.LineBasicMaterial({ color: color, transparent: true, opacity: opacidad, depthWrite: false, blending: THREE.AdditiveBlending }));
        l.frustumCulled = false; scene.add(l);
        return l;
      },
      ajustar: function () { u.uEsc.value = (K.gl.renderer.getPixelRatio() * 1080) / (2 * Math.tan((fov * Math.PI) / 360)); },
      // la cámara gira alrededor de un punto; dx corre la escena a la derecha del texto
      mirar: function (az, el, R, c, dx) {
        camera.position.set(c[0] + R * Math.cos(el) * Math.sin(az), c[1] + R * Math.sin(el), c[2] + R * Math.cos(el) * Math.cos(az));
        camera.lookAt(c[0], c[1], c[2]);
        camera.setViewOffset(1920, 1080, dx, 0, 1920, 1080);
        camera.updateMatrixWorld();
      },
    };
    return B;
  }

  // Un recorrido del archivo en el tiempo: avanza, se queda en el final y vuelve a empezar. Devuelve de 0 a 1.
  function recorrido(t, dura, espera) {
    if (K.quieto) return 1;
    if (t < 0) return 0;
    const ciclo = dura + espera, x = ((t % ciclo) + ciclo) % ciclo;
    if (x > ciclo - 0.7) return 1 - K.suave((x - (ciclo - 0.7)) / 0.7);
    return Math.min(1, x / dura);
  }

  // El valor de una serie [[t, v], …] en el momento t (lineal entre lecturas).
  function leer(puntos, t, antes) {
    const n = puntos.length;
    if (t <= puntos[0][0]) return antes == null ? puntos[0][1] : K.mezcla(antes, puntos[0][1], K.acotar(t / puntos[0][0], 0, 1));
    if (t >= puntos[n - 1][0]) return puntos[n - 1][1];
    let i = 1;
    while (puntos[i][0] < t) i++;
    const a = puntos[i - 1], b = puntos[i];
    return K.mezcla(a[1], b[1], (t - a[0]) / (b[0] - a[0]));
  }

  // Lo que dice la columna de texto: cuántas unidades trae el archivo y, si el motor responde, su decisión.
  function llenar(L, S) {
    L.querySelector('.cuantas .num').textContent = S.unidades.length;
    const R = S.respuesta, leyenda = L.querySelector('.leyenda'), cuesta = L.querySelector('.cuesta');
    if (!R) return;
    ['actuar', 'en_duda', 'no_actuar'].forEach(function (e) {
      L.querySelector('[data-rotulo="' + e + '"]').textContent = S.rotulos[e];
      L.querySelector('[data-cuenta="' + e + '"]').textContent = R.colores[e];
    });
    leyenda.hidden = false;
    if (R.costo_de_no_saber != null) { cuesta.querySelector('.monto').textContent = K.miles(R.costo_de_no_saber); cuesta.hidden = false; }
  }
  function tinteDe(S, id, sinRespuesta) {
    const u = S.respuesta && S.respuesta.unidades[id];
    return u ? DECISION[u.estado] : sinRespuesta;
  }

  // Etiquetas del DOM que siguen a un punto del 3D.
  function etiquetas(L, n, clase) {
    const capa = L.querySelector('.capa-etq'), salida = [];
    for (let i = 0; i < n; i++) {
      const e = document.createElement('div');
      e.className = 'etq ' + clase;
      e.appendChild(document.createElement('div'));
      capa.appendChild(e); salida.push(e);
    }
    return salida;
  }
  function poner(el, camara, x, y, z, html, ver) {
    const p = K.proyectar(x, y, z, camara);
    if (el._h !== html) { el.firstChild.innerHTML = html; el._h = html; }
    el.style.transform = 'translate(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px)';
    el.classList.toggle('ver', !!ver && !p.detras);
  }
  // En pantalla, el nombre de cada unidad se dice completo: «Sector 25», no «S-25».
  function nombre(id) { return id.replace(/^S-0?/, 'Sector ').replace(/^L-0?/, 'Línea ').replace(/^CAEX-/, 'Camión '); }
  function reloj(el, texto) { if (el._h !== texto) { el.textContent = texto; el._h = texto; } }

  // ============================== 8 · Taludes: la pared de la mina ==============================
  K.registrar('taludes', {
    tres: null, tQuieto: 14,
    crear: function (L) {
      const S = (this.S = K.datos.series.taludes), n = (this.n = S.unidades.length);
      llenar(L, S);
      this.reloj = L.querySelector('.reloj .num');
      this.horas = 0; this.maximo = 0;
      S.unidades.forEach(function (un) { un.puntos.forEach(function (p) { this.horas = Math.max(this.horas, p[0]); this.maximo = Math.max(this.maximo, p[1]); }, this); }, this);
      L.querySelector('.reloj .dato').textContent = 'de ' + Math.round(this.horas) + ' horas de radar';
      if (!K.gl.ok) return;
      const B = (this.B = base(30)), azar = K.azar(11), ANCHO = 18, ALTO = 7, BANCOS = 6;
      // La pared: se curva como un anfiteatro y sube por escalones (cada escalón es un piso de la mina).
      const pared = (this.pared = function (ux, v) {
        const b = Math.min(BANCOS - 1, Math.floor(v * BANCOS)), r = v * BANCOS - b, lado = (ux - 0.5) * 2;
        return [(ux - 0.5) * ANCHO, -ALTO / 2 + ((b + K.suave((r - 0.42) / 0.58)) / BANCOS) * ALTO, 2.6 * lado * lado + 3.2 - 6.4 * v];
      });
      const pos = [], au = [], ar = [], tinte = [];
      for (let s = 0; s < n; s++) {
        const col = tinteDe(S, S.unidades[s].id, ROJO);
        for (let c = 0; c < 14; c++) for (let f = 0; f < 72; f++) {
          const ux = (s + (c + azar()) / 14) / n, v = (f + azar() * 0.9) / 72, p = pared(ux, v);
          pos.push(p[0], p[1], p[2]); au.push(ux, v); ar.push(azar()); tinte.push(col[0], col[1], col[2]);
        }
      }
      // cuánto se ha movido cada sector ahora: una textura de una fila, que el sombreador interpola a lo largo de la pared
      this.mov = new Uint8Array(n * 4);
      this.tex = new THREE.DataTexture(this.mov, n, 1, THREE.RGBAFormat);
      this.tex.magFilter = this.tex.minFilter = THREE.LinearFilter;
      this.tex.needsUpdate = true;
      this.barre = { value: -1 };
      B.puntos({ position: [pos, 3], aU: [au, 2], aR: [ar, 1], aTinte: [tinte, 3] }, `
        attribute vec2 aU;
        attribute float aR;
        attribute vec3 aTinte;
        uniform sampler2D uMov;
        uniform float uBarre;
        uniform float uResp;
        void main() {
          float d = texture2D(uMov, vec2(aU.x, 0.5)).r;                    // de 0 a 1: milímetros sobre el máximo del archivo
          float dv = (aU.y - 0.52) / 0.32;
          float cuanto = d * (0.3 + 0.7 * exp(-dv * dv));                  // el centro de la pared se mueve más que el borde
          vec3 p = position + vec3(0.0, -0.32, 1.0) * cuanto * 2.5;
          float dr = (aU.x - uBarre) / 0.011;
          float radar = exp(-dr * dr) + (aU.x < uBarre ? 0.3 * exp(-(uBarre - aU.x) / 0.07) : 0.0);     // la franja del radar y su estela
          float k = smoothstep(0.05, 0.5, cuanto);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(mix(ARENA, aTinte, uResp * 0.7), aTinte, k) + ORO * radar * 0.85;
          vA = 0.44 + 0.75 * k + 0.2 * uResp + radar * 0.75;
          gl_PointSize = (0.056 + 0.06 * k + 0.05 * radar + 0.03 * aR) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uMov: { value: this.tex }, uBarre: this.barre, uResp: { value: S.respuesta ? 1 : 0 } });
      // dónde estaba la pared: el borde de cada escalón, y una marca por sector en el pie
      const guia = [];
      for (let b = 0; b <= BANCOS; b++) for (let k = 0; k < 72; k++) {
        const v = Math.min(0.999, b / BANCOS), a = pared(k / 72, v), c = pared((k + 1) / 72, v);
        guia.push(a[0], a[1], a[2], c[0], c[1], c[2]);
      }
      for (let s = 0; s <= n; s++) { const a = pared(s / n, 0); guia.push(a[0], a[1], a[2], a[0], a[1] - 0.22, a[2] + 0.1); }
      B.lineas(guia, 0x8a7f70, 0.42);
      // los dos sectores que más se movieron, que no estén pegados
      const finales = S.unidades.map(function (un, i) { return [un.puntos[un.puntos.length - 1][1], i]; }).sort(function (a, b) { return b[0] - a[0]; });
      this.marcados = [finales[0][1]];
      for (let i = 1; i < finales.length && this.marcados.length < 2; i++) if (Math.abs(finales[i][1] - this.marcados[0]) >= 3) this.marcados.push(finales[i][1]);
      this.etq = etiquetas(L, this.marcados.length, 'nota');
      const primero = this.marcados[0];
      this.etq.forEach(function (e, i) { if (i) e.classList.add(this.marcados[i] < primero ? 'izq' : 'alta'); }, this);
      // en la columna de texto: lo que midió el radar en dos sectores de la misma pared, el que más se movió y el que menos
      this.calmo = finales[finales.length - 1][1];
      this.cv = L.querySelector('canvas.curva');
      if (S.respuesta) this.cv.hidden = true; else this.ctx = this.cv.getContext('2d');
      this.tres = B.tres;
    },
    alAjustar: function () {
      if (this.B) this.B.ajustar();
      if (this.ctx) { this.rc = K.razon(1.5); this.cv.width = Math.round(800 * this.rc); this.cv.height = Math.round(250 * this.rc); }
    },
    curva: function (h, ahora) {
      const ctx = this.ctx, S = this.S, x0 = 2, x1 = 500, y0 = 212, y1 = 52;
      ctx.setTransform(this.rc, 0, 0, this.rc, 0, 0);
      ctx.clearRect(0, 0, 800, 250);
      ctx.fillStyle = '#b9b0a1'; ctx.font = '500 25px "Instrument Sans", sans-serif'; ctx.textAlign = 'left';
      ctx.fillText('Dos sectores de la misma pared, hora a hora:', x0, 24);
      ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y0); ctx.stroke();
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px "JetBrains Mono", monospace';
      ctx.fillText('0 h', x0, y0 + 30); ctx.textAlign = 'right'; ctx.fillText(Math.round(this.horas) + ' h', x1, y0 + 30);
      const cabezas = [[this.calmo, '#9a9080'], [this.marcados[0], '#ff7a50']].map(function (par) {
        const pts = S.unidades[par[0]].puntos;
        let ultimo = null;
        ctx.strokeStyle = par[1]; ctx.lineWidth = 3; ctx.lineJoin = 'round'; ctx.beginPath();
        for (let i = 0; i < pts.length && pts[i][0] <= h; i++) {
          const x = x0 + (pts[i][0] / this.horas) * (x1 - x0), y = y0 - (Math.max(0, pts[i][1]) / this.maximo) * (y0 - y1);
          if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y);
          ultimo = [x, y];
        }
        ctx.stroke();
        if (ultimo) { ctx.fillStyle = par[1]; ctx.beginPath(); ctx.arc(ultimo[0], ultimo[1], 6, 0, 6.2832); ctx.fill(); }
        return { u: ultimo, color: par[1], texto: nombre(S.unidades[par[0]].id) + ': ' + K.coma(Math.max(0, ahora[par[0]]), 1) + ' mm' };
      }, this);
      if (cabezas[0].u && cabezas[1].u) {
        const yCalmo = cabezas[0].u[1] + 8, yMovido = Math.min(cabezas[1].u[1] + 8, yCalmo - 32);
        ctx.textAlign = 'left'; ctx.font = '600 25px "Instrument Sans", sans-serif';
        ctx.fillStyle = cabezas[0].color; ctx.fillText(cabezas[0].texto, cabezas[0].u[0] + 16, yCalmo);
        ctx.fillStyle = cabezas[1].color; ctx.fillText(cabezas[1].texto, cabezas[1].u[0] + 16, yMovido);
      }
    },
    cuadro: function (t) {
      const S = this.S, h = recorrido(t - 0.8, 13, 4.5) * this.horas;
      reloj(this.reloj, Math.floor(h) + ' h');
      const ahora = [];
      for (let s = 0; s < this.n; s++) ahora[s] = leer(S.unidades[s].puntos, h, 0);
      if (this.ctx) this.curva(h, ahora);
      if (!this.tres) return;
      const B = this.B;
      for (let s = 0; s < this.n; s++) this.mov[s * 4] = Math.round(K.acotar(ahora[s] / this.maximo, 0, 1) * 255);
      this.tex.needsUpdate = true;
      B.u.uT.value = t;
      this.barre.value = ((t * 0.21) % 1.2) - 0.1;                          // el barrido del radar
      // la cámara se acerca a medida que la pared se mueve
      const cerca = h / this.horas;
      B.mirar(-0.5 + Math.sin(t * 0.17) * 0.07, 0.3, 36 - 4.5 * cerca, [0.3 + 1.0 * cerca, 1.9 - 0.2 * cerca, 0.6], -430);
      for (let i = 0; i < this.etq.length; i++) {
        const s = this.marcados[i], p = this.pared((s + 0.5) / this.n, 0.999), mm = ahora[s];
        poner(this.etq[i], B.camera, p[0], p[1] + 0.15, p[2], '<b>' + nombre(S.unidades[s].id) + '</b>se movió ' + K.coma(Math.max(0, mm), 1) + ' mm', mm > 0.22 * this.maximo);
      }
    },
  });

  // ============================== 9 · Flotación: las líneas de estanques ==============================
  K.registrar('flotacion', {
    tres: null, tQuieto: 20,
    crear: function (L) {
      const S = (this.S = K.datos.series.flotacion), n = (this.n = S.unidades.length);
      llenar(L, S);
      this.reloj = L.querySelector('.reloj .num');
      let celdas = 0, minutos = 0, salto = 0;
      S.unidades.forEach(function (un) {
        celdas = Math.max(celdas, un.puntos.length);
        un.puntos.forEach(function (p, j) { minutos = Math.max(minutos, p[0]); salto = Math.max(salto, p[1] - (j ? un.puntos[j - 1][1] : 0)); });
      });
      this.minutos = minutos; this.meta = S.umbral;
      if (!K.gl.ok) return;
      const B = (this.B = base(28)), azar = K.azar(23);
      const DX = 2.05, DZ = 1.95, W = 1.55, D = 1.2, H = 1.5, Y0 = -0.9, GH = 2.6;
      const xDe = function (c) { return (c - (celdas - 1) / 2) * DX - 1.1; }, zDe = function (l) { return (l - (n - 1) / 2) * DZ; };
      const xG = (this.xG = xDe(celdas - 1) + DX * 0.86);
      const zG = (this.zG = function (l) { return zDe(l) + D / 2 + 0.42; });      // la canaleta por donde corre lo recuperado
      this.zDe = zDe; this.Y0 = Y0; this.GH = GH;
      const pos = [], ab = [], medidas = [], sin = [];
      for (let l = 0; l < n; l++) {
        const pts = S.unidades[l].puntos;
        for (let c = 0; c < celdas; c++) {
          const x = xDe(c), z = zDe(l), hay = c < pts.length, x0 = x - W / 2, x1 = x + W / 2, z0 = z - D / 2, z1 = z + D / 2, y1 = Y0 + H;
          (hay ? medidas : sin).push(x0, Y0, z0, x1, Y0, z0, x1, Y0, z0, x1, Y0, z1, x1, Y0, z1, x0, Y0, z1, x0, Y0, z1, x0, Y0, z0,
            x0, y1, z0, x1, y1, z0, x1, y1, z0, x1, y1, z1, x1, y1, z1, x0, y1, z1, x0, y1, z1, x0, y1, z0,
            x0, Y0, z0, x0, y1, z0, x1, Y0, z0, x1, y1, z0, x1, Y0, z1, x1, y1, z1, x0, Y0, z1, x0, y1, z1);
          const rico = hay ? (pts[c][1] - (c ? pts[c - 1][1] : 0)) / salto : 0;          // el cobre que flotó en este estanque
          for (let i = 0; i < 230; i++) {
            pos.push(x + (azar() - 0.5) * W * 0.88, azar() * H, z + (azar() - 0.5) * D * 0.88);
            ab.push(azar(), azar(), rico, hay ? pts[c][0] : -1);
          }
        }
      }
      B.lineas(medidas, 0x8a7f70, 0.55);
      B.lineas(sin, 0x8a7f70, 0.2);
      this.minuto = { value: 0 };
      B.puntos({ position: [pos, 3], aB: [ab, 4] }, `
        attribute vec4 aB;        // ritmo, fase, cobre que flotó en este estanque, minuto en que se midió (-1: sin medir)
        uniform float uMin;
        void main() {
          float sube = mod(position.y + uT * (0.3 + 0.6 * aB.x), ${H.toFixed(2)});
          vec3 p = vec3(position.x + sin(uT * 1.3 + aB.y * 30.0) * 0.05, sube + ${Y0.toFixed(2)}, position.z);
          float medida = aB.w < 0.0 ? 0.0 : smoothstep(aB.w - 2.0, aB.w, uMin);
          float espuma = smoothstep(${(H * 0.74).toFixed(2)}, ${(H * 0.94).toFixed(2)}, sube);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(mix(ARENA * 0.8, OXIDO, medida), mix(ARENA, mix(COBRE, ORO, aB.z), medida), espuma);
          vA = 0.14 + 0.2 * medida + espuma * (0.2 + 1.1 * medida * (0.3 + 0.7 * aB.z));
          gl_PointSize = (0.045 + 0.06 * aB.y + espuma * 0.11 * (0.45 + aB.z)) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uMin: this.minuto });
      // La espuma rebalsa por el borde de cada estanque medido y corre por una canaleta hasta el final de la línea:
      // es el cobre que se recuperó ahí (más partículas donde flotó más). Así se llena la columna del final.
      const pr = [], ao = [];
      for (let l = 0; l < n; l++) {
        const pts = S.unidades[l].puntos;
        for (let c = 0; c < pts.length; c++) {
          const rico = (pts[c][1] - (c ? pts[c - 1][1] : 0)) / salto, cuantas = Math.round(16 + 130 * rico);
          for (let i = 0; i < cuantas; i++) { pr.push(xDe(c) + (azar() - 0.5) * W * 0.9, Y0 + H, zDe(l) + D / 2); ao.push(azar(), 0.4 + 0.6 * rico, xG, pts[c][0]); }
        }
      }
      B.puntos({ position: [pr, 3], aO: [ao, 4] }, `
        attribute vec4 aO;        // fase, cuánto cobre flotó ahí, dónde termina la línea, minuto en que se midió ese estanque
        uniform float uMin;
        void main() {
          float u = fract(uT * 0.17 + aO.x);
          float cae = clamp(u / 0.16, 0.0, 1.0), corre = clamp((u - 0.16) / 0.84, 0.0, 1.0);
          vec3 p = vec3(mix(position.x, aO.z, corre), position.y - 0.62 * cae * cae, position.z + 0.42 * cae);
          float medida = smoothstep(aO.w - 1.0, aO.w + 0.5, uMin);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(ORO, COBRE, corre);
          vA = medida * aO.y * (0.2 + 0.8 * sin(3.1416 * u));
          gl_PointSize = (0.05 + 0.06 * aO.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uMin: this.minuto });
      // al final de cada línea, una columna: el cobre recuperado hasta donde se midió
      const pg = [], ag = [], tg = [];
      for (let l = 0; l < n; l++) {
        const col = tinteDe(S, S.unidades[l].id, [1.0, 0.82, 0.45]);
        for (let i = 0; i < 64; i++) { pg.push(xG, Y0 + ((i + 0.5) / 64) * GH, zG(l)); ag.push(l, (i + 0.5) / 64); tg.push(col[0], col[1], col[2]); }
      }
      this.rec = { value: new Array(n).fill(0) };
      B.puntos({ position: [pg, 3], aG: [ag, 2], aTinte: [tg, 3] }, `
        attribute vec2 aG;
        attribute vec3 aTinte;
        uniform float uRec[${n}];
        void main() {
          float lleno = step(aG.y, uRec[int(aG.x + 0.5)]);
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(ARENA, aTinte, lleno);
          vA = 0.24 + 0.9 * lleno;
          gl_PointSize = (0.05 + 0.1 * lleno) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uRec: this.rec });
      // la meta de la planta, a la misma altura en las ocho columnas
      const meta = [], yM = Y0 + this.meta * GH;
      for (let k = 0; k < 40; k++) { const z = K.mezcla(zG(0) - 1.1, zG(n - 1) + 1.1, k / 40), z2 = K.mezcla(zG(0) - 1.1, zG(n - 1) + 1.1, (k + 0.55) / 40); meta.push(xG, yM, z, xG, yM, z2); }
      B.lineas(meta, 0xffffff, 0.95);
      this.etq = etiquetas(L, n, 'chica');
      this.etqMeta = etiquetas(L, 1, 'chica')[0];
      this.etqMeta.classList.add('meta');
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      const S = this.S, m = recorrido(t - 0.6, 9, 6) * (this.minutos + 1.5);
      reloj(this.reloj, Math.floor(Math.min(m, this.minutos)) + ' min');
      if (!this.tres) return;
      const B = this.B;
      B.u.uT.value = t;
      this.minuto.value = m;
      B.mirar(-0.66 + Math.sin(t * 0.15) * 0.06, 0.5, 37, [2.0, 1.0, 0.4], -330);
      for (let l = 0; l < this.n; l++) {
        const pts = S.unidades[l].puntos, r = m < 0.4 ? 0 : leer(pts, m, 0);
        this.rec.value[l] = r;
        poner(this.etq[l], B.camera, this.xG + 0.2, this.Y0 + this.GH + 0.2, this.zG(l), '<b>' + nombre(S.unidades[l].id) + '</b> ' + Math.round(r * 100) + '%', m >= pts[0][0]);
      }
      poner(this.etqMeta, B.camera, this.xG, this.Y0 + this.meta * this.GH, this.zG(0) - 1.1, 'Meta: ' + Math.round(this.meta * 100) + '%', true);
    },
  });

  // ============================== 10 · Flota: los camiones en la rampa ==============================
  K.registrar('flota', {
    tres: null, tQuieto: 17,
    crear: function (L) {
      const S = (this.S = K.datos.series.flota), n = (this.n = S.unidades.length);
      llenar(L, S);
      this.reloj = L.querySelector('.reloj .num');
      this.horas = 0;
      S.unidades.forEach(function (un) { this.horas = Math.max(this.horas, un.puntos[un.puntos.length - 1][0]); }, this);
      this.falla = S.umbral || 1;
      if (!K.gl.ok) return;
      const B = (this.B = base(30)), azar = K.azar(37), VUELTAS = 1.7, ALTO_COL = 2.6, PIE = 1.85;
      this.ALTO_COL = ALTO_COL; this.PIE = PIE;
      // la rampa: una espiral que sube desde el fondo del rajo
      const rampa = (this.rampa = function (s, afuera) {
        const a = 0.5 + s * 6.2832 * VUELTAS, r = 3.0 + 6.9 * s + (afuera || 0);
        return [1.28 * r * Math.cos(a), -3.5 + 6.6 * s, r * Math.sin(a)];
      });
      const pos = [], ar = [], paso = 6.9 / VUELTAS;                          // lo que crece el radio en una vuelta
      for (let i = 0; i < 24000; i++) {
        const s = -0.12 + azar() * 1.12, cresta = azar() < 0.24, w = cresta ? 0.34 + azar() * 0.012 : azar(), camino = w < 0.34;
        // de la rampa hacia afuera: primero el camino, plano; después la pared, que sube hasta la vuelta siguiente
        const sube = camino ? 0 : K.suave((w - 0.34) / 0.66) * (6.6 / VUELTAS), p = rampa(Math.max(s, -0.12), w * paso);
        if ((s < 0 && w > 0.5) || p[1] + sube > 3.5) continue;
        pos.push(p[0], p[1] + sube + (azar() - 0.5) * 0.05, p[2]); ar.push(cresta ? 2 : (camino ? 1 : 0), azar());
      }
      for (let i = 0; i < 700; i++) { const a = azar() * 6.2832, r = Math.sqrt(azar()) * 3.0; pos.push(1.28 * r * Math.cos(a), -3.5 - 0.1 * azar(), r * Math.sin(a)); ar.push(0, azar()); }
      B.puntos({ position: [pos, 3], aR: [ar, 2] }, `
        attribute vec2 aR;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(ARENA, ARENA * 1.35, min(aR.x, 1.0));
          vA = 0.26 + 0.2 * min(aR.x, 1.0) + 0.14 * aR.y + 0.16 * step(1.5, aR.x);
          gl_PointSize = (0.055 + 0.045 * aR.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`);
      // un camión, hecho de puntos para que se vea en cualquier pantalla: chasis, tolva, cabina, ruedas y dos focos
      const T = [], tipo = [];
      const punto = function (x, y, z, k) { T.push(x, y, z); tipo.push(k || 0); };
      const arista = function (a, b) {                                                  // puntos seguidos a lo largo de una arista
        const largo = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]), cuantos = Math.max(2, Math.ceil(largo / 0.055));
        for (let i = 0; i <= cuantos; i++) punto(K.mezcla(a[0], b[0], i / cuantos), K.mezcla(a[1], b[1], i / cuantos), K.mezcla(a[2], b[2], i / cuantos));
      };
      const caja = function (x0, x1, y0, y1, z0, z1) {
        [[x0, y0], [x1, y0], [x1, y1], [x0, y1]].forEach(function (q, i, lista) {
          const r = lista[(i + 1) % 4];
          arista([q[0], q[1], z0], [r[0], r[1], z0]); arista([q[0], q[1], z1], [r[0], r[1], z1]); arista([q[0], q[1], z0], [q[0], q[1], z1]);
        });
      };
      caja(-0.8, 0.8, 0.26, 0.46, -0.36, 0.36);                                         // chasis
      caja(0.42, 0.78, 0.46, 0.86, -0.36, 0.02);                                        // cabina
      const perfil = [[-0.74, 0.48], [0.3, 0.48], [0.44, 0.96], [0.9, 0.96], [0.9, 1.08], [-0.9, 1.08]];   // tolva, con visera
      perfil.forEach(function (q, i) {
        const r = perfil[(i + 1) % perfil.length];
        arista([q[0], q[1], -0.43], [r[0], r[1], -0.43]); arista([q[0], q[1], 0.43], [r[0], r[1], 0.43]); arista([q[0], q[1], -0.43], [q[0], q[1], 0.43]);
      });
      [[-0.48, -0.42], [-0.48, 0.42], [0.5, -0.42], [0.5, 0.42]].forEach(function (c) {     // ruedas
        for (let k = 0; k < 22; k++) { const a = (k / 22) * 6.2832; punto(c[0] + Math.cos(a) * 0.29, 0.29 + Math.sin(a) * 0.29, c[1]); }
        for (let k = 0; k < 8; k++) { const a = (k / 8) * 6.2832; punto(c[0] + Math.cos(a) * 0.13, 0.29 + Math.sin(a) * 0.13, c[1]); }
      });
      punto(0.84, 0.52, -0.26, 1); punto(0.84, 0.52, 0.26, 1);                          // focos
      const ESC = 1.45, pt = [], ac = [], tt = [];
      for (let i = 0; i < n; i++) {
        const col = tinteDe(S, S.unidades[i].id, null) || [0, 0, 0];
        for (let k = 0; k < tipo.length; k++) { pt.push(T[k * 3] * ESC, T[k * 3 + 1] * ESC, T[k * 3 + 2] * ESC); ac.push(i, tipo[k]); tt.push(col[0], col[1], col[2]); }
      }
      this.cam = { value: [] }; this.est = { value: [] };
      for (let i = 0; i < n; i++) { this.cam.value.push(new THREE.Vector4()); this.est.value.push(new THREE.Vector2()); }
      const comun = { uCam: this.cam, uEst: this.est, uResp: { value: S.respuesta ? 1 : 0 } };
      const cabecera = `
        attribute vec2 aCam;           // qué camión es, y si este punto es un foco (o la marca de la falla, en la columna)
        attribute vec3 aTinte;
        uniform vec4 uCam[${n}];       // dónde va cada camión (x, y, z) y hacia dónde mira
        uniform vec2 uEst[${n}];       // su desgaste (0 a 1: 1 es la falla) y cuánto se ve
        uniform float uResp;
        vec3 colorDe(float des) {
          vec3 c = des < 0.55 ? mix(OXIDO, COBRE, des / 0.55) : mix(COBRE, ROJO, smoothstep(0.55, 0.9, des));
          return mix(c, aTinte, uResp);
        }`;
      B.puntos({ position: [pt, 3], aCam: [ac, 2], aTinte: [tt, 3] }, cabecera + `
        void main() {
          int i = int(aCam.x + 0.5);
          vec4 c = uCam[i];
          float co = cos(c.w), si = sin(c.w), des = uEst[i].x;
          vec3 p = vec3(position.x * co - position.z * si, position.y, position.x * si + position.z * co) + c.xyz;
          float alerta = smoothstep(0.8, 0.95, des) * (0.5 + 0.5 * sin(uT * 7.0));       // el que está por fallar, parpadea
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = aCam.y > 0.5 ? vec3(1.0, 0.95, 0.8) : colorDe(des) * (1.0 + 0.9 * alerta);
          vA = uEst[i].y * (aCam.y > 0.5 ? 1.7 : 0.5 + 0.5 * alerta);
          gl_PointSize = (aCam.y > 0.5 ? 0.17 : 0.062) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);
      // sobre cada camión, su desgaste: la columna se llena hasta donde va; arriba, la marca de la falla
      const pc = [], acol = [], fc = [], tc = [];
      for (let i = 0; i < n; i++) {
        const col = tinteDe(S, S.unidades[i].id, null) || [0, 0, 0];
        for (let k = 0; k < 36; k++) { pc.push(0, 0, 0); acol.push(i, 0); fc.push((k + 0.5) / 36); tc.push(col[0], col[1], col[2]); }
        for (let k = 0; k < 7; k++) { pc.push((k - 3) * 0.1, 0, 0); acol.push(i, 1); fc.push(1.0); tc.push(col[0], col[1], col[2]); }
      }
      B.puntos({ position: [pc, 3], aCam: [acol, 2], aF: [fc, 1], aTinte: [tc, 3] }, cabecera + `
        attribute float aF;            // la altura dentro de la columna (0 a 1)
        void main() {
          int i = int(aCam.x + 0.5);
          float des = uEst[i].x, lleno = step(aF, des);
          vec4 mv = modelViewMatrix * vec4(uCam[i].xyz + vec3(0.0, ${PIE.toFixed(2)} + aF * ${ALTO_COL.toFixed(2)}, 0.0), 1.0);
          mv.x += position.x;                                               // la marca de la falla, siempre de frente
          vColor = aCam.y > 0.5 ? ROJO : mix(ARENA, colorDe(des), lleno);
          vA = uEst[i].y * (aCam.y > 0.5 ? 1.0 : 0.3 + 0.9 * lleno);
          gl_PointSize = (aCam.y > 0.5 ? 0.09 : 0.05 + 0.1 * lleno) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);
      this.etq = etiquetas(L, 2, 'nota');
      this.etq[1].classList.add('alta');
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      const S = this.S, h = recorrido(t - 0.6, 12, 5) * this.horas;
      reloj(this.reloj, K.miles(Math.floor(h / 10) * 10) + ' h');
      if (!this.tres) return;
      const B = this.B, orden = [];
      B.u.uT.value = t;
      B.mirar(0.35 + t * 0.03, 0.66, 48, [0, 0.8, 0], -480);
      for (let i = 0; i < this.n; i++) {
        const pts = S.unidades[i].puntos, des = K.acotar(leer(pts, h, 0) / this.falla, 0, 1);
        const s = (((i / this.n + t * 0.013) % 1) + 1) % 1, p = this.rampa(s, 0.7), q = this.rampa(s + 0.004, 0.7);
        this.cam.value[i].set(p[0], p[1], p[2], Math.atan2(q[2] - p[2], q[0] - p[0]));
        this.est.value[i].set(des, K.acotar(s / 0.03, 0, 1) * K.acotar((1 - s) / 0.03, 0, 1));
        orden.push([des, i, p]);
      }
      orden.sort(function (a, b) { return b[0] - a[0]; });
      for (let k = 0; k < this.etq.length; k++) {
        const o = orden[k];
        // la etiqueta no se muestra mientras su camión pasa por debajo del reloj: dos textos nunca se pisan
        const y = o[2][1] + this.PIE + this.ALTO_COL + 0.1, q = K.proyectar(o[2][0], y, o[2][2], B.camera), libre = !(q.x > 1130 && q.y < 390);
        poner(this.etq[k], B.camera, o[2][0], y, o[2][2],
          '<b>' + nombre(S.unidades[o[1]].id) + '</b>desgaste: ' + Math.floor(o[0] * 100) + '% del límite', libre && o[0] > 0.8 && this.est.value[o[1]].y > 0.9);
      }
    },
  });

  // ============================== 11 · Sismicidad: los túneles después de la explosión ==============================
  K.registrar('sismicidad', {
    tres: null, tQuieto: 16,
    crear: function (L) {
      const S = (this.S = K.datos.series.sismicidad), n = (this.n = S.unidades.length);
      llenar(L, S);
      this.reloj = L.querySelector('.reloj .num');
      this.horas = S.horizonte || 6;
      this.fuerte = S.umbral == null ? 1 : S.umbral;
      if (!K.gl.ok) return;
      const B = (this.B = base(30)), azar = K.azar(53), LARGO = 5.6;
      const arco = function (salida, cx, cy, cz, radio, alZ) {
        for (let j = 0; j < 12; j++) {
          const a = (j / 12) * Math.PI, b = ((j + 1) / 12) * Math.PI;
          if (alZ) salida.push(cx, cy + Math.sin(a) * radio, cz + Math.cos(a) * radio, cx, cy + Math.sin(b) * radio, cz + Math.cos(b) * radio);
          else salida.push(cx + Math.cos(a) * radio, cy + Math.sin(a) * radio, cz, cx + Math.cos(b) * radio, cy + Math.sin(b) * radio, cz);
        }
      };
      // el túnel principal, a lo largo; de él salen los ocho sectores, cuatro a cada lado
      const principal = [];
      for (let k = 0; k <= 22; k++) arco(principal, -9 + k * 0.82, -0.5, 0, 0.82, true);
      principal.push(-9, -0.5, -0.82, 9.04, -0.5, -0.82, -9, -0.5, 0.82, 9.04, -0.5, 0.82);
      B.lineas(principal, 0x8a7f70, 0.75);
      this.sector = [];
      const pe = [], dir = [], ev = [];
      this.eventos = [];
      for (let k = 0; k < n; k++) {
        const x = -6.6 + Math.floor(k / 2) * 4.4, lado = k % 2 ? 1 : -1, v = [];
        for (let j = 0; j <= 7; j++) arco(v, x, -0.5, lado * (0.95 + j * (LARGO / 7)), 0.7, false);
        v.push(x - 0.7, -0.5, lado * 0.95, x - 0.7, -0.5, lado * (0.95 + LARGO), x + 0.7, -0.5, lado * 0.95, x + 0.7, -0.5, lado * (0.95 + LARGO));
        const tunel = B.lineas(v, 0x8a7f70, 0.5), tinte = tinteDe(S, S.unidades[k].id, null);
        this.sector.push({ x: x, lado: lado, fin: lado * (0.95 + LARGO), linea: tunel, tinte: tinte, horas: [] });
        S.unidades[k].puntos.forEach(function (p) {
          const a = azar() * 6.2832, r = 0.95 + azar() * 1.35, c = [x + Math.cos(a) * r * 1.15, 0.1 + Math.sin(a) * r * 0.85, lado * (1.3 + azar() * (LARGO - 0.7))];
          this.sector[k].horas.push(p[0]);
          if (p[1] >= this.fuerte) this.eventos.push({ hora: p[0], mag: p[1], sector: k, c: c });
          pe.push(c[0], c[1], c[2]); dir.push(0, 0, 0); ev.push(p[0], p[1], 0);                  // la brasa que queda
          for (let i = 0; i < 44; i++) {                                                       // la onda que se abre
            const u = 2 * azar() - 1, b = azar() * 6.2832, q = Math.sqrt(1 - u * u);
            pe.push(c[0], c[1], c[2]); dir.push(q * Math.cos(b), u, q * Math.sin(b)); ev.push(p[0], p[1], 1);
          }
        }, this);
      }
      this.hora = { value: 0 }; this.extra = { value: 0 };
      const tiempos = { uHora: this.hora, uExtra: this.extra, uSeg: { value: 13 / this.horas }, uFuerte: { value: this.fuerte } };
      B.puntos({ position: [pe, 3], aDir: [dir, 3], aE: [ev, 3] }, `
        attribute vec3 aDir;
        attribute vec3 aE;             // la hora del temblor, su magnitud y si este punto es parte de la onda
        uniform float uHora;
        uniform float uExtra;
        uniform float uSeg;
        uniform float uFuerte;
        void main() {
          float edad = (uHora - aE.x) * uSeg + uExtra;                       // segundos de animación desde el temblor
          float mag = clamp((aE.y + 1.0) / 2.3, 0.0, 1.0), fuerte = step(uFuerte, aE.y);
          float nace = step(aE.x, uHora);
          float radio = (0.3 + 1.5 * mag + 2.4 * fuerte) * (1.0 - exp(-edad * 2.4));
          vec4 mv = modelViewMatrix * vec4(position + aDir * radio, 1.0);
          float onda = aE.z;
          vColor = mix(mix(COBRE, ORO, exp(-edad * 1.6)), ROJO, fuerte);
          vA = nace * mix(0.62 + 0.5 * mag + 0.6 * fuerte + 1.2 * exp(-edad * 1.4), (0.45 + 0.7 * mag + fuerte) * exp(-edad * (1.9 - 1.1 * fuerte)), onda);
          gl_PointSize = mix((0.13 + 0.26 * mag + 0.22 * fuerte) * (1.0 + 1.5 * exp(-edad * 3.0)), 0.07 + 0.07 * mag + 0.08 * fuerte, onda) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, tiempos);
      // la explosión que lo empieza todo, en el frente del túnel principal
      const frente = (this.frente = [9.3, 0.0, 0]), px = [], dx = [];
      for (let i = 0; i < 420; i++) { const u = 2 * azar() - 1, b = azar() * 6.2832, q = Math.sqrt(1 - u * u); px.push(frente[0], frente[1], frente[2]); dx.push(q * Math.cos(b), u, q * Math.sin(b), 0.4 + azar() * 0.6); }
      B.puntos({ position: [px, 3], aD: [dx, 4] }, `
        attribute vec4 aD;
        uniform float uHora;
        uniform float uExtra;
        uniform float uSeg;
        void main() {
          float edad = uHora * uSeg + uExtra;
          vec4 mv = modelViewMatrix * vec4(position + aD.xyz * aD.w * 4.2 * (1.0 - exp(-edad * 1.5)), 1.0);
          vColor = mix(vec3(1.0, 0.95, 0.85), COBRE, 1.0 - exp(-edad * 1.2));
          vA = step(0.0005, uHora) * 1.5 * exp(-edad * 0.95);
          gl_PointSize = (0.07 + 0.1 * aD.w) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, tiempos);
      this.etq = etiquetas(L, n, 'chica');
      this.etqFuerte = etiquetas(L, Math.min(2, this.eventos.length), 'nota');
      this.etqFuerte.forEach(function (e) { e.classList.add('roja', 'alta'); });
      this.etqFrente = etiquetas(L, 1, 'nota')[0];
      this.etqFrente.classList.add('izq');
      this.gris = new THREE.Color(0x8a7f70); this.vivo = new THREE.Color(0xf0a060);
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      const S = this.S, DURA = 13, ESPERA = 4.5, k = recorrido(t - 0.7, DURA, ESPERA), h = k * this.horas;
      const min = Math.floor(h * 60);
      reloj(this.reloj, Math.floor(min / 60) + ' h ' + (min % 60 < 10 ? '0' : '') + (min % 60) + ' min');
      if (!this.tres) return;
      const B = this.B, ciclo = DURA + ESPERA, x = (((t - 0.7) % ciclo) + ciclo) % ciclo;
      B.u.uT.value = t;
      this.hora.value = h;
      this.extra.value = K.quieto ? 0.5 : (k >= 1 ? x - DURA : 0);          // en el final, las ondas siguen apagándose
      B.mirar(0.42 + Math.sin(t * 0.16) * 0.1, 0.55, 47, [0.6, 0.9, 0], -330);
      const segPorHora = DURA / this.horas;
      for (let i = 0; i < this.n; i++) {
        const s = this.sector[i];
        let cuenta = 0, actividad = 0;
        for (let j = 0; j < s.horas.length; j++) if (s.horas[j] <= h) { cuenta++; actividad += Math.exp(-((h - s.horas[j]) * segPorHora + this.extra.value) / 1.1); }
        const a = K.acotar(actividad, 0, 1);
        if (s.tinte) s.linea.material.color.setRGB(s.tinte[0], s.tinte[1], s.tinte[2]);
        else s.linea.material.color.copy(this.gris).lerp(this.vivo, a);
        s.linea.material.opacity = 0.7 + 0.3 * a;
        poner(this.etq[i], B.camera, s.x, -0.5, s.fin + s.lado * 0.55, '<b>' + S.unidades[i].id + '</b> ' + cuenta, h > 0);
      }
      for (let i = 0; i < this.etqFuerte.length; i++) {
        const e = this.eventos[i];
        poner(this.etqFuerte[i], B.camera, e.c[0], e.c[1], e.c[2], '<b>Magnitud ' + K.coma(e.mag, 1) + '</b>temblor fuerte', h >= e.hora);
      }
      poner(this.etqFrente, B.camera, this.frente[0], this.frente[1] + 0.9, this.frente[2], '<b>Explosión</b>hora cero', h > 0 && h < this.horas * 0.14);
    },
  });
})();
