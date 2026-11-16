"""Visitas internacionales: compradores que vinieron a ver las comunidades.

Cada visita vive en content/visits/<slug>/visit.json (+ photos.json, que
escribe tools/community_photos.py visits/<slug> ...). Se publican en la página
de productores y en la ficha de cada comunidad que la visita incluyó.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "content" / "visits"
IMG = "/assets/img/visits"

L = {
    "en": {
        "eyebrow": "International visits",
        "title": "Buyers who came to see it for themselves",
        "lede": "The best proof of what we say is to come and see it. These are the buyers who have visited the producing communities with us.",
        "title_one": "Visited by buyers",
        "lede_one": "{name} has been visited by international buyers. This is the record of each visit.",
        "visitor": "Visitor",
        "company": "Company",
        "dates": "Dates",
        "did": "What the visit covered",
        "more": "photos",
        "join": "Plan your own visit",
    },
    "es": {
        "eyebrow": "Visitas internacionales",
        "title": "Compradores que vinieron a verlo con sus propios ojos",
        "lede": "La mejor prueba de lo que decimos es venir a verlo. Estos son los compradores que han visitado con nosotros las comunidades productoras.",
        "title_one": "Visitada por compradores",
        "lede_one": "{name} ha recibido la visita de compradores internacionales. Este es el registro de cada visita.",
        "visitor": "Visitante",
        "company": "Empresa",
        "dates": "Fechas",
        "did": "Qué incluyó la visita",
        "more": "fotos",
        "join": "Planificar tu propia visita",
    },
}
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}
FLAG_CA = ('<svg class="flag" viewBox="0 0 30 15" aria-hidden="true"><rect width="30" height="15" fill="#fff"/>'
           '<rect width="7.5" height="15" fill="#D52B1E"/><rect x="22.5" width="7.5" height="15" fill="#D52B1E"/>'
           '<path d="M15 2.6l.9 1.8 1.1-.5-.4 2.4 1.3-1.3.3.8 1.6-.3-.5 1.6.6.3-2.6 2 .3 1-2-.3V12h-.6v-1.9l-2 .3.3-1-2.6-2 .6-.3-.5-1.6 1.6.3.3-.8 1.3 1.3-.4-2.4 1.1.5Z" fill="#D52B1E"/></svg>')
EXT = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" '
       'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def load():
    out = []
    if not DIR.exists():
        return out
    for d in sorted((p for p in DIR.iterdir() if p.is_dir()), reverse=True):
        v = json.loads((d / "visit.json").read_text(encoding="utf-8"))
        v["dims"] = json.loads((d / "photos.json").read_text(encoding="utf-8"))
        for n in v["photos"]:
            if n not in v["dims"]:
                raise SystemExit(f"visita {d.name}: falta la foto «{n}»")
        out.append(v)
    return out


def dates(lang, a, b):
    ya, ma, da = (int(x) for x in a.split("-"))
    yb, mb, db = (int(x) for x in b.split("-"))
    if lang == "en":
        if (ya, ma) == (yb, mb):
            return f"{MONTHS['en'][ma-1]} {da}–{db}, {ya}"
        return f"{MONTHS['en'][ma-1]} {da} – {MONTHS['en'][mb-1]} {db}, {yb}"
    if (ya, ma) == (yb, mb):
        return f"{da} al {db} de {MONTHS['es'][ma-1]} de {ya}"
    return f"{da} de {MONTHS['es'][ma-1]} al {db} de {MONTHS['es'][mb-1]} de {yb}"


def _img(v, name, lang, sizes):
    w, h = v["dims"][name]
    base = f"{IMG}/{v['slug']}/{name}"
    sm = round(w * min(1, 720 / max(w, h)))
    srcset = f"{base}-sm.jpg {sm}w, {base}.jpg {w}w" if sm < w else f"{base}.jpg {w}w"
    return (f'<img src="{base}-sm.jpg" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{escape(v["captions"][name][lang])}" loading="lazy" decoding="async">')


def _card(v, lang, contact_url):
    t = L[lang]
    tiles = []
    for i, n in enumerate(v["photos"][:5]):
        extra = len(v["photos"]) - 5
        badge = f'<span class="vm-more">+{extra} {t["more"]}</span>' if i == 4 and extra > 0 else ""
        tiles.append(f'<button type="button" class="vm-{i}" data-zoom="{v["slug"]}/{n}" '
                     f'data-src="{IMG}/{v["slug"]}/{n}.jpg" data-cap="{escape(v["captions"][n][lang])}">'
                     f'{_img(v, n, lang, "(max-width: 700px) 50vw, 360px")}{badge}</button>')
    hidden = "".join(
        f'<button type="button" hidden data-zoom="{v["slug"]}/{n}" data-src="{IMG}/{v["slug"]}/{n}.jpg" '
        f'data-cap="{escape(v["captions"][n][lang])}"></button>' for n in v["photos"][5:])
    did = "".join(f"<li>{escape(x)}</li>" for x in v["did"][lang])
    flag = FLAG_CA if v.get("flag") == "CA" else ""
    host = v["company_url"].split("//", 1)[-1].rstrip("/")
    return f"""<article class="visit">
      <div class="visit-mosaic">{"".join(tiles)}{hidden}</div>
      <div class="visit-info">
        <span class="visit-date">{dates(lang, v["start"], v["end"])}</span>
        <h3>{escape(v["visitor"])}</h3>
        <p class="visit-role">{escape(v["role"][lang])}, <a href="{escape(v["company_url"])}" target="_blank" rel="noopener">{escape(v["company"])}</a></p>
        <p class="visit-place">{flag}{escape(v["company_place"][lang])}</p>
        <p class="visit-sum">{escape(v["summary"][lang])}</p>
        <div class="visit-did"><span>{t["did"]}</span><ul class="checklist">{did}</ul></div>
        <a class="visit-site" href="{escape(v["company_url"])}" target="_blank" rel="noopener">{escape(host)}{EXT}</a>
      </div>
    </article>"""


def section(visits, lang, contact_url, community=None, community_name=None):
    """Sección de visitas. Con `community`, solo las visitas que la incluyeron."""
    t = L[lang]
    chosen = [v for v in visits if community is None or community in v.get("communities", [])]
    if not chosen:
        return ""
    head = (f'<h2>{t["title_one"]}</h2><p>{t["lede_one"].format(name=escape(community_name))}</p>' if community
            else f'<h2>{t["title"]}</h2><p>{t["lede"]}</p>')
    cards = "".join(_card(v, lang, contact_url) for v in chosen)
    return f"""<section class="block visits" id="visits">
  <div class="wrap">
    <div class="sec-head"><div class="eyebrow">{t["eyebrow"]}</div>{head}</div>
    {cards}
    <p class="visits-join"><a class="btn btn-line" href="{contact_url}?p=visita">{t["join"]} →</a></p>
  </div>
</section>"""
