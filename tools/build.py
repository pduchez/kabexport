#!/usr/bin/env python3
"""Genera el sitio estático de KAB EXPORT.

Cada página vive en content/<idioma>/<clave>.html. La primera línea es un
comentario con metadatos en JSON:

    <!--meta {"title": "...", "description": "..."} -->

Este script envuelve cada fragmento con la cabecera, el menú y el pie de
página, y escribe el resultado en docs/ (la carpeta que se publica), junto
con sitemap.xml.

Uso:  python3 tools/build.py
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
DOMAIN = "https://kabexport.com"
EMAIL = "info@kabexport.com"

# clave: (ruta en español, ruta en inglés)
PAGES = {
    "home": ("/", "/en/"),
    "products": ("/productos/", "/en/products/"),
    "cardamom": ("/productos/cardamomo/", "/en/products/cardamom/"),
    "honey": ("/productos/miel/", "/en/products/honey/"),
    "vanilla": ("/productos/vainilla/", "/en/products/vanilla/"),
    "about": ("/nosotros/", "/en/about/"),
    "sustainability": ("/sostenibilidad/", "/en/sustainability/"),
    "quality": ("/calidad/", "/en/quality/"),
    "export": ("/exportacion/", "/en/export/"),
    "contact": ("/contacto/", "/en/contact/"),
    "thanks": ("/gracias/", "/en/thanks/"),
}
NO_INDEX = {"thanks"}
PRODUCT_KEYS = ("cardamom", "honey", "vanilla")

T = {
    "es": {
        "nav": [("products", "Productos"), ("about", "Nosotros"), ("sustainability", "Sostenibilidad"),
                ("quality", "Calidad"), ("export", "Exportación"), ("contact", "Contacto")],
        "names": {"home": "Inicio", "products": "Productos", "cardamom": "Cardamomo", "honey": "Miel",
                  "vanilla": "Vainilla", "about": "Nosotros", "sustainability": "Sostenibilidad",
                  "quality": "Calidad", "export": "Exportación", "contact": "Contacto", "thanks": "Gracias"},
        "skip": "Saltar al contenido",
        "menu": "Abrir menú",
        "switch": ("EN", "English version"),
        "home_label": "KAB EXPORT, inicio",
        "foot_about": "Cardamomo, miel y vainilla orgánicos de Centroamérica para importadores y la industria alimentaria en Europa y Norteamérica.",
        "foot_products": "Productos",
        "foot_company": "Empresa",
        "foot_contact": "Contacto",
        "foot_quote": "Solicitar cotización",
        "rights": "Todos los derechos reservados.",
        "origin": "Hecho en Centroamérica.",
        "locale": "es_ES",
        "org_desc": "Exportador de cardamomo, miel y vainilla orgánicos de Centroamérica.",
    },
    "en": {
        "nav": [("products", "Products"), ("about", "About"), ("sustainability", "Sustainability"),
                ("quality", "Quality"), ("export", "Export"), ("contact", "Contact")],
        "names": {"home": "Home", "products": "Products", "cardamom": "Cardamom", "honey": "Honey",
                  "vanilla": "Vanilla", "about": "About", "sustainability": "Sustainability",
                  "quality": "Quality", "export": "Export", "contact": "Contact", "thanks": "Thank you"},
        "skip": "Skip to content",
        "menu": "Open menu",
        "switch": ("ES", "Versión en español"),
        "home_label": "KAB EXPORT, home",
        "foot_about": "Organic cardamom, honey and vanilla from Central America for importers and food manufacturers in Europe and North America.",
        "foot_products": "Products",
        "foot_company": "Company",
        "foot_contact": "Contact",
        "foot_quote": "Request a quote",
        "rights": "All rights reserved.",
        "origin": "Made in Central America.",
        "locale": "en_US",
        "org_desc": "Exporter of organic cardamom, honey and vanilla from Central America.",
    },
}

MARK = ('<svg class="mark" viewBox="0 0 64 64" aria-hidden="true">'
        '<path d="M32 6 54.5 19v26L32 58 9.5 45V19Z" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"/>'
        '<path d="M24 19v26M24 33 37 20" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M28.5 28.5 40 41q5 5 15 4" fill="none" stroke="var(--honey)" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="59" cy="45" r="3" fill="var(--honey)"/></svg>')
LOCKUP = MARK + '<span class="lk-text"><b>KAB</b><small>EXPORT</small></span>'

ICONS = {
    "cardamom": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
                 '<path d="M14 46C10 30 24 12 44 12c4 16-10 36-30 34Z" fill="currentColor" fill-opacity=".14"/>'
                 '<path d="M18 42 40 16M22 38c2-6 8-14 14-18M26 42c6-4 12-12 14-20"/><path d="M44 12c2-3 5-5 8-6"/></g></svg>'),
    "honey": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round">'
              '<path d="M32 6 52 17.5v23L32 52 12 40.5v-23Z"/><path d="M32 18 42 23.8v11.5L32 41l-10-5.7V23.8Z" fill="var(--honey)" stroke="none"/>'
              '<path d="M32 52v4a3 3 0 0 0 6 0v-7.5"/></g></svg>'),
    "vanilla": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
                '<path d="M12 56C24 44 36 30 46 14"/><path d="M17 56C29 44 40 31 49 16"/>'
                '<g transform="translate(48 13)" fill="currentColor" fill-opacity=".14"><ellipse rx="4" ry="9" transform="rotate(-20)"/>'
                '<ellipse rx="4" ry="9" transform="rotate(50)"/><ellipse rx="4" ry="9" transform="rotate(120)"/></g></g>'
                '<circle cx="48" cy="13" r="2.6" fill="var(--honey)"/></svg>'),
}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">')


def path_of(key, lang):
    return PAGES[key][0 if lang == "es" else 1]


def read_page(lang, key):
    raw = (CONTENT / lang / f"{key}.html").read_text(encoding="utf-8")
    m = re.match(r"\s*<!--meta\s+(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        raise SystemExit(f"Falta el comentario meta en content/{lang}/{key}.html")
    meta = json.loads(m.group(1))
    body = raw[m.end():]
    for k, svg in ICONS.items():
        body = body.replace("{{icon:%s}}" % k, svg)
    body = body.replace("{{email}}", EMAIL)
    for k in PAGES:
        body = body.replace("{{url:%s}}" % k, path_of(k, lang))
    return meta, body


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def json_ld(key, lang, meta):
    t = T[lang]
    org = {
        "@type": "Organization",
        "@id": DOMAIN + "/#org",
        "name": "KAB EXPORT",
        "url": DOMAIN + "/",
        "logo": DOMAIN + "/assets/img/logo.png",
        "email": EMAIL,
        "description": t["org_desc"],
        "areaServed": ["DE", "ES", "US", "MX", "GT", "SV", "NI", "HN", "CR", "PA", "BZ"],
    }
    graph = [org]
    if key == "home":
        graph.append({"@type": "WebSite", "@id": DOMAIN + "/#web", "url": DOMAIN + "/", "name": "KAB EXPORT",
                      "inLanguage": lang, "publisher": {"@id": DOMAIN + "/#org"}})
    else:
        crumbs = [("home", path_of("home", lang))]
        if key in PRODUCT_KEYS:
            crumbs.append(("products", path_of("products", lang)))
        crumbs.append((key, path_of(key, lang)))
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t["names"][k], "item": DOMAIN + p}
            for i, (k, p) in enumerate(crumbs)]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def crumbs_html(key, lang):
    if key == "home":
        return ""
    t = T[lang]
    parts = [f'<a href="{path_of("home", lang)}">{t["names"]["home"]}</a>']
    if key in PRODUCT_KEYS:
        parts.append(f'<a href="{path_of("products", lang)}">{t["names"]["products"]}</a>')
    parts.append(f'<span aria-current="page">{t["names"][key]}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(parts) + "</nav>"


def render(key, lang, meta, body):
    t = T[lang]
    other = "en" if lang == "es" else "es"
    url = DOMAIN + path_of(key, lang)
    active = "products" if key in PRODUCT_KEYS else key
    nav = "".join(
        f'<li><a href="{path_of(k, lang)}"{" aria-current=\"page\"" if k == active else ""}>{label}</a></li>'
        for k, label in t["nav"])
    robots = '<meta name="robots" content="noindex">\n' if key in NO_INDEX else ""
    body = body.replace("{{crumbs}}", crumbs_html(key, lang))
    prod_links = "".join(f'<li><a href="{path_of(k, lang)}">{t["names"][k]}</a></li>' for k in PRODUCT_KEYS)
    company_links = "".join(f'<li><a href="{path_of(k, lang)}">{t["names"][k]}</a></li>'
                            for k in ("about", "sustainability", "quality", "export"))
    year = date.today().year
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["description"])}">
{robots}<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es" href="{DOMAIN}{path_of(key, "es")}">
<link rel="alternate" hreflang="en" href="{DOMAIN}{path_of(key, "en")}">
<link rel="alternate" hreflang="x-default" href="{DOMAIN}{path_of(key, "es")}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="KAB EXPORT">
<meta property="og:title" content="{esc(meta["title"])}">
<meta property="og:description" content="{esc(meta["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{t["locale"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1F3B2D">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/assets/css/styles.css">
<script type="application/ld+json">{json_ld(key, lang, meta)}</script>
</head>
<body class="page-{key}">
<a class="skip" href="#main">{t["skip"]}</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="lockup" href="{path_of("home", lang)}" aria-label="{t["home_label"]}">{LOCKUP}</a>
    <ul class="nav-links" id="nav-links">{nav}</ul>
    <div class="nav-right">
      <a class="lang" href="{path_of(key, other)}" hreflang="{other}" lang="{other}" title="{t["switch"][1]}">{t["switch"][0]}</a>
      <button class="menu-btn" type="button" aria-controls="nav-links" aria-expanded="false" aria-label="{t["menu"]}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
    </div>
  </div>
</header>
<main id="main">
{body.strip()}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="lockup" href="{path_of("home", lang)}" aria-label="{t["home_label"]}">{LOCKUP}</a>
        <p>{t["foot_about"]}</p>
      </div>
      <div><h2>{t["foot_products"]}</h2><ul>{prod_links}</ul></div>
      <div><h2>{t["foot_company"]}</h2><ul>{company_links}</ul></div>
      <div><h2>{t["foot_contact"]}</h2><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="{path_of("contact", lang)}">{t["foot_quote"]}</a></li></ul></div>
    </div>
    <div class="foot-bottom"><span>© {year} KAB EXPORT. {t["rights"]}</span><span>{t["origin"]}</span></div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def write(path, html):
    dest = OUT / path.lstrip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def sitemap():
    today = date.today().isoformat()
    rows = []
    for key, (es, en) in PAGES.items():
        if key in NO_INDEX:
            continue
        for p in (es, en):
            rows.append(
                f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod>"
                f'<xhtml:link rel="alternate" hreflang="es" href="{DOMAIN}{es}"/>'
                f'<xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{en}"/></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main():
    count = 0
    for lang in ("es", "en"):
        for key in PAGES:
            meta, body = read_page(lang, key)
            write(path_of(key, lang), render(key, lang, meta, body))
            count += 1
    # 404: usa el contenido en español con enlace al inglés
    meta, body = read_page("es", "404")
    page = render("home", "es", meta, body).replace('<link rel="canonical" href="https://kabexport.com/">', '<meta name="robots" content="noindex">')
    (OUT / "404.html").write_text(page, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print(f"{count} páginas + 404 + sitemap.xml generados en {OUT}")


if __name__ == "__main__":
    main()
