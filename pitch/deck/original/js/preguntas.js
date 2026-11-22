/* Las láminas de preguntas (fuera del recorrido; cada una se abre con su tecla): lo que preguntaría quien dirige una empresa.
   - Q · ¿Quién lo usa?: las cinco figuras de la lámina «Cinco decisiones», cada una con la persona que toma esa decisión.
   - A · ¿Qué archivo recibe?: el que pide el modelo de cada decisión (casos/<caso>.yaml → datos.js → modelos).
   - L · ¿Y un LLM?: tendría que correr el modelo caro cada vez. A la izquierda, una cadena de MCMC de verdad (Metropolis,
     corrida aquí con semilla) que arma la posteriori muestra por muestra; a la derecha, la misma posteriori de una vez.
     Los tiempos son los de la prueba de pitch/deck/datos/prueba_llm/ y el del sello.
   - M · Cada predicción viene con su intervalo de credibilidad: los intervalos de la planta y lo que de verdad pasó. */
(function () {
  'use strict';
  const K = window.K;

  // ============================== Q · ¿Quién lo usa? ==============================
  // Comparte la escena 3D de la lámina de las cinco decisiones: las mismas figuras, ahora con quién decide.
  K.registrar('quien', {
    tres: null, tQuieto: 9.3,
    crear: function () {
      const v = (this.v = K.escenas.vision);
      if (!v._creada) { v._creada = true; v.crear(document.getElementById('l-vision')); }
      this.tres = v.tres;
    },
    alAjustar: function () { this.v.alAjustar(); },
    cuadro: function (t) { this.v.cuadro(t); },
  });

  // ============================== A · ¿Qué archivo recibe? ==============================
  const DECISION = { leyes: 'La roca', taludes: 'La pared', flotacion: 'La planta', flota: 'Los camiones', sismicidad: 'Los túneles' };
  const FILA = {
    leyes: 'una muestra: dónde está y cuánto arsénico tiene', taludes: 'una lectura del radar: qué sector, a qué hora y cuántos milímetros',
    flotacion: 'una medición: qué línea, a qué minuto y cuánto cobre lleva recuperado', flota: 'una muestra de aceite: qué camión, con cuántas horas, su desgaste y la exigencia de su ruta',
    sismicidad: 'un temblor: en qué sector, a qué hora y de qué magnitud',
  };
  const QUE = { leyes: 'muestras', taludes: 'lecturas', flotacion: 'mediciones', flota: 'muestras de aceite', sismicidad: 'temblores' };
  // el dibujo de cómo agrupa el modelo: el conjunto, sus unidades y las filas de cada una
  function niveles(m) {
    const n = m.unidades ? Math.min(m.unidades, 7) : 0;
    let s = '<svg viewBox="0 0 330 64" class="niveles"><circle cx="16" cy="32" r="13"/>';
    for (let i = 0; i < n; i++) {
      const y = 8 + (i / Math.max(1, n - 1)) * 48;
      s += '<path d="M29 32 C 70 32 70 ' + y + ' 112 ' + y + '"/><circle cx="118" cy="' + y + '" r="5.5"/>';
      for (let k = 0; k < 9; k++) s += '<circle class="fila" cx="' + (150 + k * 19) + '" cy="' + y + '" r="2.4"/>';
    }
    if (!n) for (let i = 0; i < 48; i++) s += '<circle class="fila" cx="' + (60 + (i % 12) * 22 + ((i * 7) % 5) * 2) + '" cy="' + (10 + Math.floor(i / 12) * 15 + ((i * 3) % 4) * 2) + '" r="2.6"/>';
    return s + '</svg>';
  }
  K.registrar('archivo', {
    crear: function (L) {
      L.querySelector('#modelos').innerHTML = K.datos.modelos.map(function (m) {
        const grupos = m.unidades ? '<b>' + m.unidades + ' ' + m.unidad.plural + '</b>, ' + K.miles(m.filas) + ' ' + QUE[m.caso] : '<b>Un terreno</b>, ' + K.miles(m.filas) + ' ' + QUE[m.caso];
        return '<div class="fila"><span class="t3">' + DECISION[m.caso] + '</span>' + niveles(m) +
          '<span class="p"><span class="grupos">' + grupos + '</span>Cada fila, ' + FILA[m.caso] + '.</span>' +
          '<span class="cols">' + m.columnas.map(function (c) { return c.nombre; }).join('  ·  ') + '</span></div>';
      }).join('');
    },
  });

  // ============================== L · ¿Y un LLM? ==============================
  K.registrar('llm', {
    tres: null, tQuieto: 60.6,
    crear: function (L) {
      const R = K.datos.prueba_llm, S = K.datos.sello;
      if (R) {
        const a = Math.min(R.llm_a.segundos, R.llm_b.segundos), b = Math.max(R.llm_a.segundos, R.llm_b.segundos);
        L.querySelector('#llm-lento').textContent = Math.floor(a / 60) + ' a ' + Math.ceil(b / 60) + ' minutos';
        L.querySelector('#llm-rapido').textContent = S.latencia_ms + ' milisegundos';
        L.querySelector('#llm-prueba').textContent = 'Lo probamos con el mismo archivo: ' + R.llm_a.segundos + ' y ' + R.llm_b.segundos + ' segundos, para acertar parecido (' + R.llm_a.dentro + ' y ' + R.llm_b.dentro + ' de ' + R.krylov.n + ', contra ' + R.krylov.dentro + ').';
      }
      if (!K.gl.ok || !K.base3d) return;
      const B = (this.B = K.base3d(30)), azar = K.azar(77), N = 2600;
      // Una cadena de Metropolis de verdad sobre una posteriori con forma de banana: cada paso propone moverse un poco
      // y acepta o no. Así arma la respuesta el método caro: de a una muestra.
      const normal = function () { return Math.sqrt(-2 * Math.log(1 - azar())) * Math.cos(6.2832 * azar()); };
      const logp = function (p) { const c = p[1] - 0.32 * (p[0] * p[0] - 2.6); return -0.5 * ((p[0] * p[0]) / 2.6 + (c * c) / 0.36 + (p[2] * p[2]) / 0.8); };
      let actual = [2.6, 2.2, 0.8], la = logp(actual);
      const cadena = [], orden = [];
      for (let i = 0; i < N; i++) {
        const prop = [actual[0] + normal() * 0.5, actual[1] + normal() * 0.5, actual[2] + normal() * 0.5], lp = logp(prop);
        if (Math.log(azar()) < lp - la) { actual = prop; la = lp; }
        cadena.push(actual[0] * 1.5 + normal() * 0.03, actual[1] * 1.5 - 1.2 + normal() * 0.03, actual[2] * 1.5 + normal() * 0.03); orden.push(i / N);
      }
      this.avance = { value: 0 };
      const lento = B.puntos({ position: [cadena, 3], aI: [orden, 1] }, `
        attribute float aI;            // en qué paso de la cadena salió esta muestra (0 a 1)
        uniform float uAv;
        void main() {
          float ya = step(aI, uAv), reciente = ya * exp(-(uAv - aI) * ${N}.0 / 55.0);     // las últimas, encendidas: la cabeza de la cadena
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(ARENA * 1.5, vec3(1.0, 0.95, 0.85), reciente);
          vA = ya * (0.3 + 1.5 * reciente);
          gl_PointSize = (0.07 + 0.2 * reciente) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uAv: this.avance });
      // Krylov: la misma posteriori, entera, con cada dataset que llega
      const mezcla = [], ar = [];
      for (let i = N - 1; i >= 0; i -= 2) { mezcla.push(cadena[i * 3], cadena[i * 3 + 1], cadena[i * 3 + 2]); ar.push(azar()); }
      const rapido = B.puntos({ position: [mezcla, 3], aR: [ar, 1] }, `
        attribute float aR;
        void main() {
          float ciclo = uT / 1.5, c = fract(ciclo), giro = floor(ciclo) * 2.1;            // cada vuelta, un dataset distinto
          float abre = 1.0 - pow(1.0 - clamp(c / 0.16, 0.0, 1.0), 3.0);
          float co = cos(giro), si = sin(giro);
          vec3 p = vec3(position.x * co - position.z * si, position.y, position.x * si + position.z * co) * (0.12 + 0.88 * abre);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(vec3(1.0, 0.95, 0.85), mix(COBRE, ORO, aR), clamp(c / 0.3, 0.0, 1.0));
          vA = (0.5 + 0.9 * exp(-c * 6.0)) * (1.0 - smoothstep(0.82, 1.0, c));
          gl_PointSize = (0.07 + 0.05 * aR) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`);
      lento.position.x = -8.6; rapido.position.x = 8.6;
      this.nubes = [lento, rapido];
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      if (!this.tres) return;
      const DURA = 26, ESPERA = 3, x = t % (DURA + ESPERA);
      this.B.u.uT.value = t;
      this.avance.value = K.quieto ? 0.55 : Math.min(1, x / DURA);
      this.nubes.forEach(function (n) { n.rotation.y = t * 0.16; });
      this.B.mirar(0, 0.14, 46, [0, -4.4, 0], 0);          // las nubes, arriba; el texto de cada una, debajo
    },
  });

  // ============================== M · Cada predicción, con su intervalo ==============================
  K.registrar('produccion', {
    crear: function (L) {
      const S = K.datos.series.flotacion, caja = L.querySelector('#int-produccion');
      if (!S.respuesta) { caja.hidden = true; return; }
      const o = K.filasDe.flotacion(true);
      const dentro = o.filas.filter(function (f) { return f.verdad >= f.bajo && f.verdad <= f.alto; }).length;
      K.intervalos(caja, o);
      L.querySelector('#int-cuenta').textContent = dentro + ' de ' + o.filas.length;
    },
  });
})();
