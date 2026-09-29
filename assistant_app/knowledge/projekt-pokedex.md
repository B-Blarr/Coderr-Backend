---
titel: Pokédex
quelle: Projekt Pokédex
---

## Was der Pokédex ist

Der Pokédex ist ein interaktives Pokémon-Verzeichnis, das Benjamin in reinem
JavaScript gebaut hat. Die Daten kommen live von der PokéAPI. Die Anwendung
zeigt die Pokémon als Kartenraster, eine Suche nach Namen filtert sie, und ein
Klick öffnet eine Detailansicht mit Grundwerten, Fähigkeiten, der
Shiny-Variante und der Entwicklungsreihe.

Der Pokédex ist unter benjaminblarr.de/pokedex erreichbar.

## Wo die eigentliche Schwierigkeit im Pokédex lag

Fast nichts kommt bei diesem Projekt fertig an. Eine einzige Detailansicht wird
aus mehreren Endpunkten zusammengesetzt, die Antworten sind tief verschachtelt,
und die Entwicklungsreihe lässt sich erst über mehrere aufeinander aufbauende
Abrufe auflösen.

Gleichzeitig müssen Liste, Suche und Detailansicht bedienbar bleiben, während
im Hintergrund noch Anfragen laufen. Der größte Teil der Arbeit steckte genau
darin: nicht in einer einzelnen Funktion, sondern darin, dass sich das Ganze
flüssig anfühlt, obwohl ständig auf Daten gewartet wird.

Die Pokémon werden nicht alle auf einmal geladen, sondern nachgeladen, wenn sie
gebraucht werden.

## Was Benjamin am Pokédex gelernt hat

Der Pokédex ist das Projekt, an dem Benjamin den Umgang mit einer fremden API
gelernt hat, die ihm ihre Struktur vorgibt. Man bekommt die Daten so, wie die
Schnittstelle sie liefert, nicht so, wie man sie in der Oberfläche braucht. Die
Arbeit besteht darin, dazwischen zu übersetzen und dabei die Zahl der Anfragen
im Blick zu behalten.
