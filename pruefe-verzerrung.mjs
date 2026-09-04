/**
 * Findet Bilder, die verzerrt dargestellt werden: dargestelltes Seitenverhältnis
 * gegen das natürliche der Datei. Das passiert lautlos, sobald ein Bild mit
 * fester Höhe in einer Flexbox landet, die es auf ihre Breite streckt, und
 * fällt beim Draufsehen erst auf, wenn man das Motiv kennt.
 * Aufruf: node pruefe-verzerrung.mjs [adresse]
 */
import puppeteer from "puppeteer";
const adresse = process.argv[2] || "http://localhost:8080";
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
  await new Promise((r) => setTimeout(r, 160));
  const funde = await s.evaluate(() =>
    [...document.querySelectorAll("section.present img")]
      .filter((i) => i.naturalWidth && i.getBoundingClientRect().width > 4)
      .map((i) => {
        const r = i.getBoundingClientRect();
        const soll = i.naturalWidth / i.naturalHeight;
        const ist = r.width / r.height;
        const fit = getComputedStyle(i).objectFit;
        return { datei: i.src.split("/").pop(), abw: Math.round((ist / soll - 1) * 100), fit };
      })
      // object-fit cover/contain schneidet bewusst zu, das ist keine Verzerrung
      .filter((x) => Math.abs(x.abw) > 4 && x.fit === "fill")
  );
  for (const f of funde) {
    treffer++;
    console.error(`  Folie ${h + 1}: ${f.datei} ist ${f.abw > 0 ? "" : ""}${f.abw}% ${f.abw > 0 ? "zu breit" : "zu schmal"} gezogen`);
  }
}
await b.close();
console.log(treffer ? `\n${treffer} verzerrte Bilder.` : "\nKein Bild verzerrt.");
if (treffer) process.exit(1);
