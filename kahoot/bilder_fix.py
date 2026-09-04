#!/usr/bin/env python3
"""Robuster Bild-Upload je Frage mit Warten und Hash-Prüfung."""
import base64, subprocess, sys, time, pathlib, io, urllib.request
from PIL import Image
HIER=pathlib.Path(__file__).parent
def js(code, versuche=3):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    for _ in range(versuche):
        r=subprocess.run(["osascript","-e",scr],capture_output=True,text=True)
        if r.stdout.strip(): return r.stdout.strip()
        time.sleep(1)
    return "ERR "+r.stderr.strip()
def ahash(im):
    im=im.convert("L").resize((16,16)); px=list(im.getdata()); m=sum(px)/len(px); return [p>m for p in px]
orig={n:ahash(Image.open(HIER/"bilder"/f"frage-{n:02d}.jpg")) for n in range(1,11)}
def welches(i):
    src=js("(document.querySelector('[data-functional-selector=media-details__media-image] img, [data-functional-selector=media-details__with-media] img')||{}).src||''")
    if not src.startswith("http"): return None
    im=Image.open(io.BytesIO(urllib.request.urlopen(src.split('?')[0]+"?auto=webp&width=400").read()))
    h=ahash(im); return min(orig, key=lambda n: sum(a!=b for a,b in zip(h,orig[n])))
def waehlen(i):
    js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').click()" % i)
    for _ in range(15):
        time.sleep(0.5)
        if "iWizMh" in js("document.querySelector('[data-functional-selector=sidebar-block__kahoot-block-%d]').className" % i): return True
    return False
def hochladen(n):
    i=n-1; waehlen(i); time.sleep(1)
    if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')")=="true":
        js("document.querySelector('[data-functional-selector=media-details__media-remove]').click()"); time.sleep(1.5)
    js("(()=>{const b=[...document.querySelectorAll('button')].find(e=>/^Datei hochladen$/.test(e.innerText.trim())); b&&b.click();})()")
    inp=False
    for _ in range(12):
        time.sleep(0.5)
        if js("!!document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]')")=="true": inp=True; break
    if not inp: return "kein Upload-Dialog"
    b64=base64.b64encode(open(HIER/"bilder"/f"frage-{n:02d}.jpg","rb").read()).decode()
    js("window.__edgeB64=''")
    for k in range(0,len(b64),150000): js("window.__edgeB64+='%s'" % b64[k:k+150000])
    js("(()=>{ const inp=document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]'); const bin=atob(window.__edgeB64); const arr=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i); const f=new File([arr],'sparky-frage-%02d.jpg',{type:'image/jpeg'}); const dt=new DataTransfer(); dt.items.add(f); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true})); return 'gesetzt'; })()" % n)
    for _ in range(30):
        time.sleep(1)
        if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')")=="true": break
    time.sleep(1.5)
    return "zeigt Bild %s" % welches(i)
for n in [int(x) for x in sys.argv[1:]]:
    print(n, hochladen(n))
