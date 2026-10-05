# Übergabe: footyagent.app

**Stand 05.10.2026** (Umbau auf Generator, Intent-Seiten und Analytics; vorher 21.08.2026).
Diese Datei richtet sich an alle, die an der Website arbeiten – Menschen wie KI-Assistenten.
Wie die Seite gebaut ist und gepflegt wird, steht in [`ANLEITUNG.md`](ANLEITUNG.md); hier stehen die Spielregeln.

## Dieses Repo ist die einzige Quelle

Seit 21.08.2026 liegt die Website nur noch hier (im Spiel-Repo unter `AppStore/website/` steht nur ein
Verweis). Seit 05.10.2026 gilt zusätzlich: **Die Quelle ist `_src/`.** Die HTML-Dateien im Repo sind
erzeugt – wer sie direkt bearbeitet, verliert die Änderung beim nächsten `python3 _src/build.py`, und die
GitHub-Prüfung schlägt an. Einzige Ausnahme: `datenschutz/index.html` (von Hand gepflegt).

## Veröffentlichen

Ein Merge/Push auf `main` **ist** die Veröffentlichung – GitHub Pages baut automatisch, nach etwa
einer Minute ist es live. Deshalb: auf einem Branch arbeiten, Pull Request, grüner Haken der Prüfung,
dann mergen. Live-Prüfung siehe `ANLEITUNG.md` (Build-Kennung vergleichen, `?cb=` gegen den CDN-Cache).

## Harte Regeln

**`CNAME` niemals löschen oder ändern.** Inhalt ist `footyagent.app`.

**Zwei Pfade sind im App Store hinterlegt** (alle 9 Store-Sprachen, geprüft 05.10.2026) und dürfen nie
verschwinden: `/` (Support- und Marketing-URL) und `/datenschutz/` (Datenschutz-URL).

**Fakten nur aus `_src/data/product.json`** – und dort nur, was die **herunterladbare** Store-Version wirklich
kann. Keine angekündigten Funktionen, keine erfundenen Bewertungen, Downloadzahlen, Pressezitate oder
»bestes Spiel«-Behauptungen. Keine Bewertungen im JSON-LD.

**Keine externen Ressourcen** (keine Google Fonts, kein CDN, keine eingebetteten Videos, keine Social-Widgets).
Externe Ressourcen übertragen IP-Adressen an Dritte und wären in Deutschland einwilligungspflichtig.
**Einzige Ausnahme: PostHog** (Florians Entscheidung vom 05.10.2026) – EU-Cloud, `cookieless_mode: 'always'`,
lädt nur, wenn in `product.json` ein Schlüssel steht. Den Schlüssel erst eintragen, wenn
(1) die Datenschutzerklärung PostHog nennt und (2) in PostHog »Cookieless server hash mode« aktiv ist.
Keine weiteren Tracker, kein zweites Analytics-System, kein Cookie-Banner nachrüsten. Details: `docs/analytics.md`.

**App-Store-Links nur über den Baustein `{{cta:…}}`.** Er setzt Kampagne (`pt`/`ct`) und Messung. Wo Dritte
den Link weiterverwenden (JSON-LD, `llms.txt`, Presse), steht der neutrale Link ohne Kampagne.

**Sprachen:** EN ist die Hauptsprache (`/`), DE hat eigene Seiten unter `/de/`. Inhalte eines Sprachpaars
gemeinsam pflegen (`pair:` im Kopfblock). Keine automatisch übersetzten Massen-Seiten.

**Datenschutztext nicht eigenmächtig ändern** – rechtliche Texte formuliert Florian bzw. seine Beratung.

## Offene Punkte

1. **Datenschutzerklärung für PostHog ergänzen** – `MANUAL PRIVACY POLICY UPDATE REQUIRED`
   (welche Daten, siehe `docs/analytics.md` §8). Bis dahin bleibt der Schlüssel leer = keine Messung.
2. **Impressums-Adresse – Entscheidung des Betreibers.** `datenschutz/index.html` nennt eine c/o-Geschäftsadresse,
   der App Store die Privatadresse. Nicht eigenmächtig ändern.
3. **Optional: offizielles Apple-Badge.** Der Download-Knopf ist eine Eigengestaltung mit Apple-Logo;
   Apples Richtlinien sehen das offizielle »Download on the App Store«-Badge vor
   (<https://developer.apple.com/app-store/marketing/guidelines/>). Wer tauscht: Inhalt in `cta()` (`build.py`) ersetzen.

## Zugriff

Wer hier schreiben darf, sollte **ausschließlich** auf dieses Repo Rechte haben – Collaborator mit Write-Rolle
oder ein Fine-grained Token nur für `footyagent-site` (Contents: Read and write) mit Ablaufdatum. Zugriff auf das
private Spiel-Repo, Apple-Konten oder PostHog wird für Textänderungen nicht gebraucht.
