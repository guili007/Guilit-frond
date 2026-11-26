"""Régénère l'aperçu social depuis un SVG, sans retouche d'image bitmap.

Outil local facultatif : pip install playwright ; Chrome déjà installé.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]


async def main() -> None:
    logo = (ROOT / "favicon.svg").read_text(encoding="utf-8")
    logo = logo.replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg x="80" y="65" width="72" height="72"')
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#fcf9f3"/>
{logo}
<text x="170" y="119" font-family="Georgia,serif" font-size="46" font-weight="bold" fill="#0c447c">Guilit</text>
<text x="80" y="315" font-family="Georgia,serif" font-size="64" font-weight="bold" fill="#123247">L’assistant qui parle</text>
<text x="80" y="397" font-family="Georgia,serif" font-size="73" font-weight="bold" fill="#0c447c">votre langue.</text>
<rect x="755" y="150" width="378" height="175" rx="24" fill="#fff"/>
<rect x="780" y="176" width="89" height="28" rx="14" fill="#1c9673"/>
<text x="791" y="196" font-family="Arial,sans-serif" font-size="15" font-weight="bold" fill="#fff">Lingala</text>
<text x="780" y="235" font-family="Arial,sans-serif" font-size="23" fill="#123247"><tspan x="780">Mbote ! Tuna ngai likambo</tspan><tspan x="780" dy="31">nyonso, na lingala to na</tspan><tspan x="780" dy="31">français.</tspan></text>
<path d="M960 630L1200 390V470L1040 630Z" fill="#e24b4a"/><path d="M1040 630L1200 470V550L1120 630Z" fill="#f0a227"/><path d="M1120 630L1200 550V630Z" fill="#0c447c"/>
<text x="80" y="552" font-family="Arial,sans-serif" font-size="25" fill="#4d6982">Français &amp; lingala · app.guilit.com · conçu en RDC</text>
</svg>'''
    path = ROOT / "og-image.svg"
    path.write_text(source, encoding="utf-8")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        await page.goto(path.as_uri())
        await page.screenshot(path=str(ROOT / "og-image.png"))
        await browser.close()
    print("Aperçu social régénéré pour app.guilit.com.")


if __name__ == "__main__":
    asyncio.run(main())
