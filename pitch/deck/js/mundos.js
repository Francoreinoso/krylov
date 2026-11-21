/* 3 · Millones de mundos simulados: el campo de terrenos, el contador (M-01) y la pila. */
(function () {
  'use strict';
  const K = window.K;

  K.registrar('mundos', {
    tres: null,
    tQuieto: 21,
    s: { mezcla: 0 },
    crear: function (L) {
      this.contador = L.querySelector('#contador-mundos');
      this.total = K.datos.sello.simulaciones_entrenamiento;
      this.campo = K.campo();
      if (this.campo) this.tres = this.campo.tres;
    },
    entrar: function () { this.s.mezcla = 0; if (this.campo) this.campo.ventana(0.72, 0.33); },
    paso: function (p, inst) {
      if (this.cuenta) this.cuenta.kill();
      if (p === 0) {
        K.anim(this.s, { mezcla: 0 }, 1.2, inst);
        this.cuenta = K.contar(this.contador, 0, this.total, 5.5, K.miles, inst);
      } else {
        this.contador.textContent = K.miles(this.total);
        K.anim(this.s, { mezcla: 1 }, 5.2, inst, 'power1.inOut');
      }
    },
    cuadro: function (t) {
      if (this.campo) this.campo.actualizar(t, this.s.mezcla, K.mezcla(0.9, 1, this.s.mezcla));
    },
  });
})();
