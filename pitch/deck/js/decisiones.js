/* 8 y 10 · La pared y los camiones, cada una como una escena hecha de puntos que se mueve con los datos del archivo de
   su caso (datos.js → series), y lo común a las escenas de las decisiones (K.d3, K.base3d, K.camionDePuntos):
   - taludes: la pared del rajo, partida en sus sectores; cada sector se desplaza lo que el radar midió, hora a hora;
   - flota: los camiones en la rampa, cada uno en el color de su decisión.
   La planta (9) y los túneles (11) viven en flotacion.js y sismicidad.js. En todas, el foco de Krylov viaja de unidad
   en unidad y su tarjeta muestra la respuesta de la red para la que se está mirando (js/foco.js). */
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
  // Los colores de las decisiones para los lienzos 2D y las tarjetas: los tokens de :root (deck.css). Un rojo y un verde.
  const token = function (nombre, respaldo) { return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim() || respaldo; };
  const COLOR_CSS = (K.coloresDecision = { actuar: token('--actuar', '#e4603c'), en_duda: token('--en-duda', '#eec25a'), no_actuar: token('--no-actuar', '#1fa87a') });

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
  // La columna de texto de cada decisión: lo que Krylov entrega.
  //   El gráfico: la estimación de cada unidad con su intervalo de credibilidad de 90% (js/intervalos.js).
  //   Los colores: en cuántas unidades conviene actuar, en cuántas no se sabe y en cuántas no hace falta.
  //   El valor: lo que cuesta no saber, que es lo que vale despejar esa duda.
  // Los números aparecen solo si el motor del caso respondió (series.<caso>.respuesta); si no, quedan los rótulos.
  function llenar(L, S) { L.classList.toggle('con-respuesta', !!S.respuesta); }
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
  function reloj(el, texto) { if (el && el._h !== texto) { el.textContent = texto; el._h = texto; } }

  // Un camión minero hecho de puntos sobre su carrocería (x hacia adelante). P son posiciones; Q es (tipo, brillo, ángulo, radio).
  // Tipo 1: rueda, que gira. Tipo 2: foco. Lo usan la lámina de la flota y la portada.
  function camionDePuntos(azar, RUEDA) {
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
      return { P: P, Q: Q };
  }
  K.camionDePuntos = camionDePuntos;
  K.base3d = base;
  // lo común, para las escenas que viven en su propio archivo (flotacion.js, sismicidad.js)
  K.d3 = { base: base, recorrido: recorrido, leer: leer, tinteDe: tinteDe, etiquetas: etiquetas, poner: poner, nombre: nombre, DECISION: DECISION, COLOR_CSS: COLOR_CSS };

  // ============================== 8 · Taludes: la pared de la minera ==============================
  // La pared del rajo, vista desde el otro lado: ocho escalones de roca, partida en los 36 sectores del archivo.
  // Cada sector se abulta lo que el radar midió a esa hora (el movimiento está exagerado para que se vea) y lleva el color
  // de su decisión. Abajo, el radar y sus haces barren la pared una y otra vez.
  // El foco de Krylov viaja de sector en sector (js/foco.js). Cuando se detiene en uno que conviene cerrar, la escena
  // proyecta lo que viene si sigue acelerando: ese tramo de la pared se desliza y se desgrana. Es una proyección, y lo dice.
  K.registrar('taludes', {
    tres: null, tQuieto: 14,
    crear: function (L) {
      const S = (this.S = K.datos.series.taludes), n = (this.n = S.unidades.length), R = S.respuesta;
      llenar(L, S);
      this.horas = 0; this.maximo = 0;
      S.unidades.forEach(function (un) { un.puntos.forEach(function (q) { this.horas = Math.max(this.horas, q[0]); this.maximo = Math.max(this.maximo, q[1]); }, this); }, this);
      this.indice = {}; S.unidades.forEach(function (un, i) { this.indice[un.id] = i; }, this);
      // El recorrido del foco: un sector que conviene cerrar, el que más se movió sin que haga falta cerrarlo, el que está
      // en duda, otro que conviene cerrar y el más quieto. Los que no se aceleran no tienen «horas que faltan»:
      // su tarjeta muestra lo que midió el radar.
      const F = (this.F = K.foco.crear(L, 'taludes')), finales = S.unidades.map(function (un, i) { return [un.puntos[un.puntos.length - 1][1], i]; }).sort(function (x, y) { return y[0] - x[0]; });
      const con = S.unidades.map(function (un) { return un.id; }).filter(function (id) { return R.posteriori[id]; });
      const rojos = con.filter(function (id) { return R.unidades[id].estado === 'actuar'; }).sort(function (x, y) { return R.posteriori[x].medio - R.posteriori[y].medio; });
      const duda = con.filter(function (id) { return R.unidades[id].estado === 'en_duda'; });
      const verdes = finales.map(function (f) { return S.unidades[f[1]].id; }).filter(function (id) { return R.unidades[id] && R.unidades[id].estado === 'no_actuar'; });
      K.foco.recorrer(F, con);
      // el eje llega hasta las 36 horas del gráfico del caso: el sector en duda tiene un rango ancho y tiene que caber
      F.eje = { min: 0, max: 36, log: false, raiz: false, limite: S.horizonte };
      con.forEach(function (id) { F.fichas[id] = K.foco.ficha('taludes', id, F.eje); });
      const sinCurva = function (id, que) {
        const un = S.unidades[this.indice[id]], mm = un.puntos[un.puntos.length - 1][1];
        F.fichas[id] = { id: id, nombre: K.nombreDe(id), estado: 'no_actuar', decision: S.rotulos.no_actuar, color: K.foco.rgb(COLOR_CSS.no_actuar),
          grande: K.coma(Math.max(0, mm), mm >= 10 ? 0 : 1).replace(',0', '') + ' mm', que: que, serie: un.puntos, tope: this.maximo, rotuloSerie: 'Lo que midió el radar en ' + Math.round(this.horas) + ' horas' };
      }.bind(this);
      const movido = verdes[0], quieto = verdes[verdes.length - 1];
      if (movido) sinCurva(movido, 'se movió, pero a ritmo parejo: no se está acelerando');
      if (quieto && quieto !== movido) sinCurva(quieto, 'se movió: está quieto');
      F.ids = [rojos[0], movido, duda[0], rojos[1], quieto].filter(function (id) { return id && F.fichas[id]; });
      K.foco.reiniciar(F);
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
        const col = tinteDe(S, S.unidades[s].id, ROJO), r0 = R && R.unidades[S.unidades[s].id];
        const enf = r0 && r0.estado !== 'no_actuar' ? 1 : 0;          // lo que conviene cerrar y lo que está en duda se enciende, se haya movido mucho o poco
        for (let c = 0; c < 16; c++) for (let f = 0; f < 104; f++) {
          const ux = (s + (c + azar()) / 16) / n, v = (f + azar()) / 104, r = (v * BANCOS) % 1;
          // la cara de roca recibe la luz; el piso de cada escalón queda en sombra
          poner3(ux, v, r < PIE ? 0.16 + 0.1 * azar() : 0.5 + 0.5 * K.acotar(0.5 + 1.6 * ruido(ux * 40, v * 30), 0, 1), 0, col, enf);
        }
        for (let b = 0; b < BANCOS; b++) for (let k = 0; k < 26; k++) poner3((s + azar()) / n, (b + 0.985 + azar() * 0.014) / BANCOS, 1.25, 0, col, enf);      // el borde de cada escalón
      }
      // las divisiones entre sectores, tenues; las del sector que se mira se encienden (en el sombreador)
      for (let s = 0; s <= n; s++) for (let k = 0; k < 150; k++) poner3(Math.min(0.9999, s / n), (k + 0.5) / 150, 1, 1, [0, 0, 0]);
      // cuánto se ha movido cada sector ahora: una fila de textura. R: lo medido (color). G: lo mismo, suavizado entre vecinos (forma).
      this.mov = new Uint8Array(n * 4);
      this.tex = new THREE.DataTexture(this.mov, n, 1, THREE.RGBAFormat);
      this.tex.magFilter = this.tex.minFilter = THREE.LinearFilter;
      this.tex.needsUpdate = true;
      this.barre = { value: -1 };
      this.foc = { value: new THREE.Vector3(-1, -1, 0) };            // el sector que se mira, el que viene y el avance de uno al otro
      this.cede = { value: new THREE.Vector2(-1, 0) };               // el sector cuya caída se proyecta, y cuánto ha cedido (0 a 1)
      B.puntos({ position: [pos, 3], aU: [au, 2], aS: [as, 4], aTinte: [tinte, 3] }, `
        attribute vec2 aU;             // dónde está en la pared: a lo largo (0 a 1) y hacia arriba (0 a 1)
        attribute vec4 aS;             // luz, azar, si es una división entre sectores, y si su decisión se destaca
        attribute vec3 aTinte;
        uniform sampler2D uMov;
        uniform float uBarre;
        uniform float uResp;
        uniform vec3 uFoc;
        uniform vec2 uCede;
        void main() {
          vec4 m = texture2D(uMov, vec2(aU.x, 0.5));
          float d = m.r, g = m.g, lado = (aU.x - 0.5) * 2.0, sec = aU.x * ${n.toFixed(1)};
          float marca = aS.z;
          float miraA = 1.0 - step(marca > 0.5 ? 0.62 : 0.5, abs(sec - (uFoc.x + 0.5)));
          float miraB = 1.0 - step(marca > 0.5 ? 0.62 : 0.5, abs(sec - (uFoc.y + 0.5)));
          float mira = miraA * (1.0 - uFoc.z) + miraB * uFoc.z;
          float dv = (aU.y - 0.36) / 0.36;
          float afuera = g * (0.3 + 0.7 * exp(-dv * dv));                  // la parte baja se abulta hacia el rajo
          float baja = g * (0.2 + 0.8 * aU.y);                             // la parte alta se hunde
          vec3 p = position + vec3(-lado * 0.3, 0.0, 1.0) * afuera * 1.15 + vec3(0.0, -0.5, 0.0) * baja;
          // la proyección: el tramo que se mira se desliza hacia el rajo y se desgrana (lo de arriba baja más; los fragmentos caen)
          float c = uCede.y * (1.0 - step(0.5, abs(sec - (uCede.x + 0.5)))) * step(marca, 0.5);
          float borde = 1.0 - smoothstep(0.30, 0.5, abs(fract(sec) - 0.5));  // el tramo se rompe más en el centro que en sus orillas
          float canto = step(1.2, aS.x);                                    // el borde encendido de cada escalón
          float desliza = c * (0.3 + 0.9 * aU.y) * (0.5 + 0.5 * borde);
          float suelta = step(0.72, aS.y) * c * c;
          // el tramo baja más de un escalón y sus fragmentos se abren en abanico al pie
          p += vec3(-lado * 0.2, -1.2, 0.9) * desliza + vec3((aS.y - 0.86) * 5.0, -3.0 * aS.y, 1.7 * aS.y) * suelta * (0.4 + 0.6 * aU.y);
          float dr = (aU.x - uBarre) / 0.008;
          float radar = exp(-dr * dr) + (aU.x < uBarre ? 0.3 * exp(-(uBarre - aU.x) / 0.06) : 0.0);    // la franja del radar y su estela
          radar *= 1.0 - 0.85 * uCede.y;                                    // mientras se proyecta la caída, el barrido no compite
          float k = max(smoothstep(0.04, 0.42, d) * mix(1.0, 0.45, uResp), 0.75 * aS.w * uResp);        // con respuesta manda la decisión, no cuánto se movió
          k = max(k, 0.9 * mira);
          vec3 caliente = mix(mix(COBRE, ROJO, smoothstep(0.18, 0.55, d)), vec3(1.0, 0.88, 0.74), smoothstep(0.6, 1.0, d));
          vec3 color = mix(mix(ARENA * 0.92, aTinte, uResp * 0.7), mix(caliente, aTinte, uResp), k);
          color = mix(color, vec3(1.0, 0.66, 0.42), 0.45 * c);
          color = mix(color, vec3(1.0, 0.9, 0.78), 0.55 * suelta);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = marca > 0.5 ? vec3(0.96, 0.93, 0.88) : color + ORO * radar * 0.85;
          vA = marca > 0.5 ? mix(0.06, 0.6, mira) : (0.07 + 0.3 * aS.x) * (1.0 + 1.6 * k) * mix(0.72, 1.25, mira) + radar * 0.6;
          // donde cede, los escalones se cortan y arriba queda la cicatriz oscura
          vA *= (1.0 - 0.92 * c * canto) * (1.0 - 0.7 * c * smoothstep(0.45, 0.95, aU.y) * (1.0 - step(0.72, aS.y)));
          gl_PointSize = (marca > 0.5 ? 0.028 : 0.03 + 0.016 * aS.y + 0.022 * k + 0.035 * radar) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uMov: { value: this.tex }, uBarre: this.barre, uResp: { value: R ? 1 : 0 }, uFoc: this.foc, uCede: this.cede });

      // el radar, al otro lado del rajo: se ubica una vez, donde la cámara lo ve abajo a la derecha
      this.encuadre = { az: 0.5, el: 0.2, R: 37, c: [1.0, 3.1, 0.6], dx: -420 };
      B.mirar(this.encuadre.az, this.encuadre.el, this.encuadre.R, this.encuadre.c, this.encuadre.dx);
      const rayo = new THREE.Vector3(0.34, -0.66, 0.5).unproject(B.camera).sub(B.camera.position).normalize();
      const Rd = (this.radar = B.camera.position.clone().add(rayo.multiplyScalar(15)).toArray());
      const pr = [];
      for (let k = 0; k < 26; k++) pr.push(Rd[0], Rd[1] - 1.3 + (k / 25) * 1.3, Rd[2]);                          // el poste
      for (let k = 0; k < 44; k++) { const a = (k / 44) * 6.2832; pr.push(Rd[0] + Math.cos(a) * 0.34, Rd[1] + Math.sin(a) * 0.34, Rd[2]); }   // la antena
      for (let k = 0; k < 30; k++) { const a = azar() * 6.2832, q = Math.sqrt(azar()) * 0.32; pr.push(Rd[0] + Math.cos(a) * q, Rd[1] + Math.sin(a) * q, Rd[2]); }
      this.radAlfa = { value: 1 };
      B.puntos({ position: [pr, 3] }, `
        uniform float uRad;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = ORO;
          vA = 0.8 * uRad;
          gl_PointSize = 0.05 * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uRad: this.radAlfa });
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
      this.etqCede = etiquetas(L, 1, 'nota')[0];
      this.etqCede.classList.add('proyeccion');
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); if (this.F) K.foco.ajustar(this.F); },
    entrar: function () { if (this.F) K.foco.reiniciar(this.F); this._cede = 0; },
    cuadro: function (t, dt) {
      const S = this.S, n = this.n, F = this.F, yo = this, DURA = 8, ESPERA = 8, k = recorrido(t - 0.8, DURA, ESPERA), h = k * this.horas;
      if (!this.tres) { K.foco.cuadro(F, t, function () { return null; }); return; }
      const B = this.B, E = this.encuadre, ahora = [];
      for (let s = 0; s < n; s++) ahora[s] = leer(S.unidades[s].puntos, h, 0);
      let crudo = ahora.map(function (v) { return K.acotar(v / this.maximo, 0, 1); }, this), liso = crudo;
      for (let vez = 0; vez < 4; vez++) liso = liso.map(function (v, s, lista) { return (lista[Math.max(0, s - 1)] + 2 * v + lista[Math.min(n - 1, s + 1)]) / 4; });
      for (let s = 0; s < n; s++) { this.mov[s * 4] = Math.round(crudo[s] * 255); this.mov[s * 4 + 1] = Math.round(liso[s] * 255); }
      this.tex.needsUpdate = true;
      B.u.uT.value = t;
      const ux = (this.barre.value = ((t * 0.2) % 1.25) - 0.12);              // el barrido del radar
      // la cámara acompaña al foco: gira un poco hacia el sector que se mira
      const ia = this.indice[F.a], ib = F.b == null ? ia : this.indice[F.b], centro = K.mezcla(ia, ib, F.e) / n - 0.5;
      // …y se acerca cuando proyecta cómo cede
      const qx = this.pared(K.acotar(centro + 0.5, 0, 0.999), 0.6), cerca = this._cede || 0;
      B.mirar(E.az + Math.sin(t * 0.17) * 0.03 - centro * 0.3, E.el, E.R - 1.6 - 9 * cerca, [K.mezcla(E.c[0], qx[0], 0.45 + 0.35 * cerca), E.c[1] - 1.0 * cerca, E.c[2]], E.dx);
      const ph = this.haces.geometry.attributes.position, Rd = this.radar;
      this.haces.visible = ux >= 0 && ux <= 1 && (this._cede || 0) < 0.12;
      this.radAlfa.value = 1 - K.suave((this._cede || 0) / 0.2);            // el radar se apaga antes de que el acercamiento lo corte
      if (this.haces.visible) {
        for (let i = 0; i < this.HACES; i++) {
          const q = this.pared(ux, (i + 0.5) / this.HACES);
          for (let j = 0; j < this.TRAMOS; j++) {
            const f = (j + 0.5) / this.TRAMOS, o = (i * this.TRAMOS + j) * 3;
            ph.array[o] = K.mezcla(Rd[0], q[0], f); ph.array[o + 1] = K.mezcla(Rd[1], q[1], f); ph.array[o + 2] = K.mezcla(Rd[2], q[2], f);
          }
        }
        ph.needsUpdate = true;
      }
      poner(this.etqRadar, B.camera, Rd[0] + 0.5, Rd[1], Rd[2], '<b>Radar</b>', (this._cede || 0) < 0.08);
      // el foco y su tarjeta
      const punto = function (id) { const q = yo.pared((yo.indice[id] + 0.5) / n, 0.62); return K.proyectar(q[0], q[1], q[2], B.camera); };
      K.foco.cuadro(F, t, punto, 4.6, 1.2);
      this.foc.value.set(ia, F.b == null ? -1 : ib, F.e);
      // la proyección: mientras el foco está detenido en un sector que conviene cerrar, ese tramo cede; al irse, vuelve
      const estado = F.fichas[F.a].estado, cuanto = estado === 'actuar' ? 1 : estado === 'en_duda' ? 0.22 : 0;
      const meta = K.quieto ? cuanto * 0.8 : F.b == null ? cuanto * K.suave((t - 1.6 - F.t0 - 0.7) / 2.6) : 0;
      this._cede = K.quieto ? meta : this._cede + (meta - this._cede) * Math.min(1, (dt || 0) * (meta > this._cede ? 6 : 3.2));
      this.cede.value.set(ia, this._cede);
      const qc = this.pared((ia + 0.5) / n, 0.9);
      poner(this.etqCede, B.camera, qc[0], qc[1], qc[2] + 0.4, '<b>Proyección</b>así cede si sigue acelerando', estado === 'actuar' && this._cede > 0.25 && F.b == null);
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
      llenar(L, S, 'flota');
      this.reloj = L.querySelector('.reloj .num');
      this.horas = 0;
      S.unidades.forEach(function (un) { this.horas = Math.max(this.horas, un.puntos[un.puntos.length - 1][0]); }, this);
      this.falla = S.umbral || 1;
      // el foco viaja de camión en camión; su tarjeta muestra el riesgo de cada uno con su distribución (js/foco.js)
      this.F = K.foco.crear(L, 'flota');
      K.foco.recorrer(this.F, S.unidades.map(function (un) { return un.id; }));
      this.indice = {}; S.unidades.forEach(function (un, i) { this.indice[un.id] = i; }, this);
      this.pos = []; this.vistos = [];
      if (!K.gl.ok) return;
      const B = (this.B = base(30)), azar = K.azar(37);
      const ESC = (this.ESC = 0.62), NIVELES = (this.NIVELES = 4), LARGO = (this.LARGO = 48), RUEDA = 0.92, VEL = (this.VEL = 1.0);
      this.nivel = function (k) { return { y: -3.6 + k * 2.0, z: 6.0 - k * 5.2, dir: k % 2 ? -1 : 1 }; };

      const modelo = camionDePuntos(azar, RUEDA), P = modelo.P, Q = modelo.Q;
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
        uniform vec3 uFoc;             // el camión que se está mirando, el que viene y cuánto se ha avanzado de uno al otro
        void main() {
          int i = int(aCam + 0.5);
          float mira = (abs(aCam - uFoc.x) < 0.5 ? 1.0 - uFoc.z : 0.0) + (abs(aCam - uFoc.y) < 0.5 ? uFoc.z : 0.0);
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
          vA = uEst[i].y * (foco > 0.5 ? 1.5 : (0.16 + 0.5 * aQ.y) * frente) * mix(0.5, 1.9, mira);
          gl_PointSize = (foco > 0.5 ? 0.1 : 0.034 + 0.012 * aQ.y + 0.012 * mira) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uCam: this.cam, uEst: this.est, uResp: { value: S.respuesta ? 1 : 0 }, uFoc: (this.foc = { value: new THREE.Vector3(-1, -1, 0) }) });

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
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); if (this.F) K.foco.ajustar(this.F); },
    entrar: function () { if (this.F) { K.foco.reiniciar(this.F); this._ini = false; this.vistos = []; } },
    cuadro: function (t) {
      const S = this.S, F = this.F, yo = this, h = recorrido(t - 0.6, 12, 5) * this.horas;
      if (!this.tres) { K.foco.cuadro(F, t, function () { return null; }); return; }
      const B = this.B, paso = this.LARGO / Math.ceil(this.n / this.NIVELES), borde = this.LARGO / 2 - 5;
      B.u.uT.value = t;
      B.mirar(-0.4 + Math.sin(t * 0.13) * 0.04, 0.2, 26, [4.6, -0.9, -1.0], -450);
      for (let i = 0; i < this.n; i++) {
        const des = K.acotar(leer(S.unidades[i].puntos, h, 0) / this.falla, 0, 1);
        const N = this.nivel(i % this.NIVELES), j = Math.floor(i / this.NIVELES);
        const x = ((((j * paso + N.dir * this.VEL * t + (i % this.NIVELES) * 1.7) % this.LARGO) + this.LARGO) % this.LARGO) - this.LARGO / 2;
        this.cam.value[i].set(x, N.y, N.z, N.dir > 0 ? 0 : Math.PI);
        this.est.value[i].set(des, K.acotar((this.LARGO / 2 - Math.abs(x)) / 5, 0, 1));
        // dónde está en la pantalla, y si va a seguir a la vista el rato que dura una parada del foco
        const q = K.proyectar(x, N.y + 2.0 * this.ESC, N.z, B.camera), xd = x + N.dir * this.VEL * 4.3, qd = K.proyectar(xd, N.y + 2.0 * this.ESC, N.z, B.camera);
        const p = this.pos[i] || (this.pos[i] = {});
        // se puede mirar si está entero a la derecha de la columna, y si va a seguir ahí lo que dura una parada (3 s) y el viaje
        p.x = q.x; p.y = q.y; p.ve = Math.abs(x) < borde && q.x > 1120 && q.x < 1800 && q.y > 130 && q.y < 960;
        p.ok = p.ve && Math.abs(xd) < borde && q.x > 1200 && q.x < 1740 && qd.x > 1200 && qd.x < 1740 && q.y > 170 && q.y < 900;
      }
      // El foco elige el camión siguiente entre los que están a la vista: cambia de color de decisión cuando puede,
      // y no repite los últimos que mostró.
      const R = S.respuesta.unidades;
      const elegir = function (actual) {
        let mejor = null, nota = -1;
        for (let i = 0; i < yo.n; i++) {
          const id = S.unidades[i].id, p = yo.pos[i];
          if (!p.ok || id === actual || yo.vistos.indexOf(id) >= 0 || !F.fichas[id]) continue;
          const e = R[id].estado, v = (actual && e !== R[actual].estado ? 4 : 0) + (e === 'en_duda' ? 3 : e === 'actuar' ? 2 : 0) + 1 - Math.abs(p.x - 1480) / 900;
          if (v > nota) { nota = v; mejor = id; }
        }
        if (mejor) { yo.vistos.push(mejor); if (yo.vistos.length > 7) yo.vistos.shift(); }
        return mejor;
      };
      // al entrar, y si el que se miraba sale del cuadro, el foco se pone en otro sin viaje: no hay de dónde venir
      if (F.b == null && (!this._ini || !this.pos[this.indice[F.a]].ve)) { const id = elegir(this._ini ? F.a : null); if (id) { F.a = id; F.t0 = Math.max(0, t - 1.6); this._ini = true; } }
      K.foco.cuadro(F, t, function (id) { return yo.pos[yo.indice[id]]; }, 3.0, 1.0, elegir);
      this.foc.value.set(this.indice[F.a], F.b == null ? -1 : this.indice[F.b], F.e);
    },
  });

})();
