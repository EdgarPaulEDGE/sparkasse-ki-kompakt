#!/usr/bin/env python3
"""Pflegt das Kahoot über Safari: Fragen anwählen, Bilder anhängen, Antworten prüfen.

Wichtig, zweimal teuer gelernt:
1. Die Block-Kennungen (kahoot-block-N) sind KEINE Positionen. Sie bleiben an der
   Frage kleben, auch wenn davor gelöscht wird. Deshalb werden sie hier immer
   frisch aus der Seite gelesen, nie geraten.
2. Nach dem Anwählen einer Frage braucht der Editor einen Moment. Ohne Abgleich
   (erste Antwort stimmt mit der Seitenleiste überein) landet ein Bild in der
   falschen Frage, und die Prüfung misst die vorherige Frage.

Aufruf:
    python3 kahoot/pflege.py pruefen          Positionen der richtigen Antworten
    python3 kahoot/pflege.py bilder [n ...]   Bilder anhängen (ohne n: alle)
"""
import base64, json, pathlib, subprocess, sys, time

HIER = pathlib.Path(__file__).parent
ERWARTET = [2, 3, 1, 4, 2, 3, 4, 1, 3, 2]   # Position der richtigen Antwort je Frage


def js(code, versuche=3):
    scr = ('tell application "Safari"\nrepeat with w from 1 to (count of windows)\n'
           'repeat with i from 1 to (count of tabs of window w)\n'
           'if URL of tab i of window w contains "kahoot.it/creator" then\n'
           'return do JavaScript "%s" in tab i of window w\nend if\n'
           'end repeat\nend repeat\nend tell') % code.replace('\\', '\\\\').replace('"', '\\"')
    for _ in range(versuche):
        r = subprocess.run(["osascript", "-e", scr], capture_output=True, text=True)
        if r.stdout.strip():
            return r.stdout.strip()
        time.sleep(1)
    return ""


def block_ids():
    """Die Kennungen in Anzeigereihenfolge, direkt aus der Seitenleiste."""
    roh = js("JSON.stringify([...document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]')]"
             ".map(e=>e.getAttribute('data-functional-selector')))")
    return json.loads(roh)


def titel_liste():
    """Die Fragetexte in Anzeigereihenfolge, aus der Import-Tabelle gelesen.

    Die Seitenleiste mischt Nummer, Fragetyp und Zeitlimit in denselben Text,
    deshalb ist die Tabelle die verlässlichere Quelle für den Abgleich."""
    import openpyxl
    ws = openpyxl.load_workbook(HIER / "kahoot-ki-kompakt.xlsx").active
    return [ws.cell(r, 2).value for r in range(9, 19)]


def waehlen(sel, erwarte_titel):
    """Frage anwählen und warten, bis der Editor sie wirklich zeigt."""
    js("document.querySelector('[data-functional-selector=%s]').click()" % sel)
    stichwort = erwarte_titel[:26]
    for _ in range(24):
        time.sleep(0.5)
        jetzt = js("(document.querySelector('[data-functional-selector=question-title__input]')||{})"
                   ".getAttribute ? document.querySelector('[data-functional-selector=question-title__input]')"
                   ".getAttribute('data-editor-value') : ''")
        if jetzt[:26] == stichwort:
            return True
    return False


def pruefen():
    ids, titel = block_ids(), titel_liste()
    ist = []
    for n, (sel, t) in enumerate(zip(ids, titel), 1):
        ok = waehlen(sel, t)
        roh = js("JSON.stringify([...document.querySelectorAll('[data-functional-selector=question-answer]')]"
                 ".map(e=>e.innerText.includes('als die richtige Antwort markiert')))")
        pos = [k + 1 for k, v in enumerate(json.loads(roh)) if v]
        bild = js("!!document.querySelector('[data-functional-selector=media-details__with-media]')") == "true"
        ist.append(pos[0] if len(pos) == 1 else pos)
        print(f"{n:2}  Position {str(ist[-1]):>3}  Bild {'ja' if bild else 'NEIN'}  angewählt {'ok' if ok else 'UNSICHER'}")
    print("\nist :", ist)
    print("soll:", ERWARTET, "PASST" if ist == ERWARTET else "ABWEICHUNG")


def bild_anhaengen(n, sel, titel):
    if not waehlen(sel, titel):
        return "Frage nicht sicher angewählt"
    if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')") == "true":
        js("document.querySelector('[data-functional-selector=media-details__media-remove]').click()")
        time.sleep(1.5)
    js("(()=>{const b=[...document.querySelectorAll('button')].find(e=>/^Datei hochladen$/.test(e.innerText.trim())); b&&b.click();})()")
    for _ in range(14):
        time.sleep(0.5)
        if js("!!document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]')") == "true":
            break
    else:
        return "kein Upload-Dialog"
    b64 = base64.b64encode((HIER / "bilder" / f"frage-{n:02d}.jpg").read_bytes()).decode()
    js("window.__b=''")
    for k in range(0, len(b64), 150000):
        js("window.__b+='%s'" % b64[k:k + 150000])
    js("(()=>{const inp=document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]');"
       "const bin=atob(window.__b); const arr=new Uint8Array(bin.length);"
       "for(let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i);"
       "const f=new File([arr],'sparky-%02d.jpg',{type:'image/jpeg'}); const dt=new DataTransfer(); dt.items.add(f);"
       "inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})()" % n)
    for _ in range(30):
        time.sleep(1)
        if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')") == "true":
            return "Bild sitzt"
    return "Bild kam nicht an"


def bilder(nummern):
    ids, titel = block_ids(), titel_liste()
    for n in nummern:
        print(f"{n:2}", bild_anhaengen(n, ids[n - 1], titel[n - 1]))
    js("document.querySelector('[data-functional-selector=top-bar__save-button]').click()")
    time.sleep(6)
    print("gespeichert:", js("document.body.innerText.slice(0,60).replace(/\\n+/g,' / ')"))


if __name__ == "__main__":
    was = sys.argv[1] if len(sys.argv) > 1 else "pruefen"
    if was == "pruefen":
        pruefen()
    else:
        nrs = [int(x) for x in sys.argv[2:]] or list(range(1, 11))
        bilder(nrs)
