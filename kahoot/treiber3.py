#!/usr/bin/env python3
"""Zweiter Durchgang mit Verifikation: Block anwählen, warten bis die Auswahl
wirklich steht, dann Titel, Antworten und richtige Antwort setzen und prüfen."""
import json, subprocess, time, openpyxl
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    return subprocess.run(["osascript","-e",scr],capture_output=True,text=True).stdout.strip()
ws=openpyxl.load_workbook("kahoot/kahoot-ki-kompakt.xlsx").active
fragen=[(ws.cell(r,2).value,[ws.cell(r,c).value for c in range(3,7)],int(ws.cell(r,8).value)) for r in range(9,19)]
def waehlen(i):
    js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').click()" % i)
    for _ in range(20):
        time.sleep(0.4)
        cls=js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').className" % i)
        andere=js("[...document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]')].filter(e=>e.className.includes('iWizMh')).length")
        if "iWizMh" in cls and andere.startswith("1"): return True
    return False
def tippen(sel_js, text):
    js("(()=>{const el=%s; el.focus(); document.execCommand('selectAll',false,null); document.execCommand('delete',false,null); document.execCommand('insertText',false,%s); el.blur();})()" % (sel_js, json.dumps(text,ensure_ascii=False)))
    time.sleep(0.4)
    return js("(%s).getAttribute('data-editor-value')" % sel_js)
fehler=[]
for i,(q,ans,korrekt) in enumerate(fragen):
    ok=waehlen(i); 
    t=tippen("document.querySelector('[data-functional-selector=question-title__input]')", q)
    if t!=q: t=tippen("document.querySelector('[data-functional-selector=question-title__input]')", q)
    got=[]
    for k,a in enumerate(ans):
        v=tippen("document.querySelectorAll('[data-functional-selector=question-answer__input]')[%d]" % k, a)
        if v!=a: v=tippen("document.querySelectorAll('[data-functional-selector=question-answer__input]')[%d]" % k, a)
        got.append(v)
    # richtige Antwort: Label sagt, wohin umgeschaltet wird
    for k in range(4):
        lab=js("document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]')[%d].getAttribute('aria-label')" % k)
        ist_richtig = "falsch" in lab   # „auf falsch umschalten" heißt: ist gerade richtig
        soll = (k==korrekt-1)
        if ist_richtig!=soll:
            js("document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]')[%d].click()" % k); time.sleep(0.4)
    labs=js("JSON.stringify([...document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]')].map(b=>b.getAttribute('aria-label').includes('falsch')))")
    stat="OK" if (ok and t==q and got==ans and json.loads(labs)==[k==korrekt-1 for k in range(4)]) else "FEHLER"
    if stat=="FEHLER": fehler.append(i+1)
    print(i+1, stat, "| ausgewählt:",ok, "| Titel:", t==q, "| Antworten:", got==ans, "| richtig:", labs)
print("Fehler bei:", fehler)
