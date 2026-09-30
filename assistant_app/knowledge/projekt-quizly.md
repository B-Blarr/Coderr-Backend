---
titel: Quizly
quelle: Projekt Quizly
---

## Was Quizly ist

Quizly ist das Projekt, in dem Benjamin KI-Modelle in ein eigenes Backend
eingebunden hat. Das Backend mit Django und dem Django REST Framework macht aus
einem YouTube-Video ein Quiz. Der Nutzer gibt einen Link ein, das Backend lädt
die Tonspur mit yt-dlp herunter, wandelt sie mit dem Spracherkennungsmodell
Whisper in Text um und lässt Gemini über dessen API zehn Fragen mit je vier Antworten
schreiben.

Die Umwandlung in Text läuft lokal im Backend, der Ton geht also an keinen
fremden Dienst. Nur das fertige Transkript geht an Gemini. Welche Modelle
verwendet werden, lässt sich über die Konfiguration ändern, ohne den Code
anzufassen.

Die Anmeldung läuft über JWT in HttpOnly-Cookies. Beim Abmelden kommt der
Refresh-Token auf eine Sperrliste und kann nicht wiederverwendet werden.

Benjamins Teil ist das Backend, das Frontend stammt aus der Weiterbildung. Der
Quelltext liegt öffentlich auf GitHub.

## Wie Quizly die Antwort der KI absichert

Eine KI liefert nicht zuverlässig das Format, das man sich wünscht. Quizly
verlässt sich deshalb nicht auf den Text der Anfrage, sondern gibt Gemini ein
festes Antwortschema vor. Die Antwort kommt als JSON in genau der Struktur, die
das Backend erwartet.

Vor dem Speichern prüft Quizly zusätzlich, ob die richtige Antwort jeder Frage
wörtlich unter den vier Antwortmöglichkeiten steht. Ist das nicht der Fall,
bricht die Anfrage mit einem Fehler ab. Ohne diese Prüfung könnte ein Quiz
gespeichert werden, in dem eine Frage keine richtige Antwort hat, und das
würde erst ein Nutzer beim Spielen bemerken.

Die Tests rufen weder YouTube noch Whisper noch Gemini auf. Die ganze Kette ist
in den Tests ersetzt, damit sie schnell laufen, nichts kosten und jedes Mal
gleich ausgehen.
