#!/usr/bin/env python3
"""Hängt je Frage ein Bild an: Block wählen, „Datei hochladen“ öffnen, Bild in
Häppchen als Base64 in die Seite schieben, per DataTransfer in das File-Input
setzen. Aufruf: python3 kahoot/bilder_hochladen.py [von] [bis]"""
import base64, subprocess, sys, time, pathlib
HIER=pathlib.Path(__file__).parent
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    r=subprocess.run(["osascript","-e",scr],capture_output=True,text=True); return (r.stdout.strip() or ("ERR "+r.stderr.strip()))
von=int(sys.argv[1]) if len(sys.argv)>1 else 1; bis=int(sys.argv[2]) if len(sys.argv)>2 else 10
for n in range(von,bis+1):
    idx=n-1
    js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').click()" % idx); time.sleep(1.5)
    js("(()=>{ if(document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]')) return 'offen'; const b=[...document.querySelectorAll('button')].find(e=>/^Datei hochladen$/.test(e.innerText.trim())); b&&b.click(); return 'geklickt'; })()"); time.sleep(1.5)
    b64=base64.b64encode(open(HIER/"bilder"/f"frage-{n:02d}.jpg","rb").read()).decode()
    js("window.__edgeB64=''")
    for k in range(0,len(b64),150000):
        js("window.__edgeB64+='%s'" % b64[k:k+150000])
    r=js("(()=>{ const inp=document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]'); if(!inp) return 'kein input'; const bin=atob(window.__edgeB64); const arr=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i); const f=new File([arr],'sparky-frage-%02d.jpg',{type:'image/jpeg'}); const dt=new DataTransfer(); dt.items.add(f); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true})); return 'gesetzt '+f.size; })()" % n)
    time.sleep(7)
    st=js("JSON.stringify({dialog:[...document.querySelectorAll('[role=dialog]')].map(d=>d.innerText.slice(0,160).replace(/\\n+/g,' / ')).filter(t=>!/Datenschutz/.test(t)), bild:!!document.querySelector('[data-functional-selector=media-details]'), text:document.body.innerText.slice(0,260).replace(/\\n+/g,' / ')})")
    print(n, r, st[:500])
