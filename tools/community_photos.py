#!/usr/bin/env python3
"""Prepara las fotos de una comunidad para publicarlas.

    python3 tools/community_photos.py <slug> <carpeta-de-originales> <mapa.json>

El mapa dice qué original se publica y con qué nombre:

    {"cosecha-a-mano": {"src": "59.jpg"},
     "salida-camino":  {"src": "36.jpg", "blur": [[1110, 1120, 1200, 1230]]}}

`blur` difumina rectángulos [x0, y0, x1, y1] del original (placas, rostros,
logotipos de terceros). Cada foto sale en dos tamaños, sin metadatos (EXIF,
GPS): <nombre>.jpg (lado mayor 1600 px) y <nombre>-sm.jpg (lado mayor 720 px).
Además escribe content/communities/<slug>/photos.json con las medidas, que
tools/build.py usa para el width/height de cada <img>.

Los originales se quedan fuera del repositorio: el repositorio es público.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    slug, src_dir, map_file = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    mapping = json.loads(map_file.read_text(encoding="utf-8"))
    out_dir = ROOT / "docs" / "assets" / "img" / "communities" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    dims = {}
    for name, spec in mapping.items():
        im = ImageOps.exif_transpose(Image.open(src_dir / spec["src"])).convert("RGB")
        for box in spec.get("blur", []):
            region = im.crop(tuple(box)).filter(ImageFilter.GaussianBlur(18))
            im.paste(region, tuple(box[:2]))
        for suffix, side in (("", 1600), ("-sm", 720)):
            copy = im.copy()
            copy.thumbnail((side, side), Image.LANCZOS)
            # Imagen nueva: así no viaja ningún metadato del teléfono.
            clean = Image.new("RGB", copy.size)
            clean.paste(copy)
            clean.save(out_dir / f"{name}{suffix}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
            if suffix == "":
                dims[name] = list(clean.size)
    meta_dir = ROOT / "content" / "communities" / slug
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "photos.json").write_text(json.dumps(dims, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(dims)} fotos en {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
