---
titel: Projekte im Überblick
quelle: Projektübersicht
---

## Welche Projekte Benjamin gebaut hat und mit welchem Stack

Benjamins Projekte in der Reihenfolge, in der sie entstanden sind, jeweils mit
den wichtigsten Technologien:

- **Fotogram**: JavaScript, HTML, CSS, Bildergalerie mit Großansicht
- **Book-Store**: JavaScript, HTML, CSS, Speicherung im LocalStorage
- **BestellApp**: JavaScript, HTML, CSS
- **Pokédex**: JavaScript, Daten von der PokéAPI
- **El Pollo Loco**: JavaScript, objektorientiert, Zeichnen auf Canvas
- **Join**: Angular, TypeScript, SCSS, Supabase, im Team zu viert
- **Portfolio**: Angular, TypeScript, SCSS, zweisprachig
- **Cardelia**: Python, Django, Celery, Redis, Supabase
- **KanMind**: Python, Django REST Framework
- **Coderr**: Python, Django REST Framework, PostgreSQL
- **Quizly**: Python, Django REST Framework, Whisper, Gemini
- **Videoflix**: Python, Django REST Framework, Redis, RQ, FFmpeg, Docker
- **Nina, Telefon-Sprachagent für ein Hotel**: ElevenLabs Agents, Claude, n8n,
  PostgreSQL, Docker

Dazu kommt der Assistent auf dieser Seite: Django, PostgreSQL mit pgvector und
ein eigener Embedding-Dienst mit FastAPI.

Die Liste zeigt auch den Weg: Angefangen hat Benjamin mit reinem JavaScript
ohne Framework, dann kamen Angular und TypeScript, danach das Backend mit
Python und Django und der Betrieb auf einem eigenen Server. Zuletzt sind
Anwendungen mit KI dazugekommen.

## Welche Projekte Benjamin mit Django und Python gebaut hat

Im Backend arbeitet Benjamin mit Python, Django und dem Django REST Framework.
Damit sind sechs Projekte entstanden:

- **Coderr** ist eine REST-API für eine Plattform, auf der Dienstleistungen
  angeboten, bestellt und bewertet werden. Sie läuft auf seinem eigenen Server.
- **KanMind** ist eine REST-API für ein Kanban-Board mit Boards, Aufgaben und
  Kommentaren. Berechtigungen auf Objektebene regeln, wer was sehen und ändern
  darf. Der Quelltext liegt öffentlich auf GitHub.
- **Quizly** macht aus einem YouTube-Video ein Quiz: Der Ton wird lokal mit
  Whisper in Text umgewandelt, Gemini schreibt daraus zehn Fragen.
- **Videoflix** ist eine Videoplattform, die hochgeladene Videos im Hintergrund
  in mehrere Auflösungen umwandelt. Das Projekt ist noch in Arbeit.
- **Cardelia** ist ein Kartenkatalog mit Sammlungsverwaltung und sein größtes
  Projekt. Stack und Architektur hat er dort selbst gewählt.
- **Der Assistent auf dieser Seite** sucht Antworten in einer Wissensbasis mit
  PostgreSQL und pgvector.

## Welche Frontend-Projekte Benjamin gebaut hat

Im Frontend hat Benjamin zuerst ohne Framework gearbeitet, in reinem
JavaScript mit HTML und CSS. So sind die Bildergalerie Fotogram, der
Book-Store, die BestellApp, der Pokédex und das Spiel El Pollo Loco
entstanden. So war die Weiterbildung aufgebaut, und das hat einen Sinn: Wer
einmal jede Änderung von Hand ins DOM geschrieben hat, versteht, was ein
Framework später abnimmt.

Danach kamen Angular und TypeScript. Damit sind Join, ein Task-Manager im Team
zu viert, und sein Portfolio gebaut, beide mit SCSS und ohne UI-Framework wie
Bootstrap oder Angular Material.

Bis auf Fotogram sind alle Frontend-Projekte öffentlich erreichbar und laufen
auf Benjamins eigenem Server. Den Quelltext von Fotogram gibt es auf GitHub.

## Welche Projekte Benjamin mit KI gebaut hat

Drei von Benjamins Projekten setzen KI ein, jedes auf eine andere Art. Der
Assistent auf dieser Seite arbeitet mit RAG: Er sucht passende Abschnitte über
Embeddings in PostgreSQL mit pgvector und lässt Claude nur aus diesen
Abschnitten antworten. Quizly bindet die Gemini-API in ein Django-Backend ein
und gibt ihr ein festes Antwortschema vor. Nina ist ein Telefon-Sprachagent und
entscheidet per Tool-Calling selbst, wann sie über n8n-Workflows in der
Datenbank nachsieht oder eine Anfrage speichert.

Beim Assistenten und bei Nina hat Benjamin das Sprachmodell anhand fester Tests
ausgewählt und dabei Qualität und Kosten gegeneinander abgewogen.

## Warum im Portfolio nur vier Projekte stehen

Im Portfolio stehen vier Projekte: Join, El Pollo Loco, Cardelia und Coderr.
Der Pokédex, die BestellApp und der Book-Store laufen weiterhin und sind
erreichbar, werden dort aber nicht mehr gezeigt.

Das ist eine bewusste Entscheidung. Vier Projekte lesen sich als Auswahl, sechs
oder mehr als Sammlung. Kommt ein neues Projekt dazu, wird deshalb getauscht
und nicht angehängt. Die Auswahl soll zeigen, was Benjamin heute kann, und
nicht alles, was er je gebaut hat.
