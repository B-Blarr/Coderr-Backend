---
titel: Coderr
quelle: Projekt Coderr
---

## Was Coderr ist

Coderr ist eine REST-API, die Benjamin mit dem Django REST Framework gebaut
hat. Sie bildet eine Plattform ab, auf der Dienstleistungen angeboten, bestellt
und bewertet werden: Angebote, Bestellungen und Bewertungen, dazu Registrierung
und Anmeldung mit Token-Authentifizierung.

Das Frontend stammt von der Developer Akademie und war vorgegeben. Benjamins
Arbeit ist das Backend dahinter, das die vorgegebene Schnittstelle exakt
bedienen muss.

Coderr läuft unter coderr.benjaminblarr.de auf Benjamins eigenem Server, der
Quelltext liegt öffentlich auf GitHub.

## Wie Coderr aufgebaut ist

Coderr ist in sechs Django-Apps aufgeteilt, jede mit einem eigenen Bereich für
die Schnittstelle: Serializer, Views, URLs und Berechtigungen liegen getrennt
voneinander. Der Zuschnitt folgt der Fachlichkeit — Anmeldung, Angebote,
Bestellungen, Bewertungen — statt alles in eine große Anwendung zu legen.

Die API ist über drf-spectacular dokumentiert und lässt sich als Swagger-
Oberfläche aufrufen.

Die Standardeinstellung für Berechtigungen ist bewusst geschlossen: Jeder
Endpunkt verlangt zunächst eine Anmeldung, und öffentliche Endpunkte müssen das
ausdrücklich erlauben. Der umgekehrte Weg — alles offen, einzelne Endpunkte
abgesichert — verzeiht keinen Fehler, weil ein vergessener Endpunkt dann offen
steht statt zu.

## Das Kontaktformular des Portfolios läuft über Coderr

Das Kontaktformular auf benjaminblarr.de schickt seine Nachrichten an dieselbe
Django-Instanz. An diesem kleinen Endpunkt hängen mehrere Entscheidungen, die
Benjamin gern erklärt, weil sie zeigen, woran man bei einem öffentlichen
Formular denken muss.

Ein für Menschen unsichtbares Feld erkennt automatisierte Einsendungen. Wird es
ausgefüllt, antwortet der Server trotzdem mit einer Erfolgsmeldung und verwirft
die Nachricht still. Eine ehrliche Fehlermeldung würde dem Absender verraten,
dass die Falle erkannt wurde, und ihm beim nächsten Versuch helfen.

Die Begrenzung der Anfragen pro Absender richtet sich nach der IP-Adresse, die
der Webserver einträgt, und nicht nach der, die der Absender selbst behaupten
kann. Der Unterschied entscheidet darüber, ob die Begrenzung überhaupt wirkt.

Die Nachricht wird zuerst gespeichert und erst danach als E-Mail verschickt. Ist
der Mailversand gestört, ist die Nachricht trotzdem da. Als Absender steht dabei
Benjamins eigene Adresse, die Adresse des Besuchers steht in der
Antwort-an-Angabe — eine fremde Adresse als Absender zu setzen, lässt Mails in
Spamfiltern hängen.

## Warum der Zwischenspeicher in der Datenbank liegt

Eine Besonderheit an Coderr: Der Zwischenspeicher liegt nicht im
Arbeitsspeicher, sondern in der Datenbank. Das ist langsamer und trotzdem die
richtige Wahl.

Der Grund liegt in der Zählung der Anfragen pro Absender. Die Anwendung läuft
mit mehreren Arbeitsprozessen nebeneinander. Läge der Zähler im Arbeitsspeicher,
hätte jeder Prozess seinen eigenen — bei drei Prozessen dürfte derselbe Absender
das Dreifache des erlaubten Limits verschicken, weil keiner von den anderen
weiß. Erst ein gemeinsamer Speicher macht die Begrenzung zu einer echten
Begrenzung.

Das ist ein Beispiel für einen Fehler, den man im Betrieb nicht bemerkt: Es
funktioniert scheinbar, es zählt nur falsch.
