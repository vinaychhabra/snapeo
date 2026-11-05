#!/usr/bin/env python3
"""Make web-ready WebP copies of your photos (the biggest speed win for the site).

Usage:  python3 tools/optimize_images.py <folder-with-your-photos> [output-folder]
Needs:  pip install pillow
Output: img/<name>-480.webp, img/<name>-900.webp, img/<name>-1600.webp

Then in assets/config.js set:
   widths:[480,900,1600],
   imageTemplate:"/img/{src}-{w}.webp",
and replace each photo link with just the file name (no extension), e.g. "DSC_0412".
Upload the img/ folder next to index.html.
"""
import sys, os
from PIL import Image, ImageOps
src = sys.argv[1] if len(sys.argv) > 1 else "."
out = sys.argv[2] if len(sys.argv) > 2 else "img"
os.makedirs(out, exist_ok=True)
names = []
for f in sorted(os.listdir(src)):
    stem, ext = os.path.splitext(f)
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"):
        continue
    im = ImageOps.exif_transpose(Image.open(os.path.join(src, f))).convert("RGB")
    for w in (480, 900, 1600):
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(out, f"{stem}-{w}.webp"), "WEBP", quality=78, method=6)
    names.append(stem)
    print("done", f)
print("\nFile names to use in config.js:\n" + "\n".join(f'  "{n}",' for n in names))
