/**
 * Sucht Kanten, die fast, aber nicht ganz fluchten. Genau das liest das Auge
 * als "sitzt nicht". Geprüft werden alle sichtbaren Blöcke einer Folie:
 *  - Blöcke nebeneinander (gleiches Höhenband): fluchten Ober- und Unterkante?
 *  - Blöcke untereinander: fluchten linke und rechte Kante?
 * Gemeldet wird nur der Graubereich 1 bis 24 Pixel. Alles darunter ist
 * Rundung, alles darüber ist erkennbar Absicht.
 */
import puppeteer from "puppeteer";
const adresse = process.argv[2] || "http://localhost:8150";
const MIN = 1, MAX = 24;
const b = await puppeteer.launch();
const s = await b.newPage();
await s.setViewport({ width: 1920, height: 1080 });
await s.goto(`${adresse}/?nofrag`, { waitUntil: "networkidle0" });
await s.evaluate(() => document.fonts.ready);
await s.evaluate(() => Reveal.configure({ transition: "none" }));
await new Promise((r) => setTimeout(r, 1500));

const anzahl = await s.evaluate(() => document.querySelectorAll(".reveal .slides > section").length);
let treffer = 0;
for (let h = 0; h < anzahl; h++) {
  await s.evaluate((h) => Reveal.slide(h, 0), h);
  await new Promise((r) => setTimeout(r, 200));
  const funde = await s.evaluate((MIN, MAX) => {
    const sec = document.querySelector("section.present");
    const bu = sec.querySelector(".slide");
    const bt = bu.getBoundingClientRect();
    const z = bt.height / 1080;
    const bloecke = [...bu.querySelectorAll(".feld, .fenster, .zettel, .prompt, .posting, .metrik, .takeaway")]
      .map((el) => {
        const r = el.getBoundingClientRect();
        return {
          o: (r.top - bt.top) / z, u: (r.bottom - bt.top) / z,
          l: (r.left - bt.left) / z, re: (r.right - bt.left) / z,
          was: (el.className.split(" ")[0] || "block") + ': "' +
               (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 20) + '"',
        };
      })
      .filter((x) => x.u - x.o > 30 && x.re - x.l > 60);
    const raus = [];
    for (let i = 0; i < bloecke.length; i++)
      for (let j = i + 1; j < bloecke.length; j++) {
        const a = bloecke[i], c = bloecke[j];
        const nebeneinander = a.o < c.u - 40 && c.o < a.u - 40;
        const untereinander = a.l < c.re - 40 && c.l < a.re - 40;
        const pruef = (v1, v2, kante, gilt) => {
          const d = Math.abs(v1 - v2);
          if (gilt && d >= MIN && d <= MAX) raus.push(`${kante} ${d.toFixed(0)}px  ${a.was}  gegen  ${c.was}`);
        };
        pruef(a.o, c.o, "Oberkante", nebeneinander);
        pruef(a.u, c.u, "Unterkante", nebeneinander);
        pruef(a.l, c.l, "linke Kante", untereinander);
        pruef(a.re, c.re, "rechte Kante", untereinander);
      }
    return raus;
  }, MIN, MAX);
  if (funde.length) {
    treffer += funde.length;
    console.log(`\nFolie ${h + 1}`);
    [...new Set(funde)].forEach((f) => console.log("  " + f));
  }
}
await b.close();
console.log(treffer ? `\n${treffer} Kanten im Graubereich.` : "\nAlle Kanten fluchten oder stehen bewusst versetzt.");
