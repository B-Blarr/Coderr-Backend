---
titel: Server und Betrieb
quelle: Infrastruktur
---

## Benjamin betreibt seine Projekte auf einem eigenen Server

Benjamins Projekte laufen nicht bei einem Hosting-Baukasten, sondern auf einem
eigenen virtuellen Server unter Ubuntu, den er selbst aufgesetzt hat und selbst
administriert. Das schließt alles ein, was dazugehört: Betriebssystem
einrichten, Dienste installieren und absichern, Zertifikate ausstellen, Updates
einspielen, Fehler im laufenden Betrieb finden.

Das ist der Unterschied zwischen "ich habe eine Anwendung geschrieben" und "ich
betreibe eine Anwendung". Auf demselben Server laufen mehrere seiner Projekte
nebeneinander, jedes unter einer eigenen Adresse.

## Wie die Anwendungen ausgeliefert werden

Vor den Anwendungen steht Nginx als Reverse Proxy. Er nimmt alle Anfragen
entgegen, liefert statische Dateien direkt aus und reicht alles andere an die
Anwendung dahinter weiter. Die Django-Anwendung selbst läuft unter Gunicorn mit
mehreren Arbeitsprozessen, angebunden über einen lokalen Socket statt über
einen offenen Port.

Die Verschlüsselung läuft über Zertifikate von Let's Encrypt, die sich
automatisch erneuern. HSTS ist aktiv, der Zugriff erfolgt ausschließlich über
HTTPS.

Als Datenbank kommt PostgreSQL zum Einsatz, erreichbar nur vom Server selbst
und nicht aus dem Netz.

## Absicherung des Servers

Die Firewall lässt nur die Ports offen, die tatsächlich gebraucht werden. Ein
Dienst zur Erkennung wiederholter Fehlanmeldungen sperrt auffällige Adressen
automatisch. Zugangsdaten und Schlüssel liegen in einer Konfigurationsdatei mit
eng gesetzten Dateirechten und stehen nicht im Quellcode.

Öffentliche Formulare sind zusätzlich abgesichert: Eine Begrenzung der Anfragen
pro Absender verhindert massenhaftes Absenden, und ein für Menschen unsichtbares
Feld erkennt automatisierte Einsendungen.

## Datensicherung

Die Datenbank wird jede Nacht automatisch gesichert, zusätzlich vor jedem
Ausrollen einer neuen Version. Die Sicherungen werden über einen festen
Zeitraum aufbewahrt und ältere automatisch gelöscht.

Benjamin prüft die Sicherungen auch auf Wiederherstellbarkeit. Eine Sicherung,
die noch nie zurückgespielt wurde, ist keine Sicherung, sondern eine Annahme.

## Wie neue Versionen live gehen

Benjamin deployt nicht von Hand, sondern über eine CI/CD-Pipeline in GitHub
Actions. Bei jeder Änderung laufen zuerst die Prüfungen: Codeformatierung,
statische Analyse, automatische Tests, ein vollständiger Build. Erst wenn alles
davon durchläuft und die Änderung im Hauptzweig landet, wird ausgerollt.

Ein Pull Request durchläuft dieselben Prüfungen, rollt aber nie aus. Dadurch ist
der Moment, in dem etwas live geht, eine bewusste Entscheidung und kein
Nebeneffekt.

Nach dem Ausrollen prüft die Pipeline selbst, ob die Seite erreichbar ist und
ob die ausgelieferten Dateien den richtigen Inhaltstyp haben. Ein fehlerhaftes
Ausrollen fällt dadurch sofort auf, statt unbemerkt zu bleiben.

## Was Benjamin dabei gelernt hat

Die Fehler, die im Betrieb auftreten, sind andere als die beim Entwickeln. Ein
Beispiel: Nach dem Hochladen von Dateien kamen Unterordner mit zu engen Rechten
auf dem Server an. Der Webserver durfte sie nicht betreten und lieferte
daraufhin für Bilder und Sprachdateien die Startseite aus, mit dem Statuscode
200 und ohne jede Fehlermeldung. Die Seite sah funktionierend aus und war es
nicht.

Aus solchen Fällen hat er sich angewöhnt, nach jedem Ausrollen nicht nur zu
schauen, ob eine Seite lädt, sondern zu prüfen, ob auch das Richtige
ausgeliefert wird. Genau diese Prüfung läuft heute automatisch in der Pipeline
mit.
