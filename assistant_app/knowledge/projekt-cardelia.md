---
titel: Cardelia
quelle: Projekt Cardelia
---

## Was Cardelia ist

Cardelia ist ein Kartenkatalog mit Sammlungsverwaltung für Pokémon-Karten. Der
Bestand umfasst rund 80.000 Karten in vier Sprachen, jede Sprachfassung mit
eigenem Eintrag und eigenem Preis aus mehreren Quellen. Unter cardelia.de/demo
lässt sich Cardelia ohne Konto als Demo ausprobieren.

Benjamin baut Cardelia aus eigenem Antrieb, Stack, Architektur und Umfang hat
er vollständig selbst entschieden.

Unter benjaminblarr.de/cardelia ist die Laufzeit-Architektur als Schaubild
einsehbar: welche Bestandteile es gibt, woher die Daten kommen und wohin sie
gehen.

## Die Architektur von Cardelia

Cardelia trennt zwei Ebenen, die oft verwechselt werden.

**Django ist das Backend.** Dort liegen die Domänenlogik, die API und die
Hintergrundjobs, also alles, was Cardelia inhaltlich ausmacht.

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
mit rund 80.000 Karten in vier Sprachen ist keine Datenmenge, die man von Hand
pflegt. Fällt eine Quelle aus, bleibt der letzte Preis mit seinem Datum stehen,
sodass jeder sieht, von wann ein Preis stammt.

Mehrere Quellen für dasselbe bedeuten dabei nicht mehr Sicherheit, sondern mehr
Arbeit: Die Quellen widersprechen sich, benennen Dinge unterschiedlich und
fallen unterschiedlich oft aus.

Cardelia hat inzwischen über elf Millionen Preispunkte gespeichert. Mitte
November 2026 kamen jeden Tag rund 98.000 dazu.

## Das Erklärvideo zu Cardelia

Zu Cardelia gibt es ein Erklärvideo von gut anderthalb Minuten. Es läuft im
Portfolio auf der Projektkarte von Cardelia und auf der Architekturseite. Im
ersten Teil zeigt es in 3D, was Cardelia für Sammler tut. Der zweite Teil
zeigt, was nachts im Hintergrund passiert: den Weg eines einzelnen Preises von
der Datenquelle über die Hintergrundjobs und die Datenbank bis in die Wertkurve
einer Sammlung. Auf der englischen Seite laufen englische Untertitel
automatisch, auf der deutschen lassen sie sich einschalten.

Entstanden ist das Video in Zusammenarbeit mit KI. Idee, Richtung und die
Entscheidungen bis hin zu den Tönen kamen von Benjamin, den Sprechertext hat er
in mehreren Runden geformt. Die 3D-Szenen hat Claude per Skript in Blender
gebaut, gesprochen ist der Text von einer KI-Stimme von ElevenLabs.

## Warum Cardelia als Projekt zählt

Bei Cardelia hat Benjamin selbst entschieden, was er einsetzt und wie er es
zuschneidet. Entsprechend verantwortet er diese Entscheidungen auch selbst.

Es ist außerdem das Projekt, das am längsten läuft und dadurch Fragen aufwirft,
die in einem abgeschlossenen Übungsprojekt nie auftauchen: Was passiert, wenn
eine Datenquelle ihr Format ändert? Wie merkt man überhaupt, dass ein
nächtlicher Lauf nur halb durchgelaufen ist? Was tut man mit Daten, die
widersprüchlich sind?
