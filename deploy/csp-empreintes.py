"""
Recalcule les empreintes CSP des scripts en ligne du site.

À lancer après toute modification d'un <script> :

    python deploy/csp-empreintes.py

puis remplacer la liste après script-src 'self' dans nginx-securite.conf.
"""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

racine = Path(__file__).resolve().parent.parent
empreintes = sorted(
    {
        "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'"
        for page in racine.glob("*.html")
        for m in re.finditer(r"<script>(.*?)</script>", page.read_text(encoding="utf-8"), re.S)
    }
)
print(" ".join(empreintes))
