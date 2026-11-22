/* 4 · El mapa   y   5 · ¿Dónde mido?
   El terreno real como una superficie topográfica. Altura = metal estimado; color = decisión; curvas de nivel cada 100 mg/kg;
   línea blanca = el nivel que obliga a actuar; malla de arriba = tope del rango creíble; puntos blancos = las mediciones reales.
   Todo sale de datos.js (api.analizar, api.donde_medir y los mapas rehechos por la red). La superficie se dibuja interpolando
   entre los bloques del motor. Las dos láminas comparten la escena. */
(function () {
  'use strict';
  const K = window.K;
  let F = 0.0052;                      // unidades de escena por unidad del caso; se ajusta al construir
  const TOPE = 15;                     // altura máxima de la malla y de los puntos, en unidades de escena
  const M = 192;                       // lado de la rejilla fina con que se dibuja la superficie
  let E = null;

  // ---------- de los bloques del motor a una rejilla suave ----------
  function rejilla(T, capa) {
    const N = T.nx, lleno = new Uint8Array(N * N);
    const g = { media: new Float32Array(N * N), alto: new Float32Array(N * N), p: new Float32Array(N * N) }, claves = ['media', 'alto', 'p'];
    T.dentro.forEach(function (idx, i) { lleno[idx] = 1; claves.forEach(function (k) { g[k][idx] = capa[k][i]; }); });
    const masc = Float32Array.from(lleno);
    // Fuera del terreno se repite el valor del bloque más cercano, para que el borde no se caiga.
    for (let vuelta = 0, falta = true; falta && vuelta < 64; vuelta++) {
      falta = false;
      const nuevos = [];
      for (let f = 0; f < N; f++) for (let c = 0; c < N; c++) {
        const i = f * N + c;
        if (lleno[i]) continue;
        let n = 0; const suma = [0, 0, 0];
        for (let df = -1; df <= 1; df++) for (let dc = -1; dc <= 1; dc++) {
          const ff = f + df, cc = c + dc;
          if (ff < 0 || cc < 0 || ff >= N || cc >= N || !lleno[ff * N + cc]) continue;
          n++; claves.forEach(function (k, q) { suma[q] += g[k][ff * N + cc]; });
        }
        if (n) nuevos.push([i, suma[0] / n, suma[1] / n, suma[2] / n]); else falta = true;
      }
      nuevos.forEach(function (v) { lleno[v[0]] = 1; g.media[v[0]] = v[1]; g.alto[v[0]] = v[2]; g.p[v[0]] = v[3]; });
    }
    const subir = function (a) {
      const s = new Float32Array(M * M);
      for (let y = 0; y < M; y++) {
        const fy = K.acotar(((y + 0.5) / M) * N - 0.5, 0, N - 1), y0 = Math.floor(fy), y1 = Math.min(N - 1, y0 + 1), ty = fy - y0;
        for (let x = 0; x < M; x++) {
          const fx = K.acotar(((x + 0.5) / M) * N - 0.5, 0, N - 1), x0 = Math.floor(fx), x1 = Math.min(N - 1, x0 + 1), tx = fx - x0;
          s[y * M + x] = (a[y0 * N + x0] * (1 - tx) + a[y0 * N + x1] * tx) * (1 - ty) + (a[y1 * N + x0] * (1 - tx) + a[y1 * N + x1] * tx) * ty;
        }
      }
      return s;
    };
    const difuminar = function (a, radio, pasadas) {
      let o = a, t = new Float32Array(M * M);
      for (let k = 0; k < pasadas * 2; k++) {
        const horizontal = k % 2 === 0;
        for (let y = 0; y < M; y++) for (let x = 0; x < M; x++) {
          let s = 0;
          for (let d = -radio; d <= radio; d++) {
            const xx = horizontal ? K.acotar(x + d, 0, M - 1) : x, yy = horizontal ? y : K.acotar(y + d, 0, M - 1);
            s += o[yy * M + xx];
          }
          t[y * M + x] = s / (2 * radio + 1);
        }
        const cambio = o === a ? new Float32Array(M * M) : o; o = t; t = cambio;
      }
      return o;
    };
    return { media: difuminar(subir(g.media), 3, 2), alto: difuminar(subir(g.alto), 3, 2), p: difuminar(subir(g.p), 2, 1), masc: difuminar(subir(masc), 2, 1) };
  }
  K.rejilla = function (T, capa) { T = T || K.datos.terreno; return rejilla(T, capa || T); };
  K.rejillaLado = M;

  const VERT = `
    uniform sampler2D uA;
    uniform sampler2D uB;
    uniform float uMorf, uCrece, uAlt, uTecho;
    uniform vec2 uPin;
    uniform vec2 uCentro;
    varying vec2 vUv;
    varying vec3 vP;
    varying float vK;
    varying float vCrece;
    void main() {
      vUv = uv;
      float frente = uMorf * 1.9 - distance(position.xz, uPin) / 16.0 * 0.9;
      float k = clamp(frente, 0.0, 1.0);
      k = k * k * (3.0 - 2.0 * k);
      vec4 d = mix(texture2D(uA, uv), texture2D(uB, uv), k);
      float crece = clamp(uCrece * 1.7 - length(position.xz - uCentro) / 20.0 * 0.7, 0.0, 1.0);
      crece = 1.0 - pow(1.0 - crece, 3.0);
      float h = mix(d.r, d.g, uTecho) * uAlt * crece;
      float onda = sin(clamp(frente, 0.0, 1.0) * 3.14159) * 0.45 * step(0.0005, uMorf) * step(uMorf, 0.9995);
      vec3 p = vec3(position.x, h + onda, position.z);
      vP = p; vK = k; vCrece = crece;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
    }`;

  const ZONAS = `
    uniform float uDuda;
    const vec3 C_ACTUAR = vec3(0.90, 0.38, 0.23);     // rojo cobre
    const vec3 C_BIEN = vec3(0.10, 0.62, 0.44);       // verde malaquita
    const vec3 C_DUDA = vec3(0.94, 0.76, 0.35);       // oro
    float zona(float p, float w) {                    // +1 actuar, 0 en duda, −1 no hace falta
      return smoothstep(1.0 - uDuda - w, 1.0 - uDuda + w, p) - (1.0 - smoothstep(uDuda - w, uDuda + w, p));
    }`;

  const FRAG = `
    precision highp float;
    uniform sampler2D uA;
    uniform sampler2D uB;
    uniform float uMax, uUmbral, uT, uColor;
    varying vec2 vUv;
    varying vec3 vP;
    varying float vK;
    varying float vCrece;
    ${ZONAS}
    void main() {
      vec4 a = texture2D(uA, vUv), b = texture2D(uB, vUv), d = mix(a, b, vK);
      if (d.a < 0.5) discard;
      float mg = d.r * uMax, w = fwidth(d.b) * 1.2 + 0.004;
      float z = zona(d.b, w);
      float raya = smoothstep(0.40, 0.60, abs(fract((vP.x + vP.z) * 1.1 - uT * 0.1) - 0.5) * 2.0);
      vec3 c = mix(C_DUDA, C_DUDA * 0.46, raya);
      c = mix(c, C_ACTUAR, max(z, 0.0));
      c = mix(c, C_BIEN, max(-z, 0.0));
      vec3 n = normalize(cross(dFdx(vP), dFdy(vP)));
      if (n.y < 0.0) n = -n;
      float luz = 0.52 + 0.62 * max(dot(n, normalize(vec3(0.5, 0.75, 0.42))), 0.0);
      // curvas de nivel cada 100 mg/kg, y más marcada cada 500
      float f = mg / 100.0, ancho = fwidth(f);
      float curva = 1.0 - smoothstep(0.0, 1.3, abs(fract(f - 0.5) - 0.5) / ancho);
      float g = mg / 500.0;
      float mayor = 1.0 - smoothstep(0.0, 2.0, abs(fract(g - 0.5) - 0.5) / fwidth(g));
      c = c * luz * (1.0 - 0.42 * curva - 0.25 * mayor);
      // lo que cambió de decisión al rehacer el mapa, destella
      float cambio = clamp(abs(zona(a.b, 0.02) - zona(b.b, 0.02)), 0.0, 1.0) * sin(3.14159 * vK);
      float pinta = uColor * smoothstep(0.0, 0.3, vCrece);
      c = mix(vec3(0.16, 0.15, 0.14), c, pinta);
      float corte = (1.0 - smoothstep(0.7, 2.0, abs(mg - uUmbral) / fwidth(mg))) * pinta;
      c = mix(c, vec3(1.0), corte) + vec3(1.0, 0.95, 0.8) * cambio * 0.8;
      c *= 0.62 + 0.38 * smoothstep(0.5, 0.64, d.a);
      gl_FragColor = vec4(c, 1.0);
    }`;

  const FRAG_TECHO = `
    precision highp float;
    uniform sampler2D uA;
    uniform sampler2D uB;
    uniform float uMax, uVidrio;
    varying vec2 vUv;
    varying vec3 vP;
    varying float vK;
    ${ZONAS}
    void main() {
      vec4 d = mix(texture2D(uA, vUv), texture2D(uB, vUv), vK);
      if (d.a < 0.5) discard;
      vec2 g = abs(fract(vP.xz) - 0.5) / fwidth(vP.xz);
      float red = 1.0 - smoothstep(0.0, 1.25, min(g.x, g.y));
      float sep = (d.g - d.r) * uMax;
      float al = (red * 0.62 + 0.03) * uVidrio * smoothstep(15.0, 160.0, sep);
      if (al < 0.006) discard;
      float z = zona(d.b, 0.02);
      vec3 c = mix(mix(C_DUDA, C_ACTUAR, max(z, 0.0)), C_BIEN, max(-z, 0.0));
      gl_FragColor = vec4(mix(c, vec3(1.0), 0.45) * al, 1.0);
    }`;

  const FRAG_BASE = `
    precision highp float;
    uniform sampler2D uA;
    varying vec2 vUv;
    varying vec3 vP;
    void main() {
      float m = texture2D(uA, vUv).a;
      if (m < 0.5) discard;
      vec2 g = abs(fract(vP.xz) - 0.5) / fwidth(vP.xz);
      float red = 1.0 - smoothstep(0.0, 1.2, min(g.x, g.y));
      gl_FragColor = vec4(vec3(0.085, 0.078, 0.07) + vec3(0.07, 0.06, 0.05) * red, 1.0);
    }`;

  const VERT_HAZ = `
    varying float vY;
    void main() { vY = position.y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
  const FRAG_HAZ = `
    precision highp float;
    uniform vec3 uCol;
    uniform float uA;
    varying float vY;
    void main() { gl_FragColor = vec4(uCol * uA * (0.16 + 0.84 * vY * vY), 1.0); }`;

  function construir() {
    const D = K.datos, T = D.terreno, n = T.dentro.length, nx = T.nx;
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(33, 16 / 9, 1, 500);

    // centro del terreno
    let cx = 0, cz = 0;
    const indiceDe = {};
    T.dentro.forEach(function (idx, i) { cx += ((idx % nx) - nx / 2 + 0.5) / n; cz += -(Math.floor(idx / nx) - nx / 2 + 0.5) / n; indiceDe[idx] = i; });
    function aEscena(x, y) { return { x: (x - T.x0) / T.lado - nx / 2 - cx, z: -((y - T.y0) / T.lado - nx / 2) - cz }; }
    function bloqueDe(x, y) { return indiceDe[Math.floor((y - T.y0) / T.lado) * nx + Math.floor((x - T.x0) / T.lado)]; }

    // La estimación más alta del mapa llega a unas 7,5 unidades de escena, sea cual sea el caso.
    F = 7.5 / Math.max.apply(null, T.media);

    // ----- una textura por capa: la base y los nueve mapas rehechos -----
    let maximo = 0;
    const capas = [T];
    Object.keys(D.mediciones).forEach(function (l) { Object.keys(D.mediciones[l]).forEach(function (q) { capas.push(D.mediciones[l][q]); }); });
    capas.forEach(function (c) { c.alto.forEach(function (v) { maximo = Math.max(maximo, v); }); });
    maximo = Math.min(maximo, TOPE / F);
    function textura(capa) {
      if (capa._tex) return capa._tex;
      const r = rejilla(T, capa), bytes = new Uint8Array(M * M * 4);
      for (let i = 0; i < M * M; i++) {
        bytes[i * 4] = Math.round(K.acotar(r.media[i] / maximo, 0, 1) * 255);
        bytes[i * 4 + 1] = Math.round(K.acotar(r.alto[i] / maximo, 0, 1) * 255);
        bytes[i * 4 + 2] = Math.round(K.acotar(r.p[i], 0, 1) * 255);
        bytes[i * 4 + 3] = Math.round(K.acotar(r.masc[i], 0, 1) * 255);
      }
      const t = new THREE.DataTexture(bytes, M, M, THREE.RGBAFormat);
      t.magFilter = t.minFilter = THREE.LinearFilter;
      t.needsUpdate = true;
      capa._tex = t;
      return t;
    }

    const u = {
      uA: { value: textura(T) }, uB: { value: textura(T) }, uMorf: { value: 0 }, uCrece: { value: 0 }, uAlt: { value: maximo * F },
      uPin: { value: new THREE.Vector2(0, 0) }, uMax: { value: maximo }, uUmbral: { value: T.umbral }, uDuda: { value: T.umbral_de_duda || 0.1 },
      uT: { value: 0 }, uColor: { value: 1 }, uVidrio: { value: 0 }, uCentro: { value: new THREE.Vector2(cx, cz) },
    };
    const plano = new THREE.PlaneGeometry(nx, nx, 220, 220);
    plano.rotateX(-Math.PI / 2);
    function malla(frag, techo, opciones) {
      const m = new THREE.Mesh(plano, new THREE.ShaderMaterial(Object.assign({
        uniforms: Object.assign({}, u, { uTecho: { value: techo } }), vertexShader: VERT, fragmentShader: frag,
        side: THREE.DoubleSide, extensions: { derivatives: true },
      }, opciones || {})));
      m.position.set(-cx, 0, -cz);
      m.frustumCulled = false;
      return m;
    }
    const base = malla(FRAG_BASE, 0);
    base.material.uniforms.uAlt = { value: 0 };
    base.position.y = -0.03;
    const superficie = malla(FRAG, 0);
    const techo = malla(FRAG_TECHO, 1, { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
    techo.renderOrder = 6;
    scene.add(base, superficie, techo);

    const piso = new THREE.GridHelper(60, 30, 0x2a2622, 0x191715);
    piso.position.y = -0.06;
    scene.add(piso);

    // ----- la orilla del río -----
    const orillas = T.orilla.map(function (p) { return aEscena(p[0], p[1]); });
    const gOrilla = new THREE.BufferGeometry();
    gOrilla.setAttribute('position', new THREE.BufferAttribute(new Float32Array([].concat.apply([], orillas.map(function (e) { return [e.x, 0.12, e.z]; }))), 3));
    if (orillas.length) {
      scene.add(new THREE.Points(gOrilla, new THREE.PointsMaterial({ color: 0x57b6ff, size: 1.5, transparent: true, opacity: 0.2, depthWrite: false })));
      scene.add(new THREE.Points(gOrilla, new THREE.PointsMaterial({ color: 0x8fd0ff, size: 0.46, transparent: true, opacity: 1 })));
    }

    // ----- las mediciones reales -----
    const np = T.puntos.length, azar = K.azar(155);
    const mEsfera = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 1 });
    const esferas = new THREE.InstancedMesh(new THREE.SphereGeometry(0.17, 12, 8), mEsfera, np);
    esferas.frustumCulled = false;
    const puntos = T.puntos.map(function (p) { const e = aEscena(p[0], p[1]); return { x: e.x, y: Math.min(p[2] * F, TOPE), z: e.z, demora: azar() * 1.5 }; });
    const tallos = new Float32Array(np * 6);
    puntos.forEach(function (p, i) { tallos.set([p.x, 0, p.z, p.x, p.y, p.z], i * 6); });
    const gTallos = new THREE.BufferGeometry();
    gTallos.setAttribute('position', new THREE.BufferAttribute(tallos, 3));
    const mTallos = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
    scene.add(esferas, new THREE.LineSegments(gTallos, mTallos));
    const matriz = new THREE.Matrix4();

    // ----- «¿Dónde mido?»: una columna de luz por cada lugar candidato, tan alta como lo que vale medir ahí -----
    const cajaHaz = new THREE.BoxGeometry(1, 1, 1);
    cajaHaz.translate(0, 0.5, 0);
    const valorMax = D.donde.lugares[0].valor_de_medir;
    const porX = D.donde.lugares.map(function (l, j) { return j; }).sort(function (a, b) { return D.donde.lugares[a].x - D.donde.lugares[b].x; });
    const haces = D.donde.lugares.map(function (l, j) {
      const e = aEscena(l.x, l.y), mejor = j < 3;
      const mat = new THREE.ShaderMaterial({
        uniforms: { uCol: { value: new THREE.Color(mejor ? 0xffe2a0 : 0xeec25a) }, uA: { value: 0 } },
        vertexShader: VERT_HAZ, fragmentShader: FRAG_HAZ, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      });
      const haz = new THREE.Mesh(cajaHaz, mat);
      const mCima = new THREE.MeshBasicMaterial({ color: mejor ? 0xffffff : 0xeec25a, transparent: true, opacity: 0 });
      const cima = new THREE.Mesh(new THREE.SphereGeometry(mejor ? 0.42 : 0.24, 16, 12), mCima);
      const mAro = new THREE.MeshBasicMaterial({ color: 0xffe2a0, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
      const aro = new THREE.Mesh(new THREE.RingGeometry(0.7, 0.86, 40), mAro);
      aro.rotation.x = -Math.PI / 2;
      haz.renderOrder = cima.renderOrder = aro.renderOrder = 8;
      scene.add(haz, cima, aro);
      return {
        l: l, i: bloqueDe(l.x, l.y), x: e.x, z: e.z, alto: 1.5 + (l.valor_de_medir / valorMax) * 11.5, ancho: mejor ? 0.5 : 0.32,
        orden: porX.indexOf(j) / D.donde.lugares.length, mejor: mejor, letra: mejor ? 'ABC'[j] : null, haz: haz, mat: mat, cima: cima, mCima: mCima, aro: aro, mAro: mAro, etq: null,
      };
    });
    // el taladro que baja a medir, y la medición nueva
    const taladro = new THREE.Mesh(cajaHaz, new THREE.MeshBasicMaterial({ color: 0xffffff }));
    const nueva = new THREE.Mesh(new THREE.SphereGeometry(0.4, 20, 14), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    const mOnda = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
    const ondaAro = new THREE.Mesh(new THREE.RingGeometry(0.93, 1.0, 80), mOnda);
    ondaAro.rotation.x = -Math.PI / 2;
    taladro.visible = nueva.visible = false;
    taladro.renderOrder = nueva.renderOrder = ondaAro.renderOrder = 9;
    scene.add(taladro, nueva, ondaAro);

    // ----- el punto fijo del zoom: un aro sobre el bloque elegido (su tarjeta la dibuja js/zoom.js) -----
    const mAroZoom = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false, depthTest: false });
    const aroZoom = new THREE.Mesh(new THREE.RingGeometry(0.66, 0.86, 48), mAroZoom);
    aroZoom.rotation.x = -Math.PI / 2;
    aroZoom.renderOrder = 10;
    scene.add(aroZoom);
    function centroDe(i) { const idx = T.dentro[i]; return { x: (idx % nx) + 0.5 - nx / 2 - cx, z: -(Math.floor(idx / nx) + 0.5 - nx / 2) - cz }; }
    // El bloque que se ve en un lugar de la pantalla (de −1 a 1 en cada eje): se camina por el rayo hasta tocar el terreno.
    const rayo = new THREE.Raycaster(), lugar = new THREE.Vector2();
    function bloqueEn(nx_, ny_) {
      lugar.set(nx_, ny_);
      rayo.setFromCamera(lugar, camera);
      const o = rayo.ray.origin, d = rayo.ray.direction;
      for (let t = 20; t < 240; t += 0.2) {
        const col = Math.floor(o.x + d.x * t + cx + nx / 2), fila = Math.floor(nx / 2 - (o.z + d.z * t + cz));
        if (col < 0 || fila < 0 || col >= nx || fila >= nx) continue;
        const i = indiceDe[fila * nx + col];
        if (i != null && o.y + d.y * t <= altura(i)) return i;
      }
      return null;
    }

    // ----- estado animable -----
    const s = {
      zoom: 0,
      crece: 0, color: 1, vidrio: 0, caida: 0, tallos: 0, puntos: 1, morf: 0, escaneo: 0, destaca: 0, haces: 0, taladro: 0, medido: 0,
      az: -0.62, el: 0.62, R: 92, ty: -1.5, dx: -400, dy: 0, fase: 0, arrastre: 0, arrastreEl: 0,
    };
    let actual = T, destino = T, pin = null;

    function altura(i) { return i == null ? 0 : actual.media[i] * F * s.crece; }

    E = {
      tres: { scene: scene, camera: camera }, s: s, T: T, D: D, haces: haces, orillas: orillas, sel: 'A', nivel: 'medio',
      punto: null,                                              // dónde está el foco sobre el terreno ({ x, y, z } en la escena)
      clic: null,                                               // el bloque donde se hizo clic: el foco va hacia allá
      centroDe: centroDe,
      // El bloque que hay bajo un lugar de la escena (null fuera del terreno).
      bloqueBajo: function (x, z) { const col = Math.floor(x + cx + nx / 2), fila = Math.floor(nx / 2 - (z + cz)); return col < 0 || fila < 0 || col >= nx || fila >= nx ? null : indiceDe[fila * nx + col]; },
      bloqueEn: bloqueEn,
      // Las paradas del recorrido del foco: bloques que se ven bien a la derecha de la tarjeta y que no tapa un cerro, en
      // cada uno de los tres colores. Se eligen una vez, con el terreno entero y la cámara en su posición de entrada
      // (sin su vaivén): el recorrido es siempre el mismo.
      paradas: function () {
        const crece = s.crece, visibles = [];
        s.crece = 1;
        camera.setViewOffset(1920, 1080, -400, BAJA, 1920, 1080);
        camera.position.set(Math.sin(-0.62) * Math.cos(0.62) * 92, -1.5 + Math.sin(0.62) * 92, Math.cos(-0.62) * Math.cos(0.62) * 92);
        camera.lookAt(0, -1.5, 0);
        camera.updateMatrixWorld();
        for (let i = 0; i < n; i++) {
          const c = centroDe(i), q = K.proyectar(c.x, actual.media[i] * F, c.z, camera);
          if (q.x < 1090 || q.x > 1760 || q.y < 300 || q.y > 900) continue;
          if (bloqueEn((q.x / 1920) * 2 - 1, 1 - (q.y / 1080) * 2) !== i) continue;          // que no lo tape un cerro
          visibles.push({ i: i, x: q.x, y: q.y });
        }
        s.crece = crece;
        const lejos = function (v, lista) { return lista.every(function (o) { return Math.hypot(v.x - o.x, v.y - o.y) > 170; }); };
        const mejor = function (estado, nota, lista) {
          let m = null, top = -Infinity;
          visibles.forEach(function (v) { if (T.estado[v.i] !== estado || !lejos(v, lista)) return; const k = nota(v); if (k > top) { top = k; m = v; } });
          if (m) lista.push(m);
        };
        const P = [];
        mejor(1, function (v) { return -Math.abs(T.p[v.i] - 0.5); }, P);          // en duda, lo más parejo entre sí y no
        mejor(2, function (v) { return T.media[v.i]; }, P);                       // conviene apartar: donde más arsénico hay
        mejor(0, function (v) { return -T.media[v.i]; }, P);                      // puede ir a la planta: donde menos
        mejor(1, function (v) { return T.alto[v.i] - T.bajo[v.i]; }, P);          // en duda: donde el rango es más ancho
        mejor(2, function (v) { return -Math.abs(T.p[v.i] - 0.85); }, P);
        mejor(0, function (v) { return -Math.abs(T.p[v.i] - 0.08); }, P);
        return P.map(function (v) { return v.i; });
      },
      candidata: function (letra) { return D.donde.candidatas.filter(function (c) { return c.etiqueta === letra; })[0]; },
      // Rehace el mapa hacia otra capa (la respuesta de la red con una medición más), propagándose desde el pin.
      morfar: function (capa, desde, inst, demora) {
        gsap.killTweensOf(s, 'morf');
        u.uA.value = textura(destino);
        u.uB.value = textura(capa);
        actual = destino = capa;
        s.morf = 0;
        if (desde) u.uPin.value.set(desde.x + cx, desde.z + cz);
        pin = desde || null;
        K.anim(s, { morf: 1 }, 2.8, inst, 'power1.inOut', demora || 0);
      },
      capaActual: function () { return destino; },
      cuadro: function (t, dt, lamina) {
        s.fase += dt;
        u.uT.value = t;
        u.uCrece.value = s.crece; u.uMorf.value = s.morf; u.uColor.value = s.color; u.uVidrio.value = s.vidrio;
        mTallos.opacity = 0.24 * s.tallos * s.puntos;
        mEsfera.opacity = s.puntos;

        const tau = s.caida * 3.0;
        for (let i = 0; i < np; i++) {
          const p = puntos[i], k = K.fuera((tau - p.demora) / 1.3);
          if (k <= 0) matriz.makeScale(0, 0, 0); else matriz.makeTranslation(p.x, p.y + (1 - k) * 34, p.z);
          esferas.setMatrixAt(i, matriz);
        }
        esferas.instanceMatrix.needsUpdate = true;

        // columnas de luz: se encienden en un barrido, y al final quedan las tres mejores
        haces.forEach(function (h) {
          const k = K.fuera((s.escaneo * 1.25 - h.orden) / 0.22), y0 = altura(h.i);
          const quedan = h.mejor ? 1 : 1 - 0.55 * s.destaca;
          const elegido = h.letra === E.sel ? 1 : 0;
          const apagado = h.letra && s.medido > 0 ? (elegido ? 1 - s.medido : 1) : 1;
          h.haz.visible = h.cima.visible = k > 0 && s.haces > 0;
          h.haz.position.set(h.x, y0, h.z);
          h.haz.scale.set(h.ancho, Math.max(0.01, h.alto * k * apagado), h.ancho);
          h.mat.uniforms.uA.value = (h.mejor ? 0.95 : 0.6) * quedan * s.haces;
          h.cima.position.set(h.x, y0 + h.alto * k * apagado, h.z);
          h.mCima.opacity = quedan * s.haces * apagado;
          const pulso = K.acotar((s.escaneo * 1.25 - h.orden) / 0.3, 0, 1);
          h.aro.position.set(h.x, y0 + 0.08, h.z);
          h.aro.scale.setScalar(1 + pulso * 3.2);
          h.mAro.opacity = pulso > 0 && pulso < 1 ? (1 - pulso) * 0.9 * s.haces : 0;
        });

        // el taladro baja, toca el terreno y deja la medición
        if (pin && s.taladro > 0) {
          const tope = 38, suelo = altura(pin.i), abajo = K.mezcla(tope, suelo, K.suave(s.taladro));
          taladro.visible = s.taladro < 1 || s.medido < 1;
          taladro.position.set(pin.x, abajo, pin.z);
          taladro.scale.set(0.09, Math.max(0.01, tope - abajo) * (1 - s.medido), 0.09);
          nueva.visible = s.medido > 0;
          nueva.position.set(pin.x, Math.min(pin.valor * F, TOPE), pin.z);
          nueva.scale.setScalar(K.fuera(s.medido * 2));
          const frente = K.acotar(s.morf * 1.9, 0, 1);
          ondaAro.position.set(pin.x, suelo + 0.3, pin.z);
          ondaAro.scale.setScalar(0.5 + frente * 17);
          mOnda.opacity = s.morf > 0 && s.morf < 1 ? (1 - frente) * 0.75 : 0;
        } else { taladro.visible = nueva.visible = false; mOnda.opacity = 0; }

        if (E.punto) {
          aroZoom.position.set(E.punto.x, E.punto.y, E.punto.z);
          aroZoom.scale.setScalar(1 + 0.12 * Math.sin(t * 2.2));
        }
        mAroZoom.opacity = E.punto ? s.zoom : 0;

        const az = s.az + 0.16 * Math.sin(s.fase * 0.2) + s.arrastre, el = K.acotar(s.el + s.arrastreEl, 0.2, 1.4);
        camera.setViewOffset(1920, 1080, s.dx, s.dy, 1920, 1080);
        camera.position.set(Math.sin(az) * Math.cos(el) * s.R, s.ty + Math.sin(el) * s.R, Math.cos(az) * Math.cos(el) * s.R);
        camera.lookAt(0, s.ty, 0);
        camera.updateMatrixWorld();
      },
      alturaDe: altura,
      pinDe: function (letra, valor) {
        const h = haces.filter(function (q) { return q.letra === letra; })[0];
        return { x: h.x, z: h.z, i: h.i, valor: valor };
      },
    };

    // Arrastrar con el mouse gira el terreno (para las preguntas).
    const lienzo = K.gl.renderer.domElement;
    let agarre = null;
    lienzo.addEventListener('pointerdown', function (ev) { agarre = { x: ev.clientX, y: ev.clientY, a: s.arrastre, e: s.arrastreEl }; lienzo.setPointerCapture(ev.pointerId); });
    lienzo.addEventListener('pointermove', function (ev) {
      if (!agarre) return;
      s.arrastre = agarre.a - ((ev.clientX - agarre.x) * 0.006) / K.escala;
      s.arrastreEl = agarre.e + ((ev.clientY - agarre.y) * 0.004) / K.escala;
    });
    lienzo.addEventListener('pointerup', function (ev) {
      const quieto = agarre && Math.hypot(ev.clientX - agarre.x, ev.clientY - agarre.y) < 6, donde = K.donde();
      agarre = null;
      if (!quieto || K.laminas[donde.lamina].id !== 'l-leyes' || donde.paso !== 0) return;
      const r = lienzo.getBoundingClientRect(), i = bloqueEn(((ev.clientX - r.left) / r.width) * 2 - 1, 1 - ((ev.clientY - r.top) / r.height) * 2);
      if (i != null) E.clic = i;                                // un clic sobre el terreno manda el foco a ese punto
    });
    lienzo.addEventListener('pointercancel', function () { agarre = null; });
    return E;
  }

  function terreno() { return E || (K.gl.ok ? construir() : null); }

  // ============================== 5 · Leyes: el banco y «¿Dónde perforo?» ==============================
  // En el paso 0 la escena baja un poco (en píxeles de la lámina): el cerro queda entero bajo el borde de arriba.
  const BAJA = -60;

  K.registrar('leyes', {
    tres: null, interactivo: true, tQuieto: 0,
    crear: function (L) {
      const m = (this.m = terreno()), yo = this, D = K.datos;
      // los tres mejores lugares para una muestra más: su valor, comparado con el del mejor (no en plata: sale de costos supuestos)
      this.filas = {};
      const ranking = L.querySelector('#ranking'), tope = D.donde.candidatas[0].valor_de_medir;
      D.donde.candidatas.forEach(function (c) {
        const fila = document.createElement('div'), pc = Math.round((c.valor_de_medir / tope) * 100);
        fila.className = 'fila ' + c.etiqueta.toLowerCase();
        fila.innerHTML = '<span class="letra">' + c.etiqueta + '</span><span class="riel"><i style="width:' + pc + '%"></i></span><span class="num">' + pc + '</span>';
        ranking.appendChild(fila);
        yo.filas[c.etiqueta] = fila;
      });
      ranking.insertAdjacentHTML('beforeend', '<div class="p nota">Lo que aporta una muestra en cada lugar, con A = 100.</div>');
      this.cuentaAnalisis = L.querySelector('#cuenta-analisis');
      const seg = L.querySelector('#perforo-s'), medido = K.config.cifras && K.config.cifras.donde_perforo_s;
      if (seg && medido) seg.textContent = K.coma(medido, 1) + ' segundos';
      // la tarjeta del foco: el eje del arsénico, en logaritmo, y el máximo que acepta la planta
      const F = (this.F = K.foco.crear(L, 'leyes')), G = K.filasDe.leyes(1);
      F.eje = { min: Math.min(G.min, Math.min.apply(null, D.terreno.bajo) * 0.8), max: Math.max(G.max, Math.max.apply(null, D.terreno.alto) * 1.25), log: true, limite: G.limite };
      this.colores = ['no_actuar', 'en_duda', 'actuar'].map(function (e) { return K.foco.rgb(K.coloresDecision[e]); });
      this.rotulos = ['no_actuar', 'en_duda', 'actuar'].map(function (e) { return D.terreno.rotulos[e]; });
      if (!m) return;
      this.tres = m.tres;
      const capa = L.querySelector('#etq-leyes');
      m.haces.forEach(function (h) {
        if (!h.letra) return;
        h.etq = document.createElement('div');
        h.etq.className = 'etq letra' + (h.letra === 'A' ? '' : ' menor');
        h.etq.textContent = h.letra;
        capa.appendChild(h.etq);
      });
    },
    alAjustar: function () { if (this.F) K.foco.ajustar(this.F); },
    entrar: function () {
      const m = this.m;
      if (!m) return;
      const s = m.s;
      gsap.killTweensOf(s);
      if (m.capaActual() !== m.T) m.morfar(m.T, null, true);
      Object.assign(s, { zoom: 0, crece: 0, vidrio: 0, caida: 1, tallos: 1, puntos: 1, color: 1, morf: 1, haces: 0, escaneo: 0, destaca: 0, taladro: 0, medido: 0,
        az: -0.62, el: 0.62, R: 92, ty: -1.5, dx: -400, dy: BAJA, arrastre: 0, arrastreEl: 0 });
      // el recorrido del foco parte siempre igual: las paradas se eligen la primera vez
      if (!this.paradas) this.paradas = m.paradas();
      m.clic = null;
      this.v = null; this.de = 0; this.a = 1 % Math.max(1, this.paradas.length); this.t0 = null;
      // el banco se levanta apenas entra la lámina; después aparece la malla del rango
      K.anim(s, { crece: 1 }, 3.0, false, 'power1.inOut', 0.3);
      K.anim(s, { vidrio: 1 }, 1.6, false, 'power1.inOut', 3.0);
    },
    paso: function (p, inst) {
      const m = this.m;
      if (!m) return;
      const s = m.s;
      if (inst) { gsap.killTweensOf(s, 'crece,vidrio'); s.crece = 1; s.vidrio = p === 0 ? 1 : 0; }
      gsap.killTweensOf(s, 'zoom');
      if (p === 0) K.anim(s, { zoom: 1 }, 0.8, inst, 'power1.out', s.crece < 0.5 ? 2.6 : 0.2); else K.anim(s, { zoom: 0 }, 0.25, inst);
      if (p === 0) {
        K.anim(s, { haces: 0, puntos: 1 }, 0.6, inst);
        K.anim(s, { az: -0.62, el: 0.62, R: 92, ty: -1.5, dy: BAJA }, 2.2, inst);
        if (inst) { s.escaneo = 0; s.destaca = 0; }
      } else {
        gsap.killTweensOf(s, 'crece,vidrio');
        s.crece = 1;
        K.anim(s, { vidrio: 0, puntos: 0.3, haces: 1 }, 0.8, inst);
        K.anim(s, { az: -0.5, el: 0.84, R: 96, ty: 1.5, dy: 0 }, 2.6, inst);
        if (!inst) { s.escaneo = 0; s.destaca = 0; }
        K.anim(s, { escaneo: 1 }, 3.0, inst, 'power1.inOut', 0.5);
        K.anim(s, { destaca: 1 }, 1.6, inst, 'power1.inOut', 3.4);
      }
    },
    // El foco sobre el terreno: se detiene en una parada, viaja en línea recta a la siguiente y, en el camino, la tarjeta
    // muestra lo que la red respondió para el bloque que tiene debajo en ese instante. Un clic en el terreno lo manda ahí.
    foco: function (t, dt) {
      const m = this.m, T = m.T, P = this.paradas, PAUSA = 2.6, VIAJE = 2.4;
      if (!P.length) return null;
      if (this.t0 == null) this.t0 = t;
      if (m.clic != null) { P.splice(this.a, 0, m.clic); if (P.length > 9) P.splice((this.a + 4) % P.length, 1); this.de = Math.min(this.de, P.length - 1); this.a = P.indexOf(m.clic); m.clic = null; this.t0 = t - PAUSA; }
      let k = K.quieto ? 0 : (t - this.t0 - PAUSA) / VIAJE;
      if (k >= 1) { this.de = this.a; this.a = (this.a + 1) % P.length; this.t0 = t; k = 0; }
      const e = K.suave(K.suave(K.acotar(k, 0, 1))), A = m.centroDe(P[this.de]), B = m.centroDe(P[this.a]);
      const x = K.mezcla(A.x, B.x, e), z = K.mezcla(A.z, B.z, e), i = m.bloqueBajo(x, z);
      const j = i == null ? P[this.de] : i, obj = { bajo: T.bajo[j], medio: T.media[j], alto: T.alto[j], c: this.colores[T.estado[j]] };
      // lo que se muestra sigue al bloque de abajo con suavidad: sin escalones al cruzar de un bloque a otro
      const v = this.v || (this.v = { bajo: obj.bajo, medio: obj.medio, alto: obj.alto, c: obj.c.slice(), y: m.alturaDe(j) }), q = K.quieto ? 1 : Math.min(1, (dt || 0.016) * 9);
      v.bajo += (obj.bajo - v.bajo) * q; v.medio += (obj.medio - v.medio) * q; v.alto += (obj.alto - v.alto) * q;
      for (let n = 0; n < 3; n++) v.c[n] += (obj.c[n] - v.c[n]) * q;
      v.y += (m.alturaDe(j) - v.y) * q;
      v.estado = T.estado[j]; v.x = x; v.z = z;
      return v;
    },
    cuadro: function (t, dt) {
      const m = this.m, F = this.F;
      if (!m) return;
      const s = m.s, yo = this, n = m.D.donde.analisis_rehechos, v = this.foco(t, dt);
      m.punto = v ? { x: v.x, y: v.y + 0.15, z: v.z } : null;
      m.cuadro(t, dt, 'leyes');
      if (v) {
        const eje = F.eje, ancho = Math.log(v.alto / v.bajo) / 3.29 / Math.log(eje.max / eje.min);
        this._n = (this._n || 0) + 1;
        K.foco.pintar(F, { id: 'p', sello: this._n, nombre: 'En este punto del terreno', decision: this.rotulos[v.estado], color: v.c, bajo: v.bajo, medio: v.medio, alto: v.alto,
          d: K.foco.densidad(eje, null, { centro: v.medio, ancho: ancho }) }, null, 0, K.suave(s.zoom));
        const pp = K.proyectar(v.x, v.y + 0.15, v.z, m.tres.camera);
        K.foco.hilar(F, pp.x, pp.y, s.zoom > 0.5);
      }
      this.cuentaAnalisis.textContent = K.miles(Math.min(n, Math.floor(K.acotar(s.escaneo * 1.02, 0, 1) * n)));
      ['C', 'B', 'A'].forEach(function (l, j) { yo.filas[l].classList.toggle('ver', s.destaca > 0.08 + j * 0.3); });   // C, B y al final A
      m.haces.forEach(function (h) {
        if (!h.etq) return;
        h.etq.classList.toggle('ver', s.destaca > 0.5 && s.haces > 0.5);
        const q = K.proyectar(h.cima.position.x, h.cima.position.y + 1.3, h.cima.position.z, m.tres.camera);
        h.etq.style.transform = 'translate(' + q.x.toFixed(1) + 'px,' + q.y.toFixed(1) + 'px) translate(-50%, -100%)';
      });
    },
  });
})();
