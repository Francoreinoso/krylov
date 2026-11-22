/* W · Quién investiga esto (fuera del recorrido, tecla W): el mapa mundial de los grupos que están detrás de
   amortized inference. Un mapamundi de puntos, inclinado, y una luz en cada grupo. La cámara va sola: primero el mundo
   entero y después, parada por parada, se acerca a cada región, enciende sus grupos y los nombra en una lista unida a
   cada luz por un hilo. Arrastrar gira el mapa; pasar el mouse por una luz dice qué aportó ese grupo.
   Todo sale de datos/laboratorios.js (que escribe datos/generar_laboratorios.py): los grupos, con la cita del review que
   justifica a cada uno, y la tierra firme como rejilla de puntos. Nada se pide a internet.
   El recorrido es una función del tiempo de la lámina: no acumula estado, así que en pausa queda quieto, al repetirse
   no salta, y sin movimiento (?quieto) muestra el mundo entero con todos los grupos encendidos. */
(function () {
  'use strict';
  const K = window.K, D = window.KRYLOV_LABORATORIOS;
  if (!D || !D.mapa || !D.grupos || !D.grupos.length) { K.registrar('laboratorios', {}); return; }

  // ---------- la proyección de Robinson: la misma tabla con que generar_laboratorios.py armó la rejilla ----------
  const PR = D.proyeccion;
  function tabla(t, lat) { const a = Math.min(Math.abs(lat), 90) / 5, i = Math.min(17, Math.floor(a)); return t[i] + (t[i + 1] - t[i]) * (a - i); }
  // De longitud y latitud a la escena: x hacia el este, z hacia el sur (el norte queda al fondo).
  function lugar(lon, lat) {
    return { x: 0.8487 * PR.escala * tabla(PR.x, lat) * ((lon * Math.PI) / 180), z: -1.3523 * PR.escala * tabla(PR.y, lat) * (lat >= 0 ? 1 : -1) };
  }

  // ---------- el recorrido ----------
  // Dónde se para la cámara en cada parada: a qué mira, desde qué distancia, y cuánto se corre la escena en la lámina
  // (dx a la derecha, dy hacia abajo, en píxeles) para dejarle el lugar al texto.
  const REGION = { el: 0.8, dx: -330, dy: -70 };
  const VISTA = {
    mundo: { lon: 14, lat: 12, R: 47, el: 0.86, dx: 0, dy: -190, dura: 4.4 },
    chile: Object.assign({ lon: -63, lat: -29, R: 17, dura: 3.2 }, REGION),
    norteamerica: Object.assign({ lon: -99, lat: 40, R: 11.5, dura: 7.0 }, REGION),
    europa_oeste: Object.assign({ lon: 1.2, lat: 52.2, R: 4.6, dura: 6.4 }, REGION),
    alemania_austria: Object.assign({ lon: 11.6, lat: 50.2, R: 4.3, dura: 5.8 }, REGION),
    nordicos: Object.assign({ lon: 17.5, lat: 58.4, R: 5.2, dura: 5.8 }, REGION),
    review: Object.assign({ lon: 96, lat: -2, R: 36, dura: 4.2 }, REGION),
  };
  const VUELO = 1.3;                    // segundos de una parada a la siguiente
  const ALTO = 0.075;                   // alto de cada columna de luz, como fracción de la distancia de la cámara
  const CONTINENTES = ['Europa', 'Norteamérica', 'Sudamérica', 'Asia', 'Oceanía'];

  const grupos = D.grupos.map(function (g, i) { const q = lugar(g.lon, g.lat); return { g: g, i: i, x: q.x, z: q.z }; });
  const N = grupos.length;
  const paises = {}, trabajos = {};
  grupos.forEach(function (o) { paises[o.g.pais] = 1; trabajos[o.g.cita + ' ' + o.g.anio] = o.g.anio; });
  const nPaises = Object.keys(paises).length, nTrabajos = Object.keys(trabajos).length;
  // «la última década»: de 2016 en adelante. Cuántos de los trabajos del mapa caen ahí se cuenta, no se escribe a mano.
  const DESDE = 2016, nRecientes = Object.keys(trabajos).filter(function (k) { return trabajos[k] >= DESDE; }).length;

  // las paradas, en orden: el mundo y después las regiones de datos/laboratorios.js
  const paradas = [{ id: 'mundo', nombre: '', grupos: grupos }].concat(D.paradas.map(function (p) {
    return { id: p.id, nombre: p.nombre, grupos: grupos.filter(function (o) { return o.g.parada === p.id; }) };
  })).filter(function (p) { return VISTA[p.id] && p.grupos.length; });
  paradas.forEach(function (p) { const v = VISTA[p.id], c = lugar(v.lon, v.lat); p.v = v; p.cx = c.x; p.cz = c.z; });
  let CICLO = 0;
  paradas.forEach(function (p) { p.desde = CICLO; CICLO += p.v.dura + VUELO; });

  // En qué va el recorrido en el segundo t: la parada, la que sigue y cuánto se ha volado hacia ella (0: detenida).
  function donde(t) {
    let x = ((t % CICLO) + CICLO) % CICLO;
    for (let i = 0; i < paradas.length; i++) {
      const p = paradas[i];
      if (x < p.v.dura) return { i: i, j: i, k: 0, local: x };
      x -= p.v.dura;
      if (x < VUELO) return { i: i, j: (i + 1) % paradas.length, k: K.suave(x / VUELO), local: -1 };
      x -= VUELO;
    }
    return { i: 0, j: 0, k: 0, local: 0 };
  }

  // Qué grupo va en cada fila de la lista para que los hilos no se crucen: el reparto que suma menos largo de hilo
  // (si dos hilos se cruzaran, intercambiarlos acortaría la suma). Con ocho grupos como mucho, se prueban todos los repartos.
  const LISTA = { x: 110, y: 400 };            // la esquina de la lista en la lámina (laboratorios.css)
  function sinCruces(luces, filas) {
    const n = luces.length, total = 1 << n, costo = new Float64Array(total).fill(Infinity), quien = new Int8Array(total);
    costo[0] = 0;
    for (let m = 0; m < total; m++) {
      if (costo[m] === Infinity) continue;
      let f = 0;
      for (let b = m; b; b >>= 1) f += b & 1;                // las filas ya ocupadas
      if (f >= n) continue;
      for (let j = 0; j < n; j++) {
        if ((m >> j) & 1) continue;
        const c = costo[m] + Math.hypot(luces[j].x - filas[f].x, luces[j].y - filas[f].y), m2 = m | (1 << j);
        if (c < costo[m2]) { costo[m2] = c; quien[m2] = j; }
      }
    }
    const orden = new Array(n);
    for (let f = n - 1, m = total - 1; f >= 0; f--) { orden[f] = quien[m]; m ^= 1 << quien[m]; }
    return orden;
  }

  function texto(etiqueta, clase, html) { const e = document.createElement(etiqueta); e.className = clase; e.innerHTML = html; return e; }

  K.registrar('laboratorios', {
    tres: null, interactivo: true, tQuieto: 3.6,
    crear: function (L) {
      const yo = this, R = D.review;
      // ---------- el texto ----------
      const notas = L.querySelector('aside.notas'), poner = function (e) { return L.insertBefore(e, notas); };      // en este orden: velos, hilos, texto, nota
      poner(texto('div', 'lab-velo arriba', ''));
      this.veloLado = poner(texto('div', 'lab-velo lado', ''));
      this.capaHilos = poner(texto('div', 'lab-hilos', ''));
      const cabeza = texto('div', 'bloque lab-cabeza',
        '<div class="t2">Ciencia de la última década.<br><span class="cobre">La industria recién empieza.</span></div>' +
        '<div class="p">Detrás de amortized inference hay <b class="nb">' + N + ' grupos de investigación</b> de <b class="nb">' + nPaises + ' países</b>. ' +
        'De los ' + nTrabajos + ' trabajos que los ponen en este mapa, <span class="nb">' + nRecientes + ' son de ' + DESDE + ' en adelante.</span></div>' +
        '<div class="dato">' + R.autores + ' · ' + R.titulo + ' · ' + R.anio + '</div>');
      cabeza.dataset.paso = '0';
      poner(cabeza);

      // el mundo entero: cuántos grupos hay en cada continente
      const cuenta = {};
      grupos.forEach(function (o) { cuenta[o.g.continente] = (cuenta[o.g.continente] || 0) + 1; });
      const conteo = (this.conteo = texto('div', 'lab-conteo', ''));
      CONTINENTES.concat(Object.keys(cuenta).filter(function (c) { return CONTINENTES.indexOf(c) < 0; })).forEach(function (c) {
        if (cuenta[c]) conteo.appendChild(texto('div', 'lab-item', '<b class="num">' + cuenta[c] + '</b><span>' + c + '</span>'));
      });
      poner(conteo);
      paradas[0].filas = Array.prototype.slice.call(conteo.children);

      // cada región: su lista de grupos, y un hilo de cada nombre a su luz
      paradas.forEach(function (p, n) {
        if (!n) return;
        const lista = (p.lista = texto('div', 'lab-lista', '<div class="lab-parada">' + p.nombre + ' · ' + p.grupos.length + (p.grupos.length === 1 ? ' grupo' : ' grupos') + '</div>'));
        p.alto = Math.min(78, Math.floor(540 / p.grupos.length));
        lista.style.setProperty('--alto', p.alto + 'px');
        poner(lista);
        p.cabecera = lista.firstChild;
      });
      this.nota = poner(texto('div', 'lab-nota', ''));

      // ---------- las notas de quien presenta ----------
      const dice = L.querySelector('#lab-dice'), fuente = L.querySelector('#lab-fuente');
      if (dice) dice.textContent = '«Esto no lo inventamos nosotros. Detrás de amortized inference hay ' + N + ' grupos de investigación de ' + nPaises +
        ' países, y casi todos sus trabajos son de ' + DESDE + ' en adelante. Uno se firmó en Valparaíso. Krylov lleva esa ciencia a un producto para la minera.»';
      if (fuente) fuente.innerHTML = 'Los grupos son las instituciones que firman el review «' + R.titulo + '» (' + R.autores + '; ' + R.revista + ', ' + R.anio +
        ') y las de los autores de métodos y software que ese review cita. <b>La afiliación es la del trabajo citado</b>, no necesariamente la de hoy: se comprobó en el review, en OpenAlex y en la portada de un artículo; el año es el de la cita. ' +
        '<b>La lista no es exhaustiva:</b> entra solo lo que se pudo comprobar (' + N + ' grupos, ' + nPaises + ' países, ' + nTrabajos + ' trabajos, ' + nRecientes + ' de ellos de ' + DESDE + ' en adelante). ' +
        '<b>«La industria recién empieza» es una lectura nuestra, no una medición.</b> El trabajo de Valparaíso es Cranmer, Pavez y Louppe (2015), con Juan Pavez en la Universidad Técnica Federico Santa María. ' +
        'El mapa es la tierra firme de Natural Earth (dominio público), en puntos. El recorrido va solo; arrastrar gira el mapa, y pasar el mouse por una luz dice qué aportó ese grupo. Detalle y fuentes de cada grupo: <code>datos/generar_laboratorios.py</code>.';

      if (!K.gl.ok) return;

      // ---------- la escena ----------
      const B = (this.B = K.base3d(30)), M = D.mapa, bits = K.b64(M.b64), azar = K.azar(404);
      // la tierra: un punto por celda. Nivel 0, la rejilla gruesa (se ve siempre); 1 y 2, las finas (aparecen al acercarse)
      const pos = [], al = [];
      for (let r = 0; r < M.filas; r++) for (let c = 0; c < M.cols; c++) {
        const k = r * M.cols + c;
        if (!((bits[k >> 3] >> (k & 7)) & 1)) continue;
        pos.push(M.x0 + (c + 0.5) * M.paso, 0, -(M.y_norte - (r + 0.5) * M.paso));
        al.push(c % 4 === 0 && r % 4 === 0 ? 0 : (c % 2 === 0 && r % 2 === 0 ? 1 : 2), azar());
      }
      this.uTierra = { uFino1: { value: 0 }, uFino2: { value: 0 }, uTam: { value: 0.07 }, uFoco: { value: new THREE.Vector3(0, 0, 60) } };
      B.puntos({ position: [pos, 3], aL: [al, 2] }, `
        attribute vec2 aL;             // nivel de detalle (0, 1 o 2) y azar
        uniform float uFino1;          // cuánto se ven los puntos del nivel 1, y los del 2
        uniform float uFino2;
        uniform float uTam;            // tamaño de un punto, en unidades de escena
        uniform vec3 uFoco;            // hacia dónde mira la cámara (x, z) y qué radio queda iluminado
        void main() {
          float ver = aL.x < 0.5 ? 1.0 : (aL.x < 1.5 ? uFino1 : uFino2);
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          float d = distance(position.xz, uFoco.xy) / uFoco.z;
          float cerca = exp(-d * d);
          float onda = 0.5 + 0.5 * sin(position.x * 0.55 + position.z * 0.3 - uT * 0.5 + aL.y * 1.5);       // un brillo lento que cruza el mapa
          vColor = mix(ARENA, COBRE, 0.2 + 0.45 * cerca);
          vA = ver * (0.36 + 0.26 * cerca + 0.1 * onda);
          gl_PointSize = uTam * (0.86 + 0.28 * aL.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, this.uTierra);

      // los grupos: una columna de chispas que suben, un anillo que se abre y una brasa en la base
      const pg = [], ap = [], at = [];
      grupos.forEach(function (o) {
        const fase = azar();
        for (let k = 0; k < 46; k++) { pg.push(o.x, 0, o.z); ap.push(o.i, (k + azar()) / 46, azar()); at.push(0); }
        for (let k = 0; k < 28; k++) { pg.push(o.x, 0, o.z); ap.push(o.i, k / 28, fase); at.push(1); }
        pg.push(o.x, 0, o.z); ap.push(o.i, 0, fase); at.push(2);
      });
      this.on = { value: new Array(N).fill(0) };
      this.alto = { value: 1 };
      B.puntos({ position: [pg, 3], aP: [ap, 3], aTipo: [at, 1] }, `
        attribute vec3 aP;             // a qué grupo pertenece, su lugar en la figura (0 a 1) y azar
        attribute float aTipo;         // 0: chispa de la columna. 1: anillo. 2: brasa
        uniform float uOn[${N}];       // cuánto está encendido cada grupo (0 a 1)
        uniform float uAlto;
        uniform float uLejos;          // 1 con el mundo entero a la vista: las luces se achican para que Europa no se queme
        void main() {
          float on = uOn[int(aP.x + 0.5)];
          vec3 p = position;
          float a, tam;
          vec3 color = mix(COBRE, ORO, on);
          if (aTipo < 0.5) {
            float s = fract(aP.y + uT * (0.14 + 0.1 * aP.z));
            p.y = s * uAlto * (0.3 + 0.7 * on);
            a = (0.14 + 0.86 * on) * (1.0 - s) * (0.45 + 0.55 * aP.z) * (1.0 - 0.45 * uLejos);
            tam = uAlto * (0.03 + 0.035 * (1.0 - s));
          } else if (aTipo < 1.5) {
            float s = fract(uT * 0.4 + aP.z), ang = aP.y * 6.2832, r = uAlto * 0.5 * s;
            p.x += cos(ang) * r; p.z += sin(ang) * r;
            a = on * on * (1.0 - s) * 0.6;
            tam = uAlto * 0.024;
          } else {
            a = (0.55 + 0.9 * on) * (1.0 - 0.4 * uLejos);
            tam = uAlto * (0.09 + 0.05 * on) * (1.0 - 0.45 * uLejos);
            color = mix(color, vec3(1.0, 0.95, 0.84), 0.6 * on);
          }
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = color;
          vA = a;
          gl_PointSize = tam * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uOn: this.on, uAlto: this.alto, uLejos: (this.lejos = { value: 1 }) });
      this.tres = B.tres;

      // ---------- las listas: en cada región, los grupos de arriba abajo como se ven en pantalla ----------
      paradas.forEach(function (p, n) {
        if (!n) return;
        yo.mirar(p.cx, p.cz, p.v.R, 0, p.v.el, p.v.dx, p.v.dy);
        const luces = p.grupos.map(function (o) { return K.proyectar(o.x, 0, o.z, B.camera); });
        const orden = sinCruces(luces, p.grupos.map(function (o, f) { return { x: LISTA.x + 660, y: LISTA.y + 40 + f * p.alto + 19 }; })).map(function (j) { return p.grupos[j]; });
        orden.forEach(function (o) {
          const g = o.g;
          o.fila = p.lista.appendChild(texto('div', 'lab-fila', '<b>' + g.institucion + '</b><span>' + g.ciudad + ', ' + g.pais + ' · ' + g.cita + ', ' + g.anio + '</span><i></i>'));
          o.hilo = yo.capaHilos.appendChild(texto('div', 'lab-hilo', '<i></i>'));
        });
        p.filas = [p.cabecera].concat(orden.map(function (o) { return o.fila; }));
      });

      // ---------- el mouse: arrastrar gira el mapa; sobre una luz, dice qué aportó ese grupo ----------
      const lienzo = K.gl.renderer.domElement;
      let agarre = null;
      this.giro = { az: 0, el: 0 };
      this.sobre = null;
      const enLamina = function (ev) { const r = lienzo.getBoundingClientRect(); return { x: ((ev.clientX - r.left) / r.width) * 1920, y: ((ev.clientY - r.top) / r.height) * 1080 }; };
      lienzo.addEventListener('pointerdown', function (ev) {
        if (!yo.activa) return;
        agarre = { x: ev.clientX, y: ev.clientY, az: yo.giro.az, el: yo.giro.el };
        lienzo.setPointerCapture(ev.pointerId);
      });
      lienzo.addEventListener('pointermove', function (ev) {
        if (!yo.activa) return;
        if (agarre) {
          yo.giro.az = agarre.az - ((ev.clientX - agarre.x) * 0.005) / K.escala;
          yo.giro.el = K.acotar(agarre.el + ((ev.clientY - agarre.y) * 0.003) / K.escala, -0.45, 0.5);
          yo.sobre = null;
          return;
        }
        const q = enLamina(ev);
        let mejor = null, cerca = 34;
        grupos.forEach(function (o) { if (!o.px) return; const d = Math.hypot(o.px.x - q.x, o.px.y - q.y); if (d < cerca) { cerca = d; mejor = o; } });
        yo.sobre = mejor;
      });
      const soltar = function () { agarre = null; };
      lienzo.addEventListener('pointerup', soltar);
      lienzo.addEventListener('pointercancel', soltar);
      lienzo.addEventListener('pointerleave', function () { yo.sobre = null; });
    },

    // La cámara mira a un punto del mapa (cx, cz) desde la distancia R, girada az y levantada el.
    mirar: function (cx, cz, R, az, el, dx, dy) {
      const cam = this.B.camera;
      cam.position.set(cx + R * Math.cos(el) * Math.sin(az), R * Math.sin(el), cz + R * Math.cos(el) * Math.cos(az));
      cam.lookAt(cx, 0, cz);
      cam.setViewOffset(1920, 1080, dx, dy, 1920, 1080);
      cam.updateMatrixWorld();
    },

    // Dónde nace cada hilo: al final del nombre más largo de su lista, a la altura de su fila.
    medir: function () {
      paradas.forEach(function (p, n) {
        if (!n || !p.lista) return;
        let ancho = 0;
        p.grupos.forEach(function (o) { o._w = Math.max(o.fila.children[0].offsetWidth, o.fila.children[1].offsetWidth); ancho = Math.max(ancho, o._w); });
        p.grupos.forEach(function (o) {
          const raya = o.fila.children[2];
          raya.style.left = (o._w + 14) + 'px';
          raya.style.width = Math.max(0, ancho + 30 - o._w - 14) + 'px';
          o.ax = LISTA.x + ancho + 30;
          o.ay = LISTA.y + o.fila.offsetTop + 19;
        });
      });
    },

    alAjustar: function () { if (this.B) { this.B.ajustar(); this.medir(); } },
    entrar: function () {
      this.activa = true;
      if (this.giro) { this.giro.az = 0; this.giro.el = 0; }
      this.sobre = null;
      const yo = this;
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (yo.B) yo.medir(); });
    },
    salir: function () { this.activa = false; this.sobre = null; if (this.nota) this.nota.classList.remove('ver'); },

    cuadro: function (t) {
      const e = donde(t), a = paradas[e.i], b = paradas[e.j], k = e.k;
      // el texto: las filas de la parada en que se está van apareciendo de a una; al partir, se van todas
      for (let n = 0; n < paradas.length; n++) {
        const p = paradas[n], aqui = n === e.i && k === 0;
        if (!p.filas) continue;
        for (let f = 0; f < p.filas.length; f++) p.filas[f].classList.toggle('ver', aqui && (K.quieto || e.local > 0.15 + f * 0.09));
      }
      const lado = K.mezcla(e.i ? 1 : 0, e.j ? 1 : 0, k);
      if (this._lado !== lado) { this._lado = lado; this.veloLado.style.opacity = lado.toFixed(3); }
      if (!this.tres) return;

      // ---------- la cámara ----------
      const B = this.B, va = a.v, vb = b.v;
      const lejos = Math.hypot(b.cx - a.cx, b.cz - a.cz);
      const R = K.mezcla(va.R, vb.R, k) + Math.sin(Math.PI * k) * K.acotar(0.5 * lejos - 0.5 * Math.abs(va.R - vb.R), 0, 12);   // en un vuelo largo, se aleja un poco
      const cx = K.mezcla(a.cx, b.cx, k) + (K.quieto ? 0 : 0.012 * R * Math.sin(t * 0.13)), cz = K.mezcla(a.cz, b.cz, k);
      const az = (K.quieto ? 0 : 0.05 * Math.sin(t * 0.21)) + this.giro.az, el = K.acotar(K.mezcla(va.el, vb.el, k) + this.giro.el, 0.3, 1.35);
      this.mirar(cx, cz, R, az, el, K.mezcla(va.dx, vb.dx, k), K.mezcla(va.dy, vb.dy, k));
      B.u.uT.value = t;
      const fino1 = 1 - K.suave((R - 22) / 18), fino2 = 1 - K.suave((R - 9) / 11);
      this.uTierra.uFino1.value = fino1; this.uTierra.uFino2.value = fino2;
      this.uTierra.uTam.value = 0.074 * K.mezcla(1, 0.5, fino1) * K.mezcla(1, 0.42, fino2);
      this.uTierra.uFoco.value.set(cx, cz, 0.55 * R);
      this.alto.value = ALTO * R;
      this.lejos.value = K.suave((R - 18) / 26);

      // ---------- los grupos: al entrar se encienden de oeste a este; después brilla más la región en que se está ----------
      for (let i = 0; i < N; i++) {
        const o = grupos[i];
        const peso = K.mezcla(e.i === 0 || a.id === o.g.parada ? 1 : 0, e.j === 0 || b.id === o.g.parada ? 1 : 0, k);
        const nace = K.quieto ? 1 : K.suave((t - 0.3 - 1.5 * ((o.x + 18) / 36)) / 0.5);
        this.on.value[i] = nace * (0.26 + 0.74 * peso) * (this.sobre === o ? 1.25 : 1);
        o.px = K.proyectar(o.x, 0, o.z, B.camera);
        if (!o.hilo) continue;
        const ver = o.fila.classList.contains('ver') && o.ax != null;
        if (o.ax != null && (o.g.parada === a.id || o.g.parada === b.id)) {          // también mientras se apaga: el hilo no se despega de su luz
          const dx = o.px.x - o.ax, dy = o.px.y - o.ay;
          o.hilo.style.transform = 'translate(' + o.ax.toFixed(1) + 'px,' + o.ay.toFixed(1) + 'px) rotate(' + Math.atan2(dy, dx).toFixed(4) + 'rad)';
          o.hilo.style.width = Math.hypot(dx, dy).toFixed(1) + 'px';
        }
        o.hilo.classList.toggle('ver', ver);
        o.fila.classList.toggle('foco', this.sobre === o);
        o.hilo.classList.toggle('foco', this.sobre === o);
      }

      // ---------- la nota del grupo que está bajo el mouse ----------
      const s = this.sobre;
      if (s && s.px && !s.px.detras) {
        if (this._nota !== s) {
          this._nota = s;
          this.nota.innerHTML = '<b>' + s.g.institucion + '</b><span>' + s.g.ciudad + ', ' + s.g.pais + '</span><p>' + s.g.aporte + '.</p><span>' + s.g.cita + ', ' + s.g.anio + '</span>';
        }
        const izq = s.px.x > 1340;
        this.nota.classList.toggle('izq', izq);
        this.nota.style.transform = 'translate(' + (s.px.x + (izq ? -22 : 22)).toFixed(1) + 'px,' + K.acotar(s.px.y - 40, 430, 880).toFixed(1) + 'px)';
        this.nota.classList.add('ver');
      } else this.nota.classList.remove('ver');
    },
  });
})();
