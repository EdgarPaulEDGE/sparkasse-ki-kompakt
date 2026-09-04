# KI-Kompakt. Der S-KIPilot im Arbeitsalltag

Workshop von EDGE Digital für die **Sparkasse zu Lübeck**, online,
**10. September 2026, 13:00 bis 16:30 Uhr**. 18 Teilnehmende in drei
Sechsergruppen, alle neu im Thema. 37 Folien plus drei Fall-PDFs.
Referenten: Emre Erdogan und Edgar Paul-Ghazaryan (Eddie).

## Bauweise

Das Deck ist ein Kind des K64-Stamms (`CC/cbl-aufgeweckt`, 80/20-Prinzip):
Kopf, Stylesheet, Galaxie und Skript kommen unverändert von dort, dieses
Projekt hält nur `folien.html`, den Zusatzstil in `bau.py` und die Bilder.

```bash
python3 bau.py          # setzt index.html aus Stamm + folien.html zusammen
npm run serve           # http://localhost:8080
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
baut sich klickweise auf: die RAKETE (23) mit sechs Bausteinen. Alles andere
steht beim Folienwechsel komplett.

## Der Begleiter: Sparky

Der Roboter mit der roten „Sparkasse zu Lübeck“-Kappe kommt aus
`EDGE/Clients/Sparkasse zu Lübeck/Sparky/` (dort liegen 20 Posen und 15
Szenen in Originalgröße). Hier liegen sie beschnitten und auf 1200 Pixel
Höhe verkleinert in `assets/images/sparky/`, die Szenen auf 2048 Pixel in
`assets/images/szenen/`. Jede Pose steht dort, wo ihre Geste zum Inhalt
zeigt: ratlos bei der ersten Frage, Fernglas beim Ausblick, Megafon beim
Battle, Rakete beim Tempo, Laptop im Breakout, Glühbirne beim Prompt für
morgen. Alle Bilder sind KI-erzeugt und auf den Vollbildfolien gekennzeichnet.

Ausnahme: die beiden Pizza-Roboter auf Folie 21 tragen noch die
Fischbrötchen-Mütze aus dem Lübeck-Deck. Wenn Zeit ist, mit Nano Banana 2
aus `Sparky.png` nachbauen (Prompt: dieselbe Szene, Kappe aus der Vorlage).

## Was noch fehlt (Stand 04.09.2026)

1. **Skippy-Updates** von Alyssa und Steffi auf Folie 7 einsetzen
   (Platzhalterkasten unten).
2. **Slido**: `assets/images/slido-qr.png` ist der Code vom Juni. Neues Event
   anlegen, QR tauschen. Vier Slido-Momente: Einstiegsfrage (4), Potenzial-
   Wordcloud (12), Prompt-Battle-Voting (19), Live-Reparatur-Bausteine (24),
   Mein erster Prompt (33).
3. **Kahoot**: PIN und QR auf Folie 32, zehn Fragen aus Block 1 und 2.
4. **Fall A**: geht davon aus, dass das Kundencenter schriftliche Beschwerden
   bearbeitet. Falls dort fast nur telefoniert wird, den Fall auf
   Gesprächsleitfaden plus internen Vermerk drehen (`faelle/bau_faelle.py`).
5. **Live-Momente einmal durchspielen**: Fördermittel-Prompt (25) mit
   Web-Hilfe im S-KIPilot, Live-Reparatur (24) mit der Fördermittel-Anfrage
   als Unterlage. Beide Prompts vorher in den Zwischenspeicher.

## Die drei Fälle

`faelle/bau_faelle.py` baut die PDFs mit reportlab und den Sparkasse-Schriften:

| Fall | Gruppe | Farbe | Aufgabe |
|---|---|---|---|
| A | Kundencenter | Rot | Verärgerte Kundenmail: Antwortmail + Leitfaden für den Rückruf |
| B | Vorstandsstab | Blau | FI-Rundschreiben (Seite 2): Management Summary + Intranet-Meldung |
| C | Firmenkundencenter | Grün | PV-Förderung mit Web-Hilfe: Antwortmail mit Optionen und nächsten Schritten |

Alles fiktiv, alles S1. Firmen, Personen und das Rundschreiben 2026/41 sind
erfunden. Die Fallfarben sind die Ringfarben auf den Folien 29 und 31.

## Gestaltung

Wie K64, SoulByte und Lübeck.lokal: Raumschwarz `#030309`, Avenir Next,
Galaxie aus `kosmos.js`, Schlüsselwörter im Verlauf Purple zu Blau zu Cyan.
Sparkassen-Rot nur als Gastfarbe (Fall A, Einschränkung in der RAKETE).
Keine Dashes, keine Emojis, kein Monospace, kein `box-shadow`.
Logos: EDGE links oben, Sparkasse rechts oben, auf Titel und Trennfolien aus.
