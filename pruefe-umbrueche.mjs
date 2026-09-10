/** Wo bricht eine Headline mitten im Satz statt an der Satzgrenze? */
import puppeteer from "puppeteer";
const b = await puppeteer.launch();
const s = await b.newPage();
await s.setViewport({ width: 1920, height: 1080 });
await s.goto("http://localhost:8171/?nofrag", { waitUntil: "networkidle0" });
await s.evaluate(() => document.fonts.ready);
await s.evaluate(() => Reveal.configure({ transition: "none" }));
await new Promise((r) => setTimeout(r, 1200));
const n = await s.evaluate(() => document.querySelectorAll(".reveal .slides > section").length);
for (let h = 0; h < n; h++) {
  await s.evaluate((i) => Reveal.slide(i, 0), h);
  await new Promise((r) => setTimeout(r, 150));
  const f = await s.evaluate(() => {
    const el = document.querySelector("section.present .headline, section.present .hero");
    if (!el) return null;
    // Zeilen über die Rechtecke der Textknoten rekonstruieren
    const zeilen = [];
    const lauf = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = lauf.nextNode())) {
      const worte = node.textContent.split(/(\s+)/);
      let off = 0;
      for (const w of worte) {
        if (w.trim()) {
          const r = document.createRange();
          r.setStart(node, off); r.setEnd(node, off + w.length);
          const box = r.getClientRects()[0];
          if (box) {
            const zeile = zeilen.find((z) => Math.abs(z.y - box.top) < 8);
            if (zeile) zeile.worte.push(w);
            else zeilen.push({ y: box.top, worte: [w] });
          }
        }
        off += w.length;
      }
    }
    zeilen.sort((a, c) => a.y - c.y);
    return zeilen.map((z) => z.worte.join(" "));
  });
  if (f && f.length > 1) {
    // Warnung, wenn eine Zeile nicht auf Satzzeichen endet, obwohl später eines kommt
    const problem = f.slice(0, -1).some((z, i) => !/[.!?:,]$/.test(z) && /[.!?]/.test(f.slice(i + 1).join(" ")));
    console.log(`${String(h + 1).padStart(2)} ${problem ? "<<<" : "   "} ${f.join("  /  ")}`);
  }
}

// Zweiter Durchgang: Textblöcke, deren letzte Zeile als einzelnes Wort hängt.
// Genau so stand auf Folie 10 das Wort „schickt." allein unter seinem Satz.
console.log("\n--- haengende Einzelwoerter ---");
let haenger = 0;
for (let h = 0; h < n; h++) {
  await s.evaluate((i) => Reveal.slide(i, 0), h);
  await new Promise((r) => setTimeout(r, 150));
  const funde = await s.evaluate(() => {
    const raus = [];
    const bloecke = document.querySelectorAll("section.present .feld p, section.present .fenster p, section.present .prompt span, section.present .station p");
    for (const el of bloecke) {
      const kasten = el.getBoundingClientRect().width;
      for (const knoten of el.childNodes) {
        if (knoten.nodeType !== 3 || !knoten.textContent.trim()) continue;
        const r = document.createRange();
        r.selectNodeContents(knoten);
        const rects = [...r.getClientRects()];
        if (rects.length < 2) continue;
        const letzte = rects[rects.length - 1];
        const worte = knoten.textContent.trim().split(/\s+/);
        // letzte Zeile schmaler als ein Viertel des Kastens: da haengt ein Rest
        if (letzte.width < kasten * 0.25) {
          raus.push({ text: knoten.textContent.trim().slice(0, 60), zeilen: rects.length,
                      rest: Math.round(letzte.width), kasten: Math.round(kasten), worte: worte.length });
        }
      }
    }
    return raus;
  });
  for (const f of funde) {
    haenger++;
    console.log(`${String(h + 1).padStart(2)} <<< "${f.text}" bricht auf ${f.zeilen} Zeilen, die letzte ist nur ${f.rest} von ${f.kasten} Pixeln breit`);
  }
}
console.log(haenger === 0 ? "Kein Textblock endet mit einem haengenden Rest." : `${haenger} haengende Zeile(n).`);

await b.close();
