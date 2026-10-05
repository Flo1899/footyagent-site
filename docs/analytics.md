# Website-Analytics: PostHog, Kanäle, App-Store-Attribution

Stand 05.10.2026. Gilt für footyagent.app (statische Seite auf GitHub Pages, Generator `_src/build.py`).

## 1. Aufbau in einem Satz

Eine einzige Datei, [`assets/site.js`](../assets/site.js) (gzip ~5 KB, keine Abhängigkeiten), erkennt den
Akquise-Kanal, setzt den passenden App-Store-Kampagnenlink, meldet alle Ereignisse über **eine**
Funktion (`FA.track`) und lädt PostHog erst, wenn die Seite fertig ist – und nur, wenn ein Schlüssel
konfiguriert ist. **Ohne Schlüssel verlässt keine einzige Anfrage die Seite.**

### Konfiguration (statt Environment Variables)

Die Seite hat keinen Server und keinen Build auf dem Host; »Environment Variables« gibt es hier nicht.
Die Entsprechung ist [`_src/data/product.json`](../_src/data/product.json) → wird von `build.py` als
`<script id="fa-config">` in jede Seite geschrieben:

| Feld | Bedeutung | Wert |
|---|---|---|
| `analytics.posthogKey` | PostHog **Project API Key** (`phc_…`, öffentlicher Client-Schlüssel – gehört ins HTML) | leer = Analytics aus |
| `analytics.posthogHost` | Ingestion-Host | `https://eu.i.posthog.com` (EU-Cloud) |
| `analytics.posthogUiHost` | Oberfläche (für Links/Toolbar) | `https://eu.posthog.com` |
| `analytics.posthogDefaults` | Konfig-Stand des SDK | `2026-08-30` |
| `analytics.cookielessMode` | `always` = nie Cookies/Storage | `always` |
| `appStore.campaigns` | Kampagnen-Token je Kanal | siehe §5 |
| `verification.google` / `.bing` | Meta-Tag-Codes für Search Console / Bing | leer (DNS-Weg empfohlen) |

**Niemals** einen *Personal API Key* (`phx_…`) eintragen – der hätte Lesezugriff aufs ganze Konto.

## 2. Was PostHog selbst erfasst (dafür gibt es bewusst keine eigenen Ereignisse)

| Bedarf laut Spec | Quelle in PostHog |
|---|---|
| Seitenaufrufe, Pfade durch die Website | `$pageview` (`$pathname`, `$current_url`) |
| Sitzungen, Dauer, Absprung | Web Analytics (Sitzungen werden serverseitig gebildet) |
| Einstiegsseite der Sitzung | Sitzungs-Eigenschaft `$entry_pathname` |
| Referrer | `$referrer`, `$referring_domain`; Sitzung: `$entry_referring_domain` |
| UTM | `utm_source/medium/campaign` am Pageview; Sitzung: `$entry_utm_*` |
| Kanal (PostHog-eigen) | Sitzungs-Eigenschaft `$channel_type` – kennt den Typ **AI** (ChatGPT, Claude, Gemini, Perplexity, Copilot) |
| Gerät, Browser, OS | `$device_type`, `$browser`, `$os` |
| Sprache | `$browser_language` (Browser) + `page_language` (Seite, eigene Eigenschaft) |
| Verweildauer, Scrolltiefe | `$pageleave` (`$prev_pageview_duration`, `$prev_pageview_max_scroll_percentage`) |
| Land | **nicht verfügbar** im Cookieless-Modus (siehe §8) – Ersatz: `$timezone` |

## 3. Eigene Eigenschaften an *jedem* Ereignis

Per `before_send` an alle Ereignisse (auch `$pageview`/`$pageleave`) angehängt:

| Eigenschaft | Beispiel | Bedeutung |
|---|---|---|
| `acquisition_channel` | `chatgpt` | Kanal dieses Seitenaufrufs, siehe §4 (`internal` = kam von einer eigenen Seite) |
| `is_entry_page` | `true` | Seite wurde von außen betreten (nicht `internal`) |
| `page_language` | `de` | Sprache der Seite |
| `page_type` | `intent` | `home`, `intent`, `feature`, `faq`, `updates`, `press`, `about`, `error` |
| `site_build` | `6affc9f024` | Kennung des Website-Stands (zum Vergleichen vor/nach Änderungen) |

## 4. Kanal-Erkennung: `getAcquisitionChannel(url, referrer, ownHost)`

Reine Funktion in `site.js`, getestet in [`_src/tests/test_channel.mjs`](../_src/tests/test_channel.mjs)
(39 Fälle in `channel_cases.json`). Regeln in dieser Reihenfolge:

1. **UTM hat Vorrang.** `utm_medium` ∈ {cpc, ppc, paid, paidsocial, paid_social, display, ads, cpm} → `paid`.
   Sonst `utm_source`: chatgpt.com/chatgpt/openai → `chatgpt`; perplexity/claude/gemini/copilot/… → `ai_other`;
   google → `google_organic`; bing → `bing_organic`; twitter → `x`; Domains (z. B. `reddit.com`) wie Referrer;
   reddit/youtube/tiktok/instagram/x → gleichnamig; alles andere → `other_referral`.
2. **Kein UTM, kein Referrer** → `direct`.
3. **Referrer** (www. wird ignoriert): eigene Domain → `internal`; chatgpt.com, chat.openai.com → `chatgpt`;
   perplexity.ai, claude.ai, gemini.google.com, copilot.microsoft.com, deepseek, grok, meta.ai, mistral,
   poe, duck.ai, … → `ai_other` (**vor** Google geprüft, sonst wäre Gemini »Google«);
   google.* → `google_organic`; bing.com → `bing_organic`; duckduckgo, ecosia, brave, yahoo, … → `other_search`;
   reddit, youtube, tiktok, instagram, x/t.co → gleichnamig; facebook, threads, bluesky, linkedin, discord, … → `other_social`;
   sonst → `other_referral`.
4. Referrer, der keine URL ist → `unknown`.

**Erstkontakt:** Die Seite speichert bewusst **nichts** im Browser (keine Cookies, kein Storage – sonst
wäre eine Einwilligung nötig). Der Erstkontakt einer Sitzung kommt deshalb aus PostHog selbst:
Auf der Einstiegsseite steht er direkt in `acquisition_channel`; für Folgeseiten nutzt man die
Sitzungs-Eigenschaften `$entry_referring_domain`, `$entry_utm_source`, `$entry_pathname` bzw. `$channel_type`.

**Empfehlung PostHog-Einstellung:** unter *Project Settings → Web analytics → Custom channel types* einen
Kanal **»ChatGPT«** anlegen (Referring domain = `chatgpt.com` *oder* `chat.openai.com`, *oder*
UTM source = `chatgpt.com`) und ganz nach oben schieben. Eigene Kanäle haben Vorrang vor den
eingebauten; damit trennt `$channel_type` ChatGPT von übriger KI – auf Sitzungsebene, also auch für
Klicks auf Folgeseiten.

## 5. App-Store-Attribution

Alle Download-Knöpfe sind `<a data-cta="POSITION">` aus *einem* Baustein (`cta()` in `build.py`).
Im HTML steht der Standard-Link (funktioniert auch ohne JavaScript); `site.js` ersetzt ihn je Kanal:

```
https://apps.apple.com/app/apple-store/id6790972595?pt=129172457&ct=<KAMPAGNE>&mt=8
```

- `pt=129172457` = Anbieter-ID des Developer-Kontos (geprüft, nicht geraten).
- `ct` aus `product.json → appStore.campaigns`: `default` = `website`, `chatgpt` und `ai_other` = `website_ai`.
- **Bewusst nur zwei Kampagnen:** App Store Connect zeigt Kampagnen erst ab einer Mindestzahl an
  Installationen. Fünf kleine Töpfe (chatgpt/ai/google/social/direct) blieben anfangs alle unter der
  Schwelle und zeigten gar nichts. Feiner aufteilen = eine Zeile in `product.json`, sobald `website_ai`
  regelmäßig Zahlen zeigt (z. B. `"chatgpt": "website_chatgpt"`, `"google_organic": "website_google"`).
- Klicks auf Folgeseiten (Kanal `internal`) bekommen `website` – ohne Browser-Speicher ist der
  Erstkontakt dort clientseitig unbekannt. In PostHog ist er über die Sitzung trotzdem auswertbar.
- **Neutrale Links ohne Kampagne** (`https://apps.apple.com/app/id6790972595`) stehen dort, wo Dritte den
  Link weiterverwenden: JSON-LD, `llms.txt`, »Link for articles« in der Pressemappe. Sonst zählte Apple
  einen Klick direkt aus einer ChatGPT-Antwort fälschlich als Website-Besuch.
- Direkte Wege ChatGPT → App Store sieht nur App Store Connect (Quelle »Web Referrer«/»App Referrer«),
  nie die Website-Analytics.

Auswertung: App Store Connect → *App Analytics* → *Acquisition* → Kampagnen `website` / `website_ai`
(Impressionen, Produktseitenaufrufe, Erst-Downloads).

## 6. Ereignis-Wörterbuch

Alle eigenen Ereignisse laufen durch `FA.track()`; Klick-Ereignisse gehen per `sendBeacon` raus,
damit sie das Verlassen der Seite überleben.

### `app_store_click` – genau einmal je Klick auf einen Download-Knopf

| Eigenschaft | Beispiel | Hinweis |
|---|---|---|
| `page` | `/features/negotiations/` | Seite des Klicks |
| `landing_page` | `/` | Einstiegsseite; `null` auf Folgeseiten → `$entry_pathname` nutzen |
| `acquisition_channel` | `chatgpt` | siehe §4 |
| `referrer` | `https://chatgpt.com/` | `document.referrer` |
| `utm_source` / `utm_medium` / `utm_campaign` | `chatgpt.com` / – / – | von der aktuellen URL |
| `language` | `en` | Seitensprache |
| `cta_position` | `hero` | `hero`, `header`, `feature_page`, `bottom_cta`, `faq`, `press_page`, `body` |
| `destination` | `https://apps.apple.com/…&ct=website_ai&mt=8` | tatsächliches Ziel |
| `campaign_token` | `website_ai` | verwendetes `ct` |

Doppelzählung ausgeschlossen: ein Listener für die ganze Seite; dasselbe Element zählt innerhalb
von 800 ms nur einmal (Doppelklick, Klick + Mittelklick); Rechtsklick zählt nicht.

### Weitere

| Ereignis | Eigenschaften | Wann |
|---|---|---|
| `language_changed` | `from`, `to`, `page` | Klick auf DE/EN im Kopf |
| `faq_opened` | `question_id`, `page` | eine FAQ-Antwort wird aufgeklappt (Zuklappen zählt nicht) |
| `outbound_link_clicked` | `destination`, `destination_host`, `page`, `link_location` (`header`/`body`/`footer`) | Link auf fremde Domain (außer App-Store-Knöpfe) |

`scroll_depth_50/90` gibt es bewusst **nicht**: `$pageleave` liefert die maximale Scrolltiefe je Seite
schon mit – eigene Ereignisse wären nur Rauschen.

## 7. Dashboard »AI / GEO Acquisition« (in PostHog anlegen)

Alle Insights mit Datumsfilter des Dashboards. »Besuche« = Einstiegs-Pageviews
(`$pageview` mit `is_entry_page = true`), gezählt als **Unique sessions**. Nutzerzahlen
über mehrere Tage sind im Cookieless-Modus überhöht (§8) – deshalb Sitzungen.

| # | Insight | Typ | Ereignis + Filter | Aufschlüsselung |
|---|---|---|---|---|
| 1 | AI visitors over time | Trends (Linie, täglich) | Besuche mit `acquisition_channel` ∈ {chatgpt, ai_other} | – |
| 2 | ChatGPT visitors over time | Trends | Besuche mit `acquisition_channel = chatgpt` | – |
| 3 | AI traffic by source | Trends (Balken) | Besuche, `acquisition_channel` ∈ {chatgpt, ai_other} | `$referring_domain` (Fallback `utm_source`) |
| 4 | ChatGPT landing pages | Tabelle | Besuche, `acquisition_channel = chatgpt` | `$pathname` |
| 5 | AI visitors by »country« | Tabelle | wie 1 | `$timezone` (Land nicht verfügbar, §8) |
| 6 | AI visitors by language | Tabelle | wie 1 | `$browser_language`, zusätzlich `page_language` |
| 7 | AI visitors by device | Torte | wie 1 | `$device_type` |
| 8 | App Store clicks from AI | Trends | `app_store_click`, Sitzungsfilter `$channel_type` ∈ {AI, ChatGPT} | – |
| 9 | App Store clicks from ChatGPT | Trends | `app_store_click`, Sitzungsfilter `$channel_type = ChatGPT` | `cta_position` |
| 10 | ChatGPT → App Store CTR | Funnel | Schritt 1 Besuch (`acquisition_channel = chatgpt`) → Schritt 2 `app_store_click`; Fenster 1 Tag | – |
| 11 | AI → App Store CTR | Funnel | wie 10 mit {chatgpt, ai_other} | `acquisition_channel` |
| 12 | Landing page → App Store CTR | Funnel | Besuch → `app_store_click` | Schritt 1: `$pathname` |
| 13 | Top referrers | Tabelle | Besuche | `$referring_domain` |
| 14 | Top landing pages | Tabelle | Besuche | `$pathname` |
| 15 | Top organic landing pages | Tabelle | Besuche, `acquisition_channel` ∈ {google_organic, bing_organic, other_search} | `$pathname` |
| 16 | Google → App Store CTR | Funnel | wie 10 mit `google_organic` | – |
| 17 | Source mix | Trends (gestapelt) | Besuche | `acquisition_channel` |

**Hauptfunnel** (eigenes Insight): `AI/ChatGPT-Besuch → sinnvolle Beschäftigung → app_store_click`.
»Sinnvolle Beschäftigung« als PostHog-*Action* »Engaged« anlegen = eines von:
`$pageview` mit `is_entry_page = false` (zweite Seite) · `faq_opened` · `language_changed` ·
`$pageleave` mit `$prev_pageview_max_scroll_percentage ≥ 0.5`.
Weil manche direkt im Hero klicken, zusätzlich immer Funnel 10/11 (ohne Zwischenschritt) ansehen.

**Dashboard-Filter:** Quelle (`acquisition_channel` bzw. `$channel_type`), Land → `$timezone`,
Landingpage (`$entry_pathname`), Gerät (`$device_type`), Sprache (`$browser_language`), Zeitraum.

Ohne jede Einrichtung zeigt außerdem das eingebaute **Web Analytics**-Dashboard Kanäle (inkl. »AI«),
Einstiegsseiten, Referrer, Geräte, Absprung und Sitzungsdauer.

## 8. Datenschutz und Grenzen

**Was neu verarbeitet wird, sobald ein Schlüssel gesetzt ist** (Grundlage für die Datenschutzerklärung –
`MANUAL PRIVACY POLICY UPDATE REQUIRED`):

- Anbieter: PostHog Inc., Datenverarbeitung in der **EU-Cloud** (`eu.i.posthog.com`); AV-Vertrag (DPA) in PostHog abschließen.
- Beim Laden: Skript von `eu-assets.i.posthog.com` → die IP-Adresse des Besuchers erreicht PostHog.
- Daten je Seitenaufruf/Ereignis: URL, Pfad, Referrer, UTM-Parameter, Browser, Betriebssystem, Gerätetyp,
  Bildschirmgröße, Browsersprache, Zeitzone, Verweildauer, Scrolltiefe, die Ereignisse aus §6.
- **Keine Cookies, kein localStorage/sessionStorage** durch PostHog (`cookieless_mode: 'always'`).
  Einzige Browser-Speicherung der Seite: `fa_lang` (localStorage), nur wenn jemand selbst die Sprache wählt.
- PostHog bildet aus `team_id`, täglich wechselndem Salt, IP, User-Agent und Hostname einen Hash zum
  Zählen; der Salt wird nach dem Tag gelöscht. Die IP wird vor jeder Anreicherung entfernt
  (keine GeoIP, kein Standort). Kein `identify()`, keine Personenprofile, keine Aufzeichnungen, keine Umfragen.
- Offen für Florian/Rechtsberatung: Rechtsgrundlage (berechtigtes Interesse oder Einwilligung) und die
  Frage, ob das Auslesen von Browserangaben per Skript unter § 25 TDDDG fällt. Die Seite ist technisch auf
  den einwilligungsfreien Weg ausgelegt; wer einen Banner will, stellt `cookielessMode` auf `on_reject`
  und braucht dann ein Consent-Werkzeug.

**Grenzen der Messung:**

- **Kein Land** (Folge des Cookieless-Hashes, laut PostHog-Doku: »location data isn't added to events«). Ersatz: Zeitzone, Browsersprache.
- **Besucher werden jeden Tag neu gezählt**; Wochen-/Monats-Unique-Users sind überhöht → Sitzungen verwenden.
- Keine Bot-Erkennung über IP; das SDK filtert bekannte Bot-User-Agents selbst.
- Werbeblocker blockieren PostHog teilweise (Untererfassung, typischerweise einige bis 30 %). Abhilfe wäre
  ein eigener Proxy-Host – nur bei Bedarf.
- KI-Antworten ohne Referrer und ohne UTM (manche Apps/In-App-Browser) landen bei `direct`.
  ChatGPT hängt an zitierte Links meist `utm_source=chatgpt.com` an – das ist der Hauptweg.
- Google AI Overviews/AI Mode und Copilot in der Bing-Suche kommen als `google_organic` bzw. `bing_organic` an.
- E-Mail-Links ohne UTM landen je nach Mailprogramm bei `google_organic` (Gmail leitet über google.com) – eigene Links immer mit UTM versehen.

## 9. Testen

- **Debug-Modus:** beliebige Seite mit `?fa_debug=1` öffnen → Ereignisse in der Konsole (`[FA] …`) und in
  `window.FA.events`; `FA.channel` zeigt den erkannten Kanal. Funktioniert auch ohne Schlüssel.
- **Automatisch:** `node _src/tests/test_channel.mjs` (Kanal-Fälle, Kampagnen-Links, genau ein `app_store_click`,
  Pflichtfelder, `cta_position`, Folgeseiten, Altlinks). Läuft bei jedem Push in GitHub Actions.
- **Nach dem Schlüssel-Eintrag:** `https://footyagent.app/?utm_source=chatgpt.com` öffnen, Download-Knopf
  klicken → in PostHog unter *Activity* erscheinen `$pageview` (mit `acquisition_channel = chatgpt`) und
  genau ein `app_store_click`.
