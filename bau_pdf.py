"""Setzt fertige JPEG-Seiten zu einem PDF zusammen, ohne sie neu zu kodieren.

Die Bilddaten wandern unveraendert als DCTDecode-Strom ins Dokument. Damit
gibt es genau einen Kodierschritt (den von pdftoppm) und keinen Qualitaets-
verlust durch ein zweites Umrechnen.
"""
import pathlib, struct, sys

def masse(daten):
    """Breite und Hoehe aus den JPEG-Markern lesen."""
    i = 2
    while i < len(daten):
        if daten[i] != 0xFF:
            i += 1; continue
        marke = daten[i + 1]
        if marke in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            hoehe, breite = struct.unpack('>HH', daten[i + 5:i + 9])
            teile = daten[i + 9]
            return breite, hoehe, teile
        i += 2 + struct.unpack('>H', daten[i + 2:i + 4])[0]
    raise ValueError('kein JPEG-Kopf gefunden')

quelle = pathlib.Path(sys.argv[1])
ziel = pathlib.Path(sys.argv[2])
punkt_breite, punkt_hoehe = float(sys.argv[3]), float(sys.argv[4])
seiten = sorted(quelle.glob('*.jpg'))

teile, versatz = [], []
def schreibe(rohtext):
    versatz.append(sum(len(x) for x in teile))
    teile.append(rohtext)

teile.append(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')

anzahl = len(seiten)
# 1 Katalog, 2 Seitenbaum, danach je Seite drei Objekte
seiten_ids = [3 + i * 3 for i in range(anzahl)]
schreibe(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
kinder = ' '.join(f'{i} 0 R' for i in seiten_ids).encode()
schreibe(b'2 0 obj\n<< /Type /Pages /Count %d /Kids [%s] >>\nendobj\n' % (anzahl, kinder))

for n, bild in enumerate(seiten):
    daten = bild.read_bytes()
    breite, hoehe, kanaele = masse(daten)
    p, inhalt, xobj = seiten_ids[n], seiten_ids[n] + 1, seiten_ids[n] + 2
    schreibe(
        b'%d 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] '
        b'/Resources << /XObject << /Im0 %d 0 R >> >> /Contents %d 0 R >>\nendobj\n'
        % (p, punkt_breite, punkt_hoehe, xobj, inhalt))
    strom = b'q %.2f 0 0 %.2f 0 0 cm /Im0 Do Q\n' % (punkt_breite, punkt_hoehe)
    schreibe(b'%d 0 obj\n<< /Length %d >>\nstream\n%s\nendstream\nendobj\n' % (inhalt, len(strom), strom))
    farbe = b'/DeviceRGB' if kanaele == 3 else b'/DeviceGray'
    schreibe(b'%d 0 obj\n<< /Type /XObject /Subtype /Image /Width %d /Height %d '
             b'/ColorSpace %s /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n'
             % (xobj, breite, hoehe, farbe, len(daten)) + daten + b'\nendstream\nendobj\n')

start = sum(len(x) for x in teile)
letzte = 3 + anzahl * 3
xref = [b'xref\n0 %d\n' % letzte, b'0000000000 65535 f \n']
for v in versatz:
    xref.append(b'%010d 00000 n \n' % v)
teile.append(b''.join(xref))
teile.append(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (letzte, start))

ziel.write_bytes(b''.join(teile))
print(f'{anzahl} Seiten, {ziel.stat().st_size/1048576:.1f} MB')
