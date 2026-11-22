/* 4 · Millones de simulaciones: el remolino de terrenos y el contador.
   El número grande es la suma de las simulaciones con que pre-entrenaron los cinco modelos que pasaron su sello
   (M-01 y M-48; la suma es M-66). Debajo, el desglose por modelo y el tiempo total de pre-entrenamiento. Todo sale
   de datos.js: sello (la roca) y series.<caso>.respuesta.sello (los otros cuatro). */
(function () {
  'use strict';
  const K = window.K;
  const MODELOS = [['leyes', 'bancos de roca'], ['taludes', 'paredes'], ['flotacion', 'plantas'], ['flota', 'flotas de camiones'], ['sismicidad', 'túneles']];
  const millones = function (n) { return K.coma(n / 1e6, 1) + ' M'; };

  K.registrar('mundos', {
    tres: null,
    tQuieto: 21,
    s: { mezcla: 0 },
    crear: function (L) {
      const d = K.datos;
      let total = 0, minutos = 0;
      const partes = MODELOS.map(function (m) {
        const S = m[0] === 'leyes' ? d.sello : d.series[m[0]].respuesta.sello;
        total += S.simulaciones_entrenamiento; minutos += S.entrenamiento_min;
        return '<div><b class="num">' + millones(S.simulaciones_entrenamiento) + '</b><span>' + m[1] + '</span></div>';
      });
      this.contador = L.querySelector('#contador-mundos');
      this.total = total;
      this.filas = L.querySelector('#desglose-mundos');
      this.filas.innerHTML = partes.join('');
      L.querySelector('#sub-mundos').textContent = 'Cinco modelos, pre-entrenados en dos notebooks en menos de ' + Math.ceil(minutos / 60) + ' horas.';
      this.campo = K.campo();
      if (this.campo) this.tres = this.campo.tres;
    },
    entrar: function () { this.s.mezcla = 0; if (this.campo) this.campo.ventana(0.8, 0.5); },
    paso: function (p, inst) {
      if (this.cuenta) this.cuenta.kill();
      K.anim(this.s, { mezcla: 0 }, 1.2, inst);
      // el contador sube desde cero y frena al llegar; el desglose aparece cuando ya se leyó la suma
      this.cuenta = K.contar(this.contador, 0, this.total, 2.2, K.miles, inst, 'expo.out');
      this.filas.classList.remove('ver');
      if (inst || K.quieto) this.filas.classList.add('ver');
      else { const f = this.filas; clearTimeout(this.reloj); this.reloj = setTimeout(function () { f.classList.add('ver'); }, 1500); }
    },
    salir: function () { clearTimeout(this.reloj); },
    cuadro: function (t) {
      if (this.campo) this.campo.actualizar(t, this.s.mezcla, K.mezcla(0.92, 1, this.s.mezcla));
    },
  });
})();
