/* ============================================================================
   EDGE Tools — Kosmos
   Die echte Galaxie aus dem EdgeVision-Wizard, portiert: Spiralarme in
   three.js, drei Sternschichten und ein Milchstrassenband. Der Wizard bindet
   three.js lokal ein (675 KB), hier kommt es vom CDN und wird erst geladen,
   nachdem die Karten stehen: die Seite ist also sofort bedienbar, der Himmel
   blendet sich dazu.

   Faellt WebGL aus (alte Grafiktreiber, abgeschaltete Beschleunigung, zu viele
   offene Kontexte), uebernimmt das leichte 2D-Feld am Ende der Datei. Eine
   Startseite ohne Hintergrund waere kein Drama, ein schwarzes Rechteck schon.
   ========================================================================== */
/* Aus dem eigenen Haus, nicht vom CDN: so geht bei keinem Seitenaufruf
   eine IP-Adresse an einen Dritten. Die Datei liegt einmal in edge-tools
   und wird von allen Werkzeugen derselben Domain mitbenutzt, der Browser
   laedt sie also fuer die ganze Familie nur einmal. */
const THREE_CDN = new URL('vendor/three.module.min.js', location.href).href;

/* Sternfarben und ihre Gewichtung, beides aus dem Wizard uebernommen. */
const STERNFARBEN = ['#FFFFFF', '#9CC5FF', '#009FF4', '#00E2E2', '#C15DE6'];
const STERNGEWICHT = [0.42, 0.26, 0.14, 0.11, 0.07];

const ruhig = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* Nachvollziehbar machen, welcher Weg genommen wurde. Ohne diesen Marker
   laesst sich das von aussen nicht messen: ein getContext('webgl2') von der
   Konsole aus ERZEUGT den Kontext, wenn noch keiner da ist, und liefert damit
   ein Ergebnis, das man selbst verursacht hat. */
window.EDGE_KOSMOS = { weg: 'startet', fehler: null };

(async function raum() {
  const canvas = document.getElementById('kosmos');
  if (!canvas) { window.EDGE_KOSMOS.weg = 'kein canvas'; return; }
  try {
    const THREE = await import(THREE_CDN);
    if (galaxieStarten(THREE, canvas)) {
      window.EDGE_KOSMOS.weg = 'galaxie';
    } else {
      window.EDGE_KOSMOS.weg = 'feld (WebGL nicht verfuegbar)';
      feldStarten(canvas);
    }
  } catch (e) {
    /* CDN nicht erreichbar oder Modul kaputt: der Himmel ist Zierde, kein
       Grund, die Seite scheitern zu lassen. */
    window.EDGE_KOSMOS.weg = 'feld (three nicht ladbar)';
    window.EDGE_KOSMOS.fehler = String(e && e.message || e).slice(0, 200);
    feldStarten(canvas);
  }
})();

/* ---------------------------------------------------------------------------
   Galaxie (three.js)
   Gibt false zurueck, wenn kein WebGL-Kontext zustande kommt.
   ------------------------------------------------------------------------- */
function galaxieStarten(THREE, canvas) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'high-performance' });
  } catch (e) {
    window.EDGE_KOSMOS.fehler = String(e && e.message || e).slice(0, 200);
    return false;
  }
  if (!renderer) return false;

  const mobil = matchMedia('(max-width: 900px)').matches;
  const N = mobil ? 15000 : 42000;
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.75));

  const szene = new THREE.Scene();
  const kamera = new THREE.PerspectiveCamera(46, 1, 0.1, 300);
  kamera.position.set(0, 11, 19);
  kamera.lookAt(0, 0, 0);

  /* Ein weicher Punkt als Textur. Ohne den waeren die Sterne harte Quadrate. */
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255,255,255,1)');
  grad.addColorStop(0.3, 'rgba(255,255,255,0.45)');
  grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  const sprite = new THREE.CanvasTexture(c);

  /* --- Spiralarme --- */
  const basis = new Float32Array(N * 3);
  const farben = new Float32Array(N * 3);
  const cKern = new THREE.Color('#FFFFFF'), cEis = new THREE.Color('#9CC5FF'),
        cBlau = new THREE.Color('#009FF4'), cCyan = new THREE.Color('#00E2E2'),
        cPurple = new THREE.Color('#C15DE6');
  const ARME = 3, TWIST = 2.6, R0 = 9.5;
  for (let i = 0; i < N; i++) {
    /* Hoch 0.55 zieht die Punkte zur Mitte: so entsteht der helle Kern. */
    const t = Math.pow(Math.random(), 0.55);
    const r = t * R0;
    const arm = (i % ARME) / ARME * Math.PI * 2;
    const streu = (Math.random() - 0.5) * (0.55 - 0.35 * t);
    const winkel = arm + r * TWIST / R0 * Math.PI + streu * Math.PI;
    const dicke = (1 - t) * 1.4 + 0.1;
    basis[i * 3]     = Math.cos(winkel) * r;
    basis[i * 3 + 1] = (Math.random() - 0.5) * dicke;
    basis[i * 3 + 2] = Math.sin(winkel) * r;
    const mix = Math.random();
    let farbe;
    if (t < 0.14) farbe = cKern.clone();
    else if (t > 0.62) farbe = (mix < 0.45 ? cPurple : mix < 0.75 ? cBlau : cEis).clone();
    else farbe = (mix < 0.5 ? cEis : mix < 0.8 ? cBlau : cCyan).clone();
    farbe.multiplyScalar(t < 0.14 ? 1.0 : 0.62 + Math.random() * 0.4);
    farben[i * 3] = farbe.r; farben[i * 3 + 1] = farbe.g; farben[i * 3 + 2] = farbe.b;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(basis, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(farben, 3));
  const mat = new THREE.PointsMaterial({
    size: mobil ? 0.066 : 0.054, map: sprite, vertexColors: true, transparent: true,
    opacity: 0.72, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
  });
  const galaxie = new THREE.Points(geo, mat);
  galaxie.position.set(mobil ? 0 : 1.4, -0.4, 0);
  galaxie.rotation.x = 0.30;
  szene.add(galaxie);

  /* --- Sternschichten im Hintergrund --- */
  function schicht(anzahl, minR, maxR, groesse, opazitaet, farbe) {
    const arr = new Float32Array(anzahl * 3);
    for (let i = 0; i < anzahl; i++) {
      const r = minR + Math.random() * (maxR - minR);
      const a = Math.random() * Math.PI * 2, b = Math.acos(2 * Math.random() - 1);
      arr[i * 3]     = r * Math.sin(b) * Math.cos(a);
      arr[i * 3 + 1] = r * Math.cos(b) * 0.6;
      arr[i * 3 + 2] = r * Math.sin(b) * Math.sin(a) - 20;
    }
    const g2 = new THREE.BufferGeometry();
    g2.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const m2 = new THREE.PointsMaterial({ size: groesse, map: sprite, transparent: true,
      opacity: opazitaet, color: farbe, depthWrite: false, blending: THREE.AdditiveBlending });
    const p = new THREE.Points(g2, m2);
    szene.add(p);
    return p;
  }
  schicht(mobil ? 1400 : 3200, 32, 82, 0.095, 0.38, 0xCFDCFF);
  schicht(mobil ? 120 : 280, 28, 72, 0.21, 0.50, 0xEAF2FF);
  schicht(mobil ? 2500 : 6500, 30, 92, 0.055, 0.20, 0xAEBFE8);

  /* --- Milchstrassenband --- */
  (function band() {
    const B = mobil ? 2200 : 5200, arr = new Float32Array(B * 3);
    for (let i = 0; i < B; i++) {
      const u = (Math.random() - 0.5) * 2;
      /* Drei addierte Zufallszahlen ergeben eine Glockenkurve: das Band ist
         in der Mitte dicht und franst nach aussen aus. */
      const gauss = (Math.random() + Math.random() + Math.random() - 1.5) / 1.5;
      arr[i * 3]     = u * 95;
      arr[i * 3 + 1] = gauss * 7;
      arr[i * 3 + 2] = -55 + gauss * 12 + (Math.random() - 0.5) * 8;
    }
    const g2 = new THREE.BufferGeometry();
    g2.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const m2 = new THREE.PointsMaterial({ size: 0.075, map: sprite, transparent: true,
      opacity: 0.15, color: 0x9FB4E8, depthWrite: false, blending: THREE.AdditiveBlending });
    const p = new THREE.Points(g2, m2);
    p.rotation.z = -0.42;
    szene.add(p);
  })();

  /* --- Groesse, Maus, Schleife --- */
  function anpassen() {
    renderer.setSize(innerWidth, innerHeight, false);
    kamera.aspect = innerWidth / innerHeight;
    kamera.updateProjectionMatrix();
  }
  anpassen();
  let umbau;
  addEventListener('resize', () => { clearTimeout(umbau); umbau = setTimeout(() => { anpassen(); renderer.render(szene, kamera); }, 180); });

  let mausX = 0, mausY = 0, zielX = 0, zielY = 0;
  addEventListener('pointermove', e => {
    zielX = (e.clientX / innerWidth - 0.5) * 2;
    zielY = (e.clientY / innerHeight - 0.5) * 2;
  }, { passive: true });

  /* Die Galaxie dreht sich langsam um ihre eigene Achse, die Kamera folgt der
     Maus traege. Beides bewusst dezent: der Himmel ist Hintergrund, keine
     Attraktion, ueber der man die Werkzeuge vergisst. */
  function malen() {
    mausX += (zielX - mausX) * 0.035;
    mausY += (zielY - mausY) * 0.035;
    galaxie.rotation.y += 0.00035;
    kamera.position.x = mausX * 1.6;
    kamera.position.y = 11 - mausY * 1.1;
    kamera.lookAt(0, 0, 0);
    renderer.render(szene, kamera);
    if (!ruhig) requestAnimationFrame(malen);
  }
  malen();

  /* Beim Verlassen der Seite den Kontext freigeben: Browser erlauben nur eine
     begrenzte Zahl gleichzeitiger WebGL-Kontexte. */
  addEventListener('pagehide', () => { try { renderer.dispose(); } catch (e) {} });
  return true;
}

/* ---------------------------------------------------------------------------
   Rueckfall: 2D-Sternenfeld
   Etwa 500 Punkte, gleiche Farben, Tiefenstaffelung, langsame Drehung.
   Kostet keine Bibliothek und laeuft ueberall.
   ------------------------------------------------------------------------- */
function feldStarten(canvas) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  let breite = 0, hoehe = 0, dpr = 1, punkte = [];
  let mausX = 0, mausY = 0, zielX = 0, zielY = 0;

  const farbeZiehen = () => {
    let r = Math.random(), summe = 0;
    for (let i = 0; i < STERNFARBEN.length; i++) { summe += STERNGEWICHT[i]; if (r <= summe) return STERNFARBEN[i]; }
    return STERNFARBEN[0];
  };

  function aufbauen() {
    dpr = Math.min(devicePixelRatio || 1, 1.75);
    breite = canvas.width = Math.floor(innerWidth * dpr);
    hoehe = canvas.height = Math.floor(innerHeight * dpr);
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
    const anzahl = innerWidth < 900 ? 260 : 520;
    const mitteX = breite / 2, mitteY = hoehe * 0.42;
    punkte = [];
    for (let i = 0; i < anzahl; i++) {
      const t = Math.sqrt(Math.random());
      const tiefe = 0.25 + Math.random() * 0.75;
      punkte.push({
        winkel: Math.random() * Math.PI * 2,
        radius: t * Math.max(breite, hoehe) * 0.78,
        tiefe, mitteX, mitteY,
        groesse: (0.5 + Math.random() * 1.5) * tiefe * dpr,
        farbe: farbeZiehen(),
        deckkraft: (0.30 + Math.random() * 0.55) * tiefe,
        flackern: Math.random() * Math.PI * 2,
        tempo: (0.00006 + Math.random() * 0.00010) * (0.4 + tiefe),
      });
    }
  }

  function zeichnen(zeit) {
    ctx.clearRect(0, 0, breite, hoehe);
    mausX += (zielX - mausX) * 0.04;
    mausY += (zielY - mausY) * 0.04;
    for (const p of punkte) {
      if (!ruhig) p.winkel += p.tempo;
      const x = p.mitteX + Math.cos(p.winkel) * p.radius + mausX * p.tiefe * 26 * dpr;
      const y = p.mitteY + Math.sin(p.winkel) * p.radius * 0.55 + mausY * p.tiefe * 18 * dpr;
      if (x < -20 || x > breite + 20 || y < -20 || y > hoehe + 20) continue;
      const puls = ruhig ? 1 : 0.72 + 0.28 * Math.sin(zeit * 0.0012 + p.flackern);
      ctx.globalAlpha = p.deckkraft * puls;
      ctx.fillStyle = p.farbe;
      ctx.beginPath(); ctx.arc(x, y, p.groesse, 0, 6.283); ctx.fill();
      if (p.groesse > 1.5 * dpr) {
        ctx.globalAlpha = p.deckkraft * puls * 0.16;
        ctx.beginPath(); ctx.arc(x, y, p.groesse * 4, 0, 6.283); ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
    if (!ruhig) requestAnimationFrame(zeichnen);
  }

  addEventListener('pointermove', e => {
    zielX = (e.clientX / innerWidth - 0.5) * 2;
    zielY = (e.clientY / innerHeight - 0.5) * 2;
  }, { passive: true });
  let umbau;
  addEventListener('resize', () => { clearTimeout(umbau); umbau = setTimeout(() => { aufbauen(); if (ruhig) zeichnen(0); }, 200); });

  aufbauen();
  zeichnen(0);
}
