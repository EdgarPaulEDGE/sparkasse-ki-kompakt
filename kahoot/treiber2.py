#!/usr/bin/env python3
"""Befüllt die Kahoot-Fragen über den Lexical-Editor (execCommand insertText),
weil direktes Setzen von innerText vom Editor verworfen wird."""
import json, subprocess, time, openpyxl
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    return subprocess.run(["osascript","-e",scr],capture_output=True,text=True).stdout.strip()
ws=openpyxl.load_workbook("kahoot/kahoot-ki-kompakt.xlsx").active
fragen=[(ws.cell(r,2).value,[ws.cell(r,c).value for c in range(3,7)],int(ws.cell(r,8).value)) for r in range(9,19)]
n_bloecke=int(float(js("document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]').length") or 0))
print("Blöcke vorhanden:", n_bloecke)
def tippen(sel_js, text):
    return js("(()=>{const el=%s; if(!el) return 'fehlt'; el.focus(); document.execCommand('selectAll',false,null); document.execCommand('delete',false,null); document.execCommand('insertText',false,%s); el.blur(); return el.getAttribute('data-editor-value')||el.innerText;})()" % (sel_js, json.dumps(text,ensure_ascii=False)))
for idx,(q,ans,korrekt) in enumerate(fragen):
    if idx >= n_bloecke:
        js("document.querySelector('[data-functional-selector=add-question-button]').click()"); time.sleep(1.5)
        js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Quiz-Typ Frage/.test(b.getAttribute('aria-label')||b.innerText)); if(b) b.click();})()"); time.sleep(2)
        n_bloecke+=1
    else:
        js("document.querySelector('[data-functional-selector=button-wrapper__kahoot-block-%d]').click()" % idx); time.sleep(1.5)
    print(idx+1, tippen("document.querySelector('[data-functional-selector=question-title__input]')", q))
    for k,a in enumerate(ans):
        print("   ", tippen("document.querySelectorAll('[data-functional-selector=question-answer__input]')[%d]" % k, a))
    time.sleep(0.5)
    print("   korrekt:", js("(()=>{const t=document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]'); const b=t[%d]; const s=b.getAttribute('aria-label'); if(!/richtig\\W*\\s*(ist|markiert)/.test(s)) {} b.click(); return document.body.innerText.includes('als die richtige Antwort markiert');})()" % (korrekt-1)))
    time.sleep(0.6)
print("Fertig. Blöcke:", js("document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]').length"))
