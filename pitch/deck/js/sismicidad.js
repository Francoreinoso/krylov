/* 11 · Los túneles después de la explosión («Tras la explosión, ¿puede volver a entrar la gente?»).
   Una minera subterránea cortada a la altura de sus túneles: el macizo de roca es una losa densa de puntos (y dos estratos
   más tenues arriba y abajo), y en ella están tallados el túnel principal y los ocho sectores del archivo.
   Lo que se mueve sale del archivo del caso (datos.js → series.sismicidad):
   - a la hora cero, la explosión en el frente del túnel principal: dos frentes de onda cruzan la roca (los puntos se corren
     cuando pasa el frente y vuelven), el polvo avanza por el túnel y se asienta, y la roca rota cae y queda apilada;
   - después, cada temblor del archivo, a su hora y con su magnitud: una sacudida que sale de su sector y mueve la roca de
     alrededor. Si es fuerte (magnitud 1,0 o más), la onda es grande y cae roca del techo de ese sector;
   - el túnel de cada sector lleva el color de la decisión de Krylov, y el foco (js/foco.js) viaja de sector en sector con
     su tarjeta; la cámara lo acompaña.
   Dónde cae cada temblor dentro de su sector es una ilustración: el archivo trae la hora y la magnitud, no la ubicación. */
(function () {
  'use strict';
  const K = window.K, D3 = K.d3;
  const NO = 12;                                   // frentes de onda a la vez: dos de la explosión y diez de temblores
  const DURA = 13, ESPERA = 4.6, PARTE = 1.0;      // segundos: lo que dura el archivo, lo que se queda al final, y cuándo explota
  const LARGO = 5.6, G = 7.0, PISO = -0.5;
  const FRENTE = [9.3, -0.05, 0];

  // Lo que comparten todos los materiales: los frentes de onda. Cada punto se corre hacia afuera cuando el frente pasa por él.
  const ONDAS = `
    #define NO ${NO}
    uniform vec4 uOnda[NO];          // centro del frente (x, y, z) y su radio ahora
    uniform vec3 uOndaF[NO];         // cuánto mueve, qué tan ancho es el frente, cuánto enciende
    uniform float uS;                // segundos de animación desde la explosión
    uniform float uVida;             // 1 mientras corre el archivo; baja a 0 antes de volver a empezar
    vec3 sacude(vec3 p, out float luz) {
      vec3 d = vec3(0.0);
      luz = 0.0;
      for (int i = 0; i < NO; i++) {
        vec3 r = p - uOnda[i].xyz;
        float dist = length(r), z = (dist - uOnda[i].w) / uOndaF[i].y, g = exp(-z * z) * uOndaF[i].x;
        d += (r / max(dist, 0.05)) * g + vec3(0.0, g * 0.7, 0.0);
        luz += g * uOndaF[i].z;
      }
      return d;
    }`;

  if (!document.getElementById('estilo-sismicidad')) {
    const st = document.createElement('style');
    st.id = 'estilo-sismicidad';
    st.textContent =
      '#l-sismicidad .sis-reloj { position: absolute; right: 110px; top: 88px; text-align: right; opacity: 0; transition: opacity .6s ease; pointer-events: none; }' +
      '#l-sismicidad .sis-reloj.ver { opacity: 1; }' +
      '#l-sismicidad .sis-reloj b { display: block; font-family: var(--titulo); font-weight: 800; font-size: 60px; line-height: 1; color: var(--tinta); font-variant-numeric: tabular-nums; white-space: nowrap; }' +
      '#l-sismicidad .sis-reloj span { display: block; margin-top: 6px; font-family: var(--texto); font-size: 24px; font-weight: 500; color: var(--suave); white-space: nowrap; }' +
      '.quieto #l-sismicidad .sis-reloj { transition: none; }';
    document.head.appendChild(st);
  }

  K.registrar('sismicidad', {
    tres: null, tQuieto: PARTE + DURA + 1.6,
    crear: function (L) {
      const S = (this.S = K.datos.series.sismicidad), n = (this.n = S.unidades.length), R = S.respuesta;
      this.horas = S.horizonte || 6;
      this.fuerte = S.umbral == null ? 1 : S.umbral;
      L.classList.toggle('con-respuesta', !!R);
      this.indice = {};
      S.unidades.forEach(function (un, i) { this.indice[un.id] = i; }, this);

      // El foco: parte por el sector en duda más cercano al punto de corte y va alternando colores.
      const corte = R && R.punto_de_corte != null ? R.punto_de_corte : 0.5;
      const por = { en_duda: [], no_actuar: [], actuar: [] };
      S.unidades.forEach(function (un) { const r = R && R.unidades[un.id]; if (r) por[r.estado].push(un.id); });
      const cerca = function (a, b) { return Math.abs(R.unidades[a].p - corte) - Math.abs(R.unidades[b].p - corte); };
      por.en_duda.sort(cerca); por.actuar.sort(cerca); por.no_actuar.sort(cerca);
      const orden = [], filas = [por.en_duda, por.actuar, por.no_actuar];
      for (let k = 0; orden.length < n && k < n; k++) filas.forEach(function (f) { if (f[k]) orden.push(f[k]); });
      this.F = K.foco.crear(L, 'sismicidad');
      K.foco.recorrer(this.F, orden);

      // el reloj del archivo, arriba a la derecha
      this.relojEl = document.createElement('div');
      this.relojEl.className = 'sis-reloj';
      this.relojEl.innerHTML = '<b></b><span>después de la explosión</span>';
      L.querySelector('.capa-etq').appendChild(this.relojEl);
      this.relojNum = this.relojEl.firstChild;
      if (!K.gl.ok) return;

      const B = (this.B = D3.base(30)), azar = K.azar(53);
      const segPorHora = DURA / this.horas;
      // ---- dónde va cada cosa ----
      const sector = (this.sector = []);
      for (let k = 0; k < n; k++) {
        const x = -6.6 + Math.floor(k / 2) * 4.4, lado = k % 2 ? 1 : -1;
        sector.push({ x: x, lado: lado, z0: lado * 0.95, z1: lado * (0.95 + LARGO), tinte: D3.tinteDe(S, S.unidades[k].id, [0.5, 0.45, 0.38]) });
      }
      // distancia de un punto de la losa a la pared del túnel más cercano (negativa: adentro de un túnel)
      const aTunel = function (x, z) {
        let d = x < -9 ? Math.hypot(x + 9, Math.max(0, Math.abs(z) - 0.82)) : x > FRENTE[0] ? Math.hypot(x - FRENTE[0], Math.max(0, Math.abs(z) - 0.82)) : Math.abs(z) - 0.82;
        for (let k = 0; k < n; k++) {
          const s = sector[k], zz = z * s.lado, dx = Math.abs(x - s.x) - 0.7;
          const dk = zz < 0.82 ? 9 : zz > 0.95 + LARGO ? Math.hypot(Math.max(0, dx), zz - 0.95 - LARGO) : dx;
          d = Math.min(d, dk);
        }
        return d;
      };

      // ---- los frentes de onda ----
      this.uOnda = { value: [] }; this.uOndaF = { value: [] };
      for (let i = 0; i < NO; i++) { this.uOnda.value.push(new THREE.Vector4(0, 0, 0, -100)); this.uOndaF.value.push(new THREE.Vector3(0, 1, 0)); }
      this.uS = { value: -1 }; this.uVida = { value: 1 };
      const ondas = { uOnda: this.uOnda, uOndaF: this.uOndaF, uS: this.uS, uVida: this.uVida };

      // ---- el macizo, como un bloque de roca abierto a la altura del piso de los túneles: la cara del corte es una losa
      //      densa de puntos (los túneles quedan como canales oscuros), las dos caras del frente muestran sus estratos,
      //      y arriba queda, muy tenue, la roca que se sacó para mirar. La roca junto a cada sector toma su color. ----
      const XR = 10.5, ZR = 7.4, HONDO = 3.0, pos = [], ar = [], ti = [];
      const ARENA = [0.5, 0.45, 0.38];
      const cercaDe = function (x, z) {                                       // el sector más cercano y a qué distancia de su túnel
        let mejor = -1, dm = 9;
        for (let k = 0; k < n; k++) {
          const s = sector[k], zz = z * s.lado, dz = zz < 0.95 ? 0.95 - zz : zz > 0.95 + LARGO ? zz - 0.95 - LARGO : 0, d = Math.hypot(Math.max(0, Math.abs(x - s.x) - 0.7), dz);
          if (d < dm) { dm = d; mejor = k; }
        }
        return [mejor, dm];
      };
      const roca = function (x, y, z, luz, tinte, peso, sec) { pos.push(x, y, z); ar.push(luz, azar(), sec); ti.push(K.mezcla(ARENA[0], tinte[0], peso), K.mezcla(ARENA[1], tinte[1], peso), K.mezcla(ARENA[2], tinte[2], peso)); };
      const ondula = function (x, z) { return 0.3 * Math.sin(x * 0.33 + z * 0.21) + 0.18 * Math.sin(z * 0.57 - x * 0.12); };
      for (let x = -XR; x <= XR; x += 0.1) for (let z = -ZR; z <= ZR; z += 0.1) {      // la cara del corte
        const px = x + (azar() - 0.5) * 0.1, pz = z + (azar() - 0.5) * 0.1, d = aTunel(px, pz);
        if (d < 0.03) continue;                                                 // adentro de un túnel no hay roca
        const c = cercaDe(px, pz), peso = 0.7 * Math.exp(-c[1] / 1.0), borde = Math.min(XR - Math.abs(px), ZR - Math.abs(pz));
        roca(px, PISO + (azar() - 0.5) * 0.04, pz, (0.5 + 1.5 * Math.exp(-d / 0.3)) * (borde < 0.12 ? 1.9 : 1), sector[c[0]].tinte, peso, c[1] < 1.7 ? c[0] : -1);
      }
      for (let j = 1; j <= 9; j++) {                                            // las dos caras que dan a la cámara, con sus estratos
        const y0 = PISO - (j / 9) * HONDO, luz = 1.25 * (1 - 0.085 * j);
        for (let x = -XR; x <= XR; x += 0.05) roca(x, y0 + 0.5 * ondula(x * 1.7, j * 2.1) * (j / 9), ZR, luz * (0.6 + 0.4 * azar()), ARENA, 0, -1);
        for (let z = -ZR; z <= ZR; z += 0.05) roca(XR, y0 + 0.5 * ondula(j * 2.1 + 30, z * 1.7) * (j / 9), z, luz * (0.6 + 0.4 * azar()), ARENA, 0, -1);
      }
      for (let i = 0; i < 9000; i++) { const y = PISO - azar() * HONDO; if (azar() < 0.5) roca((azar() * 2 - 1) * XR, y, ZR, 0.3, ARENA, 0, -1); else roca(XR, y, (azar() * 2 - 1) * ZR, 0.3, ARENA, 0, -1); }
      for (let y = PISO - HONDO; y <= PISO; y += 0.04) { roca(XR, y, ZR, 0.8, ARENA, 0, -1); roca(-XR, y, ZR, 0.5, ARENA, 0, -1); roca(XR, y, -ZR, 0.5, ARENA, 0, -1); }      // las aristas del bloque
      for (let x = -XR; x <= XR; x += 0.26) for (let z = -ZR; z <= ZR; z += 0.26) {      // la roca de encima, apenas insinuada: se ve cuando la cruza una onda
        const px = x + (azar() - 0.5) * 0.26, pz = z + (azar() - 0.5) * 0.26;
        roca(px, 2.1 + ondula(px, pz), pz, 0.15 * K.acotar(Math.min(XR - Math.abs(px), ZR - Math.abs(pz)) / 2.5, 0, 1), ARENA, 0, -1);
      }
      B.puntos({ position: [pos, 3], aR: [ar, 3], aTinte: [ti, 3] }, ONDAS + `
        attribute vec3 aR;             // cuánta luz recibe, un azar, y de qué sector es la roca (-1: de ninguno)
        attribute vec3 aTinte;
        uniform vec3 uFoc;
        void main() {
          float luz;
          vec3 p = position + sacude(position, luz);
          float l = clamp(luz, 0.0, 1.15);
          float mira = (abs(aR.z - uFoc.x) < 0.5 ? 1.0 - uFoc.z : 0.0) + (abs(aR.z - uFoc.y) < 0.5 ? uFoc.z : 0.0);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(aTinte, mix(COBRE, ORO, clamp(l * 1.2 - 0.3, 0.0, 1.0)), clamp(l * 1.5, 0.0, 1.0));
          vA = aR.x * (0.52 + 0.24 * aR.y) * (1.0 + 0.7 * mira) + l * 0.5 * (0.4 + 0.6 * min(aR.x, 1.0));
          gl_PointSize = (0.04 + 0.022 * aR.y + 0.05 * clamp(l, 0.0, 1.0)) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, Object.assign({ uFoc: (this.foc = { value: new THREE.Vector3(-1, -1, 0) }) }, ondas));

      // ---- los túneles: una bóveda de puntos, con sus arcos y los dos bordes del piso más marcados ----
      const pt = [], am = [], at = [];
      const boveda = function (alZ, a0, a1, fijo, radio, sec, tinte, densidad) {
        const largo = Math.abs(a1 - a0), cuantos = Math.round(largo * densidad);
        const pon = function (s, ang, luz) {
          const u = fijo + Math.cos(ang) * radio, y = PISO + Math.sin(ang) * radio;
          if (alZ) pt.push(u, y, s); else pt.push(s, y, u);
          am.push(sec, luz, azar()); at.push(tinte[0], tinte[1], tinte[2]);
        };
        for (let i = 0; i < cuantos; i++) pon(K.mezcla(a0, a1, azar()), azar() * Math.PI, 0.22 + 0.3 * azar());
        const arcos = Math.max(2, Math.round(largo / 0.8));
        for (let j = 0; j <= arcos; j++) for (let k = 0; k <= 40; k++) pon(K.mezcla(a0, a1, j / arcos), (k / 40) * Math.PI, 0.95);
        for (let k = 0; k <= largo / 0.035; k++) { const s = K.mezcla(a0, a1, k / (largo / 0.035)); pon(s, 0, 0.8); pon(s, Math.PI, 0.8); }
      };
      boveda(false, -9, FRENTE[0], 0, 0.82, -1, [0.62, 0.56, 0.47], 420);
      for (let k = 0; k < n; k++) boveda(true, sector[k].z0, sector[k].z1, sector[k].x, 0.7, k, sector[k].tinte, 520);
      // el frente del túnel principal: la cara donde se puso el explosivo
      for (let i = 0; i < 420; i++) { const a = azar() * Math.PI, q = Math.sqrt(azar()) * 0.82; pt.push(FRENTE[0], PISO + Math.sin(a) * q, Math.cos(a) * q); am.push(-2, 0.5, azar()); at.push(0.62, 0.56, 0.47); }
      B.puntos({ position: [pt, 3], aM: [am, 3], aTinte: [at, 3] }, ONDAS + `
        attribute vec3 aM;             // sector (-1: túnel principal; -2: el frente), luz, azar
        attribute vec3 aTinte;
        uniform vec3 uFoc;             // el sector que se mira, el que viene y cuánto se ha avanzado de uno al otro
        void main() {
          float luz;
          vec3 p = position + sacude(position, luz) * 0.45;
          float l = clamp(luz, 0.0, 1.0);
          float mira = (abs(aM.x - uFoc.x) < 0.5 ? 1.0 - uFoc.z : 0.0) + (abs(aM.x - uFoc.y) < 0.5 ? uFoc.z : 0.0);
          float esSector = step(-0.5, aM.x), esFrente = step(aM.x, -1.5);
          float calor = esFrente * step(0.0, uS) * exp(-max(uS, 0.0) * 0.9);          // el frente, al rojo justo después de la explosión
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(aTinte, vec3(1.0, 0.9, 0.72), clamp(l * 0.45 + calor, 0.0, 1.0));
          vA = (0.1 + 0.62 * aM.y) * mix(1.0, mix(0.42, 1.75, mira), esSector) + l * 0.25 + calor * 1.2;
          gl_PointSize = (0.034 + 0.016 * aM.z + 0.016 * mira * esSector + 0.03 * clamp(l, 0.0, 1.0) + 0.05 * calor) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, Object.assign({ uFoc: this.foc }, ondas));

      // ---- los temblores del archivo: dónde nace cada uno (un punto que se enciende a su hora y queda como brasa) ----
      const pe = [], ae = [], eventos = (this.eventos = []), cp = [], cv = [], cc = [];
      const cae = function (x, y, z, vx, vy, vz, s0, brillo) {                // un trozo de roca que cae y se queda en el piso
        const tl = (vy + Math.sqrt(vy * vy + 2 * G * (y - PISO))) / G;
        cp.push(x, y, z); cv.push(vx, vy, vz, tl); cc.push(s0, brillo, azar());
      };
      this.fuertes = [];
      for (let k = 0; k < n; k++) {
        const s = sector[k];
        S.unidades[k].puntos.forEach(function (p) {
          // en la roca junto al túnel de su sector, a un lado o al otro, sobre la cara del corte
          const zz = s.lado * (1.3 + azar() * (LARGO - 0.7)), c = [s.x + (azar() < 0.5 ? -1 : 1) * (0.95 + azar() * 1.15), PISO + 0.04, zz];
          const m = K.acotar((p[1] + 1) / 2.3, 0, 1), f = p[1] >= this.fuerte ? 1 : 0, s0 = p[0] * segPorHora;
          eventos.push({ s0: s0, m: m, f: f, c: c, sector: k,
            vel: 2.6 + 2.4 * m + 3.2 * f, vida: 1.25 + 0.7 * m + 1.7 * f, amp: 0.1 + 0.34 * m + 0.26 * f, ancho: 0.34 + 0.3 * m + 0.45 * f });
          pe.push(c[0], c[1], c[2]); ae.push(s0, m, f);
          if (f) {                                                             // un temblor fuerte: cae roca del techo de ese sector
            this.fuertes.push({ s0: s0, c: [s.x + 0.2, 0.45, zz], hora: p[0] });
            for (let i = 0; i < 620; i++) {
              const ang = 0.25 + azar() * (Math.PI - 0.5), dz = (azar() + azar() - 1) * 1.5;
              cae(s.x + Math.cos(ang) * 0.68, PISO + Math.sin(ang) * 0.68, zz + dz, (azar() - 0.5) * 0.5, -azar() * 0.4, (azar() - 0.5) * 0.5, s0 + 0.08 + azar() * 0.9 + Math.abs(dz) * 0.35, 0.6 + 0.4 * azar());
            }
          }
        }, this);
      }
      eventos.sort(function (a, b) { return a.s0 - b.s0; });
      B.puntos({ position: [pe, 3], aE: [ae, 3] }, ONDAS + `
        attribute vec3 aE;             // el segundo de animación en que ocurre, su magnitud (0 a 1) y si es fuerte
        void main() {
          float edad = uS - aE.x, nace = step(0.0, edad), fuerte = aE.z;
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(mix(COBRE, ORO, exp(-edad * 2.2)), ROJO, fuerte * (1.0 - exp(-edad * 1.5)));
          vA = nace * uVida * (0.2 + 0.25 * aE.y + 0.5 * fuerte + 1.1 * exp(-edad * 2.6));
          gl_PointSize = (0.06 + 0.09 * aE.y + 0.2 * fuerte) * (1.0 + 1.8 * exp(-edad * 3.4)) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, ondas);

      // ---- la explosión: la roca rota sale del frente, cae por su peso y queda apilada en el túnel ----
      for (let i = 0; i < 1500; i++) {
        const a = azar() * Math.PI, q = Math.sqrt(azar()) * 0.78, lejos = azar();
        cae(FRENTE[0] - azar() * 0.25, PISO + 0.02 + Math.sin(a) * q, Math.cos(a) * q * 0.9, -(0.4 + 5.2 * lejos * lejos), 0.2 + azar() * 1.9, (azar() - 0.5) * 0.35, azar() * 0.12, 0.55 + 0.45 * azar());
      }
      B.puntos({ position: [cp, 3], aV: [cv, 4], aC: [cc, 3] }, ONDAS + `
        attribute vec4 aV;             // velocidad con que sale y el momento en que toca el piso
        attribute vec3 aC;             // el segundo de animación en que se suelta, su brillo y un azar
        void main() {
          float edad = uS - aC.x, nace = step(0.0, edad), a = clamp(edad, 0.0, aV.w), enPiso = step(aV.w, edad);
          vec3 p = position + aV.xyz * a + vec3(0.0, -0.5 * ${G.toFixed(1)} * a * a, 0.0);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(vec3(1.0, 0.9, 0.72), ARENA * 1.35, clamp(edad * 0.9, 0.0, 1.0));
          vA = nace * uVida * aC.y * mix(0.9, 0.42, enPiso);
          gl_PointSize = (0.04 + 0.045 * aC.z) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, ondas);

      // ---- el polvo: avanza por el túnel principal, se frena y se asienta ----
      const pd = [], ad = [];
      for (let i = 0; i < 3200; i++) {
        const a = azar() * Math.PI, q = Math.sqrt(azar()) * 0.76;
        pd.push(FRENTE[0], PISO + 0.04 + Math.sin(a) * q, Math.cos(a) * q);
        ad.push(1.5 + 15.5 * Math.pow(azar(), 1.4), 0.5 + 0.9 * azar(), 0.4 + azar(), azar());
      }
      B.puntos({ position: [pd, 3], aD: [ad, 4] }, ONDAS + `
        attribute vec4 aD;             // hasta dónde llega, qué tan rápido, cuánto pesa, azar
        void main() {
          float edad = max(uS, 0.0), nace = step(0.0, uS);
          float avance = aD.x * (1.0 - exp(-edad * aD.y * 0.55));
          float x = max(-8.7, position.x - avance);
          float y = max(${(PISO + 0.03).toFixed(2)}, position.y + 0.1 * sin(edad * 1.4 + aD.w * 30.0) * exp(-edad * 0.3) - 0.035 * aD.z * edad);
          vec4 mv = modelViewMatrix * vec4(x, y, position.z * (1.0 - 0.15 * exp(-edad)), 1.0);
          vColor = mix(vec3(1.0, 0.86, 0.66), ARENA * 1.1, 1.0 - exp(-edad * 1.1));
          vA = nace * uVida * smoothstep(0.0, 0.12, edad) * (0.02 + 0.13 * exp(-edad * 0.45));
          gl_PointSize = (0.05 + 0.07 * aD.w) * (1.0 + 0.7 * (1.0 - exp(-edad * 0.8))) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, ondas);

      this.etqFrente = D3.etiquetas(L, 1, 'nota')[0];
      this.etqFrente.classList.add('izq');
      this.etqFuerte = D3.etiquetas(L, Math.min(2, this.fuertes.length), 'chica');
      this.vista = { c: null, lista: false };
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); if (this.F) K.foco.ajustar(this.F); },
    entrar: function () { if (this.F) K.foco.reiniciar(this.F); if (this.vista) this.vista.lista = false; },
    cuadro: function (t, dt) {
      const F = this.F, yo = this, ciclo = DURA + ESPERA;
      // el tiempo del archivo: explota, corre, se queda un momento, se apaga y vuelve a empezar
      let s = t - PARTE, vida = 1;
      if (!K.quieto && s >= 0) { s = s % ciclo; vida = 1 - K.suave((s - (ciclo - 1.0)) / 0.85); }
      const h = K.acotar(s / DURA, 0, 1) * this.horas, min = Math.floor(h * 60);
      const texto = Math.floor(min / 60) + ' h ' + (min % 60 < 10 ? '0' : '') + (min % 60) + ' min';
      if (this._reloj !== texto) { this._reloj = texto; this.relojNum.textContent = texto; }
      this.relojEl.classList.toggle('ver', s >= 0 && vida > 0.5);
      if (!this.tres) { K.foco.cuadro(F, t, function () { return null; }, 3.6, 1.2); return; }
      const B = this.B, O = this.uOnda.value, OF = this.uOndaF.value;
      B.u.uT.value = t;
      this.uS.value = s; this.uVida.value = vida;

      // ---- los frentes de onda activos: dos de la explosión y los diez temblores más fuertes que estén pasando ----
      let usados = 0;
      const frente = function (c, radio, amp, ancho, brillo) { if (usados >= NO || amp <= 0.002) return; O[usados].set(c[0], c[1], c[2], radio); OF[usados].set(amp, ancho, brillo); usados++; };
      if (s >= 0 && s < 3.4) frente(FRENTE, 8.5 * s, 0.62 * Math.exp(-s * 0.5) * K.acotar((3.4 - s) / 0.6, 0, 1), 1.15, 1.3);
      if (s >= 0.3 && s < 5.2) frente(FRENTE, 4.6 * (s - 0.3), 0.4 * Math.exp(-(s - 0.3) * 0.36) * K.acotar((5.2 - s) / 0.8, 0, 1), 0.85, 1.0);
      const vivos = [];
      for (let i = 0; i < this.eventos.length; i++) {
        const e = this.eventos[i], edad = s - e.s0;
        if (edad < 0) break;
        if (edad < e.vida) { const q = 1 - edad / e.vida; vivos.push([e.amp * q * Math.sqrt(q), e, edad]); }
      }
      vivos.sort(function (a, b) { return b[0] - a[0]; });
      for (let i = 0; i < vivos.length && usados < NO; i++) { const e = vivos[i][1]; frente(e.c, 0.15 + e.vel * vivos[i][2], vivos[i][0], e.ancho, 2.2 - 0.6 * e.f); }
      for (let i = usados; i < NO; i++) { O[i].w = -100; OF[i].x = 0; }

      // ---- la cámara acompaña al foco: se acerca despacio al sector que se mira ----
      const sa = this.sector[this.indice[F.a]], sb = F.b != null ? this.sector[this.indice[F.b]] : sa, e = F.b != null ? F.e : 0;
      const fx = K.mezcla(sa.x, sb.x, e), lado = K.mezcla(sa.lado, sb.lado, e);
      const V = this.vista, abre = K.quieto ? 1 : K.suave((t - 2.4) / 3.2);      // primero la vista entera, con la explosión; después se acerca
      const meta = [0.3 + abre * fx * 0.08, -1.9, abre * lado * 0.5, K.mezcla(52, 49.5, abre), 0.54 - abre * (0.035 * lado + 0.007 * fx)];
      if (!V.lista || K.quieto) { V.c = meta.slice(); V.lista = true; }
      else { const k = 1 - Math.exp(-(dt || 0) * 1.4); for (let i = 0; i < 5; i++) V.c[i] += (meta[i] - V.c[i]) * k; }
      const golpe = s >= 0 && s < 1.2 && !K.quieto ? 0.11 * Math.exp(-s * 3.2) : 0;   // la explosión remece un instante la vista
      B.mirar(V.c[4] + Math.sin(t * 0.15) * 0.05, 0.74, V.c[3], [V.c[0] + golpe * Math.sin(s * 61), V.c[1] + golpe * Math.sin(s * 47 + 1), V.c[2]], -455);

      // ---- el foco y lo poco que se rotula ----
      const punto = function (id) { const q = yo.sector[yo.indice[id]], p = K.proyectar(q.x, 0.3, q.lado * (0.95 + LARGO * 0.55), B.camera); return { x: p.x, y: p.y }; };
      K.foco.cuadro(F, t, punto, 3.6, 1.2);
      this.foc.value.set(this.indice[F.a], F.b == null ? -1 : this.indice[F.b], F.e);
      D3.poner(this.etqFrente, B.camera, FRENTE[0], 0.55, FRENTE[2], '<b>Explosión</b>hora cero', s >= 0.05 && s < 2.6);
      for (let i = 0; i < this.etqFuerte.length; i++) {
        const f = this.fuertes[i];
        D3.poner(this.etqFuerte[i], B.camera, f.c[0], f.c[1] + 0.2, f.c[2], '<b>Temblor fuerte</b>', s >= f.s0 && (vida > 0.5 || K.quieto));
      }
    },
  });
})();
