/* Krylov · deck. Lámina 12: el sexto modelo, `yacimiento`, un yacimiento en 3D leído desde perforaciones.
   La escena vive en su propia página (yacimiento.html) y aquí se muestra dentro de un marco. El deck le manda el paso y la
   página le devuelve las teclas que recibe cuando tiene el foco, así que las flechas funcionan igual que en las demás láminas.
   El marco se carga al entrar y se suelta al salir: su 3D no gasta nada mientras se muestra otra lámina. */
(function () {
  'use strict';
  let marco = null, cargado = false, lista = false, quiero = 0, soltar = null;
  const direccion = function () { return 'yacimiento.html' + (K.quieto ? '?quieto' : '') + '#' + quiero; };

  function mandar() { if (lista && marco.contentWindow) marco.contentWindow.postMessage({ krylov: 1, paso: quiero }, '*'); }

  window.addEventListener('message', function (ev) {
    if (!marco || ev.source !== marco.contentWindow || !ev.data || ev.data.krylov !== 1) return;
    if (ev.data.lista) { lista = true; mandar(); }
    else if (typeof ev.data.tecla === 'string') window.dispatchEvent(new KeyboardEvent('keydown', { key: ev.data.tecla }));
  });

  K.registrar('yacimiento', {
    crear: function (L) { marco = L.querySelector('iframe'); },
    entrar: function () {
      clearTimeout(soltar);
      if (cargado) return;                                         // se volvió antes de soltarlo: sigue cargado
      cargado = true; lista = false;
      marco.src = direccion();
    },
    paso: function (p) {
      quiero = p;
      if (!lista) marco.src = direccion();                         // todavía cargando: parte en ese paso
      else mandar();
    },
    salir: function () {
      clearTimeout(soltar);
      soltar = setTimeout(function () { cargado = lista = false; marco.src = 'about:blank'; window.focus(); }, 600);   // después del fundido de salida
    },
  });
})();
