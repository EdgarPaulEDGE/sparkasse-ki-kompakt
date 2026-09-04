/**
 * Misst jede Folie im Browser, meldet Überlauf und legt von jeder Folie
 * ein PNG ab. Reveal schneidet zu hohe Folien kommentarlos ab: kein Fehler,
 * keine Scrollleiste, der Inhalt ist einfach weg.
 *
 * Gemessen wird genau in Foliengröße (1920x1080) und immer auf der aktiven
 * Folie, nie an einer von Hand sichtbar geschalteten: Reveal positioniert
 * beides unterschiedlich.
 *
 * Aufruf: node pruefe-folien.mjs [adresse] [bildordner]
 */
import puppeteer from "puppeteer";
import { mkdirSync } from "node:fs";

const adresse = process.argv[2] || "http://localhost:8150";
const bildordner = process.argv[3];
const HOEHE = 1080;

if (bildordner) mkdirSync(bildordner, { recursive: true });

const browser = await puppeteer.launch();
const seite = await browser.newPage();
await seite.setViewport({ width: 1920, height: 1080 });
await seite.goto(`${adresse}/?nofrag`, { waitUntil: "networkidle0" });
await seite.evaluate(() => document.fonts.ready);
// Ohne Überblendung messen: sonst liegt beim Auslösen des Bildes noch die
// halb ausgeblendete Vorgängerfolie darüber und verfälscht die Sicht.
await seite.evaluate(() => Reveal.configure({ transition: "none", backgroundTransition: "none" }));
await new Promise((r) => setTimeout(r, 1800));

const anzahl = await seite.evaluate(
  () => document.querySelectorAll(".reveal .slides > section").length
);

const ueberlauf = [];
const leer = [];

for (let h = 0; h < anzahl; h++) {
  await seite.evaluate((h) => Reveal.slide(h, 0), h);
  await new Promise((r) => setTimeout(r, 300));

  const fund = await seite.evaluate((HOEHE) => {
    const s = document.querySelector("section.present");
    const buehne = s && s.querySelector(".slide");
    if (!buehne) return null;

    const kopf = (s.querySelector("h1, h2") || {}).textContent || "";
    const bt = buehne.getBoundingClientRect();
    const zoom = bt.height / HOEHE;
    const ergebnis = { kopf: kopf.trim().replace(/\s+/g, " ").slice(0, 40), raus: null, tot: [] };

    buehne.querySelectorAll("*").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.height < 1) return;
      const o = (r.top - bt.top) / zoom;
      const u = (r.bottom - bt.top) / zoom;
      const raus = Math.max(u - HOEHE, -o);
      if (raus > 0.5 && (!ergebnis.raus || raus > ergebnis.raus.px)) {
        ergebnis.raus = {
          px: Math.round(raus),
          wo: o < 0 ? "oben" : "unten",
          text: (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 46),
        };
      }
      // seitlich
      const l = (r.left - bt.left) / zoom;
      const re = (r.right - bt.left) / zoom;
      if ((re > 1920.5 || l < -0.5) && !ergebnis.raus) {
        ergebnis.raus = {
          px: Math.round(Math.max(re - 1920, -l)),
          wo: l < 0 ? "linken" : "rechten",
          text: (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 46),
        };
      }
    });

    s.querySelectorAll(".fragment").forEach((f) => {
      const r = f.getBoundingClientRect();
      if ((r.top - bt.top) / zoom > HOEHE - 20) {
        ergebnis.tot.push((f.textContent || "").trim().replace(/\s+/g, " ").slice(0, 50));
      }
    });
    return ergebnis;
  }, HOEHE);

  if (bildordner) {
    await seite.screenshot({
      path: `${bildordner}/folie-${String(h + 1).padStart(2, "0")}.png`,
    });
  }

  if (!fund) continue;
  if (fund.raus) ueberlauf.push({ nr: h + 1, kopf: fund.kopf, ...fund.raus });
  fund.tot.forEach((t) => leer.push({ nr: h + 1, text: t }));
}

await browser.close();

console.log(`Geprüft: ${anzahl} Folien`);
if (leer.length) {
  console.error("\nEINBLENDUNGEN UNTERHALB DES RANDS:");
  leer.forEach((f) => console.error(`  Folie ${f.nr}: "${f.text}"`));
}
if (ueberlauf.length) {
  console.error("\nINHALT AUSSERHALB DER FOLIE:");
  ueberlauf.forEach((f) =>
    console.error(`  Folie ${f.nr} (${f.kopf}): ${f.px}px über den ${f.wo} Rand  "${f.text}"`)
  );
}
if (leer.length || ueberlauf.length) process.exit(1);
console.log("Sauber: kein Überlauf, keine tote Einblendung.");
