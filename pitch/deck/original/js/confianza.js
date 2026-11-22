/* 12 · «¿Y cómo sé que acierta?»: la accuracy de cada modelo, de 0 a 1. Una sola medida, la misma para los cinco:
   de las unidades donde Krylov decidió (actuar o no actuar), en cuántas acertó, según la verdad escondida del archivo
   de demo de ese caso. Las que dejó «en duda» no cuentan: ahí dijo que no sabía.
   Sale de datos.js: terreno.examen_bloques (nucleo/espacial.examen_de_bloques) y series.<caso>.respuesta.aciertos
   (generar.py, contra datos/demo/<caso>_verdad.csv). Un modelo sin red no lleva número. Los archivos son simulados. */
(function () {
  'use strict';
  const K = window.K;
  const MODELOS = [['leyes', 'La roca'], ['taludes', 'La pared'], ['flotacion', 'La planta'], ['flota', 'Los camiones'], ['sismicidad', 'Los túneles']];

  K.registrar('confianza', {
    crear: function (L) {
      const d = K.datos;
      L.querySelector('#conf-modelos').innerHTML = MODELOS.map(function (m, i) {
        let a = null;
        if (m[0] === 'leyes') { const C = d.terreno.examen_bloques.colores; a = { decididas: C.actuar.bloques + C.no_actuar.bloques, correctas: C.actuar.sobre_el_limite + C.no_actuar.bloques - C.no_actuar.sobre_el_limite }; }
        else { const R = d.series[m[0]].respuesta; a = R && R.aciertos; }
        if (!a || !a.decididas) return '<div class="fila sin-red"><span class="t3">' + m[1] + '</span><span class="riel"></span><span class="num"></span><span class="p">Su red todavía está entrenando</span></div>';
        const acc = a.correctas / a.decididas;
        return '<div class="fila" style="--d:' + (0.5 + i * 0.18).toFixed(2) + 's"><span class="t3">' + m[1] + '</span><span class="riel"><i style="width:' + (acc * 100).toFixed(1) + '%"></i></span>' +
          '<span class="num">' + K.coma(acc, 2) + '</span><span class="p"><span class="nb">' + K.miles(a.correctas) + ' de ' + K.miles(a.decididas) + '</span> decisiones</span></div>';
      }).join('');
    },
  });
})();
