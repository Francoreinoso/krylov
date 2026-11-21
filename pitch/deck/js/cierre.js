/* 9 · Cierre: la frase, el QR y, de fondo, los terrenos simulados pasando. */
(function () {
  'use strict';
  const K = window.K;

  K.registrar('cierre', {
    tres: null,
    tQuieto: 33,
    crear: function () {
      this.campo = K.campo();
      if (this.campo) this.tres = this.campo.tres;
    },
    entrar: function () { if (this.campo) this.campo.ventana(0.97, 0.52); },
    cuadro: function (t) {
      if (this.campo) this.campo.actualizar(t * 0.6 + 40, 0, 0.8);
    },
  });
})();
