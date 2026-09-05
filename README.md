# KI-Kompakt. Der S-KIPilot im Arbeitsalltag

Workshop von EDGE Digital für die **Sparkasse zu Lübeck**, online,
**10. September 2026, 13:00 bis 16:30 Uhr**. 18 Teilnehmende in drei
Sechsergruppen, alle neu im Thema. 37 Folien plus drei Fall-PDFs.
Referenten: Emre Erdogan und Edgar Paul-Ghazaryan (Eddie).

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

Die beiden Pizza-Roboter auf Folie 21 sind am 04.09.2026 mit Higgsfield
(Nano Banana Pro, Referenzen: `Sparky.png` plus die K64-Pizzabilder) neu
gebaut und per Background-Remover freigestellt worden.

## Was noch fehlt (Stand 04.09.2026)

1. **Slido** ist angelegt, zwei Events, weil der kostenlose Plan drei
   Abfragen je Event erlaubt: **#9940537** (Folien 4, 12, 19: Einstiegsfrage,
   Potenzial-Wordcloud, Prompt-Battle-Voting) und **#3748531** „Teil 2“
   (Folien 24, 33: Live-Reparatur-Bausteine, Mein erster Prompt). QR-Codes
   liegen in `assets/images/slido-1.png` und `slido-2.png`, mit zxingcpp
   gegengelesen. Beim Battle die drei Optionen „Ergebnis 1 bis 3“ live
   umbenennen. Ein Upgrade auf Engage würde beides in ein Event holen.
2. **Kahoot** „KI-Kompakt Sparkasse zu Lübeck“ liegt im Kahoot-Konto
   (`create.kahoot.it/creator/1871ffde-06f3-448b-96e3-6b06f419230a`), zehn
   Fragen aus `kahoot/kahoot-ki-kompakt.xlsx`. Die richtige Antwort steht
   überall an Position 1, deshalb beim Hosten „Antworten mischen“ einschalten.
   PIN entsteht erst beim Hosten, Folie 32 bleibt bei „Code kommt in den Chat“.
3. **Live-Momente einmal in Claude durchspielen**: Fördermittel-Prompt (25)
   mit Websuche, Live-Reparatur (24) mit der Fördermittel-Anfrage als
   Unterlage. Beide Prompts vorher in den Zwischenspeicher. Die Demos laufen
   in Claude, weil EDGE keinen S-KIPilot-Zugang hat; die Teilnehmenden
   arbeiten in ihren Übungen im S-KIPilot.

## Kahoot

`kahoot/kahoot-ki-kompakt.xlsx` ist die Import-Tabelle im Kahoot-Format
(Fragen ab Zeile 9, Spalten B bis H). Der Weg, der funktioniert hat: im
Creator „Hinzufügen“, Reiter „Import“, „Tabelle importieren“, Datei setzen.
Direktes Tippen in die Lexical-Editoren per DOM sieht gespeichert aus,
kommt aber nie im Modell an (`kahoot/treiber*.py` sind die Fehlversuche,
`aufraeumen.py` der Import-Nachlauf).

Jede Frage trägt ein Sparky-Bild (`kahoot/bilder/`, Higgsfield Nano Banana
Pro mit `Sparky.png` als Referenz, 16:9): Rakete, Türsteher, Papierberg,
Laufband, Teamwork, EU-Richter, Verkehrspolizist, Tresor, Koch, Azubi mit
Kaffeetablett. Upload über `kahoot/bilder_fix2.py`: Bild in Häppchen als
Base64 in die Seite, per DataTransfer ins File-Input des Upload-Dialogs.
Wichtig: vor jedem Upload warten, bis der Editor die richtige Frage zeigt
(Titelabgleich), sonst landet das Bild eine Frage weiter. Prüfung über die
Hintergrundbilder der Seitenleisten-Vorschau, nicht über den Editor.

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
