/* 4 · El mapa   y   5 · ¿Dónde mido?
   El terreno real en 3D. Altura = zinc estimado; color = decisión; capa translúcida = rango creíble; puntos = mediciones reales.
   Todo sale de datos.js (api.analizar, api.donde_medir y los mapas rehechos por la red). Las dos láminas comparten la escena. */
(function () {
  'use strict';
  const K = window.K;
  const F = 0.0062;                    // unidades de escena por mg/kg
  let M = null;

  const VERT = `
    attribute vec2 aPos;
    attribute vec2 aAlt;
    attribute vec2 aTope;
    attribute vec2 aEst;
    attribute float aRet;
    attribute float aOrden;
    attribute float aCambia;
    uniform float uCrece;
    uniform float uMorf;
    uniform float uEsVidrio;
    varying vec3 vN;
    varying vec3 vM;
    varying vec2 vEst;
    varying float vK;
    varying float vY;
    varying float vCrece;
    varying float vCambia;

    void main() {
      float k = clamp(uMorf * 1.7 - aRet * 0.7, 0.0, 1.0);
      k = k * k * (3.0 - 2.0 * k);
      float crece = clamp(uCrece * 1.8 - aOrden * 0.8, 0.0, 1.0);
      crece = 1.0 - pow(1.0 - crece, 3.0);
      float h = max(mix(aAlt.x, aAlt.y, k) * crece, 0.07);
      float y = position.y * h;
      float ancho = 0.9;
      if (uEsVidrio > 0.5) {
        float tope = max(mix(aTope.x, aTope.y, k) * crece, h);
        y = h + position.y * (tope - h);
        ancho = 0.82;
      }
      vec3 p = vec3(aPos.x + position.x * ancho, y, aPos.y + position.z * ancho);
      vN = normal; vM = p; vEst = aEst; vK = k; vY = position.y; vCrece = crece;
      vCambia = aCambia * sin(3.14159 * k);
      gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0);
    }`;

  const COLOR = `
    vec3 colorDe(float e, vec3 m) {
      if (e < 0.5) return vec3(0.122, 0.616, 0.380);                         // no hace falta  (#1f9d61)
      if (e > 1.5) return vec3(0.851, 0.247, 0.247);                         // hay que limpiar (#d93f3f)
      float raya = step(0.5, fract((m.x + m.z + m.y) * 1.3));                // no sabemos: ámbar achurado (#e0a100)
      return mix(vec3(0.878, 0.631, 0.0), vec3(1.0, 0.87, 0.55), raya * 0.8);
    }`;

  const FRAG = `
    precision highp float;
    varying vec3 vN;
    varying vec3 vM;
    varying vec2 vEst;
    varying float vK;
    varying float vY;
    varying float vCrece;
    varying float vCambia;
    ${COLOR}
    void main() {
      vec3 c = mix(colorDe(vEst.x, vM), colorDe(vEst.y, vM), vK);
      c = mix(vec3(0.15, 0.16, 0.27), c, smoothstep(0.0, 0.3, vCrece));
      float d = max(dot(vN, normalize(vec3(0.5, 0.85, 0.3))), 0.0);
      float luz = 0.40 + 0.62 * d;
      float grad = vN.y > 0.5 ? 1.0 : mix(0.5, 1.0, vY);
      c = c * luz * grad + vec3(1.0) * vCambia * 0.7;
      gl_FragColor = vec4(c, 1.0);
    }`;

  const FRAG_VIDRIO = `
    precision highp float;
    uniform float uVidrio;
    varying vec3 vN;
    varying vec3 vM;
    varying vec2 vEst;
    varying float vK;
    varying float vY;
    ${COLOR}
    void main() {
      vec3 c = mix(colorDe(vEst.x, vM), colorDe(vEst.y, vM), vK);
      c = mix(c, vec3(1.0), 0.35);
      float a = vN.y > 0.5 ? 0.30 : (vN.y < -0.5 ? 0.0 : 0.035 + 0.11 * vY * vY);
      gl_FragColor = vec4(c * a * uVidrio, 1.0);
    }`;

  function construir() {
    const D = K.datos, T = D.terreno, n = T.dentro.length, nx = T.nx;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(33, 16 / 9, 1, 400);
    camera.setViewOffset(1920, 1080, -400, 0, 1920, 1080);          // el terreno, a la derecha del texto

    // ----- geometría de los bloques -----
    const px = new Float32Array(n), pz = new Float32Array(n), indiceDe = {};
    let cx = 0, cz = 0;
    for (let i = 0; i < n; i++) {
      const idx = T.dentro[i];
      px[i] = (idx % nx) - nx / 2 + 0.5;
      pz[i] = -(Math.floor(idx / nx) - nx / 2 + 0.5);
      cx += px[i] / n; cz += pz[i] / n;
      indiceDe[idx] = i;
    }
    function aEscena(x, y) {
      return { x: (x - T.x0) / T.lado - nx / 2 - cx, z: -((y - T.y0) / T.lado - nx / 2) - cz };
    }
    function bloqueDe(x, y) {
      const c = Math.floor((x - T.x0) / T.lado), f = Math.floor((y - T.y0) / T.lado);
      return indiceDe[f * nx + c];
    }

    const aPos = new Float32Array(n * 2), aAlt = new Float32Array(n * 2), aTope = new Float32Array(n * 2),
      aEst = new Float32Array(n * 2), aRet = new Float32Array(n), aOrden = new Float32Array(n), aCambia = new Float32Array(n);
    let rMax = 0;
    for (let i = 0; i < n; i++) {
      px[i] -= cx; pz[i] -= cz;
      aPos[i * 2] = px[i]; aPos[i * 2 + 1] = pz[i];
      rMax = Math.max(rMax, Math.hypot(px[i], pz[i]));
    }
    for (let i = 0; i < n; i++) aOrden[i] = Math.hypot(px[i], pz[i]) / rMax;

    const atributos = {
      aPos: new THREE.InstancedBufferAttribute(aPos, 2), aAlt: new THREE.InstancedBufferAttribute(aAlt, 2),
      aTope: new THREE.InstancedBufferAttribute(aTope, 2), aEst: new THREE.InstancedBufferAttribute(aEst, 2),
      aRet: new THREE.InstancedBufferAttribute(aRet, 1), aOrden: new THREE.InstancedBufferAttribute(aOrden, 1),
      aCambia: new THREE.InstancedBufferAttribute(aCambia, 1),
    };
    function geometria() {
      const caja = new THREE.BoxGeometry(1, 1, 1);
      caja.translate(0, 0.5, 0);
      const g = new THREE.InstancedBufferGeometry();
      g.index = caja.index;
      g.setAttribute('position', caja.attributes.position);
      g.setAttribute('normal', caja.attributes.normal);
      Object.keys(atributos).forEach(function (k) { g.setAttribute(k, atributos[k]); });
      g.instanceCount = n;
      return g;
    }
    const u = { uCrece: { value: 0 }, uMorf: { value: 0 }, uVidrio: { value: 0 } };
    const solido = new THREE.Mesh(geometria(), new THREE.ShaderMaterial({
      uniforms: { uCrece: u.uCrece, uMorf: u.uMorf, uEsVidrio: { value: 0 } }, vertexShader: VERT, fragmentShader: FRAG,
    }));
    const vidrio = new THREE.Mesh(geometria(), new THREE.ShaderMaterial({
      uniforms: { uCrece: u.uCrece, uMorf: u.uMorf, uVidrio: u.uVidrio, uEsVidrio: { value: 1 } }, vertexShader: VERT, fragmentShader: FRAG_VIDRIO,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    solido.frustumCulled = vidrio.frustumCulled = false;
    vidrio.renderOrder = 5;
    scene.add(solido, vidrio);

    // capa actual (desde) y destino (hacia) de cada bloque
    let actual = T;
    function poner(capa, componente) {
      for (let i = 0; i < n; i++) {
        aAlt[i * 2 + componente] = capa.media[i] * F;
        aTope[i * 2 + componente] = capa.alto[i] * F;
        aEst[i * 2 + componente] = capa.estado[i];
      }
    }
    function subir() { atributos.aAlt.needsUpdate = atributos.aTope.needsUpdate = atributos.aEst.needsUpdate = atributos.aRet.needsUpdate = atributos.aCambia.needsUpdate = true; }
    poner(T, 0); poner(T, 1);

    // ----- piso, orilla del río y nivel que obliga a limpiar -----
    const piso = new THREE.GridHelper(40, 40, 0x2b2d4c, 0x181a2d);
    piso.position.y = -0.02;
    scene.add(piso);

    const orilla = new Float32Array(T.orilla.length * 3);
    const orillas = [];
    T.orilla.forEach(function (p, i) {
      const e = aEscena(p[0], p[1]);
      orilla[i * 3] = e.x; orilla[i * 3 + 1] = 0.1; orilla[i * 3 + 2] = e.z;
      orillas.push(e);
    });
    const gOrilla = new THREE.BufferGeometry();
    gOrilla.setAttribute('position', new THREE.BufferAttribute(orilla, 3));
    scene.add(new THREE.Points(gOrilla, new THREE.PointsMaterial({ color: 0x57b6ff, size: 1.5, transparent: true, opacity: 0.22, depthWrite: false })));
    scene.add(new THREE.Points(gOrilla, new THREE.PointsMaterial({ color: 0x8fd0ff, size: 0.5, transparent: true, opacity: 1 })));

    const yUmbral = T.umbral * F;
    const mPlano = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
    const plano = new THREE.Mesh(new THREE.PlaneGeometry(36, 36), mPlano);
    plano.rotation.x = -Math.PI / 2;
    plano.position.y = yUmbral;
    plano.renderOrder = 4;
    const mBorde = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
    const borde = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-18, yUmbral, -18), new THREE.Vector3(18, yUmbral, -18), new THREE.Vector3(18, yUmbral, 18), new THREE.Vector3(-18, yUmbral, 18),
    ]), mBorde);
    scene.add(plano, borde);

    // ----- las 155 mediciones reales -----
    const np = T.puntos.length, azar = K.azar(155);
    const mEsfera = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 1 });
    const esferas = new THREE.InstancedMesh(new THREE.SphereGeometry(0.21, 12, 8), mEsfera, np);
    esferas.frustumCulled = false;
    const puntos = T.puntos.map(function (p) {
      const e = aEscena(p[0], p[1]);
      return { x: e.x, y: p[2] * F, z: e.z, demora: azar() * 1.5 };
    });
    const tallos = new Float32Array(np * 6);
    puntos.forEach(function (p, i) { tallos.set([p.x, 0, p.z, p.x, p.y, p.z], i * 6); });
    const gTallos = new THREE.BufferGeometry();
    gTallos.setAttribute('position', new THREE.BufferAttribute(tallos, 3));
    const mTallos = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 });
    scene.add(esferas, new THREE.LineSegments(gTallos, mTallos));
    const matriz = new THREE.Matrix4();

    // ----- los tres pines de «¿Dónde mido?» -----
    const pines = D.donde.candidatas.map(function (c, j) {
      const e = aEscena(c.x, c.y), i = bloqueDe(c.x, c.y);
      const grupo = new THREE.Group();
      const cabeza = new THREE.Mesh(new THREE.SphereGeometry(0.62, 24, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }));
      cabeza.position.y = 2.5;
      const aguja = new THREE.Mesh(new THREE.ConeGeometry(0.34, 2.3, 18), new THREE.MeshBasicMaterial({ color: 0xdadbff }));
      aguja.rotation.x = Math.PI;
      aguja.position.y = 1.15;
      const mAnillo = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
      const anillo = new THREE.Mesh(new THREE.RingGeometry(0.8, 1.02, 48), mAnillo);
      anillo.rotation.x = -Math.PI / 2;
      grupo.add(cabeza, aguja);
      grupo.visible = false;
      scene.add(grupo, anillo);
      return { c: c, i: i, x: e.x, z: e.z, grupo: grupo, anillo: anillo, mAnillo: mAnillo, cabeza: cabeza, demora: j * 0.32, etq: null };
    });

    // ----- estado animable -----
    const s = {
      crece: 0, vidrio: 0, plano: 0, caida: 0, tallos: 0, puntos: 1, pines: 0, morf: 0,
      az: -0.42, el: 0.5, R: 61, ty: 0.6, giro: 0, fase: 0, arrastre: 0, arrastreEl: 0,
    };
    const ojo = new THREE.Vector3();

    function altura(i) {                       // altura actual de la columna i, para apoyar los pines
      const k = u.uMorf.value;
      return K.mezcla(aAlt[i * 2], aAlt[i * 2 + 1], k) * s.crece;
    }

    M = {
      tres: { scene: scene, camera: camera }, s: s, pines: pines, T: T, D: D, sel: 'A', nivel: 'alto', orillas: orillas,
      yUmbral: yUmbral,
      // Rehace el mapa hacia otra capa (la respuesta de la red con una medición más). `desde`: pin desde donde se propaga.
      morfar: function (capa, desde, inst) {
        poner(actual, 0);
        poner(capa, 1);
        let dMax = 1e-6;
        for (let i = 0; i < n; i++) {
          aRet[i] = desde ? Math.hypot(px[i] - desde.x, pz[i] - desde.z) : aOrden[i];
          dMax = Math.max(dMax, aRet[i]);
          aCambia[i] = actual.estado[i] !== capa.estado[i] ? 1 : 0;
        }
        for (let i = 0; i < n; i++) aRet[i] = Math.min(1, aRet[i] / Math.min(dMax, 14));
        subir();
        actual = capa;
        s.morf = 0;
        K.anim(s, { morf: 1 }, 2.6, inst, 'power1.inOut');
      },
      capaActual: function () { return actual; },
      cuadro: function (t, dt, lamina) {
        s.fase += dt;
        s.giro = 0.2 * Math.sin(s.fase * 0.21);          // la cámara se mece: el encuadre no se pierde
        u.uCrece.value = s.crece;
        u.uMorf.value = s.morf;
        u.uVidrio.value = s.vidrio;
        mPlano.opacity = 0.05 * s.plano;
        mBorde.opacity = 0.42 * s.plano;
        mTallos.opacity = 0.26 * s.tallos * s.puntos;
        mEsfera.opacity = s.puntos;

        const tau = s.caida * 3.0;
        for (let i = 0; i < np; i++) {
          const p = puntos[i], k = K.fuera((tau - p.demora) / 1.3);
          matriz.makeTranslation(p.x, p.y + (1 - k) * 34, p.z);
          if (k <= 0) matriz.makeScale(0, 0, 0);
          esferas.setMatrixAt(i, matriz);
        }
        esferas.instanceMatrix.needsUpdate = true;

        const tp = s.pines * 2.4;
        pines.forEach(function (p) {
          const k = K.fuera((tp - p.demora) / 1.1), y0 = p.i == null ? 0 : altura(p.i);
          p.grupo.visible = k > 0;
          p.grupo.position.set(p.x, y0 + 0.1 + (1 - k) * 36, p.z);
          const pulso = (t * 0.7 + p.demora) % 1;
          p.anillo.position.set(p.x, y0 + 0.12, p.z);
          p.anillo.scale.setScalar(1 + pulso * 2.4);
          p.mAnillo.opacity = k >= 1 ? (1 - pulso) * 0.85 : 0;
          const es = M.sel === p.c.etiqueta && lamina === 'donde';
          p.cabeza.scale.setScalar(es ? 1.25 : 1);
        });

        const az = s.az + s.giro + s.arrastre, el = K.acotar(s.el + s.arrastreEl, 0.18, 1.35);
        ojo.set(Math.sin(az) * Math.cos(el) * s.R, s.ty + Math.sin(el) * s.R, Math.cos(az) * Math.cos(el) * s.R);
        camera.position.copy(ojo);
        camera.lookAt(0, s.ty, 0);
        camera.updateMatrixWorld();
      },
    };

    // Arrastrar con el mouse gira la cámara (para las preguntas).
    const lienzo = K.gl.renderer.domElement;
    let agarre = null;
    lienzo.addEventListener('pointerdown', function (ev) { agarre = { x: ev.clientX, y: ev.clientY, a: s.arrastre, e: s.arrastreEl }; lienzo.setPointerCapture(ev.pointerId); });
    lienzo.addEventListener('pointermove', function (ev) {
      if (!agarre) return;
      s.arrastre = agarre.a - (ev.clientX - agarre.x) * 0.006 / K.escala;
      s.arrastreEl = agarre.e + (ev.clientY - agarre.y) * 0.004 / K.escala;
    });
    lienzo.addEventListener('pointerup', function () { agarre = null; });
    lienzo.addEventListener('pointercancel', function () { agarre = null; });
    return M;
  }

  function terreno() { return M || (K.gl.ok ? construir() : null); }

  function etiqueta(capa, clase, html) {
    const el = document.createElement('div');
    el.className = 'etq ' + clase;
    el.innerHTML = html;
    capa.appendChild(el);
    return el;
  }
  function colocar(el, x, y, z, camara, dx, dy) {
    const p = K.proyectar(x, y, z, camara);
    el.style.transform = 'translate(' + (p.x + (dx || 0)).toFixed(1) + 'px,' + (p.y + (dy || 0)).toFixed(1) + 'px) translate(-50%, -100%)';
  }

  // ============================== 4 · El mapa ==============================
  K.registrar('mapa', {
    tres: null, interactivo: true, tQuieto: 0,
    crear: function (L) {
      const m = (this.m = terreno());
      if (!m) return;
      this.tres = m.tres;
      const capa = L.querySelector('#etq-mapa');
      this.rio = etiqueta(capa, 'linea', 'Río Mosa');
      this.umbral = etiqueta(capa, 'umbral', K.miles(m.T.umbral) + ' ' + m.T.unidad_valor + ' · nivel que obliga a limpiar');
    },
    entrar: function () {
      const m = this.m;
      if (!m) return;
      if (m.capaActual() !== m.T) m.morfar(m.T, null, true);
      Object.assign(m.s, { pines: 0, morf: 1, arrastre: 0, arrastreEl: 0 });
      K.anim(m.s, { az: -0.42, el: 0.5, R: 61, ty: 0.6 }, 1.8, false);
    },
    paso: function (p, inst) {
      const m = this.m;
      if (!m) return;
      const s = m.s;
      if (p === 0) {
        K.anim(s, { crece: 0, vidrio: 0, plano: 0, puntos: 1 }, 0.5, inst);
        s.caida = 0; s.tallos = 0;
        K.anim(s, { caida: 1 }, 3.0, inst, 'none', 0.3);
        K.anim(s, { tallos: 1 }, 1.0, inst, 'power1.out', 2.4);
      } else {
        K.anim(s, { caida: 1, tallos: 1 }, 0.4, inst);
        K.anim(s, { crece: 1 }, 2.8, inst, 'power1.inOut');
        K.anim(s, { plano: 1 }, 1.2, inst, 'power1.out', 1.6);
        K.anim(s, { vidrio: p >= 2 ? 1 : 0 }, 1.4, inst);
      }
      this.rio.classList.add('ver');
      this.umbral.classList.toggle('ver', p >= 1);
    },
    cuadro: function (t, dt) {
      const m = this.m;
      if (!m) return;
      m.cuadro(t, dt, 'mapa');
      const cam = m.tres.camera;
      // «Río Mosa»: junto al punto de la orilla que queda más abajo en pantalla (el más cercano a la cámara).
      let mejor = null;
      for (let i = 0; i < m.orillas.length; i += 6) {
        const p = K.proyectar(m.orillas[i].x, 0.1, m.orillas[i].z, cam);
        if (!p.detras && p.x > 760 && p.x < 1800 && p.y < 980 && (!mejor || p.y > mejor.y)) mejor = p;
      }
      if (mejor) this.rio.style.transform = 'translate(' + (mejor.x - 20).toFixed(1) + 'px,' + (mejor.y + 16).toFixed(1) + 'px) translate(-100%, 0)';
      // El nivel de 720 mg/kg: en la esquina o el borde del plano que se vea más a la derecha.
      const y = m.yUmbral, bordes = [[18, -18], [18, 0], [0, -18], [-18, -18], [18, 18], [-18, 18]];
      let e = null;
      bordes.forEach(function (q) {
        const p = K.proyectar(q[0], y, q[1], cam);
        if (!p.detras && p.x > 900 && p.x < 1880 && p.y > 150 && p.y < 980 && (!e || p.x > e.x)) e = p;
      });
      if (e) this.umbral.style.transform = 'translate(' + e.x.toFixed(1) + 'px,' + e.y.toFixed(1) + 'px) translate(-100%, -135%)';
    },
  });

  // ============================== 5 · ¿Dónde mido? ==============================
  K.registrar('donde', {
    tres: null, interactivo: true, tQuieto: 0,
    crear: function (L) {
      const m = (this.m = terreno()), yo = this;
      if (!m) return;
      this.tres = m.tres;
      this.L = L;
      const capa = L.querySelector('#etq-donde');
      m.pines.forEach(function (p) {
        p.etq = etiqueta(capa, 'pin', '<b>Medir en ' + p.c.etiqueta + ' vale</b><span>US$ ' + K.miles(p.c.valor_de_medir) + '</span>');
        p.etq.addEventListener('click', function () {
          m.sel = p.c.etiqueta;
          if (K.donde().paso === 0) K.siguiente(); else yo.medir(false);
        });
      });
      this.texto = L.querySelector('#texto-medicion');
      this.despues = L.querySelector('#cuesta-despues');
      this.botones = Array.prototype.slice.call(L.querySelectorAll('#opciones-medicion button'));
      this.botones.forEach(function (b) {
        b.addEventListener('click', function () { m.nivel = b.dataset.nivel; yo.medir(false); });
      });
    },
    entrar: function () {
      const m = this.m;
      if (!m) return;
      m.sel = 'A'; m.nivel = 'alto';
      Object.assign(m.s, { crece: 1, vidrio: 1, plano: 1, caida: 1, tallos: 1, arrastre: 0, arrastreEl: 0 });
    },
    medir: function (inst) {
      const m = this.m, pin = m.pines.filter(function (p) { return p.c.etiqueta === m.sel; })[0];
      const capa = m.D.mediciones[m.sel][m.nivel], antes = m.capaActual().costo_de_no_saber;
      m.morfar(capa, pin, inst);
      const palabra = { bajo: 'bajo', medio: 'medio', alto: 'alto' }[m.nivel];
      this.texto.innerHTML = '<b>Mido en ' + m.sel + '.</b> Sale ' + palabra + ': ' + K.miles(pin.c.resultados_posibles[m.nivel]) + ' ' + m.T.unidad_valor + '.';
      if (this.cuenta) this.cuenta.kill();
      this.cuenta = K.contar(this.despues, antes, capa.costo_de_no_saber, 2.2, K.miles, inst);
      this.botones.forEach(function (b) { b.classList.toggle('sel', b.dataset.nivel === m.nivel); });
      m.pines.forEach(function (p) { p.etq.classList.toggle('sel', p.c.etiqueta === m.sel); });
    },
    paso: function (p, inst) {
      const m = this.m;
      if (!m) return;
      const s = m.s;
      K.anim(s, { puntos: 0.35 }, 0.8, inst);
      if (p === 0) {
        if (m.capaActual() !== m.T) m.morfar(m.T, null, true);
        s.morf = 1;
        K.anim(s, { az: -0.62, el: 0.74, R: 68, ty: -1.2 }, 2.4, inst);
        if (!inst) s.pines = 0;
        K.anim(s, { pines: 1 }, 2.4, inst, 'none', 0.5);
        m.pines.forEach(function (pin) { pin.etq.classList.remove('sel'); });
      } else {
        K.anim(s, { pines: 1 }, 0.3, inst);
        K.anim(s, { az: -0.72, el: 0.8, R: 64, ty: -1.2 }, 2.2, inst);
        this.medir(inst);
      }
    },
    cuadro: function (t, dt) {
      const m = this.m;
      if (!m) return;
      m.cuadro(t, dt, 'donde');
      const tp = m.s.pines * 2.4;
      m.pines.forEach(function (p) {
        const visto = (tp - p.demora) / 1.1 >= 1;
        p.etq.classList.toggle('ver', visto);
        const q = K.proyectar(p.grupo.position.x, p.grupo.position.y + 2.5, p.grupo.position.z, m.tres.camera);
        const lado = { A: [-34, 0, '-100%, -50%'], B: [34, 30, '0, -50%'], C: [0, -40, '-50%, -100%'] }[p.c.etiqueta] || [0, -40, '-50%, -100%'];
        p.etq.style.transform = 'translate(' + (q.x + lado[0]).toFixed(1) + 'px,' + (q.y + lado[1]).toFixed(1) + 'px) translate(' + lado[2] + ')';
      });
    },
  });
})();
