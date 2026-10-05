#!/usr/bin/env python3
"""SEO-/Struktur-Prüfung der fertigen Website (nur Python-Standardbibliothek).

    python3 _src/tests/test_site.py                          # prüft die Dateien im Repo
    python3 _src/tests/test_site.py --live https://footyagent.app   # zusätzlich die Live-Seite (nach dem Deploy)

Fehler (✗) → Exit 1. Hinweise (!) brechen nichts.
"""
from __future__ import annotations

import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / "_src/data/product.json").read_text(encoding="utf-8"))
ORIGIN = DATA["site"]["origin"].rstrip("/")
APP_ID = str(DATA["app"]["appStoreId"])
PT = str(DATA["appStore"]["providerToken"])
CTA_POSITIONS = {"hero", "header", "sticky_header", "body", "feature_page", "faq", "footer", "bottom_cta", "press_page"}
SKIP_DIRS = {"_src", ".git", ".github", "docs", "node_modules"}
NO_CTA = {"/datenschutz/"}               # Rechtstext ohne Knopf
# Reine Deko (Logo neben dem Schriftzug, Zierwappen): alt="" ist hier richtig, Screenshots brauchen Text.
DECORATIVE = {"footyagent-icon-96.webp", "icon.webp", "wappen-krone.webp", "wappen-pokal.webp"}

errors: list[str] = []
notes: list[str] = []
def err(page: str, msg: str): errors.append(f"✗ {page}: {msg}")
def note(page: str, msg: str): notes.append(f"! {page}: {msg}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None; self._in = []; self.texts = []; self.h1 = 0
        self.metas = []; self.links = []; self.anchors = []; self.imgs = []; self.scripts = []
        self.ids = set(); self.html_lang = None; self._script = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if "id" in a: self.ids.add(a["id"])
        if tag == "html": self.html_lang = a.get("lang")
        elif tag == "meta": self.metas.append(a)
        elif tag == "link": self.links.append(a)
        elif tag == "a": self.anchors.append(a)
        elif tag == "img": self.imgs.append(a)
        elif tag == "h1": self.h1 += 1
        elif tag == "script": self._script = {"attrs": a, "body": ""}
        if tag in ("title", "script", "style", "head"): self._in.append(tag)

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            self.scripts.append(self._script); self._script = None
        if self._in and self._in[-1] == tag: self._in.pop()

    def handle_data(self, data):
        if self._script is not None: self._script["body"] += data
        if self._in and self._in[-1] == "title": self.title = (self.title or "") + data
        elif not self._in: self.texts.append(data)

    def meta(self, key, value):
        return next((m.get("content", "") for m in self.metas if m.get(key) == value), None)

    def text(self):
        return re.sub(r"\s+", " ", " ".join(self.texts)).strip()


def url_path(file: pathlib.Path) -> str:
    rel = file.relative_to(ROOT).as_posix()
    if rel == "index.html": return "/"
    if rel.endswith("/index.html"): return "/" + rel[: -len("index.html")]
    return "/" + rel


def resolve(path: str) -> pathlib.Path | None:
    p = path.split("#")[0].split("?")[0]
    if not p.startswith("/"): return None
    f = ROOT / p.lstrip("/")
    if p.endswith("/"): f = f / "index.html"
    return f if f.is_file() else None


def jpeg_size(file: pathlib.Path):
    b = file.read_bytes(); i = 2
    while i < len(b):
        if b[i] != 0xFF: i += 1; continue
        marker = b[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
    return None


# ------------------------------------------------------------------ Seiten einlesen
pages: dict[str, tuple[pathlib.Path, Page]] = {}
for f in sorted(ROOT.rglob("*.html")):
    if set(f.relative_to(ROOT).parts) & SKIP_DIRS: continue
    p = Page(); p.feed(f.read_text(encoding="utf-8")); pages[url_path(f)] = (f, p)

titles, descs = {}, {}
for path, (f, p) in pages.items():
    is404 = path == "/404.html"
    robots = (p.meta("name", "robots") or "").lower()
    # Titel, Beschreibung, H1
    if not (p.title or "").strip(): err(path, "kein <title>")
    elif len(p.title) > 65: note(path, f"Titel {len(p.title)} Zeichen (Google kürzt ab ~60): {p.title}")
    desc = p.meta("name", "description")
    if not desc: err(path, "keine meta description")
    elif not 50 <= len(desc) <= 160: note(path, f"description {len(desc)} Zeichen (Google kürzt ab ~160)")
    if p.h1 != 1: err(path, f"{p.h1} × <h1> statt genau einer")
    if not p.html_lang: err(path, "<html lang> fehlt")
    if not is404:
        titles.setdefault(p.title, []).append(path); descs.setdefault(desc, []).append(path)
    # Indexierbarkeit + Canonical
    canon = next((l.get("href") for l in p.links if l.get("rel") == "canonical"), None)
    if is404:
        if "noindex" not in robots: err(path, "404-Seite ohne noindex")
    else:
        if "noindex" in robots: err(path, "noindex auf öffentlicher Seite")
        if canon != ORIGIN + path: err(path, f"Canonical {canon!r} ≠ {ORIGIN + path!r}")
    # hreflang
    alts = {l["hreflang"]: l.get("href") for l in p.links if l.get("rel") == "alternate" and l.get("hreflang")}
    if alts:
        if alts.get(p.html_lang) != ORIGIN + path: err(path, f"hreflang ohne Selbstverweis für {p.html_lang}")
        if "x-default" not in alts: err(path, "hreflang ohne x-default")
        for code, href in alts.items():
            if code == "x-default": continue
            other = pages.get(href.replace(ORIGIN, ""))
            if not other: err(path, f"hreflang {code} zeigt auf fehlende Seite {href}"); continue
            back = {l["hreflang"]: l.get("href") for l in other[1].links if l.get("rel") == "alternate" and l.get("hreflang")}
            if back.get(p.html_lang) != ORIGIN + path: err(path, f"hreflang {code} nicht gegenseitig ({href})")
    # Open Graph
    for prop in ("og:title", "og:description", "og:image", "og:url"):
        if not is404 and path != "/datenschutz/" and not p.meta("property", prop): err(path, f"{prop} fehlt")
    # Skripte: Konfiguration, JSON-LD, nichts Fremdes
    for s in p.scripts:
        src, typ = s["attrs"].get("src"), s["attrs"].get("type", "")
        if src and re.match(r"(?i)https?://", src): err(path, f"externes Skript {src}")
        if typ == "application/ld+json":
            try: ld = json.loads(s["body"])
            except json.JSONDecodeError as e: err(path, f"JSON-LD kaputt: {e}"); continue
            blob = json.dumps(ld)
            for bad in ("aggregateRating", "ratingValue", "reviewCount", '"review"'):
                if bad in blob: err(path, f"JSON-LD enthält {bad} (keine erfundenen Bewertungen)")
            if "ct=" in blob: err(path, "JSON-LD enthält Kampagnen-Link (soll neutral sein)")
            for node in ld.get("@graph", [ld]):
                types = node.get("@type"); types = types if isinstance(types, list) else [types]
                if "MobileApplication" in types or "VideoGame" in types:
                    offer = node.get("offers") or {}
                    if str(offer.get("price")) != DATA["app"]["price"]: err(path, f"JSON-LD-Preis {offer.get('price')!r}")
                    if node.get("softwareVersion") != DATA["app"]["currentVersion"]: err(path, "JSON-LD-Version veraltet")
        if s["attrs"].get("id") == "fa-config":
            try: cfg = json.loads(s["body"])
            except json.JSONDecodeError as e: err(path, f"fa-config kaputt: {e}"); continue
            if cfg["page"]["lang"] != p.html_lang: err(path, "fa-config-Sprache ≠ <html lang>")
            if cfg["page"]["path"] != path: err(path, f"fa-config-Pfad {cfg['page']['path']} ≠ {path}")
    for l in p.links:
        if "stylesheet" in (l.get("rel") or "") and re.match(r"(?i)https?://", l.get("href", "")):
            err(path, f"externes Stylesheet {l['href']}")
    # Bilder
    for img in p.imgs:
        src = img.get("src", "")
        if "alt" not in img: err(path, f"Bild ohne alt: {src}")
        elif not img["alt"].strip() and src.rsplit("/", 1)[-1] not in DECORATIVE: err(path, f"Inhaltsbild ohne Alt-Text: {src}")
        elif img["alt"].strip() and len(img["alt"]) < 15: note(path, f"sehr kurzer Alt-Text {img['alt']!r}")
        if src.startswith("/") and not resolve(src): err(path, f"Bild fehlt: {src}")
        if not (img.get("width") and img.get("height")): note(path, f"Bild ohne width/height (Layout-Sprung): {src}")
    # Links
    ctas = 0
    for a in p.anchors:
        href = a.get("href", "")
        if href.startswith(ORIGIN): href = href[len(ORIGIN):] or "/"
        if "apps.apple.com" in href:
            pos = a.get("data-cta")
            if pos is None: err(path, f"App-Store-Link ohne data-cta: {href}")
            elif pos not in CTA_POSITIONS: err(path, f"unbekannte cta_position {pos!r}")
            if f"id{APP_ID}" not in href or f"pt={PT}" not in href or "ct=" not in href:
                err(path, f"App-Store-Knopf ohne Kampagnen-Link: {href}")
            ctas += 1
        elif href.startswith("#"):
            if href[1:] and href[1:] not in p.ids: err(path, f"Anker fehlt: {href}")
        elif href.startswith("/"):
            target = resolve(href)
            if not target: err(path, f"toter interner Link: {href}")
            elif "#" in href:
                frag = href.split("#", 1)[1]
                tp = pages.get(url_path(target))
                if frag and tp and frag not in tp[1].ids: err(path, f"Anker fehlt auf Zielseite: {href}")
        elif href.startswith("http://"):
            err(path, f"unsicherer Link (http): {href}")
    if not is404 and path not in NO_CTA and ctas == 0: err(path, "kein App-Store-Knopf")

for t, ps in titles.items():
    if len(ps) > 1: err(", ".join(ps), f"doppelter Titel {t!r}")
for d, ps in descs.items():
    if len(ps) > 1: err(", ".join(ps), "doppelte description")

# ------------------------------------------------------------------ Startseite: erste 100 Wörter
for path, needed in (("/", ["FootyAgent", "iPhone", "iPad", "agent", "manager"]),
                     ("/de/", ["FootyAgent", "iPhone", "iPad", "Berater", "Verein"])):
    first = " ".join(pages[path][1].text().split()[:130])   # ~100 Wörter Fließtext nach Navigation
    for w in needed:
        if w.lower() not in first.lower(): err(path, f"»{w}« nicht in den ersten ~100 Wörtern")

# ------------------------------------------------------------------ OG-Bild
og = resolve(DATA["site"]["ogImage"])
if not og: err("product.json", f"OG-Bild fehlt: {DATA['site']['ogImage']}")
elif og.suffix.lower() in (".jpg", ".jpeg") and jpeg_size(og) != (1200, 630): err(og.name, f"OG-Bild {jpeg_size(og)} statt 1200×630")

# ------------------------------------------------------------------ Sitemap, robots, llms.txt
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [e.text for e in ET.parse(ROOT / "sitemap.xml").getroot().findall("s:url/s:loc", ns)]
for loc in locs:
    path = loc.replace(ORIGIN, "")
    if path not in pages: err("sitemap.xml", f"Eintrag ohne Seite: {loc}")
    elif "noindex" in (pages[path][1].meta("name", "robots") or ""): err("sitemap.xml", f"noindex-Seite gelistet: {loc}")
for path in pages:
    if path != "/404.html" and ORIGIN + path not in locs: err("sitemap.xml", f"Seite fehlt: {path}")
if len(set(locs)) != len(locs): err("sitemap.xml", "doppelte Einträge")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
groups = {}
for block in re.split(r"\n\s*\n", robots):
    agents = re.findall(r"(?im)^user-agent:\s*(\S+)", block)
    rules = re.findall(r"(?im)^(allow|disallow):\s*(\S*)", block)
    for ag in agents: groups[ag.lower()] = rules
for bot in ("*", "oai-searchbot"):
    rules = groups.get(bot, groups.get("*", []))
    if any(k.lower() == "disallow" and v == "/" for k, v in rules): err("robots.txt", f"{bot} komplett gesperrt")
if "oai-searchbot" not in groups: err("robots.txt", "OAI-SearchBot nicht ausdrücklich erlaubt")
if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots: err("robots.txt", "Sitemap-Zeile fehlt/falsch")

for url in re.findall(r"\]\((https?://[^)]+)\)", (ROOT / "llms.txt").read_text(encoding="utf-8")):
    if url.startswith(ORIGIN) and url.replace(ORIGIN, "") not in pages: err("llms.txt", f"toter Link {url}")
    if "apps.apple.com" in url and "ct=" in url: err("llms.txt", "Kampagnen-Link (soll neutral sein)")

if "td.js" in "".join(f.read_text(encoding="utf-8") for f, _ in pages.values()): err("site", "Verweis auf altes td.js")


# ------------------------------------------------------------------ Live (optional)
def live(base: str):
    ctx = ssl.create_default_context(cafile="/etc/ssl/cert.pem") if pathlib.Path("/etc/ssl/cert.pem").exists() else None
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), NoRedirect)
    def get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)"})
        try:
            with opener.open(req, timeout=30) as r: return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e: return e.code, dict(e.headers), ""
    for path in ["/robots.txt", "/sitemap.xml", "/llms.txt", DATA["site"]["ogImage"]] + [l.replace(ORIGIN, "") for l in locs]:
        st, hdr, body = get(base + path)
        if st != 200: err(f"LIVE {path}", f"HTTP {st} (als OAI-SearchBot)")
        elif path.endswith("/") and f'<link rel="canonical" href="{ORIGIN + path}">' not in body:
            err(f"LIVE {path}", "Canonical stimmt live nicht")
    st, _, _ = get(base + "/gibt-es-nicht-" + "x" * 6 + "/")
    if st != 404: err("LIVE 404", f"fehlende Seite liefert HTTP {st} statt 404")
    st, hdr, _ = get("https://footyagent.de/")
    if st not in (301, 302, 308):                       # IONOS-Weiterleitung = 302 (kein 301 möglich), bekannt
        err("LIVE footyagent.de", f"Weiterleitung kaputt: HTTP {st}")
    elif (hdr.get("location") or hdr.get("Location") or "").rstrip("/") != ORIGIN:
        err("LIVE footyagent.de", f"leitet nicht auf {ORIGIN} weiter")


if "--live" in sys.argv:
    live(sys.argv[sys.argv.index("--live") + 1].rstrip("/"))

print("\n".join(notes))
print("\n".join(errors))
print(f"{len(pages)} Seiten, {len(locs)} Sitemap-Einträge geprüft: {len(errors)} Fehler, {len(notes)} Hinweise")
sys.exit(1 if errors else 0)
