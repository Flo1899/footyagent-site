#!/usr/bin/env python3
"""Gleicht die Website-Fakten mit dem öffentlichen App-Store-Eintrag ab (iTunes-Lookup, kein Login).

    python3 _src/sync_appstore.py          # nur prüfen – Exit 1, wenn die Website veraltet ist
    python3 _src/sync_appstore.py --write  # product.json + releases.json aktualisieren, danach build.py

Übernommen werden: aktuelle Version + Datum, Mindest-iOS, Download-Größe und – bei einer neuen
Version – der »Neue Funktionen«-Text (en aus dem US-Store, de aus dem deutschen Store) als neuer
Eintrag auf /updates/. Preis, Altersfreigabe und Sprachanzahl werden nur verglichen, nicht geändert.
"""
from __future__ import annotations

import json
import pathlib
import re
import ssl
import sys
import urllib.request

SRC = pathlib.Path(__file__).resolve().parent
PRODUCT = SRC / "data/product.json"
RELEASES = SRC / "data/releases.json"


def lookup(app_id: str, country: str) -> dict:
    ctx = ssl.create_default_context()
    if pathlib.Path("/etc/ssl/cert.pem").exists():          # macOS-Python ohne eigene Zertifikate
        ctx.load_verify_locations("/etc/ssl/cert.pem")
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}&entity=software"
    with urllib.request.urlopen(url, timeout=30, context=ctx) as r:
        results = json.load(r).get("results") or []
    if not results:
        raise SystemExit(f"App {app_id} im Store {country} nicht gefunden")
    return results[0]


def notes(text: str | None) -> list[str]:
    lines = [re.sub(r"^\s*[•\-*–]\s*", "", l).strip() for l in (text or "").splitlines()]
    return [l for l in lines if l]


def main() -> int:
    write = "--write" in sys.argv
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    releases = json.loads(RELEASES.read_text(encoding="utf-8"))
    app = product["app"]
    us, de = lookup(str(app["appStoreId"]), "us"), lookup(str(app["appStoreId"]), "de")

    store = {
        "currentVersion": us["version"],
        "currentVersionDate": us["currentVersionReleaseDate"][:10],
        "minimumOs": us["minimumOsVersion"],
        "downloadSizeMB": round(int(us["fileSizeBytes"]) / 1_000_000),
    }
    diffs = {k: (app.get(k), v) for k, v in store.items() if app.get(k) != v}

    warn = []
    if float(us.get("price", 0)) != float(app["price"]): warn.append(f"Preis im Store {us.get('price')} ≠ {app['price']}")
    if us.get("contentAdvisoryRating") != app.get("ageRating"): warn.append(f"Altersfreigabe {us.get('contentAdvisoryRating')} ≠ {app.get('ageRating')}")
    if len(us.get("languageCodesISO2A") or []) != len(app["languages"]):
        warn.append(f"Store meldet {len(us['languageCodesISO2A'])} Sprachen ({', '.join(us['languageCodesISO2A'])}), "
                    f"product.json {len(app['languages'])} – Sprachliste von Hand prüfen")

    known = {r["version"] for r in releases["releases"]}
    new_release = None
    if us["version"] not in known:
        new_release = {"version": us["version"], "date": store["currentVersionDate"],
                       "en": {"title": None, "notes": notes(us.get("releaseNotes"))},
                       "de": {"title": None, "notes": notes(de.get("releaseNotes"))}}

    for w in warn: print("!", w)
    if not diffs and not new_release:
        print(f"OK – Website entspricht dem Store (Version {app['currentVersion']}).")
        return 0
    for k, (old, new) in diffs.items(): print(f"~ {k}: {old} → {new}")
    if new_release: print(f"+ neue Version {new_release['version']} ({new_release['date']}) für /updates/:",
                          *("  en: " + n for n in new_release["en"]["notes"]),
                          *("  de: " + n for n in new_release["de"]["notes"]), sep="\n")
    if not write:
        print("→ übernehmen mit: python3 _src/sync_appstore.py --write && python3 _src/build.py")
        return 1

    # Gezielt ersetzen statt neu serialisieren: die Dateien sind von Hand formatiert (kleine Diffs).
    raw = PRODUCT.read_text(encoding="utf-8")
    for k, (_, new) in diffs.items():
        raw, n = re.subn(rf'("{k}":\s*)("[^"]*"|\d+(?:\.\d+)?)', lambda m: m.group(1) + json.dumps(new), raw, count=1)
        if n != 1: raise SystemExit(f"{k} in product.json nicht gefunden")
    json.loads(raw)
    PRODUCT.write_text(raw, encoding="utf-8")
    if new_release:
        raw = RELEASES.read_text(encoding="utf-8")
        entry = "\n".join("  " + l for l in json.dumps(new_release, ensure_ascii=False, indent=1).splitlines())
        raw, n = re.subn(r'("releases":\s*\[\n)', lambda m: m.group(1) + entry + ",\n", raw, count=1)
        if n != 1: raise SystemExit("Liste »releases« in releases.json nicht gefunden")
        json.loads(raw)
        RELEASES.write_text(raw, encoding="utf-8")
    print("Geschrieben. Jetzt: python3 _src/build.py – und die neuen Texte auf /updates/ kurz ansehen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
