/**
 * Sucht Kasten im Kasten: ein umrandeter Block (.feld, .fenster, .prompt),
 * der in einem anderen umrandeten Block steckt. Edgars Regel: eine Aussage,
 * eine Umrandung. Bricht mit Code 1 ab, wenn etwas verschachtelt ist.
 */
import puppeteer from 'puppeteer';

const adresse = process.argv[2] || 'http://localhost:8171';
const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
const seite = await browser.newPage();
await seite.setViewport({ width: 1920, height: 1080 });
await seite.goto(adresse + '/?nofrag', { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1500));

const funde = await seite.evaluate(() => {
  const raus = [];
  document.querySelectorAll('section').forEach((s, i) => {
    s.querySelectorAll('.feld, .fenster, .prompt').forEach(el => {
      const aussen = el.parentElement.closest('.feld, .fenster, .prompt');
      if (aussen && s.contains(aussen)) {
        const h = s.querySelector('h2');
        raus.push({ folie: i + 1, titel: h ? h.textContent.trim() : '(ohne Headline)',
                    innen: el.className, aussen: aussen.className });
      }
    });
  });
  return raus;
});
await browser.close();

if (funde.length === 0) {
  console.log('Kaesten: kein Kasten im Kasten.');
} else {
  for (const f of funde) console.log(`Folie ${f.folie} (${f.titel}): "${f.innen}" steckt in "${f.aussen}"`);
  console.log(`\n${funde.length} Verschachtelung(en). Die aeussere Umrandung gehoert weg.`);
  process.exit(1);
}
