#!/usr/bin/env python3
"""footyagent.app – statischer Seitengenerator (nur Python-Standardbibliothek).

Warum es ihn gibt: Die Website bleibt reines HTML auf GitHub Pages (kein Framework, kein
JavaScript für Inhalte – Crawler wie OAI-SearchBot führen kein JS aus). Damit Fakten trotzdem
nur an EINER Stelle stehen, erzeugt dieses Skript alle Seiten aus
    _src/data/product.json   Produktfakten, App-Store-Kampagnen, Analytics-Konfiguration
    _src/data/faq.json       FAQ (sichtbar + FAQPage-JSON-LD)
    _src/data/releases.json  Versionshistorie (/updates/)
    _src/pages/<lang>/*.html Seitentexte mit Kopfblock (Titel, Beschreibung, Pfad …)
    _src/site-base.css + _src/site-extra.css  Design (wird in jede Seite eingebettet)

Aufruf:
    python3 _src/build.py          # baut alles ins Repo-Wurzelverzeichnis
    python3 _src/build.py --check  # baut nichts, meldet nur Abweichungen (Exit 1 = veraltet)

Jekyll (GitHub Pages) ignoriert _src/ (Unterstrich) – die Quellen werden nicht veröffentlicht.
"""
from __future__ import annotations

import datetime
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
DATA = json.loads((SRC / "data/product.json").read_text("utf-8"))
FAQ = json.loads((SRC / "data/faq.json").read_text("utf-8"))
RELEASES = json.loads((SRC / "data/releases.json").read_text("utf-8"))["releases"]
SITE, APP, N, TERMS = DATA["site"], DATA["app"], DATA["app"]["numbers"], DATA["terms"]
ORIGIN = SITE["origin"]

# ------------------------------------------------------------------ Texte je Sprache
UI = {
    "en": {
        "skip": "Skip to content", "home": "Home", "nav": [("/football-agent-game/", "The game"),
            ("/how-it-works/", "How it works"), ("/faq/", "FAQ")],
        "nav_label": "Main", "lang_label": "Language", "store_small": "Download on the",
        "store_note": "Free · iPhone & iPad · iOS {os}+", "crumbs": "Breadcrumb",
        "hint": "This page is also available in English.", "hint_link": "Read in English",
        "close": "Close", "tagline": "The football agent game for iPhone and iPad.",
        "foot_game": "Game", "foot_features": "Features", "foot_info": "Info",
        "privacy": "Privacy & imprint", "support": "Support", "follow": "Follow",
        "og_locale": "en_US", "og_alt": "FootyAgent – the football agent game for iPhone and iPad",
    },
    "de": {
        "skip": "Zum Inhalt springen", "home": "Start", "nav": [("/de/fussball-berater-spiel/", "Das Spiel"),
            ("/de/faq/", "FAQ"), ("/how-it-works/", "So funktioniert's (EN)")],
        "nav_label": "Hauptnavigation", "lang_label": "Sprache", "store_small": "Laden im",
        "store_note": "Kostenlos · iPhone & iPad · ab iOS {os}", "crumbs": "Brotkrumen",
        "hint": "Diese Seite gibt es auch auf Deutsch.", "hint_link": "Auf Deutsch lesen",
        "close": "Schließen", "tagline": "Das Fußball-Berater-Spiel für iPhone und iPad.",
        "foot_game": "Spiel", "foot_features": "Funktionen (englisch)", "foot_info": "Info",
        "privacy": "Datenschutz & Impressum", "support": "Support", "follow": "Folgen",
        "og_locale": "de_DE", "og_alt": "FootyAgent – das Fußball-Berater-Spiel für iPhone und iPad",
    },
}

EXPLORE = {
    "en": [
        ("/football-agent-game/", "The football agent game", "What FootyAgent is and how it differs from a manager game."),
        ("/football-agent-game-ios/", "On iPhone & iPad", "Requirements, price, offline play and iCloud."),
        ("/how-it-works/", "How it works", "Weeks, seasons, transfer windows and your inbox."),
        ("/features/scouting/", "Scouting", "Find talent – and see through the uncertainty."),
        ("/features/negotiations/", "Negotiations", "Commission, playing time, contract length and wages."),
        ("/features/transfers/", "Transfers & loans", "Offers, pitching clients to clubs and loan deals."),
        ("/features/agency-management/", "Agency management", "Office, staff, licences, specialisations, club shares."),
        ("/offline-football-game/", "Offline play", "What works without internet (everything that matters)."),
        ("/faq/", "FAQ", "Short answers to common questions."),
        ("/updates/", "Updates", "Every version since the launch."),
        ("/press/", "Press kit", "Facts, descriptions, screenshots and contact."),
    ],
    "de": [
        ("/de/fussball-berater-spiel/", "Das Fußball-Berater-Spiel", "Was FootyAgent ist und was es vom Fußball-Manager unterscheidet."),
        ("/de/faq/", "Häufige Fragen", "Kurze Antworten auf die wichtigsten Fragen."),
        ("/how-it-works/", "How it works (englisch)", "Wochen, Saisons, Transferfenster und dein Postfach."),
        ("/features/negotiations/", "Negotiations (englisch)", "Provision, Spielzeit, Laufzeit und Gehalt im Detail."),
        ("/updates/", "Updates (englisch)", "Alle Versionen seit dem Start."),
        ("/press/", "Press kit (englisch)", "Fakten, Texte, Screenshots und Kontakt."),
    ],
}

FOOTER = {
    "en": {"game": [("/football-agent-game/", "Football agent game"), ("/football-agent-game-ios/", "iPhone & iPad"),
                    ("/how-it-works/", "How it works"), ("/offline-football-game/", "Offline play")],
           "features": [("/features/scouting/", "Scouting"), ("/features/negotiations/", "Negotiations"),
                        ("/features/transfers/", "Transfers"), ("/features/agency-management/", "Agency management")],
           "info": [("/faq/", "FAQ"), ("/updates/", "Updates"), ("/press/", "Press"), ("/about/", "About")]},
    "de": {"game": [("/de/", "Start"), ("/de/fussball-berater-spiel/", "Fußball-Berater-Spiel"), ("/de/faq/", "Häufige Fragen")],
           "features": [("/features/scouting/", "Scouting"), ("/features/negotiations/", "Verhandlungen"),
                        ("/features/transfers/", "Transfers"), ("/features/agency-management/", "Agentur-Management")],
           "info": [("/updates/", "Updates"), ("/press/", "Presse"), ("/about/", "Über FootyAgent")]},
}

APPLE_SVG = ('<svg viewBox="0 0 384 512" aria-hidden="true"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>')
CHECK_SVG = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6.2 12.5 2 8.3l1.5-1.5 2.7 2.7L12.5 3 14 4.5z"/></svg>'

esc = lambda s: html.escape(str(s), quote=True)
MACROS = {"steckbrief", "faq", "releases", "explore", "storeurl", "storecanonical"}


# ------------------------------------------------------------------ Hilfen
def store_url(channel: str = "default") -> str:
    a = DATA["appStore"]
    ct = a["campaigns"].get(channel) or a["campaigns"]["default"]
    return f'{a["baseUrl"]}?pt={a["providerToken"]}&ct={ct}&mt=8'


def store_canonical() -> str:
    """Neutraler Store-Link ohne Kampagne – für alles, was Maschinen oder Dritte weiterverwenden
    (JSON-LD, llms.txt, Pressemappe). Mit Kampagne zählte Apple z. B. einen Klick direkt aus einer
    ChatGPT-Antwort als Website-Besuch. Kampagnen-Links gibt es nur an echten Knöpfen der Website."""
    return f'https://apps.apple.com/app/id{APP["appStoreId"]}'


def lang_list(lang: str) -> str:
    names = [l[lang] for l in APP["languages"]]
    joiner = " and " if lang == "en" else " und "
    return ", ".join(names[:-1]) + joiner + names[-1]


def fmt_date(iso: str, lang: str) -> str:
    d = datetime.date.fromisoformat(iso)
    if lang == "de":
        monate = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
                  "Oktober", "November", "Dezember"]
        return f"{d.day}. {monate[d.month - 1]} {d.year}"
    return d.strftime("%B %-d, %Y")


def lookup(path: str, lang: str):
    """{{a.b.c}} – Punktpfad in einen Kontext; Sonderfälle siehe unten."""
    ctx = {"n": N, "app": APP, "site": SITE, "t": TERMS}
    if path == "langlist":
        return lang_list(lang)
    if path == "releasecount":
        return str(len(RELEASES))
    if path == "langcount":
        return str(len(APP["languages"]))
    if path == "year":
        return str(datetime.date.today().year)
    if path == "version":
        return APP["currentVersion"]
    if path == "versionDate":
        return fmt_date(APP["currentVersionDate"], lang)
    if path == "releaseDate":
        return fmt_date(APP["releaseDate"], lang)
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def fill(text: str, lang: str) -> str:
    """Ersetzt {{pfad}} durch (escapten) Wert aus den Daten. Unbekannt = Abbruch (kein stiller Fehler)."""
    def rep(m):
        if m.group(1).strip() in MACROS:          # Bausteine erledigt macros()
            return m.group(0)
        val = lookup(m.group(1).strip(), lang)
        if isinstance(val, (dict, list)):
            raise SystemExit(f"Platzhalter {{{{{m.group(1)}}}}} zeigt auf keinen Einzelwert")
        return esc(val)
    return re.sub(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}", rep, text)


def cta(pos: str, lang: str, note: bool = True, cls: str = "") -> str:
    u = UI[lang]
    btn = (f'<a class="knopf{(" " + cls) if cls else ""}" data-cta="{esc(pos)}" href="{esc(store_url())}">{APPLE_SVG}'
           f'<span><span class="klein">{u["store_small"]}</span><span class="gross">App&nbsp;Store</span></span></a>')
    if not note:
        return btn
    return (f'<div class="cta-reihe">{btn}<span class="cta-notiz">'
            f'{esc(u["store_note"].format(os=APP["minimumOs"].split(".")[0]))}</span></div>')


def steckbrief(lang: str) -> str:
    rows = {
        "en": [("Platform", "iPhone and iPad (iOS/iPadOS " + APP["minimumOs"].split(".")[0] + " or later)"),
               ("Genre", APP["category"]["en"] + " · " + " / ".join(APP["genres"]["en"])),
               ("Price", "Free · no ads · optional one-time Pro Pack"),
               ("Mode", APP["mode"]["en"]),
               ("Internet", APP["offline"]["en"]),
               ("Languages", lang_list("en")),
               ("Current version", f'{APP["currentVersion"]} ({fmt_date(APP["currentVersionDate"], "en")})'),
               ("Developer", f'{APP["developer"]} ({APP["developerCountry"]["en"]})')],
        "de": [("Plattform", "iPhone und iPad (ab iOS/iPadOS " + APP["minimumOs"].split(".")[0] + ")"),
               ("Genre", APP["category"]["de"] + " · " + " / ".join(APP["genres"]["de"])),
               ("Preis", "Kostenlos · keine Werbung · optionales Pro-Paket (Einmalkauf)"),
               ("Modus", APP["mode"]["de"]),
               ("Internet", APP["offline"]["de"]),
               ("Sprachen", lang_list("de")),
               ("Aktuelle Version", f'{APP["currentVersion"]} ({fmt_date(APP["currentVersionDate"], "de")})'),
               ("Entwickler", f'{APP["developer"]} ({APP["developerCountry"]["de"]})')],
    }[lang]
    inner = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in rows)
    return f'<dl class="steckbrief">{inner}</dl>'


def shot(arg: str) -> str:
    """{{shot:datei.webp|Alt-Text|Bildunterschrift}} – Gerät mit Screenshot."""
    parts = [p.strip() for p in arg.split("|")]
    src, alt = parts[0], parts[1]
    cap = parts[2] if len(parts) > 2 else ""
    if not (ROOT / "assets" / src).exists():
        raise SystemExit(f"Bild fehlt: assets/{src}")
    fig = (f'<figure class="bild"><div class="phone"><img loading="lazy" decoding="async" src="/assets/{esc(src)}" '
           f'width="660" height="1434" alt="{esc(alt)}"></div>')
    if cap:
        fig += f"<figcaption>{esc(cap)}</figcaption>"
    return fig + "</figure>"


def faq_html(lang: str) -> str:
    items = []
    for f in FAQ[lang]:
        a = fill(f["a"], lang)
        items.append(f'<details data-faq="{esc(f["id"])}" id="{esc(f["id"])}"><summary><h2>{esc(f["q"])}</h2></summary>'
                     f"<p>{a}</p></details>")
    return '<div class="faq">' + "\n".join(items) + "</div>"


def releases_html(lang: str) -> str:
    out = []
    for r in RELEASES:
        t = r.get(lang) or r.get("en")
        notes = "".join(f"<li>{esc(n)}</li>" for n in t["notes"])
        title = f'<p class="titel">{esc(t["title"])}</p>' if t.get("title") else ""
        out.append(f'<li id="v{esc(r["version"].replace(".", "-"))}"><h2>Version {esc(r["version"])}'
                   f'<time datetime="{r["date"]}">{esc(fmt_date(r["date"], lang))}</time></h2>{title}'
                   f"<ul>{notes}</ul></li>")
    return '<ol class="versionen">' + "\n".join(out) + "</ol>"


def explore(lang: str, exclude: str) -> str:
    items = [f'<li><a href="{esc(h)}"><b>{esc(t)}</b><span>{esc(d)}</span></a></li>'
             for h, t, d in EXPLORE[lang] if h != exclude]
    return '<ul class="weiter-grid">' + "".join(items) + "</ul>"


def checklist(arg: str) -> str:
    """{{punkte}} … {{/punkte}} wird nicht genutzt; Listenpunkte mit Haken: {{haken:Fett|Text}}."""
    b, t = (arg.split("|", 1) + [""])[:2]          # Seitentext ist vertrauenswürdiges HTML
    return f'<li>{CHECK_SVG}<span><b>{b}</b> {t}</span></li>'


def macros(text: str, page: dict) -> str:
    lang = page["lang"]
    text = fill(text, lang)                          # erst Daten-Platzhalter (auch in Bausteinen)
    text = re.sub(r"\{\{cta:([a-z_]+)\}\}", lambda m: cta(m.group(1), lang), text)
    text = re.sub(r"\{\{ctabtn:([a-z_]+)\}\}", lambda m: cta(m.group(1), lang, note=False), text)
    text = re.sub(r"\{\{shot:([^}]+)\}\}", lambda m: shot(m.group(1)), text)
    text = re.sub(r"\{\{haken:([^}]+)\}\}", lambda m: checklist(m.group(1)), text)
    text = text.replace("{{steckbrief}}", steckbrief(lang))
    text = text.replace("{{faq}}", faq_html(lang))
    text = text.replace("{{releases}}", releases_html(lang))
    text = text.replace("{{explore}}", explore(lang, page["path"]))
    text = text.replace("{{storeurl}}", esc(store_url()))
    text = text.replace("{{storecanonical}}", esc(store_canonical()))
    return text


# ------------------------------------------------------------------ Seiten einlesen
def read_pages() -> list[dict]:
    pages = []
    for f in sorted((SRC / "pages").rglob("*.html")):
        raw = f.read_text("utf-8")
        m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
        if not m:
            raise SystemExit(f"{f}: Kopfblock fehlt")
        meta = {}
        for line in m.group(1).splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["body"] = raw[m.end():]
        meta["src"] = str(f.relative_to(SRC))
        for req in ("id", "lang", "path", "title", "description", "type"):
            if not meta.get(req):
                raise SystemExit(f"{f}: Feld '{req}' fehlt")
        for k in ("title", "description"):          # Zahlen/Version auch in Titel + Beschreibung aus den Daten
            meta[k] = html.unescape(fill(meta[k], meta["lang"]))
        meta["schema"] = [s.strip() for s in meta.get("schema", "").split(",") if s.strip()]
        pages.append(meta)
    return pages


PAGES = read_pages()
BY_ID = {p["id"]: p for p in PAGES}


def alternates(page: dict) -> dict:
    if not page.get("pair"):
        return {}
    return {p["lang"]: p["path"] for p in PAGES if p.get("pair") == page["pair"]}


def lang_switch_targets(page: dict) -> dict:
    alt = alternates(page)
    return {"en": alt.get("en", "/"), "de": alt.get("de", "/de/")}


# ------------------------------------------------------------------ JSON-LD
def jsonld(page: dict) -> str:
    lang = page["lang"]
    graph = []
    dev = {"@type": "Person", "@id": f"{ORIGIN}/#developer", "name": APP["developer"],
           "url": f"{ORIGIN}/about/"}
    shots = ["footyagent-transfer-decision.webp", "footyagent-inbox-transfer-offers.webp",
             "footyagent-agent-contract-negotiation.webp", "footyagent-agency-promotion.webp"]
    app = {
        "@type": ["VideoGame", "MobileApplication"], "@id": f"{ORIGIN}/#app",
        "name": APP["name"], "url": f"{ORIGIN}/",
        "description": {"en": ("FootyAgent is a single-player football agent simulation for iPhone and iPad. "
                               "Scout talents, negotiate contracts, wages and transfers, and grow your agency "
                               "from a local office into a worldwide agency."),
                        "de": ("FootyAgent ist eine Spielerberater-Simulation für iPhone und iPad im Einzelspieler. "
                               "Scoute Talente, verhandle Verträge, Gehälter und Transfers und baue deine Agentur "
                               "vom lokalen Büro zur Weltagentur aus.")}[lang],
        "applicationCategory": "GameApplication",
        "genre": APP["genres"]["en"], "gamePlatform": APP["devices"],
        "operatingSystem": f'iOS {APP["minimumOs"]} or later, iPadOS {APP["minimumOs"]} or later',
        "playMode": "SinglePlayer", "numberOfPlayers": {"@type": "QuantitativeValue", "value": 1},
        "inLanguage": [l["code"] for l in APP["languages"]],
        "contentRating": APP["ageRating"], "datePublished": APP["releaseDate"],
        "softwareVersion": APP["currentVersion"], "dateModified": APP["currentVersionDate"],
        "fileSize": f'{APP["downloadSizeMB"]} MB', "isAccessibleForFree": True,
        "image": f"{ORIGIN}/assets/apple-touch-icon.png",
        "screenshot": [f"{ORIGIN}/assets/{s}" for s in shots],
        "author": {"@id": dev["@id"]}, "publisher": {"@id": dev["@id"]},
        "installUrl": store_canonical(), "downloadUrl": store_canonical(),
        "offers": {"@type": "Offer", "price": APP["price"], "priceCurrency": APP["priceCurrency"],
                   "availability": "https://schema.org/InStock", "url": store_canonical()},
        "sameAs": [store_canonical()] + [s["url"] for s in DATA["social"]],
    }
    website = {"@type": "WebSite", "@id": f"{ORIGIN}/#website", "url": f"{ORIGIN}/", "name": SITE["name"],
               "inLanguage": ["en", "de"], "publisher": {"@id": dev["@id"]}}
    webpage = {"@type": {"faq": "FAQPage", "about": "AboutPage"}.get(page["type"], "WebPage"),
               "@id": f'{ORIGIN}{page["path"]}#webpage', "url": f'{ORIGIN}{page["path"]}',
               "name": page["title"], "description": page["description"], "inLanguage": lang,
               "isPartOf": {"@id": website["@id"]}, "about": {"@id": app["@id"]}}
    if page["type"] == "faq":
        webpage["mainEntity"] = [{"@type": "Question", "name": f["q"],
                                  "acceptedAnswer": {"@type": "Answer", "text": fill(f["a"], lang)}}
                                 for f in FAQ[lang]]
    graph += [webpage, website, dev]
    if "app" in page["schema"]:
        graph.append(app)
    crumbs = breadcrumb_items(page)
    if len(crumbs) > 1:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{ORIGIN}{href}"}
            for i, (href, name) in enumerate(crumbs)]})
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return data.replace("</", "<\\/")


def breadcrumb_items(page: dict) -> list[tuple[str, str]]:
    if page["type"] in ("home", "error"):
        return []
    home = "/" if page["lang"] == "en" else "/de/"
    items = [(home, UI[page["lang"]]["home"])]
    parent = page.get("parent")
    if parent:
        par = BY_ID[parent]
        items.append((par["path"], par.get("crumb") or par["title"]))
    items.append((page["path"], page.get("crumb") or page["title"]))
    return items


# ------------------------------------------------------------------ Seite zusammensetzen
CSS_RAW = (SRC / "site-base.css").read_text("utf-8") + "\n" + (SRC / "site-extra.css").read_text("utf-8")


def mini_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    return css.strip()


CSS = mini_css(CSS_RAW)
BUILD_ID = hashlib.sha1((json.dumps(DATA, sort_keys=True) + json.dumps(RELEASES) +
                         (ROOT / "assets/site.js").read_text("utf-8")).encode()).hexdigest()[:10]


def head(page: dict) -> str:
    lang, u = page["lang"], UI[page["lang"]]
    canon = f'{ORIGIN}{page["path"]}'
    out = ['<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
           f'<title>{esc(page["title"])}</title>',
           f'<meta name="description" content="{esc(page["description"])}">']
    if page["type"] == "error":
        out.append('<meta name="robots" content="noindex">')
    else:
        out.append(f'<link rel="canonical" href="{esc(canon)}">')
        alt = alternates(page)
        if len(alt) > 1:
            for l, p in sorted(alt.items()):
                out.append(f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{p}">')
            out.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{alt.get("en", page["path"])}">')
    out += [f'<meta name="theme-color" content="{SITE["themeColor"]}">',
            '<link rel="icon" href="/assets/favicon.png" sizes="64x64">',
            '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
            '<meta property="og:type" content="website">',
            f'<meta property="og:site_name" content="{esc(SITE["name"])}">',
            f'<meta property="og:title" content="{esc(page.get("og_title") or page["title"])}">',
            f'<meta property="og:description" content="{esc(page["description"])}">',
            f'<meta property="og:url" content="{esc(canon)}">',
            f'<meta property="og:image" content="{ORIGIN}{SITE["ogImage"]}">',
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{esc(u["og_alt"])}">',
            f'<meta property="og:locale" content="{u["og_locale"]}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:site" content="{esc(SITE["xHandle"])}">']
    v = DATA["verification"]
    if v.get("google"):
        out.append(f'<meta name="google-site-verification" content="{esc(v["google"])}">')
    if v.get("bing"):
        out.append(f'<meta name="msvalidate.01" content="{esc(v["bing"])}">')
    out.append(f"<style>{CSS}</style>")
    if page["type"] != "error":
        out.append(f'<script type="application/ld+json">\n{jsonld(page)}\n</script>')
    a = DATA["analytics"]
    cfg = {"build": BUILD_ID,
           "page": {"lang": lang, "type": page["type"], "path": page["path"], "alternates": alternates(page)},
           "appStore": DATA["appStore"] | {"_hinweis": None},
           "analytics": {"key": a["posthogKey"], "host": a["posthogHost"], "uiHost": a["posthogUiHost"],
                         "defaults": a["posthogDefaults"], "cookieless": a["cookielessMode"]}}
    cfg["appStore"].pop("_hinweis", None)
    out.append('<script id="fa-config" type="application/json">' +
               json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")
    return "\n".join(out)


def header(page: dict) -> str:
    lang, u = page["lang"], UI[page["lang"]]
    home = "/" if lang == "en" else "/de/"
    cur_attr, mobil_attr = ' aria-current="page"', ' class="weg-mobil"'
    nav = "".join(
        f'<a href="{esc(h)}"{cur_attr if h == page["path"] else ""}'
        f'{mobil_attr if i == 2 else ""}>{esc(t)}</a>' for i, (h, t) in enumerate(u["nav"]))
    tgt = lang_switch_targets(page)
    on_attr = ' aria-current="true"'
    switch = "".join(
        f'<a href="{esc(tgt[l])}" hreflang="{l}" lang="{l}" data-setlang="{l}"'
        f'{on_attr if l == lang else ""}>{l.upper()}</a>' for l in ("en", "de"))
    hint = ""
    if len(alternates(page)) > 1:
        other = "de" if lang == "en" else "en"
        hint = (f'<div id="sprachhinweis" class="sprachhinweis" lang="{other}" hidden><div class="seite">'
                f'<span>{esc(UI[other]["hint"])}</span>'
                f'<a href="{esc(alternates(page)[other])}" data-setlang="{other}">{esc(UI[other]["hint_link"])} →</a>'
                f'<button type="button" aria-label="{esc(u["close"])}">×</button></div></div>')
    return (f'<a class="skip" href="#inhalt">{esc(u["skip"])}</a>\n'
            '<div class="buehne" aria-hidden="true"><div class="rasen"></div><div class="mittellinie"></div>'
            '<div class="mittelkreis"></div></div>\n'
            f'{hint}<header class="top"><div class="top-in">'
            f'<a class="marke" href="{home}" style="text-decoration:none;color:inherit">'
            '<img src="/assets/footyagent-icon-96.webp" alt="" width="30" height="30">'
            '<span>Footy<span class="gruen">Agent</span></span></a>'
            f'<nav class="nav" aria-label="{esc(u["nav_label"])}">{nav}</nav>'
            f'<div class="top-rechts"><nav class="sprache" aria-label="{esc(u["lang_label"])}">{switch}</nav>'
            f'{cta("header", lang, note=False, cls="mini")}</div></div></header>')


def crumbs_html(page: dict) -> str:
    items = breadcrumb_items(page)
    if len(items) < 2:
        return ""
    lis = []
    for i, (href, name) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{esc(name)}</span></li>')
        else:
            lis.append(f'<li><a href="{esc(href)}">{esc(name)}</a></li>')
    return (f'<div class="seite"><nav class="krumen" aria-label="{esc(UI[page["lang"]]["crumbs"])}">'
            f'<ol>{"".join(lis)}</ol></nav></div>')


def footer(page: dict) -> str:
    lang, u, f = page["lang"], UI[page["lang"]], FOOTER[page["lang"]]
    col = lambda title, links: (f'<nav aria-label="{esc(title)}"><b>{esc(title)}</b>' +
                                "".join(f'<a href="{esc(h)}">{esc(t)}</a>' for h, t in links) + "</nav>")
    social = "".join(f'<a href="{esc(s["url"])}" rel="me noopener">{esc(s["name"])}</a>' for s in DATA["social"])
    return (f'<footer><div class="foot-in foot-spalten">'
            f'<div><span class="marke"><img src="/assets/footyagent-icon-96.webp" alt="" width="30" height="30" loading="lazy">'
            f'<span>Footy<span class="gruen">Agent</span></span></span><p>{esc(u["tagline"])}</p>'
            f'<div class="foot-sozial" aria-label="{esc(u["follow"])}">{social}</div></div>'
            f'{col(u["foot_game"], f["game"])}{col(u["foot_features"], f["features"])}{col(u["foot_info"], f["info"])}'
            f'</div><div class="foot-in"><span>© {datetime.date.today().year} {esc(APP["developer"])} · FootyAgent</span>'
            f'<span class="foot-links"><a href="/datenschutz/">{esc(u["privacy"])}</a>'
            f'<a href="mailto:{esc(SITE["supportEmail"])}">{esc(u["support"])}</a></span></div></footer>')


def render(page: dict) -> str:
    body = macros(page["body"], page)
    return (f'<!DOCTYPE html>\n<html lang="{page["lang"]}">\n<head>\n{head(page)}\n</head>\n<body>\n'
            f'{header(page)}\n<main id="inhalt">\n{crumbs_html(page)}\n{body}\n</main>\n{footer(page)}\n'
            '<script src="/assets/site.js" defer></script>\n</body>\n</html>\n')


def out_path(page: dict) -> pathlib.Path:
    if page["type"] == "error":
        return ROOT / "404.html"
    p = page["path"].strip("/")
    return ROOT / (p + "/index.html" if p else "index.html")


# ------------------------------------------------------------------ Begleitdateien
def git_date(rel: str) -> str | None:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.strip() or None
    except OSError:
        return None


def sitemap() -> str:
    urls = []
    for p in PAGES:
        if p["type"] == "error":
            continue
        last = p.get("updated", "")
        urls.append(f'  <url><loc>{ORIGIN}{p["path"]}</loc>' + (f"<lastmod>{last}</lastmod>" if last else "") + "</url>")
    priv = git_date("datenschutz/index.html")
    urls.append(f"  <url><loc>{ORIGIN}/datenschutz/</loc>" + (f"<lastmod>{priv}</lastmod>" if priv else "") + "</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            "\n".join(urls) + "\n</urlset>\n")


def robots() -> str:
    return f"""# footyagent.app – robots.txt
# Alle öffentlichen Seiten dürfen gecrawlt werden – auch von KI-Suchsystemen.
# OAI-SearchBot = ChatGPT-Suche, ChatGPT-User = Abruf auf Nutzerwunsch, GPTBot = OpenAI-Training.
# GPTBot bewusst erlaubt (Bekanntheit des Spiels in Modellen). Zum Sperren: »Allow« → »Disallow«.

User-agent: *
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

Sitemap: {ORIGIN}/sitemap.xml
"""


def llms_txt() -> str:
    lines = [f"# {APP['name']}", "",
             f"> {APP['name']} is a single-player football agent management game for iPhone and iPad "
             f"(iOS/iPadOS {APP['minimumOs']} or later). You play as a players' agent, not a coach: scout talents, "
             "negotiate agent contracts, wages, playing time and transfers, and grow your agency. "
             f"Free, no ads, playable offline, no account needed. Developer: {APP['developer']} ({APP['developerCountry']['en']}). "
             f"Current version {APP['currentVersion']}.", "",
             "## Official pages", ""]
    for h, t, d in EXPLORE["en"]:
        lines.append(f"- [{t}]({ORIGIN}{h}): {d}")
    lines += [f"- [Deutsch]({ORIGIN}/de/): German homepage", f"- [App Store]({store_canonical()}): Download", "",
              "## Facts", "",
              f"- Platforms: {', '.join(APP['devices'])}", f"- Price: free (optional one-time Pro Pack, no gameplay advantage)",
              f"- Languages: {lang_list('en')}",
              f"- World: {N['nations']} nations, {N['leagues']} leagues, {N['clubs']} clubs (fictional players, clubs named after cities)",
              f"- Released: {APP['releaseDate']}", ""]
    return "\n".join(lines)


# ------------------------------------------------------------------ Ausgabe
def outputs() -> dict[pathlib.Path, str]:
    files = {out_path(p): render(p) for p in PAGES}
    files[ROOT / "sitemap.xml"] = sitemap()
    files[ROOT / "robots.txt"] = robots()
    files[ROOT / "llms.txt"] = llms_txt()
    if SITE.get("indexNowKey"):                       # Besitznachweis für IndexNow (_src/indexnow.py)
        files[ROOT / f'{SITE["indexNowKey"]}.txt'] = SITE["indexNowKey"]
    return files


def main() -> int:
    check = "--check" in sys.argv
    files = outputs()
    stale = []
    for path, content in files.items():
        old = path.read_text("utf-8") if path.exists() else None
        if old != content:
            stale.append(path.relative_to(ROOT))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, "utf-8")
    if check:
        if stale:
            print("VERALTET – bitte python3 _src/build.py ausführen:", *stale, sep="\n  ")
            return 1
        print(f"OK – {len(files)} Dateien aktuell")
        return 0
    print(f"{len(files)} Dateien, {len(stale)} geändert:", *stale, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
