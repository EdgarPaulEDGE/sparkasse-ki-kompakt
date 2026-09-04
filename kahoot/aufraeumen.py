#!/usr/bin/env python3
"""Importierte Fragen übernehmen, die zehn leeren Blöcke löschen, speichern."""
import subprocess, time, json
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    return subprocess.run(["osascript","-e",scr],capture_output=True,text=True).stdout.strip()
def bloecke(): return int(float(js("document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]').length") or 0))
print("hinzufügen:", js("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>/Fragen hinzufügen/.test(b.innerText)); if(!b) return 'kein Knopf'; b.click(); return 'ok';})()")); time.sleep(3)
print("Blöcke nach Import:", bloecke())
# Titel je Block: leere Blöcke finden (Seitenleiste zeigt 'Frage' als Platzhalter)
titel=json.loads(js("JSON.stringify([...document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]')].map(e=>e.innerText.split('\\n')[0]))"))
print("Seitenleiste:", titel)
# leere Blöcke von hinten nach vorn löschen, damit die Indizes stabil bleiben
for idx in range(len(titel)-1,-1,-1):
    if titel[idx].strip()=="Frage":
        js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').click()" % idx); time.sleep(0.8)
        js("(()=>{const w=document.querySelector('[data-functional-selector=button-wrapper__kahoot-block-%d]'); const b=w.querySelector('[data-functional-selector=sidebar__remove]')||w.parentElement.querySelector('[data-functional-selector=sidebar__remove]'); b&&b.click();})()" % idx); time.sleep(0.8)
        js("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>/^(Löschen|Entfernen|OK)$/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(0.8)
print("Blöcke nach Löschen:", bloecke())
print("Seitenleiste:", js("JSON.stringify([...document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]')].map(e=>e.innerText.split('\\n')[0]))"))
js("document.querySelector('[data-functional-selector=top-bar__save-button]').click()"); time.sleep(5)
print("Nach Speichern:", js("location.href + ' :: ' + document.body.innerText.slice(0,300).replace(/\\n+/g,' / ')"))
