---
titel: BestellApp
quelle: Projekt BestellApp
---

## Was die BestellApp ist

Die BestellApp ist eine Bestelloberfläche nach dem Vorbild von Lieferdiensten
wie Lieferando, gebaut in reinem JavaScript mit HTML und CSS, ohne Framework.
Die Speisekarte einer Pizzeria mit Pizzen, Desserts und Getränken wird aus
einem JavaScript-Datenobjekt erzeugt.

Gerichte lassen sich in den Warenkorb legen, in der Menge ändern und wieder
entfernen. Zwischensumme, Lieferkosten und Gesamtsumme werden bei jeder
Änderung neu berechnet. Auf großen Bildschirmen steht der Warenkorb neben der
Speisekarte, auf dem Smartphone öffnet er sich als eigenes Dialogfenster. Nach
dem Bestellen erscheint eine Bestätigung, und der Warenkorb wird geleert.
Bestellt wird dabei nichts, es gibt kein Backend.

Die BestellApp ist eines der ersten Projekte, die Benjamin an der Developer
Akademie gebaut hat. Sie ist unter benjaminblarr.de/bestellapp erreichbar, der
Quelltext liegt öffentlich auf GitHub.

## Was Benjamin an der BestellApp über Frameworks gelernt hat

Der Zustand der BestellApp liegt in einfachen Variablen und Objekten. Jede
Änderung muss von Hand ins DOM zurückgeschrieben werden, in der richtigen
Reihenfolge und an jeder Stelle, an der derselbe Wert auftaucht.

Genau das ist hier die Schwierigkeit: Den Warenkorb gibt es zweimal, einmal
neben der Speisekarte für große Bildschirme und einmal im Dialog für das
Smartphone. Jeder Zähler, jeder Einzelpreis und jede Summe muss an beiden
Stellen nachgeführt werden. Wird eine Stelle vergessen, zeigen die beiden
Warenkörbe unterschiedliche Beträge.

Diesen Teil nimmt einem ein Framework wie Angular ab: Man ändert die Daten, und
die Oberfläche folgt von selbst. Weil Benjamin es vorher von Hand gemacht hat,
weiß er, welches Problem Datenbindung eigentlich löst.
