#!/usr/bin/env python3
"""Meldet Seiten per IndexNow an Bing & Co. (Bing, Yandex, Seznam, Naver teilen sich die Meldungen).

    python3 _src/indexnow.py                 # zeigt nur, was gemeldet würde
    python3 _src/indexnow.py --send          # alle Sitemap-URLs melden (nach einem Deploy mit neuen Seiten)
    python3 _src/indexnow.py --send /faq/ /updates/   # nur bestimmte Pfade (nach kleinen Änderungen)

Erst NACH dem Deploy ausführen – die Schlüsseldatei /<key>.txt muss live erreichbar sein.
Nur geänderte Seiten melden; dieselben URLs ohne Änderung immer wieder zu senden, mögen die Suchmaschinen nicht.
"""
from __future__ import annotations

import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "_src/data/product.json").read_text(encoding="utf-8"))["site"]
ORIGIN, KEY = SITE["origin"].rstrip("/"), SITE["indexNowKey"]


def main() -> int:
    paths = [a for a in sys.argv[1:] if a.startswith("/")]
    urls = ([ORIGIN + p for p in paths] if paths else
            re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8")))
    body = {"host": ORIGIN.split("://", 1)[1], "key": KEY, "keyLocation": f"{ORIGIN}/{KEY}.txt", "urlList": urls}
    print(f"{len(urls)} URL(s):", *urls, sep="\n  ")
    if "--send" not in sys.argv:
        print("Probelauf – senden mit --send")
        return 0
    ctx = ssl.create_default_context()
    if pathlib.Path("/etc/ssl/cert.pem").exists():
        ctx.load_verify_locations("/etc/ssl/cert.pem")
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            print(f"HTTP {r.status} – angenommen")   # 200 oder 202 (Schlüssel wird noch geprüft)
            return 0
    except urllib.error.HTTPError as e:
        hint = {400: "Anfrage ungültig", 403: "Schlüssel nicht gefunden/ungültig – ist /<key>.txt live?",
                422: "URLs gehören nicht zur Domain", 429: "zu viele Meldungen – später erneut"}.get(e.code, "")
        print(f"HTTP {e.code} {hint}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
