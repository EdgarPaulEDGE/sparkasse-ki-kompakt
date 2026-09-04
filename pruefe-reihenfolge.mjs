/**
 * Klickt sich durch jede Folie und protokolliert, in welcher Reihenfolge die
 * Einblendungen erscheinen und wo sie auf der Folie liegen. Meldet jeden
 * Sprung entgegen der Leserichtung (nach oben, oder nach links im selben
 * Höhenband). Genau dort wirkt der Aufbau sprunghaft.
 */
import puppeteer from "puppeteer";
const adresse = process.argv[2] || "http://localhost:8150";
const BAND = 90; // ab so vielen Pixeln Höhenunterschied gilt es als neue Zeile

const b = await puppeteer.launch();
const s = await b.newPage();
await s.setViewport({ width: 1920, height: 1080 });
await s.goto(adresse, { waitUntil: "networkidle0" });
await s.evaluate(() => document.fonts.ready);
await s.evaluate(() => Reveal.configure({ transition: "none" }));
await new Promise((r) => setTimeout(r, 1200));

const anzahl = await s.evaluate(() => document.querySelectorAll(".reveal .slides > section").length);
let fehler = 0;

for (let h = 0; h < anzahl; h++) {
  await s.evaluate((h) => Reveal.slide(h, 0), h);
  await new Promise((r) => setTimeout(r, 180));

  const schritte = await s.evaluate(() => {
    const sec = document.querySelector("section.present");
    const bu = sec.querySelector(".slide");
    const bt = bu.getBoundingClientRect();
    const zoom = bt.height / 1080;
    const alle = [...sec.querySelectorAll(".fragment")];
    // Kopf muss ohne Klick da sein
    const kopf = sec.querySelector(".headline, .hero");
    const kopfSichtbar = kopf ? getComputedStyle(kopf).opacity !== "0" : true;
    const sichtbar = () => alle.filter((f) => f.classList.contains("visible"));
    const liste = [];
    let vorher = new Set(sichtbar());
    let schutz = 0;
    while (Reveal.availableFragments().next && schutz++ < 20) {
      Reveal.nextFragment();
      const jetzt = sichtbar();
      for (const f of jetzt) {
        if (vorher.has(f)) continue;
        // reine Grafik ohne Text trägt keine eigene Aussage und wird in der
        // Reihenfolge nicht mitgezählt
        if (!(f.textContent || "").trim()) continue;
        const r = f.getBoundingClientRect();
        liste.push({
          y: Math.round((r.top - bt.top) / zoom),
          x: Math.round((r.left - bt.left) / zoom),
          text: (f.textContent || "").trim().replace(/\s+/g, " ").slice(0, 26),
        });
      }
      vorher = new Set(jetzt);
    }
    return { liste, kopfSichtbar, kopfText: kopf ? kopf.textContent.trim().slice(0, 26) : "" };
  });

  if (!schritte.kopfSichtbar) {
    console.error(`Folie ${h + 1}: Kopfzeile ist beim Blättern noch unsichtbar`);
    fehler++;
  }
  const l = schritte.liste;
  const probleme = [];
  for (let i = 1; i < l.length; i++) {
    const a = l[i - 1], c = l[i];
    const spaltenwechsel = c.x > a.x + 200;
    if (c.y < a.y - BAND && !spaltenwechsel)
      probleme.push(`  ${i}. "${c.text}" springt ${a.y - c.y}px nach OBEN, ohne die Spalte zu wechseln`);
    else if (Math.abs(c.y - a.y) <= BAND && c.x < a.x - 40)
      probleme.push(`  ${i}. "${c.text}" springt ${a.x - c.x}px nach LINKS`);
  }
  const kette = l.map((f) => `${f.text}`).join(" -> ");
  if (probleme.length) {
    fehler += probleme.length;
    console.error(`Folie ${h + 1} (${l.length} Einblendungen): ${kette}`);
    probleme.forEach((p) => console.error(p));
  } else {
    console.log(`Folie ${String(h + 1).padStart(2)}: ${l.length} Einblendungen  ${kette.slice(0, 90)}`);
  }
}
await b.close();
console.log(fehler ? `\n${fehler} Stellen laufen gegen die Leserichtung.` : "\nAlle Einblendungen laufen in Leserichtung.");
