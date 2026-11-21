/* 1 · Portada: la mina como una maqueta topográfica. Un rajo abierto modelado como superficie continua (no puntos):
   sus bancos, su rampa y el terreno de alrededor, con curvas de nivel y luz rasante. Cada tanto, una onda sale del fondo
   y enciende las curvas al pasar: Krylov leyendo la mina. Es una ilustración: no es ninguna mina ni representa datos. */
(function () {
  'use strict';
  const K = window.K;
  const N = 380, MEDIO = 13.5, RADIO = 8.6, HONDO = 6.4, BANCOS = 9;

  K.registrar('valor', {
    tres: null, tQuieto: 6.5,
    crear: function () {
      if (!K.gl.ok) return;
      // un ruido suave con semilla, para que el borde del rajo y el terreno de afuera no sean perfectos
      const azar = K.azar(2026), G = 48, grano = [];
      for (let i = 0; i < G * G; i++) grano.push(azar() - 0.5);
      const ruido = function (x, y) {
        const x0 = Math.floor(x), y0 = Math.floor(y), fx = K.suave(x - x0), fy = K.suave(y - y0);
        const g = function (i, j) { return grano[((((j % G) + G) % G) * G) + (((i % G) + G) % G)]; };
        return K.mezcla(K.mezcla(g(x0, y0), g(x0 + 1, y0), fx), K.mezcla(g(x0, y0 + 1), g(x0 + 1, y0 + 1), fx), fy);
      };
      const altura = function (x, z) {
        const ang = Math.atan2(z, x), r = Math.hypot(x / 1.22, z) * (1 + 0.07 * Math.sin(3 * ang + 1.1) + 0.04 * Math.sin(5 * ang + 0.4)) + ruido(x * 0.35 + 9, z * 0.35) * 0.9;
        const afuera = 0.55 * ruido(x * 0.22, z * 0.22 + 4) + 0.22 * ruido(x * 0.6 + 2, z * 0.6);
        if (r >= RADIO) return afuera * K.suave((r - RADIO) / 2.2) + 0.12;
        const q = Math.max(r / RADIO, 0.15), s = q * BANCOS, b = Math.floor(s), f = s - b;
        const banco = -HONDO * (1 - (b + K.suave((f - 0.5) / 0.5)) / BANCOS);              // piso plano y después la cara del banco
        // la rampa: un camino que sube en espiral, con pendiente pareja, cortando los bancos
        let d = ang - (0.6 + q * 6.2832 * 1.15);
        d = Math.atan2(Math.sin(d), Math.cos(d));
        const enRampa = K.suave(1 - Math.abs(d) * r / 0.95);
        return K.mezcla(banco, -HONDO * (1 - q) - 0.05, enRampa * K.suave((q - 0.16) / 0.08)) + 0.12 * K.suave((q - 0.92) / 0.08);
      };
      const pos = new Float32Array(N * N * 3), idx = new Uint32Array((N - 1) * (N - 1) * 6);
      for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
        const x = (i / (N - 1) - 0.5) * 2 * MEDIO, z = (j / (N - 1) - 0.5) * 2 * MEDIO, o = (j * N + i) * 3;
        pos[o] = x; pos[o + 1] = altura(x, z); pos[o + 2] = z;
      }
      let k = 0;
      for (let j = 0; j < N - 1; j++) for (let i = 0; i < N - 1; i++) { const a = j * N + i; idx[k++] = a; idx[k++] = a + N; idx[k++] = a + 1; idx[k++] = a + 1; idx[k++] = a + N; idx[k++] = a + N + 1; }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      g.setIndex(new THREE.BufferAttribute(idx, 1));
      g.computeVertexNormals();                              // normales suaves: las caras de los bancos no quedan dentadas
      const u = (this.u = { uT: { value: 0 } });
      const malla = new THREE.Mesh(g, new THREE.ShaderMaterial({
        uniforms: u, extensions: { derivatives: true },
        vertexShader: 'varying vec3 vP;\nvarying vec3 vN;\nvoid main() { vP = position; vN = normal; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
        fragmentShader: `
          precision highp float;
          varying vec3 vP;
          varying vec3 vN;
          uniform float uT;
          void main() {
            vec3 n = normalize(vN);
            if (n.y < 0.0) n = -n;
            float luz = clamp(dot(n, normalize(vec3(-0.62, 0.62, 0.48))), 0.0, 1.0);
            float piso = smoothstep(0.80, 0.985, n.y);                                   // el piso de cada banco, y el terreno de afuera
            vec3 cara = mix(vec3(0.15, 0.085, 0.05), vec3(0.80, 0.45, 0.22), pow(luz, 1.25));     // las caras de roca: cobre
            vec3 plano = mix(vec3(0.10, 0.085, 0.07), vec3(0.60, 0.51, 0.40), luz);                // los pisos: arena
            vec3 c = mix(cara, plano, piso);
            float hondo = smoothstep(-${HONDO.toFixed(1)}, 0.4, vP.y);
            c *= mix(0.42, 1.0, hondo);                                                   // el fondo del rajo, en sombra
            // curvas de nivel
            float nivel = vP.y * 2.8, ancho = fwidth(nivel);
            float curva = 1.0 - smoothstep(0.7, 1.7, abs(fract(nivel - 0.5) - 0.5) / max(ancho, 1e-4));
            c = mix(c, vec3(1.0, 0.80, 0.50), curva * 0.34);
            // la onda que sale del fondo y enciende las curvas al pasar
            float r = length(vP.xz * vec2(0.82, 1.0)), frente = mod(uT * 2.4, 26.0);
            float onda = exp(-pow((r - frente) / 0.55, 2.0)) * smoothstep(13.0, 6.0, r);
            c += vec3(1.0, 0.74, 0.40) * onda * (0.18 + 0.82 * curva);
            // hacia la orilla se funde con el fondo de la lámina
            float borde = smoothstep(${(MEDIO - 0.6).toFixed(1)}, ${(MEDIO - 4.4).toFixed(1)}, length(vP.xz * vec2(0.9, 1.0)));
            c *= mix(0.6, 1.0, smoothstep(${(RADIO + 3.5).toFixed(1)}, ${RADIO.toFixed(1)}, r));        // lo de afuera, más apagado: manda el rajo
            gl_FragColor = vec4(mix(vec3(0.043, 0.039, 0.035), c, borde), 1.0);
          }`,
      }));
      malla.frustumCulled = false;
      const scene = new THREE.Scene(), camera = (this.camara = new THREE.PerspectiveCamera(28, 16 / 9, 1, 200));
      scene.add(malla);
      this.tres = { scene: scene, camera: camera };
    },
    cuadro: function (t) {
      if (!this.tres) return;
      this.u.uT.value = t;
      const az = 0.7 + t * 0.045, el = 0.6, R = 45, c = this.camara;                // gira despacio, vista desde arriba
      c.position.set(R * Math.cos(el) * Math.sin(az), -1.6 + R * Math.sin(el), R * Math.cos(el) * Math.cos(az));
      c.lookAt(0, -1.6, 0);
      c.setViewOffset(1920, 1080, -450, 20, 1920, 1080);
    },
  });
})();
