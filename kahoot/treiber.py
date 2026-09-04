#!/usr/bin/env python3
"""Füllt das Kahoot im Safari-Tab (kahoot.it/creator) Frage für Frage über die
EDGE-Safari-Erweiterung. Liest die Fragen aus kahoot-ki-kompakt.xlsx."""
import json, os, subprocess, time, openpyxl
SK=os.path.expanduser("~/.claude/skills/claude-for-safari/scripts"); M="kahoot.it/creator"
def runner(script,cfg):
    env=dict(os.environ,EDGE_URL_MATCH=M,EDGE_SCRIPT=f"{SK}/{script}",EDGE_CONFIG=json.dumps(cfg,ensure_ascii=False))
    out=subprocess.run(["osascript","-l","JavaScript",f"{SK}/edge_runner.jxa"],env=env,capture_output=True,text=True).stdout.strip()
    try: return json.loads(out)
    except Exception: return {"raw":out}
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    return subprocess.run(["osascript","-e",scr],capture_output=True,text=True).stdout.strip()
def karte():
    d=runner("edge_page_map.js",{"__edgeMapOptions":{"filter":"interactive","max":120}})
    refs={}
    for e in d.get("elemente",[]):
        r,typ,lab=[x.strip() for x in e.split("|",2)]
        if typ=="textbox":
            if lab.startswith("Fragetitel"): refs["titel"]=int(r[4:])
            for n in range(1,5):
                if lab.startswith(f"Antwort {n} "): refs[f"a{n}"]=int(r[4:])
    return refs
ws=openpyxl.load_workbook("kahoot/kahoot-ki-kompakt.xlsx").active
fragen=[(ws.cell(r,2).value,[ws.cell(r,c).value for c in range(3,7)],int(ws.cell(r,8).value)) for r in range(9,19)]
for n,(q,ans,korrekt) in enumerate(fragen,1):
    if n>1:
        print(js("document.querySelector('[data-functional-selector=add-question-button]').click(); 'add'")); time.sleep(1.5)
        print(js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Quiz-Typ Frage/.test(b.getAttribute('aria-label')||b.innerText)); if(!b) return 'kein quiz-knopf'; b.click(); return 'quiz';})()")); time.sleep(2)
    refs=karte(); print(n,refs)
    print(" ",runner("edge_act.js",{"__edgeAction":{"typ":"fuellen","ref":refs["titel"],"wert":q}}).get("status"))
    for k,a in enumerate(ans,1):
        print(" ",a,runner("edge_act.js",{"__edgeAction":{"typ":"fuellen","ref":refs[f"a{k}"],"wert":a}}).get("status"))
    print("  korrekt:",js("(()=>{const t=document.querySelectorAll('[data-functional-selector=question-answer__toggle-button]'); t[%d].click(); return t.length+' toggles, geklickt '+%d;})()" % (korrekt-1,korrekt-1)))
    time.sleep(0.8)
print("Fragen im Kahoot:", js("document.querySelectorAll('[data-functional-selector^=question-block],[data-functional-selector=question-list-item]').length + ' / Titel: ' + (document.querySelector('[data-functional-selector=question-title__input]')||{}).innerText"))
