---
titel: Nina, Telefon-Sprachagent für ein Hotel
quelle: Projekt Telefon-Sprachagent
---

## Was Nina ist

Nina ist ein Voice-Agent, also ein Telefon-Sprachagent, den Benjamin als eigenes
Projekt gebaut hat. Sie ist die KI-Assistentin an der Rezeption des Hotel
Elmblick, eines ausgedachten Familienhotels in Schöningen. Nina ist unter einer
echten Schöninger Telefonnummer erreichbar, nimmt Anrufe auf Deutsch an und
stellt sich dabei als KI-Assistentin vor. Sie beantwortet Fragen zu Zimmern,
Preisen, Frühstück, Anreise und Hausregeln. Außerdem prüft sie, welche Zimmer
für einen gewünschten Zeitraum frei sind und was der Aufenthalt kostet. Passt
ein Zimmer, hält sie eine Buchungsanfrage fest, die das Team anschließend
bestätigt. Direkt über Nina buchen kann man bewusst nicht. Braucht eine Frage
einen Menschen, nimmt sie eine Rückrufbitte auf.

Die Telefonnummer steht nicht öffentlich im Netz, Benjamin gibt sie auf Anfrage
über das Kontaktformular auf dieser Seite gerne weiter. Thema und Aufbau hat er
selbst gewählt. Der Quelltext liegt öffentlich auf GitHub unter
github.com/B-Blarr/Voice-Agent-Hotel.

## Wie Nina technisch aufgebaut ist

Das Gespräch läuft über ElevenLabs Agents, dort sitzen Spracherkennung,
Sprachmodell und Stimme. Die Anrufe kommen über einen SIP-Trunk von Telnyx.
Nina arbeitet mit Tool-Calling und entscheidet selbst, welches ihrer drei
Werkzeuge sie aufruft. Jedes Werkzeug ist ein Webhook auf Benjamins eigenem
Server, wo n8n-Workflows die Angaben prüfen und in PostgreSQL die freien Zimmer
abfragen oder Anfragen speichern. Doppelbuchungen verhindert PostgreSQL selbst
über eine Ausschlussbedingung auf dem Zeitraum.

Fehlt eine Angabe oder liegt ein Datum in der Vergangenheit, antworten die
Workflows mit Status 200, mit `ok: false` und dem Grund. ElevenLabs würde jeden
HTTP-Fehler als kaputtes Werkzeug werten und Nina erführe nur, dass etwas schiefgegangen
ist. So kann sie beim Anrufer gezielt nachfragen. Echte Ausfälle melden die
Workflows weiterhin als Fehler.

Jede Buchungsanfrage und jede Rückrufbitte geht sofort per E-Mail an das
Hotelteam. Nach jedem Anruf schickt ElevenLabs einen signierten
Post-Call-Webhook, aus dem n8n Dauer, Kosten und Kanal speichert. Was ein Anruf
gebracht hat, ergibt sich per SQL aus den gespeicherten Daten.

Auf dem Server laufen n8n und PostgreSQL in Docker hinter Nginx. Die Datenbank
ist in SQL-Migrationen beschrieben. Bei jeder Änderung laufen sie in GitHub
Actions auf einer frischen Datenbank, wo Tests freie Zimmer und Preise,
Doppelbuchungen, die Rechte der Datenbankrolle und die Löschfristen prüfen.

## Wie Nina ein Telefongespräch führt

Nina rechnet Angaben wie "nächsten Freitag" in ein genaues Datum um und liest es
zur Bestätigung vor. Bevor sie etwas speichert, wiederholt sie die
Telefonnummer Ziffer für Ziffer. Eine Buchung bestätigt sie nie und eine
Rückrufzeit verspricht sie auch nicht. Scheitert ein Werkzeug, sagt sie das dem
Anrufer ehrlich. Vor jedem Werkzeugaufruf sagt sie einen kurzen Satz, damit der
Anrufer während der Abfrage keine Stille hört. Kurze Einwürfe wie ein "mhm" und
Gespräche im Hintergrund unterbrechen sie nicht. Beginnt jemand, Kartendaten
vorzulesen, unterbricht sie höflich.

Sie legt erst auf, wenn sich auch der Anrufer verabschiedet hat oder 30
Sekunden Stille waren. Ein Anruf dauert höchstens acht Minuten und für die
Kosten gilt eine feste Monatsgrenze.

## Wie Nina abgesichert ist und was mit den Daten der Anrufer passiert

Von außen erreichbar sind nur die Webhooks. Die drei Werkzeuge verlangen einen
eigenen Schlüssel, den das Sprachmodell selbst nie zu sehen bekommt. Der
Post-Call-Webhook ist mit einer Signatur gesichert, die n8n nachrechnet. Die
Oberfläche von n8n ist von außen gar nicht zu sehen. Die Workflows arbeiten mit
einer eigenen Datenbankrolle. Sie darf Zimmer und Belegung lesen und neue
Anfragen anlegen, ändern kann sie nichts. Löschen kann sie nur über eine
nächtliche Aufräumfunktion, die ausschließlich Daten nach Ablauf der Löschfrist
entfernt. Wer den Schlüssel stehlen würde, könnte also höchstens Anfragen
hinzufügen.

Versucht ein Anrufer, Nina mit Anweisungen aus ihrer Rolle zu holen, beendet ein
Schutzfilter von ElevenLabs das Gespräch. Weitere Filter blockieren anstößige
oder gewalttätige Antworten.

Tonaufnahmen werden nicht gespeichert und die Nummer des Anrufers landet nicht
in der Datenbank. Die Gesprächsprotokolle löscht ElevenLabs nach 30 Tagen.
Anfragen mit Namen und Telefonnummern werden ebenfalls nach 30 Tagen gelöscht,
die übrigen Anrufdaten nach 90 Tagen. Die E-Mails an das Team bleiben im
Postfach.

## Wie Benjamin das Sprachmodell für Nina ausgewählt hat

Das Sprachmodell hinter Nina hat Benjamin anhand von Tests ausgewählt. Er prüft
Nina mit sieben festen Tests in ElevenLabs: Zwei prüfen die Angaben, mit denen
sie ihre Werkzeuge aufruft, drei prüfen einzelne Antworten und zwei spielen mit
einem simulierten Anrufer ein ganzes Gespräch durch. Geprüft wird etwa, ob sie
einen falschen Wochentag bemerkt, Preise genau aus dem Werkzeug übernimmt und
ehrlich bleibt, wenn das Speichern scheitert. Jeden Test hat er fünfmal pro
Modell laufen lassen und so drei Claude-Modelle verglichen.

Sonnet 5.5 hat alle 35 Läufe bestanden, Haiku 5.5 kam auf 32 und Sonnet 5 auf
28. Sonnet 5 war vor der Zimmerabfrage mit etwa 0,9 Sekunden am schnellsten,
hat aber einen Samstag als Freitag akzeptiert. Haiku 5.5 ist beim Sprachmodell
etwa zwanzigmal günstiger, hat dem simulierten Anrufer aber immer wieder
erzählt, es dürfe die Webadresse des Hotels nicht nennen. Nina läuft deshalb
auf Sonnet 5.5. Die rund 3,3 Sekunden bis zur Zimmerabfrage überbrückt sie mit
einem kurzen Satz.

## Was ein Anruf bei Nina kostet und wie Benjamin die Tests bewertet

Ein echter Anruf von 88 Sekunden hat etwa 13 US-Cent gekostet. Davon entfiel
nur ein kleiner Teil auf das Sprachmodell, den größeren Teil machen Stimme und
Telefonie aus. Bei wenigen Anrufen liegt der Unterschied zwischen den Modellen
deshalb bei etwa einem Dollar im Monat. Für ein Hotel mit Hunderten Anrufen im
Monat wäre Haiku der bessere Kompromiss.

Drei der ersten Fehlschläge in den Tests gingen auf den Bewerter zurück, der
einmal den Artikel "ein" als Zimmeranzahl gelesen hat. Seitdem liest Benjamin
jeden fehlgeschlagenen Lauf selbst, bevor er ihn zählt. Die Kriterien formuliert
er so, dass sie sich nicht missverstehen lassen.
