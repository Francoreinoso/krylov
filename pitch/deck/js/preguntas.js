/* Las láminas de preguntas (fuera del recorrido; cada una se abre con su tecla): lo que preguntaría quien dirige una
   empresa. Aquí solo se llenan sus tablas con datos de datos.js (y una cifra de config.js, M-44); ninguna está escrita a mano.
   - A · ¿Qué archivo recibe?: las primeras filas reales de dos archivos de demo y el papel de cada columna (casos/<caso>.yaml).
   - L · ¿Y si le subo el archivo a un LLM?: la prueba de pitch/deck/datos/prueba_llm/ (ver su LEEME.md).
   - M · ¿Y si falla en producción?: el semáforo, el examen y el sello, con lo que de verdad responde la API. */
(function () {
  'use strict';
  const K = window.K;
  const PAPEL = { x: 'dónde, a lo ancho', y: 'dónde, a lo largo', valor: 'lo que se midió', unidad: 'qué equipo', tiempo: 'cuándo' };

  K.registrar('archivo', {
    crear: function (L) {
      const A = K.datos.archivos, P = K.datos.practica;
      const tabla = function (a) {
        let h = '<table><thead><tr>' + a.cabecera.map(function (c) { return '<th class="' + (a.papeles[c] ? 'usa' : 'no') + '">' + (a.papeles[c] ? '<i>' + PAPEL[a.papeles[c]] + '</i>' : '<i>no se usa</i>') + c + '</th>'; }).join('') + '</tr></thead><tbody>';
        a.filas.forEach(function (f) { h += '<tr>' + f.map(function (v, i) { return '<td class="' + (a.papeles[a.cabecera[i]] ? 'usa' : 'no') + '">' + v.replace('.', ',') + '</td>'; }).join('') + '</tr>'; });
        return h + '<tr><td class="mas" colspan="' + a.cabecera.length + '">… ' + K.miles(a.n) + ' filas en total</td></tr></tbody></table>';
      };
      L.querySelector('#archivo-mapa').innerHTML = tabla(A.mapa);
      L.querySelector('#archivo-series').innerHTML = tabla(A.series);
      L.querySelector('#archivo-rango').textContent = 'entre ' + P.minimo + ' y ' + P.maximo + ' muestras';
    },
  });

  K.registrar('llm', {
    crear: function (L) {
      const R = K.datos.prueba_llm, S = K.datos.sello, D = K.datos.donde;
      if (!R) return;
      const lento = Math.min(R.llm_a.segundos, R.llm_b.segundos), veces = Math.floor((lento / (S.latencia_ms / 1000)) / 1000) * 1000;
      const horas = Math.round((D.analisis_rehechos * lento) / 3600);
      const poner = function (id, v) { L.querySelector(id).textContent = v; };
      poner('#llm-veces', K.miles(veces) + ' veces');
      poner('#llm-k-rango', R.krylov.dentro + ' de ' + R.krylov.n); poner('#llm-a-rango', R.llm_a.dentro + ' de ' + R.llm_a.n); poner('#llm-b-rango', R.llm_b.dentro + ' de ' + R.llm_b.n);
      poner('#llm-k-seg', S.latencia_ms + ' milisegundos'); poner('#llm-a-seg', R.llm_a.segundos + ' segundos'); poner('#llm-b-seg', R.llm_b.segundos + ' segundos');
      poner('#llm-k-donde', K.coma(K.config.cifras.donde_perforo_s, 1) + ' segundos'); poner('#llm-a-donde', 'unas ' + horas + ' horas');
      poner('#llm-difiere', 'hasta ' + R.entre_corridas.diferencia_maxima_ppm + ' ppm');
      poner('#llm-analisis', D.analisis_rehechos);
    },
  });

  K.registrar('produccion', {
    crear: function (L) {
      const d = K.datos, E = d.examen_puntos, C = d.sello.criterios, total = Object.keys(C).length, pasan = Object.keys(C).filter(function (k) { return C[k]; }).length;
      L.querySelector('#prod-motivo').textContent = '«' + d.pocos.semaforo.motivo + '»';
      L.querySelector('#prod-examen').textContent = E.dentro + ' de ' + E.n;
      L.querySelector('#prod-sello').textContent = pasan + ' de ' + total;
    },
  });
})();
