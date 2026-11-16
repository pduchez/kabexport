#!/usr/bin/env python3
"""Genera el sitio estático de KAB EXPORT.

Cada página vive en content/<idioma>/<clave>.html. La primera línea es un
comentario con metadatos en JSON:

    <!--meta {"title": "...", "description": "..."} -->

Este script envuelve cada fragmento con la cabecera, el menú y el pie de
página, y escribe el resultado en docs/ (la carpeta que se publica), junto
con sitemap.xml.

Uso:  python3 tools/build.py

El inglés va en la raíz (/) y el español en /es/.
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

# El inglés es el idioma principal: vive en la raíz. El español vive en /es/.
# clave: (ruta en español, ruta en inglés)
PAGES = {
    "home": ("/es/", "/"),
    "products": ("/es/productos/", "/products/"),
    "cardamom": ("/es/productos/cardamomo/", "/products/cardamom/"),
    "allspice": ("/es/productos/pimienta-gorda/", "/products/allspice/"),
    "pepper": ("/es/productos/pimienta-negra/", "/products/black-pepper/"),
    "clove": ("/es/productos/clavo/", "/products/clove/"),
    "cinnamon": ("/es/productos/canela/", "/products/cinnamon/"),
    "cacao": ("/es/productos/cacao/", "/products/cacao/"),
    "honey": ("/es/productos/miel/", "/products/honey/"),
    "vanilla": ("/es/productos/vainilla/", "/products/vanilla/"),
    "producers": ("/es/productores/", "/producers/"),
    "about": ("/es/nosotros/", "/about/"),
    "sustainability": ("/es/sostenibilidad/", "/sustainability/"),
    "quality": ("/es/calidad/", "/quality/"),
    "export": ("/es/exportacion/", "/export/"),
    "contact": ("/es/contacto/", "/contact/"),
    "thanks": ("/es/gracias/", "/thanks/"),
    "founder": ("/es/pedro-pablo-duchez-meyer/", "/pedro-pablo-duchez-meyer/"),
}

# Perfil del director: datos para que los buscadores relacionen su nombre con esta página.
PERSON = {
    "name": "Pedro Pablo Duchez Meyer",
    "alternateName": ["Pedro Pablo Duchez", "Pedro Duchez", "Pedro Duchez Meyer", "P. P. Duchez Meyer"],
    "image": "/assets/img/pedro-pablo-duchez-meyer.jpg",
    "sameAs": [
        "https://www.linkedin.com/in/pedropabloduchez",
        "https://www.da-consortium.com/pedro-pablo-duchez-meyer",
        "https://destinopropiedades.com/quienes-somos",
    ],
}
NO_INDEX = {"thanks"}
PRODUCT_KEYS = ("cardamom", "allspice", "pepper", "clove", "cinnamon", "cacao", "honey", "vanilla")
SOON_KEYS = ("honey", "vanilla")  # se muestran como "Próximamente"

# Direcciones de la versión anterior del sitio (español en la raíz, inglés en /en/).
# Se redirigen a su página nueva para no romper enlaces ni posiciones en Google.
LEGACY = {
    "/productos/": "products", "/productos/cardamomo/": "cardamom", "/productos/miel/": "honey",
    "/productos/vainilla/": "vanilla", "/nosotros/": "about", "/sostenibilidad/": "sustainability",
    "/calidad/": "quality", "/exportacion/": "export", "/contacto/": "contact", "/gracias/": "thanks",
}
LEGACY_EN = {
    "/en/": "home", "/en/products/": "products", "/en/products/cardamom/": "cardamom",
    "/en/products/honey/": "honey", "/en/products/vanilla/": "vanilla", "/en/about/": "about",
    "/en/sustainability/": "sustainability", "/en/quality/": "quality", "/en/export/": "export",
    "/en/contact/": "contact", "/en/thanks/": "thanks",
}

T = {
    "es": {
        "nav": [("products", "Productos"), ("producers", "Productores"), ("sustainability", "Sostenibilidad"),
                ("about", "Nosotros"), ("export", "Exportación"), ("contact", "Contacto")],
        "names": {"home": "Inicio", "products": "Productos", "cardamom": "Cardamomo", "allspice": "Pimienta gorda",
                  "pepper": "Pimienta negra", "clove": "Clavo", "cinnamon": "Canela", "cacao": "Cacao",
                  "honey": "Miel", "vanilla": "Vainilla", "producers": "Productores", "about": "Nosotros",
                  "sustainability": "Sostenibilidad", "quality": "Calidad", "export": "Exportación",
                  "contact": "Contacto", "thanks": "Gracias",
                  "founder": "Pedro Pablo Duchez Meyer"},
        "soon": "Próximamente",
        "skip": "Saltar al contenido",
        "menu": "Abrir menú",
        "switch": ("EN", "English version"),
        "home_label": "KAB EXPORT, inicio",
        "foot_about": "Especias y cacao de comunidades productoras de Alta Verapaz, Guatemala, para compradores en Canadá y Estados Unidos.",
        "foot_products": "Productos",
        "foot_company": "Empresa",
        "foot_contact": "Contacto",
        "foot_quote": "Solicitar cotización",
        "rights": "Todos los derechos reservados.",
        "origin": "Desde Alta Verapaz, Guatemala.",
        "locale": "es_GT",
        "org_desc": "Exportador guatemalteco de especias y cacao de comunidades productoras de Alta Verapaz.",
    },
    "en": {
        "nav": [("products", "Products"), ("producers", "Producers"), ("sustainability", "Sustainability"),
                ("about", "About"), ("export", "Export"), ("contact", "Contact")],
        "names": {"home": "Home", "products": "Products", "cardamom": "Cardamom", "allspice": "Allspice",
                  "pepper": "Black pepper", "clove": "Clove", "cinnamon": "Cinnamon", "cacao": "Cacao",
                  "honey": "Honey", "vanilla": "Vanilla", "producers": "Producers", "about": "About",
                  "sustainability": "Sustainability", "quality": "Quality", "export": "Export",
                  "contact": "Contact", "thanks": "Thank you",
                  "founder": "Pedro Pablo Duchez Meyer"},
        "soon": "Coming soon",
        "skip": "Skip to content",
        "menu": "Open menu",
        "switch": ("ES", "Versión en español"),
        "home_label": "KAB EXPORT, home",
        "foot_about": "Spices and cacao from producer communities in Alta Verapaz, Guatemala, for buyers in Canada and the United States.",
        "foot_products": "Products",
        "foot_company": "Company",
        "foot_contact": "Contact",
        "foot_quote": "Request a quote",
        "rights": "All rights reserved.",
        "origin": "From Alta Verapaz, Guatemala.",
        "locale": "en_US",
        "org_desc": "Guatemalan exporter of spices and cacao from producer communities in Alta Verapaz.",
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
    "allspice": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
                 '<path d="M34 8c-2 8-4 14-10 20M34 8c4 6 6 12 6 18M34 8c8 4 12 8 16 14"/>'
                 '<path d="M10 20c6-8 16-10 22-12-4 8-12 14-22 12Z" fill="currentColor" fill-opacity=".14"/>'
                 '<g fill="currentColor" fill-opacity=".14"><circle cx="22" cy="36" r="7"/><circle cx="38" cy="38" r="7"/><circle cx="30" cy="50" r="7"/></g>'
                 '</g><circle cx="51" cy="28" r="6" fill="var(--honey)"/></svg>'),
    "pepper": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
               '<path d="M20 6c2 16 6 34 18 52"/>'
               '<path d="M22 14c8-6 20-6 30 0-8 8-20 8-30 0Z" fill="currentColor" fill-opacity=".14"/>'
               '<g fill="currentColor" fill-opacity=".14"><circle cx="17" cy="26" r="4"/><circle cx="27" cy="29" r="4"/><circle cx="20" cy="36" r="4"/>'
               '<circle cx="31" cy="39" r="4"/><circle cx="25" cy="45" r="4"/><circle cx="35" cy="49" r="4"/></g>'
               '</g><circle cx="41" cy="56" r="3.6" fill="var(--honey)"/></svg>'),
    "clove": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M29 24 25 58h6l-2-34" fill="currentColor" fill-opacity=".14"/>'
              '<path d="M22 24h14l-3 6h-8Z" fill="currentColor" fill-opacity=".14"/>'
              '<path d="M23 24c-6-2-8-8-6-12 4 0 8 4 9 10M35 24c6-2 8-8 6-12-4 0-8 4-9 10"/>'
              '</g><circle cx="29" cy="14" r="6" fill="var(--honey)"/></svg>'),
    "cinnamon": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
                 '<path d="M14 40 44 10a6 6 0 0 1 8 8L22 48" fill="currentColor" fill-opacity=".14"/>'
                 '<path d="M44 10a6 6 0 0 0 8 8M47 13a2 2 0 0 0 2 2"/>'
                 '<path d="M14 52 44 22a6 6 0 0 1 8 8L22 60"/><path d="M14 40l-2 2a6 6 0 0 0 8 8l2-2"/>'
                 '</g><circle cx="12" cy="56" r="4" fill="var(--honey)"/></svg>'),
    "cacao": ('<svg class="icon" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
              '<path d="M32 6c12 6 16 18 14 30S36 58 32 58 18 48 18 36 20 12 32 6Z" fill="currentColor" fill-opacity=".14"/>'
              '<path d="M32 6c-4 14-4 36 0 52M32 6c4 14 4 36 0 52M25 12c-4 14-3 32 2 44M39 12c4 14 3 32-2 44"/>'
              '<path d="M32 6V2"/></g><circle cx="49" cy="52" r="5" fill="var(--honey)"/></svg>'),
}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Hanken+Grotesk:wght@400;500;600&display=swap">')


def _ridge(seed, base, amp, n, width=1440):
    """Línea de cerros: picos redondeados, como los conos kársticos de Alta Verapaz."""
    import random
    rnd = random.Random(seed)
    xs = sorted({0, width} | {int(width * (i + rnd.uniform(-0.3, 0.3)) / n) for i in range(1, n)})
    d = f"M0 320 L0 {base}"
    for a, b in zip(xs, xs[1:]):
        h = base - amp * rnd.uniform(0.35, 1.0)
        d += f" C{a + (b - a) * 0.15:.0f} {h:.0f} {a + (b - a) * 0.85:.0f} {h:.0f} {b} {base + rnd.uniform(-6, 6):.0f}"
    return d + f" L{width} 320 Z"


def _canopy(seed, y, rmin, rmax, width=1440):
    """Copas de árboles en primer plano: círculos que se enciman."""
    import random
    rnd = random.Random(seed)
    out, x = [], -20
    while x < width + 40:
        r = rnd.uniform(rmin, rmax)
        out.append(f'<circle cx="{x:.0f}" cy="{y - r * rnd.uniform(0.2, 0.6):.0f}" r="{r:.0f}"/>')
        x += r * rnd.uniform(0.9, 1.4)
    return "".join(out)


def landscape(big=False):
    """Paisaje de Alta Verapaz dibujado en SVG: cerros, neblina, sol y copas de árboles."""
    cls = "scape scape-big" if big else "scape"
    sun = ('<circle class="sun-glow" cx="1110" cy="150" r="150" fill="url(#halo)"/><circle class="sun" cx="1110" cy="150" r="30"/>' if big else
           '<circle class="sun-glow" cx="1200" cy="222" r="80" fill="url(#halo)"/><circle class="sun" cx="1200" cy="222" r="18"/>')
    seeds = "".join(f'<circle class="seed" cx="{x}" cy="{y}" r="{r}" style="animation-delay:{dl}s"/>'
                    for x, y, r, dl in [(220, 120, 2.2, 0), (420, 80, 1.6, 2.1), (640, 150, 2, 1.2), (860, 70, 1.4, 3.3),
                                        (980, 190, 2.4, .6), (1240, 90, 1.8, 2.7), (1350, 200, 1.5, 1.8), (120, 210, 1.7, 3.9)]) if big else ""
    return (f'<div class="{cls}" aria-hidden="true"><svg viewBox="0 0 1440 320" preserveAspectRatio="xMidYMax slice">'
            '<defs><radialGradient id="halo"><stop offset="0" stop-color="#E9B866" stop-opacity=".55"/><stop offset="1" stop-color="#E9B866" stop-opacity="0"/></radialGradient>'
            '<filter id="blur" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="12"/></filter></defs>'
            + sun + seeds +
            f'<path class="l1" d="{_ridge(3, 205, 110, 14)}"/>'
            '<ellipse class="mist m1" cx="420" cy="225" rx="520" ry="16" filter="url(#blur)"/>'
            f'<path class="l2" d="{_ridge(7, 250, 95, 18)}"/>'
            '<ellipse class="mist m2" cx="1050" cy="262" rx="560" ry="14" filter="url(#blur)"/>'
            f'<path class="l3" d="{_ridge(11, 288, 60, 24)}"/>'
            f'<g class="l4">{_canopy(5, 330, 22, 46)}</g>'
            '</svg></div>')


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
        "areaServed": ["CA", "US"],
    }
    person = {
        "@type": "Person",
        "@id": DOMAIN + "/pedro-pablo-duchez-meyer/#person",
        "name": PERSON["name"],
        "alternateName": PERSON["alternateName"],
        "jobTitle": "Director" if lang == "en" else "Director",
        "worksFor": {"@id": DOMAIN + "/#org"},
        "affiliation": {"@type": "Organization", "name": "DAConsortium", "url": "https://www.da-consortium.com/"},
        "image": DOMAIN + PERSON["image"],
        "url": DOMAIN + path_of("founder", lang),
        "sameAs": PERSON["sameAs"],
        "knowsAbout": ["Agribusiness", "Spice export", "Cardamom", "Supply chains", "Strategic management", "Business structuring"],
        "knowsLanguage": ["es", "en"],
        "nationality": {"@type": "Country", "name": "Guatemala"},
    }
    org["employee"] = {"@id": person["@id"]}
    graph = [org]
    if key in ("founder", "about"):
        graph.append(person)
    if key == "founder":
        graph.append({"@type": "ProfilePage", "@id": DOMAIN + path_of("founder", lang) + "#page",
                      "url": DOMAIN + path_of("founder", lang), "name": meta["title"], "inLanguage": lang,
                      "mainEntity": {"@id": person["@id"]}, "about": {"@id": person["@id"]}})
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
    body = body.replace('<section class="hero">', '<section class="hero">' + landscape(big=True), 1)
    body = body.replace('<section class="page-hero">', '<section class="page-hero">' + landscape(), 1)
    prod_links = "".join(f'<li><a href="{path_of(k, lang)}">{t["names"][k]}</a></li>'
                         for k in PRODUCT_KEYS if k not in SOON_KEYS)
    prod_links += "".join(f'<li><a href="{path_of(k, lang)}">{t["names"][k]} · {t["soon"].lower()}</a></li>'
                          for k in SOON_KEYS)
    company_links = "".join(f'<li><a href="{path_of(k, lang)}">{t["names"][k]}</a></li>'
                            for k in ("producers", "about", "founder", "sustainability", "quality", "export"))
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
<link rel="alternate" hreflang="x-default" href="{DOMAIN}{path_of(key, "en")}">
<meta property="og:type" content="{"profile" if key == "founder" else "website"}">
<meta property="og:site_name" content="KAB EXPORT">
<meta property="og:title" content="{esc(meta["title"])}">
<meta property="og:description" content="{esc(meta["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}{PERSON["image"] if key == "founder" else "/assets/img/og-image.png"}">
<meta property="og:image:width" content="{800 if key == "founder" else 1200}">
<meta property="og:image:height" content="{1000 if key == "founder" else 630}">
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
        for p in (en, es):
            rows.append(
                f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod>"
                f'<xhtml:link rel="alternate" hreflang="es" href="{DOMAIN}{es}"/>'
                f'<xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{en}"/></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def redirect_page(target):
    url = DOMAIN + target
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>KAB EXPORT</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body><p><a href="{target}">KAB EXPORT</a></p></body>
</html>
"""


def legacy_redirects():
    """Rutas viejas -> ruta nueva. Las usan las páginas de redirección y vercel.json."""
    pairs = {old: path_of(k, "es") for old, k in LEGACY.items()}
    pairs.update({old: path_of(k, "en") for old, k in LEGACY_EN.items()})
    return pairs


def clean_output():
    """Borra las páginas generadas antes (deja assets, CNAME, robots.txt y .nojekyll)."""
    for f in OUT.rglob("index.html"):
        if "assets" not in f.parts:
            f.unlink()
    for d in sorted((p for p in OUT.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        if "assets" not in d.parts and not any(d.iterdir()):
            d.rmdir()


def main():
    clean_output()
    count = 0
    for lang in ("en", "es"):
        for key in PAGES:
            meta, body = read_page(lang, key)
            write(path_of(key, lang), render(key, lang, meta, body))
            count += 1
    redirects = legacy_redirects()
    for old, new in redirects.items():
        write(old, redirect_page(new))
    vercel = ROOT / "vercel.json"
    cfg = json.loads(vercel.read_text(encoding="utf-8"))
    cfg["redirects"] = [{"source": old, "destination": new, "permanent": True} for old, new in redirects.items()]
    vercel.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # 404: en inglés, con enlace al español
    meta, body = read_page("en", "404")
    page = render("home", "en", meta, body).replace('<link rel="canonical" href="https://kabexport.com/">', '<meta name="robots" content="noindex">')
    (OUT / "404.html").write_text(page, encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print(f"{count} páginas + {len(redirects)} redirecciones + 404 + sitemap.xml generados en {OUT}")


if __name__ == "__main__":
    main()
