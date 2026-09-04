/**
 * Findet Kästen, die sich gegenseitig überdecken. Der Überlauf-Test prüft nur
 * gegen den Folienrand, der Kanten-Test nur gegen Fluchtlinien: zwei Kästen
 * mitten auf der Folie können sich trotzdem überlappen, ohne dass beide
 * Prüfungen anschlagen. Genau das passiert, wenn ein Element mit width:100%
 * plus Innenabstand ohne border-box breiter wird als sein Platz.
 */
import puppeteer from "puppeteer";
const adresse = process.argv[2] || "http://localhost:8150";
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
  await new Promise((r) => setTimeout(r, 180));
  const funde = await s.evaluate(() => {
    const sec = document.querySelector("section.present");
    const bu = sec.querySelector(".slide");
    const bt = bu.getBoundingClientRect();
    const z = bt.height / 1080;
    const els = [...bu.querySelectorAll(".feld, .fenster, .zettel, .prompt, .posting, .karte-schwach, .karte-gut, .takeaway, .begleiter, .slide > img, .spalte > img, .spalten img")];
    const raus = [];
    for (let i = 0; i < els.length; i++)
      for (let j = i + 1; j < els.length; j++) {
        const A = els[i], B = els[j];
        if (A.contains(B) || B.contains(A)) continue;   // verschachtelt ist erlaubt
        const a = A.getBoundingClientRect(), c = B.getBoundingClientRect();
        const x = Math.min(a.right, c.right) - Math.max(a.left, c.left);
        const y = Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top);
        if (x > 2 && y > 2)
          raus.push(`${Math.round(x / z)}x${Math.round(y / z)}px  "${(A.textContent || "").trim().slice(0, 22)}"  über  "${(B.textContent || "").trim().slice(0, 22)}"`);
      }
    return raus;
  });
  if (funde.length) {
    treffer += funde.length;
    console.log(`Folie ${h + 1}:`);
    funde.forEach((f) => console.log("  " + f));
  }
}
await b.close();
console.log(treffer ? `\n${treffer} Überlappungen.` : "\nKeine Überlappungen.");
