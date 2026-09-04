#!/usr/bin/env python3
"""Bild je Frage setzen, mit Wartezeit auf den Editor und Bestätigung über die
Seitenleisten-Vorschau. Blöcke sind nach dem Neuladen 1-indexiert."""
import base64, subprocess, sys, time, pathlib, io, urllib.request, re, json, openpyxl
from PIL import Image
HIER=pathlib.Path(__file__).parent
def js(code):
    scr='tell application "Safari"\nrepeat with w from 1 to (count of windows)\nrepeat with i from 1 to (count of tabs of window w)\nif URL of tab i of window w contains "kahoot.it/creator" then\nreturn do JavaScript "%s" in tab i of window w\nend if\nend repeat\nend repeat\nend tell' % code.replace('\\','\\\\').replace('"','\\"')
    try:
        r=subprocess.run(["osascript","-e",scr],capture_output=True,text=True,timeout=25); return r.stdout.strip() or ("ERR "+r.stderr.strip()[:100])
    except subprocess.TimeoutExpired: return "ERR timeout"
ws=openpyxl.load_workbook(HIER/"kahoot-ki-kompakt.xlsx").active
fragen={n:ws.cell(8+n,2).value for n in range(1,11)}
def ahash(im):
    im=im.convert("L").resize((16,16)); px=list(im.getdata()); m=sum(px)/len(px); return [p>m for p in px]
orig={n:ahash(Image.open(HIER/"bilder"/f"frage-{n:02d}.jpg")) for n in range(1,11)}
def bloecke():
    return json.loads(js("JSON.stringify([...document.querySelectorAll('[data-functional-selector^=sidebar-block__kahoot-block-]')].map(e=>e.getAttribute('data-functional-selector')))"))
def vorschau(sel):
    st=js("(document.querySelector('[data-functional-selector=%s] [data-functional-selector=media-info__image-prev]')||{getAttribute(){return ''}}).getAttribute('style')||''" % sel)
    m=re.search(r'url\("?(https://images-cdn[^"?)]+)',st); return m.group(1) if m else None
def welches(url):
    if not url: return None
    im=Image.open(io.BytesIO(urllib.request.urlopen(url+"?auto=webp&width=400",timeout=20).read()))
    h=ahash(im); d={n:sum(a!=b for a,b in zip(h,orig[n])) for n in orig}; return min(d,key=d.get)
def waehlen(sel, n):
    js("document.querySelector('[data-functional-selector=%s]').click()" % sel)
    for _ in range(30):
        time.sleep(0.5)
        t=js("(document.querySelector('[data-functional-selector=question-title__input]')||{getAttribute(){return ''}}).getAttribute('data-editor-value')||''")
        if t==fragen[n]: return True
    return False
def setzen(sel, n):
    if not waehlen(sel,n): return "Editor zeigt nicht Frage %d" % n
    time.sleep(1)
    alt=vorschau(sel)
    if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')")=="true":
        js("document.querySelector('[data-functional-selector=media-details__media-remove]').click()")
        for _ in range(20):
            time.sleep(0.5)
            if js("!!document.querySelector('[data-functional-selector=media-details__with-media]')")=="false": break
    js("(()=>{const b=[...document.querySelectorAll('button')].find(e=>/^Datei hochladen$/.test(e.innerText.trim())); b&&b.click();})()")
    ok=False
    for _ in range(16):
        time.sleep(0.5)
        if js("!!document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]')")=="true": ok=True; break
    if not ok: return "kein Upload-Dialog"
    b64=base64.b64encode(open(HIER/"bilder"/f"frage-{n:02d}.jpg","rb").read()).decode()
    js("window.__edgeB64=''")
    for k in range(0,len(b64),150000): js("window.__edgeB64+='%s'" % b64[k:k+150000])
    js("(()=>{ const inp=document.querySelector('[data-functional-selector=media-upload-dialog__upload-media-input]'); const bin=atob(window.__edgeB64); const arr=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i); const f=new File([arr],'sparky-frage-%02d.jpg',{type:'image/jpeg'}); const dt=new DataTransfer(); dt.items.add(f); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true})); })()" % n)
    for _ in range(40):
        time.sleep(1)
        neu=vorschau(sel)
        if neu and neu!=alt: break
    time.sleep(1)
    return "zeigt Bild %s" % welches(vorschau(sel))
if __name__=="__main__":
    sels=bloecke(); print("Blöcke:", len(sels))
    ziel=[int(x) for x in sys.argv[1:]] or list(range(1,11))
    for n in ziel:
        print(n, setzen(sels[n-1], n), flush=True)
    stand=[welches(vorschau(s)) for s in sels]
    print("Vorschau je Frage:", stand, "ALLE OK" if stand==list(range(1,11)) else "FEHLER")
    js("document.querySelector('[data-functional-selector=top-bar__save-button]').click()"); time.sleep(6)
    print("Nach Speichern:", js("document.body.innerText.slice(0,70).replace(/\\n+/g,' / ')"))
