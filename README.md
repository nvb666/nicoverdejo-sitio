# nicoverdejo.com

Sitio personal de Nico Verdejo: arquitecto, historiador e ilustrador.

Sitio estático: `index.html` y la carpeta `img/`. Se publica en Cloudflare con cada cambio en la rama `main`.

## Páginas por proyecto
`index.html` es la fuente. Después de editarlo, corre `python3 build.py`: genera una página por sección y por proyecto (por ejemplo `/ilustracion/croquis-nueva-york/`), `404.html` y `sitemap.xml`.

## Imágenes e idiomas
- Imagen nueva: guárdala en `img/`, referénciala como `/img/nombre.jpg` en `index.html` y corre `python3 optimize_images.py && python3 build.py`.
- `build.py` genera también la versión en inglés bajo `/en/`.
