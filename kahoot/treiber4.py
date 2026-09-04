#!/usr/bin/env python3
"""Richtige Antworten anhand des Statustexts im Antwortkasten setzen, dann Titel und Speichern."""
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
        if "iWizMh" in js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').className" % i): return True
    return False
def zustand():
    return json.loads(js("JSON.stringify([...document.querySelectorAll('[data-functional-selector=question-answer]')].map(e=>e.innerText.includes('die richtige Antwort')))"))
for i,(q,ans,korrekt) in enumerate(fragen):
    waehlen(i); time.sleep(0.5)
    soll=[k==korrekt-1 for k in range(4)]
    for versuch in range(3):
        ist=zustand()
        if ist==soll: break
        for k in range(4):
            if ist[k]!=soll[k]:
                js("document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]')[%d].click()" % k); time.sleep(0.5)
    titel=js("document.querySelector('[data-functional-selector=question-title__input]').getAttribute('data-editor-value')")
    print(i+1, "OK" if zustand()==soll and titel==q else "FEHLER", zustand(), titel[:40])
# Titel setzen
js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Kahoot-Titel/.test(b.innerText)); b&&b.click();})()"); time.sleep(1.5)
print("Titel-Dialog Felder:", js("JSON.stringify([...document.querySelectorAll('input,textarea')].map(e=>(e.placeholder||e.getAttribute('aria-label')||e.id||'')+' | '+(e.getAttribute('data-functional-selector')||'')))"))
