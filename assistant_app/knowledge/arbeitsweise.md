---
titel: Arbeitsweise
quelle: Arbeitsweise
---

## Wie Benjamin eine neue Aufgabe angeht

Benjamin zerlegt Aufgaben, bevor er anfängt. Zuerst sammelt er, welche großen
Aufgaben es überhaupt gibt. Diese zerlegt er in Teilaufgaben, und diese
wiederum, bis einzelne To-dos übrig bleiben, die klein genug sind, dass eine
Person sie abschließen kann.

Das Verfahren stammt aus der Teamarbeit an Join und hat sich für ihn auch
allein bewährt. Der Nutzen liegt weniger in der Liste als in dem, was beim
Zerlegen auffällt: Eine Aufgabe, die sich nicht sauber zerlegen lässt, ist
meistens noch nicht verstanden.

Beim Umsetzen gilt dieselbe Reihenfolge wie beim Zerlegen: erst verstehen,
dann Lösungswege erarbeiten, dann sauber umsetzen. Der mittlere Schritt ist ihm
wichtig, weil die erste Lösung, die einem einfällt, selten die beste ist.

## Wie Benjamin im Team arbeitet

An Join hat Benjamin in einem Team aus vier Personen gearbeitet, koordiniert
über Trello. Aufgaben wurden gemeinsam zerlegt, dann hat sich jeder eines der
entstandenen To-dos genommen und es abgearbeitet.

Der Sinn dahinter ist, dass niemand dem anderen in die Quere kommt: keine
doppelte Arbeit, keine Blockaden, und der Stand ist für alle jederzeit sichtbar.

Benjamins Erfahrung aus dem Projekt ist deutlich: Die Koordination war
schwieriger als der Code. Das ist keine Klage, sondern eine Einschätzung, die
jeder teilt, der einmal zu viert an einer Anwendung gearbeitet hat. Die
technischen Probleme lassen sich nachlesen, die organisatorischen nicht.

## Was Benjamin an Code wichtig ist

Qualität geht vor Schnelligkeit. Lieber ein paar Minuten länger für eine
saubere Lösung als ein verfrühtes "ist fertig", das später jemand
auseinandernehmen muss.

Bei Fehlern sucht Benjamin die Ursache, statt das Symptom zu überdecken. Ein
Fehler, der nur kaschiert wurde, kommt an anderer Stelle wieder, dann aber ohne
erkennbaren Zusammenhang.

Wichtig sind ihm außerdem Lesbarkeit, Performance und die Bedienbarkeit für den
Anwender. Code kommentiert er sparsam: Was der Code tut, soll er selbst zeigen.
Kommentare hebt er sich für Entscheidungen auf, die man nicht ansieht, etwa
warum ein unsichtbares Formularfeld außerhalb des Sichtbereichs positioniert ist
statt mit display:none, weil manche automatisierten Absender ausgeblendete
Felder erkennen.

## Wie Benjamin mit Git arbeitet

Benjamin arbeitet nicht direkt auf dem Hauptzweig. Jede Änderung entsteht in
einem eigenen Feature-Branch und kommt über einen Pull Request in den
Hauptzweig, auch dann, wenn er allein am Projekt arbeitet und den Pull Request
selbst zusammenführt. Seine Commit-Nachrichten folgen den Conventional Commits
und sind auf Englisch.

Diese Arbeitsweise hat er sich bewusst angewöhnt, und zwar seit er mit CI/CD
arbeitet. Vorher hat er direkt auf dem Hauptzweig gearbeitet.

Zwei Gründe nennt er dafür. Der erste ist Übung: Er arbeitet meistens allein,
ist aber der Meinung, dass er das können muss. Im Team führt an diesem Ablauf
nichts vorbei, und ihn erst dann zu lernen, wenn andere davon abhängen, ist der
schlechtere Zeitpunkt.

Der zweite ist Schutz vor eigenen Fehlern. In seinen Projekten laufen bei jedem
Pull Request die vollständigen Prüfungen durch: Codeformatierung, statische
Analyse, Tests, Build. Ausgerollt wird aber nur, was im Hauptzweig landet. Ein
direkter Push auf den Hauptzweig würde also ungeprüft live gehen. Der Umweg
über den Pull Request sorgt dafür, dass zwischen "geschrieben" und
"ausgeliefert" immer eine automatische Kontrolle liegt.

## Welche Projekte nach Vorgabe entstanden sind und welche frei

Diese Einordnung nimmt Benjamin von sich aus vor, weil sie für die Bewertung
seiner Projekte wichtig ist.

Bei den Projekten aus der Developer Akademie (Join, El Pollo Loco, Pokédex,
Coderr und Videoflix) waren Stack und Technologien vorgegeben. Die Aufgabe bestand
nicht darin, die Werkzeuge auszuwählen, sondern damit ein funktionierendes und
sauber gebautes Ergebnis zu liefern.

Cardelia ist die Ausnahme: Es entsteht ohne Vorgaben und außerhalb der Akademie.
Stack, Architektur und Zuschnitt hat Benjamin dort selbst entschieden und
verantwortet sie entsprechend auch selbst.

Dass ein Stack vorgegeben war, heißt dabei nicht, dass er nichts dazu sagen
kann. Bei Videoflix kann er begründen, warum dort RQ und nicht Celery passt und
warum die Tokens in HttpOnly-Cookies liegen und nicht im LocalStorage. Bei
Cardelia hat er beides andersherum entschieden, weil das Projekt anders
zugeschnitten ist.
