#!/usr/bin/env python3
"""Baut die drei Fall-PDFs für die Breakout-Session am 10.09.2026.

Design wie die Juni-Fälle: dunkle Fläche, eine Akzentfarbe je Fall (A rot,
B blau, C grün), Sparkasse-Schrift, Fußzeile mit Seitenzähler. Fall B trägt
das fiktive FI-Rundschreiben als zweite Seite. Aufruf: python3 bau_faelle.py
"""
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, KeepTogether)

HIER = pathlib.Path(__file__).parent
pdfmetrics.registerFont(TTFont("Sparkasse", str(HIER / "Sparkasse Rg Regular.ttf")))
pdfmetrics.registerFont(TTFont("Sparkasse-Bold", str(HIER / "Sparkasse Rg Bold.ttf")))

RAUM = colors.HexColor("#121214")
WEISS = colors.HexColor("#F4F6FF")
GRAU = colors.HexColor("#B8BCC8")
GRAU_DUNKEL = colors.HexColor("#7A7F8C")
KASTEN = colors.HexColor("#1B1B20")
W, H = A4
RAND = 18 * mm

FAELLE = {
    "A": dict(farbe=colors.HexColor("#FF3B3B"), bereich="Kundencenter",
              titel="Die verärgerte Kundenmail",
              datei="Fall_A_Kundencenter_Kundenmail.pdf"),
    "B": dict(farbe=colors.HexColor("#3FB4FF"), bereich="Vorstandsstab",
              titel="Das FI-Rundschreiben",
              datei="Fall_B_Vorstandsstab_Rundschreiben.pdf"),
    "C": dict(farbe=colors.HexColor("#3AD29F"), bereich="Firmenkundencenter",
              titel="Fördermittel für die PV-Anlage",
              datei="Fall_C_Firmenkundencenter_Foerdermittel.pdf"),
}


def stile(farbe):
    return dict(
        titel=ParagraphStyle("titel", fontName="Sparkasse-Bold", fontSize=26, leading=30, textColor=WEISS),
        titel2=ParagraphStyle("titel2", fontName="Sparkasse-Bold", fontSize=26, leading=30, textColor=farbe),
        label=ParagraphStyle("label", fontName="Sparkasse-Bold", fontSize=8.5, leading=11, textColor=farbe,
                             spaceBefore=0, spaceAfter=5),
        labelgrau=ParagraphStyle("labelgrau", fontName="Sparkasse-Bold", fontSize=8.5, leading=11,
                                 textColor=GRAU_DUNKEL, spaceAfter=5),
        text=ParagraphStyle("text", fontName="Sparkasse", fontSize=10, leading=14.2, textColor=GRAU),
        textweiss=ParagraphStyle("textweiss", fontName="Sparkasse", fontSize=10, leading=14.2, textColor=WEISS),
        fett=ParagraphStyle("fett", fontName="Sparkasse-Bold", fontSize=10, leading=14.2, textColor=WEISS),
        punkt=ParagraphStyle("punkt", fontName="Sparkasse", fontSize=9.6, leading=13.6, textColor=GRAU, leftIndent=10,
                             bulletIndent=0),
        mail=ParagraphStyle("mail", fontName="Sparkasse", fontSize=9.6, leading=13.6, textColor=WEISS),
        mailkopf=ParagraphStyle("mailkopf", fontName="Sparkasse", fontSize=9, leading=13, textColor=GRAU_DUNKEL),
        rund=ParagraphStyle("rund", fontName="Sparkasse", fontSize=9.1, leading=12.6, textColor=GRAU),
        rundh=ParagraphStyle("rundh", fontName="Sparkasse-Bold", fontSize=9.8, leading=13, textColor=WEISS,
                             spaceBefore=5, spaceAfter=1),
    )


def kasten(inhalt, farbe, breite, rahmen=True, hintergrund=KASTEN):
    """Ein Kasten mit Akzentrahmen, wie in den Juni-Fällen."""
    t = Table([[inhalt]], colWidths=[breite])
    stil = [("BACKGROUND", (0, 0), (-1, -1), hintergrund),
            ("LEFTPADDING", (0, 0), (-1, -1), 16), ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("TOPPADDING", (0, 0), (-1, -1), 11), ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ("ROUNDEDCORNERS", [8, 8, 8, 8])]
    if rahmen:
        stil.append(("BOX", (0, 0), (-1, -1), 1.2, farbe))
    t.setStyle(TableStyle(stil))
    return t


def seite(farbe, kennung, seiten_gesamt, anlage=False):
    def zeichnen(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(RAUM)
        canvas.rect(0, 0, W, H, stroke=0, fill=1)
        # Fußzeile
        canvas.setFont("Sparkasse-Bold", 6.6)
        canvas.setFillColor(GRAU_DUNKEL)
        canvas.drawString(RAND, 14 * mm, "EDGE DIGITAL · KI-KOMPAKT · SPARKASSE ZU LÜBECK · 10. SEPTEMBER 2026")
        zeile2 = (f"FALL {kennung} · BREAKOUT-SESSION · SEITE {doc.page} VON {seiten_gesamt}"
                  if not anlage or doc.page == 1 else
                  f"FALL {kennung} · ANLAGE ZUR ÜBUNG · SEITE {doc.page} VON {seiten_gesamt}")
        canvas.drawString(RAND, 10 * mm, zeile2)
        # Kennung rechts unten in der Fallfarbe
        canvas.setFillColor(farbe)
        canvas.circle(W - RAND - 5 * mm, 12.5 * mm, 5 * mm, stroke=0, fill=1)
        canvas.setFillColor(RAUM)
        canvas.setFont("Sparkasse-Bold", 11)
        canvas.drawCentredString(W - RAND - 5 * mm, 12.5 * mm - 3.8, kennung)
        canvas.restoreState()
    return zeichnen


def bauen(kennung, bloecke, anlage=None):
    fall = FAELLE[kennung]
    farbe = fall["farbe"]
    st = stile(farbe)
    breite = W - 2 * RAND
    gesamt = 2 if anlage else 1
    doc = BaseDocTemplate(str(HIER / fall["datei"]), pagesize=A4,
                          leftMargin=RAND, rightMargin=RAND, topMargin=15 * mm, bottomMargin=22 * mm,
                          title=f"Fall {kennung}: {fall['titel']}", author="EDGE Digital")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="s", frames=[frame],
                                       onPage=seite(farbe, kennung, gesamt, anlage=bool(anlage)))])
    E = [Paragraph(f"Fall {kennung} · {fall['bereich']}", st["labelgrau"]),
         Paragraph(fall["titel"].split(" ", 1)[0] if False else fall["bereich"], st["titel"]),
         Paragraph(fall["titel"], st["titel2"]),
         Spacer(1, 12)]
    for art, inhalt in bloecke:
        if art == "abschnitt":
            label, text = inhalt
            E += [Paragraph(label, st["label"]), Paragraph(text, st["text"]), Spacer(1, 9)]
        elif art == "kasten":
            label, absaetze, wichtig = inhalt
            innen = [Paragraph(label, st["label"])]
            for a in absaetze:
                innen += [Paragraph(a, st["fett"] if wichtig else st["textweiss"]), Spacer(1, 5)]
            E += [KeepTogether(kasten(innen, farbe, breite)), Spacer(1, 9)]
        elif art == "mail":
            kopf, absaetze = inhalt
            innen = [Paragraph(k, st["mailkopf"]) for k in kopf] + [Spacer(1, 7)]
            for a in absaetze:
                innen += [Paragraph(a, st["mail"]), Spacer(1, 5)]
            E += [KeepTogether(kasten(innen, farbe, breite, rahmen=False,
                                      hintergrund=colors.HexColor("#1F1F26"))), Spacer(1, 9)]
        elif art == "punkte":
            label, punkte = inhalt
            E += [Paragraph(label, st["labelgrau"])]
            E += [Paragraph(f"·&nbsp;&nbsp;{p}", st["punkt"]) for p in punkte]
    if anlage:
        E.append(PageBreak())
        E += [Paragraph("Anlage zur Übung", st["labelgrau"]),
              Paragraph(anlage["titel"], st["titel"]),
              Paragraph(anlage["untertitel"], ParagraphStyle("ut", fontName="Sparkasse", fontSize=12,
                                                              leading=16, textColor=GRAU)),
              Spacer(1, 9)]
        innen = [Paragraph(anlage["label"], st["label"]), Spacer(1, 4)]
        for a in anlage["absaetze"]:
            if a.startswith("## "):
                innen.append(Paragraph(a[3:], st["rundh"]))
            else:
                innen += [Paragraph(a, st["rund"]), Spacer(1, 4)]
        E.append(kasten(innen, farbe, breite))
    doc.build(E)
    print("gebaut:", fall["datei"], "Seiten:", doc.page)


HINWEISE = ("Denkt zum Beispiel an", [
    "R-A-K-E-T-E: Rolle, Auftrag, Kontext, Ergebnis, Ton, Einschränkung",
    "Der Prompt ist euer Ergebnis. Zeigt, WIE ihr gefragt habt.",
    "Alles ist fiktiv und S1. Keine echten Kundendaten in den S-KIPilot.",
    "Eine Person aus eurer Gruppe präsentiert, fünf Minuten.",
])

# ---------------------------------------------------------------- Fall A
bauen("A", [
    ("abschnitt", ("Situation",
        "Herr Jansen ist seit 14 Jahren Kunde und hat im Juli auf Empfehlung eines Beraters vom "
        "Kontomodell „Giro Klassik“ auf „Giro Komfort“ gewechselt. Auf dem Augustauszug steht zum "
        "ersten Mal eine Kontoführungsgebühr von 9,90 Euro. Er hatte verstanden, das neue Modell sei "
        "für ihn kostenlos. Heute Morgen kam seine Mail ins Kundencenter, und sie ist deutlich.")),
    ("mail", (["Von: t.jansen@beispiel-mail.de", "An: kundencenter@sparkasse-luebeck.de",
               "Betreff: Kontoführungsgebühr?? Ich bin fassungslos"], [
        "Sehr geehrte Damen und Herren,",
        "im Juli hat mir Ihr Kollege den Wechsel auf Giro Komfort empfohlen. Kostenlos, hieß es, "
        "wegen meines Gehaltseingangs. Jetzt sehe ich auf dem Auszug 9,90 Euro Kontoführungsgebühr. "
        "Das hat mir niemand gesagt. Ich habe nicht vor, für ein Konto zu bezahlen, das ich vorher "
        "14 Jahre kostenlos hatte.",
        "Wenn das so bleibt, kündige ich mein Konto und wechsle zu einer Direktbank. Ich erwarte "
        "eine Antwort bis Freitag.",
        "Thomas Jansen"])),
    ("kasten", ("Was ihr wisst", [
        "Giro Komfort kostet 9,90 Euro im Monat. Die Gebühr entfällt ab einem monatlichen Geldeingang "
        "von 2.500 Euro. Herr Jansens Gehaltseingang lag im August bei 2.380 Euro, weil ein Teil "
        "auf ein anderes Konto ging.",
        "Ihr könnt anbieten: die Gebühr für August aus Kulanz erstatten, den Geldeingang prüfen und "
        "gemeinsam das passende Modell wählen. Ein Rückwechsel auf Giro Klassik ist möglich."], False)),
    ("kasten", ("Eure Aufgabe", [
        "Erstellt mit dem S-KIPilot zwei Dinge aus derselben Information: erstens eine wertschätzende, "
        "lösungsorientierte Antwortmail an Herrn Jansen, zweitens einen kurzen Gesprächsleitfaden für "
        "den Rückruf, falls er anruft, bevor die Mail raus ist.",
        "Achtet darauf, wie stark Ton und Einschränkung im Prompt das Ergebnis drehen. Nutzt das "
        "R-A-K-E-T-E-Schema."], True)),
    ("punkte", HINWEISE),
])

# ---------------------------------------------------------------- Fall B
RUNDSCHREIBEN = [
    "Sehr geehrte Damen und Herren,",
    "mit dem OSPlus-Release 26.2 werden zum 2. November 2026 die Prozesse der Legitimationsprüfung "
    "und der Dokumentation im Kontoeröffnungsprozess für natürliche Personen angepasst. Die "
    "Änderungen setzen die Anforderungen der Auslegungs- und Anwendungshinweise der BaFin in der "
    "Fassung vom 12. Februar 2026 sowie die Beschlüsse des Fachrats Vertriebsprozesse vom 3. Juni "
    "2026 um. Die Institute werden gebeten, die nachfolgend beschriebenen Anpassungen in ihre "
    "Arbeitsanweisungen zu übernehmen und die betroffenen Mitarbeitenden vor dem Stichtag zu schulen.",
    "## 1. Legitimationsprüfung (Abschnitt 3.4 Prozessbeschreibung Kontoeröffnung neu)",
    "Die Legitimationsprüfung erfolgt künftig ausschließlich über das Modul „Legitimation digital“ "
    "im OSPlus-Portal. Die manuelle Erfassung der Ausweisdaten in der Kundenstammmaske entfällt. Das "
    "Modul liest die Daten des Ausweisdokuments über den Kartenleser beziehungsweise die Kamera des "
    "Arbeitsplatzes aus, prüft die Echtheitsmerkmale automatisiert und übernimmt die Daten in den "
    "Kundenstamm. Eine Sichtprüfung durch die Mitarbeitenden bleibt verpflichtend und ist im Modul "
    "durch Bestätigung des Prüfschritts „Dokument in Augenschein genommen“ zu quittieren. Bei "
    "Ausweisdokumenten ohne maschinenlesbare Zone ist der Ersatzprozess nach Abschnitt 3.4.3 zu "
    "verwenden.",
    "## 2. Dokumentation (Abschnitt 3.6 Prozessbeschreibung Kontoeröffnung neu)",
    "Die bisherige Ausweiskopie in Papierform wird durch die elektronische Legitimationsakte "
    "ersetzt. Das Modul legt je Kontoeröffnung automatisch einen Vorgang unter „Kunde > Legitimation "
    "> Vorgänge“ an, der das Prüfprotokoll, die Bilddatei des Dokuments und den Zeitstempel der "
    "Sichtprüfung enthält. Papierhafte Zweitablagen sind ab dem Stichtag unzulässig. Bereits "
    "bestehende Papierakten sind nicht nachzuerfassen. Die Aufbewahrungsfrist beträgt unverändert "
    "fünf Jahre ab Ende der Geschäftsbeziehung.",
    "## 3. Vier-Augen-Prinzip und Freigabe (Abschnitt 3.7 neu)",
    "Kontoeröffnungen, bei denen das Modul ein Echtheitsmerkmal als „nicht prüfbar“ kennzeichnet, "
    "sind vor Freigabe durch eine zweite Person mit der Rolle „Legitimation Freigabe“ zu bestätigen. "
    "Die Rolle ist durch die Institute bis zum 15. Oktober 2026 im Berechtigungssystem zu vergeben. "
    "Ohne Zweitfreigabe wird der Vorgang mit dem Status „Eröffnung gesperrt“ geführt und nach 10 "
    "Bankarbeitstagen automatisch storniert.",
    "## 4. Übergangsregelung und Schulung",
    "Kontoeröffnungen, die vor dem 2. November 2026 begonnen und nach diesem Datum abgeschlossen "
    "werden, können nach dem bisherigen Verfahren beendet werden. Für alle Mitarbeitenden mit "
    "Kontoeröffnungsberechtigung steht ab dem 1. Oktober 2026 das Web Based Training „Legitimation "
    "digital“ in der Lernwelt bereit. Die Institute stellen die Teilnahme vor dem Stichtag sicher. "
    "Die aktualisierte Prozessbeschreibung wird am 20. Oktober 2026 im FI-Kundenportal "
    "veröffentlicht.",
    "Bei Rückfragen wenden Sie sich bitte an das FI-Servicecenter Vertriebsprozesse "
    "(vertriebsprozesse@f-i.de) oder an Ihre Kundenbetreuung.",
    "Mit freundlichen Grüßen",
    "Finanz Informatik GmbH & Co. KG, Bereich Vertriebsprozesse",
]

bauen("B", [
    ("abschnitt", ("Situation",
        "Ein Rundschreiben der Finanz Informatik kündigt das OSPlus-Release 26.2 an. Es ändert die "
        "Legitimationsprüfung und die Dokumentation bei der Kontoeröffnung, dazu kommt eine neue "
        "Freigaberolle mit Frist. Der Originaltext steht auf der nächsten Seite, geschrieben im "
        "typischen Aufsichts- und Juristendeutsch. Der Vorstand will es in zwei Minuten erfassen, die "
        "Belegschaft will wissen, was sich für sie ändert. Beide aus derselben Quelle.")),
    ("kasten", ("Was ihr wisst", [
        "Betroffen sind alle Geschäftsstellen, das Kundencenter und die Marktfolge. Die Rolle "
        "„Legitimation Freigabe“ muss bis 15. Oktober vergeben sein, das Training steht ab "
        "1. Oktober bereit, Stichtag ist der 2. November 2026.",
        "Das Rundschreiben ist fiktiv und für die Übung geschrieben. Es enthält keine echten "
        "Kundendaten und kann in den S-KIPilot kopiert werden."], False)),
    ("kasten", ("Eure Aufgabe", [
        "Schritt 1: Kopiert das Rundschreiben von Seite 2 in den S-KIPilot und lasst euch "
        "strukturieren, welche Bereiche betroffen sind, was zu tun ist und bis wann.",
        "Schritt 2: Erstellt daraus zwei Kommunikationsstücke: eine kompakte Vorstandsinformation als "
        "Management Summary (halbe Seite, Entscheidungsbedarf zuerst) und eine verständliche "
        "Intranet-Meldung für die Belegschaft (höchstens 200 Wörter, ohne Fachjargon, mit dem "
        "Abschnitt „Das ändert sich für Sie“).",
        "Nutzt das R-A-K-E-T-E-Schema und zeigt am Ende beide Prompts nebeneinander."], True)),
    ("punkte", HINWEISE),
], anlage=dict(
    titel="Rundschreiben 2026/41",
    untertitel="OSPlus-Release 26.2: Anpassung der Legitimationsprüfung und Dokumentation im "
               "Kontoeröffnungsprozess",
    label="Originaltext · Diesen Text in den S-KIPilot kopieren",
    absaetze=RUNDSCHREIBEN))

# ---------------------------------------------------------------- Fall C
bauen("C", [
    ("abschnitt", ("Situation",
        "Die Nordholz Metallbau GmbH aus Lübeck, ein Produktionsbetrieb mit 40 Mitarbeitenden, "
        "plant eine Photovoltaikanlage auf dem Betriebsdach. Der Geschäftsführer hat seinem "
        "Firmenkundenberater geschrieben und will wissen, wie sich das finanzieren lässt und welche "
        "Förderprogramme in Frage kommen. Er erwartet keine Zusage, aber einen Überblick, mit dem er "
        "im Betrieb weiterplanen kann.")),
    ("mail", (["Von: m.nordholz@nordholz-metallbau-beispiel.de", "An: firmenkunden@sparkasse-luebeck.de",
               "Betreff: PV-Anlage auf dem Hallendach, Finanzierung und Förderung"], [
        "Moin Herr Petersen,",
        "wir wollen im Frühjahr eine PV-Anlage auf die Halle setzen. Die Dachfläche liegt bei rund "
        "1.200 Quadratmetern, der Planer rechnet mit etwa 200 Kilowatt-Peak und einer Investition um "
        "220.000 Euro. Etwa zwei Drittel des Stroms würden wir selbst verbrauchen.",
        "Welche Möglichkeiten sehen Sie bei der Finanzierung, und gibt es Förderprogramme, die wir "
        "prüfen sollten? Ein grober Überblick reicht mir erst mal.",
        "Viele Grüße, Malte Nordholz"])),
    ("kasten", ("Was ihr wisst", [
        "Förderprogramme sind öffentlich: KfW (zum Beispiel Erneuerbare Energien), das Land "
        "Schleswig-Holstein über die IB.SH, dazu steuerliche Regelungen. Der S-KIPilot findet sie mit "
        "aktivierter Web-Hilfe, ihr prüft die Quellen.",
        "Bewusst keine Gesprächsvorbereitung: dafür hat der S-KIPilot eine eigene Funktion. Heute "
        "geht es um die schriftliche Antwort."], False)),
    ("kasten", ("Eure Aufgabe", [
        "Aktiviert im S-KIPilot die Web-Hilfe und lasst die aktuellen Förderprogramme für eine "
        "gewerbliche PV-Anlage in Schleswig-Holstein recherchieren, mit Quelle je Programm.",
        "Erstellt daraus eine verständliche Antwortmail an Herrn Nordholz: die relevanten Optionen "
        "(Förderkredit, Zuschuss, Eigenmittel, Sparkassenfinanzierung), was noch zu prüfen ist, und "
        "die nächsten Schritte. Konditionen als unverbindlich kennzeichnen, keine Finanzierungszusage.",
        "Nutzt das R-A-K-E-T-E-Schema. Die Einschränkung ist hier der wichtigste Baustein."], True)),
    ("punkte", HINWEISE),
])
