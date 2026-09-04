/**
 * Vollbericht über jedes Bild im Deck: Verzerrung, Beschnitt, Auflösungsreserve.
 * Ergänzt pruefe-verzerrung.mjs um die Zahlen, wenn man alle Bilder auf einmal
 * sehen will. Aufruf: node pruefe-bilder.mjs [adresse]
 */
import puppeteer from "puppeteer";
const b = await puppeteer.launch();
const s = await b.newPage();
await s.setViewport({ width: 1920, height: 1080 });
await s.goto((process.argv[2] || "http://localhost:8080") + "/?nofrag", { waitUntil: "networkidle0" });
await s.evaluate(() => document.fonts.ready);
await s.evaluate(() => Reveal.configure({ transition: "none" }));
await new Promise((r) => setTimeout(r, 1500));
const anzahl = await s.evaluate(() => document.querySelectorAll(".reveal .slides > section").length);
let verzerrt = 0, knapp = 0;
console.log("Folie | Datei                     | Datei-Maße | gezeigt   | Verhältnis | Auflösung");
for (let h = 0; h < anzahl; h++) {
  await s.evaluate((h) => Reveal.slide(h, 0), h);
  await new Promise((r) => setTimeout(r, 150));
  const zeilen = await s.evaluate(() => {
    const sec = document.querySelector("section.present");
    const bu = sec.querySelector(".slide");
    const zoom = bu.getBoundingClientRect().height / 1080;
    return [...sec.querySelectorAll("img")]
      .filter((i) => i.naturalWidth && i.getBoundingClientRect().width > 4)
      .map((i) => {
        const r = i.getBoundingClientRect();
        const bB = r.width / zoom, hB = r.height / zoom;      // in Folienpixeln
        const soll = i.naturalWidth / i.naturalHeight;
        const ist = bB / hB;
        const fit = getComputedStyle(i).objectFit;
        // wie viel Prozent des Bildes schneidet cover weg?
        let beschnitt = 0;
        if (fit === "cover") beschnitt = Math.round((1 - Math.min(soll, ist) / Math.max(soll, ist)) * 100);
        return {
          datei: i.src.split("/").pop(),
          nat: i.naturalWidth + "x" + i.naturalHeight,
          zeigt: Math.round(bB) + "x" + Math.round(hB),
          abw: Math.round((ist / soll - 1) * 100),
          fit, beschnitt,
          // Auflösungsreserve: Datei-Breite gegen dargestellte Folienbreite
          reserve: Math.round((i.naturalWidth / bB) * 100) / 100,
        };
      });
  });
  for (const z of zeilen) {
    const verz = z.fit === "fill" && Math.abs(z.abw) > 2;
    if (verz) verzerrt++;
    if (z.reserve < 1) knapp++;
    const hinweis = verz ? `  VERZERRT ${z.abw > 0 ? "+" : ""}${z.abw}%`
      : z.fit === "cover" && z.beschnitt > 12 ? `  ${z.beschnitt}% beschnitten`
      : z.reserve < 1 ? `  nur ${z.reserve}x Auflösung`
      : "";
    console.log(
      `${String(h + 1).padStart(5)} | ${z.datei.padEnd(25).slice(0, 25)} | ${z.nat.padStart(10)} | ${z.zeigt.padStart(9)} | ${z.fit.padEnd(10)} | ${String(z.reserve).padStart(5)}x${hinweis}`
    );
  }
}
await b.close();
console.log(verzerrt ? `\n${verzerrt} verzerrt.` : "\nKein Bild verzerrt.");
console.log(knapp ? `${knapp} Bilder unter 1x Auflösung.` : "Alle Bilder mit mindestens 1x Auflösung.");
