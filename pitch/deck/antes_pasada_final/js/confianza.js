/* 13 · «¿Y cómo sé que acierta?»: cuando Krylov da un rango de 90%, ¿la respuesta real cae adentro 9 de cada 10 veces?
   Una fila por modelo: en los 2.000 datasets simulados nuevos de su validación, la fracción de veces que el valor
   verdadero cayó dentro del rango de 90% que dio la red (cobertura_90 de cada sello). Lo correcto es 90%: la línea blanca.
   Sale de datos.js: sello (la roca) y series.<caso>.respuesta.sello (los otros cuatro). El yacimiento va con la cifra de
   su mapa (M-63, en config.js, porque su archivo de datos solo se carga en su lámina). Abajo, el examen con datos reales
   públicos del motor de la roca (sello.examen_5_particiones). No se calcula nada aquí. */
(function () {
  'use strict';
  const K = window.K;
  const MODELOS = [['leyes', 'La roca'], ['taludes', 'La pared'], ['flotacion', 'La planta'], ['flota', 'Los camiones'], ['sismicidad', 'Los túneles']];
  const MIN = 0.8, MAX = 1.0, META = 0.9;
  const pc = function (v) { return (((v - MIN) / (MAX - MIN)) * 100).toFixed(2) + '%'; };

  K.registrar('confianza', {
    crear: function (L) {
      const d = K.datos, filas = MODELOS.map(function (m) { return [m[1], (m[0] === 'leyes' ? d.sello : d.series[m[0]].respuesta.sello).cobertura_90]; });
      const yac = K.config.cifras && K.config.cifras.yacimiento_cobertura_90;
      if (yac) filas.push(['El yacimiento', yac]);
      L.querySelector('#conf-modelos').innerHTML =
        '<div class="escala"><span></span><span class="riel"><i class="izq">80%</i><b style="left:' + pc(META) + '">Lo que promete: 90%</b><i class="der">100%</i></span><span></span></div>' +
        filas.map(function (f, i) {
          return '<div class="fila" style="--d:' + (0.35 + i * 0.12).toFixed(2) + 's; --x:' + pc(f[1]) + '; --meta:' + pc(META) + '"><span class="t3">' + f[0] + '</span>' +
            '<span class="riel"><i class="punto"></i></span><span class="num">' + K.coma(f[1] * 100, 1) + '%</span></div>';
        }).join('');
      const E = d.sello.examen_5_particiones, real = L.querySelector('#conf-real');
      if (E && real) real.innerHTML = 'Y con datos reales públicos: de ' + E.mediciones_escondidas + ' mediciones que le escondimos, <b>' + E.dentro_del_rango_de_90 + ' cayeron dentro de su rango</b>.';
    },
  });
})();
