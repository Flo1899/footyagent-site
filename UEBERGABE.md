# Übergabe: footyagent.app

**Stand 21.08.2026.** Diese Datei richtet sich an alle, die künftig an der Website arbeiten —
Menschen wie KI-Assistenten. Die technische Beschreibung der Seite selbst steht in
[`ANLEITUNG.md`](ANLEITUNG.md); hier stehen die Spielregeln.

## Dieses Repo ist ab sofort die einzige Quelle

Bis heute lag die Website doppelt: hier und als Kopie im privaten Spiel-Repo unter
`AppStore/website/`. Das ist beendet — im Spiel-Repo steht dort nur noch ein Verweis hierher.
**Alle Änderungen passieren in diesem Repo.** Wer die alte Kopie bearbeitet, arbeitet ins Leere
und riskiert, fremde Änderungen zu überschreiben.

## Veröffentlichen

Ein Push auf `main` **ist** die Veröffentlichung — GitHub Pages baut automatisch, nach etwa
einer Minute ist es live. Es gibt keine Staging-Umgebung und keinen Build-Schritt.

Danach prüfen:

```bash
curl -s "https://footyagent.app/?cb=$RANDOM" | grep -o '<body data-launch="[a-z]*">'
```

⚠️ **Fallstrick:** Nicht auf `data-launch="live"` allein prüfen. Diese Zeichenkette steht auch in
den CSS-Regeln (`[data-launch="live"] .wenn-soon{…}`) und meldet sofort Erfolg, auch wenn das
`<body>`-Tag noch auf `soon` steht. Immer das komplette Tag greppen. Der `cb`-Parameter umgeht
den CDN-Cache; ohne ihn liefert GitHub Pages minutenlang gemischt alt und neu aus.

## Harte Regeln

**`CNAME` niemals löschen oder ändern.** Inhalt ist `footyagent.app`. Ohne diese Datei fällt die
Seite auf die github.io-Adresse zurück und die Domain zeigt ins Leere.

**Keine externen Ressourcen einbauen.** Keine Google Fonts, kein CDN, keine Tracker, keine
eingebetteten Videos. Das ist kein Geschmacksurteil: Externe Ressourcen übertragen IP-Adressen an
Dritte und wären in Deutschland einwilligungspflichtig — die Seite käme ohne Cookie-Banner nicht
mehr aus. Alles liegt lokal in `assets/`.

**DE und EN immer paarweise pflegen.** Die Seite schaltet über `<span class="de">` und
`<span class="en">` um. Wer nur eine Sprache ändert, erzeugt eine Seite, die je nach Umschalter
etwas anderes behauptet.

**Zwei Seiten sind im App Store hinterlegt** und dürfen ihre Pfade nicht verlieren:
`/` ist die Support-URL, `/datenschutz/` die Datenschutz-URL. Umbenennen bricht die Store-Einträge.

## Was hier NICHT liegt

Die App selbst (privates Repo, kein Zugriff nötig), die Store-Texte (die pflegt App Store Connect)
und alles rund um Apple-Konto und Einreichungen. Wer hier arbeitet, braucht nichts davon.

## Offene Punkte

**1. Sprach-Chip — noch nicht ändern.** In `index.html` steht in der Merkmalliste
»Deutsch & Englisch« bzw. »German & English«. Die App spricht inzwischen acht Sprachen
(zusätzlich Spanisch, Portugiesisch (Brasilien), Französisch, Italienisch, Türkisch, Polnisch) —
**aber erst ab Version 1.1.1**, und die liegt zum Zeitpunkt dieser Übergabe noch in Apples Prüfung.
Die aktuell herunterladbare Version 1.1 kann wirklich nur Deutsch und Englisch. Erst nach der
Freigabe ändern, sonst verspricht die Seite etwas, das die App nicht hält.

**2. Impressums-Adresse — Entscheidung des Betreibers.** `datenschutz/index.html` nennt die
c/o-Anschrift eines Anbieters für Geschäftsadressen (Welserstraße 3, Dietmannsried). Im App Store
steht seit dem 21.08.2026 als Händleranschrift die Privatadresse. Zwei öffentliche Stellen, zwei
Adressen. Ob das so bleiben soll, entscheidet der Betreiber — **nicht eigenmächtig ändern**, hier
hängen rechtliche Fragen dran.

**3. Optional: offizielles Apple-Badge.** Der Download-Knopf ist eine Eigengestaltung mit
Apple-Logo. Apples Markenrichtlinien sehen das offizielle »Download on the App Store«-Badge vor.
Details stehen in `ANLEITUNG.md`.

## Zugriff

Wer hier schreiben darf, sollte **ausschließlich** auf dieses Repo Rechte haben — entweder als
Collaborator mit Write-Rolle oder über ein Fine-grained Token, das nur `footyagent-site` kennt
(Contents: Read and write) und ein Ablaufdatum hat. Zugriff auf das private Spiel-Repo oder auf
Apple-Konten wird für die Website nicht gebraucht und sollte nicht erteilt werden.
