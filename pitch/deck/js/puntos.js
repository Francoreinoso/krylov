/* La nube de puntos que abre y cierra el deck. Es una ilustración generada aquí mismo (no son datos):
   forma 0 = un rajo con sus bancos, forma 1 = una esfera, forma 2 = puntos a la deriva.
   La usan las láminas 1 (el rajo que se escanea), 8 (el rajo se envuelve en una esfera) y 9 (se dispersa detrás del cierre). */
(function () {
  'use strict';
  const K = window.K;
  let P = null;

  const VERT = `
    attribute vec3 aEsf;
    attribute vec3 aLibre;
    attribute vec3 aAzar;
    attribute float aTono;
    uniform float uForma, uT, uBarrido, uEsc, uBrillo;
    varying vec3 vColor;
    varying float vA;
    float suave(float x) { x = clamp(x, 0.0, 1.0); return x * x * (3.0 - 2.0 * x); }
    void main() {
      float f1 = suave(uForma * 1.4 - aAzar.x * 0.4);
      float f2 = suave((uForma - 1.0) * 1.4 - aAzar.x * 0.4);
      vec3 esf = aEsf * (1.0 + 0.025 * sin(uT * 0.9 + aAzar.y * 6.283));
      vec3 libre = aLibre + vec3(sin(uT * 0.11 + aAzar.y * 6.283), cos(uT * 0.09 + aAzar.z * 6.283), sin(uT * 0.07 + aAzar.x * 6.283)) * 2.2;
      vec3 p = mix(mix(position, esf, f1), libre, f2);
      p.y += sin(f1 * 3.14159) * 6.0 * (1.0 - f2);                 // al envolverse, los puntos se levantan

      // El rajo aparece con un barrido desde el centro, como un escáner.
      float d = length(position.xz) / 46.0;
      float avance = uBarrido * 1.25 - d;
      float listo = smoothstep(0.0, 0.05, avance);
      float frente = exp(-(avance / 0.03) * (avance / 0.03)) * (1.0 - f1) * step(uBarrido, 0.995);

      vec3 arena = vec3(0.50, 0.45, 0.38), cobre = vec3(0.91, 0.52, 0.27), oro = vec3(1.0, 0.80, 0.42), oxido = vec3(0.21, 0.76, 0.68);
      vec3 cRajo = mix(arena * 0.6, cobre, smoothstep(0.03, 0.55, aTono));
      cRajo = mix(cRajo, oro, smoothstep(0.78, 1.0, aTono));
      vec3 cEsf = mix(cobre, oxido, smoothstep(-0.4, 0.6, aEsf.y / 12.5 + (aAzar.z - 0.5) * 0.5));
      vec3 cLibre = mix(cobre, arena, aAzar.z);
      vColor = mix(mix(cRajo, cEsf, f1), cLibre, f2) + vec3(1.0, 0.86, 0.62) * frente * 0.7;

      vec4 mv = modelViewMatrix * vec4(p, 1.0);
      vec3 nv = normalize(normalMatrix * normalize(aEsf));
      float cara = mix(1.0, 0.18 + 0.82 * smoothstep(-0.35, 0.5, nv.z), f1 * (1.0 - f2));
      float aRajo = (0.36 + 0.74 * smoothstep(0.02, 0.45, aTono)) * listo;
      float aDeriva = step(0.5, aAzar.y) * 0.7;
      float titila = 0.82 + 0.18 * sin(uT * 1.4 + aAzar.y * 50.0);
      vA = mix(mix(aRajo, 0.85, f1), aDeriva, f2) * cara * uBrillo * titila + frente * 0.45;
      gl_PointSize = (0.12 + 0.08 * aAzar.z + frente * 0.08) * uEsc / -mv.z;
      gl_Position = projectionMatrix * mv;
    }`;

  const FRAG = `
    precision highp float;
    varying vec3 vColor;
    varying float vA;
    void main() {
      vec2 d = gl_PointCoord - 0.5;
      float r = dot(d, d);
      if (r > 0.25 || vA < 0.004) discard;
      gl_FragColor = vec4(vColor * vA * (1.0 - r * 2.6), 1.0);
    }`;

  // Altura del rajo: bancos concéntricos sobre una elipse deformada. Devuelve [altura, tono].
  function rajo(x, z) {
    const ang = Math.atan2(z, x);
    const d = Math.hypot(x / 1.32, z) * (1 + 0.10 * Math.sin(ang * 3 + 0.6) + 0.055 * Math.sin(ang * 5 + 2.1));
    const u = (19.5 - d) / 2.25, niveles = 8;
    if (u <= 0) {
      const lomas = 0.6 * Math.sin(x * 0.13 + 1.3) * Math.cos(z * 0.11) + 0.35 * Math.sin(x * 0.31 + z * 0.27);
      const cerro = Math.max(0, d - 27) * 0.42 * (0.55 + 0.45 * Math.sin(ang * 2 + 1));
      return [lomas + cerro, 0.0];
    }
    const n = Math.min(Math.floor(u), niveles), f = n >= niveles ? 0 : u - n;
    const talud = K.suave((f - 0.7) / 0.3);
    return [-(n + talud) * 2.25, Math.min(1, (n + talud) / niveles + 0.06)];
  }

  K.puntos = function () {
    if (P || !K.gl.ok) return P;
    const azar = K.azar(1902), L = 33, paso = 0.272, pos = [], esf = [], libre = [], al = [], tono = [];
    for (let x = -L; x <= L; x += paso) {
      for (let z = -L; z <= L; z += paso) {
        const px = x + (azar() - 0.5) * paso, pz = z + (azar() - 0.5) * paso, h = rajo(px, pz);
        pos.push(px, h[0], pz);
        tono.push(h[1]);
        // Esfera: el centro del rajo va al polo de arriba y el borde al de abajo, repartido por área.
        const r = Math.min(1, Math.max(Math.abs(px), Math.abs(pz)) / L), fi = Math.atan2(pz, px), c = 1 - 2 * r * r, s = Math.sqrt(Math.max(0, 1 - c * c));
        esf.push(12.5 * s * Math.cos(fi), 12.5 * c - 4, 12.5 * s * Math.sin(fi));
        libre.push((azar() - 0.5) * 150, (azar() - 0.5) * 84 - 4, -55 + azar() * 70);
        al.push(azar(), azar(), azar());
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
    g.setAttribute('aEsf', new THREE.BufferAttribute(new Float32Array(esf), 3));
    g.setAttribute('aLibre', new THREE.BufferAttribute(new Float32Array(libre), 3));
    g.setAttribute('aAzar', new THREE.BufferAttribute(new Float32Array(al), 3));
    g.setAttribute('aTono', new THREE.BufferAttribute(new Float32Array(tono), 1));
    const u = { uForma: { value: 0 }, uT: { value: 0 }, uBarrido: { value: 0 }, uEsc: { value: 2000 }, uBrillo: { value: 1 } };
    const nube = new THREE.Points(g, new THREE.ShaderMaterial({
      uniforms: u, vertexShader: VERT, fragmentShader: FRAG, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
    }));
    nube.frustumCulled = false;
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(32, 16 / 9, 1, 400);
    scene.add(nube);

    // Estado animable: forma, barrido, brillo y encuadre (dx mueve la figura a la derecha del texto).
    const s = { forma: 0, barrido: 0, brillo: 1, giro: 0.5, R: 58, el: 0.74, ty: -8, dx: -430 };
    P = {
      tres: { scene: scene, camera: camera }, s: s, total: tono.length,
      ajustar: function () { u.uEsc.value = (K.gl.renderer.getPixelRatio() * 1080) / (2 * Math.tan((16 * Math.PI) / 180)); },
      cuadro: function (t, dt) {
        s.giro += dt * 0.06;
        u.uT.value = t; u.uForma.value = s.forma; u.uBarrido.value = s.barrido; u.uBrillo.value = s.brillo;
        nube.rotation.y = s.giro;
        camera.setViewOffset(1920, 1080, s.dx, 0, 1920, 1080);
        camera.position.set(0, s.ty + Math.sin(s.el) * s.R, Math.cos(s.el) * s.R);
        camera.lookAt(0, s.ty, 0);
      },
    };
    return P;
  };
})();
