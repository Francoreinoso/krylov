/* 3 · Millones de mundos simulados: el remolino de terrenos, el contador (M-01) y la pila que queda entrenada. */
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
    entrar: function () { this.s.mezcla = 0; if (this.campo) this.campo.ventana(0.74, 0.34); },
    paso: function (p, inst) {
      if (this.cuenta) this.cuenta.kill();
      if (p === 0) {
        K.anim(this.s, { mezcla: 0 }, 1.2, inst);
        // la cifra se lee casi de inmediato: cuenta el último 10% en 1,2 s
        this.cuenta = K.contar(this.contador, Math.round(this.total * 0.9), this.total, 1.2, K.miles, inst, 'power2.out');
      } else {
        K.cifra(this.contador, K.miles(this.total));
        K.anim(this.s, { mezcla: 1 }, 5.0, inst, 'power1.inOut');
      }
    },
    cuadro: function (t) {
      if (this.campo) this.campo.actualizar(t, this.s.mezcla, K.mezcla(0.92, 1, this.s.mezcla));
    },
  });
})();
