/* 12 · Cierre: mientras se lee el mensaje, las respuestas siguen saliendo.
   El contador es una cuenta, no una medición: los segundos que pasaron desde la primera pulsación del pitch, divididos
   por lo que tarda un análisis con la red (latencia_ms del sello: 10 ms) y con el método lento (M-25: 117 s).
   Los mapas son los mismos de la lámina de la ráfaga: la respuesta de la red para 32 bancos distintos. */
(function () {
  'use strict';
  const K = window.K;
  const COLS = 7, FILAS = 4, PASO = 100, LADO = 90, X0 = 1110, Y0 = 560, CASILLAS = COLS * FILAS;
  const RITMO = 0.12;                                  // segundos entre un mapa nuevo y el siguiente

  K.registrar('cierre', {
    tQuieto: 30,
    crear: function (L) {
      // El QR se dibuja desde config.js: al cambiar la dirección de la demo, cambia solo.
      const demo = K.config.demo || {}, caja = L.querySelector('#qr');
      L.querySelector('#qr-texto').textContent = demo.texto || demo.url || '';
      if (window.qrcode && demo.url) {
        const q = window.qrcode(0, 'M');
        q.addData(demo.url);
        q.make();
        const n = q.getModuleCount();
        let d = '';
        for (let f = 0; f < n; f++) for (let c = 0; c < n; c++) if (q.isDark(f, c)) d += 'M' + c + ' ' + f + 'h1v1h-1z';
        caja.innerHTML = '<svg viewBox="0 0 ' + n + ' ' + n + '" shape-rendering="crispEdges" role="img" aria-label="QR a ' + (demo.texto || demo.url) + '"><path d="' + d + '" fill="#0b0a09"/></svg>';
      }
      this.cv = L.querySelector('canvas');
      this.ctx = this.cv.getContext('2d');
      this.bancos = K.mapasRafaga();
      this.n = L.querySelector('#cierre-n');
      this.lento = L.querySelector('#cierre-lento');
      this.ms = K.datos.sello.latencia_ms;
      this.segLento = K.datos.sello.mcmc_s_por_dataset;
      // en qué casilla cae cada mapa nuevo: primero se llena la muralla, después se renueva al azar
      const azar = K.azar(41), orden = [];
      for (let i = 0; i < CASILLAS; i++) orden.push(i);
      for (let i = CASILLAS - 1; i > 0; i--) { const j = Math.floor(azar() * (i + 1)), x = orden[i]; orden[i] = orden[j]; orden[j] = x; }
      this.casillaDe = function (k) { return k < CASILLAS ? orden[k] : Math.floor(azar() * CASILLAS); };
    },
    alAjustar: function () {
      const r = (this.r = K.razon(1.5));
      this.cv.width = Math.round(1920 * r);
      this.cv.height = Math.round(1080 * r);
    },
    entrar: function () { this.muralla = []; this.hechos = 0; },
    cuadro: function (t) {
      // lo que duró el pitch: desde la primera pulsación (o desde que se abrió el deck)
      const seg = K.estatico ? 180 : (performance.now() - (K.partida || K.cargado || performance.now())) / 1000;
      K.cifra(this.n, K.miles(Math.floor((seg * 1000) / this.ms)));
      this.lento.textContent = Math.floor(seg / this.segLento);

      const ctx = this.ctx, r = this.r, hasta = Math.floor((t - 0.9) / RITMO);
      while (this.hechos <= hasta) {
        const k = this.hechos++;
        this.muralla[this.casillaDe(k)] = { mapa: this.bancos[k % this.bancos.length].mapa, t: 0.9 + k * RITMO };
      }
      ctx.setTransform(r, 0, 0, r, 0, 0);
      ctx.clearRect(0, 0, 1920, 1080);
      for (let i = 0; i < CASILLAS; i++) {
        const x = X0 + (i % COLS) * PASO, y = Y0 + Math.floor(i / COLS) * PASO, c = this.muralla[i];
        if (!c) { ctx.strokeStyle = '#2d2924'; ctx.lineWidth = 1.5; ctx.strokeRect(x, y, LADO, LADO); continue; }
        const edad = t - c.t, k = K.fuera(edad / 0.3), lado = K.mezcla(LADO * 0.5, LADO, k);
        ctx.globalAlpha = K.acotar(edad / 0.12, 0, 1);
        ctx.drawImage(c.mapa, x + (LADO - lado) / 2, y + (LADO - lado) / 2, lado, lado);
        ctx.globalAlpha = 1;
        const brillo = 1 - K.acotar((edad - 0.1) / 0.55, 0, 1);
        if (brillo > 0) { ctx.strokeStyle = 'rgba(255,240,210,' + brillo + ')'; ctx.lineWidth = 3; ctx.strokeRect(x, y, LADO, LADO); }
      }
    },
  });
})();
