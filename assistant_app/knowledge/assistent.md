---
titel: Dieser Assistent
quelle: Über diesen Assistenten
---

## Was dieser Assistent ist und was du ihn fragen kannst

Dieser Assistent ist ein Programm auf Benjamins Website, nicht Benjamin selbst.
Er beantwortet Fragen zu Benjamin Blarr: wer er ist, wie er arbeitet, welche
Projekte er gebaut hat und mit welchen Technologien, wie er seine Anwendungen
auf dem eigenen Server betreibt und woran er gerade arbeitet. Gute erste Fragen
sind zum Beispiel: Welche Projekte hat Benjamin gebaut? Sucht er gerade eine
Stelle? Wie funktioniert dieser Assistent?

Er antwortet nur aus den Informationen auf dieser Website. Für allgemeine
Programmierfragen oder Texte zu anderen Themen ist er nicht gedacht.

## Der Assistent auf dieser Seite

Diesen Assistenten hat Benjamin selbst gebaut. Er beantwortet Fragen zu
Benjamin und seinen Projekten aus einer gepflegten Wissensbasis, statt sich
Antworten auszudenken. Das Verfahren dahinter heißt Retrieval-Augmented
Generation: Zu jeder Frage werden zuerst die passenden Abschnitte aus der
Wissensbasis gesucht, und nur diese Abschnitte bekommt das Sprachmodell als
Grundlage.

Die Suche läuft auf Benjamins eigenem Server, mit PostgreSQL, pgvector und
einem eigenen Embedding-Dienst. Findet sie nichts Passendes, sagt der
Assistent das, und das Sprachmodell wird gar nicht erst gefragt. Davor sitzt
ein Filter, der Versuche erkennt, den Assistenten aus seiner Rolle zu holen
oder ihm fremde Anweisungen unterzuschieben. Solche Anfragen werden
abgewiesen, bevor sie das Sprachmodell erreichen. Die Antwort selbst schreibt
das Sprachmodell Claude von Anthropic.

Ob Suche, Filter und Antworten zuverlässig arbeiten, misst Benjamin mit festen
Listen aus Testfragen, auch nach Änderungen an der Wissensbasis.

Benjamin hat den Assistenten gebaut, weil er RAG nicht nur in der Theorie
verstehen wollte, sondern an einem System, das öffentlich läuft und von echten
Besuchern benutzt wird.

## Ob eingegebene Texte gespeichert oder weitergegeben werden

Auf Benjamins Server wird nichts gespeichert, was Besucher hier eingeben. Für
die Antwort schickt der Server den eingegebenen Text zusammen mit den
passenden Abschnitten der Wissensbasis an Anthropic, den Anbieter des
Sprachmodells Claude. Die IP-Adresse des Besuchers erfährt Anthropic dabei
nicht.

Einzelheiten zum Datenschutz stehen in der Datenschutzerklärung dieser Website.
