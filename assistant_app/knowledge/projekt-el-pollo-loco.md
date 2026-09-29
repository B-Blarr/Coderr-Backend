---
titel: El Pollo Loco
quelle: Projekt El Pollo Loco
---

## Was El Pollo Loco ist

El Pollo Loco ist ein Jump-and-Run-Spiel, das Benjamin in reinem JavaScript
geschrieben hat. Ohne Framework, ohne Spiel-Engine, ohne Build-Schritt. Die
Spielfigur Pepe sammelt Münzen und Flaschen mit Tabasco-Salsa und setzt sie im
Kampf gegen eine Boss-Henne ein.

Das Spiel ist unter benjaminblarr.de/el-pollo-loco spielbar, der Quelltext liegt
öffentlich auf GitHub.

## Die Architektur hinter El Pollo Loco

Interessant an dem Projekt ist weniger das Spiel selbst als der Aufbau
dahinter. Es besteht aus 24 Klassen, von denen 17 eine gemeinsame Basisklasse
erweitern. Alles, was sich bewegt (die Spielfigur, die Gegner, die Flaschen,
die Wolken), erbt von dieser einen Klasse, die weiß, wo sie sich befindet, wie
groß sie ist und wie sie sich zeichnet.

Darüber läuft eine einzige Schleife, die das Bild viele Male pro Sekunde leert
und alles neu zeichnet. In jedem Durchgang werden Schwerkraft,
Animationszustände und Kollisionsprüfungen angewandt.

Benjamin nennt das als Beispiel dafür, wie er objektorientiertes Arbeiten
gelernt hat: nicht als Theorie über Vererbung, sondern an einer Stelle, an der
Vererbung tatsächlich Arbeit spart. Eine neue Gegnerart hinzuzufügen heißt in
diesem Aufbau, eine Klasse zu erweitern, statt Zeichen- und Kollisionslogik ein
weiteres Mal zu schreiben.

Der Boss-Kampf hat eine eigene Zustandsverwaltung mit den Phasen Alarm,
Angriff, Verletzung und Tod.

## Warum die Geräusche in El Pollo Loco selbst erzeugt sind

Grafiken und Spielfiguren kamen als Vorlage mit dem Projekt. Der Ton nicht: Die
mitgelieferten Geräusche fand Benjamin schwach. Er hat deshalb mit ElevenLabs
einen eigenen Satz erzeugt und davon nur behalten, was tatsächlich
funktionierte.

Das ist eine kleine Sache, sagt aber etwas über die Arbeitsweise: Was als
Vorlage kommt, wird nicht automatisch übernommen, wenn es das Ergebnis
verschlechtert.
