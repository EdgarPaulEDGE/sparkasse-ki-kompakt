#!/usr/bin/env python3
"""Setzt index.html aus dem K64-Stamm und den eigenen Folien zusammen.

Kopf, Stylesheet und Skript kommen unverändert aus cbl-aufgeweckt (80/20-Stamm),
nur Titel, Logos, Zusatzstil und der Folienblock sind neu. Aufruf: python3 bau.py
"""
import pathlib
HIER = pathlib.Path(__file__).parent
STAMM = HIER.parent / "cbl-aufgeweckt" / "index.html"
html = STAMM.read_text(encoding="utf-8")
folien = (HIER / "folien.html").read_text(encoding="utf-8")

html = html.replace("<title>Aufgeweckt. KI-Klartext zum Frühstück | EDGE Digital x LTM</title>",
                    "<title>KI-Kompakt. Der S-KIPilot im Arbeitsalltag | EDGE Digital x Sparkasse zu Lübeck</title>")
html = html.replace("""   AUFGEWECKT. KI-KLARTEXT ZUM FRÜHSTÜCK
   Netzwerkfrühstück der LTM im K64, Lübeck, 20.08.2026""",
"""   KI-KOMPAKT. DER S-KIPILOT IM ARBEITSALLTAG
   Workshop für die Sparkasse zu Lübeck, online, 10.09.2026
   Stamm: das K64-Deck (cbl-aufgeweckt), nur Folien, Bilder und Zusatzstil sind neu.""")
# Kundenlogo rechts oben
html = html.replace('<img src="assets/logos/convention-bureau.png" alt="Convention Bureau Lübeck">',
                    '<img src="assets/logos/sparkasse-weiss.svg" alt="Sparkasse zu Lübeck">')
html = html.replace('content="#030309">\n<link rel="icon"', 'content="#030309">\n<meta name="description" content="KI-Kompakt Workshop, Sparkasse zu Lübeck, 10. September 2026">\n<link rel="icon"')

zusatz = """
/* ---------- Gastfarbe: Sparkassen-Rot ---------- */
:root { --rot: #FF0000; --gold: #FFC531; }
.rot { color: var(--rot); }
.chrome-client img { height: calc(48px * var(--folie-skala, 1)); opacity: 1; }

/* ---------- Titel: beide Logos unten links ---------- */
.titel-logos { position: absolute; left: 130px; bottom: 96px; display: flex; align-items: center; gap: 34px; }
.titel-logos img { height: 54px; display: block; }
.titel-logos img.sparkasse { height: 64px; }
.titel-x { font-size: 36px; color: var(--w-45); font-weight: 500; }
.slide.rechts { align-items: flex-end; text-align: right; }
.slide.rechts .titel-logos { left: auto; right: 130px; }
.slide.rechts .bild-quelle { left: auto; right: 130px; }
.reveal .slide-background[data-schleier="seite-rechts"]::after {
  background:
    linear-gradient(270deg, rgba(3, 3, 9, .97) 0%, rgba(3, 3, 9, .88) 38%, rgba(3, 3, 9, .35) 78%, rgba(3, 3, 9, .55) 100%),
    linear-gradient(0deg, rgba(3, 3, 9, .7) 0%, transparent 45%);
}

/* ---------- Sechs Bausteine der RAKETE ----------
   Jeder Buchstabe hat seine Farbe, damit die Runde ihn später auf der
   Reparatur-Folie und in den Fall-PDFs wiedererkennt. */
.b-ergebnis { color: var(--ok); }
.b-ton { color: var(--gold); }
.b-grenze { color: var(--rot); }
.rakete { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0 60px; width: 100%; }
.rakete > div { display: grid; grid-template-columns: 96px 1fr; column-gap: 26px; padding: 30px 6px; border-bottom: 1px solid var(--hairline); align-items: start; }
.rakete > div:nth-child(-n+3) { border-top: 1px solid var(--hairline); }
.rakete .buchstabe { font-size: 92px; font-weight: 700; line-height: .9; letter-spacing: -.03em; }
.rakete b { display: block; font-size: 34px; font-weight: 700; margin-bottom: 8px; }
.rakete span { display: block; font-size: 25px; line-height: 1.45; color: var(--w-70); }

/* ---------- Drei Antworten, Frage klein, Antwort groß ---------- */
.antwort { padding: 36px 6px; }
.antwort .label { display: block; margin-bottom: 12px; }
.antwort p { font-size: 42px; font-weight: 600; line-height: 1.3; margin: 0; }

/* ---------- Schutzstufen S1 bis S4 ---------- */
.stufe { font-size: 74px; font-weight: 700; letter-spacing: -.03em; line-height: 1; margin-bottom: 14px; }
.stufe-wohin { display: inline-block; margin-top: 18px; padding: 10px 18px; border-radius: 999px;
  font-size: 21px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
  border: 1px solid var(--hairline-stark); color: var(--weiss); }
.stufe-wohin.beide { border-color: rgba(58, 210, 159, .5); color: var(--ok); }

/* ---------- Die drei Fälle in ihren Farben ---------- */
.ring.rot::before { background: conic-gradient(#ff8a8a, var(--rot) 45%, #b30000 75%, #ff8a8a); }
.ring.blau::before { background: conic-gradient(#8fd4ff, var(--blau) 45%, #005f94 75%, #8fd4ff); }
.ring.gruen::before { background: conic-gradient(#8fe9c9, var(--ok) 45%, #1e8f68 75%, #8fe9c9); }
.fall-a { border-color: rgba(255, 0, 0, .35); }
.fall-b { border-color: rgba(0, 159, 244, .45); }
.fall-c { border-color: rgba(58, 210, 159, .45); }

/* ---------- Zeitstrahl mit zwei Reihen à fünf ---------- */
.strahl.zwei .strahl-reihe + .strahl-reihe { margin-top: 44px; }
.strahl.zwei .strahl-linie { display: none; }
.strahl.zwei .strahl-reihe { position: relative; }
.strahl.zwei .strahl-reihe::before { content: ""; position: absolute; left: 0; right: 0; top: 76px; height: 2px;
  background: linear-gradient(90deg, rgba(244,246,255,.18), var(--blau) 55%, var(--cyan)); }
.strahl.zwei .strahl-jahr { margin-bottom: 14px; }
.strahl.zwei .strahl-knoten { margin-bottom: 22px; }
.strahl.zwei .strahl-text { font-size: 24px; }

/* ---------- Zwei Zahlen nebeneinander (Tempo) ---------- */
.tempo { display: grid; grid-template-columns: 1fr 1fr; width: 100%; }
.tempo > div { padding: 40px 60px; text-align: center; }
.tempo > div + div { border-left: 1px solid var(--hairline); }
.tempo .zahl { font-size: 260px; font-weight: 700; line-height: 1; letter-spacing: -.04em; }
.tempo .einheit { font-size: 40px; font-weight: 600; margin-top: 10px; }
.tempo .was { font-size: 26px; color: var(--w-45); margin-top: 18px; }

/* ---------- Vier Prompt-Typen ---------- */
.typen { display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; width: 100%; }
.typen > div { text-align: center; display: flex; flex-direction: column; align-items: center; }
.typen img { height: 300px; width: auto; display: block; margin-bottom: 18px; }
.typen h3 { font-size: 36px; font-weight: 700; margin: 0 0 12px; }
.typen .prompt.klein { font-size: 23px; text-align: left; width: 100%; }
.typen .plus, .typen .minus { font-size: 23px; line-height: 1.5; margin: 14px 0 0; text-align: left; width: 100%; }
.typen .plus { color: var(--ok); }
.typen .minus { color: var(--warn); }

/* ---------- Slido-Kennung am Folienrand ---------- */
.slido { position: absolute; right: 130px; top: 132px; display: flex; align-items: center; gap: 18px; }
.slido img { width: 120px; height: 120px; border-radius: 12px; display: block; background: #fff; }
.slido span { font-size: 20px; letter-spacing: .12em; text-transform: uppercase; font-weight: 600; color: var(--w-45); text-align: right; line-height: 1.5; }

/* ---------- Füllgrad: Inhalt trägt die Fläche, keine Luft um kleine Gruppen ---------- */
.spalten h3 { font-size: 42px; }
.spalten p { font-size: 30px; line-height: 1.5; }
.spalten .sp-icon svg { width: 88px; height: 88px; }
.spalten .sp-icon { margin-bottom: 30px; }
.rakete { gap: 0 70px; }
.rakete > div { padding: 42px 6px; grid-template-columns: 120px 1fr; }
.rakete .buchstabe { font-size: 118px; }
.rakete b { font-size: 40px; margin-bottom: 10px; }
.rakete span { font-size: 29px; }
.typen img { height: 380px; }
.typen h3 { font-size: 40px; }
.typen .prompt.klein { font-size: 26px; }
.typen .plus, .typen .minus { font-size: 26px; }
.antwort { padding: 44px 6px; }
.antwort p { font-size: 46px; }
.antwort .label { font-size: 22px; }
.mitnehmen > div { padding: 34px 4px; }
.mitnehmen .satz { font-size: 42px; }
.mitnehmen .satz small { font-size: 30px; }
.strahl.zwei .strahl-reihe + .strahl-reihe { margin-top: 80px; }
.strahl.zwei .strahl-text { font-size: 27px; }
.strahl.zwei .strahl-jahr { font-size: 46px; }
.tempo .zahl { font-size: 320px; }
.tempo .einheit { font-size: 46px; }
.tempo .was { font-size: 30px; }
.stufe { font-size: 96px; }
.stufe-wohin { font-size: 23px; margin-top: 24px; }
.lead { font-size: 38px; }
/* Folie 25: sechs lange Bausteine plus Takeaway, deshalb enger */
.rakete.kompakt > div { padding: 22px 6px; grid-template-columns: 100px 1fr; }
.rakete.kompakt .buchstabe { font-size: 96px; }
.rakete.kompakt b { font-size: 34px; margin-bottom: 6px; }
.rakete.kompakt span { font-size: 26px; line-height: 1.4; }
</style>"""
html = html.replace("</style>", zusatz, 1)

html = html.replace("""Reveal.on('ready', function () {
  document.querySelectorAll('.reveal .slides section[data-schleier]').forEach(function (s) {
    var bg = Reveal.getSlideBackground(s);
    if (bg) bg.dataset.schleier = s.dataset.schleier;
  });
});""", """function schleierKopieren() {
  document.querySelectorAll('.reveal .slides section[data-schleier]').forEach(function (s) {
    var bg = Reveal.getSlideBackground(s);
    if (bg) bg.dataset.schleier = s.dataset.schleier;
  });
}
Reveal.on('ready', schleierKopieren);
Reveal.on('slidechanged', schleierKopieren);""")

anfang = html.index('<div class="slides">') + len('<div class="slides">')
ende = html.index('</div>\n</div>\n\n<script src="vendor/reveal/reveal.js">')
html = html[:anfang] + "\n\n" + folien.strip() + "\n\n" + html[ende:]
(HIER / "index.html").write_text(html, encoding="utf-8")
print("index.html gebaut:", html.count("<section"), "Folien")
