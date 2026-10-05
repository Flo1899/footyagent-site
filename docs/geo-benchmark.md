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

_Noch kein Lauf erfasst. Erster Lauf = Ausgangswert vor dem Deploy._

## Einordnen

- **Nennung ohne Website-Zitat** → die KI kennt FootyAgent aus Store/Drittseiten; Seiten sind evtl. noch nicht im Suchindex
  (Bing Webmaster Tools → URL-Prüfung; ChatGPT-Suche greift u. a. auf den Bing-Index zurück).
- **Website zitiert, aber falsche Fakten** → Seite mit der richtigen Antwort früher/klarer formulieren (FAQ, Antwort-Absatz oben).
- **Keine Nennung bei Intent-Prompts** → ist die passende Intent-Seite indexiert? Steht die direkte Antwort im ersten Absatz?
- Ergebnisse mit den PostHog-Zahlen vergleichen (Dashboard »AI / GEO Acquisition«, siehe [analytics.md](analytics.md)):
  steigen Nennungen, sollten `chatgpt`-Besuche und die Kampagne `website_ai` in App Store Connect folgen.
