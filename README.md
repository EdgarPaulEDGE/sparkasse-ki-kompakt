# KI-Kompakt. Der S-KIPilot im Arbeitsalltag

Workshop von EDGE Digital für die **Sparkasse zu Lübeck**, online,
**10. September 2026, 13:00 bis 16:30 Uhr**. 18 Teilnehmende in drei
Sechsergruppen, alle neu im Thema. 35 Folien plus drei Fall-PDFs.
Vor Ort: Edgar Paul-Ghazaryan (Eddie, COO) und Chakira Kambara
(AI Social Media Managerin). Emre ist an dem Tag nicht dabei.

## Live

**https://kompakt.edge-digital.ai/**
GitHub Pages aus `main`, Repo `EdgarPaulEDGE/sparkasse-ki-kompakt`, öffentlich.
Jeder Push auf `main` geht in etwa einer Minute live. Die alte Adresse
`edgarpauledge.github.io/sparkasse-ki-kompakt/` leitet per 301 dorthin um.
Der CNAME `kompakt` liegt in der Wix-DNS-Zone von edge-digital.ai (gesetzt am
05.09.2026, Wix-Editor scrollt nur über die Scrollleiste, nicht per Mausrad).

## Bauweise

Das Deck ist ein Kind des K64-Stamms (`CC/cbl-aufgeweckt`, 80/20-Prinzip):
Kopf, Stylesheet, Galaxie und Skript kommen unverändert von dort, dieses
Projekt hält nur `folien.html`, den Zusatzstil in `bau.py` und die Bilder.

```bash
python3 bau.py          # setzt index.html aus Stamm + folien.html zusammen
npm run serve           # http://localhost:8171
npm run pruefe-alles    # Layoutprüfungen im Browser, braucht laufenden Server
```

`node_modules` ist ein Symlink auf den Stamm. Wer am Stil etwas ändert,
ändert es im K64-Deck und baut hier neu, nicht umgekehrt. Deckspezifisches
(Sparkassen-Rot, RAKETE-Raster, Schutzstufen, Prompt-Typen, Fallfarben)
lebt im `zusatz`-Block von `bau.py`.

## Bedienung

| Taste | Wirkung |
|---|---|
| Pfeil rechts / links | Blättern |
| **S** | Redneransicht mit allen Regie-Notizen |
| **F** | Vollbild |
| **O** | Übersicht |

`?nofrag` an die Adresse zeigt alle Einblendungen sofort. Nur eine Folie
baut sich klickweise auf: die RAKETE (22) mit sechs Bausteinen. Alles andere
steht beim Folienwechsel komplett. Zwei Folien animieren von selbst: die
Wachstumskurven auf Folie 9 und die Dampfschwaden auf der Titelfolie.

## Der Begleiter: Sparky

Der Roboter mit der roten „Sparkasse zu Lübeck“-Kappe kommt aus
`EDGE/Clients/Sparkasse zu Lübeck/Sparky/` (dort liegen 20 Posen und 15
Szenen in Originalgröße). Hier liegen sie beschnitten und auf 1200 Pixel
Höhe verkleinert in `assets/images/sparky/`, die Szenen auf 2048 Pixel in
`assets/images/szenen/`. Jede Pose steht dort, wo ihre Geste zum Inhalt
zeigt: ratlos bei der ersten Frage, Fernglas beim Ausblick, Megafon beim
Battle, Rakete beim Tempo, Laptop im Breakout, Glühbirne beim Prompt für
morgen. Alle Bilder sind KI-erzeugt und auf den Vollbildfolien gekennzeichnet.

Die beiden Pizza-Roboter (Folie 20) sind am 04.09.2026 mit Higgsfield
(Nano Banana Pro, Referenz `Sparky.png`) neu gebaut und per Background-Remover
freigestellt worden. Am 08.09. kamen dazu: neun freigestellte Figuren für den
Zeitstrahl in `assets/images/zeitstrahl/` (Turing bis ChatGPT), drei
Nachrichtenbilder für Folie 7 und zwei Szenen für Pause und Block-3-Auftakt
(`assets/images/szenen/news-*.jpg`, `pause-chill.jpg`, `drei-tueren.jpg`).

## Stand 05.09.2026

1. **Slido**: benutzt wird nur Event **#9940537** mit drei Abfragen
   (Folie 4 Einstiegsfrage, Folie 12 Potenzial-Wortwolke, Folie 34 Wortwolke
   zum Schluss). Mehr erlaubt der kostenlose Plan je Event nicht. Das zweite
   Event #3748531 stammt aus der alten Planung und bleibt ungenutzt liegen.
   QR-Code: `assets/images/slido-1.png`, mit zxingcpp gegengelesen.
2. **Kahoot** „KI-Kompakt Sparkasse zu Lübeck“ liegt im Kahoot-Konto
   (`create.kahoot.it/creator/1871ffde-06f3-448b-96e3-6b06f419230a`), zehn
   Fragen aus `kahoot/kahoot-ki-kompakt.xlsx`, jede mit Sparky-Bild. Die
   richtige Antwort wechselt jetzt die Position (2, 3, 1, 4, 2, 3, 4, 1, 3, 2),
   „Antworten mischen“ ist nicht mehr nötig. PIN entsteht erst beim Hosten,
   Folie 30 zeigt kahoot.it.
3. **Live-Momente einmal in Claude durchspielen**: der Businessplan auf
   Folie 23 (PDF liegt auf dem Desktop) und die Fördermittel-Recherche mit
   Websuche auf Folie 24. Beide Prompts vorher in den Zwischenspeicher. Die
   Demos laufen in Claude, weil EDGE keinen S-KIPilot-Zugang hat; die
   Teilnehmenden arbeiten in ihren Übungen im S-KIPilot.


## Kahoot

`kahoot/kahoot-ki-kompakt.xlsx` ist die Import-Tabelle im Kahoot-Format
(Fragen ab Zeile 9, Spalten B bis H). Der Weg, der funktioniert hat: im
Creator „Hinzufügen“, Reiter „Import“, „Tabelle importieren“, Datei setzen.
Direktes Tippen in die Lexical-Editoren per DOM sieht gespeichert aus,
kommt aber nie im Modell an (`kahoot/treiber*.py` sind die Fehlversuche,
`aufraeumen.py` der Import-Nachlauf).

Jede Frage trägt ein Sparky-Bild (`kahoot/bilder/`): Rakete, Türsteher,
Papierberg, Laufband, Teamwork, EU-Richter, Verkehrspolizist, Tresor, Koch,
Azubi mit Kaffeetablett.

`kahoot/pflege.py` ist das Werkzeug dafür: `pruefen` zeigt je Frage, auf
welcher Position die richtige Antwort steht und ob ein Bild hängt, `bilder`
hängt sie an. Zwei Fallen stecken darin, beide teuer gelernt:

- Die Block-Kennungen `kahoot-block-N` sind **keine Positionen**. Sie bleiben
  an der Frage kleben, auch wenn davor gelöscht wird. Nach dem Ersetzen der
  zehn Fragen hießen sie 11 bis 20. Das Skript liest sie deshalb immer frisch
  aus der Seite.
- Nach dem Anwählen einer Frage braucht der Editor einen Moment. Ohne Abgleich
  gegen den erwarteten Fragetext landet ein Bild in der Nachbarfrage, und eine
  Messung liest die vorherige Frage. Der Zustand „richtige Antwort“ steht
  übrigens nur im Text des Antwortblocks („als die richtige Antwort markiert“),
  nicht im aria-label des Schalters.

## Die drei Fälle

`faelle/bau_faelle.py` baut die PDFs mit reportlab und den Sparkasse-Schriften:

| Fall | Gruppe | Farbe | Aufgabe |
|---|---|---|---|
| A | Privatkunden | Rot | Verärgerte Kundenmail: Antwortmail + Leitfaden für den Rückruf |
| B | Prozesse | Blau | FI-Rundschreiben (Seite 2): Management Summary + Intranet-Meldung |
| C | Firmenkundencenter | Grün | PV-Förderung mit Web-Hilfe: Antwortmail mit Optionen und nächsten Schritten |

Alles fiktiv, alles S1. Firmen, Personen und das Rundschreiben 2026/41 sind
erfunden. Die Fallfarben sind die Ringfarben auf den Folien 29 und 31.

## Gestaltung

Wie K64, SoulByte und Lübeck.lokal: Raumschwarz `#030309`, Avenir Next,
Galaxie aus `kosmos.js`, Schlüsselwörter im Verlauf Purple zu Blau zu Cyan.
Sparkassen-Rot nur als Gastfarbe (Fall A, Einschränkung in der RAKETE).
Keine Dashes, keine Emojis, kein Monospace, kein `box-shadow`.
Logos: EDGE links oben, Sparkasse rechts oben, auf Titel und Trennfolien aus.
