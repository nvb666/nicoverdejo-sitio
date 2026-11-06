"""Crea versiones WebP de las imágenes nuevas y apunta index.html a ellas.

Uso: python3 optimize_images.py && python3 build.py
- img/w/<nombre>.webp: hasta 1800 px, para páginas de proyecto y portada.
- img/w/<nombre>-sm.webp: hasta 900 px, para las tarjetas (img class="thumb").
Los originales quedan en img/ (se usan para compartir en redes).
"""
import os, re
from PIL import Image

s = open('index.html').read()
thumbs = set(re.findall(r'<img class="thumb[^"]*"[^>]*src="/img/(?:w/)?([^"]+?)(?:-sm\.webp)?"', s))

def convert(f, small):
    stem = os.path.splitext(f)[0]
    im = Image.open('img/' + f); im.load()
    mode = 'RGBA' if (im.mode in ('RGBA', 'LA') or 'transparency' in im.info) else 'RGB'
    im = im.convert(mode)
    out = f'img/w/{stem}.webp'
    if not os.path.exists(out):
        big = im.copy(); big.thumbnail((1800, 1800), Image.LANCZOS); big.save(out, 'WEBP', quality=80, method=6)
    out_sm = f'img/w/{stem}-sm.webp'
    if small and not os.path.exists(out_sm):
        sm = im.copy(); sm.thumbnail((900, 900), Image.LANCZOS); sm.save(out_sm, 'WEBP', quality=78, method=6)

def tag(m):
    t = m.group(0)
    def rep(mm):
        f = mm.group(1); stem = os.path.splitext(f)[0]
        small = 'class="thumb' in t
        convert(f, small)
        return f'src="/img/w/{stem}-sm.webp"' if small else f'src="/img/w/{stem}.webp"'
    return re.sub(r'src="/img/([^"/]+\.(?:jpe?g|png))"', rep, t)

os.makedirs('img/w', exist_ok=True)
s = re.sub(r'<img\b[^>]*>', tag, s)
open('index.html', 'w').write(s)
print('listo')
