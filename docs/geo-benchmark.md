# GEO-Benchmark: Findet KI-Suche FootyAgent?

Wiederholbare Messung, ob und wie ChatGPT & Co. FootyAgent bei passenden Fragen nennen.
Die Website-Analytics zeigt nur, wer *kommt* – dieser Benchmark zeigt, ob FootyAgent überhaupt
*genannt* wird und mit welcher Quelle.

## Ablauf

**Wann:** einmal **vor** dem Deploy der GEO-Seiten (Ausgangswert), dann 2 und 4 Wochen danach,
anschließend monatlich. Immer dieselben Prompts, damit die Läufe vergleichbar bleiben.

**Wo (Plattform-Kürzel für die Tabelle):**

| Kürzel | Plattform | Einstellung |
|---|---|---|
| `CGPT-S` | ChatGPT mit Websuche | neuer Chat, Suche erzwingen (Websuche-Symbol) |
| `CGPT` | ChatGPT ohne Suche | neuer Chat, Suche aus – zeigt das Modellwissen |
| `PPLX` | Perplexity | Standard-Suche |
| `GEM` | Google Gemini | Standard |
| `AIO` | Google-Suche: AI Overview / AI Mode | Prompt als Suchanfrage |
| `COP` | Microsoft Copilot | Standard |

**Wichtig bei ChatGPT:** möglichst **ohne Anmeldung** testen. Ein eigenes Konto mit Erinnerungen kennt FootyAgent und
verfälscht das Ergebnis; der temporäre Chat nutzt Erinnerungen in der aktuellen Version ebenfalls (»Personalisiert«).

**Regeln:** jeder Prompt in einem **neuen** Chat; nach Möglichkeit abgemeldet bzw. ohne Verlauf/Memory;
Sprache und Land notieren (US/DE beeinflusst die Antworten); Antwort als Screenshot unter
`docs/geo-benchmark/<datum>/` ablegen, wenn etwas Auffälliges passiert.

**Bewertung:**

- *Mentioned?* – FootyAgent wird namentlich genannt (ja/nein).
- *Position/context* – Platz in einer Aufzählung (1, 2, …) oder »nur Nebensatz«; richtig beschrieben?
- *Website cited?* – footyagent.app als Quelle/Link.
- *App Store cited?* – apps.apple.com-Link zu FootyAgent.
- *Competitors* – genannte andere Spiele (z. B. Manager- oder Agenten-Spiele).
- *Reason* – warum (nicht) relevant: Plattform passt nicht, Begriff unbekannt, veraltete Info, …

## Prompts – Englisch

1. What's the best football agent game for iPhone?
2. Are there any football agent simulator games?
3. Is there a game where I can be a football player's agent?
4. What soccer agent games are available on iOS?
5. I want a football game focused on transfers and contracts.
6. What football management games let you represent players?
7. Are there any offline football management games for iPhone?
8. What game lets me scout players and negotiate their contracts?
9. Can I play as a football agent instead of a manager?
10. What are some indie football management games?
11. Best soccer agent simulator for iPhone
12. Football agent game with transfers
13. Football agency management game
14. Football contract negotiation game
15. Offline soccer management game
16. Football business simulation game
17. Game where you manage football players' careers
18. Football transfer simulator iOS
19. Football management game without managing a club
20. Football game where I am an agent instead of a coach

## Prompts – Deutsch

21. Gibt es ein Spiel, in dem ich Spielerberater im Fußball bin?
22. Welches Fußball-Berater-Spiel gibt es fürs iPhone?
23. Fußball-Manager-Spiel, bei dem man Spieler vertritt statt einen Verein zu trainieren
24. Gibt es ein Fußball-Spiel über Transfers und Vertragsverhandlungen?
25. Welche Fußball-Manager-Spiele kann man offline auf dem iPhone spielen?
26. Spiel, in dem ich Talente scoute und ihre Verträge aushandle
27. Kann ich in einem Handyspiel Spielerberater statt Trainer sein?
28. Bestes Spielerberater-Spiel für iOS
29. Fußball-Agentur-Simulation
30. Fußball-Transfer-Simulator fürs iPad
31. Kostenloses Fußball-Manager-Spiel ohne Werbung fürs iPhone
32. Fußball-Business-Simulation
33. Indie-Fußball-Manager-Spiele
34. Spiel über die Karriere von Fußballspielern als Berater
35. Was ist FootyAgent?
36. Ist FootyAgent kostenlos und gibt es das für Android?

Prompt 35/36 prüfen das **Wissen über die Marke** (Entity): Stimmen Plattform, Preis, Offline-Fähigkeit?
Falsche Antworten hier sind wichtiger als fehlende Nennungen bei 1–34.

## Tabelle

Eine Zeile je Prompt × Plattform × Datum. Kopiervorlage:

| Date | Prompt # | Platform | FootyAgent mentioned? | Position/context | Website cited? | App Store cited? | Competitors mentioned | Reason relevant / not | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-__ | 1 | CGPT-S | | | | | | | |
| 2026-10-__ | 1 | PPLX | | | | | | | |

### Läufe

<!-- Neue Läufe unten anhängen; Zusammenfassung je Lauf: Nennungen gesamt / Prompts, zitierte Quellen. -->

#### Lauf 1 – Ausgangswert, 06.10.2026 (ChatGPT)

**Bedingungen:** ChatGPT **ohne Anmeldung** (keine Erinnerungen/Personalisierung – Florians Konto kennt FootyAgent aus
früheren Chats, ein temporärer Chat ließ sich dort nicht entpersonalisieren), jede Frage in neuem Chat, Websuche
automatisch (ChatGPT entscheidet selbst), Oberfläche Deutsch, Standort per IP Vietnam (Đà Nẵng). Die neuen Seiten
waren seit 05.10. 19:30 UTC live, per IndexNow an Bing gemeldet, aber noch nicht indexiert → echter Ausgangswert.

**Ergebnis in Zahlen**

- Intent-Fragen (11): FootyAgent **1×** genannt (#26, DE, Platz 3 von 4) – Quelle App Store.
- Marken-Fragen (3): **3/3 korrekt** (iPhone/iPad, Einzelspieler, offline, kostenlos + Pro-Paket 5,99 €, kein Android,
  Entwickler Florian Schlauf); ChatGPT grenzt FootyAgent selbst von »Football Agent« (ATERO GAMES, Steam) ab.
- **footyagent.app zitiert: 0 von 14.** Quelle für FootyAgent war immer der App Store.
- Ohne Websuche (#9, #13) fragt ChatGPT zurück bzw. bietet ein eigenes Textspiel an – keine Spieleempfehlung.

| Date | Prompt # | Platform | FootyAgent mentioned? | Position/context | Website cited? | App Store cited? | Competitors mentioned | Reason FootyAgent was/was not relevant | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | 1 | CGPT-S | nein | – | nein | nein (nur Konkurrenz) | Superstar Football Agent (»best overall«, 4,6★/~6.200), Football Agent (iOS, 0,99 $), Soccer Agent: Football Game | ChatGPT wählt nach App-Store-Bewertungen; FootyAgent hat wenige | Quellen nur App Store |
| 2026-10-06 | 2 | CGPT-S | nein | – | nein | nein | Football Agent (Steam, ATERO), The Agency (Browser), Football Agent (Android), Football Agency Simulator | Steam-Spiel gleichen Namens dominiert | Steam, Google Play |
| 2026-10-06 | 3 | CGPT-S | nein | – | nein | nein | Football Agent (Steam + Android), The Agency, Football Gem Agent 26 (iOS) | wie #2 | |
| 2026-10-06 | 5 | CGPT-S | nein | – | nein | nein | Football Manager 26, EA Sports FC 27, Football Agent (Steam) | Manager-Spiele für »Transfers/Verträge« | |
| 2026-10-06 | 8 | CGPT-S | nein | – | nein | nein | Football Manager 26 | deutet Frage als FM | Quelle FM Scout |
| 2026-10-06 | 9 | CGPT | nein | – | nein | nein | – | keine Suche, Rückfrage | |
| 2026-10-06 | 13 | CGPT | nein | – | nein | nein | – | keine Suche, bietet Textspiel an | |
| 2026-10-06 | 18 | CGPT-S | nein | – | nein | nein | Lab11, Soccer Manager Club Sim 27, Football Legend, Dynasty Manager: Football | »Transfer-Simulator« = Manager-Spiele | Quellen App Store, Reddit |
| 2026-10-06 | 21 | CGPT-S | nein | – | nein | nein | Football Agent (Steam, empfohlen; Mobil), Superstar Football Agent | wie #2 | |
| 2026-10-06 | 22 | CGPT-S | nein | – | nein | nein | Football Agent (iOS), Fußball-Agent (4,6★/310), Football Gem Agent 26, Football Agent Simulator | iOS-Liste nach Store-Suche, FootyAgent nicht dabei | wichtigste Lücke |
| 2026-10-06 | 26 | CGPT-S | **ja** | Platz 3 von 4, korrekt beschrieben | nein | **ja** | Football Agent (Steam), Football Agency Simulator, Football Sporting Director 27 | Store-Text passt zu »scouten + Verträge« | einziger Intent-Treffer |
| 2026-10-06 | 35 | CGPT-S | **ja** | korrekte Beschreibung | nein | **ja** | Abgrenzung zu Football Agent (Steam) | Markenfrage | |
| 2026-10-06 | 36 | CGPT-S | **ja** | kostenlos, Pro 5,99 €, kein Android – korrekt | nein | **ja** | Football Agent (Android) als anderes Spiel | Markenfrage | |
| 2026-10-06 | (EN) What is FootyAgent? | CGPT-S | **ja** | korrekt, Entwickler genannt | nein | **ja** | – | Markenfrage | |

**Was daraus folgt**

1. **ChatGPT holt iOS-Spiele fast nur aus App-Store-Einträgen.** Untertitel und Beschreibung im Store sind damit direkt
   GEO-relevant (Begriffe »football agent game«, »Spielerberater«, »scout, negotiate, transfers«).
2. **Bewertungsanzahl entscheidet die Reihenfolge** (»best overall« = 6.200 Bewertungen). Mehr Bewertungen helfen auch
   der KI-Sichtbarkeit.
3. **Namenskonkurrenz:** »Football Agent« (Steam, Early Access seit 25.08.2026) taucht in 6 von 14 Antworten auf. Die klare
   Formel »FootyAgent – the football agent game for iPhone & iPad« bleibt richtig; ChatGPT trennt die Spiele bereits.
4. **Ziel für Lauf 2 (ca. 20.10.):** footyagent.app wird mindestens einmal zitiert; FootyAgent erscheint bei den
   iPhone-Fragen (#1, #22).

Ergänzend lohnt der Blick in **Bing Webmaster Tools → AI Performance (Beta)**: Dort zeigt Bing, wie oft footyagent.app in
Copilot-/KI-Antworten erscheint (seit 06.10.2026 eingerichtet).

#### Lauf 2 – 2 Wochen nach Deploy, 21.10.2026 (ChatGPT)

**Bedingungen:** geplant für 20.10., die geplante Aufgabe brach ab → am 21.10. von Hand nachgeholt. Gleiche Fragen wie
Lauf 1. ChatGPT **ohne Anmeldung**, nicht unbedingt erforderliche Cookies abgelehnt, jede Frage in neuem Chat. Websuche
automatisch (ChatGPT entscheidet selbst), Oberfläche Deutsch. Standort per IP **Thailand** (Lauf 1: Vietnam); ChatGPT
nannte entsprechend den Pro-Preis aus dem thailändischen App Store. FootyAgent 2.0 ist seit 20.10. im Store.

**Ergebnis in Zahlen**

- Intent-Fragen (11): FootyAgent **0×** genannt (Lauf 1: 1×). #26 nannte FootyAgent in Lauf 1 auf Platz 3, diesmal nicht –
  bei einer Stichprobe pro Frage ist das eher Streuung als Trend.
- Marken-Fragen (3): **3/3 sachlich korrekt** (iPhone/iPad, kostenlos mit In-App-Kauf, offline, Einzelspieler, kein
  Android, Entwickler Florian Schlauf). Die englische Antwort nennt mehr Spielinhalte (Scouts, Anwälte, Analysten,
  Leihen, Rivalen) – alle im Spiel vorhanden.
- **footyagent.app zitiert: 0 von 14** (Ziel »mindestens 1×« verfehlt). Quelle für FootyAgent war wieder nur der App Store.
- **Neu: falsche Bilder.** Bei #35 zeigt die FootyAgent-Karte das Icon von *Superstar Football Agent*, bei der englischen
  Markenfrage zeigt die Bildleiste Screenshots von *Football Agent* (Top Drawer Games, koreanischer App Store). Der Text
  stimmt, die Bilder gehören zu Konkurrenten.
- Namensvettern: Ein Spiel namens »Football Agent« (Steam, Android oder iOS) steht in **10 von 14** Antworten; die
  Steam-Version ausdrücklich in 5 (Lauf 1: 6).
- Ohne Websuche (#9, #13) nennt ChatGPT jetzt Spielnamen (Football Agent, Football Manager), statt nur zurückzufragen.

**Gegenprobe Bing** (21.10., ohne Anmeldung; ChatGPT-Suche nutzt u. a. den Bing-Index): footyagent.app ist indexiert.
»FootyAgent football agent game« (US) → Platz 2; »Fußball Spielerberater Spiel iPhone« (DE) → **Platz 2** (Startseite,
nicht /de/fussball-berater-spiel/); »best football agent game for iPhone« (US) → nicht unter den ersten 10 (dort:
appshunter.io-Themenseiten, ioshacker, pocketgamer, App-Store-Einträge der Konkurrenz). Die Website ist also auffindbar,
ChatGPT greift bei App-Fragen aber direkt auf App-Store-Einträge zurück.

| Date | Prompt # | Platform | FootyAgent mentioned? | Position/context | Website cited? | App Store cited? | Competitors mentioned | Reason FootyAgent was/was not relevant | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-21 | 1 | CGPT-S | nein | – | nein | nein (nur Konkurrenz) | Superstar Football Agent (Top-Empfehlung, 4,6★/~6.200), Soccer Agent: Football Game (4,6★/~1.300), Football Agent (iOS, 4,7★/33, kostenpflichtig) | Auswahl nach App-Store-Bewertungen, wie Lauf 1 | Quellen nur App Store |
| 2026-10-21 | 2 | CGPT-S | nein | – | nein | nein | Football Agent (Steam, ATERO), Football Agent (Android), The Agency (Browser), King Agent Calcio (Android), Football Agent Simulator (iPhone) | Steam-Spiel gleichen Namens zuerst | Steam, Google Play, App Store |
| 2026-10-21 | 3 | CGPT-S | nein | – | nein | nein | Football Agent (Steam, 11,99 $), Soccer Agent: Football Game (»best for iPhone/iPad«), The Agency, Agent Trouble: Football (itch.io), Football Agent (Android) | wie #2 | |
| 2026-10-21 | 5 | CGPT-S | nein | – | nein | nein | Football Manager, EA Sports FC (Karrieremodus), Soccer Manager | »Transfers/Verträge« = Manager-Spiele | offizielle Websites, Rückfragen |
| 2026-10-21 | 8 | CGPT-S | nein | – | nein | nein | Football Manager (FM 27), Football Agent (Steam) als Agenten-Alternative | deutet Frage als FM | |
| 2026-10-21 | 9 | CGPT | nein | – | nein | nein | Football Agent, Football Manager, EA Sports FC | keine Suche; jetzt mit Spielnamen + Rückfrage nach Plattform | |
| 2026-10-21 | 13 | CGPT | nein | – | nein | nein | Football Agent (Google Play), »Soccer Agent« (Steam-Suche), Football Manager | keine Quellen-Chips, nur Shop-Links; bietet auch ein Chat-Spiel an | |
| 2026-10-21 | 18 | CGPT-S | nein | – | nein | nein | Online Soccer Manager, Soccer Manager 2027, Football Manager Mobile, Soccer Agent | »Transfer-Simulator« = Manager-Spiele | Quellen App Store |
| 2026-10-21 | 21 | CGPT-S | nein | – | nein | nein | Football Agent (Steam, Empfehlung), The Agency (Browser), Football Agent (Android) | wie #2 | |
| 2026-10-21 | 22 | CGPT-S | nein | – | nein | nein | Fußball-Agent (Empfehlung, 4,6★/~310), Football Agent (Top Drawer Games), Football Gem Agent 26 | iOS-Liste nach Store-Suche, FootyAgent fehlt weiter | wichtigste Lücke, wie Lauf 1 |
| 2026-10-21 | 26 | CGPT-S | nein | – | nein | nein | Football Agent (Steam), Football Agency Simulator (Android), My Football Path (itch.io) | Lauf 1 hier Platz 3 – diesmal andere Auswahl | Streuung |
| 2026-10-21 | 35 | CGPT-S | **ja** | korrekt beschrieben, Entwickler genannt | nein | **ja** | – | Markenfrage | Karte zeigt Icon von Superstar Football Agent |
| 2026-10-21 | 36 | CGPT-S | **ja** | kostenlos + Pro (199 ฿, Thai-Store), kein Android – korrekt | nein | **ja** | Football Agent (Android, 0,99 $) als Alternative | Markenfrage | |
| 2026-10-21 | (EN) What is FootyAgent? | CGPT-S | **ja** | korrekt, ausführlich, Entwickler genannt | nein | **ja** | – | Markenfrage | Bildleiste zeigt Screenshots von Football Agent (Top Drawer Games) |

**Was daraus folgt (Vergleich mit Lauf 1)**

1. **Die neuen Website-Seiten wirken bei Bing, aber noch nicht in ChatGPT.** Für App-Fragen zitiert ChatGPT App-Store-Einträge,
   nicht Websites. Der wirksamste Hebel bleibt der Store-Eintrag: Untertitel/Schlüsselwörter (Texte liegen bereit in
   `AppStore/aso-suchbegriffe.md`, im App-Repo) und vor allem **mehr Bewertungen** – die Rangfolge folgt in #1 und #22
   wieder der Bewertungsanzahl.
2. **Für englische Intent-Fragen fehlen Drittquellen.** Bei Bing stehen dort Listen (appshunter, ioshacker, pocketgamer)
   vorn. Ein Eintrag in solchen Listen bzw. ein Presse-Pitch an Mobile-Gaming-Seiten wäre der nächste Schritt.
3. **Markenwissen ist stabil richtig**, aber die Namensnähe zu »Football Agent« führt jetzt zu falschen Bildern. Klarer
   Markenauftritt (Name »FootyAgent« sichtbar auf Icon-nahen Medien und Store-Screenshots) hilft der Zuordnung.
4. Einzelne Antworten schwanken (#26). Künftige Läufe: die Fragen #1, #22, #26 je **dreimal** stellen und Treffer zählen.
5. **Nächster Lauf (4 Wochen nach Deploy, ca. 03.11.):** dieselben 14 Fragen + Dreifach-Stichprobe; Ziel unverändert
   (footyagent.app ≥ 1× zitiert, FootyAgent bei #1/#22).

Nicht geprüft in diesem Lauf: Search Console / Bing Webmaster Tools (AI Performance) – braucht Florians Anmeldung.

## Einordnen

- **Nennung ohne Website-Zitat** → die KI kennt FootyAgent aus Store/Drittseiten; Seiten sind evtl. noch nicht im Suchindex
  (Bing Webmaster Tools → URL-Prüfung; ChatGPT-Suche greift u. a. auf den Bing-Index zurück).
- **Website zitiert, aber falsche Fakten** → Seite mit der richtigen Antwort früher/klarer formulieren (FAQ, Antwort-Absatz oben).
- **Keine Nennung bei Intent-Prompts** → ist die passende Intent-Seite indexiert? Steht die direkte Antwort im ersten Absatz?
- Ergebnisse mit den PostHog-Zahlen vergleichen (Dashboard »AI / GEO Acquisition«, siehe [analytics.md](analytics.md)):
  steigen Nennungen, sollten `chatgpt`-Besuche und die Kampagne `website_ai` in App Store Connect folgen.
