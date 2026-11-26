"""Exporte un QR code Guilit vérifié, en PNG et SVG.

Outils locaux uniquement : pip install 'qrcode[pil]==8.2' zxing-cpp
Usage : python deploy/generer-qr.py
"""

from __future__ import annotations

import io
from pathlib import Path

import qrcode
import zxingcpp
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
URL = "https://guilit.com"
NAVY = "#0C447C"
BOX = 40


def main() -> None:
    # Une marge blanche de quatre modules reste intacte autour du code.
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=BOX, border=4)
    qr.add_data(URL)
    qr.make(fit=False)
    image = qr.make_image(fill_color=NAVY, back_color="white").convert("RGB")
    size = image.width
    badge_size = 7 * BOX
    badge_start = (size - badge_size) // 2
    ImageDraw.Draw(image).rectangle(
        (badge_start, badge_start, badge_start + badge_size - 1, badge_start + badge_size - 1),
        fill="white",
    )
    logo_size = 6 * BOX
    logo_start = (size - logo_size) // 2
    with Image.open(ROOT / "guilit-telegram.png") as source:
        logo = source.convert("RGB").resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    image.paste(logo, (logo_start, logo_start))

    samples = [("original", image), ("rotation", image.rotate(90)),
               ("gris", image.convert("L"))]
    for width in (1024, 512, 300, 240):
        samples.append((str(width), image.resize((width, width), Image.Resampling.LANCZOS)))
    jpeg = io.BytesIO()
    image.resize((512, 512), Image.Resampling.LANCZOS).save(jpeg, format="JPEG", quality=60)
    jpeg.seek(0)
    samples.append(("JPEG", Image.open(jpeg).convert("RGB")))
    samples.append(("flou leger", image.resize((512, 512)).filter(ImageFilter.GaussianBlur(0.4))))
    for name, sample in samples:
        decoded = zxingcpp.read_barcode(sample)
        if decoded is None or decoded.text != URL:
            raise RuntimeError(f"Lecture du QR impossible : {name}. Aucun fichier exporté.")

    matrix = qr.get_matrix()
    modules = "".join(
        f"M{x * BOX},{y * BOX}h{BOX}v{BOX}h-{BOX}z"
        for y, row in enumerate(matrix) for x, dark in enumerate(row) if dark
    )
    # Le SVG réutilise le logo vectoriel d'origine, sans image externe.
    logo_svg = (ROOT / "favicon.svg").read_text(encoding="utf-8").replace(
        "<svg ", f'<svg x="{logo_start}" y="{logo_start}" width="{logo_size}" height="{logo_size}" ', 1,
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
        '<title>QR code Guilit : https://guilit.com</title>\n'
        f'<rect width="{size}" height="{size}" fill="white"/>\n'
        f'<path d="{modules}" fill="{NAVY}" shape-rendering="crispEdges"/>\n'
        f'<rect x="{badge_start}" y="{badge_start}" width="{badge_size}" height="{badge_size}" fill="white"/>\n'
        + logo_svg + '\n</svg>\n'
    )
    image.save(ROOT / "qr-guilit.png", optimize=True, dpi=(300, 300))
    (ROOT / "qr-guilit.svg").write_text(svg, encoding="utf-8")
    print(f"QR vérifié : {URL} ; {len(samples)} essais réussis ; PNG {size} x {size} et SVG exportés.")


if __name__ == "__main__":
    main()
