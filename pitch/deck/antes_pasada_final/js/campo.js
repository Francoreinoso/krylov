/* El campo de terrenos simulados: cientos de terrenos de 32×32 que fluyen hacia la cámara y se apilan.
   Los terrenos son muestras reales del simulador (datos.js → simulados). Lo usan las láminas 3 y 9. */
(function () {
  'use strict';
  const K = window.K;
  let campo = null;

  const VERT = `
    attribute vec4 aAzar;
    attribute float aId;
    uniform float uT;
    uniform float uMezcla;
    uniform float uPila;
    uniform vec2 uVentana;
    varying vec2 vUv;
    varying float vTile;
    varying float vLuz;

    void main() {
      // Flujo: un volumen de terrenos que viene hacia la cámara y vuelve a empezar al fondo.
      float z = mod(aAzar.z * 170.0 + uT * (6.0 + 9.0 * aAzar.w), 170.0) - 168.0;
      vec2 xy = (aAzar.xy - 0.5) * vec2(150.0, 86.0);
      // El flujo gira despacio alrededor del eje, más rápido cerca: un remolino, no una cinta.
      float vuelta = uT * (0.035 + 0.05 * aAzar.w) + (z + 168.0) * 0.004;
      xy = vec2(xy.x * cos(vuelta) - xy.y * sin(vuelta), xy.x * sin(vuelta) + xy.y * cos(vuelta)) * vec2(1.0, 0.62);
      xy += vec2(sin(uT * 0.31 + aAzar.x * 40.0), cos(uT * 0.27 + aAzar.y * 40.0)) * 1.6;
      // Una ventana elíptica libre en el centro de la pantalla, donde va el texto: los terrenos la rodean.
      vec2 q = xy / (uVentana * abs(z) + 0.0001);
      float lq = max(length(q), 0.02);
      xy *= sqrt(1.0 + lq * lq) / lq;
      vec3 flujo = vec3(xy, z);
      float giro = (aAzar.w - 0.5) * 0.7 + sin(uT * 0.35 + aAzar.x * 30.0) * 0.16;
      vec2 lado = vec2(position.x * cos(giro) - position.y * sin(giro), position.x * sin(giro) + position.y * cos(giro));
      float niebla = smoothstep(-168.0, -110.0, z) * (1.0 - smoothstep(-44.0, -22.0, z));       // se apagan antes de llegar encima de la cámara
      vec3 enFlujo = flujo + vec3(lado * 4.0 * smoothstep(0.0, 0.5, niebla), 0.0);              // y al apagarse se encogen: no dejan un cuadro oscuro

      // Pila: los primeros uPila terrenos se acuestan uno sobre otro.
      float k = aId / uPila;
      float enPila = step(aId, uPila - 0.5);
      float m = clamp((uMezcla * 1.45 - k) * 3.2, 0.0, 1.0) * enPila;
      m = m * m * (3.0 - 2.0 * m);
      float yaw = (aAzar.x - 0.5) * 0.10;
      vec2 base = vec2(position.x * cos(yaw) - position.y * sin(yaw), position.x * sin(yaw) + position.y * cos(yaw)) * 12.0;
      vec3 pila = vec3(13.0 + (aAzar.y - 0.5) * 0.35, -9.0 + k * 15.0, -36.0 + (aAzar.z - 0.5) * 0.35) + vec3(base.x, 0.0, -base.y);

      vec3 p = mix(enFlujo, pila, m);
      p.y += sin(m * 3.14159) * 9.0;                          // llegan a la pila por arriba
      vLuz = mix(niebla * (1.0 - 0.78 * uMezcla * (1.0 - enPila)), 0.78 + 0.32 * k, m);
      vUv = uv;
      vTile = mod(aId * 7.0 + floor(aAzar.x * 256.0), 256.0);
      gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
    }`;

  const FRAG = `
    precision highp float;
    uniform sampler2D uAtlas;
    uniform float uBrillo;
    varying vec2 vUv;
    varying float vTile;
    varying float vLuz;

    vec3 rampa(float v) {
      // basalto → óxido de cobre → cobre → oro
      vec3 a = vec3(0.05, 0.13, 0.14), b = vec3(0.08, 0.42, 0.40), c = vec3(0.24, 0.74, 0.66),
           d = vec3(0.89, 0.52, 0.28), e = vec3(1.0, 0.86, 0.58);
      if (v < 0.35) return mix(a, b, v / 0.35);
      if (v < 0.60) return mix(b, c, (v - 0.35) / 0.25);
      if (v < 0.82) return mix(c, d, (v - 0.60) / 0.22);
      return mix(d, e, (v - 0.82) / 0.18);
    }

    void main() {
      float col = mod(vTile, 16.0), fil = floor(vTile / 16.0);
      vec2 dentro = clamp(vUv, 0.5 / 32.0, 1.0 - 0.5 / 32.0);
      float v = texture2D(uAtlas, (vec2(col, fil) + dentro) / 16.0).r;
      vec3 c = rampa(v);
      vec2 b = min(vUv, 1.0 - vUv);
      float marco = 1.0 - smoothstep(0.0, 0.035, min(b.x, b.y));
      c = mix(c, vec3(1.0, 0.90, 0.74), marco * 0.38);
      float luz = vLuz * uBrillo;
      if (luz < 0.16) discard;
      gl_FragColor = vec4(mix(vec3(0.043, 0.039, 0.035), c, luz), 1.0);
    }`;

  K.campo = function () {
    if (campo || !K.gl.ok) return campo;
    const d = K.datos.simulados, N = d.n, L = d.lado, porLado = 16, ancho = porLado * L;
    const bytes = K.b64(d.b64);
    const atlas = new Uint8Array(ancho * ancho * 4);
    for (let k = 0; k < N; k++) {
      const cx = (k % porLado) * L, cy = Math.floor(k / porLado) * L;
      for (let f = 0; f < L; f++) {
        for (let c = 0; c < L; c++) {
          const v = bytes[k * L * L + f * L + c], i = ((cy + f) * ancho + cx + c) * 4;
          atlas[i] = atlas[i + 1] = atlas[i + 2] = v;
          atlas[i + 3] = 255;
        }
      }
    }
    const textura = new THREE.DataTexture(atlas, ancho, ancho, THREE.RGBAFormat);
    textura.magFilter = THREE.LinearFilter;
    textura.minFilter = THREE.LinearMipmapLinearFilter;
    textura.generateMipmaps = true;
    textura.needsUpdate = true;

    const M = 2400, plano = new THREE.PlaneGeometry(1, 1);
    const g = new THREE.InstancedBufferGeometry();
    g.index = plano.index;
    g.setAttribute('position', plano.attributes.position);
    g.setAttribute('uv', plano.attributes.uv);
    const azar = K.azar(2026), aAzar = new Float32Array(M * 4), aId = new Float32Array(M);
    for (let i = 0; i < M; i++) {
      aId[i] = i;
      for (let j = 0; j < 4; j++) aAzar[i * 4 + j] = azar();
    }
    g.setAttribute('aAzar', new THREE.InstancedBufferAttribute(aAzar, 4));
    g.setAttribute('aId', new THREE.InstancedBufferAttribute(aId, 1));
    g.instanceCount = M;

    const u = { uT: { value: 0 }, uMezcla: { value: 0 }, uPila: { value: 230 }, uBrillo: { value: 1 }, uAtlas: { value: textura }, uVentana: { value: new THREE.Vector2(0.7, 0.3) } };
    const malla = new THREE.Mesh(g, new THREE.ShaderMaterial({ uniforms: u, vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide }));
    malla.frustumCulled = false;
    const scene = new THREE.Scene();
    scene.add(malla);
    const camera = new THREE.PerspectiveCamera(55, 16 / 9, 0.5, 400);
    const ojo = new THREE.Vector3(), mira = new THREE.Vector3();

    campo = {
      tres: { scene: scene, camera: camera },
      // mezcla: 0 = flujo, 1 = pila. brillo: 1 en la lámina 3, menos en el cierre.
      ventana: function (x, y) { u.uVentana.value.set(x, y); },
      actualizar: function (t, mezcla, brillo) {
        const s = K.suave(mezcla);
        u.uT.value = t;
        u.uMezcla.value = mezcla;
        u.uBrillo.value = brillo;
        ojo.set(K.mezcla(0, -3, s), K.mezcla(0, 24, s), K.mezcla(0, 2, s));
        mira.set(K.mezcla(0, 3.0, s), K.mezcla(0, -3.5, s), K.mezcla(-60, -36, s));
        ojo.x += Math.sin(t * 0.17) * 1.2 * (1 - s); ojo.y += Math.cos(t * 0.13) * 0.8 * (1 - s);   // la cámara respira
        camera.position.copy(ojo);
        camera.lookAt(mira);
      },
    };
    return campo;
  };
})();
