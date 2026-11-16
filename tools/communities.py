"""Fichas de comunidad: una página por comunidad productora, en los dos idiomas.

Cada comunidad vive en content/communities/<slug>/:
  community.json  los textos y los datos (ver COMUNIDADES.md)
  photos.json     medidas de las fotos (lo escribe tools/community_photos.py)

build.py llama a load() para registrar las páginas y a body() para dibujarlas.
Nada de lo que está aquí inventa datos: un campo vacío se publica como
«en documentación», y un productor sin consentimiento no se publica.
"""
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "content" / "communities"
IMG = "/assets/img/communities"

L = {
    "en": {
        "base": "/producers/",
        "eyebrow": "Producer community",
        "share": "Share this page",
        "copy": "Copy link",
        "print": "Print or save as PDF",
        "legend_seen": "Seen on site",
        "legend_pending": "Being documented",
        "record": "Field record",
        "ledger_eyebrow": "What we can show you",
        "ledger_title": "Every claim, with its evidence",
        "ledger_lede": "Each statement on this page carries a status. <b>Seen on site</b> means we saw it ourselves on a visit, and the photo is from there. <b>Being documented</b> means we know it, but the proof is not published yet.",
        "journey_eyebrow": "From plant to sack",
        "journey_title": "How cardamom is made in {name}",
        "journey_hint": "Swipe to follow the process",
        "figures_eyebrow": "In figures",
        "figures_title": "The community in numbers",
        "figures_lede": "We publish a number only once we have measured it with the producers. Until then, it stays marked.",
        "people_eyebrow": "The families",
        "people_title": "The people behind this cardamom",
        "people_pending": "We are documenting each producing family together with them. Profiles are published only with each family's consent, and each one will include:",
        "people_fields": ["Name, and how long they have grown cardamom", "Size of their plots", "Number of plants and how they are managed", "What they harvest in a typical season", "In their own words: what the crop means for their family"],
        "commit_eyebrow": "Our commitments",
        "commit_text": "Clear prices agreed before harvest, paid on time. Purchases through the producers' own organizations. Drying, sorting and packing at origin. Volumes planned season after season.",
        "commit_link": "Read our commitments to producers",
        "gallery_eyebrow": "Photographs",
        "gallery_title": "From the field",
        "gallery_lede": "Taken on site during the {record} harvest, unretouched.",
        "visit_title": "Come and see it for yourself",
        "visit_text": "Buyers can visit {name} with us, walk the plots and see the drying facility. Visits are arranged with the community in advance, at a time that suits them.",
        "visit_btn": "Plan a visit",
        "ask_btn": "Ask about this cardamom",
        "foot_record": "Field record of {name}",
        "foot_photos": "Photographs taken on site, {record}.",
        "foot_updated": "Page updated",
        "foot_reviewed": "Information reviewed by",
        "close": "Close",
        "prev": "Previous photo",
        "next": "Next photo",
        "list_title": "Community files",
        "list_lede": "One page per community: what we have seen there, the photographs, and what we are still documenting. Share them freely.",
        "list_open": "Open the file",
        "list_soon": "File in preparation",
        "wa": "Field record of {name}, a cardamom-growing community in Alta Verapaz, Guatemala:",
    },
    "es": {
        "base": "/es/productores/",
        "eyebrow": "Comunidad productora",
        "share": "Compartir esta página",
        "copy": "Copiar enlace",
        "print": "Imprimir o guardar en PDF",
        "legend_seen": "Visto en campo",
        "legend_pending": "En documentación",
        "record": "Ficha de campo",
        "ledger_eyebrow": "Lo que podemos mostrarte",
        "ledger_title": "Cada afirmación, con su evidencia",
        "ledger_lede": "Cada afirmación de esta página lleva un estado. <b>Visto en campo</b> quiere decir que lo vimos nosotros mismos en una visita, y la foto es de ahí. <b>En documentación</b> quiere decir que lo sabemos, pero la prueba todavía no está publicada.",
        "journey_eyebrow": "De la mata al saco",
        "journey_title": "Así se hace el cardamomo en {name}",
        "journey_hint": "Desliza para seguir el proceso",
        "figures_eyebrow": "En cifras",
        "figures_title": "La comunidad en números",
        "figures_lede": "Publicamos una cifra solo cuando la hemos medido con los productores. Mientras tanto, queda marcada.",
        "people_eyebrow": "Las familias",
        "people_title": "Las personas detrás de este cardamomo",
        "people_pending": "Estamos documentando cada familia productora junto con ellas. Los perfiles se publican solo con el consentimiento de cada familia, y cada uno incluirá:",
        "people_fields": ["Nombre, y desde cuándo cultivan cardamomo", "Tamaño de sus parcelas", "Número de matas y cómo las manejan", "Lo que cosechan en una temporada normal", "En sus palabras: lo que el cultivo significa para su familia"],
        "commit_eyebrow": "Nuestros compromisos",
        "commit_text": "Precios claros acordados antes de la cosecha y pagados a tiempo. Compras a través de las propias organizaciones de los productores. Secado, clasificación y empaque en origen. Volúmenes planificados temporada tras temporada.",
        "commit_link": "Leer nuestros compromisos con los productores",
        "gallery_eyebrow": "Fotografías",
        "gallery_title": "Desde el campo",
        "gallery_lede": "Tomadas en la comunidad durante la cosecha de {record}, sin retoques.",
        "visit_title": "Ven a verlo con tus propios ojos",
        "visit_text": "Los compradores pueden visitar {name} con nosotros, recorrer las parcelas y conocer el beneficio. Las visitas se acuerdan antes con la comunidad, en el momento que mejor le quede.",
        "visit_btn": "Planificar una visita",
        "ask_btn": "Preguntar por este cardamomo",
        "foot_record": "Ficha de campo de {name}",
        "foot_photos": "Fotografías tomadas en la comunidad, {record}.",
        "foot_updated": "Página actualizada el",
        "foot_reviewed": "Información revisada por",
        "close": "Cerrar",
        "prev": "Foto anterior",
        "next": "Foto siguiente",
        "list_title": "Fichas por comunidad",
        "list_lede": "Una página por comunidad: lo que hemos visto ahí, las fotografías y lo que aún estamos documentando. Compártelas con libertad.",
        "list_open": "Abrir la ficha",
        "list_soon": "Ficha en preparación",
        "wa": "Ficha de campo de {name}, comunidad productora de cardamomo en Alta Verapaz, Guatemala:",
    },
}

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}

SEEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>'
PENDING = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M8.6 8.4c.2-.5.5-.5.8-.5h.5c.2 0 .4 0 .6.5l.7 1.6c.1.2.1.4 0 .6l-.4.6c-.1.2-.2.3 0 .6.5.9 1.3 1.7 2.3 2.2.2.1.4.1.6-.1l.6-.7c.2-.2.4-.2.6-.1l1.6.8c.2.1.4.2.4.4 0 .5-.2 1.3-1.1 1.7-.7.3-1.6.3-3.4-.5-2.2-1-3.6-3.3-3.7-3.5-.2-.2-.9-1.2-.9-2.3 0-1 .5-1.5.7-1.8Z" fill="currentColor"/></svg>'
ICON_IN = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 10v6M8 7.5v.01M12 16v-3.2c0-1.5.9-2.3 2-2.3s2 .8 2 2.3V16M12 10v6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m4 7 8 6 8-6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
ICON_LINK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
ICON_PRINT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 9V3h10v6M7 18H4v-7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v7h-3M7 14h10v7H7Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'


def load():
    """Devuelve {clave: datos} de cada comunidad, en orden alfabético."""
    out = {}
    for d in sorted(p for p in DIR.iterdir() if p.is_dir()):
        data = json.loads((d / "community.json").read_text(encoding="utf-8"))
        data["dims"] = json.loads((d / "photos.json").read_text(encoding="utf-8"))
        for name in _photos_used(data):
            if name not in data["dims"]:
                raise SystemExit(f"{d.name}: la foto «{name}» no existe; corre tools/community_photos.py")
        out["community-" + data["slug"]] = data
    return out


def _photos_used(c):
    used = {c["hero"]["photo"], c["hero"]["inset"], *c["gallery"]}
    used |= {e["photo"] for e in c["ledger"] if e.get("photo")}
    used |= {e["photo"] for e in c["journey"]}
    used |= {p["photo"] for p in c.get("producers", []) if p.get("photo")}
    return used


def paths(c):
    return (L["es"]["base"] + c["slug"] + "/", L["en"]["base"] + c["slug"] + "/")


def og_image(c):
    return f"{IMG}/{c['slug']}/og.jpg"


def _img(c, name, lang, cls="", sizes="(max-width: 700px) 100vw, 50vw", eager=False):
    w, h = c["dims"][name]
    alt = escape(c["captions"][name][lang])
    base = f"{IMG}/{c['slug']}/{name}"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    cls = f' class="{cls}"' if cls else ""
    sm = round(w * min(1, 720 / max(w, h)))  # el tamaño chico nunca agranda el original
    srcset = f"{base}-sm.jpg {sm}w, {base}.jpg {w}w" if sm < w else f"{base}.jpg {w}w"
    return (f'<img{cls} src="{base}-sm.jpg" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" {load}>')


def _status(lang, status):
    t = L[lang]
    if status == "seen":
        return f'<span class="st st-seen">{SEEN}{t["legend_seen"]}</span>'
    return f'<span class="st st-pending">{PENDING}{t["legend_pending"]}</span>'


def _date(lang, iso):
    y, m, d = (int(x) for x in iso.split("-"))
    month = MONTHS[lang][m - 1]
    return f"{month} {d}, {y}" if lang == "en" else f"{d} de {month} de {y}"


def _share(c, lang, url):
    t = L[lang]
    msg = t["wa"].format(name=c["name"]) + " " + url
    title = c["meta"][lang]["title"]
    links = [
        ("wa", "WhatsApp", f"https://wa.me/?text={quote(msg)}", ICON_WA),
        ("in", "LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={quote(url, safe='')}", ICON_IN),
        ("mail", "Email" if lang == "en" else "Correo", f"mailto:?subject={quote(title)}&body={quote(msg)}", ICON_MAIL),
    ]
    items = "".join(
        f'<a class="sh sh-{k}" href="{escape(href)}" target="_blank" rel="noopener" title="{label}">{icon}<span>{label}</span></a>'
        for k, label, href, icon in links)
    items += f'<button class="sh" type="button" data-copy="{url}">{ICON_LINK}<span>{t["copy"]}</span></button>'
    items += f'<button class="sh sh-print" type="button" data-print>{ICON_PRINT}<span>{t["print"]}</span></button>'
    return f'<div class="share" role="group" aria-label="{t["share"]}"><span class="share-label">{t["share"]}</span>{items}</div>'


def body(key, c, lang, url, crumbs, url_of, founder_url):
    t = L[lang]
    name = escape(c["name"])
    record = c["field_record"][lang]
    seen = sum(1 for e in c["ledger"] if e["status"] == "seen")
    pending = len(c["ledger"]) - seen

    # 1. Portada
    hero = f"""<section class="cf-hero">
  <div class="wrap cf-hero-grid">
    <div class="cf-hero-copy">
      {crumbs}
      <div class="eyebrow">{t["eyebrow"]} · {escape(c["place"][lang])}</div>
      <h1>{name}</h1>
      <p class="cf-tagline">{escape(c["hero"]["tagline"][lang])}</p>
      <p class="cf-lede">{escape(c["hero"]["lede"][lang])}</p>
      <ul class="cf-legend">
        <li>{_status(lang, "seen")}<b>{seen}</b></li>
        <li>{_status(lang, "pending")}<b>{pending}</b></li>
      </ul>
      {_share(c, lang, url)}
    </div>
    <div class="cf-hero-art">
      <figure class="cf-main">{_img(c, c["hero"]["photo"], lang, sizes="(max-width: 900px) 90vw, 440px", eager=True)}</figure>
      <figure class="cf-inset">{_img(c, c["hero"]["inset"], lang, sizes="260px")}</figure>
      <div class="cf-stamp" aria-hidden="true"><span>{t["record"]}</span><b>{escape(record)}</b></div>
    </div>
  </div>
</section>"""

    # 2. Libro de evidencias
    rows = []
    for e in c["ledger"]:
        photo = (f'<button class="ev-photo" type="button" data-zoom="{e["photo"]}">{_img(c, e["photo"], lang, sizes="(max-width: 700px) 100vw, 320px")}</button>'
                 if e.get("photo") else '<div class="ev-photo ev-empty" aria-hidden="true">' + PENDING + '</div>')
        rows.append(f"""<article class="ev ev-{e["status"]}">
        {photo}
        <div class="ev-text">{_status(lang, e["status"])}<h3>{escape(e["title"][lang])}</h3><p>{escape(e["text"][lang])}</p></div>
      </article>""")
    ledger = f"""<section class="block">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["ledger_eyebrow"]}</div><h2>{t["ledger_title"]}</h2><p>{t["ledger_lede"]}</p></div>
    <div class="ledger">{"".join(rows)}</div>
  </div>
</section>"""

    # 3. Recorrido
    steps = "".join(
        f'<li class="step-card"><figure>{_img(c, s["photo"], lang, sizes="(max-width: 700px) 78vw, 300px")}</figure>'
        f'<span class="n">{i:02d}</span><h3>{escape(s["title"][lang])}</h3><p>{escape(s["text"][lang])}</p></li>'
        for i, s in enumerate(c["journey"], 1))
    journey = f"""<section class="block band journey-band">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["journey_eyebrow"]}</div><h2>{t["journey_title"].format(name=name)}</h2><p class="journey-hint">{t["journey_hint"]} →</p></div>
  </div>
  <ol class="journey" tabindex="0">{steps}</ol>
</section>"""

    # 4. Cifras
    figs = []
    for f in c["figures"]:
        if f.get("value"):
            note = f'<small>{escape(f["note"][lang])}</small>' if f.get("note") else ""
            figs.append(f'<div class="fig"><span>{escape(f["label"][lang])}</span><b>{escape(f["value"][lang])}</b>{note}</div>')
        else:
            figs.append(f'<div class="fig fig-pending"><span>{escape(f["label"][lang])}</span><b aria-hidden="true">—</b>{_status(lang, "pending")}</div>')
    figures = f"""<section class="block">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["figures_eyebrow"]}</div><h2>{t["figures_title"]}</h2><p>{t["figures_lede"]}</p></div>
    <div class="figs">{"".join(figs)}</div>
  </div>
</section>"""

    # 5. Las familias: solo con consentimiento
    people_ok = [p for p in c.get("producers", []) if p.get("consent") is True]
    if people_ok:
        cards = []
        for p in people_ok:
            img = _img(c, p["photo"], lang, sizes="(max-width: 700px) 100vw, 360px") if p.get("photo") else ""
            facts = "".join(f"<li>{escape(x[lang])}</li>" for x in p.get("facts", []))
            quote_ = f'<blockquote>{escape(p["quote"][lang])}</blockquote>' if p.get("quote") else ""
            cards.append(f'<article class="person">{img}<h3>{escape(p["name"])}</h3>'
                         f'<p class="role">{escape(p["role"][lang])}</p><ul>{facts}</ul>{quote_}</article>')
        people_inner = f'<div class="people">{"".join(cards)}</div>'
    else:
        fields = "".join(f"<li>{escape(x)}</li>" for x in t["people_fields"])
        people_inner = f"""<div class="people-pending">
      <div>{_status(lang, "pending")}<p>{t["people_pending"]}</p><ul class="checklist">{fields}</ul></div>
      <figure>{_img(c, "renuevo", lang, sizes="(max-width: 900px) 100vw, 420px")}</figure>
    </div>"""
    people = f"""<section class="block tight">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["people_eyebrow"]}</div><h2>{t["people_title"]}</h2></div>
    {people_inner}
    <aside class="commit"><div class="eyebrow">{t["commit_eyebrow"]}</div><p>{t["commit_text"]}</p><a href="{url_of("producers")}#commitments">{t["commit_link"]} →</a></aside>
  </div>
</section>"""

    # 6. Galería
    tiles = "".join(
        f'<li><button type="button" data-zoom="{n}">{_img(c, n, lang, sizes="(max-width: 700px) 50vw, 300px")}</button></li>'
        for n in c["gallery"])
    gallery = f"""<section class="block tight">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["gallery_eyebrow"]}</div><h2>{t["gallery_title"]}</h2><p>{t["gallery_lede"].format(record=escape(record))}</p></div>
    <ul class="gallery">{tiles}</ul>
  </div>
</section>"""

    # 7. Visita y cierre de ficha
    visit = f"""<section class="block tight">
  <div class="wrap">
    <div class="cta">
      <div><h2>{t["visit_title"]}</h2><p>{t["visit_text"].format(name=name)}</p></div>
      <div class="hero-cta"><a class="btn btn-honey" href="{url_of("contact")}?p=visita">{t["visit_btn"]}</a><a class="btn btn-ghost" href="{url_of("contact")}?p=cardamomo">{t["ask_btn"]}</a></div>
    </div>
    <footer class="fieldnote">
      <b>{t["foot_record"].format(name=name)}</b>
      <span>{t["foot_photos"].format(record=escape(record))}</span>
      <span>{t["foot_updated"]} {_date(lang, c["updated"])}.</span>
      <span>{t["foot_reviewed"]} <a href="{founder_url}">Pedro Pablo Duchez Meyer</a>, Director, KAB EXPORT.</span>
    </footer>
  </div>
</section>"""

    # Visor de fotos (sin dependencias)
    data = {n: {"src": f"{IMG}/{c['slug']}/{n}.jpg", "cap": c["captions"][n][lang]} for n in c["dims"]}
    viewer = (f'<dialog class="viewer" aria-label="{t["gallery_title"]}"><figure><img alt=""><figcaption></figcaption></figure>'
              f'<button type="button" class="v-close" aria-label="{t["close"]}">×</button>'
              f'<button type="button" class="v-prev" aria-label="{t["prev"]}">‹</button>'
              f'<button type="button" class="v-next" aria-label="{t["next"]}">›</button></dialog>'
              f'<script type="application/json" id="photos">{json.dumps(data, ensure_ascii=False)}</script>')

    return "\n\n".join([hero, ledger, journey, figures, people, gallery, visit, viewer])


def cards(communities, lang, soon=()):
    """Tarjetas para la página de productores. `soon`: nombres de fichas en preparación."""
    t = L[lang]
    out = []
    for key, c in communities.items():
        href = paths(c)[0 if lang == "es" else 1]
        seen = sum(1 for e in c["ledger"] if e["status"] == "seen")
        out.append(f"""<a class="cf-card" href="{href}">
        <figure>{_img(c, c["hero"]["photo"], lang, sizes="(max-width: 700px) 100vw, 360px")}</figure>
        <div><span class="st st-seen">{SEEN}{seen} · {t["legend_seen"].lower()}</span><h3>{escape(c["name"])}</h3>
        <p>{escape(c["hero"]["tagline"][lang])}</p><span class="more">{t["list_open"]} →</span></div>
      </a>""")
    for s in soon:
        out.append(f'<div class="cf-card cf-soon"><div><span class="st st-pending">{PENDING}{t["list_soon"]}</span><h3>{escape(s)}</h3></div></div>')
    return f"""<section class="block tight" id="communities">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["record"]}</div><h2>{t["list_title"]}</h2><p>{t["list_lede"]}</p></div>
    <div class="cf-cards">{"".join(out)}</div>
  </div>
</section>"""
