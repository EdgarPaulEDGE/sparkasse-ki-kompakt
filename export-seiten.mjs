/**
 * Nimmt jede Folie direkt aus dem Browser auf, in anderthalbfacher Aufloesung.
 *
 * decktape faellt hier aus: es fasst nach dem Drucken Bildobjekte zusammen und
 * vergleicht sie dabei nur ueber den Datenstrom, nicht ueber Groesse und
 * Maske. In einem Deck mit vielen aehnlichen dunklen Verlaufsflaechen werden
 * so Kaesten zusammengelegt, die nichts miteinander zu tun haben, und ganze
 * Karten verschwinden (Folien 3, 10, 12, 13, 23, 28, 32 waren betroffen).
 */
import puppeteer from 'puppeteer';
import fs from 'fs';

const adresse = process.argv[2] || 'http://localhost:8171';
const ordner = process.argv[3] || '.pruefung/seiten';
const guete = Number(process.argv[4] || 90);
const schaerfe = Number(process.argv[5] || 1.5);   // 1,5 x = auf Retina bei 100 % pixelgenau

fs.rmSync(ordner, { recursive: true, force: true });
fs.mkdirSync(ordner, { recursive: true });

const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
const seite = await browser.newPage();
await seite.setViewport({ width: 1920, height: 1080, deviceScaleFactor: schaerfe });
await seite.goto(adresse + '/?nofrag', { waitUntil: 'networkidle0' });
await seite.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 2500));

const anzahl = await seite.evaluate(() => document.querySelectorAll('.reveal .slides > section').length);
for (let i = 0; i < anzahl; i++) {
  await seite.evaluate(k => Reveal.slide(k, 0), i);
  await new Promise(r => setTimeout(r, 900));
  await seite.evaluate(() => document.fonts.ready);
  const datei = `${ordner}/s-${String(i + 1).padStart(2, '0')}.jpg`;
  await seite.screenshot({ path: datei, type: 'jpeg', quality: guete });
  process.stdout.write(`\rFolie ${i + 1}/${anzahl}`);
}
console.log('\nfertig');
await browser.close();
