import puppeteer from "puppeteer";
const ZIEL = process.argv[2];
const b = await puppeteer.launch({ protocolTimeout: 180000 });
const s = await b.newPage();
// zweifache Auflösung: 3840x2160 je Seite, damit der Text auch beim Zoomen trägt
await s.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
await s.goto("http://localhost:8150/?nofrag&v=" + Date.now(), { waitUntil: "networkidle0" });
await new Promise((r) => setTimeout(r, 2500));
const anz = await s.evaluate(() => Reveal.getTotalSlides());
for (let i = 0; i < anz; i++) {
  await s.evaluate((n) => Reveal.slide(n), i);
  await new Promise((r) => setTimeout(r, 700));
  await s.screenshot({ path: `${ZIEL}/s-${String(i + 1).padStart(2, "0")}.png` });
}
console.log("Seiten fotografiert:", anz);
await b.close();
/* Aufruf: node export-pdf.mjs <zielordner>
   Danach die PNGs mit Pillow zu einem PDF binden (Qualität 88 landete bei
   9,2 MB für 23 Seiten). decktape scheidet hier aus: es rendert über
   page.pdf() im Print-Medium, dort kollabiert Reveals Bühne und die Kästen
   schneiden ihren Text ab. */
