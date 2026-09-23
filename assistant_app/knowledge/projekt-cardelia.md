---
titel: Cardelia
quelle: Projekt Cardelia
---

## Was Cardelia ist

Cardelia ist ein Kartenkatalog mit Sammlungsverwaltung für Pokémon-Karten. Der
Bestand umfasst rund 77.000 Karten in vier Sprachen, dazu Preise aus mehreren
Quellen. Die Anwendung läuft, ist aber noch nicht öffentlich zugänglich.

Cardelia ist Benjamins ambitioniertestes Projekt und das einzige, das er ohne
Vorgaben und außerhalb der Developer Akademie baut. Stack, Architektur und
Umfang hat er vollständig selbst entschieden.

Unter benjaminblarr.de/cardelia ist die Laufzeit-Architektur als Schaubild
einsehbar: welche Bestandteile es gibt, woher die Daten kommen und wohin sie
gehen.

## Die Architektur von Cardelia

Cardelia trennt zwei Ebenen, die oft verwechselt werden.

**Django ist das Backend.** Dort liegen die Domänenlogik, die API und die
Hintergrundjobs — also alles, was Cardelia inhaltlich ausmacht.

**Supabase ist Infrastruktur, kein Backend.** Es liefert PostgreSQL,
Authentifizierung und Objektspeicher als gemanagten Dienst. Diese Bestandteile
müsste Benjamin sonst selbst betreiben.

Die beiden konkurrieren also nicht miteinander, sondern liegen auf
verschiedenen Ebenen. Das ist eine Unterscheidung, die Benjamin ausdrücklich
macht: Wer Supabase als Backend bezeichnet, meint meistens den Fall, in dem es
gar kein eigenes Backend gibt und die Oberfläche direkt auf die Datenbank
zugreift. Bei Cardelia ist das nicht so.

Für die Hintergrundverarbeitung kommen Celery mit einem Worker und Celery Beat
als Zeitplaner zum Einsatz, mit Redis als Vermittler. Zusätzlich läuft eine
tägliche Sicherung.

## Woher die Daten in Cardelia kommen

Cardelia zieht seine Daten aus acht externen Quellen: TCGdex, Cardmarket,
PokeTrace, CardTrader, Limitless, PokeWallet, pokemontcg.io und tcggo.

Einmal täglich läuft ein Lauf, der die Preise aktualisiert und prüft, ob neue
Kartensets erschienen sind. Dieser Lauf ist der Kern des Systems: Ein Katalog
mit 77.000 Karten in vier Sprachen ist keine Datenmenge, die man von Hand
pflegt, und Preise, die eine Woche alt sind, sind für eine Sammlungsverwaltung
wertlos.

Mehrere Quellen für dasselbe bedeuten dabei nicht mehr Sicherheit, sondern mehr
Arbeit: Die Quellen widersprechen sich, benennen Dinge unterschiedlich und
fallen unterschiedlich oft aus.

## Warum Cardelia als Projekt zählt

Bei den Ausbildungsprojekten war der Stack vorgegeben. Cardelia ist die
Ausnahme: Hier hat Benjamin selbst entschieden, was er einsetzt und wie er es
zuschneidet — und muss diese Entscheidungen entsprechend auch selbst
verantworten.

Es ist außerdem das Projekt, das am längsten läuft und dadurch Fragen aufwirft,
die in einem abgeschlossenen Übungsprojekt nie auftauchen: Was passiert, wenn
eine Datenquelle ihr Format ändert? Wie merkt man überhaupt, dass ein
nächtlicher Lauf nur halb durchgelaufen ist? Was tut man mit Daten, die
widersprüchlich sind?
