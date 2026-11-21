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
      vec3 c = vColor * vA * (1.0 - r * 2.4);
      gl_FragColor = vec4(c, max(c.r, max(c.g, c.b)));       // la opacidad es la de su canal más fuerte: siempre un color válido
    }`;
  const FRAG_LINEA = 'precision highp float;\nvarying vec3 vColor;\nvarying float vA;\nvoid main() { vec3 c = vColor * vA; gl_FragColor = vec4(c, max(c.r, max(c.g, c.b))); }';
  const DECISION = { actuar: [0.92, 0.36, 0.22], en_duda: [0.95, 0.78, 0.36], no_actuar: [0.12, 0.68, 0.49] };
  const ROJO = [0.92, 0.36, 0.22], COBRE = [0.91, 0.52, 0.27];
  const COLOR_CSS = { actuar: '#ff7a50', en_duda: '#eec25a', no_actuar: '#2fbf8f' };

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
          // La luz suma, y su opacidad también. Antes la opacidad quedaba en cero («solo luz»): un color así no es
          // válido, y hay navegadores que simplemente no lo pintan (el panel de la app de Claude, por ejemplo): la escena
          // desaparecía entera. Con la opacidad igual al canal más fuerte, un punto casi apagado sigue sin tapar el fondo.
          blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
          blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
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
      // un trazo hecho de puntos seguidos: una línea de un píxel casi no se ve en una pantalla de alta densidad
      cordon: function (v, paso, color, alfa, grosor) {
        const pts = [];
        for (let i = 0; i < v.length; i += 6) {
          const largo = Math.hypot(v[i + 3] - v[i], v[i + 4] - v[i + 1], v[i + 5] - v[i + 2]), n = Math.max(1, Math.ceil(largo / paso));
          for (let k = 0; k <= n; k++) pts.push(K.mezcla(v[i], v[i + 3], k / n), K.mezcla(v[i + 1], v[i + 4], k / n), K.mezcla(v[i + 2], v[i + 5], k / n));
        }
        const uni = { uColor: { value: new THREE.Color(color) }, uAlfa: { value: alfa } };
        const obj = B.puntos({ position: [pts, 3] }, `
          uniform vec3 uColor;
          uniform float uAlfa;
          void main() {
            vec4 mv = modelViewMatrix * vec4(position, 1.0);
            vColor = uColor;
            vA = uAlfa;
            gl_PointSize = ${grosor.toFixed(3)} * uEsc / -mv.z;
            gl_Position = projectionMatrix * mv;
          }`, uni);
        obj.color = uni.uColor.value; obj.alfa = uni.uAlfa;
        return obj;
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
  // La columna de texto de cada decisión: lo que Krylov entrega, siempre en el mismo orden.
  //   Respuesta: cuántas unidades conviene actuar y en cuántas no hace falta.
  //   Incertidumbre: en cuántas no se sabe todavía.
  //   Valor: lo que cuesta no saber, que es lo que vale despejar esa duda.
  // Los números aparecen solo si el motor del caso respondió (series.<caso>.respuesta); si no, quedan los rótulos.
  function llenar(L, S) {
    const R = S.respuesta, rot = S.rotulos;
    const item = function (clase, n, texto) { return '<span class="item"><i class="muestra ' + clase + '"></i>' + (n == null ? '' : '<b class="num">' + n + '</b>') + '<span>' + texto + '</span></span>'; };
    L.querySelector('.salida').innerHTML =
      '<div class="fila"><span class="rot">Respuesta</span><span class="cont">' + item('actuar', R ? R.colores.actuar : null, rot.actuar) + item('no-actuar', R ? R.colores.no_actuar : null, rot.no_actuar) + '</span></div>' +
      '<div class="fila"><span class="rot">Incertidumbre</span><span class="cont">' + item('en-duda', R ? R.colores.en_duda : null, rot.en_duda) + '</span></div>' +
      '<div class="fila valor"><span class="rot">Valor</span><span class="cont"><span class="item">' +
      (R && R.costo_de_no_saber != null ? '<b class="num">US$&nbsp;' + K.miles(R.costo_de_no_saber) + '</b><span>lo que vale despejar esa duda</span>' : '<span>Lo que vale despejar esa duda, en dólares</span>') + '</span></span></div>';
    L.classList.toggle('con-respuesta', !!R);
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
  // La pared del rajo, vista desde el otro lado: ocho escalones de roca, partida en los 36 sectores del archivo.
  // Cada sector se abulta y se enciende lo que el radar midió a esa hora (el movimiento está exagerado para que se vea):
  // de roca fría a cobre, a rojo y a blanco donde más se movió. Abajo, el radar y sus haces barren la pared una y otra vez.
  // En la columna de texto, la curva de dos sectores de esa misma pared: el que más se movió y el que menos.
  K.registrar('taludes', {
    tres: null, tQuieto: 14,
    crear: function (L) {
      const S = (this.S = K.datos.series.taludes), n = (this.n = S.unidades.length);
      llenar(L, S);
      this.reloj = L.querySelector('.reloj .num');
      this.horas = 0; this.maximo = 0;
      S.unidades.forEach(function (un) { un.puntos.forEach(function (q) { this.horas = Math.max(this.horas, q[0]); this.maximo = Math.max(this.maximo, q[1]); }, this); }, this);
      L.querySelector('.reloj .dato').textContent = 'de ' + Math.round(this.horas) + ' horas de radar';
      // los dos sectores que más se movieron, que no estén pegados; y el que menos, para la curva
      const finales = S.unidades.map(function (un, i) { return [un.puntos[un.puntos.length - 1][1], i]; }).sort(function (x, y) { return y[0] - x[0]; });
      this.marcados = [finales[0][1]];
      for (let i = 1; i < finales.length && this.marcados.length < 2; i++) if (Math.abs(finales[i][1] - this.marcados[0]) >= 3) this.marcados.push(finales[i][1]);
      this.calmo = finales[finales.length - 1][1];
      // Si la red respondió, el gráfico muestra un sector que conviene cerrar: lo medido, lo que puede venir y cuánto falta.
      this.foco = -1;
      if (S.respuesta) {
        let mejor = -1;
        S.unidades.forEach(function (un, i) {
          const r = S.respuesta.unidades[un.id];
          if (r && r.estado === 'actuar' && r.curva && r.curva.marca && r.p > mejor) { mejor = r.p; this.foco = i; }
        }, this);
        if (this.foco >= 0) this.marcados = [this.foco];
      }
      this.cv = L.querySelector('canvas.curva');
      this.ctx = this.cv.getContext('2d');
      this.cw = this.foco >= 0 ? 640 : 800; this.ch = this.foco >= 0 ? 290 : 250;
      if (!K.gl.ok) return;
      const B = (this.B = base(30)), azar = K.azar(11), ANCHO = 22, ALTO = 9, BANCOS = 8, PIE = 0.36;
      // un ruido suave, para que la roca no sea una lámina lisa
      const G = 32, grano = [];
      for (let i = 0; i < G * G; i++) grano.push(azar() - 0.5);
      const ruido = function (x, y) {
        const x0 = Math.floor(x), y0 = Math.floor(y), fx = K.suave(x - x0), fy = K.suave(y - y0);
        const g = function (i, j) { return grano[((((j % G) + G) % G) * G) + (((i % G) + G) % G)]; };
        return K.mezcla(K.mezcla(g(x0, y0), g(x0 + 1, y0), fx), K.mezcla(g(x0, y0 + 1), g(x0 + 1, y0 + 1), fx), fy);
      };
      // La pared: se curva como un anfiteatro y sube por escalones. En cada escalón, primero el piso y después la cara de roca.
      const pared = (this.pared = function (ux, v) {
        const lado = (ux - 0.5) * 2, r0 = ruido(ux * 9, v * 6), r1 = ruido(ux * 31 + 5, v * 23 + 9);
        const vv = K.acotar(v + r0 * 0.014, 0, 0.9999), b = Math.min(BANCOS - 1, Math.floor(vv * BANCOS)), r = vv * BANCOS - b;
        return [(lado * ANCHO) / 2, -ALTO / 2 + ((b + K.suave((r - PIE) / (1 - PIE))) / BANCOS) * ALTO, 3.6 * lado * lado + 4.3 - 8.6 * v + r0 * 0.55 + r1 * 0.16];
      });
      const pos = [], au = [], as = [], tinte = [];
      const poner3 = function (ux, v, luz, marca, col, enf) { const q = pared(ux, v); pos.push(q[0], q[1], q[2]); au.push(ux, v); as.push(luz, azar(), marca, enf || 0); tinte.push(col[0], col[1], col[2]); };
      for (let s = 0; s < n; s++) {
        const col = tinteDe(S, S.unidades[s].id, ROJO), r0 = S.respuesta && S.respuesta.unidades[S.unidades[s].id];
        const enf = r0 && r0.estado !== 'no_actuar' ? 1 : 0;          // lo que conviene cerrar y lo que está en duda se enciende, se haya movido mucho o poco
        for (let c = 0; c < 16; c++) for (let f = 0; f < 104; f++) {
          const ux = (s + (c + azar()) / 16) / n, v = (f + azar()) / 104, r = (v * BANCOS) % 1;
          // la cara de roca recibe la luz; el piso de cada escalón queda en sombra
          poner3(ux, v, r < PIE ? 0.16 + 0.1 * azar() : 0.5 + 0.5 * K.acotar(0.5 + 1.6 * ruido(ux * 40, v * 30), 0, 1), 0, col, enf);
        }
        for (let b = 0; b < BANCOS; b++) for (let k = 0; k < 26; k++) poner3((s + azar()) / n, (b + 0.985 + azar() * 0.014) / BANCOS, 1.25, 0, col, enf);      // el borde de cada escalón
      }
      // las divisiones entre sectores, tenues; las de los sectores marcados, encendidas
      const marcados = this.marcados;
      for (let s = 0; s <= n; s++) {
        const fuerte = marcados.some(function (m) { return s === m || s === m + 1; }) ? 2 : 1;
        for (let k = 0; k < 150; k++) poner3(Math.min(0.9999, s / n), (k + 0.5) / 150, 1, fuerte, [0, 0, 0]);
      }
      // cuánto se ha movido cada sector ahora: una fila de textura. R: lo medido (color). G: lo mismo, suavizado entre vecinos (forma).
      this.mov = new Uint8Array(n * 4);
      this.tex = new THREE.DataTexture(this.mov, n, 1, THREE.RGBAFormat);
      this.tex.magFilter = this.tex.minFilter = THREE.LinearFilter;
      this.tex.needsUpdate = true;
      this.barre = { value: -1 };
      B.puntos({ position: [pos, 3], aU: [au, 2], aS: [as, 4], aTinte: [tinte, 3] }, `
        attribute vec2 aU;             // dónde está en la pared: a lo largo (0 a 1) y hacia arriba (0 a 1)
        attribute vec4 aS;             // luz, azar, si es una división entre sectores (1) o la de un sector marcado (2), y si su decisión se destaca
        attribute vec3 aTinte;
        uniform sampler2D uMov;
        uniform float uBarre;
        uniform float uResp;
        void main() {
          vec4 m = texture2D(uMov, vec2(aU.x, 0.5));
          float d = m.r, g = m.g, lado = (aU.x - 0.5) * 2.0;
          float dv = (aU.y - 0.36) / 0.36;
          float afuera = g * (0.3 + 0.7 * exp(-dv * dv));                  // la parte baja se abulta hacia el rajo
          float baja = g * (0.2 + 0.8 * aU.y);                             // la parte alta se hunde
          vec3 p = position + vec3(-lado * 0.3, 0.0, 1.0) * afuera * 1.15 + vec3(0.0, -0.5, 0.0) * baja;
          float dr = (aU.x - uBarre) / 0.008;
          float radar = exp(-dr * dr) + (aU.x < uBarre ? 0.3 * exp(-(uBarre - aU.x) / 0.06) : 0.0);    // la franja del radar y su estela
          float k = max(smoothstep(0.04, 0.42, d) * mix(1.0, 0.45, uResp), 0.75 * aS.w * uResp);        // con respuesta manda la decisión, no cuánto se movió
          vec3 caliente = mix(mix(COBRE, ROJO, smoothstep(0.18, 0.55, d)), vec3(1.0, 0.88, 0.74), smoothstep(0.6, 1.0, d));
          vec3 color = mix(mix(ARENA * 0.92, aTinte, uResp * 0.7), mix(caliente, aTinte, uResp), k);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          float marca = aS.z;
          vColor = marca > 0.5 ? vec3(0.96, 0.93, 0.88) : color + ORO * radar * 0.85;
          vA = marca > 0.5 ? (marca > 1.5 ? 0.55 : 0.07) : (0.07 + 0.3 * aS.x) * (1.0 + 1.6 * k) + radar * 0.6;
          gl_PointSize = (marca > 0.5 ? 0.028 : 0.03 + 0.016 * aS.y + 0.022 * k + 0.035 * radar) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uMov: { value: this.tex }, uBarre: this.barre, uResp: { value: S.respuesta ? 1 : 0 } });

      // el radar, al otro lado del rajo: se ubica una vez, donde la cámara lo ve abajo a la derecha
      this.encuadre = { az: 0.5, el: 0.2, R: 37, c: [1.0, 3.1, 0.6], dx: -420 };
      B.mirar(this.encuadre.az, this.encuadre.el, this.encuadre.R, this.encuadre.c, this.encuadre.dx);
      const rayo = new THREE.Vector3(0.34, -0.66, 0.5).unproject(B.camera).sub(B.camera.position).normalize();
      const R = (this.radar = B.camera.position.clone().add(rayo.multiplyScalar(15)).toArray());
      const pr = [];
      for (let k = 0; k < 26; k++) pr.push(R[0], R[1] - 1.3 + (k / 25) * 1.3, R[2]);                          // el poste
      for (let k = 0; k < 44; k++) { const a = (k / 44) * 6.2832; pr.push(R[0] + Math.cos(a) * 0.34, R[1] + Math.sin(a) * 0.34, R[2]); }   // la antena
      for (let k = 0; k < 30; k++) { const a = azar() * 6.2832, q = Math.sqrt(azar()) * 0.32; pr.push(R[0] + Math.cos(a) * q, R[1] + Math.sin(a) * q, R[2]); }
      B.puntos({ position: [pr, 3] }, `
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = ORO;
          vA = 0.8;
          gl_PointSize = 0.05 * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`);
      const HACES = (this.HACES = 40), TRAMOS = (this.TRAMOS = 46), fh = [];
      for (let i = 0; i < HACES * TRAMOS; i++) fh.push(((i % TRAMOS) + 0.5) / TRAMOS);
      this.haces = B.puntos({ position: [new Array(HACES * TRAMOS * 3).fill(0), 3], aF: [fh, 1] }, `
        attribute float aF;            // de 0 (en el radar) a 1 (en la pared)
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = ORO;
          vA = 0.05 + 0.3 * aF;
          gl_PointSize = (0.02 + 0.03 * aF) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`);
      this.etqRadar = etiquetas(L, 1, 'chica')[0];
      this.etq = etiquetas(L, this.marcados.length, 'nota');
      const primero = this.marcados[0];
      this.etq.forEach(function (e, i) { if (i) e.classList.add(this.marcados[i] < primero ? 'izq' : 'alta'); }, this);
      if (this.foco >= 0) this.etq[0].classList.add('hilo');          // un hilo une ese sector con su gráfico, que ya dice su nombre
      this.tres = B.tres;
    },
    alAjustar: function () {
      if (this.B) this.B.ajustar();
      this.rc = K.razon(1.5); this.cv.width = Math.round(this.cw * this.rc); this.cv.height = Math.round(this.ch * this.rc);
    },
    // Con respuesta: un sector que conviene cerrar. Lo que midió el radar (se va dibujando con el recorrido), y desde
    // «ahora» el abanico de lo que Krylov cree que viene, con su rango de cuánto falta. Todo sale de la curva de la API.
    abanico: function (h, brota) {
      const ctx = this.ctx, S = this.S, un = S.unidades[this.foco], R = S.respuesta.unidades[un.id], c = R.curva;
      const W = this.cw, x0 = 4, x1 = W - 10, y0 = this.ch - 38, y1 = 104, color = COLOR_CSS[R.estado];
      const fin = c.t_banda[c.t_banda.length - 1], tope = Math.max.apply(null, c.y) * 2.3;
      const X = function (t) { return x0 + (t / fin) * (x1 - x0); }, Y = function (v) { return y0 - (K.acotar(v, 0, tope) / tope) * (y0 - y1); };
      ctx.setTransform(this.rc, 0, 0, this.rc, 0, 0);
      ctx.clearRect(0, 0, W, this.ch);
      ctx.textAlign = 'left';
      ctx.fillStyle = color; ctx.font = '800 42px "Big Shoulders Display", sans-serif';
      ctx.fillText(nombre(un.id) + ': ' + S.rotulos[R.estado].toLowerCase(), x0, 36);
      ctx.fillStyle = '#f4efe6'; ctx.font = '600 28px "Instrument Sans", sans-serif';
      ctx.fillText(c.marca.texto, x0, 76);
      ctx.strokeStyle = '#3a352e'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y0); ctx.stroke();
      const xa = X(c.ahora);
      ctx.setLineDash([5, 7]); ctx.strokeStyle = '#7d7568'; ctx.beginPath(); ctx.moveTo(xa, y1 - 6); ctx.lineTo(xa, y0); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = '#7d7568'; ctx.font = '450 19px "JetBrains Mono", monospace';
      ctx.fillText('LO QUE MIDIÓ EL RADAR', x0, y0 + 30);
      ctx.textAlign = 'right'; ctx.fillText('LO QUE PUEDE VENIR', x1, y0 + 30);
      if (brota > 0) {                                                    // el abanico: de lo mejor a lo peor que puede pasar
        ctx.globalAlpha = brota;
        ctx.fillStyle = color + '55';
        ctx.beginPath(); ctx.moveTo(xa, Y(c.y[c.y.length - 1]));
        for (let i = 0; i < c.t_banda.length; i++) ctx.lineTo(X(c.t_banda[i]), Y(c.alto[i]));
        for (let i = c.t_banda.length - 1; i >= 0; i--) ctx.lineTo(X(c.t_banda[i]), Y(c.bajo[i]));
        ctx.closePath(); ctx.fill();
        ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.setLineDash([7, 6]); ctx.beginPath(); ctx.moveTo(xa, Y(c.y[c.y.length - 1]));
        for (let i = 0; i < c.t_banda.length; i++) ctx.lineTo(X(c.t_banda[i]), Y(c.medio[i]));
        ctx.stroke(); ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      }
      let ultimo = null;
      ctx.strokeStyle = '#e9dfcc'; ctx.lineWidth = 3; ctx.lineJoin = 'round'; ctx.beginPath();
      for (let i = 0; i < c.t.length && c.t[i] <= h + 0.01; i++) { const x = X(c.t[i]), y = Y(c.y[i]); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); ultimo = [x, y]; }
      ctx.stroke();
      if (ultimo) { ctx.fillStyle = '#e9dfcc'; ctx.beginPath(); ctx.arc(ultimo[0], ultimo[1], 6, 0, 6.2832); ctx.fill(); }
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
      const S = this.S, n = this.n, DURA = 8, ESPERA = 8, k = recorrido(t - 0.8, DURA, ESPERA), h = k * this.horas;
      const ciclo = DURA + ESPERA, x = (((t - 0.8) % ciclo) + ciclo) % ciclo;
      reloj(this.reloj, Math.floor(h) + ' h');
      const ahora = [];
      for (let s = 0; s < n; s++) ahora[s] = leer(S.unidades[s].puntos, h, 0);
      if (this.foco >= 0) this.abanico(h, K.quieto ? 1 : (k >= 1 ? K.acotar((x - DURA) / 0.7, 0, 1) : 0));
      else this.curva(h, ahora);
      if (!this.tres) return;
      const B = this.B, E = this.encuadre;
      let crudo = ahora.map(function (v) { return K.acotar(v / this.maximo, 0, 1); }, this), liso = crudo;
      for (let vez = 0; vez < 4; vez++) liso = liso.map(function (v, s, lista) { return (lista[Math.max(0, s - 1)] + 2 * v + lista[Math.min(n - 1, s + 1)]) / 4; });
      for (let s = 0; s < n; s++) { this.mov[s * 4] = Math.round(crudo[s] * 255); this.mov[s * 4 + 1] = Math.round(liso[s] * 255); }
      this.tex.needsUpdate = true;
      B.u.uT.value = t;
      const ux = (this.barre.value = ((t * 0.2) % 1.25) - 0.12);              // el barrido del radar
      // la cámara se acerca un poco a medida que la pared se mueve
      const cerca = h / this.horas;
      B.mirar(E.az + Math.sin(t * 0.17) * 0.035, E.el, E.R - 2.5 * cerca, E.c, E.dx);
      const ph = this.haces.geometry.attributes.position, R = this.radar;
      this.haces.visible = ux >= 0 && ux <= 1;
      if (this.haces.visible) {
        for (let i = 0; i < this.HACES; i++) {
          const q = this.pared(ux, (i + 0.5) / this.HACES);
          for (let j = 0; j < this.TRAMOS; j++) {
            const f = (j + 0.5) / this.TRAMOS, o = (i * this.TRAMOS + j) * 3;
            ph.array[o] = K.mezcla(R[0], q[0], f); ph.array[o + 1] = K.mezcla(R[1], q[1], f); ph.array[o + 2] = K.mezcla(R[2], q[2], f);
          }
        }
        ph.needsUpdate = true;
      }
      poner(this.etqRadar, B.camera, R[0] + 0.5, R[1], R[2], '<b>Radar</b>', true);
      if (this.foco >= 0) {
        const q = this.pared((this.foco + 0.5) / n, 0.999), pp = K.proyectar(q[0], q[1] + 0.1, q[2], B.camera), el = this.etq[0];
        el.style.transform = 'translate(' + pp.x.toFixed(1) + 'px,' + pp.y.toFixed(1) + 'px)';
        el.style.setProperty('--alto', Math.max(0, pp.y - 384).toFixed(0) + 'px');          // hasta el borde de abajo del gráfico
        el.classList.add('ver');
      }
      for (let i = this.foco >= 0 ? 1 : 0; i < this.etq.length; i++) {
        const s = this.marcados[i], q = this.pared((s + 0.5) / n, 0.999), mm = ahora[s];
        poner(this.etq[i], B.camera, q[0], q[1] + 0.15, q[2], '<b>' + nombre(S.unidades[s].id) + '</b>', this.foco >= 0 || mm > 0.22 * this.maximo);
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
      B.cordon(medidas, 0.06, 0x8a7f70, 0.34, 0.026);
      B.cordon(sin, 0.06, 0x8a7f70, 0.13, 0.026);
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
      B.cordon(meta, 0.04, 0xffffff, 0.9, 0.04);
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
      B.mirar(-0.66 + Math.sin(t * 0.15) * 0.05, 0.5, 46, [1.2, 1.0, 0.4], -415);
      for (let l = 0; l < this.n; l++) {
        const pts = S.unidades[l].puntos, r = m < 0.4 ? 0 : leer(pts, m, 0);
        this.rec.value[l] = r;
      }
      poner(this.etqMeta, B.camera, this.xG, this.Y0 + this.meta * this.GH, this.zG(0) - 1.1, 'Meta: ' + Math.round(this.meta * 100) + '%', true);
    },
  });

  // ============================== 10 · Flota: los camiones en la rampa ==============================
  // Cuarenta camiones mineros, cada uno hecho de miles de puntos sobre su carrocería, subiendo y bajando por los
  // cuatro niveles de la rampa. El color de cada camión es su desgaste (del archivo): de verde, sano, a rojo, cerca
  // de fallar; el que pasa el 85% del límite parpadea. No hay nada más en la escena.
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
      const B = (this.B = base(30)), azar = K.azar(37);
      const ESC = (this.ESC = 0.62), NIVELES = (this.NIVELES = 4), LARGO = (this.LARGO = 48), RUEDA = 0.92, VEL = (this.VEL = 1.0);
      this.nivel = function (k) { return { y: -3.6 + k * 2.0, z: 6.0 - k * 5.2, dir: k % 2 ? -1 : 1 }; };

      // ---- un camión (x hacia adelante): P son posiciones; Q es (tipo, brillo, ángulo, radio). Tipo 1: rueda, que gira. Tipo 2: foco.
      const P = [], Q = [];
      const pt = function (x, y, z, tipo, brillo, ang, radio) { P.push(x, y, z); Q.push(tipo || 0, brillo == null ? 0.4 : brillo, ang || 0, radio || 0); };
      const caja = function (x0, x1, y0, y1, z0, z1, cuantos, brillo) {
        for (let i = 0; i < cuantos; i++) {
          const cara = Math.floor(azar() * 3), u = azar(), v = azar(), lado = azar() < 0.5;
          if (cara === 0) pt(lado ? x0 : x1, K.mezcla(y0, y1, u), K.mezcla(z0, z1, v), 0, brillo);
          else if (cara === 1) pt(K.mezcla(x0, x1, u), lado ? y0 : y1, K.mezcla(z0, z1, v), 0, brillo);
          else pt(K.mezcla(x0, x1, u), K.mezcla(y0, y1, v), lado ? z0 : z1, 0, brillo);
        }
        [[x0, y0], [x1, y0], [x1, y1], [x0, y1]].forEach(function (q, i, lista) {                 // sus aristas, más brillantes
          const r = lista[(i + 1) % 4], largo = Math.hypot(r[0] - q[0], r[1] - q[1]);
          for (let k = 0; k <= largo * 16; k++) { const f = k / (largo * 16); pt(K.mezcla(q[0], r[0], f), K.mezcla(q[1], r[1], f), z0, 0, 0.9); pt(K.mezcla(q[0], r[0], f), K.mezcla(q[1], r[1], f), z1, 0, 0.9); }
        });
      };
      // la tolva, de lado: piso inclinado, pared del frente y la visera que tapa la cabina
      const perfil = [[-2.95, 1.98], [0.15, 1.42], [0.55, 2.86], [2.8, 3.0], [2.8, 3.17], [-3.1, 2.8]];
      const adentro = function (x, y) {
        let si = false;
        for (let i = 0, j = perfil.length - 1; i < perfil.length; j = i++) {
          const a = perfil[i], b = perfil[j];
          if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) si = !si;
        }
        return si;
      };
      for (let i = 0; i < 1500; i++) { let x, y; do { x = -3.1 + azar() * 5.9; y = 1.42 + azar() * 1.75; } while (!adentro(x, y)); pt(x, y, azar() < 0.5 ? -1.56 : 1.56, 0, 0.5); }
      perfil.forEach(function (q, i) {
        const r = perfil[(i + 1) % perfil.length], largo = Math.hypot(r[0] - q[0], r[1] - q[1]);
        for (let k = 0; k < largo * 46; k++) { const f = azar(); pt(K.mezcla(q[0], r[0], f), K.mezcla(q[1], r[1], f), (azar() - 0.5) * 3.12, 0, 0.3); }
        for (let k = 0; k <= largo * 20; k++) { const f = k / (largo * 20); pt(K.mezcla(q[0], r[0], f), K.mezcla(q[1], r[1], f), -1.56, 0, 1); pt(K.mezcla(q[0], r[0], f), K.mezcla(q[1], r[1], f), 1.56, 0, 1); }
      });
      caja(-2.5, 2.45, 0.98, 1.42, -0.95, 0.95, 320, 0.4);                                       // chasis
      caja(1.0, 2.05, 1.42, 2.62, -1.5, 1.5, 420, 0.5);                                          // cabina y plataforma, bajo la visera
      caja(2.05, 2.72, 0.95, 2.25, -1.3, 1.3, 380, 0.5);                                         // frente: radiador y parachoques
      // seis neumáticos enormes: dos adelante, cuatro atrás
      [[1.62, -1.32, 0.56], [1.62, 1.32, 0.56], [-1.38, -0.86, 0.5], [-1.38, -1.44, 0.5], [-1.38, 0.86, 0.5], [-1.38, 1.44, 0.5]].forEach(function (w) {
        for (let i = 0; i < 170; i++) pt(w[0], RUEDA, w[1] + (azar() - 0.5) * w[2], 1, 0.9, azar() * 6.2832, RUEDA);                                  // la banda
        for (let i = 0; i < 200; i++) pt(w[0], RUEDA, w[1] + (w[1] < 0 ? -1 : 1) * w[2] / 2, 1, 0.55, azar() * 6.2832, RUEDA * (0.42 + 0.58 * Math.sqrt(azar())));   // el costado
        for (let k = 0; k < 6; k++) for (let j = 0; j < 5; j++) pt(w[0], RUEDA, w[1] + (w[1] < 0 ? -1 : 1) * w[2] / 2, 1, 0.9, (k / 6) * 6.2832, RUEDA * (0.08 + 0.07 * j));   // los rayos de la llanta: se ve que gira
      });
      pt(2.74, 1.55, -0.9, 2, 1); pt(2.74, 1.55, 0.9, 2, 1);                                      // focos
      const porCamion = P.length / 3, pos = [], aq = [], ac = [], tt = [];
      for (let i = 0; i < n; i++) {
        const col = tinteDe(S, S.unidades[i].id, null) || [0, 0, 0];
        for (let k = 0; k < porCamion; k++) {
          pos.push(P[k * 3], P[k * 3 + 1], P[k * 3 + 2]); aq.push(Q[k * 4], Q[k * 4 + 1], Q[k * 4 + 2], Q[k * 4 + 3]);
          ac.push(i); tt.push(col[0], col[1], col[2]);
        }
      }
      this.cam = { value: [] }; this.est = { value: [] };
      for (let i = 0; i < n; i++) { this.cam.value.push(new THREE.Vector4()); this.est.value.push(new THREE.Vector2()); }
      B.puntos({ position: [pos, 3], aQ: [aq, 4], aCam: [ac, 1], aTinte: [tt, 3] }, `
        attribute vec4 aQ;             // tipo (1: rueda, 2: foco), brillo, y para las ruedas su ángulo y su radio
        attribute float aCam;
        attribute vec3 aTinte;
        uniform vec4 uCam[${n}];       // dónde va cada camión (x, y, z) y hacia dónde mira
        uniform vec2 uEst[${n}];       // su desgaste (0 a 1: 1 es la falla) y cuánto se ve
        uniform float uResp;
        void main() {
          int i = int(aCam + 0.5);
          vec4 c = uCam[i];
          float des = uEst[i].x, rueda = step(0.5, aQ.x) * step(aQ.x, 1.5), foco = step(1.5, aQ.x);
          vec3 p = position;
          float giro = aQ.z - uT * ${(VEL / (RUEDA * ESC)).toFixed(3)};                     // las ruedas giran a la velocidad a la que avanza
          p.x += rueda * aQ.w * cos(giro);
          p.y += rueda * aQ.w * sin(giro);
          float co = cos(c.w), si = sin(c.w);
          vec3 w = vec3(p.x * co - p.z * si, p.y, p.x * si + p.z * co) * ${ESC.toFixed(2)} + c.xyz;
          float frente = mix(0.22, 1.0, smoothstep(-0.5, 0.5, p.x * si + p.z * co));        // el costado que mira a la cámara, encendido; el otro, apagado
          vec3 color = des < 0.5 ? mix(OXIDO, COBRE, des / 0.5) : mix(COBRE, ROJO, smoothstep(0.5, 0.88, des));
          color = mix(color, aTinte, uResp);
          float alerta = smoothstep(0.82, 0.95, des) * (0.5 + 0.5 * sin(uT * 7.0));          // el que está por fallar, parpadea
          vec4 mv = modelViewMatrix * vec4(w, 1.0);
          vColor = foco > 0.5 ? vec3(1.0, 0.95, 0.82) : mix(color, ARENA * 0.9, rueda * 0.55) * (1.0 + 0.9 * alerta);
          vA = uEst[i].y * (foco > 0.5 ? 1.5 : (0.16 + 0.5 * aQ.y) * frente);
          gl_PointSize = (foco > 0.5 ? 0.1 : 0.034 + 0.012 * aQ.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uCam: this.cam, uEst: this.est, uResp: { value: S.respuesta ? 1 : 0 } });

      // ---- la rampa: cuatro niveles; de cada uno se dibujan los dos bordes del camino y la pared que sube al siguiente
      const pr = [], ar = [];
      for (let k = 0; k < NIVELES; k++) {
        const N = this.nivel(k), sig = this.nivel(k + 1);
        for (let x = -LARGO / 2; x < LARGO / 2; x += 0.06) { pr.push(x, N.y, N.z + 1.75, x, N.y, N.z - 1.75); ar.push(1, azar(), 1, azar()); }
        for (let i = 0; i < 1500; i++) { const f = azar(); pr.push((azar() - 0.5) * LARGO, K.mezcla(N.y, sig.y, K.suave(f)), K.mezcla(N.z - 1.75, sig.z + 1.75, f)); ar.push(0, azar()); }
        for (let i = 0; i < 500; i++) { pr.push((azar() - 0.5) * LARGO, N.y, N.z + (azar() - 0.5) * 3.5); ar.push(0, azar()); }
      }
      B.puntos({ position: [pr, 3], aR: [ar, 2] }, `
        attribute vec2 aR;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = ARENA;
          vA = (0.16 + 0.34 * aR.x + 0.1 * aR.y) * smoothstep(${(LARGO / 2).toFixed(1)}, ${(LARGO / 2 - 6).toFixed(1)}, abs(position.x));
          gl_PointSize = (0.035 + 0.02 * aR.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`);
      this.etq = etiquetas(L, 2, 'nota');
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      const S = this.S, h = recorrido(t - 0.6, 12, 5) * this.horas;
      reloj(this.reloj, K.miles(Math.floor(h / 10) * 10) + ' h');
      if (!this.tres) return;
      const B = this.B, orden = [], paso = this.LARGO / Math.ceil(this.n / this.NIVELES);
      B.u.uT.value = t;
      B.mirar(-0.4 + Math.sin(t * 0.13) * 0.04, 0.2, 26, [4.6, -0.9, -1.0], -450);
      for (let i = 0; i < this.n; i++) {
        const des = K.acotar(leer(S.unidades[i].puntos, h, 0) / this.falla, 0, 1);
        const N = this.nivel(i % this.NIVELES), j = Math.floor(i / this.NIVELES);
        const x = ((((j * paso + N.dir * this.VEL * t + (i % this.NIVELES) * 1.7) % this.LARGO) + this.LARGO) % this.LARGO) - this.LARGO / 2;
        this.cam.value[i].set(x, N.y, N.z, N.dir > 0 ? 0 : Math.PI);
        this.est.value[i].set(des, K.acotar((this.LARGO / 2 - Math.abs(x)) / 5, 0, 1));
        orden.push([des, i, x, N]);
      }
      // las etiquetas siguen a los dos camiones más gastados que estén a la vista, lejos del texto y del reloj
      orden.sort(function (a, b) { return b[0] - a[0]; });
      let puestas = 0;
      for (let k = 0; k < orden.length && puestas < this.etq.length; k++) {
        const o = orden[k], y = o[3].y + 3.35 * this.ESC, q = K.proyectar(o[2], y, o[3].z, B.camera);
        if (o[0] < 0.8 || q.x < 1020 || q.x > 1560 || q.y < 190 || q.y > 980) continue;
        if (puestas && Math.abs(q.x - this._x0) < 380 && Math.abs(q.y - this._y0) < 150) continue;       // que no se pisen entre sí
        if (!puestas) { this._x0 = q.x; this._y0 = q.y; }
        poner(this.etq[puestas++], B.camera, o[2], y, o[3].z, '<b>' + nombre(S.unidades[o[1]].id) + '</b>cerca de fallar', true);
      }
      for (; puestas < this.etq.length; puestas++) this.etq[puestas].classList.remove('ver');
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
      B.cordon(principal, 0.045, 0x8a7f70, 0.42, 0.034);
      this.sector = [];
      const pe = [], dir = [], ev = [];
      this.eventos = [];
      for (let k = 0; k < n; k++) {
        const x = -6.6 + Math.floor(k / 2) * 4.4, lado = k % 2 ? 1 : -1, v = [];
        for (let j = 0; j <= 7; j++) arco(v, x, -0.5, lado * (0.95 + j * (LARGO / 7)), 0.7, false);
        v.push(x - 0.7, -0.5, lado * 0.95, x - 0.7, -0.5, lado * (0.95 + LARGO), x + 0.7, -0.5, lado * 0.95, x + 0.7, -0.5, lado * (0.95 + LARGO));
        const tunel = B.cordon(v, 0.045, 0x8a7f70, 0.5, 0.04), tinte = tinteDe(S, S.unidades[k].id, null);
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
          gl_PointSize = mix((0.15 + 0.3 * mag + 0.24 * fuerte) * (1.0 + 1.5 * exp(-edad * 3.0)), 0.07 + 0.07 * mag + 0.08 * fuerte, onda) * uEsc / -mv.z;
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
      B.mirar(0.42 + Math.sin(t * 0.16) * 0.07, 0.55, 40, [0.2, 0.0, 0], -410);
      const segPorHora = DURA / this.horas;
      for (let i = 0; i < this.n; i++) {
        const s = this.sector[i];
        let cuenta = 0, actividad = 0;
        for (let j = 0; j < s.horas.length; j++) if (s.horas[j] <= h) { cuenta++; actividad += Math.exp(-((h - s.horas[j]) * segPorHora + this.extra.value) / 1.1); }
        const a = K.acotar(actividad, 0, 1);
        if (s.tinte) s.linea.color.setRGB(s.tinte[0], s.tinte[1], s.tinte[2]);
        else s.linea.color.copy(this.gris).lerp(this.vivo, a);
        s.linea.alfa.value = 0.4 + 0.5 * a;
      }
      for (let i = 0; i < this.etqFuerte.length; i++) {
        const e = this.eventos[i];
        poner(this.etqFuerte[i], B.camera, e.c[0], e.c[1], e.c[2], '<b>Magnitud ' + K.coma(e.mag, 1) + '</b>temblor fuerte', h >= e.hora);
      }
      poner(this.etqFrente, B.camera, this.frente[0], this.frente[1] + 0.9, this.frente[2], '<b>Explosión</b>hora cero', h > 0 && h < this.horas * 0.14);
    },
  });
})();
