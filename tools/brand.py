#!/usr/bin/env python3
"""Genera los archivos del logo de KAB EXPORT en brand/ (SVG con texto en curvas).

Uso: python3 tools/brand.py <Fraunces-700.woff2> <HankenGrotesk-600.woff2>
Requiere: pip install fonttools brotli
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(__file__).resolve().parent.parent / "brand"

COLORS = {
    # nombre: (trazo principal, acento)
    "color": ("#1F3B2D", "#D4922A"),
    "blanco": ("#F6EFDF", "#E9B866"),
    "negro": ("#000000", "#000000"),
}

MARK = ('<path d="M32 6 54.5 19v26L32 58 9.5 45V19Z" fill="none" stroke="{a}" stroke-width="3.5" stroke-linejoin="round"/>'
        '<path d="M24 19v26M24 33 37 20" fill="none" stroke="{a}" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M28.5 28.5 40 41q5 5 15 4" fill="none" stroke="{b}" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="59" cy="45" r="3" fill="{b}"/>')


def text_path(font, text, size, tracking, x, baseline):
    """Devuelve (d, ancho) del texto convertido a curvas."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cursor = x
    for i, ch in enumerate(text):
        name = cmap[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline))
        gs[name].draw(tp)
        cursor += gs[name].width * scale + (tracking if i < len(text) - 1 else 0)
    return pen.getCommands(), cursor - x


def main(fraunces, hanken):
    serif, sans = TTFont(fraunces), TTFont(hanken)
    OUT.mkdir(exist_ok=True)
    # Medidas del logo en el sitio: símbolo 44 px, separación 12 px,
    # "KAB" 25.6 px (+0.05em), "EXPORT" 10.24 px (+0.42em), 5 px entre líneas.
    s = 64 / 44  # el símbolo se dibuja en una caja de 64
    kab_size, exp_size = 25.6 * s, 10.24 * s
    text_x = 64 + 12 * s
    cap_k = serif["OS/2"].sCapHeight / serif["head"].unitsPerEm * kab_size
    cap_e = sans["OS/2"].sCapHeight / sans["head"].unitsPerEm * exp_size
    block = cap_k + 7 * s + cap_e
    top = (64 - block) / 2
    kab_d, kab_w = text_path(serif, "KAB", kab_size, 0.05 * kab_size, text_x, top + cap_k)
    exp_d, exp_w = text_path(sans, "EXPORT", exp_size, 0.42 * exp_size, text_x + 1, top + block)
    width = text_x + max(kab_w, exp_w + 1) + 2

    for name, (a, b) in COLORS.items():
        mark = MARK.format(a=a, b=b)
        logo = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {width + 4:.1f} 68">'
                f'<title>KAB EXPORT</title>{mark}'
                f'<path d="{kab_d}" fill="{a}"/><path d="{exp_d}" fill="{a}"/></svg>\n')
        (OUT / f"kab-export-logo-{name}.svg").write_text(logo, encoding="utf-8")
        icon = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="5.75 2 60 60">'
                f'<title>KAB EXPORT</title>{mark}</svg>\n')
        (OUT / f"kab-export-icono-{name}.svg").write_text(icon, encoding="utf-8")
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main(*sys.argv[1:3])
