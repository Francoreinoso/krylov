/* 7 · Visión (hoja de ruta). Tres ilustraciones hechas de puntos: un yacimiento con sondajes, un campo sobre una esfera
   y una grilla de empresas. Nada de esto son datos: va rotulado «hoja de ruta» e «ilustración». */
(function () {
  'use strict';
  const K = window.K;
  const SEP = 17.47, BAJA = -0.2;               // separación entre columnas y altura, en unidades de escena

  const PUNTO = `
    void main() {
      vec2 d = gl_PointCoord - 0.5;
      float r = dot(d, d);
      if (r > 0.25) discard;
      gl_FragColor = vec4(vColor * vA * (1.0 - r * 2.4), 1.0);
    }`;

  function material(vertex, uniforms) {
    return new THREE.ShaderMaterial({
      uniforms: uniforms, vertexShader: vertex,
      fragmentShader: 'precision highp float;\nvarying vec3 vColor;\nvarying float vA;\n' + PUNTO,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
  }

  K.registrar('vision', {
    tres: null, tQuieto: 9,
    crear: function () {
      if (!K.gl.ok) return;
      const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(30, 16 / 9, 1, 200);
      camera.position.set(0, 0, 60);
      const azar = K.azar(7), u = (this.u = { uT: { value: 0 }, uEsc: { value: 2000 } });

      // ----- Minería: un cuerpo bajo tierra y sondajes -----
      const mina = (this.mina = new THREE.Group());
      mina.position.set(-SEP, BAJA, 0);
      const nm = 3400, pm = new Float32Array(nm * 3), vm = new Float32Array(nm);
      const ley = function (x, y, z) {
        const a = Math.exp(-((x - 1.2) * (x - 1.2) / 7 + (y + 1.6) * (y + 1.6) / 2.2 + (z + 0.6) * (z + 0.6) / 6));
        const b = Math.exp(-((x + 2.4) * (x + 2.4) / 3 + (y + 0.2) * (y + 0.2) / 1.6 + (z - 1.6) * (z - 1.6) / 3));
        return Math.min(1, a + 0.75 * b);
      };
      for (let i = 0; i < nm; i++) {
        const x = (azar() - 0.5) * 11, y = azar() * 6.4 - 4.2, z = (azar() - 0.5) * 11;
        pm.set([x, y, z], i * 3);
        vm[i] = ley(x, y, z);
      }
      const gm = new THREE.BufferGeometry();
      gm.setAttribute('position', new THREE.BufferAttribute(pm, 3));
      gm.setAttribute('aV', new THREE.BufferAttribute(vm, 1));
      mina.add(new THREE.Points(gm, material(`
        attribute float aV; uniform float uT; uniform float uEsc; varying vec3 vColor; varying float vA;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          float late = 0.85 + 0.15 * sin(uT * 1.6 + position.x * 0.9 + position.z * 0.7);
          vec3 frio = vec3(0.24, 0.24, 0.62), medio = vec3(0.62, 0.38, 0.86), calido = vec3(1.0, 0.62, 0.32);
          vColor = aV < 0.45 ? mix(frio, medio, aV / 0.45) : mix(medio, calido, (aV - 0.45) / 0.55);
          vA = (0.30 + 1.1 * aV) * late;
          gl_PointSize = (0.10 + 0.26 * aV) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, u)));
      const lineas = [];
      for (let k = -5; k <= 5; k++) lineas.push(k * 1.1, 2.3, -5.5, k * 1.1, 2.3, 5.5, -5.5, 2.3, k * 1.1, 5.5, 2.3, k * 1.1);
      const gs = new THREE.BufferGeometry();
      gs.setAttribute('position', new THREE.BufferAttribute(new Float32Array(lineas), 3));
      mina.add(new THREE.LineSegments(gs, new THREE.LineBasicMaterial({ color: 0x4a4d86, transparent: true, opacity: 0.7 })));
      const sondas = [[-3.6, 2.2], [-1.2, -3.1], [0.9, 0.4], [2.8, -1.4], [3.9, 3.2], [-2.6, -0.4], [1.4, 3.6]], ls = [];
      sondas.forEach(function (q) { ls.push(q[0], 2.3, q[1], q[0] + 0.5, -4.2, q[1] - 0.3); });
      const gl2 = new THREE.BufferGeometry();
      gl2.setAttribute('position', new THREE.BufferAttribute(new Float32Array(ls), 3));
      mina.add(new THREE.LineSegments(gl2, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75 })));
      mina.rotation.x = 0.36;
      mina.scale.setScalar(1.14);
      scene.add(mina);

      // ----- Clima: un campo que se mueve sobre una esfera -----
      const globo = (this.globo = new THREE.Group());
      globo.position.set(0, BAJA + 0.2, 0);
      const ng = 5200, pg = new Float32Array(ng * 3);
      for (let i = 0; i < ng; i++) {
        const y = 1 - (2 * (i + 0.5)) / ng, r = Math.sqrt(1 - y * y), a = i * 2.39996323;
        pg.set([Math.cos(a) * r * 5.2, y * 5.2, Math.sin(a) * r * 5.2], i * 3);
      }
      const gg = new THREE.BufferGeometry();
      gg.setAttribute('position', new THREE.BufferAttribute(pg, 3));
      globo.add(new THREE.Points(gg, material(`
        uniform float uT; uniform float uEsc; varying vec3 vColor; varying float vA;
        float sq(float x) { return x * x; }
        void main() {
          vec3 n = normalize(position);
          float lat = asin(n.y), lon = atan(n.z, n.x);
          float banda = exp(-sq(lat / 0.28)) * (0.25 + 0.75 * pow(0.5 + 0.5 * sin(lon - uT * 0.22), 2.0));
          float onda = 0.5 * sin(3.0 * lon + 5.0 * lat + uT * 0.3) * cos(2.4 * lat) * exp(-sq((abs(lat) - 0.8) / 0.5));
          float v = banda * 1.1 + onda * 0.55;
          vec3 frio = vec3(0.30, 0.62, 1.0), neutro = vec3(0.30, 0.31, 0.62), calido = vec3(1.0, 0.56, 0.26);
          vColor = v > 0.0 ? mix(neutro, calido, clamp(v, 0.0, 1.0)) : mix(neutro, frio, clamp(-v * 2.2, 0.0, 1.0));
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vec3 nv = normalize(normalMatrix * n);
          float frente = smoothstep(-0.35, 0.5, nv.z);
          vA = (0.42 + 0.8 * abs(v)) * (0.10 + 0.90 * frente);
          gl_PointSize = (0.10 + 0.12 * abs(v)) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, u)));
      globo.rotation.z = 0.36;
      globo.scale.setScalar(1.08);
      scene.add(globo);

      // ----- Plataformas: miles de empresas, cada una con su respuesta -----
      const red = (this.red = new THREE.Group());
      red.position.set(SEP, BAJA + 0.3, 0);
      const cols = 46, filas = 26, ne = cols * filas, pe = new Float32Array(ne * 3), ae = new Float32Array(ne * 2);
      for (let f = 0; f < filas; f++) {
        for (let c = 0; c < cols; c++) {
          const i = f * cols + c;
          pe.set([(c - (cols - 1) / 2) * 0.29, 0, (f - (filas - 1) / 2) * 0.36], i * 3);
          ae[i * 2] = azar(); ae[i * 2 + 1] = azar();
        }
      }
      const ge = new THREE.BufferGeometry();
      ge.setAttribute('position', new THREE.BufferAttribute(pe, 3));
      ge.setAttribute('aAzar', new THREE.BufferAttribute(ae, 2));
      red.add(new THREE.Points(ge, material(`
        attribute vec2 aAzar; uniform float uT; uniform float uEsc; varying vec3 vColor; varying float vA;
        float sq(float x) { return x * x; }
        void main() {
          float frente = mod(uT * 0.16, 1.5) - 0.2;                     // una ola que recorre la grilla
          float u01 = position.x / 13.3 + 0.5 + (aAzar.y - 0.5) * 0.08;
          float listo = smoothstep(0.0, 0.05, frente - u01);
          float borde = exp(-sq((frente - u01) / 0.035));
          vec3 gris = vec3(0.26, 0.27, 0.45);
          vec3 decision = aAzar.x < 0.68 ? vec3(0.16, 0.74, 0.46) : (aAzar.x < 0.90 ? vec3(0.93, 0.68, 0.05) : vec3(0.92, 0.30, 0.30));
          vColor = mix(gris, decision, listo) + vec3(1.0) * borde * 0.8;
          vA = 0.5 + 0.5 * listo + borde;
          vec4 mv = modelViewMatrix * vec4(position + vec3(0.0, borde * 0.5, 0.0), 1.0);
          gl_PointSize = (0.13 + 0.06 * listo + 0.1 * borde) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, u)));
      red.rotation.x = 0.95;
      scene.add(red);

      this.tres = { scene: scene, camera: camera };
    },
    alAjustar: function () {
      if (this.u) this.u.uEsc.value = (K.gl.renderer.getPixelRatio() * 1080) / (2 * Math.tan((15 * Math.PI) / 180));
    },
    cuadro: function (t) {
      if (!this.tres) return;
      this.u.uT.value = t;
      this.mina.rotation.y = 0.5 + t * 0.14;
      this.globo.rotation.y = t * 0.12;
      this.red.rotation.z = Math.sin(t * 0.2) * 0.04;
    },
  });
})();
