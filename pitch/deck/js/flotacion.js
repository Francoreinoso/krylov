/* 9 · La planta: ¿se está perdiendo cobre?
   Las ocho líneas del archivo, cada una como una fila de estanques por donde corre la pulpa (roca molida con agua).
   Lo que se ve, y de dónde sale (todo de datos.js → series.flotacion):
   - En cada estanque, burbujas que suben. Las que brillan llevan cobre: hay más donde flotó más cobre. En los primeros
     estanques es lo que se midió (`puntos`); en los que siguen, lo que la red espera (`respuesta.unidades[id].curva`), más tenue.
   - El cobre que flota rebalsa, corre por la canaleta de su línea y sube por la columna del final: lo recuperado. La columna
     llega hasta la recuperación final que entrega la red, y su punta oscila entre el bajo y el alto del intervalo de 90%.
     La línea blanca que cruza las ocho columnas es la meta de la planta (`umbral`).
   - Lo que no flotó cae al final de la línea al canal del relave (el barro que sobra) y se va. Los destellos de ese chorro
     son el cobre que se pierde: su cantidad es 1 − recuperación, y oscila con el mismo intervalo. Una línea que conviene
     ajustar bota a la vista más cobre que una que va bien.
   - El foco de Krylov (js/foco.js) viaja de línea en línea: la que mira se enciende, las demás bajan, y la tarjeta de la
     izquierda muestra su distribución contra la meta.
   El color de cada línea es su decisión. Nada se calcula aquí: solo se dibuja lo que entregó el motor. */
(function () {
  'use strict';
  const K = window.K;

  K.registrar('flotacion', {
    tres: null, tQuieto: 20,
    crear: function (L) {
      const D3 = K.d3, S = (this.S = K.datos.series.flotacion), R = S.respuesta, n = (this.n = S.unidades.length);
      L.classList.toggle('con-respuesta', !!R);
      // El recorrido del foco: parte por una línea en duda cerca de la meta y alterna los colores de decisión.
      const F = (this.F = K.foco.crear(L, 'flotacion')), ids = S.unidades.map(function (un) { return un.id; });
      const porEstado = { en_duda: [], actuar: [], no_actuar: [] };
      ids.forEach(function (id) { const r = R && R.unidades[id]; if (r) porEstado[r.estado].push(id); });
      const corte = R ? R.punto_de_corte : 0.5;
      porEstado.en_duda.sort(function (a, b) { return Math.abs(R.unidades[a].p - corte) - Math.abs(R.unidades[b].p - corte); });
      porEstado.actuar.sort(function (a, b) { return R.unidades[b].p - R.unidades[a].p; });
      porEstado.no_actuar.sort(function (a, b) { return R.unidades[a].p - R.unidades[b].p; });
      const orden = [];
      for (let k = 0; orden.length < ids.length && k < ids.length; k++) ['en_duda', 'actuar', 'no_actuar'].forEach(function (e) { if (porEstado[e][k]) orden.push(porEstado[e][k]); });
      K.foco.recorrer(F, orden);
      this.indice = {}; ids.forEach(function (id, i) { this.indice[id] = i; }, this);

      // Las etiquetas: la meta, el relave y lo que se pierde en la línea que se mira. Sus estilos viven aquí.
      if (!document.getElementById('estilo-flotacion')) {
        const st = document.createElement('style');
        st.id = 'estilo-flotacion';
        st.textContent =
          '#l-flotacion .etq.fl > div { position: absolute; white-space: nowrap; font-family: var(--texto); font-size: 25px; line-height: 1.15; font-weight: 600; color: var(--tinta); text-shadow: 0 0 8px #0b0a09, 0 0 16px #0b0a09, 0 2px 14px #000; }' +
          '#l-flotacion .etq.fl.meta > div { right: -30px; top: -50px; }' +
          '#l-flotacion .etq.fl.relave > div { left: -40px; top: 26px; color: var(--suave); font-weight: 500; }' +
          '#l-flotacion .etq.fl.relave b { color: var(--tinta); font-weight: 650; }' +
          '#l-flotacion .etq.fl.pierde > div { right: 26px; top: 18px; text-align: right; color: var(--tinta); font-weight: 500; background: #0b0a09e0; padding: 8px 12px 9px; }' +
          '#l-flotacion .etq.fl.pierde b { display: block; font-family: var(--titulo); font-weight: 800; font-size: 58px; line-height: .95; color: var(--cobre); font-variant-numeric: tabular-nums; }';
        document.head.appendChild(st);
      }
      const et = D3.etiquetas(L, 3, 'fl');
      this.etqMeta = et[0]; this.etqRelave = et[1]; this.etqPierde = et[2];
      this.etqMeta.classList.add('meta'); this.etqRelave.classList.add('relave'); this.etqPierde.classList.add('pierde');
      if (!K.gl.ok || !R) return;

      const B = (this.B = D3.base(28)), azar = K.azar(23);
      // ---- la planta, en unidades de escena ----
      const CELDAS = Math.max(1, Math.round(S.tiempo_final / S.unidades[0].puntos[0][0]));      // estanques por línea: lo que dura la línea entre lo que tarda cada uno
      const DX = 1.78, DZ = 1.8, W = 1.42, D = 1.25, H = 1.25, GH = 5.0;
      const xDe = function (c) { return (c - (CELDAS - 1) / 2) * DX; }, zDe = function (l) { return ((n - 1) / 2 - l) * DZ; };
      const xFin = xDe(CELDAS - 1) + W / 2 + 0.12, xCanal = xFin + 1.15, yCanal = -4.3, yBase = H + 0.6, LARGO = 19;
      const eje = F.eje, alturaDe = function (v) { return K.acotar((v - eje.min) / (eje.max - eje.min), 0, 1) * GH; };
      this.geo = { xFin: xFin, xCanal: xCanal, yCanal: yCanal, yBase: yBase, H: H, zDe: zDe, alturaDe: alturaDe, GH: GH, n: n };

      // Cuánto cobre flota en cada estanque: lo medido donde hay medición; después, lo que la red espera (el medio de su curva).
      const minuto = S.unidades[0].puntos[0][0], acum = [], medidos = [];
      let salto = 0;
      S.unidades.forEach(function (un, l) {
        const c = R.unidades[un.id].curva, fila = [];
        for (let k = 0; k < CELDAS; k++) {
          const tk = (k + 1) * minuto;
          if (k < un.puntos.length) fila.push(un.puntos[k][1]);
          else {
            let i = 1;
            while (i < c.t_banda.length - 1 && c.t_banda[i] < tk) i++;
            const f = K.acotar((tk - c.t_banda[i - 1]) / (c.t_banda[i] - c.t_banda[i - 1]), 0, 1);
            fila.push(Math.max(fila[k - 1] || 0, K.mezcla(c.medio[i - 1], c.medio[i], f)));
          }
          salto = Math.max(salto, fila[k] - (k ? fila[k - 1] : 0));
        }
        acum[l] = fila; medidos[l] = un.puntos.length;
      });
      const rico = function (l, c) { return (acum[l][c] - (c ? acum[l][c - 1] : 0)) / salto; };

      // lo que cada sistema sabe de su línea: el foco, y cuánto de la planta ya «partió» al entrar a la lámina
      this.foc = { value: new THREE.Vector3(-1, -1, 0) };
      this.parte = { value: 0 };
      const rec = (this.rec = { value: [] });
      S.unidades.forEach(function (un) { const q = R.posteriori[un.id]; rec.value.push(new THREE.Vector3(q.bajo, q.medio, q.alto)); });
      const comun = { uFoc: this.foc, uParte: this.parte, uRec: rec };
      const MIRA = `
        uniform vec3 uFoc;             // la línea que se mira, la que viene y cuánto se ha avanzado de una a la otra
        uniform float uParte;          // de 0 a 1.6: la pulpa entra por la izquierda y recorre la planta
        uniform vec3 uRec[${n}];       // recuperación final de cada línea: bajo, medio y alto del intervalo de 90%
        float mira(float l) { return (abs(l - uFoc.x) < 0.5 ? 1.0 - uFoc.z : 0.0) + (abs(l - uFoc.y) < 0.5 ? uFoc.z : 0.0); }
        float llega(float x) { return smoothstep(0.0, 0.12, uParte - (x + ${(-xDe(0) + 1).toFixed(2)}) / ${(xFin - xDe(0) + 2).toFixed(2)}); }
        // la recuperación de la línea ahora: va y viene, lenta, entre el bajo y el alto de su intervalo
        float ahora(float l) { vec3 r = uRec[int(l + 0.5)]; return mix(r.x, r.z, 0.5 + 0.5 * sin(uT * 0.85 + l * 1.9)); }`;

      // ---- los estanques: su armazón de puntos, teñido con la decisión de la línea ----
      const pa = [], aa = [], ta = [];
      const tramo = function (x0, y0, z0, x1, y1, z1, l, medido, col, fuerza) {
        const largo = Math.hypot(x1 - x0, y1 - y0, z1 - z0), m = Math.max(1, Math.ceil(largo / 0.075));
        for (let k = 0; k <= m; k++) { pa.push(K.mezcla(x0, x1, k / m), K.mezcla(y0, y1, k / m), K.mezcla(z0, z1, k / m)); aa.push(l, medido, fuerza, azar()); ta.push(col[0], col[1], col[2]); }
      };
      for (let l = 0; l < n; l++) {
        const col = D3.tinteDe(S, S.unidades[l].id, [0.5, 0.45, 0.38]), z = zDe(l), z0 = z - D / 2, z1 = z + D / 2;
        for (let c = 0; c < CELDAS; c++) {
          const x = xDe(c), x0 = x - W / 2, x1 = x + W / 2, m = c < medidos[l] ? 1 : 0;
          [[x0, z0, x1, z0], [x1, z0, x1, z1], [x1, z1, x0, z1], [x0, z1, x0, z0]].forEach(function (q) {
            tramo(q[0], H, q[1], q[2], H, q[3], l, m, col, 1);                                    // el borde de arriba, por donde rebalsa la espuma
            tramo(q[0], 0, q[1], q[2], 0, q[3], l, m, col, 0.45);
            tramo(q[0], 0, q[1], q[0], H, q[1], l, m, col, 0.6);
          });
        }
        tramo(xDe(0) - W / 2, H - 0.18, z1 + 0.3, xFin - 0.2, H - 0.18, z1 + 0.3, l, 1, col, 0.5);   // la canaleta de lo recuperado
        tramo(xFin - 0.2, yBase, z, xFin - 0.2, yBase + GH, z, l, 1, col, 0.55);                      // el eje de su columna
      }
      B.puntos({ position: [pa, 3], aA: [aa, 4], aTinte: [ta, 3] }, MIRA + `
        attribute vec4 aA;             // línea, si ese estanque ya se midió, cuánto pesa este trazo, azar
        attribute vec3 aTinte;
        void main() {
          float m = mira(aA.x);
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          vColor = mix(ARENA, aTinte, 0.35 + 0.5 * m);
          vA = aA.z * (0.16 + 0.2 * aA.y) * mix(0.65, 2.3, m) * llega(position.x);
          gl_PointSize = (0.03 + 0.012 * m) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);

      // ---- la pulpa y sus burbujas: suben dentro de cada estanque; las que llevan cobre brillan al llegar a la espuma ----
      const pp = [], ab = [], al = [];
      for (let l = 0; l < n; l++) for (let c = 0; c < CELDAS; c++) {
        const r = rico(l, c), m = c < medidos[l] ? 1 : 0.5;
        for (let i = 0; i < 230; i++) {
          pp.push(xDe(c) + (azar() - 0.5) * W * 0.86, i < 110 ? H * (0.9 + 0.1 * azar()) : azar() * H, zDe(l) + (azar() - 0.5) * D * 0.86);
          ab.push(azar(), azar(), r, m); al.push(l);
        }
      }
      B.puntos({ position: [pp, 3], aB: [ab, 4], aL: [al, 1] }, MIRA + `
        attribute vec4 aB;             // ritmo, fase, cobre que flota en este estanque (0 a 1), y si es medido (1) o esperado (0,5)
        attribute float aL;
        void main() {
          float capa = step(${(H * 0.9).toFixed(3)}, position.y);                  // la mitad de los puntos es la espuma de arriba; el resto, burbujas que suben
          float sube = capa > 0.5 ? position.y + 0.05 * sin(uT * (1.5 + 2.0 * aB.x) + aB.y * 40.0) : mod(position.y + uT * (0.22 + 0.5 * aB.x), ${H.toFixed(2)});
          vec3 p = vec3(position.x + sin(uT * 1.3 + aB.y * 30.0) * 0.045, sube, position.z);
          float espuma = smoothstep(${(H * 0.7).toFixed(2)}, ${(H * 0.96).toFixed(2)}, sube);
          float cobre = step(aB.y, 0.12 + 0.62 * aB.z);                          // qué parte de las burbujas lleva cobre
          float m = mira(aL);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(mix(ARENA, OXIDO, 0.55) * 0.9, mix(COBRE, ORO, 0.35 + 0.65 * aB.z), cobre * (0.35 + 0.65 * espuma));
          vA = (0.1 + cobre * 0.16 + espuma * (0.1 + 1.0 * cobre * (0.35 + 0.65 * aB.z))) * aB.w * mix(0.5, 1.5, m) * llega(position.x);
          gl_PointSize = (0.04 + 0.04 * aB.x + espuma * cobre * 0.09 * (0.5 + aB.z)) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);

      // ---- lo recuperado: la espuma rebalsa, corre por la canaleta y sube por la columna del final de su línea ----
      const pr = [], ar = [], lr = [];
      for (let l = 0; l < n; l++) for (let c = 0; c < CELDAS; c++) {
        const r = rico(l, c), cuantas = Math.round(10 + 120 * r), m = c < medidos[l] ? 1 : 0.55;
        for (let i = 0; i < cuantas; i++) { pr.push(xDe(c) + (azar() - 0.5) * W * 0.9, H, zDe(l) + D / 2); ar.push(azar(), 0.45 + 0.55 * r, m, azar()); lr.push(l); }
      }
      B.puntos({ position: [pr, 3], aR: [ar, 4], aL: [lr, 1] }, MIRA + `
        attribute vec4 aR;             // fase, cuánto cobre flotó ahí, medido o esperado, azar
        attribute float aL;
        void main() {
          float u = fract(uT * 0.13 + aR.x);
          float cae = clamp(u / 0.14, 0.0, 1.0), corre = clamp((u - 0.14) / 0.86, 0.0, 1.0);
          vec3 p = vec3(mix(position.x, ${(xFin - 0.2).toFixed(2)}, corre * corre * (3.0 - 2.0 * corre)), position.y - 0.18 * cae * cae + 0.03 * sin(uT * 3.0 + aR.w * 20.0), position.z + 0.3 * cae);
          float m = mira(aL);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = mix(ORO, COBRE, 0.25 + 0.5 * corre);
          vA = aR.y * aR.z * (0.25 + 0.75 * sin(3.1416 * u)) * mix(0.42, 1.5, m) * llega(position.x);
          gl_PointSize = (0.042 + 0.05 * aR.y) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);

      // la columna: partículas que suben hasta la recuperación de la línea; la punta se mueve entre el bajo y el alto
      const pg = [], ag = [], tg = [];
      for (let l = 0; l < n; l++) {
        const col = D3.tinteDe(S, S.unidades[l].id, [1.0, 0.82, 0.45]);
        for (let i = 0; i < 300; i++) { pg.push(xFin - 0.2 + (azar() - 0.5) * 0.3, yBase, zDe(l) + (azar() - 0.5) * 0.42); ag.push(l, azar(), azar()); tg.push(col[0], col[1], col[2]); }
      }
      B.puntos({ position: [pg, 3], aG: [ag, 3], aTinte: [tg, 3] }, MIRA + `
        attribute vec3 aG;             // línea, fase, azar
        attribute vec3 aTinte;
        void main() {
          float nivel = clamp((ahora(aG.x) - ${eje.min.toFixed(4)}) / ${(eje.max - eje.min).toFixed(4)}, 0.0, 1.0) * ${GH.toFixed(2)} * smoothstep(1.0, 1.5, uParte);
          float u = fract(uT * (0.1 + 0.08 * aG.z) + aG.y);
          float m = mira(aG.x);
          vec4 mv = modelViewMatrix * vec4(position + vec3(0.0, u * nivel, 0.0), 1.0);
          float punta = smoothstep(0.86, 1.0, u);
          vColor = mix(aTinte, vec3(1.0, 0.96, 0.86), punta * 0.8);
          vA = (0.5 + 0.9 * punta) * mix(0.5, 1.4, m) * step(0.02, nivel);
          gl_PointSize = (0.075 + 0.08 * punta + 0.03 * m) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);
      // la meta de la planta, a la misma altura en las ocho columnas
      const yMeta = (this.yMeta = yBase + alturaDe(S.umbral)), zA = zDe(0) + 1.1, zB = zDe(n - 1) - 0.9, meta = [];
      for (let k = 0; k < 46; k++) meta.push(xFin - 0.2, yMeta, K.mezcla(zA, zB, k / 46), xFin - 0.2, yMeta, K.mezcla(zA, zB, (k + 0.55) / 46));
      this.meta = B.cordon(meta, 0.04, 0xffffff, 0, 0.042);
      this.zMeta = zB;

      // ---- lo que se pierde: al final de cada línea, lo que no flotó cae al canal del relave y se va ----
      // El barro es el mismo en todas las líneas; los destellos de cobre, tantos como lo que esa línea pierde.
      const pt = [], at = [], lt = [], P0 = 1 - eje.max, P1 = 1 - eje.min;                       // el mismo eje de la tarjeta y de la columna, al revés
      for (let l = 0; l < n; l++) {
        for (let i = 0; i < 420; i++) { pt.push(xFin, H * 0.82, zDe(l)); at.push(azar(), azar(), azar(), -1); lt.push(l); }                // barro
        for (let i = 0; i < 1300; i++) { pt.push(xFin, H * 0.82, zDe(l)); at.push(azar(), azar(), azar(), (i + 0.5) / 1300); lt.push(l); }     // cobre
      }
      B.puntos({ position: [pt, 3], aT: [at, 4], aL: [lt, 1] }, MIRA + `
        attribute vec4 aT;             // fase, azar a lo ancho, azar, y su turno (0 a 1) si es cobre; −1 si es barro
        attribute float aL;
        void main() {
          float cobre = step(0.0, aT.w);
          float pierde = clamp((1.0 - ahora(aL) - ${P0.toFixed(4)}) / ${(P1 - P0).toFixed(4)}, 0.0, 1.0);
          float sale = cobre > 0.5 ? 1.0 - smoothstep(pierde - 0.03, pierde + 0.03, aT.w) : 1.0;                               // más pérdida, más destellos
          float u = fract(uT * (0.075 + 0.03 * aT.z) + aT.x);
          float cae = clamp(u / 0.3, 0.0, 1.0), corre = clamp((u - 0.3) / 0.7, 0.0, 1.0);
          float ancho = (aT.y - 0.5) * ${(D * 0.92).toFixed(2)};
          vec3 p = vec3(position.x + ${(xCanal - xFin).toFixed(2)} * (1.0 - (1.0 - cae) * (1.0 - cae)) + (aT.z - 0.5) * 0.7 * smoothstep(0.6, 1.0, cae),
                        mix(position.y, ${yCanal.toFixed(2)}, cae * cae) + (0.06 * sin(uT * 4.0 + aT.x * 40.0) + 0.25 * aT.z * aT.z) * corre,
                        position.z + ancho * (1.0 - 0.3 * corre) - corre * ${LARGO.toFixed(1)});
          float m = mira(aL);
          float vida = smoothstep(0.0, 0.03, u) * (1.0 - smoothstep(0.55, 1.0, u));
          float chispa = 0.62 + 0.38 * sin(uT * 6.0 + aT.x * 90.0);
          float enCanal = step(0.999, cae);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          vColor = cobre > 0.5 ? mix(mix(ORO, COBRE, 0.45 + 0.4 * aT.z), COBRE, smoothstep(0.0, 0.6, corre)) : ARENA * 0.8;
          vA = sale * vida * smoothstep(1.15, 1.6, uParte) * (cobre > 0.5 ? chispa * mix(mix(0.8, 1.7, m), 0.8, enCanal * smoothstep(0.0, 0.2, corre)) : 0.3 * mix(0.75, 1.3, m));
          gl_PointSize = (cobre > 0.5 ? 0.05 + 0.05 * aT.z + 0.025 * m : 0.045 + 0.035 * aT.z) * uEsc / -mv.z;
          gl_Position = projectionMatrix * mv;
        }`, comun);
      // los bordes del canal
      const zC0 = zDe(0) + 1.4, zC1 = zDe(n - 1) - LARGO;
      this.canal = B.cordon([xCanal - 0.75, yCanal - 0.14, zC0, xCanal - 0.75, yCanal - 0.14, zC1, xCanal + 0.75, yCanal - 0.14, zC0, xCanal + 0.75, yCanal - 0.14, zC1], 0.07, 0x8a7f70, 0, 0.03);

      this.tres = B.tres;
    },
    alAjustar: function () { if (this.B) this.B.ajustar(); if (this.F) K.foco.ajustar(this.F); },
    entrar: function () { if (this.F) K.foco.reiniciar(this.F); },
    cuadro: function (t) {
      const F = this.F, S = this.S, yo = this;
      if (!this.tres) { K.foco.cuadro(F, t, function () { return null; }); return; }
      const B = this.B, G = this.geo;
      B.u.uT.value = t;
      this.parte.value = K.quieto ? 2 : K.acotar((t - 0.1) / 1.0, 0, 2);
      const listo = K.quieto ? 1 : K.suave((t - 0.9) / 0.5);
      this.meta.alfa.value = 0.9 * listo;
      this.canal.alfa.value = 0.26 * listo;
      // la cámara mira la planta desde el lado por donde sale: deriva apenas, nunca salta
      B.mirar(1.2 + Math.sin(t * 0.13) * 0.03, 0.36 + Math.sin(t * 0.09) * 0.012, 45, [3.0, -0.2, -0.2], -385);
      // el foco: el punto de cada línea donde se ve lo que pierde (la mitad de su caída al relave)
      const punto = function (id) { return K.proyectar(G.xFin + 0.62, (G.H * 0.82 + G.yCanal) * 0.5 + 0.35, G.zDe(yo.indice[id]), B.camera); };
      K.foco.cuadro(F, t, punto, 3.6, 1.1);
      this.foc.value.set(this.indice[F.a], F.b == null ? -1 : this.indice[F.b], F.e);
      // lo que se pierde en la línea que se mira: 1 − su recuperación (la estimación de la red), contado de una a otra
      const A = F.fichas[F.a], Bf = F.b ? F.fichas[F.b] : null, medio = Bf ? K.mezcla(A.medio, Bf.medio, F.e) : A.medio;
      const texto = '<b>' + K.coma((1 - medio) * 100, 1) + '%</b>se va al relave', el = this.etqPierde;
      if (el._h !== texto) { el.firstChild.innerHTML = texto; el._h = texto; }
      el.style.transform = 'translate(' + (F.px || 0).toFixed(1) + 'px,' + (F.py || 0).toFixed(1) + 'px)';
      el.classList.toggle('ver', listo > 0.6 && F.px != null);
      K.d3.poner(this.etqMeta, B.camera, G.xFin - 0.2, this.yMeta, this.zMeta, 'Meta: ' + Math.round(S.umbral * 100) + '%', listo > 0.5);
      K.d3.poner(this.etqRelave, B.camera, G.xCanal, G.yCanal - 0.1, G.zDe(Math.floor(this.n / 2)), '<b>Relave</b>: lo que sobra', listo > 0.5);
    },
  });
})();
