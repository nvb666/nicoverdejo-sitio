"""Genera una página estática por sección y por proyecto, en español y en inglés, a partir de index.html.

Uso: python3 build.py  (después de cada cambio en index.html)
Crea <seccion>/<proyecto>/index.html, en/<seccion>/<proyecto>/index.html, en/index.html, 404.html y sitemap.xml.
Las imágenes se sirven en WebP desde img/w/ (ver optimize_images.py).
"""
import re, os, shutil, html, datetime, glob

SITE = 'https://nicoverdejo.com'
SEC = {
    'ilustracion': (('Ilustración', 'Novela gráfica, obra individual y croquis urbanos de Nico Verdejo: dibujos sobre arquitectura, política, ternura y duelo.'),
                    ('Illustration', 'Graphic novels, individual work, and urban sketches by Nico Verdejo: drawings about architecture, politics, tenderness, and grief.')),
    'investigacion': (('Publicaciones', 'Libros, artículos y novelas gráficas de Nico Verdejo sobre historia de la arquitectura y política en Chile.'),
                      ('Publications', 'Books, articles, and graphic stories by Nico Verdejo on architectural history and politics in Chile.')),
    'exposiciones': (('Exposiciones y charlas', 'Exposiciones, charlas y conferencias de Nico Verdejo sobre arquitectura, política y dibujo, en Chile y el extranjero.'),
                     ('Exhibitions and talks', 'Exhibitions, talks, and conference papers by Nico Verdejo on architecture, politics, and drawing, in Chile and abroad.')),
    'sobremi': (('Sobre mí', 'Nico Verdejo (Nicolás Verdejo Bravo): arquitecto, historiador e ilustrador. Formación, investigación, ilustración, arquitectura y docencia.'),
                ('About', 'Nico Verdejo (Nicolás Verdejo Bravo): architectural designer, historian, and illustrator. Education, research, illustration, architecture, and teaching.')),
    'arquitectura': (('Arquitectura', 'Obras y proyectos de arquitectura de Nico Verdejo en Chile y el extranjero.'),
                     ('Architecture', 'Built work and architectural design projects by Nico Verdejo in Chile and abroad.')),
}
HOME = {
    'es': ('Nico Verdejo · Arquitecto, historiador e ilustrador', None),
    'en': ('Nico Verdejo · Architectural designer, historian, and illustrator',
           'Nico Verdejo (Nicolás Verdejo Bravo): Chilean architectural designer, historian, and illustrator. Illustration, urban sketches, graphic novels, publications, and architecture.'),
}
SKETCH = ('d-croquis', 'd-plaza-dignidad', 'd-sa-pa', 'd-grand-central', 'd-travesia', 'd-guggenheim')
SECTION_RE = r'(?:ilustracion|publicaciones|charlas|exposiciones|arquitectura|sobre-mi)'

src = open('index.html').read()

def text(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def only(fragment, lang):
    other = 'en' if lang == 'es' else 'es'
    fragment = re.sub(r'<(span|p) class="%s">.*?</\1>' % other, '', fragment, flags=re.S)
    return text(fragment)

def clip(t, n=158):
    if len(t) <= n: return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:.') + '…'

def attr(v): return html.escape(v, quote=True)

def og_image(webp):
    """Social networks get the original JPG/PNG, not the WebP."""
    stem = os.path.splitext(os.path.basename(webp))[0]
    for ext in ('.jpg', '.png', '.jpeg'):
        if os.path.exists('img/' + stem + ext): return '/img/' + stem + ext
    return None

def page(path, lang, title, desc, image, show_id=None, home=False):
    s = src
    url = SITE + (('/en' + path) if lang == 'en' else path)
    es_url, en_url = SITE + path, SITE + '/en' + path
    full = title if home else f'{title} · Nico Verdejo'
    s = re.sub(r'<title>.*?</title>', f'<title>{html.escape(full)}</title>', s, count=1)
    if desc:
        s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{attr(desc)}">', s, count=1)
        s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{attr(desc)}">', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">\n(<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n)*',
               f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="es" href="{es_url}">\n'
               f'<link rel="alternate" hreflang="en" href="{en_url}">\n<link rel="alternate" hreflang="x-default" href="{es_url}">\n', s, count=1)
    s = s.replace('<meta property="og:url" content="https://nicoverdejo.com/">', f'<meta property="og:url" content="{url}">', 1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{attr(full)}">', s, count=1)
    if not home:
        s = s.replace('<meta property="og:type" content="profile">', '<meta property="og:type" content="article">', 1)
    if image:
        s = s.replace('<meta property="og:image" content="https://nicoverdejo.com/img/og-image.jpg">', f'<meta property="og:image" content="{SITE}{image}">', 1)
        s = re.sub(r'<meta property="og:image:(width|height|alt)" content="[^"]*">\n', '', s)
    if lang == 'en':
        s = s.replace('<html lang="es">', '<html lang="en">', 1)
        s = s.replace('<meta property="og:locale" content="es_CL">\n<meta property="og:locale:alternate" content="en_US">',
                      '<meta property="og:locale" content="en_US">\n<meta property="og:locale:alternate" content="es_CL">', 1)
        s = s.replace('<div id="site" data-lang="es">', '<div id="site" data-lang="en">', 1)
        s = s.replace('data-set="es" aria-pressed="true"', 'data-set="es" aria-pressed="false"').replace('data-set="en" aria-pressed="false"', 'data-set="en" aria-pressed="true"')
        s = re.sub(r'href="(/%s/[^"]*)"' % SECTION_RE, r'href="/en\1"', s)
        s = s.replace('href="/"', 'href="/en/"')
    if not home:
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
    if d: os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html') if d else 'index.html', 'w').write(content)

# Clean previous build
for k in SEC:
    p = re.search(r'<section id="%s" data-path="(/[^"]+/)"' % k, src).group(1)
    shutil.rmtree(p.strip('/'), ignore_errors=True)
shutil.rmtree('en', ignore_errors=True)
for top in set(re.findall(r'data-path="/([^/"]+)/', src)):
    shutil.rmtree(top, ignore_errors=True)

urls = ['/', '/en/']
write('/en/', page('/', 'en', HOME['en'][0], HOME['en'][1], None, home=True))

for k, langs in SEC.items():
    path = re.search(r'<section id="%s" data-path="(/[^"]+/)"' % k, src).group(1)
    for lang, (name, desc) in zip(('es', 'en'), langs):
        write(('/en' if lang == 'en' else '') + path, page(path, lang, name, desc, None, k))
        urls.append(('/en' if lang == 'en' else '') + path)

for m in re.finditer(r'<article class="detail" id="(d-[^"]+)" data-parent="(\w+)" data-path="([^"]+)"[^>]*>(.*?)</article>', src, re.S):
    did, parent, path, body = m.groups()
    img = re.search(r'<img[^>]*src="(/img/[^"]+)"', body)
    image = og_image(img.group(1)) if img else None
    for lang in ('es', 'en'):
        title = only(re.search(r'<h2 class="detail-title">(.*?)</h2>', body, re.S).group(1), lang)
        meta = only(re.search(r'<p class="detail-meta">(.*?)</p>', body, re.S).group(1), lang) if 'detail-meta' in body else ''
        textblock = re.search(r'<div class="detail-text">(.*?)</div>', body, re.S).group(1)
        paras = [text(p) for p in re.findall(r'<p class="%s">(.*?)</p>' % lang, textblock, re.S)]
        body_txt = next((p for p in paras if len(p) > 40 and p != meta and p != title), '')
        desc = clip(' · '.join(x for x in [title, meta] if x) + ('. ' + body_txt if body_txt else ''))
        if did.startswith(SKETCH):
            title += ' · Croquis' if lang == 'es' else ' · Urban sketch'
        out = ('/en' if lang == 'en' else '') + path
        write(out, page(path, lang, title, desc, image, did))
        urls.append(out)

# 404: the home page, not indexed
open('404.html', 'w').write(src.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1))

today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for u in urls:
    base = u[3:] if u.startswith('/en/') else u
    sm.append(f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod>'
              f'<xhtml:link rel="alternate" hreflang="es" href="{SITE}{base}"/>'
              f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}/en{base}"/>'
              f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{base}"/></url>')
sm += [f'  <url><loc>{SITE}/cv/Verdejo-Nicolas-CV-2026.pdf</loc></url>', '</urlset>', '']
open('sitemap.xml', 'w').write('\n'.join(sm))
print(len(urls), 'páginas')
