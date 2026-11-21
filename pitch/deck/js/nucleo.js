/* Krylov · deck. Motor de navegación: escenario escalado, láminas con pasos, notas, pausa y un solo lienzo WebGL compartido.
   Sin módulos ni fetch: tiene que abrir con doble clic (file://) y sin internet. */
(function () {
  'use strict';

  const params = new URLSearchParams(location.search);
  const K = (window.K = {
    datos: window.KRYLOV_DATOS,
    escenas: {},
    estatico: params.has('estatico'),   // para el respaldo en PNG: todo en su estado final, sin movimiento
    quieto: false,                      // sin movimiento (estático o prefers-reduced-motion)
    pausado: false,
    t: 0,
    escala: 1,
    fps: 0,
  });
  K.quieto = K.estatico || params.has('quieto') ||
    (!params.has('animado') && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (K.quieto) document.documentElement.classList.add('quieto');

  // ---------- utilidades ----------
  K.registrar = function (id, escena) { K.escenas[id] = escena; };
  K.miles = function (n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.'); };
  K.coma = function (x, d) { return x.toFixed(d == null ? 2 : d).replace('.', ','); };
  K.acotar = function (x, a, b) { return Math.max(a, Math.min(b, x)); };
  K.suave = function (t) { t = K.acotar(t, 0, 1); return t * t * (3 - 2 * t); };
  K.fuera = function (t) { t = K.acotar(t, 0, 1); return 1 - Math.pow(1 - t, 3); };
  K.mezcla = function (a, b, t) { return a + (b - a) * t; };
  // Azar con semilla: el deck sale igual en el ensayo y en el escenario.
  K.azar = function (semilla) {
    let a = semilla >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  // Una línea de tiempo de GSAP que, sin movimiento o al saltar, queda en su estado final.
  K.linea = function (inst, opciones) {
    const tl = gsap.timeline(opciones || {});
    if (inst || K.quieto) Promise.resolve().then(function () { tl.progress(1); });
    return tl;
  };
  // Lleva propiedades numéricas de un objeto a su destino; sin movimiento o al saltar, las deja puestas.
  K.anim = function (obj, props, dur, inst, ease, demora) {
    gsap.killTweensOf(obj, Object.keys(props).join(','));
    if (inst || K.quieto) { Object.assign(obj, props); return null; }
    return gsap.to(obj, Object.assign({ duration: dur, ease: ease || 'power2.inOut', delay: demora || 0 }, props));
  };
  K.contar = function (el, desde, hasta, dur, formato, inst) {
    const o = { v: desde };
    formato = formato || K.miles;
    if (inst || K.quieto) { el.textContent = formato(hasta); return null; }
    return gsap.to(o, { v: hasta, duration: dur, ease: 'power2.out', onUpdate: function () { el.textContent = formato(o.v); } });
  };
  K.proyectar = (function () {
    let v = null;
    return function (x, y, z, camara) {
      v = v || new THREE.Vector3();
      v.set(x, y, z).project(camara);
      return { x: (v.x * 0.5 + 0.5) * 1920, y: (-v.y * 0.5 + 0.5) * 1080, detras: v.z > 1 };
    };
  })();
  K.b64 = function (texto) {
    const bin = atob(texto), n = bin.length, salida = new Uint8Array(n);
    for (let i = 0; i < n; i++) salida[i] = bin.charCodeAt(i);
    return salida;
  };

  // ---------- escenario y lienzo ----------
  const escenario = document.getElementById('escenario');
  const lienzo = document.getElementById('gl');
  const laminas = Array.prototype.slice.call(document.querySelectorAll('.lamina'));
  const panelNotas = document.getElementById('panel-notas');
  const cuenta = document.getElementById('cuenta');
  const avance = document.getElementById('avance');
  let actual = -1, paso = 0;
  K.laminas = laminas;

  K.gl = { renderer: null, ok: false };
  try {
    const r = new THREE.WebGLRenderer({ canvas: lienzo, antialias: true, alpha: true, powerPreference: 'high-performance' });
    r.setClearColor(0x000000, 0);
    K.gl.renderer = r;
    K.gl.ok = true;
  } catch (error) {
    console.warn('Sin WebGL: las láminas con 3D muestran su respaldo estático.', error);
    document.documentElement.classList.add('sin-gl');
  }

  function escenaDe(i) { return K.escenas[laminas[i].dataset.id] || null; }
  function pasosDe(i) { return +(laminas[i].dataset.pasos || 1); }

  K.razon = function (tope) { return Math.min(K.escala * (window.devicePixelRatio || 1), tope || 1.34); };

  function ajustar() {
    K.escala = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    escenario.style.transform = 'translate(-50%, -50%) scale(' + K.escala + ')';
    if (K.gl.ok) {
      K.gl.renderer.setPixelRatio(K.razon());
      K.gl.renderer.setSize(1920, 1080, false);
    }
    if (actual >= 0) { const e = escenaDe(actual); if (e && e.alAjustar) e.alAjustar(); }
  }
  window.addEventListener('resize', ajustar);

  // ---------- navegación ----------
  function aplicar(p, inst) {
    const L = laminas[actual], antes = paso;
    paso = p;
    L.dataset.pasoActual = p;
    L.querySelectorAll('[data-paso]').forEach(function (el) { el.classList.toggle('visto', +el.dataset.paso <= p); });
    L.querySelectorAll('[data-hasta]').forEach(function (el) { el.classList.toggle('ido', p > +el.dataset.hasta); });
    const e = escenaDe(actual);
    if (e && e.paso) e.paso(p, !!inst || K.quieto, antes);
    pintarCromo();
  }

  function ir(i, p, inst) {
    i = K.acotar(i, 0, laminas.length - 1);
    if (i !== actual) {
      if (actual >= 0) {
        const vieja = escenaDe(actual);
        laminas[actual].classList.remove('activa');
        if (vieja && vieja.salir) vieja.salir();
      }
      actual = i;
      paso = 0;
      const L = laminas[i], e = escenaDe(i);
      L.querySelectorAll('[data-paso]').forEach(function (el) { el.classList.remove('visto'); });
      void L.offsetWidth;                       // que la entrada vuelva a animarse
      L.classList.add('activa');
      if (e) {
        if (!e._creada) { e._creada = true; if (e.crear) e.crear(L); }
        e._t0 = K.t;
        if (e.entrar) e.entrar(L);
        if (e.alAjustar) e.alAjustar();
      }
      lienzo.classList.toggle('visible', !!(e && e.tres && K.gl.ok));
      lienzo.classList.toggle('interactivo', !!(e && e.interactivo));
    }
    aplicar(K.acotar(p || 0, 0, pasosDe(i) - 1), inst);
  }
  K.ir = ir;
  K.siguiente = function () {
    if (paso < pasosDe(actual) - 1) aplicar(paso + 1, false);
    else if (actual < laminas.length - 1) ir(actual + 1, 0, false);
  };
  K.anterior = function () {
    if (paso > 0) aplicar(paso - 1, true);
    else if (actual > 0) ir(actual - 1, pasosDe(actual - 1) - 1, true);
  };
  K.donde = function () { return { lamina: actual, paso: paso }; };

  function pintarCromo() {
    const total = laminas.filter(function (l) { return !l.dataset.respaldo; }).length;
    const L = laminas[actual];
    cuenta.textContent = L.dataset.respaldo ? 'respaldo' : (actual + 1) + ' / ' + total;
    avance.style.width = (L.dataset.respaldo ? 100 : ((actual + (paso + 1) / pasosDe(actual)) / total) * 100) + '%';
    const notas = L.querySelector('aside.notas');
    panelNotas.innerHTML = notas ? notas.innerHTML : '';
    const marca = '#' + (actual + 1) + (paso ? '.' + paso : '');
    if (location.hash !== marca) history.replaceState(null, '', location.pathname + location.search + marca);
  }

  function leerMarca() {
    const m = /^#(\d+)(?:\.(\d+))?/.exec(location.hash || '');
    return m ? { lamina: +m[1] - 1, paso: m[2] ? +m[2] : 0 } : { lamina: 0, paso: 0 };
  }
  window.addEventListener('hashchange', function () {
    const m = leerMarca();
    if (m.lamina !== actual || m.paso !== paso) ir(m.lamina, m.paso, true);
  });

  K.pausar = function (si) {
    K.pausado = si == null ? !K.pausado : !!si;
    document.documentElement.classList.toggle('pausado', K.pausado);
    gsap.globalTimeline.paused(K.pausado);
  };

  window.addEventListener('keydown', function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    const k = ev.key;
    if (k === 'ArrowRight' || k === ' ' || k === 'PageDown' || k === 'Enter' || k === 'ArrowDown') { K.siguiente(); ev.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'PageUp' || k === 'Backspace' || k === 'ArrowUp') { K.anterior(); ev.preventDefault(); }
    else if (k === 'Home') ir(0, 0, true);
    else if (k === 'End') ir(laminas.length - 1, 0, true);
    else if (/^[0-9]$/.test(k)) ir(k === '0' ? 9 : +k - 1, 0, false);
    else if (k === 'n' || k === 'N') document.documentElement.classList.toggle('con-notas');
    else if (k === 'p' || k === 'P') K.pausar();
    else if (k === 'f' || k === 'F') {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
    } else {
      const e = actual >= 0 ? escenaDe(actual) : null;
      if (e && e.tecla) e.tecla(k);
    }
  });

  // ---------- un solo bucle ----------
  let previo = performance.now(), cuadros = 0, desde = previo;
  function cuadro(ahora) {
    requestAnimationFrame(cuadro);
    let dt = Math.min((ahora - previo) / 1000, 0.05);
    previo = ahora;
    cuadros++;
    if (ahora - desde >= 1000) { K.fps = Math.round((cuadros * 1000) / (ahora - desde)); cuadros = 0; desde = ahora; }
    if (K.pausado || K.quieto) dt = 0;
    K.t += dt;
    if (actual < 0) return;
    const e = escenaDe(actual);
    if (!e) return;
    if (e.cuadro) e.cuadro(K.quieto ? (e.tQuieto == null ? 6 : e.tQuieto) : K.t - e._t0, dt);
    if (e.tres && K.gl.ok) K.gl.renderer.render(e.tres.scene, e.tres.camera);
  }

  // Los números del HTML salen de datos.js: <span data-dato="terreno.colores.actuar" data-formato="miles">
  K.enlazarDatos = function () {
    const d = K.datos;
    d.terreno.n_puntos = d.terreno.puntos.length;
    d.terreno.examen_dentro = Math.round(d.terreno.examen.paso * d.terreno.examen.n);
    d.nube.n_dibujadas = d.nube.puntos.length;
    const formatos = {
      miles: K.miles,
      coma1: function (v) { return K.coma(v, 1); },
      coma2: function (v) { return K.coma(v, 2); },
      coma3: function (v) { return K.coma(v, 3); },
    };
    document.querySelectorAll('[data-dato]').forEach(function (el) {
      let v = d;
      el.dataset.dato.split('.').forEach(function (k) { v = v == null ? v : v[k]; });
      if (v == null) { console.warn('Dato sin valor:', el.dataset.dato); return; }
      el.textContent = el.dataset.formato ? formatos[el.dataset.formato](v) : v;
    });
    const sbc = document.getElementById('tec-sbc');
    if (sbc) sbc.textContent = d.sello.sbc_pasa ? 'sin sesgo: pasa' : 'no pasa';
    const limites = document.getElementById('tec-limites');
    if (limites) limites.innerHTML = d.sello.limitaciones.map(function (t) { return '<li>' + t + '</li>'; }).join('');
    const equipo = document.getElementById('equipo-nombres');
    if (equipo && window.EQUIPO && window.EQUIPO.length) equipo.textContent = window.EQUIPO.join(' · ');
  };

  K.arrancar = function () {
    ajustar();
    const m = leerMarca();
    ir(m.lamina, m.paso, m.paso > 0);
    requestAnimationFrame(cuadro);
    document.documentElement.classList.add('listo');
  };
})();
