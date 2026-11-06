"""Genera una página estática por sección y por proyecto a partir de index.html.

Uso: python3 build.py  (después de cada cambio en index.html)
Crea <seccion>/index.html y <seccion>/<proyecto>/index.html, 404.html y sitemap.xml.
"""
import re, os, shutil, html, datetime

SITE = 'https://nicoverdejo.com'
SEC_DESC = {
    'ilustracion': ('Ilustración', 'Novela gráfica, obra individual y croquis urbanos de Nico Verdejo: dibujos sobre arquitectura, política, ternura y duelo.'),
    'investigacion': ('Publicaciones', 'Libros, artículos y novelas gráficas de Nico Verdejo sobre historia de la arquitectura y política en Chile.'),
    'charlas': ('Charlas y conferencias', 'Charlas, conferencias y dibujo en vivo de Nico Verdejo sobre arquitectura, política y dibujo.'),
    'exposiciones': ('Exposiciones', 'Exposiciones de dibujo e ilustración de Nico Verdejo en Chile y Estados Unidos.'),
    'arquitectura': ('Arquitectura', 'Obras y proyectos de arquitectura de Nico Verdejo en Chile y el extranjero.'),
}

src = open('index.html').read()

def text(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def es_only(fragment):
    fragment = re.sub(r'<span class="en">.*?</span>', '', fragment, flags=re.S)
    return text(fragment)

def clip(t, n=158):
    if len(t) <= n: return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:.') + '…'

def attr(v): return html.escape(v, quote=True)

def page(path, title, desc, image, show_id, parent_id):
    s = src
    full = f'{title} · Nico Verdejo'
    url = SITE + path
    s = re.sub(r'<title>.*?</title>', f'<title>{html.escape(full)}</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{attr(desc)}">', s, count=1)
    s = s.replace('<link rel="canonical" href="https://nicoverdejo.com/">', f'<link rel="canonical" href="{url}">', 1)
    s = s.replace('<meta property="og:url" content="https://nicoverdejo.com/">', f'<meta property="og:url" content="{url}">', 1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{attr(full)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{attr(desc)}">', s, count=1)
    s = s.replace('<meta property="og:type" content="profile">', '<meta property="og:type" content="article">', 1)
    if image:
        s = s.replace('<meta property="og:image" content="https://nicoverdejo.com/img/og-image.jpg">', f'<meta property="og:image" content="{SITE}{image}">', 1)
        s = re.sub(r'<meta property="og:image:(width|height|alt)" content="[^"]*">\n', '', s)
    # Static view, the same one the script shows: inner page open, cover closed
    s = s.replace('<div class="cover" id="view-inicio">', '<div class="cover" id="view-inicio" hidden>', 1)
    s = s.replace('<div class="inner" id="view-inner" hidden>', '<div class="inner" id="view-inner">', 1)
    if show_id.startswith('d-'):
        s = re.sub(r'(<article class="detail" id="%s"[^>]*?) hidden>' % re.escape(show_id), r'\1>', s, count=1)
    else:
        s = s.replace(f'<section id="{show_id}" data-path="{path}" hidden>', f'<section id="{show_id}" data-path="{path}">', 1)
    return s

def write(path, content):
    d = path.strip('/')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(content)

# Clean previous build
for k, (name, _) in SEC_DESC.items():
    m = re.search(r'<section id="%s" data-path="(/[^"]+/)"' % k, src)
    shutil.rmtree(m.group(1).strip('/'), ignore_errors=True)

urls = ['/']
for k, (name, desc) in SEC_DESC.items():
    path = re.search(r'<section id="%s" data-path="(/[^"]+/)"' % k, src).group(1)
    write(path, page(path, name, desc, None, k, k))
    urls.append(path)

for m in re.finditer(r'<article class="detail" id="(d-[^"]+)" data-parent="(\w+)" data-path="([^"]+)"[^>]*>(.*?)</article>', src, re.S):
    did, parent, path, body = m.groups()
    title = es_only(re.search(r'<h2 class="detail-title">(.*?)</h2>', body, re.S).group(1))
    paras = [es_only(p) for p in re.findall(r'<div class="detail-text">(.*?)</div>', body, re.S)[0].split('</p>')]
    meta = es_only(re.search(r'<p class="detail-meta">(.*?)</p>', body, re.S).group(1)) if 'detail-meta' in body else ''
    body_txt = next((p for p in paras[1:] if len(p) > 40 and p != meta and p != title), '')
    if did.startswith(('d-croquis','d-plaza-dignidad','d-sa-pa','d-grand-central','d-travesia','d-guggenheim')):
        title = title + ' · Croquis'
    desc = clip(' · '.join(x for x in [title, meta] if x) + ('. ' + body_txt if body_txt else ''))
    img = re.search(r'<img[^>]*src="(/img/[^"]+)"', body)
    write(path, page(path, title, desc, img.group(1) if img else None, did, parent))
    urls.append(path)

# 404: the home page, not indexed
nf = src.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
open('404.html', 'w').write(nf)

today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>' for u in urls]
sm += [f'  <url><loc>{SITE}/cv/Verdejo-Nicolas-CV-2026.pdf</loc></url>', '</urlset>', '']
open('sitemap.xml', 'w').write('\n'.join(sm))
print(len(urls), 'páginas')
