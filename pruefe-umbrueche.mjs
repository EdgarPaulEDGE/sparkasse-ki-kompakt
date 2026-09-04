/** Wo bricht eine Headline mitten im Satz statt an der Satzgrenze? */
import puppeteer from "puppeteer";
const b = await puppeteer.launch();
const s = await b.newPage();
await s.setViewport({ width: 1920, height: 1080 });
await s.goto("http://localhost:8150/?nofrag", { waitUntil: "networkidle0" });
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
await b.close();
