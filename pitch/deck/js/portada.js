/* 1 · Portada: un camión minero hecho de decenas de miles de puntos, avanzando, mientras una franja de luz lo recorre
   de punta a punta. Es una ilustración (el mismo modelo de la lámina de la flota, más denso): dice «minería» y dice
   «datos» antes de que nadie lea nada. No representa ninguna medición. */
(function () {
  'use strict';
  const K = window.K;
  const RUEDA = 0.92, VEL = 1.6;

  K.registrar('valor', {
    tres: null, tQuieto: 5.2,
    crear: function () {
      if (!K.gl.ok || !K.base3d) return;
      const B = (this.B = K.base3d(26)), pos = [], aq = [];
      for (let v = 0; v < 5; v++) {                              // cinco pasadas con azar distinto: la carrocería queda maciza
        const m = K.camionDePuntos(K.azar(101 + v * 17), RUEDA);
        for (let i = 0; i < m.P.length; i++) pos.push(m.P[i]);
        for (let i = 0; i < m.Q.length; i++) aq.push(m.Q[i]);
      }
      this.giro = { value: 0 };
      B.puntos({ position: [pos, 3], aQ: [aq, 4] }, `
        attribute vec4 aQ;             // tipo (1: rueda, 2: foco), brillo, y para las ruedas su ángulo y su radio
        uniform float uGiro;
        void main() {
          float rueda = step(0.5, aQ.x) * step(aQ.x, 1.5), foco = step(1.5, aQ.x);
          vec3 p = position;
          float a = aQ.z - uT * ${(VEL / RUEDA).toFixed(3)};
          p.x += rueda * aQ.w * cos(a);
          p.y += rueda * aQ.w * sin(a);
          float barre = mod(uT * 1.5, 11.0) - 4.0;                           // la franja que lo recorre, de atrás hacia adelante
          float luz = exp(-pow((p.x - barre) / 0.34, 2.0));
          float co = cos(uGiro), si = sin(uGiro);
          vec3 w = vec3(p.x * co - p.z * si, p.y, p.x * si + p.z * co);
          float frente = mix(0.3, 1.0, smoothstep(-1.2, 1.2, w.z));          // el costado que mira a la cámara, más encendido
          vec4 mv = modelViewMatrix * vec4(w, 1.0);
          vec3 base = mix(COBRE, ORO, 0.25 + 0.5 * aQ.y);
          vColor = foco > 0.5 ? vec3(1.0, 0.96, 0.86) : mix(mix(base, ARENA, rueda * 0.5), vec3(1.0, 0.95, 0.84), luz * 0.85);
          vA = foco > 0.5 ? 1.8 : (0.13 + 0.4 * aQ.y) * frente + luz * 0.55;
          gl_PointSize = (foco > 0.5 ? 0.13 : 0.024 + 0.011 * aQ.y + 0.02 * luz) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uGiro: this.giro });
      // el camino: puntos que pasan hacia atrás, para que se vea que avanza
      const azar = K.azar(7), pc = [], ar = [];
      for (let i = 0; i < 2600; i++) { pc.push((azar() - 0.5) * 60, 0, (azar() - 0.5) * 14); ar.push(azar()); }
      B.puntos({ position: [pc, 3], aR: [ar, 1] }, `
        attribute float aR;
        uniform float uGiro;
        void main() {
          float x = mod(position.x - uT * ${VEL.toFixed(2)} + 30.0, 60.0) - 30.0;
          float co = cos(uGiro), si = sin(uGiro);
          vec3 w = vec3(x * co - position.z * si, 0.0, x * si + position.z * co);
          vec4 mv = modelViewMatrix * vec4(w, 1.0);
          vColor = ARENA;
          vA = (0.1 + 0.2 * aR) * smoothstep(30.0, 14.0, abs(x)) * smoothstep(7.0, 2.0, abs(position.z));
          gl_PointSize = (0.03 + 0.03 * aR) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, { uGiro: this.giro });
      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); },
    cuadro: function (t) {
      if (!this.tres) return;
      this.B.u.uT.value = t;
      this.giro.value = -0.62 + Math.sin(t * 0.22) * 0.2;                    // se muestra de tres cuartos, y gira apenas
      this.B.mirar(0, 0.16, 16.5, [0, 1.75, 0], -500);
    },
  });
})();
