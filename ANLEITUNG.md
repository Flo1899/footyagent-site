# FootyAgent-Website (footyagent.app + footyagent.de)

Dieser Ordner **ist** die komplette Website:

| Datei | Zweck |
|---|---|
| `index.html` | Landingpage — zugleich die **Support-URL** im App Store |
| `datenschutz/index.html` | Datenschutz & Impressum — die **Datenschutz-URL** im App Store |
| `assets/` | Screenshots (WebP), App-Icon, Wappen-Bilder — zusammen ~400 KB |
| `CNAME` | `footyagent.app` (für GitHub Pages) |

Beide Seiten sind **komplett eigenständig**: kein Framework, keine Build-Schritte, keine
externen Ressourcen. Das ist Absicht — externe Schriften (Google Fonts) oder CDNs würden
IP-Adressen an Dritte übertragen und wären in Deutschland einwilligungspflichtig.

---

## 🚀 Beim App-Store-Launch umstellen (1 Zeichenkette!)

Solange die App in Prüfung ist, zeigt der Hero einen ruhigen Status-Knopf
(„Gerade in Apples Prüfung · Bald im App Store"). Sobald die App live ist:

In `index.html` im `<body>`-Tag umstellen:

```html
<body data-launch="soon">     <!-- vorher -->
<body data-launch="live">     <!-- nachher -->
```

Damit erscheint automatisch der grüne Download-Knopf, der auf
`https://apps.apple.com/app/id6790972595?ct=website&mt=8` zeigt. Sonst ist **nichts** zu ändern.

> **Optional, aber sauberer:** Apples Markenrichtlinien verlangen für Store-Verlinkungen
> das offizielle „Download on the App Store"-Badge. Unser Knopf ist eine eigene Gestaltung
> mit Apple-Logo — für den Start völlig üblich. Wer es ganz korrekt will, lädt das offizielle
> SVG bei <https://developer.apple.com/app-store/marketing/guidelines/> und ersetzt den
> Inhalt von `a.knopf.wenn-live`.

---

## Inhalte pflegen

**Sprachen:** Jeder Text steht zweimal im HTML — als `<span class="de">` und `<span class="en">`.
Umgeschaltet wird per CSS (letzte Regel im Stylesheet), die Wahl merkt sich `localStorage`
unter `fa_lang` und gilt für beide Seiten. Ohne gespeicherte Wahl entscheidet die
Browsersprache. **Wichtig:** Immer *beide* Sprachfassungen pflegen, sonst fehlt eine Sprache.

**Screenshots austauschen:** Neue Simulator-Screenshots (1320×2868) so verkleinern:

```bash
sips -Z 660 quelle.png --out /tmp/klein.png
cwebp -q 80 /tmp/klein.png -o assets/de-01-buero.webp
```

**Wappen-Bild neu erzeugen:** Die App hat dafür eine Debug-Ansicht:

```bash
xcrun simctl launch <UDID> com.florianschlauf.FootballAgent -wappenWeb
xcrun simctl io <UDID> screenshot /tmp/w.png
sips -c 930 1250 --cropOffset 1050 35 /tmp/w.png --out /tmp/wc.png
cwebp -q 88 /tmp/wc.png -o assets/wappen.webp
```

---

## Hosting (steht bereits)

Die Seite liegt im **öffentlichen** Repo `Flo1899/footyagent-site` (das private Spiel-Repo
kann kein kostenloses GitHub Pages). Deployen = Inhalt dieses Ordners dorthin kopieren und pushen:

```bash
cd /pfad/zu/footyagent-site
rsync -a --delete --exclude '.git' --exclude 'ANLEITUNG.md' \
      /Users/florianschlauf/Claude/FootballAgent/AppStore/website/ ./
git add -A && git commit -m "Website aktualisiert" && git push
```

`ANLEITUNG.md` bleibt bewusst im privaten Hauptrepo (nicht öffentlich).
GitHub Pages baut in ~1 Minute; danach ist `https://footyagent.app` aktuell.

**DNS (eingerichtet, nur zur Doku):** `footyagent.app` → A-Records auf die vier
GitHub-IPs `185.199.108–111.153`; `footyagent.de` → 301-Weiterleitung auf
`https://footyagent.app`; `support@footyagent.de` → IONOS-Postfach.

⚠️ **Zertifikat-Falle (schon einmal passiert):** Bleibt HTTPS nach dem Setzen der Custom
Domain hängen (`cert_state=none`), hilft: Domain lösen (`CNAME`-Datei löschen **und**
`gh api --method PUT repos/Flo1899/footyagent-site/pages -f cname=""`), ~80 s warten,
dann Domain neu setzen. Danach `-F https_enforced=true`.

---

## Lokal ansehen

```bash
cd AppStore/website && python3 -m http.server 8899
# → http://localhost:8899
```
