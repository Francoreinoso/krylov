// Respaldo estático del deck: una imagen JPG por lámina (su estado final). Con ellas se arma el PDF.
// Abre index.html por file://, sin internet, en modo ?estatico (sin movimiento, semilla fija).
//
//   npm install --no-save playwright-core            (no se versiona)
//   CHROMIUM=/ruta/a/Chromium node pitch/deck/respaldo/capturar.mjs
//
// CHROMIUM es el ejecutable de cualquier Chrome o Chromium instalado. El PDF se arma después con las imágenes
// (README.md de la carpeta del deck).
import { chromium } from 'playwright-core';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const aqui = dirname(fileURLToPath(import.meta.url));
const deck = pathToFileURL(join(aqui, '..', 'index.html')).href;
const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'],
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errores = [];
page.on('pageerror', (e) => errores.push(e.message));
page.on('console', (m) => { if (m.type() === 'error') errores.push(m.text()); });
page.on('requestfailed', (r) => errores.push('no cargó: ' + r.url()));
const laminas = await page.goto(deck + '?estatico#1').then(() => page.evaluate(() => K.laminas.length));
for (let i = 1; i <= laminas; i++) {
  await page.goto('about:blank');
  await page.goto(deck + '?estatico#' + i + '.9');          // .9: el último paso de la lámina
  await page.waitForTimeout(900);
  const nombre = String(i).padStart(2, '0') + '.jpg';
  await page.screenshot({ path: join(aqui, nombre), type: 'jpeg', quality: 90 });
  console.log(nombre);
}
await browser.close();
if (errores.length) { console.error('Errores de consola:\n' + [...new Set(errores)].join('\n')); process.exit(1); }
