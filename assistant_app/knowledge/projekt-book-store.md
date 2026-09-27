---
titel: Book-Store
quelle: Projekt Book-Store
---

## Was der Book-Store ist

Der Book-Store ist ein Buchkatalog mit Likes und Kommentaren, gebaut in reinem
JavaScript mit HTML und CSS, ohne Framework. Er zeigt neun Bücher mit Titel,
Autor, Erscheinungsjahr, Genre und Preis. Jedes Buch lässt sich liken und
kommentieren.

Likes und Kommentare bleiben nach dem Neuladen erhalten, weil sie im
LocalStorage des Browsers gespeichert werden. Einen Server gibt es nicht. Jeder
Besucher sieht deshalb nur seine eigenen Likes und Kommentare.

Der Book-Store ist das erste Projekt, das Benjamin an der Developer Akademie
gebaut hat. Er ist unter benjaminblarr.de/bookstore erreichbar, der Quelltext
liegt öffentlich auf GitHub.

## Wie der Book-Store Daten im Browser speichert

Der LocalStorage speichert nur Text. Der Book-Store wandelt deshalb nach jedem
Like und jedem Kommentar die gesamte Bücherliste in JSON um und legt sie unter
einem festen Schlüssel ab. Beim Laden der Seite wird sie wieder eingelesen und
ersetzt die Daten aus dem Quelltext. Ein Kommentar mit leerem Namen oder leerem
Text wird gar nicht erst gespeichert.

Die Daten liegen damit an zwei Orten: im Quelltext und im Browser. Das
funktioniert, solange sich die Bücherliste im Quelltext nicht ändert. Käme ein
neues Buch dazu, sähe ein Besucher mit gespeichertem Stand es nicht, weil sein
alter Stand den neuen überschreibt.

An diesem kleinen Projekt hat Benjamin gelernt, was es heißt, Zustand dauerhaft
zu speichern. Es ist dieselbe Frage, die in größeren Anwendungen eine Datenbank
beantwortet: Welcher Stand gilt, wenn es zwei gibt?
