---
titel: Woran Benjamin gerade arbeitet
quelle: Aktuelle Arbeit
---

## Woran Benjamin gerade arbeitet

Zurzeit arbeitet Benjamin an zwei Projekten weiter, die beide noch nicht
öffentlich zugänglich sind. Bei Videoflix, einer Videoplattform, steht das
Backend, das eigene Frontend ist noch im Aufbau. Cardelia, ein Kartenkatalog
mit Sammlungsverwaltung, läuft bereits, ist aber noch nicht fertig.

## Videoflix, eine Streaming-Plattform mit Hintergrundverarbeitung

Videoflix ist eine Videoplattform, an der Benjamin aktuell arbeitet. Das
Backend steht, das eigene Frontend ist noch im Aufbau, und öffentlich
erreichbar ist das Projekt bisher nicht.

Technisch ist es sein anspruchsvollstes Backend. Nach dem Hochladen eines
Videos läuft die Konvertierung mit FFmpeg zu HLS in drei Auflösungen, 480p,
720p und 1080p, dazu wird ein Vorschaubild herausgeschnitten. Das passiert
nicht während der Anfrage, sondern als Hintergrundjob. Ein Video zu
konvertieren dauert Minuten, und so lange darf niemand vor einer wartenden Seite
sitzen.

Die Jobs laufen über zwei Warteschlangen mit unterschiedlicher Priorität: eine
schnelle für E-Mails wie Kontoaktivierung und Passwort-Zurücksetzen, eine
langsame für die Videokonvertierung. Der Grund ist einfach: Eine
Aktivierungsmail, die hinter einer halbstündigen Videokonvertierung in der
Schlange steht, kommt zu spät. Abgearbeitet wird von zwei Arbeitsprozessen in
eigenen Docker-Containern, mit Redis als Unterbau.

## Warum Videoflix RQ verwendet und nicht Celery

Benjamin hat in seinen Projekten beide Werkzeuge eingesetzt: Celery bei
Cardelia, RQ bei Videoflix. Die Entscheidung fiel jeweils nach Projektgröße.

Für Videoflix reicht eine einfache Warteschlange auf Redis-Basis. Celery
entfaltet seine Stärken erst mit einem zusätzlichen Vermittler wie RabbitMQ,
und damit auch dessen Betriebsaufwand. RQ ist leichtgewichtiger, schneller
aufgesetzt und bringt über django-rq eine Oberfläche mit, auf der sich Jobs,
Fehler und vollständige Fehlerausgaben ansehen lassen.

Bei zwei Warteschlangen und im Kern einem einzigen Job-Typ war das der
passendere Zuschnitt. Die Frage ist für Benjamin nicht, welches Werkzeug
mächtiger ist, sondern welches zur Größe der Aufgabe passt.

## Warum Videoflix JWT verwendet und nicht Token-Authentifizierung

Videoflix nutzt Simple-JWT mit Access- und Refresh-Token, beide als
HttpOnly-Cookies statt im LocalStorage abgelegt.

Der Unterschied ist sicherheitsrelevant: Ein Token im LocalStorage ist für
JavaScript lesbar. Gelingt irgendwo auf der Seite eine Cross-Site-Scripting-
Lücke, ist der Token mit abgeräumt. Ein HttpOnly-Cookie kommt gar nicht erst in
JavaScript-Reichweite. Nebenbei muss das Frontend den Token dann auch nicht
selbst verwalten.

Dazu kommt die Ablaufsteuerung: Der Access-Token gilt 30 Minuten, der
Refresh-Token 7 Tage, und der Access-Token lässt sich über einen eigenen
Endpunkt sauber erneuern. Die klassische Token-Authentifizierung des Django
REST Frameworks, wie Benjamin sie bei Coderr verwendet, kennt beides nicht: Der
Token ist dort unbefristet gültig und hat keine eingebaute Erneuerung.
