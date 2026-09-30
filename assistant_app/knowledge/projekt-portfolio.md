---
titel: Portfolio
quelle: Projekt Portfolio
---

## Was das Portfolio ist

Das Portfolio unter benjaminblarr.de ist Benjamins persönliche Website, eine
Single-Page-Anwendung mit Angular und TypeScript. Sie stellt ihn vor, zeigt
seine Technologien, eine Auswahl seiner Projekte mit Links zu den laufenden
Anwendungen, Stimmen von Teampartnern, diesen Assistenten und ein
Kontaktformular.

Die Seite ist zweisprachig, Deutsch und Englisch, und passt sich von großen
4K-Bildschirmen bis hinunter zu 320 Pixel breiten Smartphones an.

Benjamin hat die Seite nach einer Designvorlage selbst umgesetzt: den Aufbau
der Komponenten, das Layout auf allen Breiten, die Übersetzung, das Formular
mit dem Backend dahinter und die Auslieferung auf seinen eigenen Server. Der
Quelltext liegt öffentlich auf GitHub.

## Wie das Portfolio technisch aufgebaut ist

Das Portfolio nutzt Angular 21 mit Standalone-Komponenten, also ohne
NgModules, und SCSS ohne UI-Framework. Jeder Bereich der Seite ist eine eigene
Komponente, wiederverwendbare Bausteine wie der Knopf, das Kontaktformular und
das Projekt-Overlay liegen getrennt davon.

Die Texte der Seite stehen nicht in den Templates, sondern in je einer
Sprachdatei für Deutsch und Englisch.

Für den Knopf, das Kontaktformular, das Projekt-Overlay und den Assistenten
gibt es Unit-Tests mit Vitest. Beim Formular und beim Assistenten wird dabei
auch die Anfrage an den Server geprüft, ohne dass ein echter Server laufen
muss.

## Wie die Zweisprachigkeit des Portfolios funktioniert

Das Portfolio ist zweisprachig, Deutsch und Englisch. Die Internationalisierung,
kurz i18n, läuft über die Bibliothek ngx-translate.

Alle sichtbaren Texte stehen in zwei JSON-Dateien, eine pro Sprache, mit
denselben Schlüsseln. Die Templates enthalten nur die Schlüssel, nicht die
Texte. Fest im Template stehen nur der Name, die Berufsbezeichnung und die
E-Mail-Adresse.

Die Sprachdateien werden zur Laufzeit geladen. Dadurch wechselt die Sprache
ohne Neuladen, und der Besucher bleibt an der Stelle der Seite, an der er
gerade war. Die gewählte Sprache merkt sich der Browser für den nächsten
Besuch. Fehlt in einer Sprache ein Text, erscheint die englische Fassung
statt eines leeren Feldes.

Beim Wechsel wird auch das Sprachattribut der Seite umgestellt. So liest ein
Screenreader englische Texte mit englischer Aussprache vor und nicht mit
deutscher.

Angular bringt mit @angular/localize eine eigene Lösung mit, die aber für jede
Sprache eine eigene Fassung der Seite baut. Für einen Sprachwechsel ohne
Neuladen passt ngx-translate besser.

## Wie das Portfolio deployt wird

Das Portfolio wird automatisch über GitHub Actions deployt. Bei jedem Pull
Request und jedem Push auf den Hauptzweig laufen Linting mit ESLint, die
Formatprüfung mit Prettier, die Tests und ein vollständiger Build. Alle
Prüfungen laufen auch dann weiter, wenn eine davon scheitert. So meldet ein
Durchlauf jedes Problem und nicht nur das erste.

Ausgerollt wird nur, was im Hauptzweig landet. Die Pipeline baut die Seite dann
neu und überträgt sie per rsync auf den Server. Dabei werden alte Dateien im
selben Durchgang entfernt und die Dateirechte direkt beim Schreiben gesetzt.

Nach dem Deployment prüft die Pipeline, ob die Seite erreichbar ist und ob die
Sprachdateien wirklich als JSON ankommen.

## Was Benjamin am Kontaktformular des Portfolios gelernt hat

Das Kontaktformular prüft die Eingaben zweimal: im Browser, damit der Besucher
sofort sieht, was fehlt, und auf dem Server, weil man sich auf den Browser nie
verlassen darf.

Einmal passten die beiden Prüfungen nicht zusammen. Der Server verlangte
mindestens zehn Zeichen in der Nachricht, das Formular im Browser nicht. Kurze
Nachrichten wurden also abgeschickt, vom Server abgelehnt, und der Besucher sah
nur eine allgemeine Fehlermeldung. Seitdem legt Benjamin bei jeder Änderung
beide Seiten nebeneinander und vergleicht sie Feld für Feld.

Die Fehlermeldungen des Servers zeigt das Formular bewusst nicht an. Sie gibt
es nur auf Deutsch, das Portfolio ist aber zweisprachig. Die Meldungen im
Formular kommen deshalb aus den Sprachdateien.
