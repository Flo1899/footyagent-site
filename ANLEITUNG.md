# FootyAgent-Website (footyagent.app) – Aufbau und Pflege

Spielregeln für alle, die hier arbeiten: [`UEBERGABE.md`](UEBERGABE.md). Analytics: [`docs/analytics.md`](docs/analytics.md).
KI-Sichtbarkeit messen: [`docs/geo-benchmark.md`](docs/geo-benchmark.md).

## Aufbau

Statisches HTML, erzeugt von einem kleinen Generator (nur Python-Standardbibliothek, kein npm, kein Framework).
Die **erzeugten** Dateien liegen im Repo und werden von GitHub Pages direkt ausgeliefert.

| Pfad | Inhalt |
|---|---|
| `_src/data/product.json` | **Einzige Quelle für Produktfakten** (Version, Zahlen, Preise, Sprachen, Store-Link, Analytics-Konfiguration) |
| `_src/data/faq.json` | FAQ (en/de), erscheint auf `/faq/`, `/de/faq/` und als FAQPage-JSON-LD |
| `_src/data/releases.json` | Versionshistorie für `/updates/` |
| `_src/pages/<sprache>/*.html` | Seitentexte mit Kopfblock (Titel, Beschreibung, Pfad …) |
| `_src/site-base.css`, `_src/site-extra.css` | Gestaltung – wird in jede Seite eingebettet (kein extra Request) |
| `_src/build.py` | Generator: Seiten, `sitemap.xml`, `robots.txt`, `llms.txt`, IndexNow-Schlüsseldatei |
| `_src/tests/` | Prüfungen (siehe unten) |
| `_src/sync_appstore.py` | Fakten mit dem App Store abgleichen |
| `_src/indexnow.py` | geänderte Seiten an Bing & Co. melden |
| `_src/og/` | Vorlage + Skript für das Link-Vorschaubild |
| `assets/site.js` | Kanal-Erkennung, App-Store-Kampagnen, Ereignisse, PostHog-Laden, Sprachhinweis |
| `assets/` | Bilder (WebP), Icon, OG-Bild |
| `datenschutz/index.html` | **von Hand gepflegt** (nicht generiert) – Datenschutz-URL im App Store |
| `CNAME` | `footyagent.app` – nie ändern |
| `_config.yml` | sagt Jekyll (GitHub Pages), welche Dateien nicht veröffentlicht werden |
| `.github/workflows/` | Prüfung bei jedem Push, wöchentlicher App-Store-Abgleich |

Ordner mit `_` am Anfang veröffentlicht GitHub Pages nicht; `docs/`, `ANLEITUNG.md`, `UEBERGABE.md`
schließt `_config.yml` aus.

### Seiten

| URL | Quelle | Zweck |
|---|---|---|
| `/` | `en/home.html` | Startseite EN – **Support-URL im App Store** |
| `/de/` | `de/home.html` | Startseite DE |
| `/football-agent-game/` · `/de/fussball-berater-spiel/` | `…/football-agent-game.html` · `de/fussball-berater-spiel.html` | Haupt-Intent »Fußball-Berater-Spiel« |
| `/football-agent-game-ios/` | `en/football-agent-game-ios.html` | iPhone/iPad, Preis, Anforderungen |
| `/offline-football-game/` | `en/offline-football-game.html` | was offline geht |
| `/how-it-works/` | `en/how-it-works.html` | Spielablauf |
| `/features/scouting/` … `/features/agency-management/` | `en/features-*.html` | vier Mechanik-Seiten |
| `/faq/` · `/de/faq/` | `en/faq.html` · `de/faq.html` (+ `faq.json`) | FAQ |
| `/updates/` | `en/updates.html` (+ `releases.json`) | Versionen |
| `/press/` | `en/press.html` | Pressemappe |
| `/about/` | `en/about.html` | Über das Spiel und den Entwickler |
| `/404.html` | `en/404.html` | Fehlerseite (noindex) |
| `/datenschutz/` | von Hand | **Datenschutz-URL im App Store** |

Sprachpaare (hreflang): `/` ↔ `/de/`, `/football-agent-game/` ↔ `/de/fussball-berater-spiel/`, `/faq/` ↔ `/de/faq/`.
Alte Links `/?lang=de` leiten auf `/de/` weiter (UTM bleibt erhalten).

## Ändern – immer so

```bash
cd footyagent-site
# 1. Quelle in _src/ bearbeiten (nie die erzeugten HTML-Dateien – die überschreibt der nächste Lauf)
python3 _src/build.py                 # 2. erzeugen
python3 _src/tests/test_site.py       # 3. SEO/Struktur prüfen
node _src/tests/test_channel.mjs      #    Analytics-Logik prüfen
python3 -m http.server 8899           # 4. ansehen: http://localhost:8899  (Debug: ?fa_debug=1)
```

Dann auf einem Branch committen, Pull Request öffnen, die GitHub-Prüfung abwarten (grüner Haken).
**Merge nach `main` = Veröffentlichung** (GitHub Pages, ~1 Minute).

### Kopfblock einer Seite

```
---
id: scouting-en            # eindeutig
lang: en
pair: home                 # optional: gleicher Wert = Sprachpaar (hreflang)
path: /features/scouting/
type: feature              # home | intent | feature | faq | updates | press | about | error
schema: app                # optional: VideoGame/MobileApplication-JSON-LD (FAQPage/AboutPage folgen aus type)
parent: game-en            # optional: Brotkrumen-Elternseite
crumb: Scouting
title: …                   # ≤ 60 Zeichen
description: …             # ≤ 160 Zeichen
updated: 2026-10-05        # lastmod in der Sitemap – bei inhaltlicher Änderung anpassen
---
```

### Platzhalter und Bausteine (auch in Titel/Beschreibung)

| Schreibweise | Ergebnis |
|---|---|
| `{{n.nations}}`, `{{n.clubs}}`, `{{app.minimumOs}}`, `{{site.supportEmail}}` | Wert aus `product.json` (unbekannter Pfad = Abbruch, kein stiller Fehler) |
| `{{version}}`, `{{versionDate}}`, `{{releaseDate}}`, `{{langlist}}`, `{{langcount}}`, `{{releasecount}}` | abgeleitete Werte |
| `{{cta:hero}}` / `{{ctabtn:hero}}` | Download-Knopf mit/ohne Hinweiszeile; Wort nach `:` = `cta_position` |
| `{{shot:datei.webp\|Alt-Text\|Bildunterschrift}}` | Screenshot im Handyrahmen |
| `{{haken:Fett:\|Text}}` | Listenpunkt mit Haken |
| `{{steckbrief}}`, `{{faq}}`, `{{releases}}`, `{{explore}}` | Faktentabelle, FAQ, Versionsliste, »Mehr erfahren«-Kacheln |
| `{{storeurl}}` / `{{storecanonical}}` | Store-Link mit Kampagne (nur für Knöpfe) / neutral (für Texte zum Kopieren) |

Neue Seite: Datei anlegen, bei Bedarf in `EXPLORE` (oben in `build.py`) eintragen, bauen, prüfen.

## Fakten ändern

Nur in `_src/data/product.json`. **Nur Fakten, die die herunterladbare Store-Version wirklich hat** –
keine angekündigten Funktionen, keine Bewertungen, keine Download-Zahlen.

### Nach jedem App-Release

```bash
python3 _src/sync_appstore.py            # zeigt, was sich im Store geändert hat
python3 _src/sync_appstore.py --write    # Version, Datum, Größe, Mindest-iOS + neuer Eintrag für /updates/
python3 _src/build.py && python3 _src/tests/test_site.py
```

Die neuen »Was ist neu«-Texte auf `/updates/` kurz lesen, committen, mergen. Danach
`python3 _src/indexnow.py --send /updates/ /` (meldet die geänderten Seiten).
Vergisst man es, schlägt montags der GitHub-Workflow »App-Store-Abgleich« fehl (E-Mail von GitHub).

## Bilder

**Screenshots** (Simulator 1320×2868) → 660 breit, WebP, sprechender Name:

```bash
sips -Z 1434 quelle.png --out /tmp/klein.png
cwebp -q 80 /tmp/klein.png -o assets/footyagent-<inhalt>.webp      # z. B. footyagent-transfer-decision.webp
```

Im HTML immer `width="660" height="1434"` und einen Alt-Text, der **das tatsächliche Bild** beschreibt
(was steht drauf?), nicht Werbung. Unterhalb des ersten Bildschirms `loading="lazy" decoding="async"`.

**Link-Vorschaubild** (`assets/footyagent-og.jpg`, 1200×630) – Vorlage `_src/og/og.html` anpassen, dann:

```bash
python3 -m http.server 8765 &                                       # im Repo-Ordner
swift _src/og/render.swift http://127.0.0.1:8765/_src/og/og.html /tmp/og.png   # WebKit, 2400×1260
sips -s format jpeg -s formatOptions 84 --resampleWidth 1200 /tmp/og.png --out assets/footyagent-og.jpg
```

**Wappen-Bild** – die App hat eine Debug-Ansicht:

```bash
xcrun simctl launch <UDID> com.florianschlauf.FootballAgent -wappenWeb
xcrun simctl io <UDID> screenshot /tmp/w.png
sips -c 930 1250 --cropOffset 1050 35 /tmp/w.png --out /tmp/wc.png
cwebp -q 88 /tmp/wc.png -o assets/wappen.webp
```

## Prüfungen

| Befehl | prüft |
|---|---|
| `python3 _src/build.py --check` | erzeugte Dateien passen zu den Quellen (jemand hat HTML direkt bearbeitet?) |
| `python3 _src/tests/test_site.py` | Titel, Beschreibung, genau eine H1, Canonical, hreflang (gegenseitig + x-default), JSON-LD (gültig, keine Bewertungen, Preis/Version), interne Links + Anker, Bilder + Alt-Texte, App-Store-Knöpfe mit Kampagne, Sitemap ↔ Seiten, robots.txt (OAI-SearchBot), llms.txt, OG-Bild 1200×630 |
| `python3 _src/tests/test_site.py --live https://footyagent.app` | zusätzlich live: HTTP 200 für alle Seiten (als OAI-SearchBot), echte 404, Canonical, footyagent.de-Weiterleitung |
| `node _src/tests/test_channel.mjs` | `site.js`: 39 Kanal-Fälle, Kampagnen je Kanal, `app_store_click` genau einmal, Pflichtfelder, Erstkontakt über Folgeseiten (`fa_src`), Altlinks |
| `swift _src/tests/webkit_smoke.swift http://127.0.0.1:8765` | nur macOS: alle Seiten in der Safari-Engine + echte Reise ChatGPT → Unterseite → Knopf |

Alle außer `--live` laufen bei jedem Push automatisch (`.github/workflows/site-check.yml`).

## Hosting (steht)

Öffentliches Repo `Flo1899/footyagent-site`, GitHub Pages aus `main` (Root), Jekyll an.

**DNS (IONOS):** `footyagent.app` → A-Records `185.199.108–111.153`; `footyagent.de` → Weiterleitung auf
`https://footyagent.app` (IONOS-Weiterleitung antwortet immer mit 302 – ein 301 bietet IONOS dort nicht an;
für eine kaum verlinkte Zweitdomain unkritisch); `support@footyagent.de` → IONOS-Postfach.

**Suchmaschinen (eingerichtet 06.10.2026):** Google Search Console = Domain-Property `footyagent.app`, bestätigt
über den TXT-Eintrag `google-site-verification=…` im DNS von footyagent.app – **diesen Eintrag nie löschen**, sonst
geht der Zugang verloren. Sitemap dort eingereicht. Alle Seiten per IndexNow gemeldet (`_src/indexnow.py`).
Bing Webmaster Tools: per »Import aus Search Console« anlegen (Anmeldung macht Florian selbst).

⚠️ **Zertifikat-Falle:** Bleibt HTTPS nach dem Setzen der Domain hängen (`cert_state=none`): Domain lösen
(`CNAME` löschen **und** `gh api --method PUT repos/Flo1899/footyagent-site/pages -f cname=""`), ~80 s warten,
Domain neu setzen, dann `-F https_enforced=true`.

⚠️ **Pages-Build hängt in »queued«:** `gh run rerun` hilft nicht – stattdessen
`gh api -X POST repos/Flo1899/footyagent-site/pages/builds`.

**Nach dem Deploy prüfen** (CDN-Cache mit `cb` umgehen): die Build-Kennung live = lokal?

```bash
curl -s "https://footyagent.app/?cb=$RANDOM" | grep -o '"build":"[0-9a-f]*"'
grep -o '"build":"[0-9a-f]*"' index.html
```
