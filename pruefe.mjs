/* ============================================================================
   Bauprüfung für das Deck.
   Eine statische Präsentation hat nichts zu kompilieren, aber sie kann sehr
   wohl kaputt sein: ein Bild, das nicht existiert, fällt im Browser stumm aus
   und man merkt es erst vor Publikum. Dieses Skript liest index.html, sammelt
   alle lokalen Verweise und prüft, ob die Dateien wirklich da sind.
   ========================================================================== */
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const wurzel = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(wurzel, "index.html"), "utf8");

/* src="…" und href="…" einsammeln, aber nur Verweise auf eigene Dateien:
   alles mit Protokoll, Anker oder data-URI überspringen. */
const verweise = new Set();
for (const treffer of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
  const ziel = treffer[1];
  if (/^(https?:|data:|#|mailto:)/.test(ziel)) continue;
  verweise.add(ziel.split("?")[0]);
}

/* Auch die aus dem Stylesheet geladenen Schriften prüfen */
for (const treffer of html.matchAll(/url\("([^"]+)"\)/g)) {
  const ziel = treffer[1];
  if (!/^(https?:|data:)/.test(ziel)) verweise.add(ziel.split("?")[0]);
}

const fehlend = [...verweise].filter((v) => !existsSync(resolve(wurzel, v)));

if (fehlend.length) {
  console.error(`Fehlende Dateien (${fehlend.length}):`);
  for (const f of fehlend) console.error(`  ${f}`);
  process.exit(1);
}

const folien = (html.match(/<section[\s>]/g) || []).length;
console.log(`Deck in Ordnung: ${folien} Folien, ${verweise.size} Verweise, alle Dateien vorhanden.`);
