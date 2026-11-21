/* 7 · Hoja de ruta. Cinco ilustraciones hechas de puntos, una por cada decisión crítica de la mina:
   leyes, sismicidad, camiones, flotación y taludes. Nada de esto son datos ni existe todavía: la lámina lo dice. */
(function () {
  'use strict';
  const K = window.K;
  const X = [-20.24, -10.12, 0, 10.12, 20.24], Y = -0.7;      // una columna por problema, en unidades de escena
  const COLORES = `
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

  K.registrar('vision', {
    tres: null, tQuieto: 9.3,
    crear: function () {
      if (!K.gl.ok) return;
      const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(30, 16 / 9, 1, 200);
      camera.position.set(0, 0, 60);
      const azar = K.azar(7), u = (this.u = { uT: { value: 0 }, uEsc: { value: 2000 } });
      const material = function (vertex) {
        return new THREE.ShaderMaterial({
          uniforms: u, vertexShader: 'uniform float uT;\nuniform float uEsc;\nvarying vec3 vColor;\nvarying float vA;\n' + COLORES + vertex,
          fragmentShader: FRAG, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
        });
      };
      const puntos = function (atributos, vertex) {
        const g = new THREE.BufferGeometry();
        Object.keys(atributos).forEach(function (k) { g.setAttribute(k, new THREE.BufferAttribute(new Float32Array(atributos[k][0]), atributos[k][1])); });
        const p = new THREE.Points(g, material(vertex));
        p.frustumCulled = false;
        return p;
      };
      const lineas = function (v, color, opacidad) {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(v), 3));
        return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: color, transparent: true, opacity: opacidad }));
      };
      const grupo = function (i) { const g = new THREE.Group(); g.position.set(X[i], Y, 0); g.scale.setScalar([1.02, 1.3, 1.1, 1.22, 1.08][i]); scene.add(g); return g; };

      // ----- 1 · Leyes: un cuerpo mineralizado bajo tierra y los sondajes que lo cruzan -----
      const leyes = (this.leyes = grupo(0));
      const pl = [], vl = [];
      const ley = function (x, y, z) {
        const a = Math.exp(-((x - 0.9) * (x - 0.9) / 4.5 + (y + 1.3) * (y + 1.3) / 1.5 + (z + 0.4) * (z + 0.4) / 4));
        const b = Math.exp(-((x + 1.8) * (x + 1.8) / 2 + (y + 0.1) * (y + 0.1) / 1.1 + (z - 1.2) * (z - 1.2) / 2));
        return Math.min(1, a + 0.75 * b);
      };
      for (let i = 0; i < 2800; i++) {
        const x = (azar() - 0.5) * 8, y = azar() * 5 - 3.4, z = (azar() - 0.5) * 8;
        pl.push(x, y, z); vl.push(ley(x, y, z));
      }
      leyes.add(puntos({ position: [pl, 3], aV: [vl, 1] }, `
        attribute float aV;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          float late = 0.85 + 0.15 * sin(uT * 1.6 + position.x * 0.9 + position.z * 0.7);
          vColor = aV < 0.45 ? mix(OXIDO * 0.55, COBRE, aV / 0.45) : mix(COBRE, ORO, (aV - 0.45) / 0.55);
          vA = (0.22 + 1.15 * aV) * late;
          gl_PointSize = (0.085 + 0.24 * aV) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`));
      const malla = [], sondas = [];
      for (let k = -4; k <= 4; k++) malla.push(k, 1.7, -4, k, 1.7, 4, -4, 1.7, k, 4, 1.7, k);
      [[-2.6, 1.6], [-0.9, -2.3], [0.7, 0.3], [2.1, -1.0], [2.9, 2.4], [-1.9, -0.3], [1.0, 2.7]].forEach(function (q) { sondas.push(q[0], 1.7, q[1], q[0] + 0.4, -3.4, q[1] - 0.25); });
      leyes.add(lineas(malla, 0x6b6156, 0.55), lineas(sondas, 0xffffff, 0.8));
      leyes.rotation.x = 0.36;

      // ----- 2 · Sismicidad: una galería y los sismos que se encadenan después de una tronadura -----
      const sismo = (this.sismo = grupo(1));
      const arcos = [], piso = [];
      for (let k = 0; k < 9; k++) {
        const z = -4 + k;
        for (let j = 0; j < 14; j++) {
          const a0 = (j / 14) * Math.PI, a1 = ((j + 1) / 14) * Math.PI;
          arcos.push(Math.cos(a0) * 1.25, Math.sin(a0) * 1.25 - 0.9, z, Math.cos(a1) * 1.25, Math.sin(a1) * 1.25 - 0.9, z);
        }
      }
      piso.push(-1.25, -0.9, -4, -1.25, -0.9, 4, 1.25, -0.9, -4, 1.25, -0.9, 4);
      sismo.add(lineas(arcos, 0x6b6156, 0.7), lineas(piso, 0x6b6156, 0.7));
      const ps = [], ts = [], focos = [[2.2, 1.6, -2.4, 0.4], [-2.4, 0.6, 0.5, 2.6], [1.6, -2.2, 2.2, 4.4], [-1.4, 2.4, 3.0, 6.0]];
      for (let i = 0; i < 420; i++) {
        const f = focos[i % focos.length], r = 0.25 + azar() * 1.5, a = azar() * 6.283, b = Math.acos(2 * azar() - 1);
        ps.push(f[0] + r * Math.sin(b) * Math.cos(a), f[1] + r * Math.cos(b), f[2] + r * Math.sin(b) * Math.sin(a));
        ts.push(f[3] - Math.log(1 - azar() * 0.97) * 0.45);          // réplicas: muchas al principio, cada vez menos
      }
      sismo.add(puntos({ position: [ps, 3], aT: [ts, 1] }, `
        attribute float aT;
        void main() {
          float dt = mod(uT - aT, 7.6);
          float golpe = exp(-dt * 1.7);
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(COBRE, ORO, golpe);
          vA = 0.22 + 1.5 * golpe;
          gl_PointSize = (0.09 + 0.46 * golpe) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`));
      sismo.rotation.x = 0.3;

      // ----- 3 · Camiones: el desgaste de cada equipo, lo ya visto y lo que podría venir -----
      const flota = (this.flota = grupo(2));
      const pf = [], uf = [], rf = [];
      for (let c = 0; c < 11; c++) {
        const ritmo = 0.45 + azar() * 1.0, curva = 1.6 + azar() * 1.6, dato = azar();
        for (let j = 0; j < 80; j++) {
          const q = j / 79, y = -2.9 + 5.6 * ritmo * (0.25 * q + 0.75 * Math.pow(q, curva)) + (azar() - 0.5) * 0.09;
          pf.push(-4.2 + 8.4 * q, y, 0); uf.push(q); rf.push(dato + (azar() - 0.5) * 0.25);
        }
      }
      flota.add(puntos({ position: [pf, 3], aU: [uf, 1], aR: [rf, 1] }, `
        attribute float aU;
        attribute float aR;
        void main() {
          float ahora = 0.32 + 0.3 * (0.5 + 0.5 * sin(uT * 0.35));
          float futuro = max(aU - ahora, 0.0);
          vec3 p = position;
          p.y += (aR - 0.5) * futuro * 4.2;                              // el abanico de lo que podría pasar
          float falla = smoothstep(1.7, 2.0, p.y);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(mix(OXIDO, COBRE, clamp(p.y * 0.2 + 0.5, 0.0, 1.0)), ROJO, falla);
          vA = futuro > 0.0 ? 0.26 + 0.5 * falla : 0.95;
          gl_PointSize = (futuro > 0.0 ? 0.10 : 0.15) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`));
      const umbral = [];
      for (let k = 0; k < 21; k++) umbral.push(-4.2 + k * 0.4, 2.0, 0, -4.2 + k * 0.4 + 0.2, 2.0, 0);
      flota.add(lineas(umbral, 0xea5c38, 0.95), lineas([-4.2, -3.1, 0, 4.2, -3.1, 0, -4.2, -3.1, 0, -4.2, 2.9, 0], 0x6b6156, 0.7));

      // ----- 4 · Flotación: burbujas que suben en tres celdas y la espuma que se lleva el metal -----
      const planta = (this.planta = grupo(3));
      const pb = [], ab = [], cajas = [];
      for (let c = 0; c < 3; c++) {
        const x0 = -2.9 + c * 2.9;
        cajas.push(x0 - 1.15, -2.9, 0, x0 - 1.15, 2.3, 0, x0 + 1.15, -2.9, 0, x0 + 1.15, 2.3, 0, x0 - 1.15, -2.9, 0, x0 + 1.15, -2.9, 0);
        for (let i = 0; i < 300; i++) { pb.push(x0 + (azar() - 0.5) * 2.0, azar() * 5.2, (azar() - 0.5) * 1.2); ab.push(azar(), azar(), c / 2); }
      }
      planta.add(lineas(cajas, 0x6b6156, 0.75));
      planta.add(puntos({ position: [pb, 3], aB: [ab, 3] }, `
        attribute vec3 aB;
        void main() {
          float sube = mod(position.y + uT * (0.35 + 0.75 * aB.x), 5.2);
          vec3 p = vec3(position.x + sin(uT * 1.3 + aB.y * 30.0) * 0.07, sube - 2.9, position.z);
          float espuma = smoothstep(4.1, 4.9, sube);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(OXIDO, mix(COBRE, ORO, aB.z), espuma);
          vA = 0.28 + 0.9 * espuma;
          gl_PointSize = (0.07 + 0.11 * aB.y + 0.12 * espuma) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`));

      // ----- 5 · Taludes y relaves: un muro con sus bancos, el barrido del radar y una zona que empieza a moverse -----
      const talud = (this.talud = grupo(4));
      const pt = [], at = [];
      for (let f = 0; f < 34; f++) {
        for (let c = 0; c < 52; c++) {
          const ux = -4.1 + (c / 51) * 8.2 + (azar() - 0.5) * 0.08, v = f / 33;
          const banco = Math.floor(v * 5), resto = v * 5 - banco, sube = (banco + K.suave((resto - 0.55) / 0.45)) / 5;
          const dx = (ux - 0.9) / 1.9, dv = (v - 0.56) / 0.2;
          pt.push(ux, -3.0 + sube * 5.6, 2.4 - v * 4.8);
          at.push(Math.exp(-(dx * dx + dv * dv)), azar());
        }
      }
      talud.add(puntos({ position: [pt, 3], aZ: [at, 2] }, `
        attribute vec2 aZ;
        void main() {
          float mueve = aZ.x * (0.5 + 0.5 * sin(uT * 0.6));
          vec3 p = position + vec3(0.0, -0.42, 0.42) * mueve;
          float dr = (position.x - (-4.4 + 8.8 * fract(uT * 0.13))) / 0.22;
          float radar = exp(-dr * dr);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(ARENA, ROJO, smoothstep(0.15, 0.7, aZ.x)) + ORO * radar * 0.9;
          vA = 0.42 + 0.6 * aZ.x + radar * 0.8;
          gl_PointSize = (0.085 + 0.07 * aZ.x + 0.06 * radar) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`));
      talud.rotation.set(0.32, -0.5, 0);

      this.tres = { scene: scene, camera: camera };
    },
    alAjustar: function () {
      if (this.u) this.u.uEsc.value = (K.gl.renderer.getPixelRatio() * 1080) / (2 * Math.tan((15 * Math.PI) / 180));
    },
    cuadro: function (t) {
      if (!this.tres) return;
      this.u.uT.value = t;
      this.leyes.rotation.y = 0.5 + t * 0.16;
      this.sismo.rotation.y = 0.7 + Math.sin(t * 0.25) * 0.45;
      this.talud.rotation.y = -0.5 + Math.sin(t * 0.2) * 0.12;
    },
  });
})();
